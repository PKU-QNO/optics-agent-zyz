---
name: transition-wrapup
description: 过渡期会话收尾 skill——整理 memento/MEMORY/rules 三载体，按四边界判定准则判体，产出项目级与全局 AGENTS/rules 修改建议、给用户的建议清单。由用户手动 /transition-wrapup 加载。
invoke: user
---

# transition-wrapup — 过渡期会话收尾

> **用途**：z-memory hard gate 上线前的过渡期收尾机制。z-memory 落地周期长，过渡期（memento + 原生 MEMORY + 原生 rules 系统）会长期甚至长期持续。本 skill 在会话结束前或用户手动调用时系统化整理三大载体，并产出需用户拍板的修改建议。
> **铁律**：不自行落盘任何 AGENTS/skill/rules 实质改动（过渡期 human gate）——只整理 + 提议，落盘需用户口头批准。第一轮整理后由内置子 agent 对抗审过才长期可靠使用。
>
> **术语约定（防歧义，全文禁用裸"memory"指代）**：
> - **memento** = memento-mcp 记忆后端（`memory_store`/`decisions_log`/`pitfalls_log`/`memory_search`）
> - **MEMORY.md** = 项目根的纯索引**头文件**（单文件，恢复上下文用）
> - **memory/** = 项目根下的**五件套正文目录**（`findings.md`/`lessons.md`/`tasks/`/`worklog/`/`archived-tasks/`/`findings-unverified.md`/`behavior-rules.md`）
> - "在 memory 里建 task" 指建 `memory/tasks/<name>.md` 文件 + 在 MEMORY.md 头部加 task 索引行；**不是** memento 的 `memory_store`。遇用户说"memory"先按本约定消歧，含糊则反问确认。

## 0. 边界判定准则（执行前必读，按此判体不凭直觉）

本准则是可执行铁律，agent 执行步骤时遇到"这算什么"一律回此章查表，不得主观判定。

### 0.1 新任务 vs 子任务

| 判据 | 新任务 | 子任务 |
|------|--------|--------|
| quest 归属 | 独立的 `quest-N`（本源追求之一） | 推进已有 quest 的局部步骤 |
| 独立恢复价值 | 脱离本会话恢复时**能独立成立**为一个待办 | 不能独立成立，仅为某 active/dormant task 服务，任务做完它就没了 |
| plan 完整性 | 各自完整（自己有下一步 + 用户决策项） | 是父 task 的 plan_agent 一部分 |
| 阻塞解除后 | 成为独立 active 任务 | 跟随父 task 状态变化 |

**判定铁律**：「**脱离本会话恢复时，这一项能否独立成立为一个待办？**」能 → 新任务（开新 `task-*` 块）；不能 → 子任务（并入相关 task 块的 plan_agent 或 plan_user）。

### 0.2 任务归档

**归档触发（两条之一满足即归档）**：
- **自然完成**：task 的 plan_agent 全部执行完、无 blockers、无 dormant 等待项。
- **30 天未跟进**：`state=active` 的 task，最近跟进时间距今 ≥30 天 且 用户未指定继续 → 归档（用户随时也可主动提出归档）。

**归档操作**：
1. 任务正文移到 MEMORY 附属文件夹：`memory/archived-tasks/<task-name>-<archived-date>.md`（搬该 task 的 urgent/general/plan_*/finding/blockers 全文）。
2. MEMORY.md 留归档索引：`tasks` 分区下加 `task-archived:<name>` 一行，含 `archived_at:` + `location: memory/archived-tasks/xxx.md` + 一句话摘要。
3. 不归档情况：任务暂无进展但 <30 天 且 未完成 且无用户归档指令 → 保留 `task-dormant`，等下次恢复。**dormant 不自动归档**，仅在 ≥30 天或用户指令时归档。

### 0.3 memento / MEMORY / 申请进 AGENTS 的载体边界

| 什么 | 走哪 | 判据 |
|------|------|------|
| 跨会话长期治理的结构化事实/证据/决策/坑 | **memento** | 需语义搜索召回、需 provenance 五要素、需 importance 分层、需 link 谱系、需 `decisions_log`/`pitfalls_log` 结构化 |
| 当前在哪/当前要做什么/quest/多任务状态/已验证长期结论 | **MEMORY.md** | 短时效恢复上下文、高频每次注入、覆盖式更新不累积、纯文本人类可读可改 |
| 路径局部成立（仅某些文件/目录）的稳定约定 | **`.claude/rules/` 带 paths**（申请） | 一条规则**只**在特定路径有意义，全局会污染 → path-scoped rule |
| 跨所有场景都成立的硬约定 | **skill/AGENTS**（申请） | 反复出现、用户多次纠正、跨项目跨场景稳定 → 全局权威 |

### 0.4 晋升三轴（申请进 rules/AGENTS 的硬门槛）

**稳定性 + 作用域 + 复现次数**三轴同时判定：

| 档位 | 稳定性 | 作用域 | 复现 | 落点 | 批准 |
|------|--------|--------|------|------|------|
| 全局权威（最高） | 用户拍板或≥2次会话纠正 | 跨所有场景 | ≥2 次会话 | skill / AGENTS | 用户口头 + 全局AGENTS保证7路径硬链接同步 |
| 路径局部（中） | 稳定 | 仅特定路径 | 在该路径下≥2 次会话重复 | `.claude/rules/<name>.md` 带 paths | 用户批准 |
| 不晋升（留原地） | 单次偶发或仅本会话 | — | 不足2次 | MEMORY（短期）或 memento（若需召回） | 无 |

**进 AGENTS 额外门槛**（最高档）：必须跨所有场景稳定成立 + 用户口头批准 + 全局 AGENTS 改动用 `cat >>` in-place 保 7 路径硬链接 inode（禁 Edit/apply_patch 换 inode），改完验 `stat -c '%i %h %n'` 七处 links=7。
**进 rules 门槛**（中档）：仅特定路径成立 + 该路径下重复出现 + 用户批准。
**未稳定猜测**：memento type=hypothesis + MEMORY 头部标 finding-unverified，不晋升。

## 1. 何时用

- 用户 `/transition-wrapup` 主动调用
- 会话有实质产出（完成任务/决策/踩坑）且即将结束
- compact 前、SessionEnd 前

## 2. 执行步骤

### 2.1 整理 memento（跨会话长期治理）

- 先 `memory_search` 查重本会话待沉淀内容的相似记忆（查询词含任务名/子系统/关键对象）。
- 用 `memory_dedup_check`（阈值 0.85）对关键结论查重；命中即改 `memory_update`，不新建。
- 按 0.3 载体边界判 claim_type，路由到对应 memento 工具：
  - `decision` → `decisions_log store`
  - `user_preference` → `memory_store`（type=user-preference）
  - `lesson_learned` / `pitfall` → `pitfalls_log store`
  - `observed_fact` / `inference` → `memory_store`（type=fact；未稳定猜测标 hypothesis）
- 每条带 provenance 五要素：`source_artifact` / `evidence_type` / `timestamp_version` / `scope_applicability` / `confidence_result_class`；缺字段写 `unknown`/`pending` 不省略；相对日期转绝对。
- 结果状态一律 `result_class` 口径，禁把 surrogate_fallback/diagnostic_only/pipeline_completed 当实质完成。
- 重要决策/高频复发提议 `memory_pin`（不自行 pin，标在建议里）。
- 相关记忆用 `memory_link` 连边；决策被推翻走 `supersedes_id` 不删除。

### 2.2 整理 MEMORY.md（恢复上下文，短时态）

**覆盖式**更新项目根 `MEMORY.md` 的 `## 当前状态` 头部（不累积瞬时状态）：

**纯索引头**（v2：头部只放 quest+task简述+导航索引+路由表，正文全下沉 `memory/` 文件，禁把发现/行为规范嵌头）：

```
## 当前状态

### 本源追求 (quest-N, 长期少变)
- quest-1: ...
- quest-2: ...

### 活动任务 (每task 3行: 名+一句话目标+状态行; 按边界准则0.1判新任务vs子任务)
#### task-active: <名> — <目标> | state=active / priority / last_followed=<date> / blockers
#### task-dormant: <名> — <目标> | state=dormant / waiting_on=<等什么> / last_active_before_dormant=<date>
#### task-archived: <名> | archived_at=<date> / location=memory/archived-tasks/<name>-<date>.md / summary

### 导航索引 (何时读什么; NOT 正文)
- 见任务正文+meta_trace → Read `memory/tasks/<name>.md`
- 见已验证结论 → Read `memory/findings.md` (## 已验证重要 / ## 已验证一般)
- 见未验证猜测 → Read `memory/findings-unverified.md` (90天清)
- 见踩坑教训 → Read `memory/lessons.md` (同步 see pitfalls_log:<id>)
- 见操作历史 → Read `memory/worklog/00-index.md` 入口,按需深读序号
- 跨会话语义召回 → memento `memory_search`/`decisions_log`/`pitfalls_log`

### 路由表 (场景信号 → 读什么)
- 我现在在哪/当前做什么 → 看本头 task-active + 当前 cwd
- compact 后恢复 → 看本头 quest + task-active 的 blocker/priority
```

**纪律**：
- **MEMORY 头是索引不是正文**——发现/行为规范/文件规范**全下沉** `memory/findings.md`、`memory/behavior-rules.md`、task 的 file_* 字段；头部只放索引指针。头部多任务+多 finding 不得膨胀超 200 行/25KB（SessionEnd hook 自动检查）。
- 细节移同目录 topic 文件（`debugging.md` 等），头部精简。
- 短时态逐轮留痕（`session-history-N` / 瞬时 finding）**不进 MEMORY**——那是 meta_trace 的职责（避免与 meta_trace 职责重叠）。
- **归档操作**按 0.2：task 正文搬 `memory/archived-tasks/`，MEMORY 留 `task-archived` 索引指针。判 30 天未跟进时查各 task 的 `last_followed`。
- **三端兼容**：Claude 端原生 autoMemoryEnabled 自动注入头 200 行；OpenCode/Codex 端无原生注入，写完提醒下个会话主动 Read。

### 2.3 整理 rules（路径局部硬规则）

按 0.3 / 0.4 判：约定来自某文件/目录证据 → 适合 path-scoped rule；跨场景 → AGENTS/skill（不当 rule）；不稳定 → 留 memory。在建议里逐条标判据来源。

### 2.4 产出修改建议（提议，不自行落盘）

按过渡期 human gate，agent 不得自行改 AGENTS/skill/rules。本 step 只产出建议清单：

**a. 项目级 AGENTS/skill/rules 修改建议**
逐条列：文件路径 + 改动类型 + 理由 + 证据来源 + 晋升三轴判定结论。

**b. 全局 AGENTS/rules 修改建议**
影响跨项目的稳定改动，逐条列理由 + 证据 + 用户批准要求。全局 AGENTS 改动提醒 7 路径硬链接保 inode（`cat >>` in-place，禁 Edit/apply_patch，改完 `stat -c '%i %h %n'` 七处验 links=7）。

**c. 输出给用户的建议（统一格式）**
```
📣 收尾建议（等你拍板）：
[memento] <memory_id|新建> — <claim_type> — <理由>
[MEMORY] <覆盖头部 / 归档某task / 无需改> — <哪些 task/finding>
[rules] <新增 path-scoped / 不需要> — <path> — <约定>
[项目 AGENTS/skill] <改动/不需要> — <文件> — <改动>（需批准）
[全局 AGENTS] <改动/不需要> — <文件> — <改动>（需批准 + 硬链接同步）
```

**d. 批准后意图复述（防多轮误解往返）**
用户批准后、动手执行前，**必须先用一句话复述本次将执行的具体动作并按载体指明落点**，等用户确认或自行无歧义时再执行。复述模板：
```
你批准了，我将执行：
- memento：<memory_store 新建 X 条 / memory_update 更新 id=X / pitfalls_log 新建 Y 条>
- MEMORY.md：<覆盖头部索引 / 加 task 索引行 / 归档某task 留指针 — 不加正文>
- memory/ 目录：<建 tasks/<name>.md / findings.md 加 N 条 / 不动>
- AGENTS/skill/rules：<不动 / 等二次批准>
对吗？
```
执行与提议不一致时（如用户说"新建 task"指 `memory/tasks/` 但被误解成 memento `memory_store`），以本复述对齐——用户纠正即按纠正执行，不重复猜测。

## 3. 禁止行为

- ❌ 不自行 `git commit` / `git push`
- ❌ 不自行落盘 AGENTS/CLAUDE/SKILL/rules 实质改动（过渡期 human gate）
- ❌ 不改全局 AGENTS 时用换 inode 的编辑方式（会断 7 路径硬链接）
- ❌ 不写 secret/敏感路径（SSH key/PAT/.mcp.json 凭据）进任何载体
- ❌ 不主动 pin 记忆（标在建议里等批准）
- ❌ 不省略 provenance 字段（缺则写 unknown/pending）

## 4. 诚实口径

- 每条建议标 `result_class`（deliverable_completed / pipeline_completed / diagnostic_only / surrogate_fallback / not_run）。
- 区分"已整理"vs"已落盘"：扎实的整理 + 提议落盘 ≠ 已实施。
- 归档 30 天判定基于 task 的 `last_followed`，无该字段者不自动归档（标待补）。
- 用户口头批准后才落盘；批准后由调用方执行，本 skill 不在收尾轮次内完成落盘。