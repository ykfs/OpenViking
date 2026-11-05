# OpenViking 资源置信度（resource confidence）实现任务

## 文档信息

- **项目名称**: OpenViking（代码库根目录 `prds/OpenViking`，git HEAD `02fb0543`）
- **创建日期**: 2026-10-10
- **版本**: v1.1
- **状态**: 已确认
- **相关文档**: `spec/resource-confidence/requirements.md` v1.8、`spec/resource-confidence/design.md` v1.1

> 本文件为**任务基线**，已由客户于 2026-10-10 以口令「确认任务计划」确认。后续变更须走任务变更流程并升版本。

## 项目概览

- **总计任务数**: 33 个
- **预计总工期**: 约 21 个工作日（其中开发 14 个、单元测试 4 个、人工三测由用户侧执行，不占开发工时）
- **主要里程碑**: 4 个
- **项目开始日期**: 2026-10-10
- **预计完成日期**: 2026-11-10

## 任务分类统计

- **基础任务**: 4 个（TASK-001~004，工具模块与存储层）
- **API 开发**: 8 个（TASK-005~012，写入链路与检索链路）
- **前端开发**: 2 个（TASK-014、TASK-015，Web Studio 与 CLI）
- **集成任务**: 4 个（TASK-013、TASK-016、TASK-017、TASK-019，服务内部消费面、文档、编译、变更说明）
- **测试任务**: 14 个（TASK-018、TASK-020~032，测试数据、单元测试、人工三测）
- **部署/收尾任务**: 1 个（TASK-033）

## 里程碑规划

### 里程碑1: 存储与写入链路打通（第1周）

**目标**: `confidence` 能从 CLI 一路写到向量集合，并可被检索读取
**相关任务**: TASK-001, TASK-002, TASK-003, TASK-004, TASK-005, TASK-006, TASK-007, TASK-008, TASK-009
**验收标准**:

- [ ] `openviking/utils/confidence.py` 三个函数实现完成且单测通过
- [ ] 向量集合 `Fields` 含 `confidence`（`float32`、`DefaultValue = 1.0`），存量集合告警生效
- [ ] 三套备份/迁移白名单与两处检索输出白名单均已包含该字段
- [ ] 携带 `confidence` 的 `add-resource` 请求能落库，且 L0/L1/L2 三条记录同值

### 里程碑2: 检索三层分数与对外契约（第2周）

**目标**: 检索返回 `score` / `raw_score` / `confidence`，门槛仍用未加权分
**相关任务**: TASK-010, TASK-011, TASK-012, TASK-013
**验收标准**:

- [ ] 有界折扣 `score = raw_score × (1 - 0.2(1-confidence))` 生效，tie-break 确定
- [ ] 门槛仍比对 `_final_score`，低置信记录不因折扣消失
- [ ] `find` / `search`（list 与 context）/ `skills/find` / MCP 文本 / `<memory>` 标签 / 记忆 agent 工具均输出两字段
- [ ] 同一 REST 端点、同一参数下 CLI 与 Web Studio 排序逐项一致

### 里程碑3: CLI 与文档、编译通过（第3周）

**目标**: CLI 可传入并回显置信度，管理台可见，文档同步，全栈编译通过
**相关任务**: TASK-014, TASK-015, TASK-016, TASK-017, TASK-019
**验收标准**:

- [ ] `ov add-resource --confidence 0.6` 回显 `confidence 0.600`，`--json` 含该键
- [ ] Web Studio 检索页与详情面板展示三个数值，且未重排
- [ ] 7 个文档文件同步完成，旧口径零残留
- [ ] `cargo check` / Python 导入 / 前端 `tsc && build` 全部通过

### 里程碑4: 测试数据、单元测试与人工三测（第4周）

**目标**: 单元测试全绿、测试数据就绪、人工三测执行完毕
**相关任务**: TASK-018, TASK-020~032
**验收标准**:

- [ ] 测试数据已落库（高/中/低置信、脏数据、跨 peer 数据）
- [ ] 单元测试覆盖 design 的 20 个测试类（Python 15 + Rust 内联 4 + 前端 1），覆盖率 ≥ 80%
- [ ] 人工集成 / 性能 / 回归三测全部通过，零回归
- [ ] 变更说明完成并交付

## 测试策略→任务映射表

> 来源：`design.md` v1.1 的 `## 测试策略`（影响范围 **17 项**、测试用例 **TC-01~TC-41 含 TC-18b 共 42 条编号**、单元测试 **20 个测试类**）。
> **本表无"❌ 缺失"条目**；每个条目均映射到下方"详细任务列表"中的统一 TASK-XXX 编号。

### 一、影响范围（design「### 影响范围」17 项）

| design 影响范围条目 | 类型 | 对应 TASK 编号 | 状态 |
|---|---|---|---|
| 1. `ov add-resource` 全部分支 | 人工回归 | TASK-025, TASK-031 | ✓ |
| 2. `--manifest` 互斥 | 人工集成 | TASK-025 | ✓ |
| 3. 资源导入落库（L0/L1/L2） | 人工集成 | TASK-025, TASK-029 | ✓ |
| 4. `ov find` / `ov search` | 人工集成 | TASK-026, TASK-027 | ✓ |
| 5. `POST /api/v1/search/find`（含 provenance） | 人工集成 | TASK-027 | ✓ |
| 6. `POST /api/v1/search/search`（list 与 context） | 人工集成 | TASK-027 | ✓ |
| 7. MCP `find` / `search` | 人工集成 | TASK-027 | ✓ |
| 8. `POST /api/v1/skills/find` | 人工集成 | TASK-027 | ✓ |
| 9. Web Studio 检索页与详情面板 | 人工集成 | TASK-027 | ✓ |
| 10. 注入 LLM 的 `<memory>` 上下文 | 人工集成 | TASK-027 | ✓ |
| 11. 自带记忆 agent 的 search 工具 | 人工集成 | TASK-027 | ✓ |
| 12. `set-tags` / `ov write` / watch / reindex | 人工集成 | TASK-028 | ✓ |
| 13. ovpack 导出/导入 | 人工集成 | TASK-029 | ✓ |
| 14. namespace 迁移 | 人工集成 | TASK-029 | ✓ |
| 15. 存量集合升级启动 | 人工集成 | TASK-029 | ✓ |
| 16. 下游 vikingbot / openclaw / langchain | 人工回归 | TASK-032 | ✓ |
| 17. 未标注资源的分数与排序 | 人工回归 | TASK-031 | ✓ |

### 二、测试用例（design「### 测试用例」42 条）

| design 测试项 | 类型 | 对应 TASK 编号 | 状态 |
|---|---|---|---|
| TC-01 | 人工集成 | TASK-025 | ✓ |
| TC-02 | 人工集成 | TASK-025 | ✓ |
| TC-03 | 人工集成 | TASK-025 | ✓ |
| TC-04 | 人工集成 | TASK-025 | ✓ |
| TC-05 | 人工集成 | TASK-025 | ✓ |
| TC-06 | 人工集成 | TASK-025 | ✓ |
| TC-07 | 人工集成 | TASK-025 | ✓ |
| TC-08 | 人工集成 | TASK-025 | ✓ |
| TC-09 | 人工集成 | TASK-026 | ✓ |
| TC-10 | 人工集成 | TASK-026 | ✓ |
| TC-11 | 人工集成 | TASK-026 | ✓ |
| TC-12 | 人工集成 | TASK-026 | ✓ |
| TC-13 | 人工集成 | TASK-026 | ✓ |
| TC-14 | 人工集成 | TASK-027 | ✓ |
| TC-15 | 人工集成 | TASK-027 | ✓ |
| TC-16 | 人工集成 | TASK-027 | ✓ |
| TC-17 | 人工集成 | TASK-027 | ✓ |
| TC-18 | 人工集成 | TASK-027 | ✓ |
| TC-18b | 人工集成 | TASK-027 | ✓ |
| TC-19 | 人工集成 | TASK-027 | ✓ |
| TC-20 | 人工集成 | TASK-028 | ✓ |
| TC-21 | 人工集成 | TASK-028 | ✓ |
| TC-22 | 人工集成 | TASK-028 | ✓ |
| TC-23 | 人工集成 | TASK-028 | ✓ |
| TC-24 | 人工集成 | TASK-028 | ✓ |
| TC-25 | 人工集成 | TASK-029 | ✓ |
| TC-26 | 人工集成 | TASK-029 | ✓ |
| TC-27 | 人工集成 | TASK-029 | ✓ |
| TC-28 | 人工集成 | TASK-029 | ✓ |
| TC-29 | 人工性能 | TASK-030 | ✓ |
| TC-30 | 人工性能 | TASK-030 | ✓ |
| TC-31 | 人工回归 | TASK-031 | ✓ |
| TC-32 | 人工回归 | TASK-031 | ✓ |
| TC-33 | 人工回归 | TASK-031 | ✓ |
| TC-34 | 人工回归 | TASK-031 | ✓ |
| TC-35 | 人工回归 | TASK-031 | ✓ |
| TC-36 | 人工回归 | TASK-032 | ✓ |
| TC-37 | 人工回归 | TASK-032 | ✓ |
| TC-38 | 人工回归 | TASK-032 | ✓ |
| TC-39 | 人工集成 | TASK-032 | ✓ |
| TC-40 | 人工回归 | TASK-032 | ✓ |
| TC-41 | 人工集成 | TASK-029 | ✓ |

### 三、单元测试（design「### 单元测试」20 个测试类 = Python 15 + Rust 内联 4 + 前端 1）

| design 测试项 | 类型 | 对应 TASK 编号 | 状态 |
|---|---|---|---|
| `tests/unit/utils/test_confidence.py`（8 例） | 单元测试 | TASK-020 | ✓ |
| `tests/storage/test_collection_schemas.py`（扩展 4 例） | 单元测试 | TASK-020 | ✓ |
| `tests/storage/test_viking_vector_index_backend_output_fields.py`（3 例） | 单元测试 | TASK-020 | ✓ |
| `tests/storage/test_portable_fields_confidence.py`（5 例） | 单元测试 | TASK-020 | ✓ |
| `tests/utils/test_ingest_options.py`（扩展 5 例） | 单元测试 | TASK-021 | ✓ |
| `tests/service/test_resource_service_confidence.py`（6 例） | 单元测试 | TASK-021 | ✓ |
| `tests/storage/test_add_resource_msg_confidence.py`（3 例） | 单元测试 | TASK-021 | ✓ |
| `tests/server/test_api_resources.py`（扩展 2 例） | 单元测试 | TASK-021 | ✓ |
| `tests/client/test_http_client_compact.py`（扩展 2 例） | 单元测试 | TASK-021 | ✓ |
| `tests/retrieve/test_hierarchical_retriever_confidence.py`（10 例） | 单元测试 | TASK-022 | ✓ |
| `tests/retrieve/test_types_confidence_serialization.py`（4 例） | 单元测试 | TASK-022 | ✓ |
| `tests/retrieve/test_context_assembler_confidence.py`（8 例） | 单元测试 | TASK-022 | ✓ |
| `tests/session/memory/test_memory_search_tool_confidence.py`（3 例） | 单元测试 | TASK-023 | ✓ |
| `tests/server/test_mcp_endpoint.py`（扩展 2 例） | 单元测试 | TASK-023 | ✓ |
| `tests/server/test_api_skills_find_confidence.py`（3 例） | 单元测试 | TASK-023 | ✓ |
| `crates/ov_cli/src/client.rs` 内联（2 例） | 单元测试 | TASK-024 | ✓ |
| `crates/ov_cli/src/commands/resources.rs` 内联（3 例） | 单元测试 | TASK-024 | ✓ |
| `crates/ov_cli/src/handlers.rs` 内联（3 例） | 单元测试 | TASK-024 | ✓ |
| `crates/ov_cli/src/main.rs` 内联（4 例） | 单元测试 | TASK-024 | ✓ |
| `web-studio/src/lib/retrieval.test.ts`（扩展 4 例） | 单元测试 | TASK-024 | ✓ |

---

## 详细任务列表

### 基础任务类别

#### TASK-001: 新增置信度工具模块

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: 无
- **预计时间**: 4小时
- **实际耗时**: [完成后填写]
- **负责人**: [指定人员]
- **开始日期**: [日期]
- **完成日期**: [日期]

**任务描述**：
按 design C1 新增 `openviking/utils/confidence.py`，承载置信度的写侧校验、读侧兜底与有界折扣因子计算。

**实现要点**：

- 常量：`CONFIDENCE_FIELD` / `DEFAULT_CONFIDENCE=1.0` / `MIN_CONFIDENCE=0.0` / `MAX_CONFIDENCE=1.0`
- `normalize_confidence_for_write`：`None → 1.0`；非数/非有限/越界 → `openviking_cli.exceptions.InvalidArgumentError`
- `coerce_confidence_for_read`：缺失/非数/非有限 → `1.0`；越界 → clamp 到 `[0,1]`
- `confidence_factor(confidence, penalty_lambda) = 1 - λ(1 - confidence)`
- 不新增第三方依赖

**验收标准**：

- [ ] 四个常量与三个函数按 design C1 实现，签名与语义一致
- [ ] `confidence_factor(1.0, λ)` 对任意 λ 严格返回 `1.0`
- [ ] 模块内不 import 任何存储/检索层模块（保持纯函数、可独立单测）
- [ ] 通过 TASK-020 的单测

**测试要求**：

- 见 TASK-020 的 `tests/unit/utils/test_confidence.py`

**相关文件**：

- `prds/OpenViking/openviking/utils/confidence.py`（新增）

**注意事项**：

- 读侧必须复用同一常量，不得各写各的字面量
- `InvalidArgumentError` 从 `openviking_cli.exceptions` 导入（与 `resource_service.py` 既有用法一致）

---

#### TASK-002: 向量集合 schema 变更与存量集合告警

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-001
- **预计时间**: 6小时
- **负责人**: [指定人员]

**任务描述**：
按 design C2 在集合 schema 中新增 `confidence` 字段（强制 `DefaultValue: 1.0`），并在 `init_context_collection` 中新增存量集合缺字段告警。

**实现要点**：

- `CollectionSchemas.context_collection` 的 `fields` 列表（`:84-133`）新增 `{"FieldName": "confidence", "FieldType": "float32", "DefaultValue": 1.0}`
- `ScalarIndex`（`:134-153`）**不加**该项
- `init_context_collection` 在 `existing_meta` 非空校验之后（`:321` 后）新增缺字段 WARNING；保留 `:313-320` 的 `hasattr` 守卫与 `raise`
- 新增导入 `from openviking.utils.confidence import CONFIDENCE_FIELD`

**验收标准**：

- [ ] schema `Fields` 含 `confidence`，`FieldType == "float32"`，`DefaultValue == 1.0`（**不是 0.0**）
- [ ] `ScalarIndex` 不含 `confidence`
- [ ] 旧集合（`Fields` 缺该字段）启动时产生含集合名与字段名的 WARNING
- [ ] 新集合（`Fields` 含该字段）启动时无该 WARNING
- [ ] 通过 TASK-020 的单测

**相关文件**：

- `prds/OpenViking/openviking/storage/collection_schemas.py`

**注意事项**：

- `DefaultValue` 遗漏会让未标注记录物化为 `0.0`（R-1），是全量分数归零的根因，必须单测断言

---

#### TASK-003: 检索输出字段白名单

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-002
- **预计时间**: 3小时
- **负责人**: [指定人员]

**任务描述**：
按 design C3 把 `confidence` 加入检索候选与按 URI 回读两处字段投影白名单。

**实现要点**：

- `RETRIEVAL_OUTPUT_FIELDS`（`:34-42`）追加 `"confidence"`
- `FETCH_BY_URI_OUTPUT_FIELDS`（`:50-66`）追加 `"confidence"`（原有 15 项保留）
- `LOOKUP_OUTPUT_FIELDS`（`:44-48`）**不改**

**验收标准**：

- [ ] `"confidence" in RETRIEVAL_OUTPUT_FIELDS`
- [ ] `"confidence" in FETCH_BY_URI_OUTPUT_FIELDS`
- [ ] `"confidence" not in LOOKUP_OUTPUT_FIELDS`
- [ ] 向量检索返回的候选 dict 中确实能取到该键（集成验证见 TC-01）
- [ ] 通过 TASK-020 的单测

**相关文件**：

- `prds/OpenViking/openviking/storage/viking_vector_index_backend.py`

---

#### TASK-004: 备份与迁移字段白名单

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-002
- **预计时间**: 4小时
- **负责人**: [指定人员]

**任务描述**：
按 design C4 把 `confidence` 加入 ovpack 导出投影、ovpack import recompute 写入白名单、namespace 迁移读侧投影三套清单。

**实现要点**：

- `storage/ovpack/index.py` 的 `PORTABLE_VECTOR_SCALAR_FIELDS`（`:22-31`）追加
- `utils/embedding_utils.py` 的 `_PORTABLE_SCALAR_FIELDS`（`:65-74`）追加
- `storage/vector_migration.py` 的 `VECTOR_MIGRATION_OUTPUT_FIELDS`（`:18-35`）追加
- `EXPORT_VECTOR_FIELDS` 由 `PORTABLE_VECTOR_SCALAR_FIELDS` 派生，无需单独改

**验收标准**：

- [ ] 三套清单均含 `"confidence"`
- [ ] `portable_scalars(record)` 能带出该字段
- [ ] 通过 TASK-020 的 `test_portable_fields_confidence.py` 5 例

**相关文件**：

- `prds/OpenViking/openviking/storage/ovpack/index.py`
- `prds/OpenViking/openviking/utils/embedding_utils.py`
- `prds/OpenViking/openviking/storage/vector_migration.py`

**注意事项**：

- 前两者是**独立的两套**（导出 vs import 重新向量化写入），只改一处仍会在 import 时丢字段

---

### API 开发类别

#### TASK-005: `IngestOptions` 载体扩展

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-001
- **预计时间**: 3小时
- **负责人**: [指定人员]

**任务描述**：
按 design C5 为 `IngestOptions` 增加 `confidence: Optional[float] = None`，并同步 `from_value` / `to_dict`。

**实现要点**：

- `IngestOptions` 新增字段，语义为"`None` = 本次不携带（重写路径保留旧值）"
- `from_value`（`:40-53`）读取 `value.get("confidence")`
- `to_dict`（`:55-58`）输出该键
- `from_search_tags`（`:26-38`）保持不变

**验收标准**：

- [ ] `IngestOptions(confidence=0.4).to_dict()` → `from_value` 往返保真
- [ ] 仅设 `search_tags` 时 `confidence is None`
- [ ] 通过 TASK-021 的 `tests/utils/test_ingest_options.py`

**相关文件**：

- `prds/OpenViking/openviking/utils/ingest_options.py`

**注意事项**：

- 不得把默认值写成 `1.0` —— 那会让重写/重索引路径把人工标注冲成 1.0（违反 Q8）

---

#### TASK-006: 落库写入点放开早退分支

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-005
- **预计时间**: 4小时
- **负责人**: [指定人员]

**任务描述**：
按 design C6 改造 `_apply_ingest_options`，使"只带 confidence、不带 tags"的导入也能写入 `context_data`。

**实现要点**：

- 原 `:91` 的 `if not embedding_msg or ingest_options.search_tags is None: return` 拆为"仅守 `embedding_msg`" + 两个独立 `if`
- 新增 `if ingest_options.confidence is not None:` 分支，写入前经 `coerce_confidence_for_read`
- 新增导入 `from openviking.utils.confidence import CONFIDENCE_FIELD, coerce_confidence_for_read`
- 三个调用点 `:423` / `:470` / `:631` 不变

**验收标准**：

- [ ] `IngestOptions(confidence=0.6)`（无 tags）→ `context_data["confidence"] == 0.6` 且不含 `search_tags` 键
- [ ] `IngestOptions()`（confidence=None）→ `context_data` **不含** `confidence` 键
- [ ] 两者都设时两个键都写入
- [ ] 通过 TASK-021 的 `_apply_ingest_options` 相关用例

**相关文件**：

- `prds/OpenViking/openviking/utils/embedding_utils.py`

---

#### TASK-007: 服务层置信度透传与闸门放开

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-005
- **预计时间**: 8小时
- **负责人**: [指定人员]

**任务描述**：
按 design C7 完成 `resource_service.py` 的 8 项变更，**关键是三个相邻方法的职责边界**。

**实现要点**：

- `add_resource`（`:1286-1340`）：新增 `confidence: Optional[float] = None` 形参；方法体内 `normalized_confidence = normalize_confidence_for_write(confidence)`（**唯一做缺省补齐处**）；转调时传 `confidence=normalized_confidence`
- `refresh_resource`（`:1342-1383`）：**不加形参、不传值**，加注释固化"重写路径保留人工标注"
- `_submit_resource_ingestion`（`:1385-1410`）：新增形参，**只透传、不做缺省补齐**
- `_add_resource_ingest_tag_kwargs` → 改名 `_add_resource_ingest_options`（`:288-296`），放开"`tags is None` 即返回 `{}`"的闸门；更新三处调用点 `:774-777` / `:1774-1777` / `:1814`
- `_ADD_RESOURCE_ARGS_RESERVED_FIELDS`（`:120-139`）追加 `"confidence"`
- 两处建消息 `:1073-1124` / `:1854-1892` 与两处消费 `:728-729` / `:774-777` 补 `confidence`
- Connector 分支 `:1610-1622` 补 `confidence`
- 新增导入 `from openviking.utils.confidence import normalize_confidence_for_write`

**验收标准**：

- [ ] `add_resource(confidence=0.6)` → 入队消息 `confidence == 0.6`
- [ ] `add_resource()`（未传）→ 消息 `confidence == 1.0`
- [ ] `add_resource(confidence=1.2)` → 抛 `InvalidArgumentError` 且**未入队**
- [ ] `tags=None, confidence=0.4` → `_add_resource_ingest_options` 返回非空且含该值（第一道闸门已放开）
- [ ] `tags=None, confidence=None` → 返回 `{}`（既有缺省路径不变）
- [ ] `args={"confidence": 0.5}` → 抛 `InvalidArgumentError`
- [ ] `refresh_resource` 调用链上 `confidence` 保持 `None`
- [ ] 通过 TASK-021 的 `test_resource_service_confidence.py` 6 例

**相关文件**：

- `prds/OpenViking/openviking/service/resource_service.py`

**注意事项**：

- ⚠️ **不得把 `normalize_confidence_for_write` 放进 `_submit_resource_ingestion`** —— watch 定时刷新会 `None → 1.0`，冲掉人工标注（这是 design v1.1 修正的功能缺陷 F-A）
- `refresh_resource` 需补一条注释说明该决定，避免后续被"顺手补齐"

---

#### TASK-008: 队列消息字段

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-005
- **预计时间**: 3小时
- **负责人**: [指定人员]

**任务描述**：
按 design C8 为 `AddResourceMsg` 增加 `confidence` 字段并同步反序列化。

**实现要点**：

- dataclass 追加 `confidence: Optional[float] = None`（放在 `tag_mode` 之后）
- `from_dict`（`:100-207`）在 `tag_mode` 之后追加，带 `isinstance(..., (int, float))` 保护
- `to_dict` 走 `asdict`，无需改动

**验收标准**：

- [ ] `to_dict` → `from_dict` 往返保真
- [ ] 旧 payload（无该键）→ `confidence is None`，不抛异常
- [ ] payload 中 `confidence="abc"` → `confidence is None`
- [ ] 通过 TASK-021 的 `test_add_resource_msg_confidence.py` 3 例

**相关文件**：

- `prds/OpenViking/openviking/storage/queuefs/add_resource_msg.py`

---

#### TASK-009: 请求模型与路由下传

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-007
- **预计时间**: 4小时
- **负责人**: [指定人员]

**任务描述**：
按 design C9 为 `AddResourceRequest` 增加 `confidence` 字段并下传到 service。

**实现要点**：

- `AddResourceRequest`（`:31-130`）在 `tag_mode`（`:111`）之后加 `confidence: Optional[float] = None`
- 类 docstring 的 Attributes 段补说明（区间 `[0.0, 1.0]`、缺省 1.0、0.0 语义）
- 路由下传处（`:300-301` 附近）加 `confidence=request.confidence`
- **不得**用 pydantic 的 `ge/le` 约束

**验收标准**：

- [ ] body 含 `confidence=0.6` → service 收到 `0.6`
- [ ] body 无该键 → service 收到 `None`（由 service 补 1.0）
- [ ] 越界值走 `InvalidArgumentError` 而非 422
- [ ] **入口范围不变量（对应 design C17）**：MCP `add_resource`（`mcp_endpoint.py:933-950`）与 `ingest_temp_upload`（`resource_ingest.py:22-76`）**本期不新增 `confidence` 参数**；二者经 `service.resources.add_resource` 复用同一实现，导入记录的 `confidence == 1.0`、`factor == 1.0`，排序与改造前一致。验证方式：通过 MCP `add_resource` 导入一条资源，断言其检索结果 `confidence == 1.0`。**此项是"有意不实现"，不得被后续评审判为漏改。**
- [ ] 通过 TASK-021 的 `tests/server/test_api_resources.py` 2 例

**相关文件**：

- `prds/OpenViking/openviking/server/routers/resources.py`

**注意事项**：

- design C17 的不变量已写入本任务验收标准；MCP 与 temp_upload 两条入口**不做改动**是已决策项（requirements FR-001「本期的入口范围」）

---

#### TASK-010: 检索打分与三层分数

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-001, TASK-003
- **预计时间**: 10小时
- **负责人**: [指定人员]

**任务描述**：
按 design C10 在 `_convert_to_matched_contexts` 中引入 `raw_score` 与有界折扣，并确定化 tie-break。

**实现要点**：

- 文件顶部新增模块级常量 `CONFIDENCE_PENALTY_LAMBDA = 0.2`
- `raw_score` = 原 `final_score`（hotness 混合后）；非有限 → `0.0`
- `confidence = coerce_confidence_for_read(c.get(CONFIDENCE_FIELD))`
- `score = raw_score * confidence_factor(confidence, CONFIDENCE_PENALTY_LAMBDA)`；非有限 → `0.0`
- `MatchedContext(..., score=score, raw_score=raw_score, confidence=confidence)`
- 排序键改为 `(x.score, x.raw_score)` 降序
- 新增导入 `from openviking.utils.confidence import CONFIDENCE_FIELD, coerce_confidence_for_read, confidence_factor`
- **不动** `_passes_threshold`（`:365-369`）与三处调用点（`:200` / `:467` / `:535`）

**验收标准**：

- [ ] `confidence=1.0` 时 `score == raw_score` 且与改造前逐位一致
- [ ] 不变式 `score == raw_score × (1 - 0.2(1 - confidence))` 容差 `1e-9` 内成立
- [ ] 有界性：任意返回项 `raw_score × 0.8 ≤ score ≤ raw_score`
- [ ] 用户样例 1：X(`0.90, 0.5`) 排在 Y(`0.46, 1.0`) 之前
- [ ] 用户样例 2：Q(`0.46, 1.0`) 排在 P(`0.50, 0.5`) 之前
- [ ] 紧边界：A(`0.50, 0.0`) vs B(`0.405, 1.0`) → B 在前；A vs B(`0.395, 1.0`) → A 在前
- [ ] 门槛分工：A(`0.42, 0.5`) 保留、B(`0.21, 1.0`) 在门槛 0.35 下丢弃
- [ ] 脏数据 `confidence=1.5` → `confidence == 1.0`、`score == raw_score`
- [ ] **返回后无二次门槛过滤**（FR-009 AC4 的剩余位置）：`openviking/storage/viking_fs/_semantic.py` 的 `find`（`:256` 附近）与 `search`（`:399` 附近）在 `retriever.retrieve()` 返回之后**不得**对 `score` 做二次阈值过滤，仅向下透传 `score_threshold`；补一条回归断言固化（防后续被"顺手加过滤"）
- [ ] 通过 TASK-022 的 `test_hierarchical_retriever_confidence.py` 10 例

**相关文件**：

- `prds/OpenViking/openviking/retrieve/hierarchical_retriever.py`

**注意事项**：

- 门槛与折扣的**先后顺序**是本任务的核心约束：折扣必须在 `_passes_threshold` 之后
- `find`（QUICK，`apply_hotness=False`）与 `search`（THINKING）两条路径都要覆盖

---

#### TASK-011: 结果模型与两处序列化

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-010
- **预计时间**: 5小时
- **负责人**: [指定人员]

**任务描述**：
按 design C11 为 `MatchedContext` 增加两个字段，并在 list 与 provenance 两处序列化点输出，反序列化回读。

**实现要点**：

- `MatchedContext`（`:276-289`）在 `search_tags` 之后加 `raw_score: float = 0.0` / `confidence: float = 1.0`
- `_context_to_dict`（`:376-383`）加两个键
- `_query_result_to_dict`（`:394-410`）的 `matched_contexts[]` 每项加两个键
- `_parse_context`（`:416-427`）回读两字段
- provenance 反序列化**本期不做**

**验收标准**：

- [ ] list 响应的每个 hit 含 `raw_score` 与 `confidence`
- [ ] `include_provenance=true` 时 `provenance[].matched_contexts[]` 也含两键
- [ ] 旧 payload 反序列化 → `raw_score=0.0`、`confidence=1.0`，不抛异常
- [ ] 既有 `score` 键名与类型不变
- [ ] 通过 TASK-022 的 `test_types_confidence_serialization.py` 4 例

**相关文件**：

- `prds/OpenViking/openviking_cli/retrieve/types.py`

---

#### TASK-012: context 装配链与 `<memory>` 标签

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-011
- **预计时间**: 6小时
- **负责人**: [指定人员]

**任务描述**：
按 design C12 打通 context 装配链（`Candidate` → `AssembledEntry` → `<memory>` 标签）与 `entries[]` 序列化。

**实现要点**：

- `gather.Candidate`（`:33-46`）加 `confidence: float` / `raw_score: float`
- `gather._build`（`:242-255`）透传；`ranked_score = score - penalty` **保持不变**
- `models.AssembledEntry`（`:17-23`）加两字段；`to_dict`（`:25-35`）输出
- `budget._make_entry`（`:59-69`）透传
- `render.render_entry`（`:36-42`）在 `<memory>` 标签加 `raw_score` / `confidence` **属性**，**不写入正文**

**验收标准**：

- [ ] `Candidate` 与 `AssembledEntry` 能带出两字段（缺失时 `1.0` / `0.0`）
- [ ] `search mode="context"` 的 `entries[]` 每项含两键
- [ ] `<memory>` 标签含 `raw_score=".."` 与 `confidence=".."` 属性，且**正文内容未被注入任何说明文字**（`out.count("confidence") == 1`）
- [ ] `other_peer` 记录 `ranked_score == raw_score × factor - penalty`（有意叠加）
- [ ] 通过 TASK-022 的 `test_context_assembler_confidence.py` 8 例

**相关文件**：

- `prds/OpenViking/openviking/retrieve/context_assembler/gather.py`
- `prds/OpenViking/openviking/retrieve/context_assembler/models.py`
- `prds/OpenViking/openviking/retrieve/context_assembler/budget.py`
- `prds/OpenViking/openviking/retrieve/context_assembler/render.py`

**注意事项**：

- 这是 FR-010 AC3 能否实现的**唯一通道**：`Candidate` 或 `_build` 漏改，`<memory>` 标签就拿不到值

---

### 集成任务类别

#### TASK-013: 服务内部消费面（记忆 agent / MCP / skills）

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-011
- **预计时间**: 6小时
- **负责人**: [指定人员]

**任务描述**：
按 design C13 改造 OpenViking **自身可控**的三个消费面，使新字段不被裁剪或遗漏。

**实现要点**：

- `session/memory/tools.py:44`：`optimize_search_result` 由 `{uri, score}` 扩为 `{uri, score, raw_score, confidence}`
- `server/mcp_endpoint.py:409-410`：文本行加入 `conf` 与 `raw`；同步 docstring（`:257` / `:301-302`）
- `server/routers/skills.py:230-241`：`_skill_summary_from_hit` 加两键
- 三处均须**保持服务端顺序**，不得重排

**验收标准**：

- [ ] 记忆 agent 工具返回项含四键，顺序与服务端一致
- [ ] MCP 文本每行含 `conf X.XX` 与 `raw X.XX`
- [ ] `skills/find` 的 `skills[]` 含两键；无该字段的记录返回 `0.0` / `1.0`
- [ ] 通过 TASK-023 的三个测试类

**相关文件**：

- `prds/OpenViking/openviking/session/memory/tools.py`
- `prds/OpenViking/openviking/server/mcp_endpoint.py`
- `prds/OpenViking/openviking/server/routers/skills.py`

---

#### TASK-014: Web Studio 字段白名单与展示

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-011
- **预计时间**: 6小时
- **负责人**: [指定人员]

**任务描述**：
按 design C13/C15 同步 Web Studio 的字段白名单与展示，**并确保前端不重排**。

**实现要点**：

- `web-studio/src/lib/retrieval.ts:101-125` 的 `normalizeFindItems` 加 `raw_score` / `confidence`（带类型守卫与默认值）
- `retrieval-results.tsx:427-428` 与 `retrieval-detail-sheet.tsx:99-100` 展示三个数值
- 前端**不得对检索结果排序**（`retrieval-controls.tsx:87` 的 `.toSorted()` 属 UI 层选项，不动）

**验收标准**：

- [ ] 归一化后每项含两字段；旧响应缺字段时默认 `raw_score=0`、`confidence=1`
- [ ] 结果行与详情面板可见三值
- [ ] 归一化保持输入顺序（单测断言）
- [ ] 通过 TASK-024 的 `retrieval.test.ts` 4 例

**相关文件**：

- `prds/OpenViking/web-studio/src/lib/retrieval.ts`
- `prds/OpenViking/web-studio/src/routes/retrieval/-components/retrieval-results.tsx`
- `prds/OpenViking/web-studio/src/routes/retrieval/-components/retrieval-detail-sheet.tsx`

**注意事项**：

- `normalizeFindItems` 是逐字段白名单，**不加就会静默丢弃** —— 现象上会被误判为"管理台与客户端不一致"

---

#### TASK-015: CLI 参数、校验、回显、注入与展示

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-009, TASK-011
- **预计时间**: 10小时
- **负责人**: [指定人员]

**任务描述**：
按 design C14 完成 CLI 五处改动。

**实现要点**：

- `main.rs`：`Commands::AddResource` 加 `--confidence`（`Option<f64>`）；`manifest` 的 `conflicts_with_all` 加 `"confidence"`；派发处补字段
- `handlers.rs`：`handle_add_resource` 加形参；本地校验 `!value.is_finite() || !(0.0..=1.0).contains(&value)` 即报错，**不发出请求**
- `commands/resources.rs`：加形参；**`println!`** 回显生效值（`confidence 0.600` / `confidence 1.000 (default)`）；把 `confidence` 合并进结果体后再调 `output_success`
- `client.rs`：`add_resource` 加形参；新增 `add_resource_confidence_field` 并在 `build_body` 汇聚点调用（**显式 `0.0` 必须发送**）
- `commands/search.rs`：解析并展示 `score` / `raw_score` / `confidence`

**验收标准**：

- [ ] `--confidence 0.6` → 请求体含 `"confidence": 0.6`
- [ ] `--confidence 0.0` → 请求体含 `"confidence": 0.0`（不被 falsy 丢弃）
- [ ] 未传 → 请求体不含该键，Table 输出 `confidence 1.000 (default)`，JSON 输出含 `"confidence": 1.0`
- [ ] `--confidence 1.5` / `-0.1` → 本地报错且不发请求
- [ ] `--manifest` + `--confidence` → 互斥报错
- [ ] `--help` 含 `--confidence`
- [ ] `ov search` 卡片展示三个数值
- [ ] **未修改** `crates/ov_cli/src/output.rs` 的通用 `output_success`
- [ ] 通过 TASK-024 的四个 Rust 内联测试类

**相关文件**：

- `prds/OpenViking/crates/ov_cli/src/main.rs`
- `prds/OpenViking/crates/ov_cli/src/handlers.rs`
- `prds/OpenViking/crates/ov_cli/src/commands/resources.rs`
- `prds/OpenViking/crates/ov_cli/src/client.rs`
- `prds/OpenViking/crates/ov_cli/src/commands/search.rs`

**注意事项**：

- `output_success` 被全仓 101 处调用，**禁止**在其中注入命令特有字段
- 回显必须走 stdout（`println!`），不是 stderr

---

#### TASK-016: 文档口径同步

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-015
- **预计时间**: 6小时
- **负责人**: [指定人员]

**任务描述**：
按 design C16 同步 7 个文档文件，落实 FR-008。

**实现要点**：

- `crates/ov_cli/README.md` / `README_CN.md`：add-resource 示例段（`:250` / `:253` / `:260` / `:294`）补 `--confidence` 用法
- `docs/zh/api/02-resources.md` / `docs/en/api/02-resources.md`：请求字段表（`tags`/`tag_mode` 行位于 `:177` 附近）新增 `confidence` 行
- `docs/zh/api/06-retrieval.md` / `docs/en/api/06-retrieval.md`：结果字段说明新增两字段，并写明"**相关性门槛用未加权分；排序与展示用加权分**"
- `docs/zh/concepts/05-storage.md` / `docs/en/concepts/05-storage.md`：Schema 表（`:99-114`）新增一行
- `main.rs` 的 `--confidence` doc comment 与文档口径一致

**验收标准**：

- [ ] 上述文件均包含对应字段说明
- [ ] 明确写出 `confidence = 0.0` 是"最强降权（80%）"而非"排除"
- [ ] 旧口径零残留（TC-40）

**相关文件**：

- 见上述 7 个文件清单

---

#### TASK-017: 编译与静态检查

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-014, TASK-015, TASK-016
- **预计时间**: 4小时
- **负责人**: [指定人员]

**任务描述**：
在编码任务完成后、测试数据生成前，完成三端编译与静态检查，确保改动能构建。

**实现要点**：

- Rust：`cd crates/ov_cli && cargo check`（或项目约定的 `make` 目标）
- Python：`python -c "import openviking"` 及受影响模块的导入检查
- 前端：`cd web-studio && npx tsc --noEmit && npm run build`
- 构建日志按规范落地 `/tmp/build.log` 后再过滤查看

**验收标准**：

- [ ] `cargo check` 无 error、无新增 warning
- [ ] Python 侧无导入错误、无语法错误
- [ ] 前端 `tsc --noEmit` 与 build 通过
- [ ] 完整构建日志已落地并在失败时逐条排查

**相关文件**：

- 无（执行类任务）

**注意事项**：

- 提示词要求：编译任务必须排在编码任务之后、数据生成任务之前

---

#### TASK-019: 变更说明与下游影响点名

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-015
- **预计时间**: 4小时
- **负责人**: [指定人员]

**任务描述**：
按 design 的 R-4 / R-9 / R-13 与 Q9 约定，产出变更说明并**逐条点名**下游行为变化。

**实现要点**：

- 说明 `score` 语义变化：由"纯语义分"变为"有界加权分"；`raw_score` 承载原语义分
- **逐条点名**三处本期不改的消费端及其行为变化：
  - `bot/vikingbot/agent/tools/ov_file.py:375`、`agent/memory.py:319`、`agent/remote_skills.py:409`（用加权分做 0.35 过滤 → 低置信资源更易被过滤）
  - `examples/openclaw-plugin/memory-ranking.ts:44/49/243`（排序与 0.85 判定；且本就会二次重排）
  - `integrations/langchain/.../retrievers.py:248`、`store.py:262`（metadata 只取 score）
- 说明"门槛用未加权分、排序用加权分"的契约与 `raw_score` 的用法
- 说明回滚顺序：**先 CLI 后服务端**（`extra="forbid"`）

**验收标准**：

- [ ] 变更说明含上述全部点名项，无遗漏
- [ ] 含回滚顺序说明
- [ ] 含 `confidence = 0.0` 的语义澄清

**相关文件**：

- `prds/OpenViking/spec/resource-confidence/change-note.md`（新增）

---

### 测试任务类别

> **测试记录统一落盘（适用于 TASK-025 ~ TASK-032）**：全部执行证据（命令行、stdout/stderr 摘录、实测数值、对照数据表、未通过项现象）统一记录到 `prds/OpenViking/spec/resource-confidence/test-reports/TASK-0XX.md`（新增目录），并在验收时引用；每个测试任务的「相关文件」即该记录文件与 TASK-018 中对应的夹具目录。

#### TASK-018: 生成测试数据

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-017
- **预计时间**: 8小时
- **负责人**: [指定人员]

**任务描述**：
为后续单元测试、人工集成测试、人工性能测试、人工回归测试生成可复现的测试数据，并落库。

**实现要点**：

- 源文件夹具：`conf-high/`（3 个 md）、`conf-low/`（3 个语义相近 md）；**作用粒度夹具**：两个各含 5 个 md 的目录（`granularity-a/`、`granularity-b/`，用于 TC-41）
- **对照记录夹具**（TC-01）：直接向向量集合写入 3 条 `confidence = 1.0` 的记录，用于与导入结果逐位对照
- **最小 manifest 文件**（TC-08）：`manifest-min.json`，用于验证 `--manifest` 与 `--confidence` 互斥
- **高低置信混合集合**（TC-18 / TC-18b：**20+ 条资源**、覆盖高/中/低置信与各 `level`），并附同一集合的 skill 数据（TC-17）
- **改造前基线快照**（TC-31：NFR-001 零回归的**唯一对照手段**）：在改造前用固定查询导出一份"URI + score + 顺序"清单，落盘为 `baseline-before.json`，改造后同查询同集合逐位比对
- 直接写库的定点数据：固定 `_score` 的成对记录 —— X(`0.90, 0.5`)、Y(`0.46, 1.0`)、P(`0.50, 0.5`)、Q(`0.46, 1.0`)、A(`0.50, 0.0`)/B(`0.405, 1.0`)、A(`0.50, 0.0`)/B(`0.395, 1.0`)、A(`0.42, 0.5`)/B(`0.21, 1.0`)
- 脏数据：`confidence = 1.5`（绕过写侧校验直接写库，用于 TC-35）
- 存量集合夹具：一份 `Fields` 不含 `confidence` 的旧 schema 集合（TC-27/28）；namespace 迁移入口数据（TC-26）
- 规模数据：10 万条记录集合（TC-29）、1000 个 10KB 文件（TC-30）
- 跨 peer 数据（TC-33）、skill 数据（TC-17）、ovpack 包（TC-25）
- **配置夹具**：启用 rerank 的配置（TC-32 走 THINKING）与 `retrieval.hotness_alpha = 0.2` 的配置（TC-34）

**验收标准**：

- [ ] 全部夹具脚本幂等、可重复执行
- [ ] 定点数据的 `_score` 可复现（用于验证 TC-09~13 的数值断言）
- [ ] 脏数据、旧 schema 集合、迁移入口数据、配置夹具就绪
- [ ] **`baseline-before.json` 在改造前导出**（改造后无法补造），且覆盖 TC-31 所需查询集
- [ ] 高低置信混合集合 ≥ 20 条，用于 TC-18/18b/19
- [ ] 夹具说明（路径 + 执行命令 + 预期）已记录

**相关文件**：

- `prds/OpenViking/spec/resource-confidence/test-fixtures/`（新增目录，含脚本、夹具数据与 `baseline-before.json` 及说明）

**注意事项**：

- `baseline-before.json` **必须在改代码之前导出**，否则 NFR-001 的零回归无法验证 —— 建议本任务在 TASK-001 之前先执行其中的基线导出部分

---

#### TASK-020: 单元测试 —— 工具模块、Schema 与白名单

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-003, TASK-004
- **预计时间**: 8小时
- **负责人**: [指定人员]

**任务描述**：
编写 design「单元测试」中归属于工具模块、集合 Schema 与四套白名单的测试类。

**实现要点**：

- `tests/unit/utils/test_confidence.py`：8 例（None 缺省、边界 0.0/1.0、越界拒绝、非有限拒绝、读侧 clamp、读侧缺失兜底、factor 端点值、factor 在 1.0 处严格恒等）
- `tests/storage/test_collection_schemas.py`（扩展）：4 例（Fields 含 `DefaultValue == 1.0`、ScalarIndex 不含、旧集合告警、新集合静默）
- `tests/storage/test_viking_vector_index_backend_output_fields.py`：3 例
- `tests/storage/test_portable_fields_confidence.py`：5 例

**验收标准**：

- [ ] 四个测试类共 20 例全部通过
- [ ] 断言 `DefaultValue == 1.0`（非 0.0）
- [ ] 三套备份/迁移白名单逐一断言
- [ ] 覆盖率 ≥ 80%

**相关文件**：

- `prds/OpenViking/tests/unit/utils/test_confidence.py`（新增）
- `prds/OpenViking/tests/storage/test_collection_schemas.py`
- `prds/OpenViking/tests/storage/test_viking_vector_index_backend_output_fields.py`（新增）
- `prds/OpenViking/tests/storage/test_portable_fields_confidence.py`（新增）

---

#### TASK-021: 单元测试 —— 写入链路

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-006, TASK-008, TASK-009
- **预计时间**: 10小时
- **负责人**: [指定人员]

**任务描述**：
编写 design「单元测试」中归属于写入链路的五个测试类。

**实现要点**：

- `tests/utils/test_ingest_options.py`（扩展）：5 例
- `tests/service/test_resource_service_confidence.py`：6 例
- `tests/storage/test_add_resource_msg_confidence.py`：3 例
- `tests/server/test_api_resources.py`（扩展）：2 例
- `tests/client/test_http_client_compact.py`（扩展）：2 例

**验收标准**：

- [ ] 五个测试类共 18 例全部通过
- [ ] 覆盖"越界拒绝且未入队"、"第一道闸门已放开"、"`confidence=None` 不写入"三条关键断言
- [ ] 覆盖率 ≥ 80%

**相关文件**：

- `prds/OpenViking/tests/utils/test_ingest_options.py`
- `prds/OpenViking/tests/service/test_resource_service_confidence.py`（新增）
- `prds/OpenViking/tests/storage/test_add_resource_msg_confidence.py`（新增）
- `prds/OpenViking/tests/server/test_api_resources.py`
- `prds/OpenViking/tests/client/test_http_client_compact.py`

---

#### TASK-022: 单元测试 —— 检索打分与序列化

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-012
- **预计时间**: 10小时
- **负责人**: [指定人员]

**任务描述**：
编写 design「单元测试」中归属于检索打分、结果序列化与 context 装配链的三个测试类。

**实现要点**：

- `tests/retrieve/test_hierarchical_retriever_confidence.py`：10 例（含用户两例、紧边界成对例、有界性、脏数据 clamp、tie-break、门槛不掺置信度）
- `tests/retrieve/test_types_confidence_serialization.py`：4 例
- `tests/retrieve/test_context_assembler_confidence.py`：8 例（含 `_make_entry`、`render_entry` 的正文未被污染断言）

**验收标准**：

- [ ] 三个测试类共 22 例全部通过
- [ ] 用户样例 1/2 与紧边界成对例（19% 换位 / 21% 不换位）均通过，可区分 λ=0.2 与 0.25
- [ ] `render_entry` 断言 `out.count("confidence") == 1`（属性不重复、不写入正文）
- [ ] 覆盖率 ≥ 80%

**相关文件**：

- `prds/OpenViking/tests/retrieve/test_hierarchical_retriever_confidence.py`（新增）
- `prds/OpenViking/tests/retrieve/test_types_confidence_serialization.py`（新增）
- `prds/OpenViking/tests/retrieve/test_context_assembler_confidence.py`（新增）

---

#### TASK-023: 单元测试 —— 消费面

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-013
- **预计时间**: 6小时
- **负责人**: [指定人员]

**任务描述**：
编写 design「单元测试」中归属于服务内部消费面的三个测试类。

**实现要点**：

- `tests/session/memory/test_memory_search_tool_confidence.py`：3 例（含保序断言）
- `tests/server/test_mcp_endpoint.py`（扩展）：2 例
- `tests/server/test_api_skills_find_confidence.py`：3 例（含保序断言）

**验收标准**：

- [ ] 三个测试类共 8 例全部通过
- [ ] 含"顺序与服务端一致"的断言（FR-011 AC5）
- [ ] 覆盖率 ≥ 80%

**相关文件**：

- `prds/OpenViking/tests/session/memory/test_memory_search_tool_confidence.py`（新增）
- `prds/OpenViking/tests/server/test_mcp_endpoint.py`
- `prds/OpenViking/tests/server/test_api_skills_find_confidence.py`（新增）

---

#### TASK-024: 单元测试 —— CLI 与前端

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-014, TASK-015
- **预计时间**: 10小时
- **负责人**: [指定人员]

**任务描述**：
编写 design「单元测试」中归属于 Rust CLI 内联测试与 Web Studio 的测试。

**实现要点**：

- `crates/ov_cli/src/client.rs` 内联：2 例
- `crates/ov_cli/src/commands/resources.rs` 内联：3 例（回显两行 + JSON 合并）
- `crates/ov_cli/src/handlers.rs` 内联：3 例（越界拒绝不发请求、边界值通过）
- `crates/ov_cli/src/main.rs` 内联：4 例（解析、越界、help、与 manifest 互斥）
- `web-studio/src/lib/retrieval.test.ts`（扩展）：4 例

**验收标准**：

- [ ] `cargo test -p ov_cli` 全部通过（12 例）
- [ ] 前端 `vitest run src/lib/retrieval.test.ts` 全部通过（4 例）
- [ ] `handlers.rs` 用例断言"未发起 HTTP 请求"

**相关文件**：

- `prds/OpenViking/crates/ov_cli/src/client.rs`
- `prds/OpenViking/crates/ov_cli/src/commands/resources.rs`
- `prds/OpenViking/crates/ov_cli/src/handlers.rs`
- `prds/OpenViking/crates/ov_cli/src/main.rs`
- `prds/OpenViking/web-studio/src/lib/retrieval.test.ts`

---

#### TASK-025: 人工集成测试 —— 参数与回显

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-018, TASK-024
- **预计时间**: 4小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-01 ~ TC-08

**验收标准**：

- [ ] 八个用例全部通过
- [ ] 明确记录每次执行的命令与 stdout/stderr 原文摘录
- [ ] 未通过项记录现象、期望与证据

---

#### TASK-026: 人工集成测试 —— 数值样例与门槛分工

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-018, TASK-024
- **预计时间**: 4小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-09 ~ TC-13

**验收标准**：

- [ ] 用户样例 1（X 在 Y 前）与样例 2（Q 在 P 前）均通过
- [ ] 紧边界对（19% 换位 / 21% 不换位）均通过
- [ ] 门槛分工例（A 保留 / B 丢弃）通过
- [ ] 记录实际 `score` / `raw_score` / `confidence` 数值

---

#### TASK-027: 人工集成测试 —— 响应字段、渲染与排序一致性

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-018, TASK-024
- **预计时间**: 8小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-14 ~ TC-19、TC-18b

**验收标准**：

- [ ] 四处序列化点（list / provenance / context `entries[]` / `<memory>` 标签）均含两字段
- [ ] MCP 文本、skills、<memory>、Web Studio 四处展示均含两字段
- [ ] **管理台与 CLI 在三条端点路径上排序逐项一致**
- [ ] 记忆 agent 输出顺序与服务端一致
- [ ] `<memory>` 属性未污染正文

---

#### TASK-028: 人工集成测试 —— 保留与重置语义

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-018, TASK-024
- **预计时间**: 6小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-20 ~ TC-24

**验收标准**：

- [ ] 重复导入（不带 `--confidence`）→ 重置为 1.0
- [ ] `ov write` / watch 增量 / `ov reindex` → **置信度保持 0.4 不变**
- [ ] `ov attrs set-tags` → 置信度不变
- [ ] 记录每次操作前后的 `confidence` 实测值

**注意事项**：

- 本任务是 Q8 与 R-8 的唯一验证点，任一项失败即为**功能性缺陷**，必须回退到设计阶段处理

---

#### TASK-029: 人工集成测试 —— 备份迁移、存量集合与作用粒度

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-018, TASK-024
- **预计时间**: 6小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-25 ~ TC-28、TC-41

**验收标准**：

- [ ] ovpack 导出→导入（recompute 分支）后置信度不丢
- [ ] namespace 迁移后不丢
- [ ] 旧集合启动出现告警并给出处置指引
- [ ] 旧集合未处置时写入不报错但字段不落库（可观测）
- [ ] 目录导入的作用粒度为"单次请求单值"，两目录互不影响

---

#### TASK-030: 人工性能测试

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-018
- **预计时间**: 4小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-29、TC-30

**验收标准**：

- [ ] 10 万条集合下 `ov find` 循环 200 次的 P50/P95 与改造前对比无可见劣化
- [ ] 单次检索的向量库调用次数与改造前一致（NFR-002）
- [ ] 1000 文件导入耗时相对改造前变化 < 2%
- [ ] 记录对照数据表

---

#### TASK-031: 人工回归测试 —— 零回归与双模式

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-018
- **预计时间**: 6小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-31 ~ TC-35

**验收标准**：

- [ ] 未标注资源的 `raw_score` 与改造前 `score` **逐位一致**，顺序一致（NFR-001）
- [ ] `find`（QUICK）与 `search`（THINKING）各自满足口径，既有差异未扩大
- [ ] `other_peer` 双重折扣断言通过
- [ ] `hotness_alpha > 0` 时门槛仍按 `_final_score`
- [ ] 脏数据 `1.5` → `factor == 1.0`，无反向加成

---

#### TASK-032: 人工回归测试 —— 下游与文档

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-016, TASK-018, TASK-019
- **预计时间**: 6小时（用户执行）
- **负责人**: 用户

**测试用例**: TC-36 ~ TC-40

**验收标准**：

- [ ] `bot/vikingbot` 行为变化与变更说明一致，无异常
- [ ] `examples/openclaw-plugin` 排序仍由插件二次重排决定，`score` 已含折扣
- [ ] `integrations/langchain` metadata 新增两键且既有 `_score` 仍在
- [ ] 7 个文档文件口径同步完成
- [ ] 旧口径零残留

---

### 部署/收尾任务类别

#### TASK-033: 知识沉淀与流程收尾

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-032
- **预计时间**: 4小时
- **负责人**: [指定人员]

**任务描述**：
完成知识沉淀与流程收尾，并复核环境异常的影响。

**实现要点**：

- 触发 `knowledge-update-skill`：沉淀本轮 6 条候选知识（检索三层分数模型、消费端字段读取面清单、有界降权约定、量纲对降权算法的影响、`resource_service` 三入口边界、`extra="forbid"` 回滚顺序）
- 复核 `example-repo/skills/` 删除事件的影响与恢复情况
- 更新 `status.md` 至 Phase 4 完成

**验收标准**：

- [ ] 候选知识已去重并沉淀到合适位置（无合适位置则新建 md 并维护 README）
- [ ] 或返回"未发现需要沉淀的新增知识"及原因
- [ ] `status.md` 与本文件状态一致

**相关文件**：

- `prds/OpenViking/spec/resource-confidence/status.md`
- `skills/aegis-skill/knowledge/**`（视恢复情况）

---

## 测试汇总索引

> 仅做汇总索引；每个测试任务的实际详情见上方"详细任务列表"（统一 TASK-XXX 编号）。
> "依赖任务"列与各任务体的「依赖关系」字段、下方「任务依赖关系图」三处保持一致。

| 统一编号 | 测试类型 | 覆盖内容 | 依赖任务 | 状态 |
|----------|----------|----------|----------|------|
| TASK-018 | 测试数据生成 | 集成/性能/回归三类夹具与定点数据 | TASK-017 | 待定 |
| TASK-020 | 单元测试 | 工具模块 + Schema + 四套白名单（20 例） | TASK-003, TASK-004 | 待定 |
| TASK-021 | 单元测试 | 写入链路五类（18 例） | TASK-006, TASK-008, TASK-009 | 待定 |
| TASK-022 | 单元测试 | 检索打分/序列化/context 装配（22 例） | TASK-012 | 待定 |
| TASK-023 | 单元测试 | 服务内部消费面（8 例） | TASK-013 | 待定 |
| TASK-024 | 单元测试 | CLI 内联 + 前端（16 例） | TASK-014, TASK-015 | 待定 |
| TASK-025 | 人工集成测试 | TC-01 ~ TC-08 | TASK-018, TASK-024 | 待定 |
| TASK-026 | 人工集成测试 | TC-09 ~ TC-13 | TASK-018, TASK-024 | 待定 |
| TASK-027 | 人工集成测试 | TC-14 ~ TC-19、TC-18b | TASK-018, TASK-024 | 待定 |
| TASK-028 | 人工集成测试 | TC-20 ~ TC-24 | TASK-018, TASK-024 | 待定 |
| TASK-029 | 人工集成测试 | TC-25 ~ TC-28、TC-41 | TASK-018, TASK-024 | 待定 |
| TASK-030 | 人工性能测试 | TC-29、TC-30 | TASK-018 | 待定 |
| TASK-031 | 人工回归测试 | TC-31 ~ TC-35 | TASK-018 | 待定 |
| TASK-032 | 人工回归测试 | TC-36 ~ TC-40 | TASK-016, TASK-018, TASK-019 | 待定 |

## 任务依赖关系图

```
TASK-001 (工具模块)
   ├─→ TASK-002 (Schema) ─→ TASK-003 (检索白名单)
   │                    └─→ TASK-004 (备份/迁移白名单)
   └─→ TASK-005 (IngestOptions)
          ├─→ TASK-006 (落库写入点)
          ├─→ TASK-007 (服务层透传) ─→ TASK-009 (请求模型/路由)
          └─→ TASK-008 (队列消息)

TASK-003, TASK-004 → TASK-020 (单测:工具/Schema/白名单)
TASK-006, TASK-008, TASK-009 → TASK-021 (单测:写入链路)

TASK-003 → TASK-010 (检索打分)
TASK-010 → TASK-011 (结果模型/序列化)
TASK-011 → TASK-012 (context 装配链) ─→ TASK-022 (单测:检索/序列化)
TASK-011 → TASK-013 (服务内部消费面) ─→ TASK-023 (单测:消费面)
TASK-011 → TASK-014 (Web Studio)
TASK-009, TASK-011 → TASK-015 (CLI)
TASK-014, TASK-015 → TASK-024 (单测:CLI/前端)
TASK-015 → TASK-016 (文档同步)
TASK-015 → TASK-019 (变更说明)

TASK-014, TASK-015, TASK-016 → TASK-017 (编译与静态检查)
TASK-017 → TASK-018 (测试数据)

TASK-018, TASK-024 → TASK-025 (人工集成:参数回显)
TASK-018, TASK-024 → TASK-026 (人工集成:数值样例)
TASK-018, TASK-024 → TASK-027 (人工集成:字段/渲染/一致性)
TASK-018, TASK-024 → TASK-028 (人工集成:保留与重置)
TASK-018, TASK-024 → TASK-029 (人工集成:备份迁移/存量/粒度)
TASK-018          → TASK-030 (人工性能)
TASK-018          → TASK-031 (人工回归:零回归/双模式)
TASK-016, TASK-018, TASK-019 → TASK-032 (人工回归:下游/文档)
TASK-032 → TASK-033 (知识沉淀与收尾)
```

> **编号与呈现顺序说明**：本文件按"基础 → API → 集成 → 测试 → 收尾"分类呈现，**TASK 编号沿用拆解时的编号，不保证与呈现顺序单调**（例如 TASK-019 排在 TASK-018 之后、但编号在前）。执行顺序请以「任务依赖关系图」为准。

## 风险识别和应对

### 技术风险

| 风险项 | 影响任务 | 概率 | 影响 | 应对措施 |
| ------ | -------- | ---- | ---- | -------- |
| `DefaultValue` 未写或写成 0.0 导致未标注记录分数归零 | TASK-002, TASK-020 | 低 | 高 | TASK-020 强制断言 `DefaultValue == 1.0`；TASK-031 做零回归对照 |
| 把 `normalize_confidence_for_write` 误放进 `_submit_resource_ingestion`，watch 刷新冲掉人工标注 | TASK-007, TASK-028 | 中 | 高 | TASK-007 注意事项显式警示；TASK-028 为唯一验证点，失败即回退设计阶段 |
| context 装配链漏改（`Candidate` / `_build` / `AssembledEntry` / `_make_entry`）导致 `<memory>` 标签拿不到值 | TASK-012, TASK-022 | 中 | 中 | TASK-022 断言 `render_entry` 输出含两属性 |
| 三套备份/迁移白名单漏改导致 ovpack/迁移丢字段 | TASK-004, TASK-020 | 中 | 中 | TASK-020 逐一断言；TASK-029 做端到端往返验证 |
| 误改通用函数 `output_success` 污染全仓 101 处 JSON 输出 | TASK-015 | 低 | 高 | TASK-015 验收项显式要求"未修改 `output.rs`" |
| 前端 `normalizeFindItems` 漏改，被误判为"管理台不一致" | TASK-014, TASK-024 | 中 | 中 | TASK-024 断言归一化含两字段且保序 |
| 存量集合未处置，置信度"设置了不生效" | TASK-002, TASK-029 | 中 | 高 | 启动告警（TASK-002）+ 运维处置文档（TASK-016）+ TC-27/28 |

### 进度风险

| 风险项 | 影响 | 应对措施 |
| ------ | ---- | -------- |
| `skills/` 目录被删导致 skill 资产不可用 | 全流程 | 已用 `git show HEAD:skills/...` 与备用副本兜底；TASK-033 复核恢复情况 |
| TASK-028 失败需回退设计阶段 | TASK-028~032 | 提前在 TASK-007 把边界写成注释并单测固化，降低返工概率 |
| 任务预估偏差 | 进度延期 | 每日跟踪，按里程碑验收 |
| 人工三测依赖用户时间 | 里程碑4 | 测试数据与判据在 TASK-018 一次备齐，减少往返 |

## 质量控制

### 代码质量标准

- **测试覆盖率**: 单元测试 ≥ 80%
- **代码审查**: 所有代码必须通过同行评审（Phase 5 质检代理 + 人工验收）
- **代码注释**: 不得带需求编号（FR-xxx / ACxx / 轮次号），只描述需求事实
- **文档更新**: 代码变更同步更新文档（TASK-016）

### 交付标准

每个任务完成必须满足：

- [ ] 功能完整实现
- [ ] 测试全部通过
- [ ] 代码审查通过
- [ ] 文档更新完成

## 进度跟踪

### 每日更新

每个任务负责人需要每日更新：

- 当前进度百分比
- 遇到的问题和阻塞
- 预计完成时间调整
- 需要的支持和帮助

## 变更管理

### 任务变更流程

1. **变更申请**: 填写变更申请表
2. **影响分析**: 评估对进度和其他任务的影响
3. **客户确认**: 重大变更需客户确认
4. **任务调整**: 更新任务列表和时间计划
5. **团队通知**: 同步给所有相关人员

### 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
| ---- | ---- | -------- | ------ |
| v1.0 | 2026-10-10 | 初始版本：33 个任务（基础 4 / API 8 / 前端 2 / 集成 4 / 测试 13 / 收尾 1），4 个里程碑；测试策略→任务映射表覆盖 design 的影响范围 17 项、测试用例 43 条、单元测试 15 个测试类，无缺失条目 | AI 助手 |
| v1.1 | 2026-10-10 | 按输出前自检结论修订（9 必修 + 3 建议）：(1) 单元测试类计数 `15` → `20`（4 处，与映射表 20 行对齐）；(2) 测试用例计数 `43` → `42`（2 处，与映射表 42 行对齐）；(3) 测试任务分类计数 `13` → `14`，修正分类合计 32≠33 的算术错误；(4) **补齐 3 处依赖缺口** —— TASK-020 依赖补 `TASK-003`、TASK-021 依赖补 `TASK-006, TASK-008`、TASK-024 依赖补 `TASK-014`（原缺口会让单测任务先于被测代码启动），并同步「测试汇总索引」与「任务依赖关系图」三处一致；同时消除 TASK-006 / TASK-008 无下游的问题；(5) TASK-018 补 6 类夹具 —— TC-01 对照记录、TC-08 最小 manifest、TC-18 的 20+ 条高低置信混合集合、**TC-31 改造前基线快照 `baseline-before.json`（必须在改代码前导出）**、TC-26 迁移入口数据、TC-32/TC-34 配置夹具；(6) 为 design C17 补落点 —— TASK-009 新增"入口范围不变量"验收项与注意事项，明确 MCP `add_resource` / `ingest_temp_upload` 不实现是**有意决策**；(7) TASK-010 新增 `viking_fs/_semantic.py:256/399` 返回后无二次门槛过滤的回归断言，补齐 FR-009 AC4 最后一处；(8) 建议：新增"测试记录统一落盘到 `test-reports/TASK-0XX.md`"说明、新增"编号与呈现顺序"注释、TASK-019 归入里程碑3 | AI 助手 |
