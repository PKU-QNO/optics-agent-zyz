# V3 上下文压缩交接笔记（2026-07-04）

> 用途：上下文即将压缩时，给后续 agent 快速恢复本轮讨论状态。本文只总结项目现状和新设计想法，不等同于已批准的落地方案。
> 置信边界：项目现状来自本仓库文档、memento 记忆和本轮只读核对；“新想法”主要来自用户与网页端模型闲聊文件 `D:/AGENT备份/模型介绍.md` 后半部分，属于设计假设，尚未经过 SEPR 真跑验证。

## 1. 当前项目定位

- `optics_agent` 是 **SEPR 的元设计工作区**，同时保留自身 COMSOL/Magnus runtime 工作。
- `self-evo-paper-repro` 是 **SEPR 执行工作区**，用于 Claude Code 以 `main-agent` / `evolution-agent` 身份跑论文复现和后期自迭代。
- 当前主路径不是自动 E-flow，而是人工预训练循环：

```text
optics_agent 设计框架
  -> SEPR 跑一篇论文复现
  -> 把真实运行经验回传给 optics_agent
  -> optics_agent 人工审查并改进 SEPR 设计
  -> 重跑验证
```

- 论文复现不是终点，而是 reusable scientific-computing blueprint、参数 sweep、case/DSL 和新科学探索的回归测试。

## 2. SEPR/V3 当前骨架

V3 骨架仍然成立：

- 4 个身份：`main-agent` / `sub-agent` / `evolution-agent` / `sub-E-agent`。
- 两套 workflow：W-flow 论文复现，E-flow 经验层自迭代。
- 三层子 agent：编排层 -> 执行层 -> leaf；拓扑固定，agent 不自动改拓扑。
- 核心防线：human gate、deterministic verifier、result_class 7 级枚举、provenance 五要素、固定拓扑、E-flow 只碰经验层。
- OpenCode 兼容已撤销；当前按 Claude Code-only 理解。Opus 不稳定时的应急是改 Claude Code URL/API 指向 DeepSeek，而不是维护 OpenCode 双系统。
- `.claude/skills/` 中文详细执行版已完成并实际使用；英文版只是后期可选优化。

## 3. 最近一次真实运行信号

Akimov 2401.04146 Mie 首跑已完成 W-flow step01-02。它不是物理复现成功，只是第一次真实运行暴露框架信号。

首跑 6 条信号：

1. memento MCP 曾不可用，确认为环境故障，不应静默假装已查记忆。
2. 路径约定自相矛盾，静态审计 A2 被真跑证实。
3. 预设目标图 `$Q_{sca}(x)$` 过渡曲线在论文 12 张图中不存在。
4. `papers.md` 旧版写入论文内容断言，属于 declared-vs-actual 问题。
5. sub-agent 漏交 8 字段报告 / `tables.md`，说明“报告靠自觉”不是 100% fire。
6. verifier `check_*.py` 已存在，但脚本存在不等于 verifier 可信。

2026-07-04 已完成的修复批次：

- `papers.md` 契约重写：框架层不得断言论文内容；“论文有哪张图”只能由 step02 原文提取、过 gate 后生效。
- A2 路径收敛：canonical 路径为 `.work/.todo/{paper}/{case}/...`，skill 草稿在该 case 下 `self-iteration/`，无额外 timestamp 层。
- W-flow spawn 全局模板加硬交付红线：8 字段报告和规定产物缺一不可；不适用也必须落盘说明。
- step02/03 目标图条款：step02 产出“目标图候选”为权威，step03 只能从候选中选择。
- memento MCP 预检第 0 步：开工先确认 memento 工具可调用；不可用时显式降级。

重要校正：`V3-AUDIT-2026-07_latest.md` 中 “A2 未修” 是修复前静态审计结论；截至 2026-07-04，应以 WORK_LOG 阶段十二和 memento 记录为准，A2 已修。

## 4. 仍然开放的设计债

仍建议后续讨论聚焦这些，而不是继续扩展治理面：

- **A1 capsule 生产侧**：E-flow 需要消费 `capsule.md`，但 W-flow 生产契约仍需前移到 step11 或等价位置。消费侧可等 E-flow 前修，生产侧最好在后续 W-flow 完成前定义。
- **D pdf 骨架诚实化**：`pdf` 空骨架不能声称不存在的脚本可用；开跑前应明确“不可依赖”或补最小脚本。
- **C1 残留**：leaf 无 `Agent` 已是硬约束，但 sub -> leaf 身份选择仍主要靠 prompt，仍有软约束成分。
- **hooks 时机**：Hook #3 报告字段校验最便宜，且已被首跑漏字段信号触发；Hook #2 result_class 门禁需 verifier 产物定义清楚；Hook #1 作业提交拦截等 SEPR 真碰 COMSOL/Magnus 再上。
- **治理过度投资风险**：V3 设计文档已经很多，但 Mie 还没完整跑通。核心纪律仍是先跑通，再按真实断点加护栏。

## 5. 用户新想法：E-flow 像 RLHF

本轮讨论认为：E-flow 确实类似一个小规模、离线、结构化的 RLHF/RLAIF 系统。

类比：

| RLHF / RL | SEPR E-flow |
|---|---|
| policy | agent + skill/prompt 行为策略 |
| rollout | 论文复现 workflow 轨迹 |
| trajectory | logs / reports / verifier outputs / human decisions |
| reward signal | verifier、result_class、人审、hooks telemetry |
| policy update | skill / prompt 备注 / 经验层更新 |
| replay buffer | 历史 case、run artifacts、capsule |
| held-out eval | 未参与 skill 学习的论文或参数点 |

对应风险：

- reward hacking：skill 学会骗评分器或满足字段，而非提升物理复现能力。
- Goodhart：一旦指标被优化，指标就可能不再代表真实目标。
- outcome bias：成功复现后，LLM 会事后高估所有被调用 skill 的贡献。
- skill overfitting：早期 Akimov/Degiron 经验被误升为通用规则。
- self-confirmation loop：系统用自己产生的证据奖励自己。
- mode collapse：系统逐渐只会走最保守套路，不再探索替代 formalization。

设计判断：

- E-flow 不应是“分数涨就吸收”。
- E-flow 应更像 evidence-reviewed skill lifecycle + CI/CD + evolutionary selection。
- LLM 可以提出 hypothesis 和 review evidence，但不能作为最终 judge。

## 6. 用户新想法：Skill 评价不做绝对打分

新方向：不要让 LLM 给 skill 打 87 分、92 分这种绝对分。更稳的是：

1. 记录客观证据。
2. 做贡献排序。
3. 做近似边际贡献。
4. 允许负贡献。
5. 用程序计算可计算的部分，LLM 只解释。

建议保留的 telemetry：

- skill 是否被调用。
- skill 输出是否被主 agent 引用。
- skill 建议是否导致后续动作。
- 是否被人工 override。
- 是否被人工修改。
- 是否与失败 / regression 共现。
- token、耗时、重试次数。
- 在成功 case 中是否 top contributor。
- 在失败 case 中是否 frequent suspect。

评价结果不要写成 `score: 92`，而应写成 evidence card：

```text
Skill: <name>
Evidence window: last N cases
Positive contribution:
Negative contribution:
Human overrides:
Regression association:
Replacement risk:
Recommended lifecycle action:
```

## 7. 用户新想法：Research Artifact / 审稿式 Skill 更新

一个值得保留的新设计方向：

```text
Workflow run
  -> Research Artifact / Technical Report
  -> Reviewer agents 审 evidence
  -> Governance 汇总
  -> Candidate skill update
  -> Regression / held-out
  -> Accept / revise / archive
```

关键点：

- Workflow 产出的不是“直接 skill update”，而是一份研究工件。
- Reviewer agent 审的是 evidence、risk、generalization、counterexample，不直接决定 accept。
- 最终 accept 应由 verifier、regression、human gate 和 governance 共同决定。
- 这比“LLM 给 skill 打分”更接近科学知识进入教材前的同行评审。

可以考虑多 reviewer：

- Physics Reviewer：物理机制是否合理。
- Evidence Reviewer：证据是否充分、是否可追溯。
- Regression Reviewer：是否可能破坏历史 case。
- Skill Reviewer：是否与已有 skill 重复、冲突或过拟合。

## 8. 用户新想法：Skill 不分类，而是状态机

不要把 skill 简单分成 A/B/C 类；那会造成 label inflation。

更好的结构是多轴：

```text
Skill =
  Type
  Evidence Level
  Lifecycle State
  Telemetry
  Dependency / conflict links
  Regression risk
  Scope applicability
```

Type 示例：

- Infrastructure
- Physics Reasoning
- Workflow / Orchestration
- Analysis / Reporting
- Experimental / Hypothesis

Evidence Level 示例：

- E0 speculation
- E1 single-case evidence
- E2 multi-case evidence
- E3 benchmark evidence
- E4 regression-safe evidence

Lifecycle 示例：

```text
Draft
  -> Candidate
  -> Benchmarking
  -> Accepted
  -> Stable
  -> Deprecated
```

这样 skill 的关键问题不再是“它属于哪类”，而是：

> 它在知识演化系统里处于什么状态、有什么证据、适用范围多大、风险多高。

## 9. 用户新想法：Work/Evolution 分离是核心优势

从 RL 视角看，Work/Evolution 分离是避免 self-referential collapse 的关键：

- W-flow 负责产生轨迹和证据。
- E-flow 负责离线审查、候选更新和回归验证。
- E-flow 不参与当前 rollout，也不在线修改正在执行的 agent。

这能降低：

- data contamination
- online feedback collapse
- reward hacking feedback loop

但会带来 evolution lag：

- 新发现不能立刻进入正式 skill。
- 短期能力提升慢。
- 最新经验可能滞后于执行。

可能的缓解：

- Stable Skill Library：正式库，版本化，regression-safe。
- Experimental Skill Cache：临时库，明确标记，允许短期试用，但不当成正式知识。
- Skill Arbitration Layer：判断某 skill 在什么条件下应该被使用，而不是只问它“好不好”。

## 10. 用户新想法：ECC / hooks / skill library 的系统解释

用户提到 ECC 有 4 门分类、200+ 内置 skill、50+ hooks。可抽象为：

```text
ECC = low-dimensional evolution gate controller
Skill library = high-dimensional operator bank
Hooks = weak-supervision telemetry system
```

这个视角有价值，但要注意 ECC bottleneck：

- 4 类动作无法表达 minor improvement、conditional activation、split vs merge、dependency impact 等细节。
- 可以保留低维动作，但加 meta-signal channel：

```text
Decision: Accept / Revise / Fork / Archive / Drop
Meta:
  confidence
  evidence_level
  novelty
  regression_risk
  dependency_impact
  scope
  suspected_negative_contribution
```

这和 SEPR 现有六维裁决并不冲突。更准确地说，六维裁决是 lifecycle action，meta-signal 是裁决证据。

## 11. 对下一轮讨论最有价值的问题

建议压缩后优先讨论这些，不要马上写代码：

1. E-flow 是否应重命名为 “Skill Review / Skill Governance Flow”，弱化“自动进化”叙事？
2. `capsule.md` 是否应该升级为 Research Artifact 的最小形式？
3. Hook #3 是否应在下一次 W-flow 前轻量试点，作为 telemetry/schema 校验，而不是完整治理？
4. Skill Card 的最小字段是什么，哪些字段现在就需要，哪些等多 case 后再加？
5. Experimental Skill Cache 是否值得引入，还是会在首轮增加复杂度？
6. Discovery Test 应放在何时：第一个复现成功后，还是等 2-3 篇复现后？
7. 贡献排序由谁做：main-agent 自评、reviewer agent 审 trace，还是程序先算候选再让 LLM 解释？

## 12. 不能忘的边界

- 不要把网页端闲聊笔记当成已批准设计。
- 不要把 E-flow 做成“自动改自己”的系统；它仍然只碰经验层，全部走 human gate。
- 不要把 skill 数量当能力；真正重要的是 selection、evidence、regression、telemetry。
- 不要在 Mie 未完整跑通前继续大规模加治理。
- 不要把 pipeline_completed / diagnostic_only / surrogate_fallback 包装成 physical_reproduction_success。

## 13. 推荐恢复顺序

压缩后若需要恢复上下文，建议顺序：

1. 本文件。
2. `WORK_LOG.md` 阶段十二。
3. `v3-final/V3-CHANGELOG-SINCE-HUMAN-CN_latest.md`。
4. `v3-final/V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md`。
5. `v3-final/V4-ROADMAP-CN_latest.md`。
6. memento 记忆：`SEPR 首跑 step01-02 六条信号 + 2026-07-04 修复批次`、`决策：框架层不得持有论文内容断言`、`只读外部笔记：E-flow/RLHF/Skill治理设计想法`。

