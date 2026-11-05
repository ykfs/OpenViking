# OpenViking 资源置信度（resource confidence）需求规格书

> 本文件为**需求基线**，已由客户于 2026-10-10 以口令「确认需求」确认。后续变更须走需求变更流程并升版本。

## 项目信息

- **项目名称**: OpenViking（代码库根目录 `prds/OpenViking`，git HEAD `02fb0543`）
- **创建日期**: 2026-10-10
- **版本**: v1.8
- **状态**: 已确认

## 项目背景

### 业务目标

用户已按可信程度把要导入 OpenViking 的资源分成了高置信与低置信两类。当前 `ov add-resource` 没有任何表达"人为可信度"的入口，导入后的资源在语义检索中只按语义相似度排序，低可信资源会与高可信资源以同等权重返回，人工分类的意图无法体现在检索结果中。

本次改造要让"人为置信度"成为资源的一等属性，并让它参与最终检索分数与排序。

### 目标用户

- 主要用户群体：使用 `ov` CLI 批量导入资源、并按可信度做过人工分类的知识库维护者。
- 次要用户群体：通过 REST / MCP / CLI / Web Studio 消费检索结果、并按 `score` 做二次阈值判断的下游（`bot/vikingbot`、`examples/openclaw-plugin`、`integrations/langchain`）。
- 使用场景描述：导入时按目录/批次标注置信度；检索时希望低置信资源排到后面。

### 问题陈述

| 痛点 | 证据（`文件:行号`） |
|------|---------------------|
| 无导入入口：`ov add-resource` 无置信度参数 | `crates/ov_cli/src/main.rs:335-465` |
| 无存储字段：向量集合 schema 无资源级置信度标量 | `openviking/storage/collection_schemas.py:84-153` |
| 无打分因子：最终分只由语义分与 hotness 混合 | `openviking/retrieve/hierarchical_retriever.py:605-657` |
| 契约未定：检索结果是否回传置信度 | `openviking_cli/retrieve/types.py:276-289`、`:376-383` |

## 关键证据核对（Evidence Checklist，复杂改造必填）

- [x] **入口证据**
  - CLI 子命令定义（clap derive）：`crates/ov_cli/src/main.rs:335`（`Commands::AddResource`，`:336-464`）；同类参数 `--tag` / `--tag-mode` 位于 `:452-462`。
  - CLI 派发：`crates/ov_cli/src/main.rs:3178-3248`；handler `crates/ov_cli/src/handlers.rs:16-132`（`tags`/`tag_mode` 在 `:34-35`、`:124-125`）；薄封装 `crates/ov_cli/src/commands/resources.rs:6-67`。
  - HTTP 客户端：`crates/ov_cli/src/client.rs:813-986`（`POST /api/v1/resources`，三个分支：目录 zip 上传 `:865-906`、单文件 `:907-942`、URL/connector `:964-985`）；body 拼装 `:851-861` 与 `:883-900` / `:919-936` / `:964-985`。
  - 服务端路由：`openviking/server/routers/resources.py:219-324`（`POST /api/v1/resources`）；请求模型 `AddResourceRequest` `:31-130`（`model_config = ConfigDict(extra="forbid")` 在 `:87`）。
  - 服务入口：`openviking/service/resource_service.py:1386-1410`（`add_resource`）。
  - 队列消息：`openviking/storage/queuefs/add_resource_msg.py:17-62`（字段表）、`:94-98`（`to_dict`）、`:100-207`（`from_dict`）。
  - 落库：`openviking/utils/embedding_utils.py:86-96`（`_apply_ingest_options` 写 `embedding_msg.context_data`）→ `openviking/storage/viking_vector_index_backend.py:178-185`（按集合 schema 过滤字段）→ `:329-365`（`upsert`）。
- [x] **参数流证据**
  - 现有同类参数完整链路（tags，由提交 `34b5a889` 引入，全链路 21 个落点见"历史学习结论"）：`--tag`（`main.rs:452-454`）→ `handlers.rs:34-35/124-125` → `commands/resources.rs:25-26/51-52` → `client.rs:832-833` → `client.rs:853` 调 `add_resource_tag_fields`（`client.rs:41-50`，空则不发送）→ body `tags`/`tag_mode` → `AddResourceRequest.tags/tag_mode`（`resources.py:110-111`）→ `resources.py:300-301` → `resource_service.py:1402-1403` → `_add_resource_ingest_tag_kwargs`（`:288-296`）→ `AddResourceMsg.tags/tag_mode`（`add_resource_msg.py:60-61`）→ `IngestOptions.search_tags`（`utils/ingest_options.py:23-24`）→ `_apply_ingest_options`（`embedding_utils.py:86-96`）→ 集合字段 `search_tags`（`collection_schemas.py:118`）。
  - 检索读取白名单（**决定候选 dict 里有没有该字段**）：`viking_vector_index_backend.py:34-42`（`RETRIEVAL_OUTPUT_FIELDS`）、`:44-48`（`LOOKUP_OUTPUT_FIELDS`）、`:50-66`（`FETCH_BY_URI_OUTPUT_FIELDS`）；注入点 `:1336`、`:1381`。
  - 打分链路：候选 `_final_score`（QUICK 路径 `hierarchical_retriever.py:199-205`；THINKING 递归路径 `:524-546`，含传播式 `:531-533`）→ `:605` `semantic_score` → `:607-626` hotness 混合 `score = (1−hotness_alpha)·semantic + hotness_alpha·hotness` → `:649` 写入 `MatchedContext.score` → `:657` 重排 → `:336` `matched[:limit]` 截断。
  - 阈值判定（**在 `_final_score` 赋值之前**）：`_passes_threshold` 定义 `:365-369`，调用点 `:200`、`:467`、`:535`；未通过即 `continue`（`:201`、`:471`、`:539`），L0/L1 目录还不会入 `dir_queue`（`:555-556`）。
- [x] **调用频率/批次策略证据**
  - 导入为单次 HTTP 请求；目录导入时对 L0/L1/L2 每条向量记录分别写入（`embedding_utils.py:423`、`:470`、`:631`），无分页、无批次隔离键。
  - 检索为单次查询；无循环写。
  - `find` 走 `RetrieverMode.QUICK`（`openviking/storage/viking_fs/_semantic.py:256-264`）→ `apply_hotness=False`（`openviking/retrieve/hierarchical_retriever.py:216`）、无 rerank、无传播；`search` 不传 mode（`_semantic.py:399-406`）→ 默认 `THINKING if self._rerank_client else QUICK`（`hierarchical_retriever.py:126-127`）。**两条路径的 `score` 语义本就不同**，乘法必须对两者都成立。
- [x] **数据源与落点证据**
  - 无关系库表、无 SQL 方言。落点为向量集合，schema 唯一来源 `openviking/storage/collection_schemas.py:71-165`（`Fields` `:84-133`、`ScalarIndex` `:134-153`、`FullText` `:159-164`）。
  - 集合只在不存在时创建（`collection_schemas.py:274-311`）；**自动 schema 迁移已被提交 `4d00feac` 显式删除**（`_migrate_acl_schema` 与 `update_collection_schema` 均已移除），现存唯一 legacy 处理是只告警的 `_collection_has_content_fulltext()`（`:232-246`，调用点 `:329-337`）。
  - 缺失标量的物化默认值来自 `openviking/storage/vectordb/utils/data_processor.py:92-104`（`TYPE_DEFAULTS`，其中 `"float32": 0.0`）与 `:120-141`（**优先取 schema 的 `DefaultValue`，取不到才用 `TYPE_DEFAULTS`**）。因此新字段必须在 schema 中显式声明 `DefaultValue`。
  - 除向量库外的承载形态：ovpack 快照（`openviking/storage/ovpack/index.py:22-32` 的 `PORTABLE_VECTOR_SCALAR_FIELDS` / `EXPORT_VECTOR_FIELDS`、`ovpack/vectors.py:260-292`）、namespace 迁移（`openviking/storage/vector_migration.py:18-35` 的 `VECTOR_MIGRATION_OUTPUT_FIELDS`、`:170-188`）。二者均按字段白名单投影，不加会导致备份/迁移丢字段。
  - 文件系统 sidecar 与 SQLite `observability/usage_audit` 均不存资源级标量（`abstract_overview.py:29` 的 OKF frontmatter 白名单；`observability/usage_audit/schema.py:17-73`），无需同步。
- [x] **多库/方言证据**
  - 不适用：无 SQL。向量库后端为适配器模式（`openviking/storage/vectordb_adapters/{local,http,volcengine,vikingdb_private}_adapter.py`），字段类型白名单见 `vectordb/utils/validation.py:46-59`（含 `float32`）。

## 历史学习结论（历史需求/任务/提交定位）

本仓库为 OpenViking 开源仓库的二次开发 fork，dev-hub 无对应需求编号，故历史学习改用 git 历史定位：

| 提交 | 作用 | 对本次改造的价值 |
|------|------|------------------|
| `21c58bd8` `Set tags (#2706)` | `search_tags` **进入 storage/schema 层** | **新增资源级标量字段的权威模板**：`collection_schemas.py` Fields + ScalarIndex、`viking_vector_index_backend.py` 两个 output_fields 白名单、独立 update 方法、引擎层 partial update |
| `34b5a889` `Feat/add resource tags (#3560)` | `add-resource` 的 tags 全链路（CLI→HTTP→service→queue→IngestOptions） | **参数透传的权威模板**（21 个落点） |
| `4d00feac` `fix(acl): remove automatic schema migration (#4522)` | 删除自动 schema 迁移 | **约束**：存量集合不会自动获得新字段，必须显式决策 |
| `4f9840ec` `feat(tags): support tagged write and filesystem filtering (#4457)` | `ov write`/`ls`/`grep` 的 tags 与 `set_tags` | **反例**：该提交**未**改 schema 层，不能作为"新增资源字段"的参照 |

## 功能需求 (使用 EARS 记号法)

### FR-001: add-resource 支持置信度参数

**需求描述**：
当 用户执行 `ov add-resource <path-or-url>` 并显式指定 `--confidence <float>` 时
系统应该 接受该参数，并把它作为请求体字段发送到服务端。

**来源**：用户原始需求（2026-10-10）。

**业务价值**：提供人工标注资源可信度的入口。

**本期的入口范围（明确界定）**：`ov add-resource` 主链路（CLI → REST `POST /api/v1/resources`）为**本期必须支持**的入口。另两条同源入口 **MCP `add_resource`**（`openviking/server/mcp_endpoint.py:933-950`）与 **`ingest_temp_upload`**（`openviking/server/resource_ingest.py:22-76`）**本期不新增置信度参数**，其导入的记录按缺省 1.0 处理；若二者经由 REST 主链路复用同一 service，则自动获得同一缺省语义。

**验收标准**：

- [ ] `ov add-resource <path> --confidence 0.6` 能成功解析，请求体含 `"confidence": 0.6`。
- [ ] 未指定 `--confidence` 时，请求体**不携带** `confidence` 字段（沿用 `add_resource_tag_fields` 的空值不发送约定，`client.rs:41-50`），服务端按缺省 1.0 处理。
- [ ] 显式传 `0.0` 时**必须发送**该字段（CLI 侧以 `Option<f64>` 表达"未指定"，不得用 `0.0` 兼作缺省，避免 `0.0` 被当作 falsy 丢弃）。
- [ ] `ov add-resource --help` 中可见该参数及其取值区间说明。
- [ ] 参数值非法（非数字、越界）时，CLI 在本地即报错并给出明确提示，不发出请求。
- [ ] 该参数与 `--manifest` 互斥（与 `--tag`/`--tag-mode`/`--reason`/`--instruction` 同列于 `main.rs:350-355` 的 `conflicts_with_all`）。
- [ ] **导入完成后必须回显生效的置信度**（用户 2026-10-10 要求"导入的时候要显示打印出置信度出来，方便用户知悉"）：
  - Table 输出：在 `ov add-resource` 的成功输出中明确打印本次生效的置信度，例如 `confidence 0.600`；未指定时打印 `confidence 1.000 (default)`。
  - JSON 输出：`--json` 输出中同样含该字段，键名**必须**为 `confidence`（与请求体一致）。
  - **生效值的来源**：由 CLI 侧本地计算（`--confidence` 入参，或缺省 `1.0`），**不依赖服务端响应体**；服务端无需在 add-resource 响应中回传该字段。
  - 打印的是**生效值**（即"显式传入值"或"缺省 1.0"），不是"是否传了参数"；目录导入多文件时只打印一次该批次值，不逐文件刷屏。
  - 渲染位置：`crates/ov_cli/src/commands/resources.rs:65` 的 `output_success(&result, format, compact)`（Table 与 `--json` 共用同一出口，`:58` 已有 Table 专属分支先例）。

**优先级**：高

---

### FR-002: 置信度随导入落库为资源级标量字段

**需求描述**：
当 服务端处理带有置信度的 add-resource 请求时
系统应该 把该置信度写入本次导入产生的每条向量记录（L0/L1/L2），使其可被检索阶段读取。

**来源**：用户原始需求；落库落点参照提交 `21c58bd8`。

**业务价值**：置信度必须持久化，否则无法参与检索打分。

**验收标准**：

- [ ] 在集合 schema 的 `Fields` 中新增 `{"FieldName": "confidence", "FieldType": "float32", "DefaultValue": 1.0}`（`collection_schemas.py:84-133` 内）。**`DefaultValue: 1.0` 为强制项**：缺省时 `data_processor.py:92-104` 会物化为 `0.0`，导致未携带该字段的记录分数被清零。
- [ ] 该字段加入 `RETRIEVAL_OUTPUT_FIELDS`（`viking_vector_index_backend.py:34-42`，**必须**，否则检索候选 dict 取不到）与 `FETCH_BY_URI_OUTPUT_FIELDS`（`:50-66`）。
- [ ] 该字段加入 **ovpack 导出投影**（`storage/ovpack/index.py:22-32` 的 `PORTABLE_VECTOR_SCALAR_FIELDS`）、**ovpack import recompute 写入白名单**（`utils/embedding_utils.py:65-74` 的 `_PORTABLE_SCALAR_FIELDS`）与 **namespace 迁移读侧投影**（`storage/vector_migration.py:18-35`）。三者缺一即会在备份恢复或迁移后丢字段（ovpack import 的非 `restore` 分支会重新向量化，走 `_apply_scalar_overrides`）。
- [ ] 本期**不**加入 `ScalarIndex`（`collection_schemas.py:134-153`）与 `LOOKUP_OUTPUT_FIELDS`（`:44-48`）：本期无按置信度服务端过滤的需求，避免引入无使用方的索引。
- [ ] `IngestOptions` 侧的两处"仅按 tags 判断"的早退分支必须一并放开，否则"只带 confidence、不带 tags"的导入到不了 `context_data`：
  - `openviking/service/resource_service.py:288-296`（`_add_resource_ingest_tag_kwargs`：`tags is None` 时直接 `return {}`，是**更靠前的第一道闸门**）；
  - `openviking/utils/embedding_utils.py:86-96`（`_apply_ingest_options` 的 `ingest_options.search_tags is None` 早退）。
  两处必须同时修，只修后者不生效。
- [ ] 目录导入时，目录下每个文件及其 L0/L1 摘要记录的置信度一致。
- [ ] 不新增独立于 `IngestOptions` 的请求级全局状态。

**优先级**：高

---

### FR-003: 检索排序分按置信度做**有界**加权，并保留未加权原始分

**需求描述**：
当 检索命中带有置信度的资源记录时
系统应该 使该记录的对外排序分数等于"未加权原始分 × 一个有界折扣因子"，**同时保留并对外暴露未加权原始分**，使"语义相关但被人工降权"与"语义本身就弱"两类记录可被区分，且**置信度的影响幅度有明确上界**。

**来源**：用户原始需求（"最终的查找结果分数要乘以这个置信度"）+ 用户 2026-10-10 追问（"语义 0.42 × 置信 0.5 与 语义 0.21 × 置信 1.0 怎么区分"）+ 用户 2026-10-10 反例（"加权分接近但不相同时，未加权分很低的排在了前面"）。

**业务价值**：纯乘法（`raw × confidence`）的惩罚幅度**没有上界** —— `confidence → 0` 时，一条语义分高得多的记录会被任意低分的记录反超。有界折扣在保留"人工降权"能力的同时，保证**语义分仍是排序的主导因素**。

**口径（唯一，无歧义）**：

**折扣因子**

```
factor(confidence) = 1 - λ · (1 - confidence)      λ = 0.2（本期固定值）
score              = raw_score × factor(confidence)
```

| λ | 语义 | `factor` 取值 | 该模型等价于 |
|---|------|---------------|--------------|
| `1.0` | 纯乘法 | `confidence` | 已否决（无界，用户反例） |
| **`0.2`** | **有界折扣（本期采用）** | `[0.8, 1.0]` | — |
| `0.0` | 完全不改排序分 | 恒为 `1.0` | 已否决（"低置信下沉"不生效） |

**为什么是乘法（相对折扣）而不是加法（绝对扣分）**：`score` **不保证落在 `[0,1]`** —— `_normalize_result_score`（`openviking/storage/vectordb_adapters/base.py:82-86`）只做有限性检查、**没有任何 min-max 归一化**（已全仓核查 `openviking/retrieve/`、`openviking/storage/vectordb_adapters/` 无归一化代码），实际量纲随后端与 rerank 供应商而变。相对折扣**与量纲无关**；绝对扣分（如 `score - 0.1`，即 `other_peer_penalty` 的形态，`context_assembler/gather.py:250`）在量纲为 0~10 时几乎无效、在 0~0.1 时又过狠，故不采用。

**三个层次的分数**（全文严格按此命名，不得混用）：

| 名称 | 定义 | 位置 | 用途 |
|------|------|------|------|
| `_final_score`（内部） | hotness 混合**之前**的检索分（语义分经传播衰减后） | `hierarchical_retriever.py:466`、`:524-533` | **相关性门槛的唯一比对对象** |
| `raw_score`（对外） | hotness 混合**之后**、**未打折**的分；等于改造前 `MatchedContext.score` 的取值 | `:605` → `:607-626` | 对外暴露的"未加权分"；NFR-001 的对照量 |
| `score`（对外） | `raw_score × factor(confidence)` | 在 `:626` 之后 | 排序与展示 |

**作用点**：

- 折扣作用点位于 `_convert_to_matched_contexts`（`:590-658`）内部，即 `_passes_threshold` 的三个调用点（`:200`、`:467`、`:535`）**之后**。
- 默认配置 `hotness_alpha = 0.0`（`openviking_cli/utils/config/retrieval_config.py:10-17`）下 `apply_hotness` 分支不改变分数（`:625-626`），因此 `_final_score == raw_score`；`hotness_alpha > 0` 时二者相差 hotness 项，但"**置信度不参与门槛**"这一结论不受影响。
- **不变**：所有相关性门槛作用在 `_final_score` 上（见 FR-009），通过门槛的候选池（`collected_by_uri`）与进入 `_convert_to_matched_contexts` 的候选集合；
- **可变（且为期望效果）**：`:657` 重排后经 `:336` `matched[:limit]` 截断返回的 Top-N 成员会随排序变化。

**有界性的精确定义（可测）**：

- 绝对值界：`raw_score × (1 - λ) ≤ score ≤ raw_score`，即 λ=0.2 时 `score ∈ [0.8·raw_score, raw_score]`。
- **相对差的定义（全文唯一定义，不得换分母）**：设两条记录 `raw_a > raw_b > 0`，则

  ```
  相对差 := (raw_a - raw_b) / raw_a
  ```

- 换位界：在上述定义下，低 `raw_score` 的一方**才可能**因置信度更高而反超，当且仅当 `相对差 < λ`。λ=0.2 时即：**未加权分相对差 < 20% 才可能换位；相对差 ≥ 20% 时，永远不会因置信度换位。**
  （等价写法：`raw_b / raw_a > 1 - λ`。**不要**写成 `λ/(1-λ)` 或 `25%` —— 那是把分母换成 `raw_b` 的另一种口径，与本定义不一致，已在需求审查第 4 轮被判定为互斥表述。）

**验收标准**：

- [ ] 置信度 1.0 的记录，其 `score == raw_score`，且与改造前 `MatchedContext.score` 逐位一致（NFR-001 的判定依据）。
- [ ] 不变式恒成立：`score == raw_score × (1 - λ·(1 - confidence))`，λ = 0.2（浮点容差 `1e-9` 内），对所有返回项可断言。
- [ ] **有界性断言**：对任意返回项，`raw_score × 0.8 - 1e-9 ≤ score ≤ raw_score + 1e-9`。
- [ ] **用户样例 1（跨档不反超，必须通过）**：默认配置（`hotness_alpha = 0`）下，X：`raw_score=0.90, confidence=0.5`（`score=0.81`）；Y：`raw_score=0.46, confidence=1.0`（`score=0.46`）→ **X 必须排在 Y 之前**。
- [ ] **用户样例 2（档内换位，属期望行为）**：P：`raw_score=0.50, confidence=0.5`（`score=0.45`）；Q：`raw_score=0.46, confidence=1.0`（`score=0.46`）→ **Q 排在 P 之前**（语义仅差 0.04、置信度差一倍，低置信让位）。
- [ ] **原样例（门槛分工）**：A：`raw_score=0.42, confidence=0.5`；B：`raw_score=0.21, confidence=1.0`。在门槛 0.35 下（门槛比对 `_final_score`），**A 保留、B 丢弃**；该判定只能用未加权的分完成。
- [ ] **换位边界断言（紧边界，必须成对）**：固定 `raw_a=0.50, confidence_a=0.0`（其 `score_a = 0.50 × 0.8 = 0.40`）。
  - 令 `raw_b=0.405, confidence_b=1.0`（`相对差 = (0.50-0.405)/0.50 = 19% < λ`）→ `score_b = 0.405 > 0.40`，断言 **B 排在 A 之前**（界内允许换位）；
  - 令 `raw_b=0.395, confidence_b=1.0`（`相对差 = 21% > λ`）→ `score_b = 0.395 < 0.40`，断言 **A 排在 B 之前**（越界不换位）。
  - 这对用例的临界值为 `raw_a × (1-λ) = 0.40`，可区分 λ=0.2 与 λ=0.25（若 λ=0.25，第二个断言会失败）。
- [ ] **并列稳定性**：当两条记录 `score` 完全相同时，以 `raw_score` 降序作为 tie-break，结果确定可复现。
- [ ] 无该字段的历史记录 `confidence = 1.0`，`factor = 1.0`，`score == raw_score`，分数与排序不发生任何变化。
- [ ] 折扣作用点唯一，不存在多处以不同口径重复折扣。
- [ ] 置信度不得参与任何相关性门槛：`_passes_threshold`（`:365-369`）的输入必须仍是 `_final_score`，三处调用点（`:200`、`:467`、`:535`）均不得改为打折后的分。低置信记录不得因折扣跌破门槛而被删除。
- [ ] `find`（QUICK，`apply_hotness=False`，`:216`）与 `search`（可能走 THINKING 且 `apply_hotness=True`、`:327`，叠加 hotness 与传播）两条路径均满足上述口径；`hotness_alpha > 0` 时须给出 `_final_score != raw_score` 的用例并断言两者各自满足上述用途。
- [ ] **越界读侧兜底（防止反向加成）**：读侧必须做 `confidence = clamp(confidence, 0.0, 1.0)`，**与写侧校验（FR-005 AC2）互为独立防线** —— 写侧校验管不到存量数据、ovpack 恢复数据与直接写库的数据。构造 `confidence = 1.5`（有限但越界）的存量记录，断言 `factor = 1.0`（而非 `1.1`）、`score == raw_score`。
- [ ] `confidence` 或 `raw_score` 缺失、非数值或非有限时分别按 `1.0` / `0.0` 处理，不产生 `nan`/`inf`。

**优先级**：高

---

### FR-004: 检索结果同时返回置信度与未加权原始分

**需求描述**：
当 检索（find / search）返回结果时
系统应该 在每条结果中同时携带 `confidence` 与 `raw_score`，与 `score` 三者并列。

**来源**：用户原始需求（本轮提问"返回的时候还需要返回置信度吗"），结论为需要；`raw_score` 由用户 2026-10-10 追问"两者怎么区分"推导而来。

**业务价值**：`score` 是"语义分 × 置信度折扣因子"的复合值且不可逆。只回传 `confidence` 时，调用方仍需自己按 `factor` 反算（受 `λ` 与浮点误差影响）；直接给出 `raw_score` 才能让"该保留 / 该丢弃"的判断稳定、可测。

**验收标准**：

- [ ] `MatchedContext`（`openviking_cli/retrieve/types.py:276-289`）新增 `confidence: float = 1.0` 与 `raw_score: float = 0.0` 两个字段，并在 `FindResult.from_dict._parse_context`（`:416-427`）中回读。
- [ ] `FindResult._context_to_dict`（`:376-383`）输出新增键 `confidence` 与 `raw_score`，与 `score` 同级；键名不使用 `tags` 式的改名映射。
- [ ] **provenance 分支同步**：`FindResult._query_result_to_dict`（`openviking_cli/retrieve/types.py:394-410`，其中 `:404` 现为 `"score": ctx.score`）的 `matched_contexts[]` 同步输出 `raw_score` 与 `confidence`。该分支经 `openviking/server/routers/search.py:360`（find）与 `:479`（search）由 `include_provenance=true` 对外可达，若不同步会出现"同一 `MatchedContext` 在 list 响应有原始分、在 provenance 响应没有"的契约不一致。
- [ ] **context 模式（`search` 的 `mode="context"`）同步输出**：响应 `entries[]` 的每一项必须含 `raw_score` 与 `confidence`（序列化点 `openviking/retrieve/context_assembler/models.py:46-52` 的 `AssembleResult.to_dict`，经 `server/routers/search.py:422` 对外）。断言方式：`POST /api/v1/search`（`mode="context"`）返回的每个 `entries[i]` 都含这两个键，且 `score == raw_score × (1 - λ·(1 - confidence))`。
- [ ] 明确 `FindResult.from_dict`（`:412-432`）是否需要解析 `provenance`：当前 `_parse_context` 只用于 `memories`/`resources`/`skills`（`:429-432`），本期**不新增** provenance 反序列化，此决定需在设计中记录。
- [ ] 三者满足不变式 `score == raw_score × (1 - λ·(1 - confidence))`，λ = 0.2（浮点容差 `1e-9` 内）。
- [ ] 历史记录（无置信度字段）返回 `confidence = 1.0` 且 `raw_score == score`，而非 `null` 或缺键。
- [ ] 不改变既有 `score` 键名与类型；`raw_score` 的取值在改造后与改造前同一条记录的 `score` 逐位一致。
- [ ] CLI `ov search` / `ov find` 的卡片输出中展示置信度（渲染分支 `crates/ov_cli/src/commands/search.rs:421-429`，解析函数 `:592-600`）。
- [ ] MCP `find` / `search` 的返回文本中展示置信度（渲染点 `openviking/server/mcp_endpoint.py:409-410`）。
- [ ] `POST /api/v1/skills/find` 的结果构造（`openviking/server/routers/skills.py:230-241`）在字段可用时同步透出；skill 记录无该字段时按 1.0。
- [ ] 既有 JSON 消费方在未同步更新时不报错：`FindResult.from_dict` 忽略未知键；CLI 以 `serde_json::Value` 透传（`crates/ov_cli/src/client.rs:693-725`）；Web Studio 手写响应类型为可选字段（`web-studio/types/ov-server/api/v1/search.ts:5-14`，实际读取发生在 `web-studio/src/lib/retrieval.ts:101-125`）。

**优先级**：高

---

### FR-005: 缺省值、取值范围与更新语义

**需求描述**：
当 资源没有显式置信度（历史数据、或本次请求未指定）时
系统应该 以 1.0 作为其置信度参与打分与输出。

**来源**：用户原始需求 + 代码证据（`data_processor.py:92-104/120-141`）。

**业务价值**：保证向后兼容，避免存量数据行为回归。

**验收标准**：

- [ ] 取值区间为闭区间 `[0.0, 1.0]`；缺省 1.0。
- [ ] `confidence = 0.0` 是合法输入，其语义为"**最强降权**"，即 `factor = 1 - λ = 0.8`（该记录仍会被返回，只是排序分被压到自身的 80%）。**本期 `confidence = 0` 不表示"排除该记录"**；若需要硬排除能力，见待确认事项 Q10。
- [ ] 越界值（`<0` 或 `>1`，含 `nan`/`inf`）服务端**拒绝**并抛 `InvalidArgumentError`，给出明确字段名提示；不做静默截断。
- [ ] 已有集合（schema 未含该字段）在改造后仍可正常检索，不抛异常。
- [ ] 历史记录在打分与输出中均表现为 1.0。
- [ ] 重复导入同一 URI（覆盖写）时，按本次请求的置信度覆盖旧值；本次请求未指定时**服务端按 1.0 显式写入**（即覆盖旧值为 1.0）。
  > 机制说明：向量写入被 `openviking/storage/collection_schemas.py:793-796` **无条件强制** `partial_update: True`，而 `viking_vector_index_backend.py:341-362` 的合并规则是 `existing.update({k: v for k, v in payload.items() if v is not None})` —— **payload 里没有该键就保留旧值**。因此"未指定即回落 1.0"必须由服务端**显式发出 `confidence=1.0`** 来实现，不能依赖缺省值自然生效。若选择"未指定即保留旧值"，见待确认事项 Q7。
- [ ] `add_resource` 的 `args` 顶层不得同时出现 `confidence`：需加入 `_ADD_RESOURCE_ARGS_RESERVED_FIELDS`（`resource_service.py:120-139`，现含 `tags` `:136`、`tag_mode` `:137`），冲突时报错。

**优先级**：高

---

### FR-006: 置信度的作用粒度与导入方式

**需求描述**：
当 用户对目录执行 add-resource 并指定置信度时
系统应该 把该置信度应用到该目录下本次导入的全部资源记录。

**来源**：用户原始需求（"我对文件做了分类"）+ 代码证据（`--tag` 的作用域先例）。

**业务价值**：与现有 `--tag` 的作用范围保持一致，不引入新的心智模型。

**验收标准**：

- [ ] 目录导入后，目录下每个文件的检索结果都反映该置信度。
- [ ] 本期作用域为"一次导入一个置信度值"，覆盖本次导入产生的全部记录；同一目录内高低置信混排的场景，约定**按置信度分目录/分批次导入**（例如先 `--confidence 1.0` 导入高置信目录，再 `--confidence 0.4` 导入低置信目录）。
- [ ] 本期不实现"按文件/路径映射置信度"（`--confidence-map` 之类）；需求原文见待确认事项 Q3。

**优先级**：中

---

### FR-007: 存量集合的字段可用性必须显式处理

**需求描述**：
当 服务启动并连接一个已存在、且 schema 中不含置信度字段的集合时
系统应该 显式告知该字段不可用并给出处置指引，而不是让携带置信度的写入被静默丢弃。

**来源**：代码证据（`collection_schemas.py:274-311` 无迁移 + `viking_vector_index_backend.py:178-185` 按 schema 静默过滤字段 + 提交 `4d00feac`）。

**业务价值**：静默丢弃会让用户以为置信度已生效而实际未生效，属不可接受的失败模式。

**验收标准**：

- [ ] 启动或首次写入时能检测"集合 schema 缺少 confidence 字段"这一状态。
- [ ] 该状态下有明确的可观测信号（启动日志告警或健康检查项），并给出处置指引（重建集合或按文档补齐字段）。
- [ ] 不得以"静默丢弃字段"作为最终行为而不给出任何信号。

**优先级**：高

---

### FR-008: 文档口径同步

**需求描述**：
当 本次改造完成后
系统应该 同步更新 CLI 帮助、API 文档与检索结果字段说明。

**来源**：提交 `34b5a889`/`21c58bd8` 的文档同步惯例。

**验收标准**：

- [ ] `crates/ov_cli/README.md` / `README_CN.md` 中 `add-resource` 的示例段（现为 `crates/ov_cli/README.md:250`、`:253`、`:260`、`:294`；这两个文件**没有 Markdown 参数表**）包含 `--confidence` 用法。
- [ ] `docs/zh/api/02-resources.md`（现有 `tags`/`tag_mode` 行位于 `:177`）与 `docs/en/api/02-resources.md` 的请求字段表包含置信度。
- [ ] `docs/zh/api/06-retrieval.md` 与 `docs/en/api/06-retrieval.md` 的检索结果字段说明包含置信度。
- [ ] `docs/zh/concepts/05-storage.md` 与 `docs/en/concepts/05-storage.md:99-114` 的 Context 集合 Schema 表包含新字段。
- [ ] 旧示例串零残留。

**优先级**：中

---

### FR-009: 相关性门槛不得掺入置信度、排序使用加权分

**需求描述**：
当 服务端执行阈值过滤，或任何调用方按分数做相关性判定时
系统应该 以**未加权的检索分**为判定依据；只有当需要排序或展示名次时才使用 `score = raw_score × confidence`。

**来源**：用户 2026-10-10 追问（"前者该保留，后者该丢，这个怎么实现"）—— 该区分只能通过"两个维度分工"实现。

**业务价值**：这是"语义相关但被人工降权"与"语义本身就弱"可被区别对待的**唯一实现方式**。若门槛也用加权分，两者恒等，区分能力为零。

**口径（与 FR-003 的三层命名严格一致）**：

- 服务端门槛比对的仍是 `_final_score`（hotness 混合**之前**的检索分），行为**不变**；
- 默认配置 `hotness_alpha = 0.0` 下 `_final_score == raw_score`，故"门槛看原始分"在默认配置下字面成立；
- `hotness_alpha > 0` 时两者相差 hotness 项 —— 该差异是**既有行为**，本需求不修改它；结论"**置信度不参与任何门槛**"在两种配置下都成立。

**验收标准**：

- [ ] 服务端 `_passes_threshold`（`hierarchical_retriever.py:365-369`）的输入保持为 `_final_score`（`:200`、`:467`、`:535` 三处调用点均不得改为加权分）；本轮改造**不改变**服务端门槛行为。
- [ ] 现有对外参数的语义与行为均不变，且文档明确其作用对象为未加权的检索分：`score_threshold`（`openviking/server/routers/search.py:131/192/290`）、MCP `min_score`（`openviking/server/mcp_endpoint.py:252/280/334`）、CLI `-t/--threshold`（`crates/ov_cli/src/main.rs:775-777`、`:847-849`）。**行为不变的验证方式**：同一查询、同一数据集下，改造前后通过门槛的 URI 集合完全一致。
- [ ] 对外契约文档明确写明分工口径："**相关性门槛用未加权分；排序与展示用加权分**"。
- [ ] 本服务内部任何**在折扣之后**使用分数的位置，其用途必须是排序/展示而非相关性门槛。已逐处核查的现有位置与判定：`hierarchical_retriever.py:657`（重排 → 排序）；`openviking/retrieve/context_assembler/gather.py:250`（`ranked_score = score - penalty` → 排序）；`:410`（排序键）；`:421`（`_dedupe_candidates` 去重取较高分）；`:166-177`（`dedupe_keep_best`，比较在 `:175`，去重取较高分）；`openviking/storage/viking_fs/_semantic.py:261/403`（仅向下透传阈值，**返回后无二次过滤**）。
- [ ] **与 `other_peer_penalty` 的叠加口径（唯一，无歧义）**：`other_peer` 记录**允许同时承受**两者的作用 —— `gather.py:242` 读取的 `score` 已含置信度折扣，`:250` 再减去 peer penalty。这是**有意为之**：两者的语义相互独立（置信度 = 人工可信度；peer penalty = 跨 peer 归属惩罚），且后者有界（默认 0.02~0.1，`params.py:107-115`，`_clamp_penalty` 限 `[0,1]`，`:168-173`）。**验收方式**：构造一条 `origin = "other_peer"`、`confidence = 0.5` 的记录，断言 `ranked_score == raw_score × 0.9 - penalty`（而非只扣其中之一），用测试固化该口径。
- [ ] 本期下游改造范围与 Q9 一致：**只改 OpenViking 自身可控的面**（CLI / MCP 文本 / `<memory>` 标签 / `web-studio` / 自带记忆 agent 工具）。仓库内的示例与集成（`bot/vikingbot`、`examples/openclaw-plugin`、`integrations/langchain`）**本期不改**；其"仍按加权分过滤"的行为变化必须在变更说明中逐条点名（见 R-4、R-9），不得沉默。
- [ ] 若消费方需要"用未加权分判定相关性、用加权分排位"，无需做除法即可实现（`raw_score` 与 `score` 均已给出，`confidence = 0` 时仍成立）。

**优先级**：高

---

### FR-010: 置信度与原始分在人/LLM 可见面上必须渲染

**需求描述**：
当 检索结果被渲染为人类可读文本或注入 LLM 上下文时
系统应该 同时呈现 `score`、`raw_score` 与 `confidence`，而不是只呈现加权后的 `score`。

**来源**：用户 2026-10-10 追问"客户端拿到置信度后会有相应的调整吗，还是被忽略了" —— 已核实默认会被静默忽略（详见风险 R-9）。

**业务价值**：MCP 返回的是**已排好序的列表**，LLM 通常直接采纳顺序、不会主动重排；若不在渲染文本中给出置信度与原始分，这个字段对 LLM 场景等于不存在。

**验收标准**：

- [ ] CLI 卡片（`crates/ov_cli/src/commands/search.rs:421-429`，解析函数 `:592-600`）同时展示三个数，例如 `score 0.210 (raw 0.420 × conf 0.500)`；缺失时按 `raw_score == score`、`confidence = 1.0` 展示。
- [ ] MCP 文本（`openviking/server/mcp_endpoint.py:409-410`）同步展示；并在工具 docstring（`:257`、`:301-302` 现仅声明 "with URI, abstract, and score"）中补充字段说明，否则 LLM 不会理解该数字。
- [ ] 注入 LLM 的 `<memory>` 标签（`openviking/retrieve/context_assembler/render.py:36-42`，现为 `score="{entry.score:.2f}"`）增加 `confidence` 与 `raw_score` 属性。
- [ ] Web Studio 结果行（`web-studio/src/routes/retrieval/-components/retrieval-results.tsx:427-428`）与详情面板（`retrieval-detail-sheet.tsx:99-100`）同步展示。
- [ ] **Web Studio 的字段白名单必须同步**：`web-studio/src/lib/retrieval.ts:101-125` 的 `normalizeFindItems` 是逐字段拷贝的白名单（现只拷 `abstract` / `category` / `context_type` / `level` / `match_reason` / `overview` / `score` / `uri`），必须新增 `raw_score` 与 `confidence`，否则**管理台会静默丢弃这两个字段**（服务端发了也看不到）。
- [ ] **自带记忆 agent 工具不得裁掉新字段**：`openviking/session/memory/tools.py:44` 现为 `return [{"uri": item["uri"], "score": item["score"]} for item in filtered[:limit]]`，会静默丢弃 `raw_score` 与 `confidence`；改造后必须至少保留 `raw_score` 与 `confidence`（或在函数注释中显式说明裁剪理由并记录该决定）。该工具是 OpenViking 自身消费检索结果的唯一代码路径，若它都丢弃字段，则 R-9 的"自有面已覆盖"不成立。
- [ ] `POST /api/v1/skills/find` 的结果构造（`openviking/server/routers/skills.py:230-241`）在字段可用时同步透出 `raw_score` 与 `confidence`。
- [ ] 展示口径统一：`score` 与 `raw_score` 保留 3 位小数，`confidence` 保留 3 位小数（与既有 `score {score:.3}` 一致）。

**优先级**：中

---

### FR-011: 各调用面的排序一致性

**需求描述**：
当 不同调用方（Web Studio 管理台 / CLI / MCP / REST / 服务内部记忆 agent）以**同一 REST 端点 + 同一组请求参数**发起检索时
系统应该 返回**完全相同的排序**；打分的唯一出口是服务端检索管线，任何调用面都不得在服务端顺序之上重新排序。**"同一端点"是本条的前提**：跨端点（`find` 与 `search`，或 `mode="list"` 与 `mode="context"`）不属于本需求的"一致性"范围，其原因见下方 AC7。

**来源**：用户 2026-10-10 追问（"如果在最后的阶段执行，那 openviking 的管理台上的检索查询，会不会和客户端的检索查询，出现排序不一致的情况"）。

**业务价值**：本次改造改变了排序分（`score`）。若各调用面对"服务端分"的使用口径不一致，同一个知识库在不同入口会呈现不同顺序，用户会失去对分类效果的信任。

**事实基础（已核实）**：

- 打分唯一落点：`HierarchicalRetriever.retrieve()`（`hierarchical_retriever.py:101`）；全仓仅两个调用入口 —— `openviking/storage/viking_fs/_semantic.py:256`（find）与 `:399`（search）。折扣在 `_convert_to_matched_contexts`（`:590-658`）内、**响应序列化之前**执行。
- 管理台与 CLI / MCP 走**同一组 REST 端点**：`web-studio/src/lib/retrieval.ts` 的 `fetchFind`（`:187-193`，调 `postSearchFind`）与 `fetchSearch`（`:224-230`，调 `postSearchSearch`）→ `POST /api/v1/search/find`、`/api/v1/search/search`，与 `crates/ov_cli/src/client.rs:693-725`（find）、`:727-761`（search）完全一致。
- 管理台的 `console` 路由（`openviking/server/routers/console.py:15`）只提供 `dashboard/summary`、`tokens`、`context-commits`、`audit`，**不含检索**。
- **结论：同一组参数下排序天然一致；不一致只可能来自"参数差异"或"消费端二次重排"。**

**验收标准**：

- [ ] 同一查询 + 同一端点 + 同一组参数（`target_uri` / `level` / `context_type` / `filter` / `tags` / `score_threshold` / `limit` / `mode`）下，返回的 URI 顺序在 CLI 与 Web Studio 上**逐项一致**，并留下可复现的对照证据。覆盖范围至少三条路径：`POST /api/v1/search/find`、`POST /api/v1/search/search`（`mode="list"`）、`POST /api/v1/skills/find`（`openviking/server/routers/skills.py:566-660`）。
- [ ] 服务端是唯一打分点：不得在任何路由层、序列化层或前端层重新计算/调整 `score`。
- [ ] CLI 侧不得对返回结果做客户端排序（已核实 `crates/ov_cli/src/commands/search.rs` 当前无排序代码，需以测试固化）。
- [ ] Web Studio 侧同样不得对**检索结果**排序（`web-studio/src/lib/retrieval.ts` 与 `web-studio/src/routes/retrieval/**` 中**无任何针对检索结果的排序**；其中 `routes/retrieval/-components/retrieval-controls.tsx:87` 的 `.toSorted()` 只用于 UI 层级选项，与检索结果无关）；`normalizeFindItems`（`retrieval.ts:101-125`）只做字段归一化（`.filter().map()` 保序），不得改变顺序。
- [ ] 服务内部唯一的检索消费者 `openviking/session/memory/tools.py:44` 在保留字段后仍须保持服务端顺序（不得重排）。
- [ ] 消费端若需做**相关性判定**，一律以 `raw_score` 为准（FR-009）。**本条约束的是消费端**：消费端不得按 `raw_score` 重新排序；服务端内部的 tie-break（FR-003 中 `score` 相同时按 `raw_score` 降序）属服务端顺序的组成部分，不受本条限制。
- [ ] 以下**既有差异不属于本次改造引入**，必须在文档中写明，避免被误判为回归：
  - **`find` 与 `search` 的 mode 不同**：`find` 强制 `RetrieverMode.QUICK`（`_semantic.py:261`）→ `apply_hotness=False`、无 rerank、无传播；`search` 不传 mode（`_semantic.py:399-406`）→ 默认 `THINKING if rerank_client else QUICK`。**参数相同但一个走 `find` 一个走 `search` 时，排序本来就可能不同。**
  - **`search` 的 `mode="list"` 与 `mode="context"` 在服务端即会重排**：`openviking/retrieve/context_assembler/gather.py:335/379/389` 按 `_rank_key`（`:408-410`）排序，其值取自 `Candidate.ranked_score = score - penalty`（`:250`），因此同一查询在两种 mode 下顺序不同，属既有行为。
  - **默认阈值不同**：REST / CLI / Web Studio 默认不传 `score_threshold`（落到 `RerankConfig.threshold` = 0.1）；MCP `find` / `search` 默认 `min_score=0.35`（`mcp_endpoint.py:252/369`）。
  - **`examples/openclaw-plugin` 会二次重排**：`memory-ranking.ts:243` 的 `rankForInjection` 在服务端顺序之上再按 lexical overlap / category / resourceType 加权排序；同类还有 `memory-tools.ts:301` 的 `>=0.85` 判定。

**优先级**：高

## 非功能需求

### NFR-001: 兼容性与零回归

当 升级到本版本并连接既有向量集合时
系统应该 保证未设置过置信度的资源其检索结果分数与排序与升级前一致。

**判定依据（可机械对照）**：以 `raw_score` 为对照量 —— 改造后任一条记录的 `raw_score` 应与改造前同一查询、同一条记录的 `score` 逐位一致；`confidence = 1.0` 时 `score == raw_score`。

### NFR-002: 性能

当 执行一次检索时
系统应该 不因本次改造引入额外的向量库查询或网络往返；单次检索的向量库调用次数与改造前相同。

### NFR-003: 可解释性

当 用户看到一个较低的检索分数时
系统应该 能从返回结果中判断该低分源于语义相似度低还是源于人为置信度低。

### NFR-004: 数值健壮性

当 候选记录的置信度缺失、非数值、非有限或**超出 `[0,1]`** 时
系统应该 在读侧将其归一为合法值（缺失/非数值/非有限 → `1.0`；越界 → clamp 到 `[0.0, 1.0]`），且对外分数不出现 `nan`/`inf`（缺失兜底口径与 `hierarchical_retriever.py:604/627-628` 一致，clamp 见 FR-003 的越界读侧兜底 AC）。

### NFR-005: 降权幅度有界

当 任一记录被施加置信度折扣时
系统应该 保证折扣因子恒落在 `[1-λ, 1]`（λ = 0.2，即 `[0.8, 1.0]`）区间内，且"未加权分相对差 `(raw_a - raw_b)/raw_a` 达到或超过 `λ`（= 20%）的两条记录不得因置信度而换位"（相对差定义与 FR-003 完全一致，不得换分母）。

**判定依据**：对同一查询的全部返回项断言 `raw_score × 0.8 ≤ score ≤ raw_score`；并用 FR-003 的"换位边界断言"用例覆盖跨档不反超。

## 约束条件

### 技术约束

- 不改变向量维度、embedding 模型与现有字段类型。
- 新字段的**载体清单（缺一不可）**：
  1. `crates/ov_cli/src/main.rs:335-465`（clap 参数）
  2. `crates/ov_cli/src/handlers.rs:16-132`、`crates/ov_cli/src/commands/resources.rs:6-67`、`crates/ov_cli/src/client.rs:813-861`
  3. `openviking/server/routers/resources.py:31-130`（`AddResourceRequest`，`extra="forbid"`）与 `:290-310`（下传）
  4. `openviking/service/resource_service.py:1386-1410`、`:120-139`（保留字段表）、`:288-296`（ingest kwargs）、`:1101-1102`（SOURCE 建消息）、`:1889-1890`（POST_PROCESS 建消息）、`:728-729`、`:774-777`（消费）
  5. `openviking/storage/queuefs/add_resource_msg.py:60-62`（消息字段）与 `from_dict`（`:100-207`）
  6. `openviking/utils/ingest_options.py:13-59`（`from_value` / `to_dict` / 构造）
  7. `openviking/utils/embedding_utils.py:86-96`（`_apply_ingest_options` 与其早退分支）
  8. `openviking/storage/queuefs/semantic_msg.py`（`ingest_options` 序列化）与 `semantic_dag.py`（透传）
  9. `openviking/storage/collection_schemas.py:84-133`（Fields，含 `DefaultValue: 1.0`）
  10. `openviking/storage/viking_vector_index_backend.py:34-42`、`:50-66`（两个输出白名单）
  11. `openviking/storage/ovpack/index.py:22-32`（`PORTABLE_VECTOR_SCALAR_FIELDS` / `EXPORT_VECTOR_FIELDS`，导出投影）、`openviking/utils/embedding_utils.py:65-74`（`_PORTABLE_SCALAR_FIELDS`，ovpack **import recompute 分支**的写入白名单，经 `ovpack/operations.py:365-372 → index_dir/index_file → _apply_scalar_overrides` 生效）、`openviking/storage/vector_migration.py:18-35`（`VECTOR_MIGRATION_OUTPUT_FIELDS`，读侧投影）；后两者是**两套独立白名单**，只改前者仍会在 import 重新向量化时丢失置信度
  12. `openviking/retrieve/hierarchical_retriever.py:590-658`（有界折扣与排序；`:605-626` 计算未加权分并在 `:624`/`:626` 之后分别产出 `raw_score` 与 `score`；`:657` 重排需加 `raw_score` 为 tie-break）；并新增模块级常量 `CONFIDENCE_PENALTY_LAMBDA = 0.2`（λ 的落点，本期不配置化）
  13. `openviking_cli/retrieve/types.py:276-289`（新增 `confidence` 与 `raw_score` 两个字段，追加在 `search_tags` 之后并保留默认值）、`:376-383`（`_context_to_dict` 输出两个新键）、`:394-410`（`_query_result_to_dict` 的 provenance 分支同步输出）、`:416-427`（`_parse_context` 回读；provenance 反序列化本期不做）
  14. 展示与渲染读取点：`crates/ov_cli/src/commands/resources.rs:65`（导入完成后回显生效置信度）、`crates/ov_cli/src/commands/search.rs:421-429/592-600`、`openviking/server/mcp_endpoint.py:409-410`（含 docstring `:257`/`:301-302`）、**`openviking/retrieve/context_assembler/gather.py:33-46`（`Candidate` 需新增 `confidence` 与 `raw_score` 字段）与 `:242-255`（`_build` 需读取并透传这两个字段）** —— 缺此两处则 `<memory>` 标签拿不到值、FR-010 AC3 不可实现、`search mode="context"` 的 `entries[]` 也无法输出新字段、`openviking/retrieve/context_assembler/models.py:17-35`（`AssembledEntry` 字段块 `:17-23` 需新增两个字段，`to_dict` `:25-35` 需同步；`AssembleResult.to_dict` `:46-52` 输出 `entries[]`）、`openviking/retrieve/context_assembler/budget.py:63`（`AssembledEntry` 构造点）、`openviking/retrieve/context_assembler/render.py:36-42`（`<memory>` 标签增加 `confidence` 属性）、**`web-studio/src/lib/retrieval.ts:101-125`（`normalizeFindItems` 逐字段白名单，必须新增 `raw_score` 与 `confidence`，否则管理台静默丢弃）**、`openviking/server/routers/skills.py:230-241`、`web-studio/src/routes/retrieval/-components/{retrieval-results,retrieval-detail-sheet}.tsx`、`openviking/session/memory/tools.py:44`（自带记忆 agent 工具的字段裁剪）
  15. 同时存在 MCP 复用入口 `openviking/server/mcp_endpoint.py:933-950` 与 `openviking/server/resource_ingest.py:22-76`，需一并评估是否透出
- 集合只在不存在时创建（`collection_schemas.py:274-311`）；自动迁移已移除（`4d00feac`）；处置方式见 FR-007。
- `score` 不保证落在 `[0,1]`：`_rerank_scores`（`hierarchical_retriever.py:371-419`）是"逐条用 rerank 原值覆盖 fallback 值"，无 min-max 归一化；`_normalize_result_score`（`openviking/storage/vectordb_adapters/base.py:82-86`）也只做有限性检查。因此 `score` 不表示概率 —— 这正是采用**乘性相对折扣**（而非加性绝对扣分）的原因：折扣因子与量纲无关。
- 置信度是人工输入的标量，不与 `active_count` / `hotness`（`retrieve/memory_lifecycle.py:21-63`）混为一个概念。
- 命名冲突已核查：仓库内既有 `confidence` 出现在 `session/memory/patch_merge_context_provider.py:25`（记忆补丁元数据）与 `session/train/**`（RL 训练梯度置信度），二者均与检索打分无关，不构成冲突。

### 业务约束

- 置信度只影响资源类记录；memory / skill 记录无该字段，按 1.0 参与。
- 本期不做服务端按置信度过滤（不新增过滤 DSL 字段、不加 `ScalarIndex`）。
- 阈值语义不改：`_passes_threshold`（`:365-369`）与默认阈值（`RerankConfig.threshold` 默认 `0.1`，`openviking_cli/utils/config/rerank_config.py:46-47`）保持原样。

## 风险识别

| 编号 | 风险 | 证据 | 处置 |
|------|------|------|------|
| R-1 | **缺省值写成 0.0 会导致未带置信度的记录分数归零** | `data_processor.py:92-104` `TYPE_DEFAULTS["float32"]=0.0`；`:120-141` 优先取 schema `DefaultValue` | 强制 `DefaultValue: 1.0`（FR-002 AC1） |
| R-2 | **存量集合不会自动获得该字段**，写入被静默过滤 | `collection_schemas.py:274-311`；`viking_vector_index_backend.py:178-185`；`4d00feac` | FR-007 要求显式检测与信号 |
| R-3 | 若乘法放在阈值判定之前，低置信记录会**静默消失**而非下沉 | 阈值调用点 `hierarchical_retriever.py:200/467/535` 均早于 `:605-626` | FR-003 固定作用点在阈值之后 |
| R-4 | 下游用**加权后的** `score` 做二次过滤，会把"语义相关但被人工降权"的记录误删（正是 FR-003 用户样例中应被保留的 A） | MCP `min_score=0.35`（`mcp_endpoint.py:252/369`，该值向下透传、作用在 raw 上，**不受影响**）；`bot/vikingbot/config/schema.py:853`（0.35）；`examples/openclaw-plugin/plugin/openviking-memory-tools.ts:301`（`>=0.85` 删除判定）；`bot/vikingbot/agent/tools/ov_file.py:366-375`；`bot/vikingbot/agent/memory.py:319`；`bot/vikingbot/agent/remote_skills.py:409` | 由 FR-009 与 FR-004 共同兜住：`raw_score` 直接对外给出，**下游若需按相关性过滤，可改读 `raw_score`**；本期不改动它们（与 FR-009 AC5、Q9、不包含范围一致），其行为变化必须在变更说明中逐条点名 |
| R-5 | 备份/迁移丢字段 | `ovpack/index.py:22-32`、`vector_migration.py:18-35` 均为白名单投影 | FR-002 AC3 |
| R-6 | 下游插件已在消费 `score` 且部分依赖其绝对量级 | 同上 R-4 | 在变更说明中明示"低置信资源的分与位次会下降"，由使用方自行调整其二次阈值 |
| R-7 | `update_search_tags` 的"读回再整条覆盖"路径可能擦除置信度 | `viking_vector_index_backend.py:1034-1134`（`get` → 改字段 → `upsert` 无 `partial_update`）；`get`（`:462-470`）无字段投影，返回整条记录 | 经核查 `get` 返回整条记录，**不构成擦除风险**；设计阶段需补一个回归用例固化该结论 |
| R-8 | **content_write / reindex 重写路径会主动清空 `IngestOptions`**，置信度只能靠未被文档化的 `partial_update=True` 侥幸保留 | `openviking/storage/queuefs/semantic_dag.py:522-533`（`_ingest_options_for_file` 在 `generation_trigger == "content_write"` 且非变更路径时返回空 `IngestOptions()`；`_ingest_options_for_directory` 只要该 trigger 成立即返回空）；trigger 置位点 `openviking/storage/content_write.py:626` 与 `openviking/service/reindex_executor.py:1062`；旧值保留依赖 `collection_schemas.py:793-796` 强制的 `partial_update: True` | 见待确认事项 Q8；无论选哪种口径，都必须补一条"重写/重索引后置信度不变"的回归用例，并在设计中显式记录 `partial_update` 依赖 |
| R-9 | **新增字段默认会被所有消费端静默忽略**（"以为生效了"的失败模式，与 R-2 同类） | `openviking/session/memory/tools.py:44` 显式只保留 `{uri, score}`；`openviking/retrieve/context_assembler/render.py:39` 只渲染 `score`；`openviking/server/mcp_endpoint.py:409-410` 只渲染百分比 `score`；`examples/openclaw-plugin/memory-ranking.ts:44/49/243` 只按 `score` 排序/过滤/加权；`bot/vikingbot/agent/tools/ov_file.py:375`、`agent/memory.py:319` 只按 `score` 过滤；`integrations/langchain/.../retrievers.py:248`、`store.py:262` 只取 `score`；`crates/ov_cli/src/commands/search.rs:421-429`、`web-studio/.../retrieval-results.tsx:427-428` 只展示 `score`（以上 10 处行号已在审查轮次 3 逐条核实） | 由 **FR-010（含 `session/memory/tools.py:44` 的专属 AC）** 覆盖"OpenViking 自身可控面"，并已把 FR-010 与 NFR-003 写入验收总则使其可验收；`bot/vikingbot` / `examples/openclaw-plugin` / `integrations/langchain` 三处按 Q9 本期不改，但必须在变更说明中逐条点名其行为变化 |
| R-10 | **λ = 0.2 是全局单一常数**，对所有资源类别一视同仁；对"高价值但低置信"的资源（如人工标注为 0.3 的权威文档）无法区别对待 | FR-003 口径；对比既有 `other_peer_penalty` 是**按类别**给不同惩罚（`params.py:107-115`：events 0.1 / preferences 0.02） | 本期不做按类别差异化（避免投机式可配置化，见规则"Simplicity First"）；若后续确需按类别调整，再评估是否引入配置项（Q11） |
| R-11 | **λ 的值是经验值**，0.2 未经过效果实测；过小则置信度不起作用，过大则逼近无界乘法 | FR-003 口径；λ=1 已被用户反例否定、λ=0 已否定"完全不起作用" | 本期固定 0.2；上线后以"低置信资源的平均位次变化"作为观测指标，必要时再调整（Q11） |
| R-12 | **置信度折扣与 `other_peer_penalty` 会叠加**：`gather.py:242` 读到的 `score` 已含折扣，`:250` 又减去 peer penalty，同一条记录可能被"双重打压" | `openviking/retrieve/context_assembler/gather.py:242-250`；`params.py:107-115`（默认 penalty 0.02~0.1）、`:168-173`（clamp `[0,1]`） | **已决策为"有意叠加"**（两者语义独立，且 penalty 有界），并在 FR-009 中固化为可验收的唯一口径 + 测试用例；本行仅作留痕，供后续调整 penalty 默认值时参考 |
| R-13 | **既有消费端二次重排会被误判为"改造引入的排序不一致"**：`examples/openclaw-plugin` 在服务端顺序之上再排一次 | `examples/openclaw-plugin/memory-ranking.ts:243`（`rankForInjection`：`clampScore(item.score) * weights.baseScore + lexicalOverlapBoost + categoryBoost + ...`）、`:44`（`sort` 降序）、`:49`（`< scoreThreshold` 过滤） | FR-011 已把"既有差异"逐条写明（mode 差异、默认阈值差异、插件二次重排），避免归因错误；本期不改动这些消费端 |

## 验收总则

项目交付时必须满足：

- [ ] FR-001 ~ FR-005、FR-007、FR-009、FR-010、FR-011 全部实现并通过单元测试。
- [ ] NFR-001 存量检索结果零回归（以 `raw_score` 与改造前 `score` 逐位对照），有可复现的对照证据。
- [ ] NFR-003 可解释性达标：人/LLM 可见面上能同时看到 `score`、`raw_score`、`confidence`。
- [ ] NFR-005 有界性达标：全部返回项满足 `raw_score × 0.8 ≤ score ≤ raw_score`，且换位边界用例通过。
- [ ] 通过完整的系统测试与人工回归。
- [ ] 文档完整且与实现一致。

## 范围说明

### 包含范围

- `ov add-resource` 新增 `--confidence` 参数（CLI → HTTP → service → 队列消息 → `IngestOptions` → 向量记录）。
- 向量集合新增资源级 `confidence` 标量字段及其全部载体白名单（检索、备份/迁移）。
- 检索排序分在门槛判定之后按置信度做**有界折扣**（λ = 0.2），并据此重排；同时对外暴露未加权原始分 `raw_score`。
- 检索结果对外返回置信度（REST / CLI / MCP / skills）。
- 存量集合字段缺失的显式检测与信号。
- 相关文档与帮助文本同步。

### 不包含范围

- 按置信度做服务端过滤/筛选参数（不加过滤 DSL 字段，不加 `ScalarIndex`）。
- 对置信度做自动推断、模型打分或时间衰减。
- 已导入资源的批量回填置信度入口（`ov attrs set-confidence` 之类）。
- 按文件/路径映射置信度（目录内高低置信混排需分批导入）。
- 修改下游消费方（vikingbot / openclaw-plugin / langchain）各自的二次阈值。
- 置信度的权限控制、审计与统计报表。
- 修改 `_passes_threshold` 的阈值语义与默认阈值。

## 待确认事项

> 以下为需要用户裁决的点。**若不回复，按"当前采用口径"执行**。

| 编号 | 问题 | 当前采用口径 | 备选（如选此项请明确回复） |
|------|------|--------------|---------------------------|
| Q1 | 是否回传置信度？ | ✅ **已裁决**：回传。用户 2026-10-10 原话"**你说的非常对，那是不是应该 score 不变，也不做乘法，而是增加一个置信度返回**"后，主代理给出"会被全部下游静默忽略"的证据与四方案对比，用户随后回复"**那就是还是应该相乘后排序**"，据此确认回传。`find`/`search` 结果中新增 `confidence`，与 `score`、`raw_score` 并列（FR-004） | ~~不回传~~（已否决：会被全部下游静默忽略） |
| Q2 | 乘法的位置 | ✅ **已裁决**：相乘后排序。用户 2026-10-10 原话"**那就是还是应该相乘后排序，但是「语义 0.42 × 置信 0.5」还是「语义 0.21 × 置信 1.0」，这个怎么实现呢**"。乘法在 `_convert_to_matched_contexts` 内、`_passes_threshold` 之后（FR-003） | ~~阈值判定之前~~（已否决：低置信资源会跌破阈值而从结果中消失，等于"软删除"） |
| Q3 | 目录内高低置信混排 | **分批导入**（一次导入一个置信度值），不实现按文件映射（FR-006） | 本期实现 `--confidence-map`（路径→置信度映射），工作量与校验规则显著增加 |
| Q4 | 是否需要后续修改已导入资源的置信度 | **不做**；重复导入同一 URI 即可覆盖（FR-005 AC5），已写入"不包含范围" | 增加 `ov attrs set-confidence` 与对应 REST 接口 |
| Q5 | 取值区间与越界行为 | `[0.0, 1.0]` 闭区间；越界**拒绝**并报错，不静默截断（FR-005 AC2）。因 FR-004 直接给出 `raw_score`，**不再需要"`confidence > 0`"这一约束**（不需要做除法反推原始分） | 越界自动 clamp 到区间内 |
| Q6 | 存量集合如何获得该字段 | **显式检测 + 告警 + 文档化处置步骤**，沿用 `4d00feac` 不自动迁移的决策（FR-007） | 启动时自动为存量集合补字段（需评估四类向量库后端的一致性）；或提供一次性迁移脚本 |
| Q7 | 重复导入时未指定置信度的语义 | ✅ **已裁决（2026-10-10 用户确认："Q7 缺省覆盖为 1.0，没问题"）**：**覆盖为 1.0** —— 服务端在未收到该字段时显式写入 1.0，使"重新导入即可重置"成立（FR-005 AC5） | ~~保留旧值~~（已否决） |
| Q8 | 重写/重索引路径（`ov write`、watch 增量、reindex）如何处理置信度 | **保留旧值**，并要求补一条"重写/重索引后置信度不变"的回归用例；设计中显式记录对 `collection_schemas.py:793-796` 强制 `partial_update=True` 的依赖（R-8） | **重写即重置为 1.0**：认为置信度属于"本次导入请求"而非资源属性。此口径需同步修改 FR-005，且会导致 watch 每次刷新都清掉人工标注，**不推荐** |
| Q9 | 下游消费端的二次过滤是否本期一并改造为读 `raw_score`？ | **仅改造 OpenViking 自身可控的面**：CLI / MCP 文本 / `<memory>` 标签 / `web-studio` / `session/memory/tools.py:44`（自带记忆 agent 工具）。仓库内的示例与集成（`bot/vikingbot`、`examples/openclaw-plugin`、`integrations/langchain`）**本期不改**，但在变更说明中逐条点名其行为变化（R-4 / R-9） | **全部改造**：范围扩大到 `bot/vikingbot`、`examples/openclaw-plugin`、`integrations/langchain` 共 6 处阈值读取点，工作量与测试面显著增加 |
| Q10 | 是否需要"按置信度硬排除"的能力？ | **本期不做**：`confidence = 0.0` 只表示"最强降权"（`factor = 0.8`，记录仍会返回）。本期只提供**软降权** | **本期提供**：新增 `min_confidence` 过滤参数（并需把 `confidence` 加入 `ScalarIndex`，`collection_schemas.py:134-153`），或约定 `confidence = 0` 表示"永不返回"（后者会让 `0.0` 从"最强降权"变成"硬排除"，语义更重、更难挽回） |
| Q11 | λ 是否配置化？0.2 是否为最终值？ | ✅ **已裁决**：用户 2026-10-10 原话"**非常好，按照你的推荐来**"，即接受主代理推荐的 λ = 0.2。**本期固定 0.2，不引入配置项**（避免投机式可配置化）。落点为模块级常量（`hierarchical_retriever.py` 顶部 `CONFIDENCE_PENALTY_LAMBDA = 0.2`），与 `hotness_alpha` 走 `RetrievalConfig` 的做法不同 | **配置化**：加入 `RetrievalConfig`（`openviking_cli/utils/config/retrieval_config.py:10-17`，与 `hotness_alpha` 同处），取值范围 `[0.0, 1.0]`；好处是可运行时调整，代价是多一个需要文档化与验证的配置面 |

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
| ---- | ---- | -------- | ------ |
| v1.0 | 2026-10-10 | 初始版本 | AI 助手 |
| v1.1 | 2026-10-10 | 按第 1 轮需求审查结论修订：补齐全部字段载体清单与两处输出白名单；强制 `DefaultValue: 1.0`；固定乘法作用点为阈值之后并消除与 Q1 的互斥表述；收敛 FR-001/FR-005/FR-006 的二义验收标准；新增 FR-007（存量集合字段可用性）与风险章节；为每条 FR 标注来源；明确 `score` 不保证 0~1、`ScalarIndex` 本期不加 | AI 助手 |
| v1.2 | 2026-10-10 | 按第 2 轮需求审查结论修订：载体清单补 `_PORTABLE_SCALAR_FIELDS`（ovpack import recompute 写入白名单）并修正 `vector_migration` 的投影性质；FR-002 AC5 补 `resource_service.py:288-296` 这道更靠前的早退闸门；FR-005 AC5 依据 `collection_schemas.py:793-796` 强制 `partial_update=True` 的实测机制改写，取消与 `tag_mode` 的错误类比；FR-003 AC5 明确阈值判定口径；FR-008 AC1 改为引用 README 中真实存在的示例段；FR-001 界定本期入口范围（MCP / temp_upload 不加参数）；修正 R-4 的 `bot/vikingbot/agent/remote_skills.py` 路径与 `apply_hotness` 的文件归属；新增 R-8（重写/重索引路径清空 `IngestOptions`）与待确认事项 Q7（重复导入缺省语义）、Q8（重写路径语义） | AI 助手 |
| v1.3 | 2026-10-10 | 按用户决策修订（相乘后排序 + 需要区分"语义相关但被降权"与"语义本身就弱"）：FR-003 改名为"加权 + 保留未加权原始分"，新增 `raw_score` 定义、不变式 `score == raw_score × confidence`、用户样例验收（A 保留 / B 丢弃）与并列 tie-break；FR-004 改为同时回传 `confidence` 与 `raw_score`；新增 FR-009（门槛与排序的维度分工）与 FR-010（CLI / MCP 文本 / `<memory>` 标签 / Web Studio 渲染）；新增 R-9（新增字段会被消费端静默忽略）；更新 R-4 处置、NFR-001 判定依据、载体清单、验收总则；Q1/Q2 标记为已裁决，Q5 取消 `confidence > 0` 约束，新增 Q9 | AI 助手 |
| v1.4 | 2026-10-10 | 按第 3 轮需求审查结论修订：(1) 修正**口径性错误** —— `raw_score` 定义为 hotness 混合**后**的分、而门槛比对的是 hotness 混合**前**的 `_final_score`，二者仅在 `hotness_alpha = 0` 时相等；FR-003 口径改为明确的三层命名表（`_final_score` / `raw_score` / `score`），FR-009 改名为"相关性门槛不得掺入置信度"，并删去"门槛作用在 `raw_score` 上"的错误断言；(2) FR-009 AC5 与 Q9／不包含范围对齐（本期只改自有面，下游不改但须点名）；(3) FR-004 补 provenance 分支（`types.py:394-410`）AC 与 `from_dict` 不解析 provenance 的决定；(4) FR-010 补 `session/memory/tools.py:44` 与 `skills.py:230-241` 的专属 AC；(5) 验收总则纳入 FR-010 与 NFR-003，使 R-9 的缓解措施可验收；(6) 载体清单第 13 项补 `:394-410`；(7) Q1/Q2 补记用户原话作为裁决依据；(8) 修正 `gather.py:177` → `:166-177`（比较在 `:175`） | AI 助手 |
| v1.5 | 2026-10-10 | 按用户裁决（"按推荐来" = λ=0.2 有界加权）修订：**FR-003 从纯乘法改为有界折扣** `score = raw_score × (1 - λ·(1 - confidence))`，λ = 0.2，并给出 λ=0/0.2/1 的连续谱说明；新增**有界性精确定义**（绝对值界与换位界）与对应 AC；说明为何用**乘性相对折扣**而非加性绝对扣分（`score` 无 0~1 归一化，`base.py:82-86`，加性对量纲敏感）；FR-004 不变式同步更新；FR-005 明确 `confidence = 0.0` 为"最强降权"而非硬排除；新增 **NFR-005 降权幅度有界**；载体清单第 14 项补 context 装配链；新增 R-10（λ 全局单一常数）与 R-11（λ=0.2 为经验值）；新增待确认事项 Q10（是否需要硬排除）与 Q11（λ 是否配置化） | AI 助手 |
| v1.6 | 2026-10-10 | 按第 4 轮需求审查结论修订（10 项）：(1) **统一换位界的定义与数值** —— 显式定义 `相对差 := (raw_a - raw_b)/raw_a`，界为 `λ`=20%，并删除 NFR-005 中分母不一致的 `λ/(1-λ)`=25%；(2) **补齐 context 装配链载体** —— 载体清单第 14 项新增 `context_assembler/gather.py:33-46`（`Candidate` 需加两字段）与 `:242-255`（`_build` 需透传），否则 FR-010 AC3 不可实现；(3) 新增**越界读侧兜底 AC**（`confidence = clamp(..., 0, 1)`，防 `confidence=1.5` 导致 `factor=1.1` 反向加成），NFR-004 同步扩到"越界"；(4) **对双重折扣给出唯一口径** —— `other_peer` 记录有意允许"置信度折扣 + peer penalty"叠加，并给出可验收断言；(5) 修正技术约束中残留的 v1.4 纯乘法表述，并把 λ 常量写入载体清单第 12 项；(6) 新增 context 模式 `entries[]` 必须含两个新字段的 AC；(7) 换位边界用例改为**紧边界成对用例**（19% 换位 / 21% 不换位，可区分 λ=0.2 与 0.25）；(8) `models.py` 行号由 `:20-35` 更正为 `:17-35` 并与变更记录一致；(9) 新增 R-12 留痕双重折扣的叠加口径；(10) Q11 补记用户"按推荐来"原话作为 λ=0.2 的裁决依据 | AI 助手 |
| v1.7 | 2026-10-10 | 按用户 2026-10-10 反馈修订：(1) **FR-001 新增"导入完成后必须回显生效置信度"AC** —— Table 输出打印生效值（未指定时 `confidence 1.000 (default)`）、`--json` 输出含该字段、目录导入只打印一次批次值；渲染位置 `crates/ov_cli/src/commands/resources.rs:65`；(2) **Q7 标记为已裁决**（用户确认"缺省覆盖为 1.0"）；(3) **新增 FR-011「各调用面的排序一致性」** —— 核实管理台与 CLI/MCP 走同一组 REST 端点、`console` 路由不含检索、打分唯一落点为 `HierarchicalRetriever.retrieve()`，并逐条写明既有差异；(4) **发现并补记一处新载体缺口** —— `web-studio/src/lib/retrieval.ts` 的 `normalizeFindItems` 是逐字段白名单，不新增 `raw_score`/`confidence` 则**管理台会静默丢弃**；(5) 新增 R-13 留痕"既有消费端二次重排"以免归因错误；(6) 验收总则纳入 FR-011 | AI 助手 |
| v1.8 | 2026-10-10 | 按 v1.7 增量审查结论修订（3 必修 + 5 建议）：(1) **消除 FR-011 需求描述与 AC7 的互斥** —— 需求描述改为"同一 REST 端点 + 同一组参数"，并声明跨端点不属一致性范围；(2) FR-011 AC7 **补第 4 类既有差异** —— `search` 的 `mode="list"` 与 `mode="context"` 在服务端即按 `gather.py:250/408-410` 的 `ranked_score` 重排；(3) 行号精度修正 —— `retrieval.ts:100-126` → `:101-125`（3 处）、`client.rs:693-720/727-756` → `:693-725/:727-761`；(4) FR-011 AC1 覆盖范围扩到 `find` / `search(mode=list)` / `skills/find` 三条路径；(5) AC4 的"无 `.sort(`"改为"无针对**检索结果**的排序"并点名 `retrieval-controls.tsx:87` 的 `.toSorted()` 属 UI 选项；(6) AC6 明确"本条约束消费端，服务端 tie-break 不受限"；(7) FR-001 的 `--json` 键名由"建议"改为"必须"，并点明回显值由 CLI 本地计算、不依赖服务端响应体 | AI 助手 |
