# 资源置信度：测试夹具与人工验证包

本目录服务于 `tasks.md` 中 TASK-018 ~ TASK-032（测试数据、人工集成测试、人工性能测试、人工回归测试）。

## 目录内容

| 文件 | 用途 | 对应用例 |
|------|------|----------|
| `generate_fixtures.py` | 生成全部源文件夹具与定点数据 | TASK-018 |
| `capture_baseline.py` | 从改造前 revision 捕获排序基线并逐条比对 | TC-31（NFR-001 零回归的唯一对照手段） |
| `data/`（由脚本生成） | `conf-high/`、`conf-low/`、`granularity-a/`、`granularity-b/`、`conf-high-group/`、`manifest-min.json`、`fixed-score-pairs.json`、`dirty-records.json` | TC-01~13、TC-41 |

## 使用方式

### 1. 生成夹具

```bash
cd prds/OpenViking
python spec/resource-confidence/test-fixtures/generate_fixtures.py
```

幂等，可重复执行。

### 2. 捕获改造前基线（**必须在改代码之前执行**）

`TC-31` 要证明"未标注记录的 `raw_score` 与改造前的 `score` 逐位一致、顺序一致"。
这需要一份改造前的排序快照：

```bash
python spec/resource-confidence/test-fixtures/capture_baseline.py \
  --repo prds/OpenViking \
  --queries queries.json \
  --baseline-rev <改造前的 commit>
```

脚本会：

1. 用 `git worktree add --detach` 检出 `--baseline-rev`；
2. 在 worktree 与本工作树各跑一遍相同查询，分别写出 `baseline-before.json`、`baseline-after.json`；
3. 逐查询逐条比对，任一差异即以非 0 退出码失败。

> `capture_baseline.py` 内嵌的采集片段需要接到项目实际的检索入口。
> `HierarchicalRetriever` 没有 `from_config()`，脚本会在检测到该情况时**明确报错而不是静默产出空基线**，
> 届时请按 `design.md` C10 的入口（`openviking/storage/viking_fs/_semantic.py:256` 的 `find`
> 与 `:399` 的 `search`）补齐采集代码。

### 3. 定点分数数据

`fixed-score-pairs.json` 记录了 5 组**必须可复现**的成对分数：

| id | 用例 | 未加权分 / 置信度 | 期望顺序 |
|----|------|-------------------|----------|
| `user-sample-1` | TC-09 | X(0.90, 0.5) vs Y(0.46, 1.0) | X → Y |
| `user-sample-2` | TC-10 | P(0.50, 0.5) vs Q(0.46, 1.0) | Q → P |
| `boundary-inside` | TC-11 | A1(0.50, 0.0) vs B1(0.405, 1.0) | B1 → A1（19% < 20%，换位） |
| `boundary-outside` | TC-12 | A2(0.50, 0.0) vs B2(0.395, 1.0) | A2 → B2（21% ≥ 20%，不换位） |
| `threshold-split` | TC-13 | A3(0.42, 0.0)、B3(0.21, 1.0)，门槛 0.35 | A3 保留（加权 0.336 < 0.35，仍返回） |

写入方式：直接向向量集合写入固定 `_final_score` 的记录（定点数据必须绕过排序逻辑注入，
否则无法复现指定的未加权分）。`dirty-records.json` 中的越界值同样必须**绕过写侧校验**直接写库，
用于验证读侧 clamp（TC-35）。

### 4. 规模数据

| 用例 | 规模 | 生成方式 |
|------|------|----------|
| TC-29 | 10 万条记录集合 | 复用项目既有的批量导入通道，或直接批量 upsert |
| TC-30 | 1000 个 10KB 文件 | `for i in $(seq 1 1000); do head -c 10240 /dev/urandom \| base64 > f$i.md; done` |
| TC-18 / TC-19 | 20+ 条高低置信混合集合 | 用 `conf-high/` 与 `conf-low/` 多次导入到同一 root，并混入 `--confidence 0.0 / 0.5 / 1.0` |
| TC-17 | skill 数据 | `ov skills add` |
| TC-25 | ovpack 包 | `ov export` |
| TC-27 / TC-28 | 旧 schema 集合 | 用一个不含 `confidence` 字段的集合（旧版本创建，或手工删除该字段的集合元数据） |
| TC-32 | 启用 rerank 的配置 | 使 `search` 走 `THINKING` |
| TC-34 | `retrieval.hotness_alpha = 0.2` | 验证门槛仍按 hotness 混合前的 `_final_score` |

## 产物落盘约定

人工三测的执行证据（命令行、stdout/stderr 摘录、实测数值、对照数据表、未通过项现象）
统一记录到 `spec/resource-confidence/test-reports/TASK-0XX.md`。
