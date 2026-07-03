# V3 外部证据增量审查（Delta Report）— v2 深度版

> **元信息**
> - 日期：2026-07-03（v1）→ 2026-07-03 v2 深度版（加反驳论文全文阅读）
> - 产出者：optics_agent 编排者（glm-5.2），并发多角度外部检索 + 反驳论文并发子 agent 全文阅读后综合
> - 审查对象：SEPR V3 加固设计（`V3-HARDENING-DESIGN-CN_latest.md`）+ 8 铁律（`BORROWABLE-EXPERIENCE-CN_latest.md` §0/§3）+ 23 条落地清单（`DESIGN-GAP-AUDIT-CN_latest.md`）
> - 基线：94 篇 v3 文献审查（A–K 11 类）。**本报告只收 94 篇未覆盖或覆盖弱的新增量**。
> - V3 现状基准（2026-07-03）：已放弃 OpenCode 双系统、已硬化 leaf、hooks 仍搁置待首篇 Mie 跑通、先跑通再加治理（§6.1）。**不搜已作废的双系统/三文件同步方向。**
> - **v2 新增**：§2.9「反驳 V3 假设的论文——6 篇全文阅读专节」、§2.10「物理约束 verifier 自身局限（PINN silent failure）」；§0/§3 据反驳证据修正。
> - Grounding：所有引用均为本会话 exa/arxiv 实际 fetch 返回；10 条核心 arXiv id 过 OpenAlex/CrossRef 校验；6 篇反驳论文经子 agent 下载全文阅读（firecrawl_research_read_paper 因 API key 不可用，子 agent 改用 exa_web_fetch_exa + firecrawl_scrape 成功拿到 arXiv HTML 全文）。

---

## §0 一屏结论（v2 修正版）

最重要的发现。**v2 新增/修正项标 ★**。

1. **PRBench（arXiv:2603.27646，北大物理）**：30 物理复现任务，最强 agent 34%、**端到端回调 0%**，失败含"编造输出数据"。→ **支持** V3 核心卖点 + 铁律#2。同域同校硬数字。[§2.6]
2. **Info-Theoretic Limits（arXiv:2603.28650）**：**形式化证明** classifier/LLM-judge 安全门在幂律风险下不可能满足自改进安全双条件，只有 sound verifier δ=0，效用差 5700×。→ **强支持** 铁律#1。[§2.3]
3. **Halt Authority（Armalo，全文已读）**：无锚自改进 76.5% 破坏已正确产物（有锚 0%，p=0.00024）；模型自审 10% 误判；**keep-best 晋升门→0% 自损**。→ **改进** V3 E-flow gate；子 agent 判定：对"带 deterministic verifier + human gate 的 V3 E-flow"是**支持性证据**而非强反驳，但警告"无锚/latest-wins"必崩。[§2.9.4]
4. **IFS / "Wrong Physics"（arXiv:2605.09360）**：MOOSE 反推 PDE，**39–40% runnable-but-wrong**。→ **改进/直接落地** V3 §4.2 #10 verifier_hooks。[§2.6]
5. **记忆投毒三连（MemoryGraft 2512.16962 + Sleeper 2605.15338 + Origin-Bound 2606.24322）**：伪造成功经验跨会话复用、sleeper AUR 60–89%、trust-label 传播规则。→ **改进** quarantine + valid_to。[§2.5]
6. **Claude-Code 原生 policy-as-code hooks（AGT 26.67%→0%、llm-rail exit2 覆盖 bypassPermissions、Sponsio LTL）**。→ **强支持** V3 §5（不改变 hooks 推迟时机）。[§2.1]
7. **leaf re-dispatch 事故 + maxDescendants（opencode #18100、oh-my-openagent PR）**。→ **改进** V3 §4.1（V3 只限 depth 缺总后代配额）。[§2.2]
8. **★ 技能库退化四连（全文已读）**：When Skills Don't Help（2605.20023，feedback-bandwidth 假说）+ Not All Skills Help/Assay（2606.15390，跨任务符号反转）+ More Skills Worse Agents（2605.24050，shadowing 主导非 context）+ SkillFlow（2604.17308，错误 skill 下游漂移、瓶颈是修复不是写入）。→ **部分反驳 V3 §4.2 预加载归因 + skill 重投入前提**，详见 §2.9。这是 v2 最重要的修正方向。

**★ v2 新增的"反驳 V3"核心结论（§2.9）**：
- **R1**：V3 §4.2"禁全量预加载"的理由写的是"撑爆上下文"，但 More Skills Worse Agents 实测**真正瓶颈是 skill shadowing（选错 skill，占总降 67%），context overhead 不显著**。V3 结论对、归因错——应改为"避免选择空间污染"。
- **R2**：V3 固定预加载一组 skill 给固定身份，但 Assay 证明**同一 skill 跨任务类型符号反转**（一任务帮、另一任务害，全局抵消看不见）；固定预加载假设"skill 对该身份所有任务非负"不成立。应把 skill 分 protected core / identity / **task-conditional（按任务 mask）**。
- **R3**：V3 在 Mie/COMSOL 物理域重投入 skill（6465 行），但 feedback-bandwidth 假说说**强确定性反馈域 skill 边际收益塌缩**（CTF 域 +8.9pp 不显著）；Mie 解析恰是高带宽反馈域——应**优先投 verifier/结构化工具反馈，skill 精简且验证驱动**。这是对 V3"skill 是核心资产"的实质性挑战。
- **R4**：V3 物理硬约束 verifier（铁律#1/#2）自身有局限——PINN silent failure（低 loss 解错）、soft constraint 不保证满足、consistency barrier、constraint 加多致 ill-conditioned（§2.10）。verifier 也要被验证（CertPINN 用 Lean 4 形式化）。

---

## §1 搜索方法与覆盖（v2）

**工具自检**：
- `exa_web_search_exa` + `exa_web_fetch_exa`：**主力**。语义搜索召回好，返回带 arXiv id/URL/摘要的真实来源；子 agent 用它成功拿到多篇 arXiv HTML 全文。
- `arxiv-mcp_search_arxiv`：**可用但召回差**（按 submittedDate 对泛词返回当日最新论文，噪声大）。已如实记录，arxiv 角度全靠 exa 间接命中。
- `academic-research_validate_citations`：10 条核心 arXiv id 全 `valid`。
- **`firecrawl_research_read_paper`**：子 agent 报告**因 API key 未授权不可用**（Unauthorized）。反驳论文全文阅读改用 `exa_web_fetch_exa` + `firecrawl_scrape` 成功完成。标 `unverified-tool`。

**v2 反驳论文全文阅读**（6 篇，并发子 agent，全部拿到 arXiv HTML 全文）：
| 论文 | arXiv | 全文 | 子 agent 判定 |
|---|---|---|---|
| When Skills Don't Help | 2605.20023 | ✅ | 部分反驳 V3 §4.2 + skill 重投入前提（强度中） |
| Not All Skills Help (Assay) | 2606.15390 | ✅ | 部分反驳固定预加载 + 六维裁决（中到强） |
| Library Drift | 2605.19576 | ✅v2 | 支持 V3 human gate，naïve governance 反噬（强度中） |
| Halt Authority | armalo 博客 | ✅ | 支持 V3 verifier+gate，强反驳无锚自迭代（中到强） |
| More Skills Worse Agents | 2605.24050 | ✅v2 | 反驳 V3"禁全量因上下文膨胀"归因（强度中） |
| SkillFlow | 2604.17308 | ✅ | 弱反驳自迭代，强支持 human gate/Archive-Fork |

**8 角度覆盖**（v1 已建）：1 护栏 / 2 递归 / 3 自改进 / 4 judge / 5 记忆 / 6 AI4S / 7 context / 8 human-gate。v2 加 §2.9 反驳专节 + §2.10 PINN 局限。

---

## §2 按角度分节的 findings

> §2.1–§2.8 为 v1 发现（已存，此处保留精炼版，细节见 v1）。§2.9–§2.10 为 v2 新增。

### §2.1 确定性护栏 / hooks-as-policy
- **F1.1 Microsoft AGT**（github, 2026-03）：prompt 级违反率 26.67% vs policy 层 0.00%；<0.1ms；OWASP Agentic Top 10 全 10 项。**强支持** 铁律#8 + V3 §5。
- **F1.2 Cupcake**（eqtylab, 2025-12）：CLAUDE.md/AGENT.md→OPA/Rego→Wasm；多 harness 含 Claude Code/OpenCode。**改进** V3 §5。
- **F1.3 Sponsio**（sponsio.dev, 2026）：NL→线性时序逻辑 LTL，FSM 求值 <0.01ms，零 LLM in hot path；**表达单事件 PreToolUse 表达不了的多步轨迹契约**。**改进** V3 §5（V3 三 hook 都是单事件）。
- **F1.4 Autoformalization PaC**（arXiv:2606.26649, 已校验）：NL prompt+MCP 定义→Cedar policy，generator-critic（hard parser + soft LLM-judge）。**改进** V3 §5（NL 红线→形式化 policy 不手写）。
- **F1.5 ILION**（arXiv:2603.13247, 已校验）：确定性 pre-execution 门，F1=0.85 vs Llama Guard 3 F1=0.01；"文本安全架构性不适用于动作治理"。**支持** 铁律#8。
- **F1.6 llm-rail**（neuradex, 2026-03）：Claude Code PreToolUse+`exit 2`，**覆盖 bypassPermissions**；workflow step 各自 policy+validation。**支持** V3 §5.1，消解 V3 §9.3 部分。
- **F1.7 Tessera / F1.8 agent-sentinel**：trust-label taint-tracking；budget 硬帽+ledger+replay+HITL。**改进** V3 失败防护（V3 缺 cost cap）。

### §2.2 多 agent 递归/编排失败
- **F2.1 AgentPatterns + opencode #18100**：47 session/20 层，depth 2–18 纯 pass-through 到 19 才跑 grep；leaf 去 Agent 工具是主导失败模式的解药。**强支持** V3 §4.1（C1）。
- **F2.2 supergood**：DeepMind 2025 末——无结构多 agent 误差放大 17.2×；Gartner 40%+ 项目 2027 被砍；硬 spawn budget + depth 2–3 **在编排层非 prompt**。**支持** 拓扑写死+铁律#8。
- **F2.3 Taming Zombie Agents**（ACL 2026）：zombie 态可恢复（Standby→Active），别永久 prune。**改进** V3。
- **F2.4 Tool Reentrancy**（tianpan）：reentrancy≠recursion；"调高 maxTurns = 把吵闹 bug 变安静 bug"；cycle detection before dispatch。**改进** V3 §9.3。
- **F2.5 hive #2082 + oh-my-openagent PR #2449**：unbounded 递归→RAM/DoS；修法 `trace_context` depth+path + MAX_RECURSION=5 + cycle detection；**`maxDescendants`（默认 3/50）+ fail-closed lineage**。**改进** V3 §4.1（V3 缺总后代配额）。
- **F2.6 subagentic Cascade-Fail + Agents of Chaos**：DoS cascade/"server destruction"；max retry 3–5 + 指数退避+jitter + per-boundary circuit breaker + cascade injection test。**改进** V3 失败防护。

### §2.3 自改进 agent 负面结果（v1 摘要，全文见 §2.9）
- **F3.1 Library Drift**（2605.19576，已在94，全文已读见§2.9.3）：naïve governance A4 -0.019 反噬；retirement+cap+prior → +0.328。**支持** 铁律#4。
- **F3.2 When Skills Don't Help**（2605.20023，全文已读见§2.9.1）：CTF 域 +8.9pp 不显著；feedback-bandwidth 假说。**部分反驳** V3 skill 重投入前提。
- **F3.3 Not All Skills Help/Assay**（2606.15390，全文已读见§2.9.2）：跨任务符号反转；judgment 生成、measurement 策展。**部分反驳** V3 固定预加载+六维裁决。
- **F3.4 Halt Authority**（Armalo，全文已读见§2.9.4）：无锚 76.5% 破坏；keep-best 门→0%。**改进** E-flow gate。
- **F3.5 Taste-Governed RSI**（Armalo）：8 闸门 promotion（metric binding/evidence/rollback/boundary/canary/multi-signal/authority restraint）；throughput-first 放行 13 不安全 vs taste 0。**改进** V3 六维裁决。
- **F3.6 Info-Theoretic Limits**（2603.28650，已校验）：classifier 安全门形式化不可能；sound verifier δ=0；效用差 5700×。**强支持** 铁律#1。
- **F3.7 Self-Harness**（2606.09498，已校验）：harness 自改进 + held-in/held-out regression-gated promotion。**改进** V3 接受规则（gap §0.2 G1）。
- **F3.8 SkillAxe**（2606.10546，已校验）：失败归因 skill vs execution。**改进** skill 退休。
- **F3.9 hermes #6051**：瞬态失败→learned helplessness；classify-before-persist + TTL。**改进** CAUTIONARY 经验。
- **F3.10 Evolvent 相变定律**：对数墙 + 局部竞争 [0.55,0.75) + god-tool 黑洞 20–35%。**改进** V3 §4.2。
- **F3.11 Kitchen Loop**（2603.25697）："Unbeatable Tests" + Drift Control pause gate；285 迭代零回归。**支持** 铁律#1/#2。
- **★ F3.12 GRASP**（arXiv:2605.29668，v2 新）：Gated Regression-Aware Skill Proposer；**held-out probe + hard regression budget（fixes > regressions 且无新 regression）+ bounded versioned reversible library + contrastive revision**；gpt-oss-120b 40.6%→88.8%；ablation 证明"无 validation 的 skill 写入 = 不如不用 skill"；frozen library 跨模型迁移（强模型写的 skill 帮弱模型，反之不行）。**改进** V3 E-flow 接受规则——这正是 V3 gap §0.2 G1（holdout+负迁移检测）的可操作实现。与 PACE（anytime-valid）互补：GRASP 管回归预算，PACE 管统计假阳性。
- **★ F3.13 SkillFlow**（arXiv:2604.17308，全文已读见§2.9.6）：lifelong skill evolution；Claude Opus 4.6 +8.43pp 但 Kimi K2.5 +0.60（usage 66.87%）、Qwen-Coder-Next regress；错误 skill 下游漂移；瓶颈是修复坏 skill 非写入。
- **★ F3.14 MASA / Skill is Not One-Size-Fits-All**（arXiv:2605.30723，v2 新）：**同一 skill 在一模型帮、另一模型害**；optimal granularity 跨模型不同；model-agnostic skill 可伤。**部分反驳** V3（V3 单 Claude 风险低，但若恢复 OpenCode 备选须重对齐 skill）。

### §2.4 LLM-as-judge / verifier gaming
- **F4.1 Gaming the Judge**（2601.14691，已校验）：只改 CoT→VLM-judge 假阳性 +90%。**改进** 铁律#1。
- **F4.2 Context Over Content**（2604.15224）：stakes signaling→leniency bias -9.8pp，CoT 审查测不到（ERR_J=0.000）。**改进** V3（judge 知道在 gate 自改进会放水）。
- **F4.3 One Token to Fool Judge**（OpenReview）：master keys（":"/"Thought process:"）→假阳性；General Verifier FPR 66.8%。**支持** 铁律#3。
- **F4.4 Evaluator Stress Test**（ACL 2026）：不变量 perturbation 检 proxy gaming；verbosity +40%。**改进** V3 verifier §4.2 #5。
- **F4.5 Security in LLM-as-Judge SoK**（2603.29403）：863 篇筛 45，taxonomy。**参考**。
- （Spec Gaming 2605.02269、LLMs Gaming Verifiers 2604.15149、Demonstrating 2502.13295 均在94。）

### §2.5 agent 记忆治理
- **F5.1 MemoryGraft**（2512.16962）：伪造成功经验跨会话复用（MetaGPT 实测）。**改进** quarantine + 铁律#5。
- **F5.2 Mnemonic Sovereignty**（2604.16548，已在94）：外源 pollution vs 内源 hallucination（confabulation during store）。**改进**——memory hallucination 是新失败类。
- **F5.3 Origin-Bound**（2606.24322，已在94，已校验）：非可锻 IFC；trust label 传播过自摘要/工具回声/伪造佐证三洗钱通道；Sybil-resistant elevation。**改进** V3 quarantine 缺 label 传播。
- **F5.4 Untrusted→Trusted Memory**（2606.04329，已在94，已校验）：False Precedent Insertion；HERCES 冻 memory 进 system prompt；weak-signal 攻击 prompt-injection 防御无效。**改进** 写回路径。
- **F5.5 Sleeper Memory**（2605.15338）：goal-adjacent 召回 94–98%，AUR Claude 60%→Gemini 89%。**改进** 铁律#5（时间炸弹）。
- **F5.6 TOKI**（2606.06240，已在94）：bitemporal algebra；LLM judge 在 write path 致 replay inconsistency/audit erasure。**改进** V3（别让 LLM judge 记忆写回）。
- **F5.7 Agent Memory Contamination**（tianpan）：dependency-tagged belief pruning + saga 补偿；24 点 short vs long gap。**改进** V3。
- **F5.8 Temporal Provenance**（Jatin Bansal）：valid_from/valid_to gating + staleness 非 recency + **provenance walk-up**（source 被纠→沿反向索引 revalidate 所有派生 claim）。**改进** V3 valid_to（gap §0.2 G1）。

### §2.6 AI-for-Science 复现验证
- **F6.1 PRBench**（2603.27646，已校验）：北大物理 30 任务/11 子领域；Codex/GPT-5.3 34%、**端到端回调 0%**；失败含**编造输出数据**。**强支持** 核心卖点+铁律#2。极高价值。
- **F6.2 ReplicationBench**（2510.24591，已校验）：天体物理 paper-scale；最强 <20%。**支持** 铁律#2。
- **F6.3 Collider-Bench**（2605.13950）：LHC；"论文省略实现细节"→触发人工输入；continuous metric + post-hoc validity judge。**改进** V3。
- **F6.4 NatureBench**（2606.24530）：information firewall；post-hoc judge 检 fabrication/feedback gaming；失败主导 wrong method choice 45.1%。**改进** V3 verifier。
- **F6.5 AutoExperiment**（2506.19724）：progressive masking；n 增大急降；Pass@1 vs Pass@5 gap→verifiers 重要。**支持** V3 verifier-driven。
- **F6.6 ClaroAI-Bench**（bioRxiv）：5 维 rubric 含 environment reconstructability；r=0.68 预测 D5。**改进** V3 执行真实性分级（gap §0.2 G2）。
- **F6.7 FABRIC**（2606.25879）：**评科学结论非精确数值**；4–6× 降工作量；AI 不擅缺清晰 workflow 的分析阶段。**改进** V3 result_class。
- **F6.8 IFS / Wrong Physics**（2605.09360，已在94，全文新核）：MOOSE Kernel/BC→weak-form 反推 PDE 与意图契约比；IFS；**39–40% runnable-but-wrong**；扩展 UFL/FEniCS/FreeFEM/FiPy/Devito。**改进/直接落地** V3 §4.2 #10。
- **F6.9 COMSOL agent 护栏 + MMS**：sim-plugin-comsol/sim-cli/comsol-project-guardrails + COMSOL MMS blog + ORNL V&V。**改进** V3 COMSOL skill + verifier（MMS 是物理硬约束 verifier 新增手段）。

### §2.7 context preload vs lazy-load
- **F7.1 Anthropic Context Engineering**（2025-09）：JIT + lightweight identifiers；bloated tool sets→模糊决策。**支持** V3 §4.2 per-identity preload。
- **F7.2 Context Budget Allocation**（AgentPatterns）：Claude Code skill desc = 1% window / 8000 char fallback；n² attention；sub-agent 隔离。**改进** V3 §9.3-3（量化）。
- **F7.3 JIT vs AOT**（Jatin Bansal）：prefetch vs demand-paging 类比；AOT 失败=attention dilution，JIT 失败=tool-loop drift；**no-progress detector（两次相同工具调用=abort）**。**改进** V3 §9.3。
- **F7.4 Factory Deferred Context Engine**（2026-05）：20–50 tools 减 21%，100+ 减 50.8%。**改进** V3。
- **F7.5 Lazy-Loaded Prompt Engineering**（gopubby）：20 skills≈2000 token；切 skills 降 35%；100+→dilute。**改进** V3 §4.2。
- **F7.6 Two Context Bloat Problems**（Agenteer/TrueFoundry）：tool-definition bloat=Skills/progressive disclosure；tool-result bloat=Subagent。**支持** V3 §4.2+§7。

### §2.8 human-in-the-loop gate
- **F8.1 Self-Modification Diff Gate**（agentpatternscatalog）：独立 critic（frozen base model）审自改 diff；同模型自审 rationalise。**改进** V3 自迭代（V3 缺自动 separate-critic 前置门）。
- **F8.2 Yohei Nakajima**（2025-12）：conservative acceptance（SICA benchmark 提升才留）；off-switches/review gates/policy filters。**支持** V3 human gate。
- （Halt Authority/Taste-Governed RSI/Info-Theoretic Limits/Self-Harness 见 §2.3 + §2.9；PACE 2606.08106 在94。）

---

### §2.9 ★ 反驳 V3 假设的论文——6 篇全文阅读专节（v2 新增）

> 6 篇经并发子 agent 下载 arXiv HTML 全文阅读，每篇给出"是否反驳 V3 + 强度 + 与 V3 真实关系"。这是 v2 的核心增量。

#### §2.9.1 When Skills Don't Help（arXiv:2605.20023）— 部分反驳 V3 skill 重投入前提

**全文已读**（子 agent，exa_web_fetch_exa 拿到 arXiv HTML 全文）。

- **核心主张**：重分析 180-run MCP-grounded CTF agent，4 条件（No-Skills 55 行→Comprehensive 4147 行）。Comprehensive vs No-Skills 仅 **+8.9pp（χ² p=0.71，Cochran-Armitage p=0.25，不显著）**；5/6 pairwise Cohen's h <0.2 small-effect。timing-side-channel 子任务 Comprehensive 反而更差（1/3 vs Curated 2/3）。
- **feedback-bandwidth 假说（精确）**：curated Skills 的边际收益与 agent 可获得的 **deterministic environment feedback bandwidth** 成反比；带宽=determinism × schema fidelity × latency。环境给严格 schema 化低延迟可验证观察时，环境本身提供 Skills 通常负责的 procedural correction signal → Skills 边际收益塌缩。
- **是否反驳 V3 §4.2 预加载有价值**：**部分反驳**（强度中）。挑战"预加载更多 procedural knowledge 通常有益"默认假设；但 V3 是人工身份分工+verifier 组合，非 CTF 那种附加文档——是设计风险证据非铁律推翻。
- **是否反驳"物理域该重投入 skill"**：**部分反驳**（关键）。Mie 解析/半解析确是高带宽反馈域（能量守恒/Rayleigh/large-size/论文图量化密集 verifier）；按假说**越这种域越该优先投 verifier/结构化工具/自动检查脚本，而非无限扩 skill 文本**。但 COMSOL 非完全高带宽（solver 报错/Java tag/参数缺失/网格 shift 反馈稀疏昂贵非结构化）→ skill 仍能编码环境不给的 convention。结论：**重投 verifier 优先，skill 精简且验证驱动**，非"物理域不需要 skill"。
- **量化**：77.8%→86.7%（+8.9pp n.s.）；token 成本 Comprehensive≈75× No-Skills。
- **可信度**：中（180-run 受控，但 15 challenge、单 CTF 域、单模型 Sonnet 4.5、workshop/arXiv）。
- **与 V3 真实关系**：更像反驳"自动技能库/大而全无条件有效"，非直接反驳 V3。**启示**：别把 6465 行 skill 当核心资产，核心资产应是 verifier+结构化执行环境+失败样例+人筛短 skill；建 ablation（无/精简/全量 skill）以物理复现成功率/误报率/token/人审成本衡量。

#### §2.9.2 Not All Skills Help / Assay（arXiv:2606.15390）— 部分反驳固定预加载 + 六维裁决

**全文已读**（子 agent，exa 拿 arXiv HTML 全文）。

- **核心主张**：skill library 存在普遍 **causal heterogeneity**——同一 skill 跨任务类型**符号反转**（一任务帮、另一任务害），正负在全局均值抵消，全局 curation 看不见。7 模型/4 provider/2 benchmark（AppWorld、τ-bench）。**judgment generates skills, measurement curates them**——生成靠 LLM judgment，保留/合并/分叉必须靠跨任务 empirical measurement。
- **per-skill randomized masking 因果归因**：dev set 上 K=12 随机 mask，每 skill Bernoulli f=0.4；$C[j,i]=E[o|s_j included]-E[o|s_j excluded]$；row range H(s_j) 高且均值≈0 是最危险（正负抵消看不见）。
- **关键数字**：GPT-5.1/AppWorld 103 skills 中 >90% per-task causal range >0.40；**uncurated library 使 test_challenge 52.5%→49.9%（退化 2.6pp）**；DeepSeek-V3 经 Assay 47.0%→69.3%（+47.4%相对）；反转实例：contact validation rule 全局 -0.03 但 shared-expense +0.50/single-app -0.67。
- **是否反驳 V3 六维裁决足够**：**部分反驳偏强**。若六维裁决 skill 退休/合并/分叉是定性判断，Assay 明确反驳"定性足够"；不否定裁决本身，但要求裁决输入含 per-skill per-task 经验测量。
- **是否反驳"固定预加载一组 skill"**：**反驳（中到强）**。固定预加载=假设 skill 对该身份所有任务非负；实验证伪。AppWorld GPT-5.1 uncurated 直接退化。同一 skill 跨任务反转 → task-conditional skill 被错当 identity-constant。
- **反驳强度**：中到强。
- **可信度**：高（arXiv 全文 + 跨模型跨 benchmark + 代码开源 github.com/aiming-lab/assay）。
- **与 V3 真实关系**：不反驳"人工 skill"本身（论文自己也加 5 个 hand-written protected templates）；反驳"仅靠人工/LLM 定性判断即可完成 skill 生命周期"。**对 V3 启示**：skill 分 protected core / identity-level / **task-conditional（按任务 mask 或触发）**；前两类固定预加载，第三类必须按任务检索/mask；六维裁决引入"跨任务是否反转"量化维。

#### §2.9.3 Library Drift（arXiv:2605.19576）— 支持 V3 human gate，naïve governance 反噬（已在94，全文新核）

**全文已读**（子 agent，exa+firecrawl 拿 v2 HTML 全文+附录）。

- **核心主张**：library drift=skill 无界累积无 outcome-driven lifecycle → 检索退化/错误注入/低于 no-skill baseline，**silent**（无显式错误信号）。问题不在 author 在 librarian。
- **A4 harsh retirement 反噬**：N_min 100→20、τ 0.10→0.0 → **gain -0.019±0.010（低于 baseline）**，3 seed 一致（-0.005/-0.027/-0.025）；library 崩到 2 active，router 19%。"naïve governance can be worse than none"。
- **Default（retirement+cap+authoring prior）**：0.258→late 0.584，gain +0.328。
- **是否反驳 V3 E-flow 改 skill**：**部分反驳**（强度中）。不反驳"skill 可改进/演化"（证明治理良好可 +0.328）；反驳"agent 自动攒、缺生命周期证据、缺 human gate"。
- **是否支持 V3 铁律#4**：**支持强**。SkillsBench：LLM-authored +0.0pp vs human-curated +16.2pp。
- **V3 受影响**：中等，非根本推翻。V3 人工写死+human gate+只碰经验层+Archive/Fork+不改拓扑 缓解了主要风险；需补：从第一轮就保 version lineage（别等跑通）、per-skill evidence、active cap、retire 证据门槛、Archive 优先于 Delete。
- **可信度**：高（全文+附录；限：MBPP+ hard-100、Opus 4.7、3 seed）。
- **94 关系**：Lane 1 已收；增量=A4 反噬细节、A5/A6 dedup 不必要、A7 cap=100 方差增、A8 meta refresh 收益有限成本高。

#### §2.9.4 Halt Authority（Armalo，2026-06-16）— 强反驳无锚自迭代，支持 V3 verifier+gate

**全文已读**（子 agent，exa+firecrawl 拿全文 markdown）。

- **实验**：17 个 Phase A 验证正确产物（每题 7–11 确定性约束 all-pass），Phase B 同模型"keep improving"3 轮，两臂唯一差异=success criteria 是否在视野。
- **核心数字**：**Unanchored 13/17（76.5%）破坏，Anchored 0/17（0%），exact McNemar p=0.000244**；survival 17→6→5→4；已正确字段被编辑率 57%；23 次 damaging revision 翻坏 80 个 passing constraint；**自审 40 次仅 4 次（10%）声明 compliant，且分不清刚破坏的轮次**；**keep-best promotion gate→两臂 self-damage 0%**。
- **external halt authority 精确定义**：external verifier that both **defines done** and **vetoes regressions**；形式=deterministic checker/oracle/independent verifier seat，**不能是作者模型自审**。
- **是否反驳 V3 自迭代价值**：**部分，总体更偏支持 V3 治理**。反驳"无锚/latest-wins/criteria 不可见"自改进；不反驳"agent 提候选"（候选生成有探索价值）。**关键**：V3 human gate + deterministic verifier 若定义 done 且 veto regression = 算外部锚；若只让 agent 自评"更好" = 不算。
- **keep-best 门机制**：持续保存"最高 externally-verified score"候选；新 revision 低于 best-so-far 则丢弃；单调防回退，仍允许探索。
- **支持 V3 铁律#1/#2**：明确——self-audit 不能 referee 自己的 loop。
- **反驳强度**：中到强（对无锚自改进强；对带 verifier+gate 的 V3 E-flow 是支持证据）。
- **可信度**：中（n=17、单实验室、单模型 MiniMax-M3、Phase A 429 限流致样本 40→17、Unanchored 文本更短有未排除 context-length confound）。

#### §2.9.5 More Skills, Worse Agents / Skill Shadowing（arXiv:2605.24050）— 反驳 V3"禁全量因上下文膨胀"归因

**全文已读**（子 agent，exa+firecrawl 拿 v2 HTML 全文 + Table 1/2/4/5/6/10）。

- **核心主张**：库扩大性能降主因**不是上下文变长，是 skill shadowing（选错/漏选/被相似 skill 替代）**。202-skill 降 21%（CI [0.15,0.27]）。
- **分解**：202-skill 时 $\Delta_{shd}=0.14$（CI [0.06,0.26]，**占总降 ~67%**）vs $\Delta_{ctx}=0.07$（CI [-0.13,0.25]，**不显著、indistinguishable from zero**）。oracle-only 轨迹 88.0%→52.6%，no-skill-invoked 12.0%→38.5%。
- **是否反驳 V3"禁全量预加载因上下文膨胀"归因**：**部分反驳（中）**。V3 结论"禁全量"对（甚至增强），但**理由错**——应从"上下文膨胀"改为"选择空间污染+skill shadowing+相似 skill 路由失败"。注意：未证 context overhead 不存在，只该规模不显著。
- **是否反驳"小而精固定 skill 集"**：**不反驳，支持**。小库/oracle set 优于大库；V3 每身份预加载=缩小候选空间减 shadowing。
- **对 V3 §4.2 启示**：保留"禁全量预加载"，改理由；领域 skill 保持少量、边界清晰、描述互斥；skill 增多需显式 routing/retrieval/pre-filter 而非全暴露。
- **量化**：SkillsBench；Haiku 4.5/Sonnet 4.6；38 task-model pairs、2545 轨迹；52/102/202 skill。
- **可信度**：高（全文；限：单 benchmark、两同厂模型、202 skill 规模）。

#### §2.9.6 SkillFlow（arXiv:2604.17308）— 弱反驳自迭代，强支持 human gate/Archive-Fork

**全文已读**（子 agent，firecrawl 拿 HTML v1 全文，定向核实 Finding 2/6 + Table 1）。

- **核心主张**：lifelong skill evolution benchmark，166 任务/20 family。Claude Opus 4.6 62.65%→71.08%（+8.43pp）；**Kimi K2.5 usage 66.87% 但仅 +0.60pp**；**Qwen-Coder-Next 44.58%，-0.60pp regress**；"high usage ≠ high utility"。
- **Finding 2（精确）**：incorrect skills create **systematic downstream drift**——一旦错误 skill 入库，后续任务继承同一 flawed abstraction，局部错变序列级模式；"external skills can amplify capability, can also amplify error"。
- **Finding 6（精确）**：key model gap is **repairing bad skills, not writing skills**——多数模型能写 skill，差异在能否识别/修订错误 skill 并在后续获更好行为；positive transfer 与有效 skill repair 相关性强于 skill volume。
- **是否反驳 V3 E-flow 价值**：**弱**。支持核心假设（经验层 skill evolution 有效，Opus +8.43）；反驳无约束自迭代（错误 skill 下游漂移、usage≠utility）。
- **是否支持 V3 human gate/Archive-Fork/小而可修复库**：**强支持**。Finding 2→human gate 阻错误入主库；Archive/Fork→版本谱系回滚分叉；Finding 6→瓶颈是 repair 非 volume，小库更利定位修补验证。
- **与 V3 真实关系**：是 V3 风险证据+治理依据，非反例。**提醒**：E-flow 价值不在"自动产出更多 skill"，在"基于失败证据识别/隔离/修补坏 skill"。
- **可信度**：高（全文）。

#### §2.9 反驳专节小结

| 论文 | 反驳对象 | 强度 | V3 真实受影响 |
|---|---|---|---|
| When Skills Don't Help | skill 重投入前提 / 物理域该重投 skill | 中 | V3 应 verifier 优先、skill 精简验证驱动 |
| Not All Skills Help | 固定预加载 + 定性六维裁决 | 中到强 | skill 分层，task-conditional 按 mask；裁决加量化维 |
| Library Drift | 无约束自动攒 + naïve governance | 中 | V3 human gate 已缓解；补 version lineage/active cap |
| Halt Authority | 无锚自迭代 / latest-wins / 自审 | 中到强 | V3 verifier+gate 算锚=支持；keep-best 门直接落地 |
| More Skills Worse Agents | "禁全量因上下文膨胀"归因 | 中 | 结论对、理由改"shadowing 非 context" |
| SkillFlow | 自迭代普遍有效 | 弱 | 强支持 human gate/Archive-Fork/repair-first |
| ★ MASA（§2.3 F3.14）| skill 模型无关 | 中 | V3 单 Claude 风险低；恢复 OpenCode 须重对齐 |
| ★ GRASP（§2.3 F3.12）| （改进非反驳）held-out regression budget | — | 直接落地 V3 gap §0.2 G1 |

**反驳带来的 V3 修正（核心）**：
- **R1（理由修正）**：V3 §4.2"禁全量预加载（撑爆上下文）"→ 改"避免 skill shadowing / 选择空间污染"（More Skills Worse Agents）。
- **R2（结构修正）**：V3 固定预加载→分 protected core / identity / task-conditional；第三类按任务 mask（Assay）。
- **R3（前提修正）**：V3"skill 是核心资产"→ 改"verifier+结构化执行环境是核心，skill 精简验证驱动"（feedback-bandwidth）；Mie 解析优先投 verifier。
- **R4（verifier 自审）**：物理硬约束 verifier 自身有 silent failure，需形式化/独立验证（§2.10）。

---

### §2.10 ★ 物理约束 verifier 自身局限（PINN silent failure）— v2 新增

> 这批论文不直接反驳 V3，但**警告 V3 铁律#1/#2"物理硬约束交叉验证"自身有失效模式**——verifier 也要被验证。V3 的 Mie 工作虽以解析/半解析为主（非 PINN），但若未来用 PINN/数值求解器做 COMSOL 辅助验证，这批风险直接相关。

- **F2.10.1 Krishnapriyan et al. "Characterizing PINN Failure Modes"（NeurIPS 2021，OpenReview a2Gr9gNFD-J）**：PINN soft regularization（PDE 残差当 loss penalty）在稍复杂问题就失败；**不是架构表达力不足，是 loss landscape 难优化**；soft constraint 使问题更 ill-conditioned。→ **部分反驳 V3"物理约束加得越多越好"**——soft constraint 形式的物理验证会 ill-condition。解法：curriculum regularization + seq2seq。
- **F2.10.2 "PINNs Failure Modes are Overfitting"（arXiv:2605.30910）**：PINN 失败的未诊断原因=**overfitting**——loss 只在 collocation points 最小化，区域高残差，"well converged to the wrong solution"；train/test loss 分离。处方=regularization。→ **支持 V3"低 loss≠正确"**（铁律#2），且给机制名（overfitting at collocation points）。
- **F2.10.3 "When PINNs Go Wrong: Pseudo-Time Stepping"（arXiv:2604.23528）**：训练看似稳定但预测物理错；PINN 倾向收敛到 **trivial/spurious solutions**；固定 collocation points 时 landscape 含多个 poor global minima；spectral bias 偏好 spurious；**关键局限：性能对 τ 高度敏感，且不同 τ 的 training loss 高度相似但解质量差很大——无法靠监控 loss 选 τ**。→ **强支持 V3"loss 不可作完成判据"**，且"仅 loss 可访问时无法调参"= V3 必须独立物理判据。
- **F2.10.4 "Consistency Barrier in PINNs"（arXiv:2602.10611，2026-02）**：数据与 PDE 不一致（噪声/离散化/建模假设）→ **consistency barrier**（误差固有下界）；PDE 残差只能部分缓解低 fidelity 数据，最终饱和于 inconsistency 决定的误差；高 fidelity 数据时 barrier 消失。→ **改进 V3**：物理约束 verifier 的精度有数据-fidelity 上限，别指望残差能无限小。
- **F2.10.5 CertPINN（OpenReview F0ag4Np9Ks）**：PINN 无形式正确性保证；silent convergence to spurious solutions 在安全关键域不可忍；提出 **Lean 4 dependent type theory 形式化验证 PDE 弱解**，machine-checkable certificate，3–7% overhead。→ **改进 V3**：verifier 也可形式化验证（对齐铁律#1 的"sound verifier"，与 Info-Theoretic Limits F3.6 呼应）。
- **F2.10.6 hPINN / KKT-hPINN（arXiv:2402.07251）**：soft constraint 不保证物理满足（mass balance 违反 ~10⁻³ vs hard ~10⁻⁷）；"hard constraint" 实现常靠 trial-and-error 调参，不严格。→ **改进 V3**：物理硬约束要做成 hard constraint（正交投影/QP），别靠 penalty。
- **F2.10.7 Gradient Pathology / CAML（arXiv:2605.25001）**：PDE 残差梯度与边界约束梯度冲突方向→局部极小；operator non-uniqueness 致 minimizer 流形→ill-conditioned valley；CAML 修 landscape 几何。→ **改进 V3**：物理约束加多会致梯度冲突，需 alignment。
- **F2.10.8 PINN with Dynamical Boundary Constraints（arXiv:2507.21800，2025-07）**：低 loss 但预测错；多尺度/强振荡尤甚；DBC 基于 prior training 限 loss。→ 支持 V3 silent failure 警告。

**§2.10 小结**：V3 铁律#1/#2（物理硬约束交叉验证）方向对，但**物理约束 verifier 自身有 silent failure（低 loss 解错）、soft constraint 不保证、consistency barrier、constraint 加多 ill-conditioned**。落地时：(a) 物理约束做成 hard constraint 而非 soft penalty；(b) verifier 也要独立验证（CertPINN 式形式化 / MMS / 同构扰动）；(c) 别用 loss/残差当完成判据；(d) Mie 解析路线（解析公式+教材极限）比 PINN 更适合做 ground-truth verifier——V3 现选解析路线本身就在规避这批风险，是正确选择。

---

## §3 对 V3 的具体建议（v2 修正版）

### §3.1 值得纳入 V3（按价值序，★=v2 修正/新增）

1. **IFS / 物理契约反推（F6.8）→ V3 §4.2 #10 verifier_hooks**：MOOSE Kernel/BC→weak-form 反推迁移到 COMSOL Java tag 反推；39–40% runnable-but-wrong。**改进**。
2. **PRBench（F6.1）→ V3 核心卖点论证 + baseline（gap §0.2 G2）**：34%/0% 是硬锚；"编造输出数据"对应假完成。**支持**。
3. **Info-Theoretic Limits（F3.6）→ 铁律#1 数学正当性**：classifier 安全门形式化不可能。**强支持**。
4. **★ keep-best 晋升门 + hard regression budget（F3.4 Halt + F3.12 GRASP）→ V3 E-flow gate**：把六维裁决（定性）升级为 keep-best promotion（确定性，低于已证最佳不 commit）+ GRASP 的 held-out probe + hard regression budget（fixes>regressions 且无新 regression）+ contrastive revision。属跑通后（gap §0.2 G1 的可操作化）。**改进**。
5. **maxDescendants 配额（F2.5）→ V3 §4.1**：补总后代 cap + fail-closed lineage。低成本。**改进**。
6. **记忆 trust-label 传播 + walk-up 作废（F5.3+F5.8）→ V3 valid_to（gap §0.2 G1）**：Origin-Bound 三洗钱通道闭合 + Bansal source→dependents 反向索引。**改进**。
7. **Sleeper/MemoryGraft（F5.1/F5.5）→ V3 quarantine 写回路径**：EXTERNAL SourceClass 默认低置信 + compaction filter。**改进**。
8. **policy-as-code hooks 工具链（F1.1–F1.6）→ V3 §5 落地选型**：AGT/Cupcake/llm-rail/Sponsio/Autoformalization。**强支持+改进**（不改变推迟时机）。
9. **★ skill 分层 + per-skill 因果归因（F3.3 Assay + F3.10 Evolvent + §2.9.2）→ V3 §4.2 + 六维裁决**：skill 分 protected core / identity / task-conditional；第三类按任务 mask；退休前做 per-skill randomized masking 归因；引入"跨任务是否反转"量化维。**改进（反驳驱动）**。
10. **★ V3 §4.2"禁全量预加载"理由修正（§2.9.5 More Skills Worse Agents）**：理由从"上下文膨胀"改为"skill shadowing/选择空间污染"；领域 skill 少量、边界清晰、描述互斥。**改进（反驳驱动）**。
11. **★ V3"skill 是核心资产"前提修正（§2.9.1 feedback-bandwidth）**：Mie 解析高带宽反馈域→优先投 verifier/结构化工具/自动检查脚本，skill 精简验证驱动；建 ablation 无/精简/全量 skill。**改进（反驳驱动，重要）**。
12. **COMSOL agent 护栏 + MMS（F6.9）→ V3 COMSOL skill + verifier**：MMS 作物理硬约束 verifier 新增手段。**改进**。
13. **cascade 控制（F2.6）→ V3 失败防护**：退避+jitter + per-boundary 断路器 + cascade injection test。**改进**。
14. **★ 物理约束 verifier 形式化/hard-constraint（§2.10）→ V3 铁律#1/#2 落地**：物理约束做 hard constraint 非 soft penalty；verifier 也独立验证（CertPINN Lean/MMS/同构扰动）；Mie 解析路线本身就是规避 PINN silent failure 的正确选择——保持。**改进**。

### §3.2 是噪声 / 与 V3 无关（丢弃）
- arxiv-mcp 当日最新论文（WorldDirector/Align4D/Program-as-Weights 等）：噪声。
- "What LLM Agents Say When No One Is Watching"（多 agent 辩论社会结构）：V3 flat fan-out 不适用。
- LACUNA（unlearning）、Distributed Attacks in Persistent-State AI Control（PR 级）：无直接映射。

### §3.3 需进一步核（unverified）
- **产品性能数字**（Sponsio/Tessera/agent-sentinel/Cupcake/AGT 的 <0.01ms、26.67%→0%、17.2×）：未独立复现，落地前自测。标 `unverified-claim`。
- **Evolvent 相变定律**：厂商研究方法未全公开；方向可信、阈值待复现。`unverified-number`。
- **Halt Authority/Taste-Governed RSI**：n=17/32 单实验室；方向强、数字待独立复现。`medium`。
- **V3 §5.5 agent-frontmatter PreToolUse 阻断自身调用**：llm-rail（F1.6）用全局 exit 2 覆盖 bypassPermissions，但 **agent 级 scoped** 精确组合仍未单独验（与 V3 §9.3-1 一致）。
- **PRBench 是否含光学/Mie 子任务**：未查 task-level 明细。
- **★ feedback-bandwidth 假说是否真能外推到 Mie/COMSOL**：论文自限单 CTF 域；Mie 解析是高带宽但 COMSOL 不是——需 V3 自己做 ablation 验证（无 skill/精简 skill/全量 skill 的物理复现成功率对比）。
- **★ firecrawl_research_read_paper API key 不可用**：本次反驳论文全文靠 exa+firecrawl_scrape 完成，未用该工具；下次若需 paper 全文检索须先修 API key。

---

## §4 完整来源清单（可追溯，全部本会话真实 fetch）

### arXiv（已过 OpenAlex/CrossRef 校验）
- PRBench — arXiv:2603.27646 (2026) — `arxiv.org/abs/2603.27646`
- ReplicationBench — arXiv:2510.24591 (2025-10)
- Origin-Bound Authority — arXiv:2606.24322 (2026)
- Untrusted→Trusted Memory — arXiv:2606.04329 (2026)
- Autoformalization PaC — arXiv:2606.26649 (2026-06)
- ILION — arXiv:2603.13247 (2026-02)
- Self-Harness — arXiv:2606.09498 (2026)
- Not All Skills Help/Assay — arXiv:2606.15390 (2026)
- SkillAxe — arXiv:2606.10546 (2026)
- Gaming the Judge — arXiv:2601.14691 (2026-01)

### arXiv（exa/firecrawl 子 agent 全文阅读）
- When Skills Don't Help — arXiv:2605.20023 (2026) — `arxiv.org/html/2605.20023v1` 【全文✅】
- Not All Skills Help/Assay — arXiv:2606.15390 — `arxiv.org/html/2606.15390` 【全文✅】
- Library Drift — arXiv:2605.19576 — `arxiv.org/html/2605.19576v2` 【全文✅v2】
- More Skills, Worse Agents — arXiv:2605.24050 (2026-06-23) — `arxiv.org/html/2605.24050v2` 【全文✅v2】
- SkillFlow — arXiv:2604.17308 — `arxiv.org/html/2604.17308v1` 【全文✅】
- GRASP — arXiv:2605.29668 — `arxiv.org/html/2605.29668` 【摘要✅】
- MASA — arXiv:2605.30723 — `arxiv.org/html/2605.30723` 【摘要✅】
- Info-Theoretic Limits — arXiv:2603.28650 — `arxiv.org/pdf/2603.28650`
- MemoryGraft — arXiv:2512.16962 (2025-12)
- Mnemonic Sovereignty — arXiv:2604.16548 [已在94]
- Sleeper Memory — arXiv:2605.15338
- TOKI — arXiv:2606.06240 [已在94]
- LLMs Gaming Verifiers — arXiv:2604.15149 [已在94]
- Spec Gaming — arXiv:2605.02269 [已在94]
- Demonstrating spec gaming — arXiv:2502.13295 (2025-02) [已在94]
- Context Over Content — arXiv:2604.15224 — `arxiv.org/pdf/2604.15224`
- Security in LLM-as-a-Judge SoK — arXiv:2603.29403
- One Token to Fool Judge — OpenReview cXMZbIBR1T
- Collider-Bench — arXiv:2605.13950
- NatureBench — arXiv:2606.24530
- AutoExperiment — arXiv:2506.19724
- FABRIC — arXiv:2606.25879
- IFS / Wrong Physics — arXiv:2605.09360 [已在94, 全文✅]
- Kitchen Loop — arXiv:2603.25697
- Evaluator Stress Test — ACL 2026 findings.513
- Taming Zombie Agents — ACL 2026 long.373
- ClaroAI-Bench — bioRxiv 2026.05.08.723611

### §2.10 PINN 失败模式（v2 新）
- Krishnapriyan "Characterizing PINN Failure Modes" — NeurIPS 2021 / OpenReview a2Gr9gNFD-J — `openreview.net/forum?id=a2Gr9gNFD-J`
- PINNs Failure Modes are Overfitting — arXiv:2605.30910 — `arxiv.org/html/2605.30910v1`
- When PINNs Go Wrong: Pseudo-Time Stepping — arXiv:2604.23528 — `arxiv.org/html/2604.23528`
- On Consistency Between Physics and Data in PINNs — arXiv:2602.10611 (2026-02) — `arxiv.org/pdf/2602.10611`
- CertPINN — OpenReview F0ag4Np9Ks — `openreview.net/attachment?id=F0ag4Np9Ks`
- hPINN / KKT-hPINN — arXiv:2402.07251 — `arxiv.org/html/2402.07251v1`
- CAML / Gradient Pathology — arXiv:2605.25001 — `arxiv.org/html/2605.25001`
- PINN with Dynamical Boundary Constraints — arXiv:2507.21800 (2025-07)

### Web / 工程 / 博客
- Microsoft AGT — `github.com/microsoft/agent-governance-toolkit` (2026-03)
- Cupcake — `github.com/eqtylab/cupcake` (2025-12)
- Sponsio — `sponsio.dev`
- Tessera — `github.com/kenithphilip/Tessera` (2026-04)
- llm-rail — `github.com/neuradex/llm-rail` (2026-03)
- agent-sentinel — `github.com/agent-sentinel/agent-sentinel-sdk` (2025-12)
- AgentPatterns Recursive Sub-Agent — `agentpatterns.ai/multi-agent/recursive-sub-agent-delegation-depth/`
- opencode #18100 — (引于 AgentPatterns)
- supergood — `supergood.solutions/blog/future-friday-recursive-multi-agent-risks-2026/` (2026-03)
- tianpan Tool Reentrancy — `tianpan.co/blog/2026-04-28-tool-reentrancy-recursive-evaluator-cycle-detection`
- aden-hive #2082 — `github.com/adenhq/hive/issues/2082` (2026-01)
- oh-my-openagent PR #2449 — `github.com/code-yeongyu/oh-my-openagent/pull/2449` (2026-03)
- subagentic Cascade-Fail — `subagentic.ai/howtos/how-to-design-multi-agent-pipelines-that-dont-cascade-fail/` (2026-02)
- hermes #6051 — `github.com/NousResearch/hermes-agent/issues/6051` (2026-04)
- Evolvent — `evolvent.co/en/research/agent-physics-skill-part1` (2026-04)
- Armalo Halt Authority — `armalo.ai/labs/research/2026-06-16-halt-authority-external-anchor` (2026-06-16) 【全文✅】
- Armalo Taste-Governed RSI — `armalo.ai/labs/research/2026-06-13-taste-governed-rsi-amendment-loop` (2026-06-13)
- Yohei Nakajima — `yoheinakajima.com/better-ways-to-build-self-improving-ai-agents/` (2025-12)
- Self-Modification Diff Gate — `agentpatternscatalog.org/patterns/inner-critic/` (2026-05)
- Anthropic Context Engineering — `anthropic.com/engineering/effective-context-engineering-for-ai-agents` (2025-09)
- AgentPatterns Context Budget — `agentpatterns.ai/context-engineering/context-budget-allocation/`
- Jatin Bansal JIT vs AOT — `jatinbansal.com/ai-engineering/context-engineering-jit-vs-aot/` (2026-05)
- Jatin Bansal Temporal Provenance — `jatinbansal.com/ai-engineering/temporal-reasoning-provenance/` (2026-05)
- Factory Deferred Context Engine — `factory.ai/news/deferred-context-engine` (2026-05)
- gopubby Lazy-Loaded — `ai.gopubby.com/how-lazy-loaded-prompt-engineering-is-becoming-the-standard-pattern-...` (2025-12)
- Agenteer Two Bloat — `agenteer.com/blog/the-two-context-bloat-problems-...` (2026-01)
- TrueFoundry Context Engineering — `truefoundry.com/docs/ai-gateway/agent-harness/context-engineering/overview`
- tianpan Memory Contamination — `tianpan.co/blog/2026-05-05-agent-memory-contamination-tool-response-poison` (2026-05)
- GenAlphAI Memory Poisoning — `genalphai.com/agent-memory-poisoning-defense-and-rollback/` (2026-06)
- sim-plugin-comsol — `github.com/svd-ai-lab/sim-plugin-comsol` (2026-04)
- sim-cli — `github.com/svd-ai-lab/sim-cli` (2026-05)
- comsol-project-guardrails — `github.com/HZ-KMNO/comsol-project-guardrails`
- COMSOL MMS Blog — `comsol.com/blogs/verify-simulations-with-the-method-of-manufactured-solutions/`
- ORNL V&V COMSOL — `info.ornl.gov/sites/publications/Files/Pub151765.pdf`
- Stanford HAI 2026 AI Index — `hai.stanford.edu/ai-index/2026-ai-index-report/science`

---

## §5 诚实边界（v2）

**搜够的角度**：1 护栏、3 自改进（含 6 篇全文）、5 记忆、6 AI4S、§2.9 反驳专节、§2.10 PINN。

**没搜够**：
- 角度 2 递归：证据多博客/issue 非同行评审（Agents of Chaos 未直接 fetch 全文）。
- 角度 4 judge：SoK 只读摘要。
- 角度 7 context：工程博客为主，缺"preload vs lazy 对 agent 成功率"受控实验。
- **物理光学（Mie/plasmonics）专用 agent 复现文献几乎不存在**（PRBench 含物理子领域但非光学专用，未核 task 明细）。

**工具局限**：
- `arxiv-mcp_search_arxiv` 按 submittedDate 对泛词召回差（噪声大）。
- **`firecrawl_research_read_paper` API key 不可用**（子 agent 报告 Unauthorized），反驳论文全文靠 exa_web_fetch_exa + firecrawl_scrape 完成。下次须先修。
- 未做引用图二跳遍历。

**反驳论文全文阅读可信度**：6 篇全部拿到 arXiv HTML 全文（含附录/表格），子 agent 判定可信度高；其中 Halt Authority/Taste-Governed RSI 为博客受控实验（n 小、单实验室），SkillFlow/More Skills Worse Agents/Assay/When Skills Don't Help 为 arXiv 全文含跨模型跨 benchmark。MASA/GRASP 仅摘要级。

**confidence 分级**：标"高"=arXiv 全文+benchmark 或 开源仓+实测；"中高"=受控实验/官方博客单源；"中"=单作者预印本/厂商/博客引 issue。所有性能数字均原出处自述未独立复现。

**v2 反驳强度总判**：6 篇反驳论文对 V3 的净效应是**"结论大多成立、归因/前提/结构需修正"**，而非推翻 V3。最强挑战是 R3（feedback-bandwidth 质疑物理域 skill 重投入）——但这恰好与 V3 §6.1"先跑通再加治理"同向（别在 skill 上过度投资），V3 可吸收。V3 的 human gate + deterministic verifier + 拓扑写死 + 只碰经验层 经这 6 篇全文阅读后**反而被强化为正确防线**（Library Drift/SkillFlow/Halt Authority 都指向它们）。

---

**本报告结束（v2 深度版）。** 定位：V3 外部证据 delta（94 篇外 + 6 篇反驳论文全文阅读 + PINN 局限）；下一步由人工挑 §3.1 的 14 条按 V3 §9.5 顺序（先跑 Mie → 再 hooks/A1/OpenCode）增量纳入；§3.3 unverified 项落地前必过核验；R1–R4 四条反驳驱动的修正建议直接回填 V3 §4.2/§5/BORROWABLE §3。
