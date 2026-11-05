# 工作区 Peer 命名改造（仓库目录名） 流程状态

> **用途**：记录 aegis-skill 流程的当前进度，支持跨会话/跨窗口恢复。
> 此文件由 AI 在流程关键节点自动更新，下次新开会话时，AI 应先读取本文件以了解上一次的进展。

## 1. 基本信息

- **功能名/Slug**: `workspace-repo-peer`
- **项目名称**: 记忆插件工作区 Peer 命名改造（git/svn 仓库目录名）
- **创建时间**: 2026-09-02 10:35
- **最后更新**: 2026-09-02 12:25
- **当前模式**: 执行（Phase 4 任务执行，自动化任务已收口）

## 2. Gate 状态机

| Gate | 状态 | 说明 |
|------|------|------|
| REQ | 已确认 | 用户口令 `确认需求`（2026-09-02），requirements.md 已落盘 |
| DESIGN | 已确认 | 用户口令 `确认设计`（2026-09-02），design.md 已落盘 |
| TASKS | 已确认 | 用户口令 `确认任务计划`（2026-09-02），tasks.md 已落盘 |
| EXEC | 允许（自动化部分已完成） | 待用户 `确认任务执行完成` 后置为已完成并放开 SCAN |
| SCAN | 禁止 | 是否允许进入漏洞扫描阶段 |
| REVIEW | 禁止 | 是否允许进入质检阶段 |

**下一口令**: `确认任务执行完成`（人工三测 TASK-007~009 由用户执行后回收结论）

## 3. 阶段进度概览

| 阶段 | 状态 | 说明 |
|------|------|------|
| Phase 1: 需求收集与分析 | ✅ 已完成 | 2 轮审查 21/21 通过；用户 `确认需求` 已落盘 |
| Phase 2: 技术设计 | ✅ 已完成 | 用户 `确认设计`，design.md 已落盘 |
| Phase 3: 任务编排 | ✅ 已完成 | 用户 `确认任务计划`，tasks.md（12 任务）已落盘 |
| Phase 4: 任务执行 | 🚧 进行中 | 自动化任务 TASK-001~006/010~012 已完成；TASK-007~009 待用户人工执行 |
| Phase 5: 漏洞扫描 | ⏳ 等待中 | — |
| Phase 6: 质检 | ⏳ 等待中 | — |
| Phase 7: 人工验收 | ⏳ 等待中 | — |

**图例**：⏳ 等待中 | 🚧 进行中 | ✅ 已完成 | ❌ 已取消 | ⚠️ 阻塞

## 4. 文档产出

| 文档 | 路径 | 状态 |
|------|------|------|
| requirements.md | `spec/workspace-repo-peer/requirements.md` | ✅ 已落盘 v1.0（已确认） |
| design.md | `spec/workspace-repo-peer/design.md` | ✅ 已落盘 v1.0（已确认） |
| tasks.md | `spec/workspace-repo-peer/tasks.md` | ✅ 已落盘 v1.0（已确认） |
| change-note.md | `spec/workspace-repo-peer/change-note.md` | ✅ 已落盘（TASK-011） |
| status.md | `spec/workspace-repo-peer/status.md` | ✅ 已生成 |

## 5. 当前阶段详情

### 当前子步骤

- Phase 4 自动化任务（TASK-001~006、010~012）全部完成，停在 EXEC 门禁等待 `确认任务执行完成`

### 当前阶段已完成的工作

- [x] Phase 1：2 轮需求审查 21/21 通过，requirements.md 已落盘
- [x] Phase 2：design.md 经 `确认设计` 落盘（含 C1 完整实现、7 副本策略、文档表、16 个单测场景、技术决策与回滚）
- [x] Phase 3：tasks.md（12 任务 + 完整测试策略→任务映射表）经 `确认任务计划` 落盘
- [x] Phase 4 TASK-001：源实现按 design C1 重写，`resolveEffectivePeerId` 函数体逐字未变
- [x] Phase 4 TASK-002：16 场景单测重写，全绿，`workspace-peer.mjs` 行/分支/函数覆盖率 100%
- [x] Phase 4 TASK-003：`node --check` + `npm run check`（含 PLUGIN_VERSION 一致）通过
- [x] Phase 4 TASK-004：`sync.mjs` 同步 7 副本，`git status` 白名单核对无越界漂移，`sync.test.mjs` 3/3
- [x] Phase 4 TASK-005：`pr.yml` 等价清单 413 测试/6 失败，与 HEAD 基线（9 失败）做失败名集合 diff → 真子集，零新增失败
- [x] Phase 4 TASK-006：`/tmp/ov-peer-fixtures.sh`（幂等）+ `/tmp/ov-peer-peer.sh` 判据脚本，11 组输出全部符合设计
- [x] Phase 4 TASK-010：10 处文档口径同步，旧示例串全仓零残留
- [x] Phase 4 TASK-011：change-note.md 落盘（含 R-1/R-7 明示与 `OPENVIKING_PEER_ID` 止血）
- [x] Phase 4 TASK-012：知识沉淀去重判断（见本轮「知识沉淀结果」小节）

### 当前阶段待完成的工作

- [ ] TASK-007 / TASK-008 / TASK-009：真实 harness 会话的人工集成/性能/回归三测（命令与判据已在 tasks.md 交付；本机安装态 `@openviking/dsh-memory-plugin@0.2.1` 需先更新或本地链接，属需用户授权的独立动作）
- [ ] 用户回复 `确认任务执行完成` → 方可进入 Phase 5

## 6. 中断恢复指引（核心）

### 恢复策略

| 中断时机 | 恢复策略 |
|----------|----------|
| Phase 1-3 中，内容已展示但等待用户确认 | AI 应先告知用户上次已展示的内容，询问"是否需要重新展示，还是可以直接确认？" |
| Phase 1-3 中，刚开始尚未展示内容 | 直接从当前阶段的第一步重新开始 |
| Phase 4 任务执行中 | 读取下方"任务执行进度"表，从第一个 `🚧 进行中` 或 `⏳ 等待中` 的任务继续 |
| Phase 5-6 分析中 | 从当前阶段的第一步重新开始（分析结果在聊天上下文中已丢失） |
| 阶段间过渡（刚完成上一阶段） | 直接从当前阶段的第二步开始 |

### 恢复检查清单

- [ ] 确认当前阶段是否正确（检查 Gate 状态是否与实际文件产出一致）
- [ ] 确认 `spec/workspace-repo-peer/` 目录下的文件是否与"文档产出"表一致
- [ ] 如果 Phase 4 且存在 tasks.md，对比 tasks.md 中的任务状态与本文件中的任务进度是否一致
- [ ] 向用户简要说明上次的进展和当前的恢复方案，获得确认后再继续

## 7. 任务执行进度（Phase 4 专属）

> 仅在进入 Phase 4 后填写。

| 任务编号 | 任务名称 | 状态 | 开始时间 | 完成时间 | 备注 |
|----------|----------|------|----------|----------|------|
| TASK-001 | 重写 shared 源 peer 派生逻辑 | ✅ 完成 | 11:55 | 11:55 | 与 design C1 一致；真实目录实测 `example-repo` / `OpenViking` |
| TASK-002 | 重写 peer 派生单元测试契约 | ✅ 完成 | 11:58 | 12:02 | 16/16 通过；覆盖率 100/100/100 |
| TASK-003 | 语法编译与版本一致性校验 | ✅ 完成 | 12:03 | 12:04 | 日志 `/tmp/ov-peer-check.log`，exit=0 |
| TASK-004 | 同步 7 个生成副本 | ✅ 完成 | 12:05 | 12:06 | 111 项 synced；变更仅源+7副本+测试；无越界 |
| TASK-005 | CI 等价自动化回归 | ✅ 完成 | 12:07 | 12:22 | 413/406/6 失败 ⊂ 基线 9 失败；零新增失败 |
| TASK-006 | 人工三测目录夹具 | ✅ 完成 | 12:20 | 12:21 | `/tmp/ov-peer-fixtures.sh` 幂等；11 组判据全对 |
| TASK-007 | 人工集成测试（TC-01~07、TC-12） | 🚧 部分实测 | 13:43 | — | **TC-01/TC-02 即时判据通过**：本会话 13:43 后 12/12 条消息 `peer_id=example-repo`（13:43 前 10 条为旧值）。`peers/example-repo` 未出现经取证为**服务端归属路由**行为，非本次缺陷；判据已于 tasks v1.1 纠正。TC-03~TC-12 待执行 |
| TASK-008 | 人工性能测试（TC-08、TC-09） | ⏳ 待用户执行 | — | — | AI 预实测 0.0585 ms/次（阈值 <1ms），人工复核 |
| TASK-009 | 人工回归测试（TC-10、TC-11、影响面 #1–#9） | ⏳ 待用户执行 | — | — | 检查单见 tasks.md |
| TASK-010 | 同步文档口径 | ✅ 完成 | 12:23 | 12:26 | 10 处（含双语官方文档）；旧示例串零残留 |
| TASK-011 | 变更说明与回滚指引 | ✅ 完成 | 12:26 | 12:27 | `spec/workspace-repo-peer/change-note.md` |
| TASK-012 | 知识沉淀去重判断 | ✅ 完成 | 12:28 | 12:30 | 见本轮知识沉淀结果 |

**当前进行中任务**: 无（自动化任务全部完成，等待人工三测与 EXEC 门禁口令）
**已完成任务数**: 9 / 12（其余 3 项为人工执行项）
**遇到问题**: 见第 8 节「执行期事实更正」与「执行期新增发现」

## 8. 阻塞与风险

### 当前阻塞

- 无

### 已识别风险

- R-1：peer 名变更后，历史数据仍在旧「整条路径净化」peer 下，新 peer 不会自动可见（同账号内需 `recallPeerScope=all` 才跨 peer 召回）。
- R-2：全局改造波及 7 个插件消费方（claude-code / codex / opencode / dsh / pi-coding-agent / zcode / agent-plugins），需回归各自测试与 5 处 README 文档口径。
- R-3：claude-code 侧存在按会话缓存 peer 的包装层（`scripts/lib/workspace-peer.mjs`），旧缓存值在会话存活期内不会被新规则刷新。**（9/3 补正：dsh 插件同样是会话级缓存，且缓存在进程内存 `runtime.mjs:24`，属全家通用行为，非 claude-code 特有。）**
- R-4：仅目录名参与命名后，不同仓库同名目录（如两个 `test`）会落到同一 peer。
- R-5：同一外层仓库根启动 → 外层仓名；在其内层仓（如 `dsh/OpenViking`）启动 → 内层仓名，二者是不同 peer（nearest-root 语义必然结果）。
- R-6：peer 变短后同账号下跨项目误召回概率上升。
- R-7：同仓库若被成员 clone 成不同目录名（如 `example` vs `example-copy`），peer 仍会分裂，需团队约定目录名或用显式 `OPENVIKING_PEER_ID` 覆盖。
- R-8（执行期新增，14:30 取证）：**升级前创建、升级后复用的长会话**其归档消息批次同时含旧/新 peer，服务端 peer 归属取自"被归档批次里 `role=user` 消息的 `peer_id`"，因此这类会话后续 commit 仍可能把记忆写进旧 peer。处置：升级后一律新开会话；旧会话让其收尾 commit 后不再复用。属服务端既有归属规则，不在本次修复范围。

### 执行期事实更正（Phase 4）

- **更正 1（影响面）**：`examples/cursor-memory-plugin` 经 `import "../../memory-plugin-shared/lib/agent-hook-runtime.mjs"` **直连共享源**，同属本次消费方。Phase 1 判定「cursor 不消费该 lib」有误——当时按 vendored 副本路径 grep，未覆盖直连相对路径 import。requirements.md FR-009 已升 v1.1 更正。
- **更正 2（取证姿势）**：Phase 1 用「字面量旧示例串」检索受影响断言，漏掉 4 处**消费方层**断言（opencode `tests/config.test.mjs`、pi `tests/config.test.mjs`、codex `scripts/session-start-commit.test.mjs`、cursor `scripts/cursor-plugin.test.mjs`）。执行期已全部按新契约修正并转绿，未禁用或放宽任何测试。

### 执行期新增发现

- 本机 `~/.npm` 在 workspace-write 沙箱下不可写，`npm ci` 需 `--cache` 重定向到 `/tmp`（环境约束，未改仓库配置）。
- `install-tui` / installer 类 3 项在基线与改动后之间随机翻转（子进程时序 flaky），与本次无关；因此判定一律以**失败测试名集合 diff**为准，不看失败计数。
- **9/3 实测新增（关键）**：peer 是**会话级 + 进程内缓存**——`runtime.mjs:24` `this.states = new Map()`，`stateFor()` 在首次触碰某会话时用 `session.header?.cwd || process.cwd()` 解析一次 peer 并写入 `state.config.peerId`，此后该会话所有 capture/commit 都复用该值。因此**升级后仍在运行的旧进程 / 旧会话会继续把数据写进旧 peer**，直到进程重启且新开会话。R-3 的适用范围据此从"claude-code 特有"更正为"全家通用"。
- 取证工具可信度标定：本沙箱下 bash 的 `[ -e file ]` 对 workspace 外路径会**假阴性**（`~/.openviking/ovcli.conf` 明明存在却判否）；`node` 的 `existsSync` 与 `ls` 正常。跨 workspace 取证必须用后两者。
- 附带事实：旧 peer `-Users-alice-Documents-work-example-Product4-0-EXAMPLE-202609` 对应目录已不存在（`ls` 确认），其数据不会被新会话命中；Product 真实工作副本根是否有 `.svn` 待用户提供路径后核验。
- **14:30 二轮取证纠正上一轮结论（重要）**：用户确已"完全重启 + 新开会话"，故"旧进程内存缓存"**不是**本次现象的主因，它只解释 9/1 创建那条旧会话（`0ffda040`）今天仍写旧 peer。本会话 13:43 后 12/12 条消息 peer 已全新、且 13:57 已成功 commit（`commit_count=4`），但 `peers/example-repo` 仍未创建。
- **真因（服务端归属路由，非本次改造缺陷）**：`peers/<peer>/` 只在"该次 commit 归档批次中 `role=user` 消息的 peer 被某条记忆显式归属引用"时才创建。证据链：`memory_isolation_handler.py:113-137`（`_is_peer_owner_message` 仅 user 消息、`allowed_peer_ids` 来源）、`:167-169`（`peer_enabled=false` 的类型会剥掉 peer_id 落 user 级）、`docs/design/session-memory-extraction-flow.md:53-54, 78-81`（路由表）、`session.py:227-251`（`allowed_peer_ids = _message_peer_ids(messages) if policy.peer_enabled else set()`）。实测对照：13:40 后 `peers/` 下唯一写入是 example 旧 peer 会话 13:55 的 13 个 `memories/events/**` 文件；本会话 13:52–13:58 的提取产物全在 user 级（`memories/entities/**`、`memories/preferences/<user>/**`）。
- **由此暴露的验收缺陷**：tasks.md 原 TC-01/TC-02 判据写成"到服务端确认数据落在同一 `peers/example-repo`"，该判据在派生正确时也可能长期不成立 → 已升 tasks v1.1 改为"`messages.jsonl` 的 `peer_id` 为即时判据、`peers/` 为延迟判据且不得据此判失败"。
- **长会话混合风险（新登记 R-8）**：升级前创建、升级后复用的长会话，其归档批次同时含旧/新 peer 消息，`allowed_peer_ids` 会含两个名字，后续 commit 的 peer 归属取决于被归档那批消息 → 可能继续写旧 peer。规避：升级后新开会话；或让旧会话结束并 commit 收尾。

## 9. 变更记录

| 时间 | 变更内容 | 变更前状态 | 变更后状态 |
|------|----------|------------|------------|
| 2026-09-02 10:35 | 创建 status.md，开始 Phase 1 | — | Phase 1 进行中 |
| 2026-09-02 10:52 | 需求审查 2 轮 21/21 通过并展示正文；用户 `确认需求` 后落盘 requirements.md | Phase 1 进行中 | REQ=已确认, DESIGN=允许 |
| 2026-09-02 11:02 | 展示 design 正文；用户 `确认设计` 后落盘 design.md；风险补 R-5/R-6/R-7 | DESIGN=允许 | DESIGN=已确认, TASKS=允许 |
| 2026-09-02 11:10 | 展示 tasks 正文（TASK-001~012 + 映射表），等待 `确认任务计划` | Phase 2 完成 | Phase 3 进行中 |
| 2026-09-02 11:50 | 用户 `确认任务计划` → tasks.md 落盘，EXEC 放开 | Phase 3 进行中 | Phase 4 进行中 |
| 2026-09-02 12:22 | TASK-001~005 完成；修正 4 处消费方层旧断言；确立「失败名集合 diff 对基线」回归判定法 | 代码未变更 | 源+7副本+5测试文件变更，CI 等价零新增失败 |
| 2026-09-02 12:30 | TASK-006/010/011/012 完成；requirements.md 升 v1.1（cursor 消费方事实更正） | 文档未同步 | 10 处文档口径统一 + change-note 落盘 |
| 2026-09-03 14:10 | 一轮排障取证：确认安装为 link 指向 checkout、加载实现为新版、无显式 peer；判定"旧进程会话级缓存"为现象成因 | 用户反馈"没按新 peer 上传" | TASK-007 标记部分实测通过；R-3 补正为全家通用 |
| 2026-09-03 14:35 | 二轮取证推翻一轮主因判断：用户确已重启+新开会话，本会话 13:43 后 12/12 消息 peer 为新值且 13:57 commit 成功；真因为服务端 peer 归属路由（`peers/` 需归属型记忆才创建），并实测 `safe_peer_id('example-repo')` 通过 | 判据不可操作 | tasks.md 升 v1.1（TC-01/02 双级判据）；新增 R-8；change-note 补观测口径；知识库补第 2 节第 5 条 |

---

**最后更新**: 2026-09-02 10:35
**更新人**: AI 助手
