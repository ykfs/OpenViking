# 工作区 Peer 命名改造（仓库目录名）实现任务

## 文档信息

- **项目名称**: OpenViking 记忆插件工作区 peer 派生规则
- **创建日期**: 2026-09-02
- **版本**: v1.0
- **状态**: 已确认（用户口令 `确认任务计划`，2026-09-02）
- **相关文档**: requirements.md v1.0, design.md v1.0

## 项目概览

- **总计任务数**: 12个
- **预计总工期**: 1.5 个工作日（自动化实现+回归约 3.5h，人工三测约 2h）
- **主要里程碑**: 4个
- **项目开始日期**: 2026-09-02
- **预计完成日期**: 2026-09-03（人工测试排期由用户决定）

## 任务分类统计

- **基础任务**: 1个（TASK-001 核心实现）
- **测试任务**: 6个（TASK-002 单测、TASK-003 编译校验、TASK-005 自动化回归、TASK-006 测试数据夹具、TASK-007/008/009 人工三测支持）
- **集成任务**: 1个（TASK-004 生成物同步）
- **文档任务**: 3个（TASK-010 口径同步、TASK-011 变更说明、TASK-012 知识沉淀）
- **前端开发**: 0个（不适用）
- **部署任务**: 1个（并入 TASK-011 发布提示，无独立部署动作）

## 里程碑规划

### 里程碑1: 核心逻辑与单元契约（TASK-001 ~ TASK-003）

**目标**：仓库根识别 + 末层目录名 peer 派生实现完成，单测契约重写并通过
**验收标准**：

- [ ] `findWorkspaceRepoRoot` / `deriveWorkspacePeerId` 按 design C1 实现，`resolveEffectivePeerId` 逐字未变
- [ ] 16 个单测场景全绿，新增逻辑分支覆盖率 ≥ 80%
- [ ] `node --check` 与 `npm run check`（含 PLUGIN_VERSION 一致）无告警

### 里程碑2: 生成物与自动化回归（TASK-004 ~ TASK-005）

**目标**：7 个副本同步且无越界漂移，CI 等价测试清单全绿
**验收标准**：

- [ ] `sync.test.mjs` 判定已同步
- [ ] `git status` 变更文件仅限：源 + `workspace-peer.test.mjs` + 7 个 `workspace-peer.mjs` 副本（文档任务另计）
- [ ] `pr.yml` 记忆插件测试清单（shared/* + dsh-memory-plugin/* + opencode + pi + agent-plugins）全绿

### 里程碑3: 人工测试支持与文档同步（TASK-006 ~ TASK-010）

**目标**：夹具可一键重建，人工三测有明确命令与判据；8 处文档口径统一
**验收标准**：

- [ ] 夹具脚本执行后 `/tmp/ovpeer` 结构与设计一致，可重复执行幂等
- [ ] TC-01~TC-12 每项都有"执行命令 + 预期判据"
- [ ] 旧示例字符串在仓库内 `grep` 无残留

### 里程碑4: 收口（TASK-011 ~ TASK-012）

**目标**：变更说明与回滚止血可交付，知识完成去重沉淀
**验收标准**：

- [ ] 发布说明含 R-1（历史 peer 数据不可见）与 R-7（clone 目录名需一致）明示 + `OPENVIKING_PEER_ID` 止血步骤
- [ ] 知识沉淀给出"写入/不写入"结论与理由

## 测试策略→任务映射表

| design 测试项 | 类型 | 对应 TASK 编号 | 状态 |
|---|---|---|---|
| UT: testFindWorkspaceRepoRoot_gitDirectoryMarker | 单元测试 | TASK-002 | ✓ |
| UT: testFindWorkspaceRepoRoot_gitFileMarkerForWorktree | 单元测试 | TASK-002 | ✓ |
| UT: testFindWorkspaceRepoRoot_nestedGitTakesNearest | 单元测试 | TASK-002 | ✓ |
| UT: testFindWorkspaceRepoRoot_svn17SingleMarker | 单元测试 | TASK-002 | ✓ |
| UT: testFindWorkspaceRepoRoot_svn16TakesOutermost | 单元测试 | TASK-002 | ✓ |
| UT: testFindWorkspaceRepoRoot_gitPreferredOverSvn | 单元测试 | TASK-002 | ✓ |
| UT: testFindWorkspaceRepoRoot_noMarkerReturnsEmpty | 单元测试 | TASK-002 | ✓ |
| UT: testDeriveWorkspacePeerId_sameRepoNameAcrossPrefixes | 单元测试 | TASK-002 | ✓ |
| UT: testDeriveWorkspacePeerId_sanitizesNonAlnum | 单元测试 | TASK-002 | ✓ |
| UT: testDeriveWorkspacePeerId_nonAsciiKeepsServerCharset | 单元测试 | TASK-002 | ✓ |
| UT: testDeriveWorkspacePeerId_fallsBackToCwdBasename | 单元测试 | TASK-002 | ✓ |
| UT: testDeriveWorkspacePeerId_rootAndBlankReturnEmpty | 单元测试 | TASK-002 | ✓ |
| UT: testDeriveWorkspacePeerId_neverThrowsOnUnreachablePath | 单元测试 | TASK-002 | ✓ |
| UT: testResolveEffectivePeerId_prefersExplicitInsideRepo | 单元测试 | TASK-002 | ✓ |
| UT: testResolveEffectivePeerId_workspaceUsesRepoName | 单元测试 | TASK-002 | ✓ |
| UT: testResolveEffectivePeerId_disabledReturnsNone | 单元测试 | TASK-002 | ✓ |
| 测试数据生成（`/tmp/ovpeer` 目录夹具） | 测试数据 | TASK-006 | ✓ |
| TC-01 在 git 仓根启动 DSH 会话 | 人工集成 | TASK-007 | ✓ |
| TC-02 团队共享验证（核心目标） | 人工集成 | TASK-007 | ✓ |
| TC-03 嵌套仓库 | 人工集成 | TASK-007 | ✓ |
| TC-04 svn 工作副本 | 人工集成 | TASK-007 | ✓ |
| TC-05 显式 peer 优先 | 人工集成 | TASK-007 | ✓ |
| TC-06 关闭派生 | 人工集成 | TASK-007 | ✓ |
| TC-07 非仓库目录 | 人工集成 | TASK-007 | ✓ |
| TC-12 无 git/svn 可执行文件环境 | 人工集成 | TASK-007 | ✓ |
| TC-08 派生开销 1000 次计时 | 人工性能 | TASK-008 | ✓ |
| TC-09 冷启动不阻塞 | 人工性能 | TASK-008 | ✓ |
| TC-10 历史数据可见性 | 人工回归 | TASK-009 | ✓ |
| TC-11 其他 6 个 harness 各 1 次会话 | 人工回归 | TASK-009 | ✓ |
| 影响范围 #1–#9（回归检查单） | 人工回归 | TASK-009 | ✓ |
| 副本同步校验（sync 不越界） | 集成校验 | TASK-004 | ✓ |
| CI 等价测试清单全绿 | 自动化回归 | TASK-005 | ✓ |
| 8 处文档口径无残留 | 文档验证 | TASK-010 | ✓ |
| 语法/版本一致性检查 | 编译校验 | TASK-003 | ✓ |

映射表无 ❌ 缺失条目。

---

## 详细任务列表

### 基础任务类别

#### TASK-001: 重写 shared 源 peer 派生逻辑

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: 无
- **预计时间**: 1小时
- **负责人**: AI 助手

**任务描述**：
按 design C1 重写 `examples/memory-plugin-shared/lib/workspace-peer.mjs`：新增 `findWorkspaceRepoRoot`（向上探测 `.git`/`.svn`，git 最近、SVN 最外层、同级 git 优先）与私有 `sanitizePeerSegment`，`deriveWorkspacePeerId` 改为"仓库根（或 cwd）末层目录名净化"，`resolveEffectivePeerId` 保持逐字不变。

**实现要点**：

- 只引入 `node:fs` 的 `existsSync` 与 `node:path` 的 `basename/dirname/join/parse/resolve`
- 空串/`null`/纯空白 cwd 一律返回 `""`（走 `source: "none"`）
- 注释只描述事实语义（为何 git 取最近、SVN 取最外层、为何必须净化），不含需求/任务编号
- 命名遵循 `languages/web-hs/javascript.md`：`const`/驼峰、常量全大写下划线（`GIT_MARKER`/`SVN_MARKER`）

**验收标准**：

- [ ] 文件内容与 design C1「完整新实现」一致，无额外开关、无 memo、无子进程
- [ ] `resolveEffectivePeerId` 函数体与改造前逐字节相同
- [ ] 手工验证：在 `example-repo` 仓根调用得 `example-repo`，在 `example-repo/dsh/OpenViking/examples` 得 `OpenViking`

**相关文件**：

- `examples/memory-plugin-shared/lib/workspace-peer.mjs`

**注意事项**：

- 这是本次唯一的**手写**代码文件；7 个副本一律由 TASK-004 生成，禁止手改

---

#### TASK-002: 重写 peer 派生单元测试契约

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-001
- **预计时间**: 1.5小时
- **负责人**: AI 助手

**任务描述**：
重写 `examples/memory-plugin-shared/workspace-peer.test.mjs`：删除"整条路径净化"旧断言，改为临时目录夹具驱动的设计文档 16 个场景。

**实现要点**：

- 夹具基址 `mkdtempSync(join(tmpdir(), "ov-peer-"))`，`try/finally rmSync({recursive:true, force:true})` 清理
- `.git` 同时构造**目录**与**文件**两种形态；SVN 构造 1.7（仅根）与 1.6（每层）两种
- 等值断言前先探测 fixture 基址向上是否意外命中 marker：命中则降级为"仅断言字符集不变量"，避免 macOS/Linux/CI 差异导致偶发失败（不得用跳过测试规避问题，此处是断言强度自适应，测试仍然执行）
- 覆盖 `deriveWorkspacePeerId("/") === ""`、含 NUL 字节路径 `doesNotThrow`
- 保留并改造 `resolveEffectivePeerId` 三条（explicit / workspace=仓库名 / 关闭→none）

**验收标准**：

- [ ] 16 个场景全部落地且 `node --test examples/memory-plugin-shared/workspace-peer.test.mjs` 通过
- [ ] `node --test --experimental-test-coverage` 显示 `workspace-peer.mjs` 行/分支覆盖率 ≥ 80%
- [ ] 测试不依赖网络、不依赖 `git`/`svn` 可执行文件、不依赖真实家目录

**相关文件**：

- `examples/memory-plugin-shared/workspace-peer.test.mjs`

---

#### TASK-003: 语法编译与版本一致性校验

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-001, TASK-002
- **预计时间**: 0.2小时
- **负责人**: AI 助手

**任务描述**：
执行编码后的静态校验（Node 侧等价于"编译"门禁），确保后续数据生成与回归在可加载代码上进行。

**实现要点**：

- `node --check` 源文件与测试文件
- `examples/dsh-memory-plugin` 内 `npm run check`（遍历 `*.mjs shared/*.mjs` 语法 + `check:version` 的 `PLUGIN_VERSION` 与 `package.json` 一致性）
- 全部命令绑定 `NODE_PATH=/Users/alice/.nvm/versions/node/v23.11.0/bin/node`，日志落 `/tmp/ov-peer-check.log` 后过滤

**验收标准**：

- [ ] 无任何 `SyntaxError`；`check:version` 通过
- [ ] 失败时从 `/tmp/ov-peer-check.log` 提取完整错误，不允许仅凭截断输出重复排查

**相关文件**：

- `examples/dsh-memory-plugin/package.json`（只读，不改）

---

### 集成任务类别

#### TASK-004: 同步 7 个生成副本并核对越界漂移

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-001
- **预计时间**: 0.5小时
- **负责人**: AI 助手

**任务描述**：
运行 `sync.mjs` 使 7 个 target 的 `workspace-peer.mjs` 副本反映新源，并确认本次同步未顺带改动其他文件。

**实现要点**：

- 命令：`node examples/memory-plugin-shared/sync.mjs 2>&1 | tee /tmp/ov-peer-sync.log`
- 同步后 `git status --porcelain` 与 `git diff --stat` 逐文件核对
- 允许变更：`examples/memory-plugin-shared/lib/workspace-peer.mjs`、7 个 `workspace-peer.mjs` 副本、（TASK-002/010 范围内的测试与文档）
- **停止条件**：若 `skills/`、其他 `*.mjs` 副本出现 diff，说明副本本就漂移 → 停止并上报，不擅自提交或覆盖

**验收标准**：

- [ ] 7 个副本首行仍为 GENERATED banner，正文与源一致
- [ ] `node --test examples/memory-plugin-shared/sync.test.mjs` 通过
- [ ] 无越界文件变更

**相关文件**：

- `examples/claude-code-memory-plugin/scripts/shared/workspace-peer.mjs`
- `examples/codex-memory-plugin/scripts/shared/workspace-peer.mjs`
- `examples/opencode-plugin/lib/shared/workspace-peer.mjs`
- `examples/dsh-memory-plugin/shared/workspace-peer.mjs`
- `examples/pi-coding-agent-extension/shared/workspace-peer.mjs`
- `examples/zcode-memory-plugin/scripts/shared/workspace-peer.mjs`
- `agent-plugins/servers/shared/workspace-peer.mjs`

---

### 测试任务类别

#### TASK-005: CI 等价自动化回归

- **状态**: 待定 ⏳
- **优先级**: 高 🔴
- **依赖关系**: TASK-003, TASK-004
- **预计时间**: 0.5小时
- **负责人**: AI 助手

**任务描述**：
在本地复刻 `.github/workflows/pr.yml` 的记忆插件测试清单，作为全消费方一致性（FR-009）的自动化证据。

**实现要点**：

- 主清单（`pr.yml:35-52`）：`memory-plugin-shared/*.test.mjs` + `examples/dsh-memory-plugin/*.test.mjs` + `opencode-plugin/tests/*.test.mjs` + `opencode-plugin/servers/mcp-proxy.test.mjs` + `pi-coding-agent-extension/tests/*.test.mjs` + `agent-plugins/plugin.test.mjs`
- 插件清单（`pr.yml:36-58`）：codex / claude-code / zcode / cursor 各测试文件
- 前置：`npm ci --prefix examples/dsh-memory-plugin`（依赖已在本地则跳过并说明）
- 日志落 `/tmp/ov-peer-test.log`，失败时 `grep -A5 "not ok"` 定位
- **禁止**通过删/禁用测试让绿灯；断言与实现不一致时按 requirements 决策修实现

**验收标准**：

- [ ] 全清单 `pass N / fail 0`
- [ ] 唯一被修改断言的测试文件是 `workspace-peer.test.mjs`（其余文件断言不改即通过）

**相关文件**：

- `.github/workflows/pr.yml`（只读基准）

---

#### TASK-006: 生成人工三测目录夹具

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-001
- **预计时间**: 0.3小时
- **负责人**: AI 助手

**任务描述**：
产出可重复执行的夹具脚本与判据脚本，供 TASK-007/008/009 人工环节使用（本需求无数据库，database-skill 不适用）。

**实现要点**：

- 脚本 `/tmp/ov-peer-fixtures.sh`：幂等创建 `plain/deep`、`repo-git/.git/`、`repo-git-wt/.git`(文件)、`repo-svn17/.svn`、`repo-svn16/{.svn,sub/.svn}`、`nested/outer/.git` + `nested/outer/inner/.git`、含空格与点的目录名、非 ASCII 目录名
- 脚本 `/tmp/ov-peer-peer.sh <cwd>`：加载改造后的源并打印 `peerId` 与 `source`
- 夹具与判据脚本只写 `/tmp`，不进仓库

**验收标准**：

- [ ] 连续执行两次无报错（幂等）
- [ ] 对 `repo-git`、`repo-svn16/sub`、`nested/outer/inner` 三个输入打印的 peer 分别为 `repo-git`、`repo-svn16`、`inner`

**相关文件**：

- `/tmp/ov-peer-fixtures.sh`、`/tmp/ov-peer-peer.sh`（临时，不纳入版本库）

---

#### TASK-007: 人工集成测试支持（TC-01 ~ TC-07、TC-12）

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-005, TASK-006
- **预计时间**: 1小时（人工执行）
- **负责人**: 用户执行，AI 提供命令与判据并回收结论

**任务描述**：
在真实 harness 会话中验证 peer 取值正确性与"团队共享"这一核心目标达成。

**实现要点**：

- 生效前提：以改造后的 checkout 装载插件（本机安装态 `@openviking/dsh-memory-plugin@0.2.1` 需更新或本地链接后**重启进程 + 新开会话**）
- TC-01/TC-02：分别在两个不同前缀的同名 git 仓（`example-repo` 与 `/tmp/u2/example-repo`）起会话并触发 capture
  - **即时判据（以此为准）**：两条会话的 `user/default/sessions/<ov会话id>/messages.jsonl` 中每条消息的 `peer_id` 均为 `example-repo`
  - **延迟判据（可选，不得据此判定失败）**：`user/default/peers/example-repo/` 仅在"该会话被 commit 且服务端提取出归属该 peer 的记忆"之后才创建；未出现不等于派生失败（服务端归属路由见 `skills/aegis-skill/knowledge/openviking-memory-plugin.md` 第 2 节第 5 条）
  - **必须用重启后新建的会话验证**：升级前创建、升级后复用的长会话，其归档批次含旧 peer 消息，后续 commit 仍可能写旧 peer
- TC-03：在 `example-repo/dsh/OpenViking` 起会话 → peer `OpenViking`
- TC-04：真实 svn WC（或 TASK-006 伪造 WC）→ peer 为 WC 根目录名
- TC-05：`OPENVIKING_PEER_ID=myteam` → peer 为 `myteam`（派生不生效）
- TC-06：`OPENVIKING_WORKSPACE_PEER=0` → 无 peer，行为与改造前一致
- TC-07：`cd /tmp/ovpeer/plain/deep` → peer `deep`
- TC-12：在无 `git`/`svn` 可执行文件的受限环境起会话 → 仍正常派生（证明未回退到子进程方案）

**验收标准**：

- [ ] 上述 8 项逐项有实测值记录，无一项以"推断"代替观测
- [ ] TC-02 出现"两个不同 peer"时判定不通过，须回到 TASK-001 排查而非放宽判据

**相关文件**：

- `examples/dsh-memory-plugin/README.md`（判据口径参照）

---

#### TASK-008: 人工性能测试支持（TC-08、TC-09）

- **状态**: 待定 ⏳
- **优先级**: 低 🟢
- **依赖关系**: TASK-006
- **预计时间**: 0.3小时（人工执行）
- **负责人**: 用户执行，AI 提供计时脚本与阈值

**任务描述**：
验证 fs 向上探测不引入可感知开销（NFR-001），且未造成 fd/内存泄漏。

**实现要点**：

- TC-08 脚本：对 8 层深路径循环 1000 次 `deriveWorkspacePeerId` 并输出均值；同时以 `lsof -p <pid>` 比较首尾 fd 数
- TC-09：在 10+ 级深层目录启动插件，记录首条 turn 完成时间，与改造前基线对比
- 阈值：单次派生均值 < 1ms；冷启动差异 < 50ms；fd 数量不随调用增长

**验收标准**：

- [ ] 有实测数字（不是"应该没问题"）
- [ ] 超阈值时提交 profile 数据，回到设计层评估是否引入 memo（不擅自降标）

**相关文件**：

- `/tmp/ov-peer-peer.sh`（TASK-006 产物）

---

#### TASK-009: 人工回归测试支持（TC-10、TC-11 + 影响范围 #1–#9）

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-005, TASK-006
- **预计时间**: 0.5小时（人工执行）
- **负责人**: 用户执行，AI 提供检查单

**任务描述**：
按 design《测试策略-影响范围》9 个功能点逐项确认，覆盖"值变更"与"不应变化"两类。

**实现要点**：

- #1 capture/commit 的 `peer_id`；#2 自动召回命中集合；#3 profile 注入；#4 MCP 代理 boot peer（README:88 已声明为进程级，属既有限制，不在本次修复）
- #5 其他 6 个 harness（claude-code/codex/opencode/pi/zcode/agent-plugins）各起 1 次会话
- #6 显式 peer 部署、#7 关闭派生 —— 二者必须与改造前行为一致
- #8 doctor 诊断输出（`ov-memory-doctor.mjs:370/324`）
- TC-10 历史数据可见性：确认"旧 peer 数据不再自动命中"，并以 `OPENVIKING_RECALL_PEER_SCOPE=all` 验证跨 peer 召回路径可用
- TC-11 其他 harness 无报错

**验收标准**：

- [ ] 9 个影响点逐项标注 通过/不通过/不适用（含原因）
- [ ] #6、#7 若出现行为变化，视为回归缺陷阻断发布

**相关文件**：

- `examples/claude-code-memory-plugin/skills/ov-memory-doctor/reference.md`

---

### 文档任务类别

#### TASK-010: 同步 8 处文档口径

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-001
- **预计时间**: 0.8小时
- **负责人**: AI 助手

**任务描述**：
把所有"路径逐字符净化"旧口径改写为"仓库根末层目录名"新口径（design C3 表逐条执行）。

**实现要点**：

- 官方文档双语各 1 处：`docs/zh/...16-capability-reference.md:208`、`docs/en/...:206`，保留"服务端对含 `/`、`\` 返回 400"的既有说明
- `examples/memory-plugin-shared/README.md:22-25` 补三条语义（仓库根末层名 / SVN1.6 取最外层 / 嵌套取内层）
- 插件 README：claude-code:143、codex（同段）、opencode:154、pi:91 与 119 表格行、dsh:124
- `claude-code-memory-plugin/skills/ov-memory-doctor/reference.md:34` 示例改新口径
- 明确写出两条运维提示：① clone 目录名需团队一致（R-7）；② 切换后旧 peer 数据不再自动命中（R-1）

**验收标准**：

- [ ] 检索旧示例串在仓库内无残留
- [ ] 中英两份描述语义一致，未遗漏 400 校验说明
- [ ] 只改 peer 命名相关句子，不顺手改相邻内容（Surgical 约束）

**相关文件**：

- 上述 8 个文档路径

---

#### TASK-011: 变更说明与回滚指引落盘

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-010
- **预计时间**: 0.3小时
- **负责人**: AI 助手

**任务描述**：
产出面向团队/发布方的变更说明，让 peer 语义变化的影响可被知情处置。

**实现要点**：

- 变更点、变更前后取值对照表（design API 节）
- 必须明示：历史 peer 数据可见性（R-1）、同名目录碰撞（R-4）、嵌套仓库分裂（R-5）、clone 目录名要求（R-7）、人际隔离能力变化（安全设计节）
- 回滚四步（design 回滚方案），其中第 4 步"设置 `OPENVIKING_PEER_ID=<旧路径净化值>`"作为无需回滚代码的止血手段优先推荐

**验收标准**：

- [ ] 说明中每条风险都有对应处置动作，无"只列风险不给办法"
- [ ] 落点为 `spec/workspace-repo-peer/change-note.md`（不污染上游 README 结构）

**相关文件**：

- `spec/workspace-repo-peer/change-note.md`（新建）

---

#### TASK-012: 知识沉淀去重判断

- **状态**: 待定 ⏳
- **优先级**: 中 🟡
- **依赖关系**: TASK-001, TASK-010
- **预计时间**: 0.3小时
- **负责人**: AI 助手

**任务描述**：
按全局规则触发 `knowledge-update-skill`，对本轮形成的私有域知识做去重判断并按需沉淀。

**实现要点**：

- 候选知识点：① OpenViking `peer_id` 服务端字符集白名单与 header 400 约束；② `peers/<peer_id>` 命名空间归属与团队共享前提（同账号）；③ memory-plugin 生成物必须经 `sync.mjs` 的约束；④ 0.2.1 运行态 uri-guard 误拦 `write` 正文这一已知缺陷
- 先查 `skills/aegis-skill/knowledge/`（当前索引无 dsh-memory-plugin / openviking 条目）与 OpenViking 实体记忆，判断"新增/合并到已有实体记忆/不沉淀"
- 不写入具体实现写法，只沉淀可指导后续开发的稳定语义与契约

**验收标准**：

- [ ] 输出逐条"沉淀/合并/不沉淀"结论及理由
- [ ] 若判定全部无需沉淀，明确回复"未发现需要沉淀的新增知识"及原因（规则要求）

**相关文件**：

- `skills/aegis-skill/knowledge/index.md`（只读，判定后按需写入）

## 测试汇总索引

| 统一编号 | 测试类型 | 测试场景 | 依赖任务 | 状态 |
|----------|----------|------------|----------|------|
| TASK-002 | 单元测试 | workspace-peer 16 场景 | TASK-001 | 待定 |
| TASK-003 | 编译校验 | 语法 + 版本一致 | TASK-001, TASK-002 | 待定 |
| TASK-005 | 自动化回归 | CI 等价清单（含 sync.test） | TASK-003, TASK-004 | 待定 |
| TASK-006 | 测试数据 | `/tmp/ovpeer` 夹具 | TASK-001 | 待定 |
| TASK-007 | 人工集成 | TC-01~07、TC-12 | TASK-005, TASK-006 | 待定（人工） |
| TASK-008 | 人工性能 | TC-08、TC-09 | TASK-006 | 待定（人工） |
| TASK-009 | 人工回归 | TC-10、TC-11 + 影响范围 #1–#9 | TASK-005, TASK-006 | 待定（人工） |

## 任务依赖关系图

```
TASK-001 (源实现)
  ├─→ TASK-002 (单测) ─→ TASK-003 (编译校验) ─┐
  ├─→ TASK-004 (sync 7 副本) ──────────────────┴─→ TASK-005 (CI 等价回归) ─┐
  ├─→ TASK-006 (夹具脚本) ───────────────────────────────────────────────┼─→ TASK-007 (人工集成)
  └─→ TASK-010 (8 处文档) ─→ TASK-011 (变更说明)                          ├─→ TASK-008 (人工性能)
                        TASK-012 (知识沉淀) ← TASK-001+TASK-010           └─→ TASK-009 (人工回归)
```

**关键路径**：TASK-001 → TASK-002 → TASK-003 → TASK-004 → TASK-005（全自动）
**可并行**：TASK-004 与 TASK-010；TASK-006 与 TASK-002
**外部依赖**：TASK-007/008/009 需用户执行（真实 harness 会话与安装态插件更新）

## 风险识别和应对

### 技术风险

| 风险项 | 影响任务 | 概率 | 影响 | 应对措施 |
|---|---|---|---|---|
| sync 顺带产生无关 diff（副本本就漂移） | TASK-004 | 中 | 中 | 白名单核对，异常即停止上报，不擅自提交 |
| 其他 harness 存在未取证的旧 peer 断言 | TASK-005 | 低 | 中 | 全量跑 CI 清单；失败按根因修实现或修断言，禁止禁用测试 |
| 测试机 TMPDIR 位于某仓库内导致夹具误判 | TASK-002 | 低 | 中 | 断言强度自适应（见 TASK-002 要点），不跳过测试 |
| 真实会话验证受阻于安装态 0.2.1 | TASK-007 | 高 | 低 | 标注为"人工/需授权升级"，不阻塞自动化任务收口 |

### 进度风险

| 风险项 | 影响 | 应对措施 |
|---|---|---|
| 人工三测排期不可控 | 里程碑3 延后 | 自动化收口先行完成，人工项以清单交付 |
| 文档改动面（8 处）超预期扩散 | TASK-010 超时 | 严格限定只改 peer 命名句，其余不动 |

## 质量控制

### 代码质量标准

- **测试覆盖率**: 单元测试新增逻辑 ≥ 80%（`--experimental-test-coverage` 实测）
- **静态检查**: `node --check` 全量、`npm run check`（含版本一致）
- **一致性**: `sync.test.mjs` 保证源与副本无漂移
- **文档同步**: 代码变更同步更新 8 处口径（TASK-010）

### 交付标准

- [ ] TASK-001~006 全部完成且自动化测试全绿
- [ ] TASK-010、TASK-011 文档收口
- [ ] TASK-012 给出知识沉淀结论
- [ ] TASK-007~009 的人工测试清单已交付（执行结论由用户回收后登记）

## 变更管理

### 变更记录

| 日期 | 变更任务 | 变更原因 | 影响评估 | 变更人 |
|---|---|---|---|---|
| 2026-09-02 | 初始版本（TASK-001~012） | Phase 3 拆解产出 | — | AI 助手 |
| 2026-09-03 | TASK-007 v1.1：TC-01/TC-02 判据精确化 | 原判据"到服务端确认 `peers/example-repo`"不可操作——`peers/<peer>/` 只在归属型记忆被提取后才创建，据此会误判为改造失败 | 改为 `messages.jsonl` 的 `peer_id` 即时判据 + `peers/` 延迟判据 + 必须用新建会话验证 | AI 助手 |
