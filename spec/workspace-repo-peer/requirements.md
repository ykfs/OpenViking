# 工作区 Peer 命名改造（仓库目录名）需求规格书

## 项目信息

- **项目名称**: OpenViking 记忆插件（memory-plugin-shared 供给的全部 harness 插件）
- **创建日期**: 2026-09-02
- **版本**: v1.1
- **状态**: 已确认（用户口令 `确认需求`，2026-09-02；v1.1 为 Phase 4 执行期事实更正，未新增需求项）

## 项目背景

### 业务目标

让同一团队在同一 OpenViking 账号下，围绕**同一个代码仓库**产生**同一个 peer**，从而实现会话记忆的团队共享。当前 peer 名由整条绝对路径净化而来，必然包含用户主目录差异（`/Users/alice/…` vs `/home/bob/…`），因此**同仓库不同人永远落在不同 peer**，共享目标无法达成。

### 目标用户

- 多人协作、共用一套 OpenViking 服务的研发团队
- 主要使用场景：在 DSH / Claude Code / Codex 等 harness 中打开某个 git 或 svn 工作副本进行会话

### 问题陈述

`examples/memory-plugin-shared/lib/workspace-peer.mjs:1-3`

```js
export function deriveWorkspacePeerId(cwd) {
  return String(cwd || "").replace(/[^A-Za-z0-9]/g, "-");   // 绝对路径全量参与命名
}
```

## 术语定义

- **仓库根**：从会话工作目录向上逐级探测，命中 `.git` / `.svn`（目录或文件均可）的最后一个合法目录；SVN 1.6 型（每层都有 `.svn`）取**最外层** `.svn` 所在目录，git 取**最近**的 `.git` 所在目录；同级同时存在时 git 优先。
- **末层目录名**：仓库根路径的 basename（如 `/a/b/example-repo` → `example-repo`）。
- **净化**：沿用现有规则 `replace(/[^A-Za-z0-9]/g, "-")`，保证跨机器一致且满足服务端字符集。

## 关键证据核对（Evidence Checklist）

- [x] **入口证据**：`dsh-memory-plugin/config.mjs:82`（进程级默认，`resolveConfig`）与 `dsh-memory-plugin/runtime.mjs:31`（每会话，`stateFor`）→ 二者均调用 `shared/workspace-peer.mjs` 的 `resolveEffectivePeerId`；另有 `dsh-memory-plugin/servers/mcp-proxy.mjs:27`、claude-code `scripts/lib/workspace-peer.mjs:10,23`、codex 4 处（`auto-capture.mjs:102`、`auto-recall.mjs:39`、`pre-compact-capture.mjs:57`、`session-end.mjs:63`、`session-start-commit.mjs:344`）、opencode `lib/config.mjs:313` + `servers/mcp-proxy.mjs:30`、zcode `agent-hook-runtime.mjs:176,245,256`、pi `shared/workspace-peer.mjs`。
- [x] **参数流证据**：`session.header.cwd`（DSH 会话工作目录）→ `resolveEffectivePeerId({cfg,cwd})` → `state.config.peerId` → HTTP 头 `X-OpenViking-Actor-Peer` + capture body `peer_id`（`client.test.mjs:42,66` 断言、`README.md:159`）→ 服务端命名空间 `user/<user>/peers/<peer_id>`（OpenViking 虚拟路径，`core/namespace.py:126`）。
- [x] **调用频率/批次策略**：每会话 1 次（`states` Map 缓存，`runtime.mjs:28`）+ 进程启动 1 次；非循环热路径。隔离键 = `peer_id`。
- [x] **数据源与落点证据**：读 = 会话消息/召回接口；写 = capture/commit 的 `peer_id` 字段。无数据库表变更。
- [x] **多库/方言证据**：不适用（纯 Node 侧插件逻辑，无 SQL）。
- [x] **可行性实测**：只读脚本模拟向上探测 → `example-repo` 根命中 `.git`；`example-repo/dsh/OpenViking/examples` 命中内层 `.git`（OpenViking）与外层（example-repo）；`/tmp`、`/` 无仓库。
- [x] **服务端契约取证**：`core/identifiers.py:8` peer_id 必须匹配 `^[a-zA-Z0-9_.@-]+$`、不得为 `.`/`..`、`@` 至多 1 个；官方文档 `docs/*/agent-integrations/16-capability-reference.md:206,208` 记录该头含 `/` 或 `\` 时服务端返回 400。

> 写作约定：本 spec 目录内的文档刻意不书写 OpenViking 虚拟路径的完整协议前缀（仅写 `user/<user>/peers/<peer_id>`），因为运行态安装的 `@openviking/dsh-memory-plugin@0.2.1` 的 uri-guard 会扫描 `write` 正文并把其中出现的该前缀误判为虚拟路径而拒绝本地写入（本仓 0.3.0 源码已在 `memory-plugin-shared/lib/uri-guard.mjs:16-35` 修复该误判，属独立缺陷，不在本次范围）。

## 功能需求 (使用 EARS 记号法)

### FR-001: 仓库根定位

**需求描述**：
当系统需要为某个工作目录派生 peer，且该目录本身或其任一上级目录存在 `.git` / `.svn` 标记时
系统应该 按术语定义返回唯一的仓库根目录（git 取最近、SVN1.6 型取最外层、同级 git 优先）

**业务价值**：peer 身份锚定在"项目"而非"某个人的路径"，是团队共享的前提。

**验收标准**：

- [ ] 输入 `/a/b/example-repo/dsh/OpenViking/examples`（内层为 git 仓）→ 根为 `…/dsh/OpenViking`
- [ ] 输入含 `.git`（文件形式，worktree/submodule）的目录 → 命中该目录
- [ ] 多层同名 `.svn`（SVN 1.6 型）→ 返回最外层
- [ ] 未命中任何标记 → 返回空（交 FR-003）

**优先级**：高

---

### FR-002: peer 名取仓库根末层目录名

**需求描述**：
当 FR-001 成功定位到仓库根时
系统应该 以该根目录的末层目录名经净化后的结果作为 peer 值，且不再包含任何路径分隔符

**业务价值**：直接消除"每人 peer 不同"的根因。

**验收标准**：

- [ ] `/Users/alice/work/example-repo` 与 `/home/bob/work/example-repo` → 均得 `example-repo`
- [ ] 目录名 `Product4.0` → `Product4-0`
- [ ] 中文目录名 `某某信托` → 全净化，结果仍满足服务端字符集（为空则走 FR-004）
- [ ] 结果字符串中不含 `/` 或 `\`

**优先级**：高

---

### FR-003: 非仓库目录回退

**需求描述**：
当 FR-001 未定位到任何 git/svn 仓库根时
系统应该 回退使用工作目录的末层目录名作为 peer 基础值（净化后）

**业务价值**：与"末层目录名"语义一致，避免临时目录退化为含个人路径的长 peer。

**验收标准**：

- [ ] cwd=`/tmp/scratch`（无仓库）→ peer `scratch`
- [ ] cwd=`/`（根目录，basename 为空）→ 返回空 peer，`source: "none"`
- [ ] cwd 为空串/`null` → 返回空 peer，`source: "none"`

**优先级**：高

---

### FR-004: 净化结果合法性兜底

**需求描述**：
当末层目录名净化后为空串、或结果与服务端非法值冲突时
系统应该 返回空 peer（`source: "none"`），由调用方按"无 peer"既有分支处理

**业务价值**：不向服务端发送非法 peer，避免 400。

**验收标准**：

- [ ] 净化结果为空 → `source: "none"`，不抛异常
- [ ] 任何情况下输出均满足 `^[a-zA-Z0-9_.@-]+$` 且不为 `.`/`..`

**优先级**：中

---

### FR-005: 显式 peer 优先级保持不变

**需求描述**：
当配置或环境变量提供了显式 peer 时
系统应该 优先使用显式值，本次改造不得改变 `OPENVIKING_PEER_ID`/`peerId` > 工作区派生 > none 的既有优先级

**业务价值**：不破坏既有部署方的显式指定能力。

**验收标准**：

- [ ] `peerId="configured"` + 位于 git 仓库内 → peer 为 `configured`，`source: "explicit"`
- [ ] 既有相关测试（`config.test.mjs`、`mcp.test.mjs`）不改断言即通过

**优先级**：高

---

### FR-006: 派生开关语义保持不变

**需求描述**：
当 `workspacePeer` 被显式设为 `false`（配置或 `OPENVIKING_WORKSPACE_PEER=0`）时
系统应该 不进行任何派生，返回空 peer

**验收标准**：

- [ ] `{workspacePeer:false, cwd:"/x/proj"}` → `{peerId:"", source:"none"}`
- [ ] dsh 现有 `workspacePeer:false` 测试（`index.test.mjs:25`、`runtime.test.mjs:288`、`live-recall.test.mjs:19` 等）全部保持通过

**优先级**：高

---

### FR-007: 探测异常不影响启动

**需求描述**：
当文件系统探测过程中发生权限拒绝或 IO 异常时
系统应该 吞掉异常并按 FR-003/FR-004 回退，绝不向会话启动路径抛出错误

**业务价值**：记忆插件故障不得阻塞主会话。

**验收标准**：

- [ ] 模拟不可读上级目录 → 不抛异常，peer 为空或回退值
- [ ] 会话初始化链路（`runtime.stateFor`）无新增异常出口

**优先级**：中

---

### FR-008: 生成物与源同步（依赖 FR-002）

**需求描述**：
当 shared 源文件修改完成后
系统应该 通过 `examples/memory-plugin-shared/sync.mjs` 重新生成 7 个 target 下的 `workspace-peer.mjs` 副本，且 `sync.test.mjs` 判定为已同步

**业务价值**：副本首行为 `DO NOT EDIT` 的生成物，手工改会被同步覆盖并造成漂移。

**验收标准**：

- [ ] `node examples/memory-plugin-shared/sync.mjs` 执行成功
- [ ] `memory-plugin-shared/sync.test.mjs` 通过
- [ ] 无人在生成物副本上手工改动

**优先级**：高

---

### FR-009: 全消费方行为一致

**需求描述**：
当任一消费方（claude-code / codex / opencode / dsh / pi-coding-agent / zcode / agent-plugins / cursor）派生工作区 peer 时
系统应该 得到与新规则完全一致的 peer 值

**验收标准**：

- [ ] CI 中 memory plugin 测试集合全绿（`pr.yml` 的 `node --test` 列表：memory-plugin-shared/*、dsh-memory-plugin/*.test.mjs、opencode tests、pi tests、agent-plugins/plugin.test.mjs）
- [ ] codex / claude-code / zcode / cursor 各自的插件测试通过（cursor 直连共享源，见下）
- [ ] cursor-memory-plugin **属于消费面**：其 `scripts/cursor-hook.mjs` 以 `import "../../memory-plugin-shared/lib/agent-hook-runtime.mjs"` 直连共享源（v1.1 更正：v1.0 曾误判为"不消费该 lib"，因当时只按 vendored 副本路径检索）；它没有自有派生实现，故无需同步副本，但其测试断言随新规则更新
- [ ] trae-* / openclaw 不在改动面内（不消费该 lib；openclaw 的 peer 由 `peer_role`/`peer_prefix` 推导）

**优先级**：高

---

### FR-010: 文档口径同步

**需求描述**：
当命名规则变更后
系统应该 更新所有描述"路径逐字符净化"旧口径的文档，示例改为仓库目录名口径

**验收标准**：

- [ ] `docs/en/agent-integrations/16-capability-reference.md:206`、`docs/zh/...:208`
- [ ] `examples/memory-plugin-shared/README.md`（22-25 行段落）
- [ ] `examples/claude-code-memory-plugin/README.md:143`、`codex-memory-plugin/README.md`、`opencode-plugin/README.md:154`、`pi-coding-agent-extension/README.md:91,119`
- [ ] `examples/dsh-memory-plugin/README.md:124` 及 `claude-code-memory-plugin/skills/ov-memory-doctor/reference.md:34`
- [ ] 更新后 `grep -r` 检索旧示例字符串无残留

**优先级**：中

---

### FR-011: 单元测试契约更新

**需求描述**：
当实现完成后
系统应该 在 `memory-plugin-shared/workspace-peer.test.mjs` 中以确定性夹具（临时目录 + 伪造 `.git`/`.svn` 标记）覆盖新规则，并删除对旧整条路径命名的断言

**验收标准**：

- [ ] 覆盖：git 命中、svn 命中、SVN1.6 多层、嵌套仓库取内层、非仓库回退、根目录空值、净化非法字符、显式优先、开关关闭、异常不抛
- [ ] 测试确定性：不依赖执行机真实主目录、不依赖网络、不依赖 git/svn 可执行文件
- [ ] 新增逻辑分支覆盖率 ≥ 80%

**优先级**：高

---

### FR-012: 诊断链路一致

**需求描述**：
当用户运行 doctor/诊断能力查看生效 peer 时
系统应该 展示与新规则一致的值及其 `source`

**验收标准**：

- [ ] `claude-code-memory-plugin/scripts/ov-memory-doctor.mjs:370`、`codex-memory-plugin/scripts/ov-memory-doctor.mjs:324` 输出 peer 为新规则值（复用同一函数，需回归验证）

**优先级**：低

## 非功能需求

### NFR-001: 性能需求

当每次会话派生 peer 时
系统应该 仅使用同步文件系统探测，**不得启动子进程**（不调用 `git`/`svn` 可执行文件）；单次派生开销应为个位数毫秒（典型路径深度 ≤ 8 次 stat）

### NFR-002: 依赖约束

当实现该能力时
系统应该 只使用 Node 内置 `node:fs` / `node:path`，不新增任何 npm 依赖，不改 `package.json` 依赖树

### NFR-003: 向后兼容

当 peer 命名规则变更时
系统应该 保持对外 HTTP 契约字段不变（仍为 `X-OpenViking-Actor-Peer` / body `peer_id`），服务端零改动

### NFR-004: 回归基线

当变更提交时
系统应该 使 CI 既有记忆插件测试集合全绿，`node --check` 无语法告警

### NFR-005: 跨平台

当运行于 Windows（`D:\work\proj`）时
系统应该 仍能正确取到末层目录名，净化后不含 `:` 与 `\`

## 约束条件

### 技术约束

- `dsh-memory-plugin/shared/workspace-peer.mjs` 等副本是**生成物**（首行 `// GENERATED … DO NOT EDIT.`），禁止手工编辑，必须经 `sync.mjs` 产出。
- 服务端 peer_id 校验 `^[a-zA-Z0-9_.@-]+$`（`openviking/core/identifiers.py:8`），且该头含 `/`、`\` 直接返回 400。
- 保持 `deriveWorkspacePeerId(cwd)` / `resolveEffectivePeerId({cfg,cwd})` 的**函数签名与同步调用特性**不变（pi 侧 `shared/workspace-peer.d.mts` 依赖签名；`resolveConfig`/`stateFor` 均为同步路径）。
- 构建/测试须绑定 `NODE_PATH=/Users/alice/.nvm/versions/node/v23.11.0/bin/node`。

### 业务约束

- 团队共享的前提是"共用同一 OpenViking 用户/账号"，peer 仅在该命名空间内区分项目。
- 不引入配置开关做 path/repo 双模式（用户决策：全局统一仓库名）。

## 风险

- **R-1 历史数据不可见**：旧 peer 为整条路径净化值，切换后新 peer 读不到旧数据（除非 `recallPeerScope=all` 且同账号）。
- **R-2 影响面**：shared 源变更波及 7 个插件 + 8 处文档。
- **R-3 claude-code 会话缓存**：`scripts/lib/workspace-peer.mjs` 会把 workspace peer 持久化到 `ws-peer-<sid>.json`，老会话存活期内仍用旧值。
- **R-4 同名仓库碰撞**：不同仓库末层目录同名（如两个 `test`）会落入同一 peer。
- **R-5 嵌套仓库分裂**：同一外层仓库根启动 → `example-repo`；在其内层 `dsh/OpenViking` 启动 → `OpenViking`，两者是不同 peer（nearest-root 语义的必然结果）。
- **R-6 召回粒度变化**：peer 变短后同账号下跨项目误召回概率上升。

## 验收总则

- [ ] FR-001~FR-009 全部实现且对应单测通过
- [ ] FR-010 文档无旧口径残留
- [ ] NFR-001/002 经代码审查确认（无子进程、无新依赖）
- [ ] CI 记忆插件测试集合全绿；`node --check` 通过
- [ ] 真实验证：在 `example-repo` 仓库内启动 DSH 会话，上报 peer 为 `example-repo`

## 范围说明

### 包含范围

- shared 源 `workspace-peer.mjs` 的派生规则
- `sync.mjs` 重新生成 7 个副本
- `workspace-peer.test.mjs` 契约重写
- 10 处文档口径更新（分布在 8 个文件）
- 上述回归验证

### 不包含范围

- 历史 peer 数据迁移 / 新旧 peer 别名（仅提供结论与人工处置建议）
- 服务端 `peer_id` 校验规则改动
- cursor-memory-plugin 的自有派生实现（v1.1 更正：cursor 直连共享源、无自有实现，因此无代码可改，但其测试断言已纳入本次改动面）
- trae-* / openclaw-plugin（不消费该 lib）
- 新增 `OPENVIKING_WORKSPACE_PEER=repo|path` 之类的模式开关
- claude-code 会话缓存失效策略改造（作为 R-3 记录，不在本次修复）
- 运行态 `@openviking/dsh-memory-plugin@0.2.1` 的 uri-guard 误拦缺陷修复（已在本仓 0.3.0 源码修复，属独立事项）

## 变更记录

| 版本 | 日期   | 变更内容 | 变更人 |
| ---- | ------ | -------- | ------ |
| v1.0 | 2026-09-02 | 初始版本（含 2 轮内部审查修订：拆分 FR-001/002，补嵌套仓库·空值·异常边界，补 NFR-001/002，补 FR-008 依赖链，闭环 PR-02 运行时绑定偏离） | AI 助手 |
| v1.1 | 2026-09-02 | Phase 4 执行期事实更正：cursor-memory-plugin 经直连相对路径 import 消费共享源，从「不包含范围」移入 FR-009 消费面；trae-*/openclaw 维持不在面内。文档口径数量按实际改写为 10 处（8 个文件） | AI 助手 |
