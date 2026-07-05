# SEPR V4 Preview：RLHF 威胁模型、审稿式 Skill 准入、Discovery Test、Hooks 与 Skill Attribution（初步思路，反思收敛版）

> **文档性质：初步思路 / design preview，不是已批准落地方案。**
>
> 日期：2026-07-05
>
> 产出位置：`optics_agent/v3-final/`
>
> 背景：本文承接 `V3-CONTEXT-COMPACTION-HANDOFF-2026-07-04_latest.md`、`V4-ROADMAP-CN_latest.md`、`V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md` 与本轮并发子 agent 讨论。它把用户提出的 5 个想法整理为 V4 方向预览，并经过一轮红队/收敛反思后改成“最小闭环优先”。本文不修改 SEPR 本体，不替代 `V4-ROADMAP-CN_latest.md`，也不表示这些设计已经通过 human gate。

---

## 0. 一屏结论

这 5 个想法不应被实现为 5 个平行大模块。反思后的最终口径是：**V4 的近期目标不是增加 agent 数量，也不是建设完整治理平台，而是让 W-flow 的真实运行经验能被最小成本地审计、归因、复盘和人审。**

V4 最小闭环：

```text
先跑通 Mie
  -> Hook #3 检查 sub-agent 报告字段和必需产物
  -> capsule.md 汇总 result_class、claim、evidence、risk、skill 线索
  -> Per-run Skill Attribution Notes 提供本轮归因证词
  -> 人工判断是否需要 candidate skill diff
  -> 用 RLHF-like threat checklist 防自我奖励和 Goodhart
  -> human gate 决定是否进入 skill lifecycle

V5+：
  -> 多 case regression / held-out
  -> 完整 Skill Governance Flow
  -> Discovery Test / Blueprint Generalization Benchmark
```

阶段判断：

| 想法 | V4-preview 判断 | 当前建议 |
|---|---|---|
| 1. 把自进化比作 RLHF，借鉴防 hack 机制 | 必要，但只作为威胁模型 | 写成 E-flow threat checklist，不照搬 RLHF 优化器 |
| 2. skill 迭代比作论文审稿 | 必要，适合作为知识准入模型 | 先做最小 `capsule.md`，不做重型审稿委员会 |
| 3. 创新 agent / 扫参式创新检验 | 远期可能需要，条件触发 | 降级为 V4-late/V5+ 的 Discovery Test；不是第五 agent |
| 4. hooks | 必要，且近期最有工程价值 | 先试 Hook #3：report schema + required artifacts gate |
| 5. agent 自己做 skill 贡献排序 / 局部贡献桶 | 有价值，但必须降级为 self-attribution | 当作本轮证词，不做百分制、平均分、排行榜或自动裁决 |

核心边界：

- 不把 `result_class`、贡献桶、reviewer findings 压成单一 reward。
- 不让 reviewer mode 直接 accept / reject 正式 skill。
- 不让 E-flow 在线修改当前 W-flow 正在用的 skill。
- 不在 Mie 未完整跑通前大规模加治理。
- 不把 `pipeline_completed` / `diagnostic_only` / `surrogate_fallback` 包装成 `physical_reproduction_success`。

### Final Stance

```text
V4 近期只收敛到：
Hook #3 + 最小 capsule.md + Per-run Skill Attribution Notes + human-gated candidate skill update。

RLHF 是威胁模型。
审稿是知识准入模型。
Discovery Test 是 V4-late/V5+ 的泛化评测。
```

### Non-goals

V4 近期不做：

- 不实现自动 E-flow。
- 不修改 V3 固定拓扑。
- 不新增“创新 agent”或第五 agent。
- 不允许 E-flow 修改自身、hooks、verifier 或 workflow。
- 不把 `result_class` / 贡献桶 / reviewer findings 合成为单一 reward。
- 不让 reviewer mode 直接 accept / reject 正式 skill。
- 不建立 skill 百分制排行榜或 leaderboard。
- 不在 Mie 跑通前引入 Discovery Test。
- 不把探索候选、流程完成或诊断结果解释成物理复现成功。

---

## 1. 当前项目状态约束

V4 preview 必须继承 V3 的基本边界：

- `optics_agent` 是 SEPR 元设计工作区，`self-evo-paper-repro` 是 SEPR 执行工作区。
- 当前主路径是人工预训练循环，不是自动 E-flow：

```text
optics_agent 设计框架
  -> SEPR 跑论文复现
  -> 真实运行经验回传 optics_agent
  -> optics_agent 人工审查并改进 SEPR 设计
  -> SEPR 重跑验证
```

- V3 骨架仍成立：4 agent、W-flow/E-flow、三层子 agent、固定拓扑、human gate、deterministic verifier、7 级 `result_class`、provenance 五要素。
- Akimov 2401.04146 Mie 首跑 step01-02 暴露了真实框架信号，但尚不是物理复现成功。
- 2026-07-04 已修复一批首跑问题：`papers.md` 不再持有论文内容断言、A2 路径收敛、spawn 交付红线、step02/03 目标图候选权威、memento 预检。
- 仍开放的关键债：A1 capsule 生产侧、D pdf 骨架诚实化、C1 leaf 选择软约束、Hook #3 试点、避免治理过度投资。

因此，本文的落点不是“马上扩展新系统”，而是回答：

> V4 如果要从 V3 的复现系统走向更可靠的 skill governance 和未来 discovery evaluation，哪些概念该保留，哪些该延后，哪些该先做最小版本？

---

## 2. 总体架构：把 5 个想法收敛成一个最小证据闭环

推荐概念层次：

```text
Hook #3
  先保证 sub-agent 交付契约成立：字段齐、产物在、路径对、有缺失理由

capsule.md
  作为本轮最小 Research Artifact：把 result_class、claim、evidence、risk、skill 线索放在一个文件里

Per-run Skill Attribution Notes
  作为 capsule 内的一类 agent 证词：本轮哪些 skill 可能有正/负/节省步骤贡献

轻量 evidence review
  不是 reviewer committee，而是人工/agent 按 checklist 审 claim 是否有证据、是否越界、是否需要 skill diff

RLHF-like threat checklist
  作为 skill diff 前的风险检查：是否 Goodhart、是否过拟合单 case、是否自我奖励

human gate
  决定是否进入 candidate skill lifecycle
```

它们的职责不能混：

| 层 | 负责什么 | 不负责什么 |
|---|---|---|
| RLHF threat model | 找出 E-flow 的 failure modes | 不训练 reward model，不做 PPO |
| 轻量 evidence review | 审证据、范围、反例、回归风险 | 不直接 accept skill |
| Hooks | schema、artifact、路径、资源、verifier artifact 存在性 | 不证明物理正确 |
| Skill Attribution Notes | agent 对本轮 skill 贡献做结构化归因 | 不给全局 skill 质量判决 |
| Discovery Test | V5+ 测 blueprint 是否能外推探索 | 不进入 V4 近期闭环，不替代论文复现 |

近期闭环只要求：

```text
Sub-agent 完成 step
  -> Hook #3 检查 required fields / artifacts / evidence_refs
  -> 通过后 main-agent 汇总或补全 capsule.md
  -> capsule.md 内保留 Skill Attribution Notes
  -> 人工判断是否需要 candidate skill diff
```

---

## 3. 想法一：把 E-flow 当作 RLHF/RLAIF 式威胁模型

### 3.1 为什么这个类比成立

SEPR E-flow 不是真正 RLHF：它不更新模型权重，也不训练 reward model。但它有类似结构：系统根据反馈信号更新未来行为策略，只是更新对象从模型参数变成了 skill、prompt 备注和经验层。

| RLHF / RL 概念 | SEPR E-flow 对应物 |
|---|---|
| policy | agent + skill + prompt + context 形成的行为策略 |
| rollout | 一次 W-flow 论文复现轨迹 |
| trajectory | logs、reports、verifier outputs、human decisions |
| reward / preference signal | `result_class`、verifier、人审、hooks telemetry、skill attribution |
| reward model / judge | reviewer mode、统计脚本、人工审查规则 |
| policy update | skill / prompt 备注 / 经验层更新 |
| replay buffer | 历史 capsule、Research Artifact、run artifacts |
| held-out eval | 未参与本轮 skill 学习的论文、旧 case、参数点 |

所以，RLHF 类比应该作为 **threat model**，不是作为实现模板。

### 3.2 真正对应的风险

**Reward hacking / specification gaming**

Agent 可能学会满足代理指标，而不是提升物理复现能力。例如：

- 报告字段齐全，但关键证据为空。
- `result_class` 写得保守或漂亮，但没有真实 verifier 支撑。
- verifier 脚本路径存在，但脚本本身不可被信任。
- skill 学会迎合 reviewer 的格式，而不是避免错误物理模型。

**Goodhart**

一旦某个指标被优化，它就可能不再代表真实目标。SEPR 中尤其要防：

- 报告完整度变高，但复现真实性没变。
- skill 贡献桶变高，但只是 agent 自己会说好话。
- `pipeline_completed` 被系统奖励后，agent 越来越擅长跑流程而不是复现物理。
- 早期 Mie/Akimov 经验被误写成跨领域通用规则。

**Outcome bias**

成功 run 后，LLM 容易事后高估所有被调用 skill 的贡献；失败 run 后，也容易把责任推给某个局部 skill。

**Skill overfitting**

单篇论文、单类物理、单个工具链的经验被误升为 Stable skill，导致跨任务负迁移。`V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md` 中 SkillFlow、Library Drift、Assay/Not All Skills Help、More Skills Worse Agents 等证据都支持这个警告。

**Self-confirmation loop**

W-flow 产生 artifact，E-flow 根据这些 artifact 改 skill，下一轮 W-flow 又用这些 skill 解释新 artifact。缺少外部 verifier、反例和人审时，系统会奖励自己的叙事。

**Mode collapse**

如果系统只奖励最稳、最保守、最像模板的流程，skill library 会逐渐丧失替代 formalization、探索异常 case、提出新模型的能力。

### 3.3 不应照搬 RLHF 的部分

不建议做：

- PPO / KL penalty / token-level reward。
- 训练 reward model。
- 把 `result_class`、reviewer findings、contribution bucket 压成一个 reward。
- 用 AI reviewer 替代 human gate。
- 在线更新当前 W-flow 正在使用的 skill。
- 让 E-flow 自己修改自己的规则、hooks、verifier 或拓扑。

SEPR 的正确方向不是“RLHF 化”，而是：

```text
small offline skill-governance process
with RLHF/RLAIF-like failure modes
and verifier / regression / human-gate defenses
```

### 3.4 E-flow Threat Checklist（初版）

每次准备吸收 skill 经验前，至少问：

```text
[ ] 这次更新优化的是物理复现能力，还是只优化了报告/格式/评分代理？
[ ] 是否有 deterministic verifier 或外部 artifact 支撑？
[ ] 是否存在失败 case、反例、负贡献或人工 override？
[ ] 适用范围是否明确写窄？
[ ] 是否把单 case 偶然成功误写成通用 skill？
[ ] 是否可能导致 skill library 更单一，压制替代路线？
[ ] reviewer mode 是否可能被同一 skill library 污染？
[ ] 是否有 held-out / regression case 检查？
[ ] 是否保留旧版本、失败版本和分叉路径？
[ ] human gate 是否看到原始证据，而不只是摘要？
```

### 3.5 对 V4 的最小落地

现在只建议：

- 把上面的 checklist 写入 E-flow / skill governance 设计。
- `result_class` 明确写成 outcome context，不是 reward。
- Skill update 必须绑定 `Claim / Evidence / Scope / Counterexample / Regression Needed`。
- 保留 Archive / Fork / Candidate / Stable / Deprecated 生命周期。
- 失败证据、负贡献、人工 override 必须可被后续检索。

不建议现在实现复杂 reward model 或自动评分裁决。

---

## 4. 想法二：把 skill 迭代当作论文审稿式知识准入

### 4.1 这个类比解决什么问题

Skill 是从运行经验中抽象出来的方法知识。它不应因为一次 run 成功就进入 Stable library。更合理的准入过程类似科学知识从实验结果进入论文、再进入教材：

```text
W-flow run
  -> capsule.md
  -> reviewer findings
  -> candidate skill diff
  -> regression / held-out check
  -> human gate
  -> lifecycle action
```

这个机制主要防：

- outcome bias：成功后高估所有参与 skill。
- overgeneralization：局部经验被写成通用规则。
- library drift：低价值或错误 skill 累积污染检索。
- self-confirmation：系统只用自己的解释奖励自己。
- reviewer 越权：review mode 直接决定 accept。
- 失败知识丢失：负贡献、误导路径、人工 override 被最终报告吞掉。

映射关系：

| 科学审稿 | SEPR skill governance |
|---|---|
| manuscript | `capsule.md` |
| supplement | logs / tables / verifier outputs / scripts |
| reviewer comments | reviewer findings |
| editor decision | governance + human gate |
| revision history | candidate diff + version lineage |
| journal archive | Stable Skill Library |
| desk reject / archive | Drop / Archive / Deprecated |

### 4.2 最小 `capsule.md` 字段

当前不应一口气做完整审稿系统。为避免概念重复，近期统一叫 `capsule.md`；“Research Artifact”只是它的设计含义，不新增第二套必交文件。

最小 `capsule.md` 先只服务三件事：

- context compaction 后还能恢复本轮证据。
- 人工能判断是否需要 candidate skill diff。
- 未来 E-flow 有统一输入，而不是散落在报告、日志和聊天里。

近期字段压到：

```yaml
run_id:
paper_id:
case_id:
workflow_step:
result_class:
claim:
evidence_refs:
missing_or_uncertain_evidence:
affected_skill:
skill_attribution:
risk_or_counterexample:
proposed_action: no_change | investigate | draft_candidate_diff | human_review
```

原则：`evidence_refs` 必须指向真实文件路径、脚本、日志、verifier 输出或人工审查记录，不能只有自然语言总结。

远期完整字段，例如 reviewer findings、regression plan、lineage、human gate decision，可以等准备真开 E-flow 时再扩展。近期不要让 sub-agent 为完整治理表格付出额外 token 成本。

### 4.3 Reviewer mode / evidence review 应该做什么

Reviewer mode 可以由 main-agent 按 checklist 执行，也可以远期由独立 reviewer agent 执行。近期不要把它实体化为新委员会。它可以审：

- 证据是否足够、可追溯。
- claim 是否越界，例如把 `pipeline_completed` 说成物理复现成功。
- 适用范围是否写窄。
- 是否有反例、失败 run、人工 override。
- proposed diff 是否过大，是否把局部修正写成全局规则。
- 是否与已有 skill 重复、冲突、shadowing。
- 是否可能造成 regression。

Reviewer mode 不应做：

- 不直接 accept / reject 正式 skill。
- 不直接写入 Stable Skill Library。
- 不修改 reviewer 自己的准则、hooks、verifier 或 workflow。
- 不用单一星级或总分替代证据。
- 不因为本轮成功就判定 skill 泛化有效。
- 不因为本轮失败就直接定罪某个 skill。

一句话：

> Reviewer 给 findings，不给最终判决；最终判决属于 verifier + regression + human gate。

### 4.4 阶段化，避免 bureaucratic overkill

```text
阶段 0：V4-preview
  只写设计，不落地完整系统。

阶段 1：最小 capsule
  每轮 W-flow 结束时留下 claim / evidence_refs / result_class / affected_skill / risk / proposed_action。

阶段 2：Hook #3 后加轻量 findings
  如果再次出现漏字段、漏产物、错误 result_class，再引入 evidence review。

阶段 3：多 case 后做 regression 准入
  至少 2-3 个 case 后，candidate skill update 才要求历史 case 或 held-out 点检查。

阶段 4：真开 E-flow 前完整化
  完整 lifecycle、版本谱系、reviewer 分工、回归预算、人审表。

阶段 5：Stable Skill Library
  只有多 case 证明有效、无明显 regression、范围清楚的 skill 才进入 Stable。
```

---

## 5. 想法三：创新 agent 降级为远期 Discovery Test

### 5.1 最终口径

“创新 agent”方向和长期目标一致：论文复现不是终点，最终要走向 reusable blueprint、case/DSL、参数 sweep 和新科学探索。

但它**不应进入 V3 或 V4 近期主路径**。当前更准确的名字是：

```text
Discovery Test / Blueprint Generalization Benchmark
```

它不是第五 agent，不是当前 Mie 主路径，不是近期要实现的新 workflow。它是 V4-late / V5+ 的远期评测框架，用于检验稳定 blueprint 是否能从“复现已知论文”外推到“受约束的新参数空间探索”。

### 5.2 为什么必须降级

当前加入创新 agent 会混淆三件事：

- blueprint 是否可靠。
- agent 是否会设计参数探索。
- 所谓“新现象”是否真实。

扫参式探索天然有 p-hacking / 多重比较风险：参数点足够多时，总能挑出一张看似有趣的图。如果 agent 可以事后选择 hypothesis、metric、窗口、色标、候选筛选规则，它很容易制造“发现感”，但这不是科学发现。

### 5.3 启动条件

Discovery Test 至少等这些条件满足后才进入设计实施：

- 至少一个 blueprint 稳定达到 `physical_reproduction_success`，最好同一 blueprint 已复用过 2-3 个 case。
- case/DSL 能表达参数、几何、材料、observable、solver、资源和失败状态。
- deterministic verifier 稳定，不只是“脚本存在”。
- 有 frozen benchmark 或 held-out 参数区间。
- 所有 sweep 点、失败点、无效点、负结果都能落盘。
- 有明确 human review，不允许 agent 自己宣布“发现”。

### 5.4 禁止自由创新 agent

新增红线：

> SEPR 不允许 agent 在无预注册协议、无固定指标、无完整负结果记录、无 verifier、无人审的情况下自主扫参、挑图、改指标，并宣称发现新现象。

具体禁止：

- 禁止跑完后再改 hypothesis、metric、色标、窗口、候选筛选规则。
- 禁止只保存漂亮图，隐藏失败点和无效点。
- 禁止把 discovery candidate 当成 `physical_reproduction_success`。
- 禁止 COMSOL 单独宣布发现；COMSOL 初期只能做 cross-check。
- 禁止 Discovery Test 的结果直接修改 Stable Skill Library。
- 禁止把“探索成功”作为 W-flow agent 的 reward。

### 5.5 远期最小 protocol 草案

这不是 V4 近期任务，只是未来设计草案。必需字段可能包括：

```yaml
test_type: rediscovery | interpolation | extrapolation | candidate_discovery
hypothesis:
null_model:
blueprint_version:
skill_versions:
benchmark_refs:
sweep_space:
  parameters:
  ranges:
  resolution:
  exclusions:
  random_seed:
primary_metric:
secondary_metrics:
success_threshold:
baselines:
candidate_selection_rule:
multiplicity_control:
stopping_rule:
resource_budget:
heldout_region:
verifier_requirements:
logging_contract:
  all_points_required: true
  failed_points_required: true
  invalid_points_required: true
provenance:
human_review:
```

延后项：

- `comsol_crosscheck_manifest.yaml`：只在候选进入验证阶段需要。
- `negative_results.md`：可先合并进 `all_results.csv` 的 `status/failure_reason` 字段。
- `candidate_findings.md`：只有出现候选时生成。
- discovery candidate 状态维度：远期再加，当前不碰 `result_class`。
- 多 reviewer agent、active learning baseline、完整独立方法验证：均不属于第一版必需项。

---

## 6. 想法四：引入 hooks

### 6.1 Hooks 解决什么

Hooks 的定位：

> 把 prompt 里的“必须做”变成机器可检查的硬契约。

它解决：

- 防漏交：检查 8 字段报告、`tables.md`、目标图候选、参数表、handoff 等产物。
- 防越级：没有 verifier artifact 时不能声明高等级 result_class。
- 防资源事故：COMSOL/Magnus 提交前检查 GPU、CPU、内存、license mount、run_id、staging path。
- 防上下文漂移：记录 agent、skill、artifact、hook warning/block、result_class 的证据链。
- 防 prompt 自觉失效：凡脚本能判定的，不再依赖 agent 记得。

Hooks 只能检查“契约是否满足”和“证据是否存在”，不能直接证明物理正确性。物理正确性仍靠 verifier、论文图定量比较、人审和复现实验。

### 6.2 Hook #3：当前最值得试点

Hook #3 建议定义为：

```text
sub-agent report schema + required artifact gate
```

它最适合现在做，因为 Akimov 首跑已经出现真实触发：sub-agent 漏交 8 字段报告和 `tables.md`。这不是物理难题，而是交付契约失败。

优点：

- 低风险：不改 W-flow 拓扑，不改 agent 角色，不碰 skill 进化逻辑。
- 可判定：字段、artifact、路径都可以脚本检查。
- 立刻有收益：提升 handoff、context compaction、E-flow evidence 质量。
- 不依赖 COMSOL/Magnus。
- 可从 `block` 开始：报告字段和必需产物没有太多模糊性。

最小规则：

```yaml
required_fields:
  - agent_role
  - task_id
  - input_refs
  - actions_taken
  - outputs
  - result_class
  - uncertainty_or_missing_evidence
  - next_handoff
required_artifacts:
  - tables.md or unavailable_with_reason
  - target_figure_candidates.md when step02 applies
  - report.md
path_contract:
  root: .work/.todo/{paper}/{case}/...
provenance:
  every_key_claim_requires_ref: true
failure_mode:
  missing_fields: block
  missing_artifacts_without_reason: block
  n_a_without_reason: block
```

### 6.3 Hook #2：result_class / verifier gate

Hook #2 不应过早 block。前置条件：

- 7 级 `result_class` enum 和语义稳定。
- 每个高等级 result_class 对应哪些 verifier artifacts 已定义。
- verifier artifact 不只是脚本存在，还包括版本/hash、输入、阈值、退出码、metrics、provenance。
- 明确最高可声明等级：没有物理 verifier 时，最多只能是 `pipeline_completed`、`diagnostic_only` 或相应低等级。

建议阶段：

```text
observe -> warn -> block
```

在 verifier contract 未稳定前，先不要 block。

### 6.4 Hook #1：COMSOL/Magnus job submission guard

Hook #1 等 SEPR 真碰 COMSOL/Magnus 后再做。前置条件：

- 统一 job manifest。
- 统一提交入口，避免 raw ssh/raw Magnus 命令绕过 gate。
- 资源策略：GPU、A-class job、超过半集群资源必须显式确认。
- 提交前按 `run_id` 查询已有 active/success job。
- stdout、metrics、final artifacts 能被后续 verifier 读取。

Mie Python-only 阶段大概率不需要先做 Hook #1。

### 6.5 Hook 分级

```text
observe: 只记录
warn: 注入警告，但允许继续
block: 阻断当前 step，要求返工
human_review: 需要人工确认
```

当前 Hook #3 可以考虑 `block`；Hook #2 先 `observe/warn`；Hook #1 等 COMSOL/Magnus 真实进入路径后再设计。

---

## 7. 想法五：Per-run Skill Attribution Notes，而不是评分系统

### 7.1 定位

用户澄清后的第 5 条不是“让 agent 给 skill 打百分制绩效分”，而是让 agent 在每次复现后结构化指出：

- 哪条 skill 最大正贡献。
- 哪条 skill 可能负贡献。
- 哪条 skill 节省最多步骤。
- 哪些 skill 被调用但实际低价值、冗余或证据不足。
- 哪些 skill 可能造成误导、重复劳动或错误路径。

这个设计应命名为：

```text
Per-run Skill Attribution Notes
```

不是：

```text
Skill Evaluation / Skill Score / Skill Metrics / Global Skill Rating
```

一句话：

> Agent 的贡献排序是证词，不是判决。

更严格地说，它只回答：

> 本轮 agent 自认为哪些 skill 影响了执行路径？

它不能回答：

> 哪个 skill 更好？哪个 skill 应该升级？哪个 skill 全局更可靠？

### 7.2 自我归因偏差

即便不用百分制，星级或相对贡献桶也可能 Goodhart。主要偏差包括：

```text
hindsight bias: 看到结果后重构“谁贡献最大”
self-serving bias: 成功归因给自身策略，失败归因给外因
salience bias: 高 token、高频出现、刚读过的 skill 被高估
availability bias: context window 里可见的 skill 被高估
hidden infrastructure bias: hooks、路径规范、verifier 这类隐性贡献被低估
confabulated counterfactual: “节省了 5 步”常是猜的
reviewer-pleasing bias: agent 写出 reviewer 想看的归因
outcome leakage: result_class 越高，越倾向于给正贡献
```

### 7.3 最小字段

```yaml
run_id:
workflow_step:
agent_role:
result_class:  # 只记录本轮结果，不参与打分

skill_claims:
  - skill_name:
    skill_version_or_hash:
    contribution_type: positive | negative | step_saving | risk_containment | redundant | unclear
    contribution_bucket: decisive | useful | ambiguous | redundant | suspected_harmful
    claim:
    evidence_refs:
    downstream_action_refs:
    counterfactual_uncertainty: low | medium | high
    alternative_explanations:
    scope_limit:
    reviewer_followup:
```

字段说明：

- `contribution_bucket` 不是星级，不是质量分，只是本轮证词强弱桶。
- `counterfactual_uncertainty` 必须显式写出，因为“节省步骤”往往只是估计。
- `alternative_explanations` 用来抵消 hindsight bias。
- `reviewer_followup` 只能提出待审问题，不得建议升级/降级正式 skill。

### 7.4 与 `result_class` 分离

`result_class` 只限定证词适用范围，不作为权重。

```text
physical_reproduction_success:
  正贡献可进入候选证据，但仍需 verifier / human review。

pipeline_completed:
  只能证明流程贡献，不能证明物理贡献。

diagnostic_only / surrogate_fallback:
  只能证明诊断或替代路径贡献，不能升级复现 skill。

failed / blocked:
  负贡献是调查线索，不是定罪证据。
```

不要把 self-attribution 乘上 `result_class` 权重后变成 skill 分数。

应写：

```text
result_class provides claim scope, not score weight.
```

### 7.5 聚合禁令

禁止：

- 禁止把 `contribution_bucket` 转成数字平均值。
- 禁止做 skill leaderboard。
- 禁止跨论文、跨领域比较 skill 排名。
- 禁止用 self-attribution 单独触发 skill 升级、降级、deprecate。
- 禁止用成功 run 给所有被调用 skill 自动加分。
- 禁止用失败 run 给某个 skill 自动定罪。
- 禁止把 step-saving 当作真实节省，除非有 action log 或人工确认。

允许的聚合只能是 evidence ledger：

```text
允许统计：某 skill 被多少次提到为 suspected_harmful，并链接证据。
允许统计：某 skill 的 claim 是否反复缺 evidence_refs。
允许统计：人工 override 是否反复发生在同一 skill 后。
允许统计：某 skill 是否常与 hook block / verifier failure 共现。
```

也就是说，聚合的是“待审线索”，不是“分数”。

### 7.6 何时启用

不要“每次任务都评”。建议只在以下场景启用：

```text
1. W-flow step 完成且产生 capsule.md 时启用。
2. 发生 hook block、verifier failure、人工 override 时启用。
3. 准备提出 skill diff 时必须启用。
4. 琐碎文件整理、路径移动、单纯查资料不启用。
5. V4 早期只 observe，不进入 lifecycle 决策。
```

---

## 8. 推荐 V4 阶段化计划

### 8.1 现在可以做的最小动作

这些动作与“先跑通，再加护栏”不冲突：

1. **定义最小 `capsule.md` 口径**
   - 先只要求 `claim / evidence_refs / result_class / affected_skill / risk / proposed_action`。
   - 近期只服务 context compaction 和人工复盘，不服务自动 E-flow。

2. **试点 Hook #3**
   - 检查 sub-agent report schema 和 required artifacts。
   - 目标是防止再次漏 8 字段报告 / `tables.md`。
   - 不检查物理正确性，不检查复杂贡献评分。

3. **加入 Per-run Skill Attribution Notes**
   - 只作为本轮归因证词。
   - 强制 evidence_refs / action_refs。
   - 不数值化、不平均、不排行、不驱动 lifecycle。

4. **写入 E-flow Threat Checklist**
   - 作为 candidate skill diff 前的人审/agent 审查清单。
   - 近期不启动自动 E-flow。

### 8.2 等 2-3 个 case 后再做

- reviewer findings 分工。
- skill evidence card 聚合。
- task-conditional skill mask。
- regression / held-out case。
- skill lifecycle dashboard。
- memory utility_score / valid_to / quarantine。

### 8.3 等 blueprint 稳定物理成功后再做（V4-late / V5+）

- Discovery Test / Blueprint Generalization Benchmark。
- 预注册 sweep protocol。
- held-out discovery validation。
- COMSOL cross-check。
- discovery candidate 状态维度。

这些不是 V4 近期闭环的一部分。初期 Discovery Test 也应先做 rediscovery / held-out known-case，而不是直接让 agent 宣称候选新发现。

### 8.4 真开 E-flow 前必须满足

- A1 capsule 产/消契约闭环。
- verifier artifacts 和 result_class gate 稳定。
- 至少多个真实 case，含成功和失败样本。
- regression set 可运行。
- human gate 流程明确。
- E-flow 不修改自己、不改拓扑、不改 verifier/hook 规则。

---

## 9. Open Questions

这些问题暂不在本文中定案：

1. 最小 `capsule.md` 字段是否已经足够支持 context compaction、人工复盘和未来 E-flow 输入？
2. Hook #3 是放在 `SubagentStop`、`Stop`，还是文件写入后的 `PostToolUse`？
3. Skill Attribution Notes 是由 sub-agent 写、main-agent 汇总，还是两者都写并保留冲突？
4. reviewer findings 是否长期需要独立 reviewer agent，还是长期保持 main-agent checklist + human review？
5. Experimental Skill Cache 是否值得引入，还是先只保留 Candidate 状态？
6. V5+ Discovery Test 的第一个目标应是 rediscovery / held-out known-case，还是更难的 interpolation / extrapolation？
7. 何时允许新增 discovery 状态维度，是否保持与 `result_class` 正交？

---

## 10. 参考锚点

本节列出影响本文判断的来源。它们提供设计锚点，不表示 SEPR 已采用对应方案。

本地文档：

- `v3-final/V3-CONTEXT-COMPACTION-HANDOFF-2026-07-04_latest.md`
- `v3-final/V4-ROADMAP-CN_latest.md`
- `v3-final/V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md`
- `v3-final/DESIGN-GAP-AUDIT-CN_latest.md`

RLHF / reward hacking / Goodhart：

- Christiano et al., 2017, Deep Reinforcement Learning from Human Preferences: https://arxiv.org/abs/1706.03741
- Ouyang et al., 2022, Training language models to follow instructions with human feedback: https://arxiv.org/abs/2203.02155
- Bai et al., 2022, Constitutional AI: Harmlessness from AI Feedback: https://arxiv.org/abs/2212.08073
- Amodei et al., 2016, Concrete Problems in AI Safety: https://arxiv.org/abs/1606.06565
- Manheim & Garrabrant, 2018, Categorizing Variants of Goodhart's Law: https://arxiv.org/abs/1803.04585
- Gao et al., 2022, Scaling Laws for Reward Model Overoptimization: https://arxiv.org/abs/2210.10760
- Lilian Weng, Reward Hacking in Reinforcement Learning: https://lilianweng.github.io/posts/2024-11-28-reward-hacking/

Skill evolution / library governance：

- SkillFlow, arXiv:2604.17308, as reviewed in `V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md`
- Library Drift, arXiv:2605.19576, as reviewed in `V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md`
- Not All Skills Help / Assay, arXiv:2606.15390, as reviewed in `V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md`
- More Skills, Worse Agents, arXiv:2605.24050, as reviewed in `V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md`

Hooks / deterministic guardrails：

- Claude Code hooks reference: https://code.claude.com/docs/en/hooks
- Claude Code hooks guide: https://code.claude.com/docs/en/hooks-guide

Scientific discovery evaluation：

- DiscoveryWorld: https://arxiv.org/abs/2406.06769
- ARA: Agentic Reproducibility Assessment for Scientific Peer Review: https://arxiv.org/abs/2605.02651
- Scientific Hypothesis Generation and Validation survey: https://arxiv.org/abs/2505.04651

---

## 11. 最终口径

V4-preview 的核心不是“给 SEPR 增加更多 agent”，而是把 V3 已有的复现轨迹变成可审计、可归因、可回归的知识准入系统。

一句话：

> RLHF 负责提醒系统会如何骗自己；审稿机制负责经验如何进 skill；hooks 负责硬契约；skill attribution 负责留下局部证词；Discovery Test 负责未来检验 blueprint 是否能从复现走向发现。

当前最小建议仍是：**先跑通 Mie，再优先做 Hook #3 + 最小 `capsule.md` + Per-run Skill Attribution Notes。**
