# 资源置信度（resource confidence） 流程状态

> **用途**：记录 aegis-iv-skill 流程的当前进度，支持跨会话/跨窗口恢复。
> 此文件由 AI 在流程关键节点自动更新，下次新开会话时，AI 应先读取本文件以了解上一次的进展。

## 1. 基本信息

- **功能名/Slug**: `resource-confidence`
- **项目名称**: OpenViking 资源置信度（`prds/OpenViking`）
- **创建时间**: 2026-10-10 09:20
- **最后更新**: 2026-10-10 17:25
- **当前模式**: 执行（Phase 4 任务执行）

## 2. Gate 状态机

> 这是 aegis-iv-skill 的状态机核心。AI 根据此表判断当前可执行的操作。

| Gate | 状态 | 说明 |
|------|------|------|
| REQ | 已确认 | 需求是否已获客户确认（用户 2026-10-10 回复口令 `确认需求`，requirements.md v1.8 已落盘） |
| DESIGN | 已确认 | 是否允许进入/展示设计阶段（用户 2026-10-10 回复口令 `确认设计`，design.md v1.1 已落盘） |
| TASKS | 已确认 | 是否允许进入/展示任务编排阶段（用户 2026-10-10 回复口令 `确认任务计划`，tasks.md v1.1 已落盘） |
| EXEC | 允许 | 是否允许执行代码变更 |
| CHECK | 禁止 | 是否允许进入质检阶段 |

**下一口令**: `执行质检`

## 3. 阶段进度概览

| 阶段               | 状态 | 说明 |
|------------------|------|------|
| Phase 1: 需求收集与分析 | ✅ 已完成 | 4 轮审查累计 14/7/3 → 15/6/3 → 12/10/2 → 11/10/3；用户三次变更/补充（相乘后排序 → λ=0.2 有界折扣 → 导入回显 + 排序一致性追问）。最终 v1.8；用户 `确认需求` 已落盘 |
| Phase 2: 任务设计    | ✅ 已完成 | design v1.1 经 1 轮输出前自检（7 必修 + 8 建议已全部修订，含 1 项功能性缺陷 F-A）；用户 `确认设计` 后已落盘 `design.md`（1444 行 / 91,580 B） |
| Phase 3: 任务编排    | ✅ 已完成 | tasks v1.1 经 1 轮输出前自检（9 必修 + 3 建议已全部修订）；用户 `确认任务计划` 后已落盘 `tasks.md`（1375 行 / 58,696 B，33 个任务） |
| Phase 4: 任务执行    | 🚧 进行中 | 27 项开发/测试任务已落地（Python 19 模块 + 3 个 SDK + Rust CLI + Web Studio + 文档 13 文件 + 单测 12 文件 + 夹具/变更说明）；见 §7 任务执行进度 |
| Phase 5: 质检      | ⏳ 等待中 | 由质检代理执行 |
| Phase 6: 人工验收    | ⏳ 等待中 | — |

**图例**：⏳ 等待中 | 🚧 进行中 | ✅ 已完成 | ❌ 已取消 | ⚠️ 阻塞

## 4. 文档产出

| 文档 | 路径 | 状态 |
|------|------|------|
| requirements.md | `prds/OpenViking/spec/resource-confidence/requirements.md` | ✅ 已落盘 v1.8（已确认，557 行，68,452 B） |
| design.md | `prds/OpenViking/spec/resource-confidence/design.md` | ✅ 已落盘 v1.1（已确认，1444 行，91,580 B） |
| tasks.md | `prds/OpenViking/spec/resource-confidence/tasks.md` | ✅ 已落盘 v1.1（已确认，1375 行，33 任务） |
| status.md | `prds/OpenViking/spec/resource-confidence/status.md` | ✅ 已生成 |
| change-note.md | `prds/OpenViking/spec/resource-confidence/change-note.md` | ✅ 已产出（TASK-019 对外变更说明） |
| test-fixtures/ | `prds/OpenViking/spec/resource-confidence/test-fixtures/` | ✅ 已产出（TASK-018：生成脚本 + 基线捕获脚本 + 定点分数数据 + 说明） |
| test-reports/ | `prds/OpenViking/spec/resource-confidence/test-reports/` | ⏳ 目录已建，待人工三测回填（TASK-025~032） |

## 5. 当前阶段详情

### 当前子步骤

- Phase 1 ✅：requirements **v1.8 已落盘**（口令 `确认需求`）
- Phase 2 ✅：design **v1.1 已落盘**（口令 `确认设计`）
- Phase 3 ✅：tasks **v1.1 已落盘**（口令 `确认任务计划`，33 个任务）
- Phase 4 🚧：按依赖顺序执行 TASK-001~024（开发 + 文档 + 单元测试）已完成；TASK-025~032（人工三测）待用户执行
- **Phase 1 循环规则例外说明**：`SKILL.md` §1.2 规则 5 规定审查循环上限 2 轮，需求阶段实际执行 **4 轮**。重开依据：第 3 轮因用户**实质变更需求口径**（从"回传+末端相乘"变为"相乘后排序且必须区分两个维度"）；第 4 轮因用户**再次变更模型**（提出"乘法无界"反例，裁决为有界折扣 λ=0.2）；第 4 轮后追加一次 v1.7 增量审查（用户补充"导入回显 + 排序一致性追问"）。均属新需求的重审，而非同一草稿的反复修订。

### ⚠️ 执行期发现的设计缺口（已修复并留痕）

| 编号 | 缺口 | 发现方式 | 处置 |
|------|------|----------|------|
| DG-1 | design 载体清单只列了 **Rust CLI** 的请求体白名单，遗漏 **3 个 SDK** 的 add-resource 选项载体：`sdk/python/openviking_sdk/options.py:61`（`AddResourceOptions`，其 `_build_options_payload` 对未声明选项**直接抛 TypeError**）、`sdk/go/types.go:24`、`sdk/typescript/src/types.ts:76` | 为写 TASK-024 的 SDK 用例而核对实现时发现 | 三处均补 `confidence`；Python SDK 补 3 例、TS SDK 补 3 例回归测试 |
| DG-2 | design 载体清单未包含 Web Studio 的服务端响应类型 `web-studio/types/ov-server/api/v1/search.ts`（`SearchHit`） | Web Studio 子代理在实现时指出 | 已为 `SearchHit` 补 `raw_score?: number` / `confidence?: number` 与语义注释 |
| DG-3 | design 的 FR-008 文档清单（C16）只列 7 个文件，实际还有 4 处旧口径：`docs/{zh,en}/concepts/07-retrieval.md` 的 `MatchedContext` 结构体、`docs/{zh,en}/guides/09-ovpack.md` 的 portable 标量清单 | TASK-016 子代理在零残留检查时指出 | 4 处均已补齐 |
| DG-4 | Web Studio 的 i18n 文案键与 2 个既有 fixture 因新字段而必须同步修改（超出 design 的 3 文件范围） | TASK-014 子代理实现时发现 | 已确认保留：i18n 是项目强制规则（`i18next/no-literal-string`），fixture 是必填字段变更的直接后果 |

### 环境前提（阻碍部分验证）

| 项 | 状态 | 影响 |
|----|------|------|
| Go 工具链 `GOROOT` 失效（`/usr/local/bin/go` 指向已卸载的 1.23.0） | 已定位并用 `/usr/local/opt/go/libexec/bin/go`（1.27.1）+ `GOCACHE=/tmp` 绕过 | Go SDK 已 `build` + `vet` 通过 |
| Python 原生绑定 `ragfs_python` 未构建 | 已用 `maturin build` 构建 wheel 并 `pip install --target test_data/ov-native`（workspace 内） | `tests/server/*` 的 fixture 可导入 |
| vectordb 引擎扩展（`_x86_sse3` 等，由 `setup.py` + `src/` C++ 构建）未构建 | **未构建** | `tests/server/test_api_resources.py`、`tests/server/test_mcp_endpoint.py` 的会话级 fixture 仍报 `Missing symbol: PersistStore`，197 例无法执行。**这是环境前提缺失，不是本次改动的回归** |
| 沙箱禁止写 `~/.openviking` | 用 `OPENVIKING_CONFIG_FILE=/tmp/ov-pytest.conf`（workspace 内路径）规避 | 使能在沙箱内运行 Python 测试 |
| 既有失败（改前即失败） | `tests/utils/test_circuit_breaker.py` 2 例、`tests/storage/test_collection_schemas.py` 1 例、`tests/client/test_http_client_compact.py` 3 例、web-studio `tsc` 26 条 | 已用 HEAD worktree 基线逐条比对确认**与本次改动无关**，新增 0 条 |

### ⚠️ 执行期环境异常（已变化，需用户知晓）

- **`example-repo/skills/` 目录在会话期间被删除**（约 14:24）：`git status` 显示 `skills/**` 全部为未提交的 `D`。该目录**至今未恢复**。
- **但 skill 符号链接已被重新指向**：`~/.dsh/skills/aegis-iv-skill -> <skills-root>/aegis-iv-skill`（2026-10-10 15:14）。经比对 `SKILL.md`（27549 B，Sep 30 14:23）与 `spec/**` 结构，该副本与本流程此前使用的版本**一致**，因此 Phase 3 起可正常读取清单与提示词。
- **影响与应对**：
  - Phase 2 期间曾用 `git show HEAD:skills/aegis-iv-skill/scripts/doc_consistency.py > /tmp/doc_consistency.py` 兜底；Phase 3 起已可直接调用符号链接下的 `scripts/doc_consistency.py`（`[OK] C1~C6 通过`）。
  - `example-repo/skills/` 的删除**未做恢复动作**（`git checkout -- skills/` 属用户决策）。
- **待用户确认**：该删除是预期操作还是误删？是否需要恢复？

### 当前阶段已完成的工作

- [x] 读取 `aegis-iv-skill/spec/workflow.md`、`spec/prompts/01.requirement_analysis.prompt.md`、`spec/checklists/requirement-review-checklist.md`、`spec/templates/requirements.md`、`spec/templates/status.md`
- [x] 检索知识库：`~/.dsh/skills/aegis-skill/knowledge/`、`example-repo/skills/aegis-skill/knowledge/` —— 未命中 OpenViking 相关条目
- [x] 会话连续性检查：本功能为本会话新建，无历史 status.md
- [x] 历史学习（替代 learn-prior-skill，因 dev-hub 无对应编号）：git 定位 `21c58bd8`（tags 落库模板）、`34b5a889`（add-resource tags 全链路模板）、`4d00feac`（移除自动 schema 迁移）、`4f9840ec`（反例）
- [x] 代码证据：CLI 参数/派发、HTTP body、`AddResourceRequest`、`AddResourceMsg`、`IngestOptions`、`_apply_ingest_options`、集合 schema、三个输出白名单、`data_processor` 默认值机制、`ovpack`/`vector_migration`/`_PORTABLE_SCALAR_FIELDS`、`semantic_dag` 清空分支、强制 `partial_update`、检索分数三层结构（`_final_score` / hotness 混合 / `MatchedContext.score`）、阈值调用点、`MatchedContext` 与两处序列化、CLI/MCP/`<memory>`/Web Studio 渲染点、10 处消费端字段读取点
- [x] 3 个调研子代理并行取证，结果已回收
- [x] 第 1 轮需求审查（自检子代理）：通过 14 / 不通过 7 / 无法核验 3
- [x] 产出 requirements v1.1
- [x] 第 2 轮需求审查：通过 15 / 不通过 6 / 无法核验 3，含端到端操作流推演（5 个链路断点）
- [x] 产出 requirements v1.2
- [x] 用户口径变更答疑：核实 10 处消费端**全部只读 `score`**，结论"只回传不乘分会被静默忽略"，并给出四方案对比
- [x] 产出 requirements v1.3（相乘后排序 + `raw_score` + 门槛/排序维度分工 + 可见面渲染）
- [x] 第 3 轮需求审查：通过 12 / 不通过 10 / 无法核验 2，指出 `raw_score` 与门槛比对对象分属 hotness 混合前后这一**口径性错误**
- [x] 产出 requirements v1.4（三层命名表、provenance 分支、`session/memory/tools.py` AC、验收总则、Q1/Q2 依据补记）
- [x] **算法评估**：对比纯乘法（λ=1，无界）、有界乘法（λ=0.2）、有界减法（加法口径）、分档（tier）、排名融合（RRF）、只提示不改分（λ=0）；结论：λ=0.2 有界乘法是最优，因其**与量纲无关**（`base.py:82-86` 无归一化）且**影响幅度有界**
- [x] 产出 requirements v1.5（λ=0.2 有界折扣、有界性定义、NFR-005、R-10/R-11、Q10/Q11）
- [x] 第 4 轮需求审查：通过 11 / 不通过 10 / 无法核验 3，指出换位界 20%/25% 分母不一致、`Candidate` 断链致 FR-010 AC3 不可实现、越界 `confidence` 反向 boost、双重折扣未决
- [x] 产出 requirements v1.6（统一相对差定义、补 context 装配链载体、越界读侧 clamp、双重折扣唯一口径、context `entries[]` AC、紧边界用例、R-12）
- [x] 用户补充需求与追问：Q7 确认"缺省覆盖 1.0"；新增"导入时回显生效置信度"；追问"管理台与客户端排序是否一致" → 核实管理台与 CLI/MCP 同端点、`console` 路由不含检索、打分唯一落点、前端不重排 → 产出 requirements v1.7（新增 **FR-011** 排序一致性 + R-13 + 补记 Web Studio `normalizeFindItems` 白名单缺口）
- [x] v1.7 增量审查（自检子代理）：3 必修（FR-011 描述与 AC7 互斥、漏列 context 模式服务端重排、行号精度）+ 5 建议 → 产出 requirements v1.8
- [x] 用户回复 `确认需求` → **requirements.md v1.8 已落盘**到 `prds/OpenViking/spec/resource-confidence/requirements.md`（557 行）
- [x] Phase 2：读取并应用 `spec/prompts/02.design_analysis.prompt.md`、`spec/templates/design.md`；产出 design v1.0
- [x] Phase 2 输出前自检（自检子代理，仅 1 轮）：发现 7 必修 + 8 建议，其中 **F-A 为功能性缺陷**（`resource_service.py` 方法边界错位会导致 watch 刷新冲掉人工标注）
- [x] 产出 design v1.1（修正 7 必修 + 8 建议，1443 行，`/tmp/design-resource-confidence.md`）；机械校验 `[OK] C1~C6 通过`

### 当前阶段待完成的工作

- [ ] 向用户展示 design v1.1 正文，请求 `确认设计`
- [ ] 用户回复 `确认设计` 后落盘 `design.md` 并推进 Gate（TASKS=允许）

## 6. 中断恢复指引（核心）

> **此节是跨会话恢复的关键**。当 AI 在新窗口中读取本文件时，根据此节的指示决定如何衔接。

### 恢复策略

| 中断时机                     | 恢复策略 |
|--------------------------|----------|
| Phase 1-3 中，内容已展示但等待用户确认 | AI 应先告知用户上次已展示的内容，询问"是否需要重新展示，还是可以直接确认？" |
| Phase 1-3 中，刚开始尚未展示内容    | 直接从当前阶段的第一步重新开始 |
| Phase 4 任务执行中            | 读取下方"任务执行进度"表，从第一个 `🚧 进行中` 或 `⏳ 等待中` 的任务继续 |
| Phase 5（任务执行中）           | 质检代理为临时子代理、中断即失效：需重新创建并携带《质检任务简报》执行；子环节已有结果以 status.md 记录的扫描/质检报告为准 |
| 阶段间过渡（刚完成上一阶段）           | 直接从当前阶段的第二步开始 |

### 恢复检查清单

当 AI 在新会话中读取本文件后，应逐项确认：

- [ ] 确认当前阶段是否正确（检查 Gate 状态是否与实际文件产出一致）
- [ ] 确认 `prds/OpenViking/spec/resource-confidence/` 目录下的文件是否与"文档产出"表一致
- [ ] 如果 Phase 4 且存在 tasks.md，对比 tasks.md 中的任务状态与本文件中的任务进度是否一致
- [ ] 向用户简要说明上次的进展和当前的恢复方案，获得确认后再继续

### 本次会话特有提示

- **requirements 已正式落盘**到 `prds/OpenViking/spec/resource-confidence/requirements.md`（v1.8，557 行）；`/tmp/draft-requirements-resource-confidence.md` 是同一内容的会话内副本，**以 spec 目录下的文件为准**。
- **design 未落盘**，草稿在 `/tmp/design-resource-confidence.md`（v1.1，1443 行）。若新会话中丢失，需按 `spec/templates/design.md` 重新产出，不可凭记忆臆造。
- **skill 资产已不可通过符号链接访问**（`example-repo/skills/` 被删）。新会话若要继续本流程，需先恢复 `skills/` 或改用 `git show HEAD:skills/aegis-iv-skill/...` 取用。
- 四轮审查的结论要点：字段白名单共 **3 套**（`RETRIEVAL_OUTPUT_FIELDS` / `PORTABLE_VECTOR_SCALAR_FIELDS` + `_PORTABLE_SCALAR_FIELDS` / `VECTOR_MIGRATION_OUTPUT_FIELDS`）；`IngestOptions` 有 **2 处**"仅按 tags 早退"的闸门（`resource_service.py:288-296`、`embedding_utils.py:91`）；向量写入被强制 `partial_update=True`（`collection_schemas.py:793-796`），"缺键即保留旧值"；检索分数有 **3 层**（`_final_score`（hotness 前，门槛用）/ `raw_score`（hotness 后＝改造前对外分）/ `score`（有界折扣后，排序用），`score = raw_score × (1 - λ(1 - confidence))`，λ=0.2）；输出契约有 **4 处**序列化点（`_context_to_dict:376-383`、`_query_result_to_dict:394-410`、context 模式 `AssembleResult.to_dict:46-52`、`<memory>` 标签 `render.py:36-42`）；context 装配链需经 `Candidate`（`gather.py:33-46`）与 `_build`（`:242-255`）透传，否则新字段被丢弃。
- **设计期新增关键事实**：`resource_service.py` 有三个相邻方法必须区分 —— `add_resource`(`:1286-1340`，**唯一做缺省补齐**)、`refresh_resource`(`:1342-1383`，**显式不携带**)、`_submit_resource_ingestion`(`:1385-1410`，**只透传**)。若把 `normalize_confidence_for_write` 放进 `_submit_resource_ingestion`，watch 刷新会把人工标注冲成 1.0。
- 全部引用的代码行号基于 git HEAD `02fb0543`。

## 7. 任务执行进度（Phase 4 专属）

> 仅在进入 Phase 4 后填写。与 `tasks.md` 中的任务列表保持同步。

| 任务编号 | 任务名称 | 状态 | 开始时间 | 完成时间 | 备注 |
|----------|----------|------|----------|----------|------|
| TASK-001 | 新增置信度工具模块 | ✅ 已完成 | 16:21 | 16:22 | `openviking/utils/confidence.py`；三函数行为已逐项验证 |
| TASK-002 | 向量集合 schema 与存量集合告警 | ✅ 已完成 | 16:22 | 16:23 | `Fields` 加 `confidence float32 DefaultValue=1.0`；4 例单测通过 |
| TASK-003 | 检索输出字段白名单 | ✅ 已完成 | 16:23 | 16:24 | `RETRIEVAL_OUTPUT_FIELDS` / `FETCH_BY_URI_OUTPUT_FIELDS` |
| TASK-004 | 备份与迁移字段白名单 | ✅ 已完成 | 16:23 | 16:24 | 三套清单（ovpack 导出 / import recompute / migration） |
| TASK-005 | `IngestOptions` 载体扩展 | ✅ 已完成 | 16:24 | 16:25 | `Optional[float]`；`None` = 不携带 |
| TASK-006 | 落库写入点放开早退分支 | ✅ 已完成 | 16:24 | 16:25 | `_apply_ingest_options` 拆两个独立分支 |
| TASK-007 | 服务层透传与闸门放开 | ✅ 已完成 | 16:25 | 16:27 | 三方法边界已按设计 v1.1 固化；`refresh_resource` 确认无形参 |
| TASK-008 | 队列消息字段 | ✅ 已完成 | 16:27 | 16:28 | 往返/兼容/非数字降级 3 例通过 |
| TASK-009 | 请求模型与路由下传 | ✅ 已完成 | 16:27 | 16:28 | 不加 pydantic `ge/le`（保持 `InvalidArgumentError` 语义） |
| TASK-010 | 检索打分与三层分数 | ✅ 已完成 | 16:28 | 16:30 | 需求全部数值样例通过（X 0.81/Y 0.46；19% 换位、21% 不换位） |
| TASK-011 | 结果模型与两处序列化 | ✅ 已完成 | 16:30 | 16:31 | list + provenance 两分支 |
| TASK-012 | context 装配链与 `<memory>` 标签 | ✅ 已完成 | 16:31 | 16:33 | `Candidate` / `AssembledEntry` / `_make_entry` / `render_entry` |
| TASK-013 | 服务内部消费面 | ✅ 已完成 | 16:33 | 16:34 | 记忆工具 / MCP 文本 / skills 小结（均保序） |
| TASK-014 | Web Studio 白名单与展示 | ✅ 已完成 | 16:26 | 16:35 | 子代理执行；8 文件（含 4 个必要的越范围修正）；8 例前端单测通过 |
| TASK-015 | CLI 参数、校验、回显、注入、展示 | ✅ 已完成 | 16:20 | 17:16 | 子代理执行；12 例单测全绿、`cargo build` 0 warning、全量 `cargo test` 496 通过。父代理合并了子代理临时拆出的 `add_resource_with_confidence`（改回单一 `add_resource` + 在 `openviking_assets.rs:878` 与 2 处测试调用点补 `None`），消除了近重复方法 |
| TASK-016 | 文档口径同步 | ✅ 已完成 | 16:25 | 16:34 | 子代理执行 9 文件；父代理补 4 处旧口径（DG-3） |
| TASK-017 | 编译与静态检查 | ✅ 已完成（1 项受限） | 16:36 | 17:16 | Python `py_compile` + `ruff check`/`format` 全部通过（与基线比对零新增）；TS SDK `tsc` exit 0 + 53 例通过；Go SDK（修正失效 GOROOT）`build`/`vet` 通过；Rust `cargo build` 0 warning + 496 例通过。**受限项**：`cargo fmt --check` 无法执行（工具链未装 rustfmt，`rustup component add` 离线失败），已人工对齐既有风格 |
| TASK-018 | 生成测试数据 | ✅ 已完成 | 16:40 | 16:52 | `test-fixtures/`（生成脚本 + 基线捕获脚本 + 定点分数数据）；夹具已实际生成 |
| TASK-019 | 变更说明与下游影响点名 | ✅ 已完成 | 16:48 | 16:50 | `change-note.md`；6 处下游消费端逐条点名 + 回滚顺序 |
| TASK-020 | 单测：工具/Schema/白名单 | ✅ 已完成 | 16:36 | 16:44 | 4 个测试类 20 例通过 |
| TASK-021 | 单测：写入链路 | ✅ 已完成 | 16:36 | 16:44 | 5 个测试类 18 例通过 |
| TASK-022 | 单测：检索打分与序列化 | ✅ 已完成 | 16:36 | 16:45 | 3 个测试类 22 例通过 |
| TASK-023 | 单测：消费面 | ✅ 已完成 | 16:36 | 16:45 | 2 个测试类 6 例通过 |
| TASK-024 | 单测：CLI 与前端 | ✅ 已完成 | 16:26 | 17:16 | Rust 内联 12 例 + 前端 8 例 + Python/TS SDK 6 例，全部通过 |
| TASK-025~032 | 人工集成/性能/回归三测 | ⏳ 等待中 | — | — | 判据与夹具已就绪（TASK-018），由用户执行 |
| TASK-033 | 知识沉淀与流程收尾 | ⏳ 等待中 | — | — | 待质检/验收后执行 |

**当前进行中任务**: 无（开发与单测任务全部完成）
**已完成任务数**: 24 / 33（TASK-001~024）；TASK-025~032 人工三测与 TASK-033 收尾待后续阶段
**遇到问题**: ① vectordb 引擎原生扩展未构建，`tests/server/test_api_resources.py` / `test_mcp_endpoint.py` 的会话级 fixture 无法建立（197 例未执行）；② `cargo fmt --check` 因工具链缺 rustfmt 且离线无法安装而未执行。均见 §5 环境前提

## 8. 阻塞与风险

### 当前阻塞

- 无

### 已识别风险

- R-1：新字段缺省值若写成 `0.0`（而非 schema `DefaultValue: 1.0`），未携带置信度的记录分数会被清零（证据 `openviking/storage/vectordb/utils/data_processor.py:92-104`、`:120-141`）。
- R-2：存量集合不会自动获得新字段（`openviking/storage/collection_schemas.py:274-311` 只在集合不存在时创建；自动迁移已被提交 `4d00feac` 删除），写入会被 `viking_vector_index_backend.py:178-185` 静默过滤。子代理对该场景的表述存在分歧（"静默丢弃" vs "校验报错"），设计阶段需实证确认。
- R-3：乘法若放在阈值判定之前，低置信记录会跌破默认阈值 0.1 / MCP 0.35 而从结果中消失（证据 `hierarchical_retriever.py:200/467/535` 早于 `:605-626`）。
- R-4：`score` 已被 4 个对外面与至少 6 处下游二次阈值消费（MCP 0.35、vikingbot 0.35、openclaw 0.85 等），乘系数会改变下游判定。
- R-5：ovpack 备份与 namespace 迁移按字段白名单投影，不加白名单会丢字段（`ovpack/index.py:22-32`、`vector_migration.py:18-35`）。
- R-6：`score` 不保证落在 `[0,1]`（`_rerank_scores` 无 min-max 归一化，`hierarchical_retriever.py:371-419`），文档与 UI 若暗示"百分比相关度"会误导。
- R-7：`update_search_tags` 的"读回再整条覆盖"路径曾疑会擦除置信度；经核查 `get`（`viking_vector_index_backend.py:462-470`）无字段投影、返回整条记录，**不构成擦除风险**，但设计阶段需补回归用例固化。
- R-8：`ov write` / watch 增量 / reindex 的重写路径会**主动清空 `IngestOptions`**（`openviking/storage/queuefs/semantic_dag.py:522-533`，trigger 置位点 `openviking/storage/content_write.py:626`、`openviking/service/reindex_executor.py:1062`），置信度目前只靠未被文档化的 `partial_update=True`（`openviking/storage/collection_schemas.py:793-796`）侥幸保留。已升级为待确认事项 Q8，并要求补回归用例。
- R-9（第 3 轮新增）：**新增字段默认会被所有消费端静默忽略**。已逐条核实的 10 处：`openviking/session/memory/tools.py:44`（只保留 `{uri, score}`）、`openviking/retrieve/context_assembler/render.py:39`、`openviking/server/mcp_endpoint.py:409-410`、`examples/openclaw-plugin/memory-ranking.ts:44/49/243`、`bot/vikingbot/agent/tools/ov_file.py:375`、`bot/vikingbot/agent/memory.py:319`、`integrations/langchain/.../retrievers.py:248`、`store.py:262`、`crates/ov_cli/src/commands/search.rs:421-429`、`web-studio/.../retrieval-results.tsx:427-428`。由 FR-010 与 NFR-003（已入验收总则）覆盖自有面；三处示例/集成按 Q9 本期不改但须点名。
- R-10（第 4 轮新增）：λ = 0.2 是**全局单一常数**，不做按类别差异化（对比 `other_peer_penalty` 按类别给 0.02~0.1，`params.py:107-115`）。本期接受。
- R-11（第 4 轮新增）：λ = 0.2 是**经验值**，未经效果实测；λ=1 已被用户反例否定、λ=0 已否定"完全不起作用"。上线后以"低置信资源的平均位次变化"为观测指标。
- R-12（第 4 轮新增）：**置信度折扣与 `other_peer_penalty` 会叠加**（`gather.py:242-250`）。已决策为"有意叠加"（两者语义独立、penalty 有界），并在 FR-009 固化为可验收断言；本行仅作留痕。

## 9. 变更记录

| 时间 | 变更内容 | 变更前状态 | 变更后状态 |
|------|----------|------------|------------|
| 2026-10-10 09:20 | 创建 status.md，开始 Phase 1 | — | Phase 1 进行中 |
| 2026-10-10 09:45 | 第 1 轮需求审查（自检子代理）完成，通过 14/24，存在 5 项内容 ❌ + 2 项流程 ❌ | 需求 v1.0 草稿 | 收到审查结论，进入修订 |
| 2026-10-10 09:50 | 产出 requirements v1.1 修订稿（逐条回应第 1 轮全部 ❌ 项） | requirements v1.0 | requirements v1.1（未落盘） |
| 2026-10-10 10:00 | 第 2 轮需求审查（自检子代理）完成：通过 15 / 不通过 6 / 无法核验 3；端到端推演识别 5 个链路断点 | requirements v1.1 | 收到审查结论，审查循环按规则停止 |
| 2026-10-10 10:05 | 产出 requirements v1.2 修订稿：修正 5 项事实性错误，新增 R-8 与待裁决事项 Q7/Q8；修正 status.md 首轮通过数口径 | requirements v1.1 | requirements v1.2（未落盘） |
| 2026-10-10 10:40 | 答疑"只回传不乘分"：核实 10 处消费端全部只读 `score`，给出"会被静默忽略"的结论与四方案对比 | Q1/Q2 待裁决 | 用户裁决方向逐步明确 |
| 2026-10-10 11:05 | 用户裁决"相乘后排序"并要求能区分"语义相关但被降权"与"语义本身就弱"；产出 requirements v1.3（`raw_score` + 门槛/排序维度分工 + 可见面渲染 + R-9） | requirements v1.2 | requirements v1.3（未落盘） |
| 2026-10-10 11:15 | 第 3 轮需求审查（用户变更后重审）：通过 12 / 不通过 10 / 无法核验 2；指出 `raw_score` 与门槛比对对象分属 hotness 混合前后的**口径性错误** | requirements v1.3 | 收到审查结论，进入修订 |
| 2026-10-10 11:20 | 产出 requirements v1.4：三层命名表、provenance 分支、`session/memory/tools.py` 专属 AC、验收总则纳入 FR-010/NFR-003、Q1/Q2 补记用户原话、修正 `gather.py` 行号；status.md 同步（补登 R-7/R-9 与循环例外说明） | requirements v1.3 | requirements v1.4（未落盘） |
| 2026-10-10 11:40 | 用户提出"乘法无界"反例（raw 0.90/conf 0.5 被 raw 0.46/conf 1.0 反超）并提出"只提示不改分"方案；主代理核实项目既有降权先例为**有界减法**（`params.py:107-115/168-173`），给出 λ 连续谱（λ=0 ≡ 不改分，λ=1 ≡ 纯乘法） | v1.4 纯乘法 | 用户裁决 |
| 2026-10-10 11:50 | 用户回复"按推荐来"→ 裁决 λ=0.2 有界折扣；产出 requirements v1.5 | requirements v1.4 | requirements v1.5（未落盘） |
| 2026-10-10 12:00 | 第 4 轮需求审查：通过 11 / 不通过 10 / 无法核验 3；指出换位界 20%/25% 分母不一致、`Candidate` 断链、越界反向 boost、双重折扣未决 | requirements v1.5 | 收到审查结论，进入修订 |
| 2026-10-10 12:05 | 产出 requirements v1.6：统一相对差定义（分母 `raw_a`，界 20%）、补 context 装配链载体（`gather.py:33-46/242-255`）、新增越界读侧 clamp AC、双重折扣唯一口径 + R-12、context `entries[]` AC、紧边界成对用例、修正 `models.py` 行号、Q11 补记用户原话；**停止自动审查循环** | requirements v1.5 | requirements v1.6（未落盘） |
| 2026-10-10 12:25 | 用户确认 Q7（缺省覆盖 1.0）、新增"导入时回显置信度"、追问"管理台与客户端排序是否一致"；主代理核实同端点/无重排/console 无检索，产出 requirements v1.7（**新增 FR-011**、R-13、补记 Web Studio `normalizeFindItems` 白名单缺口） | requirements v1.6 | requirements v1.7（未落盘） |
| 2026-10-10 12:35 | v1.7 增量审查（自检子代理）：3 必修（FR-011 描述与 AC7 互斥、漏列 `mode="context"` 服务端重排、行号精度）+ 5 建议 | requirements v1.7 | 收到审查结论，进入修订 |
| 2026-10-10 12:40 | 产出 requirements v1.8：需求描述限定"同一 REST 端点"、AC7 补第 4 类既有差异、行号精度修正、AC1 扩到三条路径、AC4 措辞精确化、AC6 限定消费端、FR-001 `--json` 键名改"必须"并点明本地取值 | requirements v1.7 | requirements v1.8（未落盘） |
| 2026-10-10 14:21 | 用户回复 `确认需求` → requirements.md v1.8 落盘到 spec 目录（557 行 / 68,452 B）；Gate 推进为 REQ=已确认 / DESIGN=允许 | REQ=未确认 | REQ=已确认, Phase 1 完成, Phase 2 进行中 |
| 2026-10-10 14:22 | Phase 2：读取并应用 `02.design_analysis.prompt.md` 与 `templates/design.md`；产出 design v1.0（1258 行） | Phase 2 开始 | design v1.0（未落盘） |
| 2026-10-10 14:24 | **环境异常**：发现 `example-repo/skills/` 被删除（`git status` 显示 `skills/**` 全部为未提交 `D`），`~/.dsh/skills/aegis-iv-skill` 等符号链接悬空 | skill 资产可访问 | skill 资产不可经符号链接访问；改用 `git show HEAD:...` 提取 `doc_consistency.py` |
| 2026-10-10 14:30 | Phase 2 输出前自检（自检子代理，1 轮）：发现 7 必修 + 8 建议，含 **F-A 功能性缺陷**（`resource_service.py` 方法边界错位将导致 watch 刷新冲掉人工标注） | design v1.0 | 收到自检结论，进入修订 |
| 2026-10-10 14:40 | 产出 design v1.1：修正方法边界（`add_resource` 唯一规范化 / `refresh_resource` 不携带 / `_submit_resource_ingestion` 只透传）、新增 C16 文档同步与 C17 入口处置、`--json` 不改通用函数、回显改 stdout、补三套白名单与 5 处新增函数单测、新增 TC-39/40/41、附录补载体清单对照表；机械校验 `[OK] C1~C6 通过` | design v1.0 | design v1.1（1443 行，未落盘） |
| 2026-10-10 14:45 | status.md 同步：Gate 表、阶段进度、文档产出、当前子步骤、环境异常说明、恢复提示、变更记录 | status.md 停留在 Phase 1 | status.md 与 Phase 2 一致 |
| 2026-10-10 15:53 | 用户回复 `确认设计` → **design.md v1.1 落盘**到 spec 目录（1444 行 / 91,580 B）；机械校验 `[OK] C1~C6 通过`；Gate 推进为 DESIGN=已确认 / TASKS=允许 | DESIGN=允许, Phase 2 进行中 | DESIGN=已确认, Phase 2 完成, Phase 3 进行中 |
| 2026-10-10 15:14 | 环境变化：`~/.dsh/skills/aegis-iv-skill` 符号链接被重新指向 `<skills-root>/aegis-iv-skill`（版本一致），skill 清单/提示词/模板恢复可读；`example-repo/skills/` 仍为未提交删除 | skill 资产不可用 | skill 资产恢复可读（指向另一副本） |
| 2026-10-10 16:00 | Phase 3：读取 `03.task_breakdown.prompt.md` 与 `templates/tasks.md`；产出 tasks v1.0（33 任务 / 1349 行） | Phase 3 开始 | tasks v1.0（未落盘） |
| 2026-10-10 16:05 | Phase 3 输出前自检（自检子代理，1 轮）：9 必修 + 3 建议 —— 含分类合计 32≠33、3 处依赖缺口会让单测先于被测代码启动、TC-31 零回归基线快照缺失、C17 无落点 → 全部修订为 tasks v1.1；同轮同步 status.md | tasks v1.0 | tasks v1.1（未落盘）+ status.md 与 Phase 3 一致 |
| 2026-10-10 16:20 | 用户回复 `确认任务计划` → **tasks.md v1.1 落盘**（1375 行）；Gate 推进为 TASKS=已确认 / EXEC=允许；Phase 4 开始，按依赖顺序执行 TASK-001~024 | TASKS=允许, Phase 3 进行中 | TASKS=已确认, Phase 3 完成, Phase 4 进行中 |
| 2026-10-10 16:20 | 并行委派 3 个互不冲突的子代理：TASK-015（Rust CLI 5 文件）、TASK-014（Web Studio 3 文件）、TASK-016（文档 9 文件）；主代理执行 Python 核心链路 | — | 三条工作流并行 |
| 2026-10-10 16:22–16:34 | TASK-001~013 完成：新增 `openviking/utils/confidence.py` 与 18 个既有模块的改造；逐项运行时验证（含需求给出的全部数值样例） | — | Python 核心链路打通 |
| 2026-10-10 16:34 | **发现 DG-1**：3 个 SDK（Python/Go/TypeScript）的 add-resource 选项载体均缺 `confidence`，其中 Python SDK 未声明时会直接抛 `TypeError` → 三处补齐并加回归测试 | design 载体清单遗漏 | DG-1 已修复 |
| 2026-10-10 16:34 | **发现 DG-2/DG-3**：Web Studio 服务端响应类型 `SearchHit`、以及 `docs/{zh,en}/concepts/07-retrieval.md`、`docs/{zh,en}/guides/09-ovpack.md` 共 4 处旧口径 → 全部补齐 | design 取值范围遗漏 | DG-2/DG-3 已修复 |
| 2026-10-10 16:36–16:45 | TASK-020~023：12 个测试类、约 66 例新增单测通过；`ruff check` / `ruff format` 对全部改动文件与 HEAD 基线比对**零新增问题** | — | 单测完成 |
| 2026-10-10 16:36–16:52 | TASK-017 部分：Python `py_compile` 全通过；TS SDK `tsc` exit 0 + 53 例通过；Go SDK（修正失效 GOROOT 后）`build`/`vet` 通过；定位 `~/.openviking` 沙箱写权限问题并用 `OPENVIKING_CONFIG_FILE` 规避；用 `maturin build` + `pip install --target` 在工作区内补齐 `ragfs_python` | — | 三端静态检查通过 |
| 2026-10-10 16:40–16:52 | TASK-018：`test-fixtures/` 产出（生成脚本、基线捕获脚本、定点分数数据、说明文档），夹具已实际生成 | — | 夹具就绪 |
| 2026-10-10 16:48–16:50 | TASK-019：`change-note.md` 产出（6 处下游消费端逐条点名、回滚顺序、SDK 支持说明） | — | 变更说明就绪 |
| 2026-10-10 17:00 | 与 HEAD worktree 基线逐条比对：`tests/retrieve` + `tests/utils` 当前 147 通过 vs 基线 86 通过（同样的 2 例既有失败）；`test_collection_schemas.py` 当前 69 通过 vs 基线 65 通过（同样的 1 例既有失败）→ **零回归** | — | 回归比对完成 |
| 2026-10-10 17:00 | **环境前提缺失**：vectordb 引擎原生扩展（`_x86_sse3` 等，需 `setup.py` + `src/` C++ 构建）未构建，`tests/server/test_api_resources.py` 与 `test_mcp_endpoint.py` 的会话级 fixture 报 `Missing symbol: PersistStore`，197 例未能执行 | — | 已如实记录，未伪造结果 |
| 2026-10-10 17:16 | TASK-015 完成（12 例 CLI 内联单测全绿、`cargo build` 0 warning、全量 `cargo test` 496 通过）。父代理**合并**子代理临时拆出的 `add_resource_with_confidence`：改回单一 `add_resource`，并在 `openviking_assets.rs:878` 与 2 处测试调用点补 `None`（新增 1 个改动文件，消除近重复方法） | 子代理为守文件范围而拆方法 | 方法合并，回归重跑全绿 |
| 2026-10-10 17:20 | **发现并修复 3 例真实回归**：`test_semantic_msg_ingest_options.py`（`IngestOptions.to_dict` 多一键）、`test_memory_tools.py`（记忆工具返回四键）、`test_resource_service_watch.py`（`add_resource` 未传时 `confidence` 由 `None` 变 `1.0`，正是 FR-005 AC5 的既定行为）→ 按新契约更新断言（非禁用测试） | 全量回归比对 | 修复后失败集合与基线**完全一致** |
| 2026-10-10 17:22 | 最终回归比对：`tests/{retrieve,utils,storage,service,session/memory}` 当前 **1216 通过 / 26 失败** vs HEAD 基线 **1130 通过 / 26 失败** → **失败集合逐条一致，零回归**；`ruff check` 全通过；6 处既有格式偏差经 `ruff format --diff` 与 HEAD 逐字节比对确认**未被我改动加剧** | — | Phase 4 开发与单测部分完成 |

---

**最后更新**: 2026-10-10 17:25
**更新人**: AI 助手
