# 变更说明：工作区 peer 改为「仓库目录名」派生

- **功能名**: workspace-repo-peer
- **日期**: 2026-09-02
- **影响面**: `examples/memory-plugin-shared/lib/workspace-peer.mjs` 及其 7 个生成副本 + 直连该源的 cursor hooks；记忆插件全家（claude-code / codex / opencode / dsh / pi / zcode / agent-plugins / cursor）
- **是否含配置开关变更**: 否（`OPENVIKING_PEER_ID`、`OPENVIKING_WORKSPACE_PEER` 语义不变）

## 1. 变更点

会话数据上传时用于归属的 actor peer（HTTP 头 `X-OpenViking-Actor-Peer`、capture 体 `peer_id`，落到服务端 `user/<user>/peers/<peer_id>`）不再由**整条工作区绝对路径**逐字符净化得到，而是由**当前 git 或 SVN 工作副本根目录的最后一层目录名**得到。

目的：同一团队使用同一个 OpenViking 账号时，不同成员的机器路径不同会导致 peer 不同、记忆互相看不到；改用仓库名后同一天然对齐。

## 2. 变更前后取值对照

| 场景 | 变更前 peer | 变更后 peer |
|---|---|---|
| 机器 A `/Users/alice/Documents/work/example-repo` | `-Users-alice-Documents-work-example-repo` | `example-repo` |
| 机器 B `/home/bob/code/example-repo` | `-home-bob-code-example-repo` | `example-repo` |
| 仓库子目录 `.../example-repo/dsh/OpenViking/examples` | 整条路径净化 | `OpenViking`（内层 `.git` 优先） |
| git worktree / submodule（`.git` 是文件） | 整条路径净化 | 该 checkout 目录名 |
| SVN 1.7 工作副本任意子目录 | 整条路径净化 | WC 根目录名 |
| SVN 1.6（每层都有 `.svn`） | 整条路径净化 | **最外层** WC 根目录名 |
| 不在任何工作副本内（如 `/tmp`） | 整条路径净化 | cwd 最后一层目录名（`tmp`） |
| 空 cwd / 全被净化为空 | `""` → `source:"none"` | 不变 |
| 显式 `OPENVIKING_PEER_ID` | 优先生效 | 优先生效（未改动） |
| `OPENVIKING_WORKSPACE_PEER=0` | 不派生 | 不派生（未改动） |

目录名中含非 `[A-Za-z0-9]` 字符时仍逐字符替换为 `-`（服务端 `peer_id` 白名单为 `^[a-zA-Z0-9_.@-]+$`，且请求头含 `/`、`\` 会被判 400，因此这一步必须保留）。例：`Product 4.0` → `Product-4-0`；`某某信托` → `----`。

## 3. 风险与处置（每条都有对应动作）

| 风险 | 现象 | 处置动作 |
|---|---|---|
| R-1 历史数据不可见 | 改造前按整条路径写入的记忆位于 `peers/<旧整条路径净化值>`，切换后默认不再自动命中 | 需要旧数据时：① 召回侧设 `OPENVIKING_RECALL_PEER_SCOPE=all`（同账号跨 peer 可见）；② 或直接设 `OPENVIKING_PEER_ID=<旧值>` 回到旧 peer |
| R-7 clone 目录名不一致 | 同一仓库被不同人 clone 成 `example-repo` 与 `example-repo-dev`，会分裂成两个 peer | 团队约定统一 clone 目录名；无法统一时由个人设 `OPENVIKING_PEER_ID=<团队约定名>` |
| R-4 同名不同仓碰撞 | 两个不同仓库目录名相同，记忆会互相可见 | 需要隔离时显式设 `OPENVIKING_PEER_ID`；或用 `OPENVIKING_RECALL_PEER_SCOPE=actor` 收紧召回 |
| R-5 嵌套仓库分裂 | 在 `outer/inner` 工作时 peer 是 `inner`，在 `outer` 工作时是 `outer` | 这是设计意图（就近归属）。若希望整树共享，在 `outer` 层工作或显式设 peer |
| R-3 claude-code 会话缓存 | 该 harness 会按 session 缓存 peer，长会话期间改环境变量不会即时生效 | 开新会话即可；不属本次修复范围 |
| 非 ASCII 目录名 | 中文仓库名净化成全 `-`，多仓可能同形 | 建议仓库目录使用 ASCII 名，或显式设 peer |
| 人际隔离能力变化 | 同账号成员由"路径天然隔离"变为"仓库名天然共享" | 若一台机器上多人共用账号需要彼此隔离，必须改用 `OPENVIKING_PEER_ID` 逐人显式配置 |

## 4. 回滚

1. 回退代码：还原 `examples/memory-plugin-shared/lib/workspace-peer.mjs` 并重跑 `node examples/memory-plugin-shared/sync.mjs`（禁止手改副本）。
2. 回退配套：还原 4 个消费方测试断言（`workspace-peer.test.mjs`、opencode/pi `config.test.mjs`、codex `session-start-commit.test.mjs`、cursor `cursor-plugin.test.mjs`）。
3. 回退文档：docs 双语 + 5 个 README + doctor reference。
4. **无需回滚代码的止血手段（推荐优先）**：在受影响机器上设置 `OPENVIKING_PEER_ID=<旧整条路径净化值>`，即恢复原 peer 归属，历史记忆立刻重新可见。

## 5. 验证证据（本机实测）

- 单测 16/16 通过，`workspace-peer.mjs` 覆盖率 行/分支/函数 100%
- CI 等价清单（`pr.yml` 的 `node --test` 全集）：改动后 413 测试 / 6 失败；HEAD 基线 401 测试 / 9 失败；6 项失败为基线失败集真子集（install-TUI/TRAE 类既存 flaky）→ **零新增失败**
- 同步面：`git status` 仅源 + 7 副本 + 测试/文档，无越界漂移；`sync.test.mjs` 3/3 通过
- 跨机器同 peer 实测：`/tmp/ovpeer/machine-a/.../example-repo` 与 `/tmp/ovpeer/machine-b/.../example-repo` 均得 `example-repo`
- 派生开销预实测：0.058 ms/次（阈值 <1ms）
- **真实会话实测（2026-09-03，本机已 link 安装 0.3.0 并重启）**：`sessions/<本会话id>/messages.jsonl` 中 13:43 之后 12 条消息 `peer_id` 全为 `example-repo`，13:43 之前 10 条为旧值 → **派生改造在真实链路上已生效**。
- **观测口径纠正（重要，避免误判为"没生效"）**：`peers/<peer>/` 目录不会随 capture 立即出现。服务端只在"本次 commit 归档批次中 `role=user` 消息的 peer 被记忆归属引用"时才创建它（`openviking/session/memory/memory_isolation_handler.py:113-137`；`docs/design/session-memory-extraction-flow.md:78-81`）。因此：
  - 判定派生是否生效 → 看 `sessions/<id>/messages.jsonl` 的 `peer_id`；
  - 判定共享记忆是否可召回 → 看 commit 后 `peers/<peer>/memories/…` 或直接用 recall；
  - 升级前创建、升级后复用的**长会话**，其归档批次含旧 peer 消息，后续 commit 仍可能写旧 peer → 必须用重启后新建的会话做验证。
- 待人工确认：TC-03~TC-12（含第二台机器/第二路径的同名仓复测）。

## 6. 发布提示

- 这是**行为变更**（同一配置的 peer 取值会变），建议在发布说明中单列，并附第 3 节 R-1 与 R-7 两条明示。
- 服务端无需改动：`peer_id` 白名单与 400 校验保持不变，新值恒为白名单字符集。
- 无数据迁移：不做旧 peer 的搬迁或合并，避免不可逆写入。
