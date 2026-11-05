# 资源置信度：变更说明（对外）

- **版本**: v1.0 ｜ **日期**: 2026-10-10
- **对应**: `requirements.md` v1.8、`design.md` v1.1、`tasks.md` v1.1

## 一、一句话说明

`ov add-resource` 新增可选参数 `--confidence`（闭区间 `[0.0, 1.0]`，缺省 `1.0`），
用于人工标注资源的可信度；检索结果的排序分按该标注做**有界降权**，并新增两个返回字段
`raw_score` 与 `confidence`。

## 二、字段语义

| 字段 | 含义 | 位置 |
|------|------|------|
| `confidence` | 人工置信度。`1.0` = 未标注、不折扣；`0.0` = **最强降权**（排序分压到自身的 80%），**不表示排除该资源** | 请求参数 + 检索结果 |
| `raw_score` | **未加权**检索分，等于改造前的 `score` | 检索结果 |
| `score` | **加权**排序分，`score == raw_score × (1 - 0.2 × (1 - confidence))` | 检索结果 |

**分工口径（对外契约）**：

> **相关性门槛用未加权分；排序与展示用加权分。**

即 `score_threshold`（以及 MCP 的 `min_score`、CLI 的 `-t/--threshold`）只作用于 `raw_score`。
人工置信度**不参与任何门槛判定**，因此标注不会让一条本应命中的记录消失，只会改变它与同档记录的先后。

## 三、`score` 语义变化（最重要的一条）

改造前：`score` 是"语义相关度（与热度的加权混合）"。
改造后：`score` 是"在上一项基础上再乘置信度折扣"，`raw_score` 承载原来那个值。

未标注（`confidence = 1.0`）的记录：折扣因子恰为 `1.0`，`score` 与改造前**逐位一致**、顺序一致（NFR-001）。
只有显式标注过的记录会变。

## 四、下游消费端行为变化（逐条点名）

以下位置**本次未改动**，但因为 `score` 语义变化而行为随之改变。上线前请逐条确认可接受：

| # | 位置 | 现用口径 | 变化后行为 |
|---|------|----------|------------|
| 1 | `bot/vikingbot/agent/tools/ov_file.py:375` | 用 `score` 与阈值比较 | 低置信资源更易被阈值挡掉 |
| 2 | `bot/vikingbot/agent/memory.py:319` | 用 `score` 过滤记忆 | 同上 |
| 3 | `bot/vikingbot/agent/remote_skills.py:409` | 用 `score` 过滤技能 | 同上 |
| 4 | `examples/openclaw-plugin/memory-ranking.ts:44`、`:49` | 读取 `score` 参与插件内排序与判定 | 服务端顺序已含折扣；插件随后**再按自己的规则重排一次**（既有行为，未改） |
| 5 | `examples/openclaw-plugin/memory-ranking.ts:243`（`rankForInjection`） | 二次重排 | 与 Web Studio / CLI 的顺序**本来就可能不同**，这与本次改造无关 |
| 6 | `integrations/langchain/.../retrievers.py:248`、`store.py:262` | metadata 只取 `score` | metadata 现在多出 `raw_score` / `confidence`；`score` 含义如上 |

**给下游的迁移建议**：若某个消费端希望"只按语义相关性过滤、不受人工标注影响"，
应改用 `raw_score`；若希望"按最终排序分过滤"，继续用 `score`。

## 五、新增参数

```bash
ov add-resource ./docs --confidence 0.6        # 中等可信
ov add-resource ./vendor-docs --confidence 0.2 # 低可信，降权但不排除
ov add-resource ./specs                        # 等效 --confidence 1.0
```

- 越界（`< 0` 或 `> 1`，含 `nan` / `inf`）或非数字：CLI 本地报错、服务端返回 `InvalidArgumentError`，**不做静默截断**。
- **未指定时服务端按 `1.0` 显式写入**：对同一 URI 重复导入即可把置信度重置为 `1.0`。
- 作用粒度：单次请求携带单值，广播到本次导入产生的全部 L0/L1/L2 记录；目录内高低置信混排需分批导入。
- 与 `--manifest` 互斥；不能写入 `--args`。

## 六、重写与重索引保留标注

| 操作 | `confidence` 结果 |
|------|-------------------|
| `ov add-resource`（不带 `--confidence`） | 重置为 `1.0` |
| `ov write`（修改正文） | **保留原值** |
| watch 定时刷新 | **保留原值** |
| `ov reindex` | **保留原值** |
| `ov attrs set-tags` | **保留原值** |

## 七、升级与回滚

### 升级

- 新集合：自动带 `confidence` 字段，无需额外操作。
- **存量集合不含该字段**：启动日志会出现明确告警（`Existing collection ... lacks the 'confidence' field`）。
  不处置时携带置信度的写入**不会报错**，但该字段会被静默丢弃（检索结果恒为 `1.0`）。建议把该告警纳入健康检查。
- 处置二选一：① 重建集合（`ov reindex` 全量重建）；② 由运维在向量库侧为集合追加 `confidence: float32`、默认 `1.0`。
- 配置项：**无新增**。λ 固定为 `0.2`（`openviking/retrieve/hierarchical_retriever.py` 的模块级常量）。

### 回滚

- 代码回滚即可，**无需重建集合**：多出的 `confidence` 字段对旧代码无害（旧代码不投影该字段）。
- ⚠️ **回滚顺序：先回滚 CLI，再回滚服务端。**
  服务端的 `AddResourceRequest` 使用 `extra="forbid"`：若服务端先回滚，新版 CLI 发来的 `confidence`
  会被判为未知字段并拒绝整个请求。

## 八、SDK 支持

`confidence` 已在三个 SDK 中透出：Python（`AddResourceOptions`）、Go（`AddResourceOptions.Confidence`）、
TypeScript（`AddResourceOptions.confidence`）。未传时不发送该键，以兼容尚未升级的服务端。

## 九、代码注释约定

本次改动新增的代码注释只描述需求事实，**不含需求编号、任务编号或评审轮次号**。
