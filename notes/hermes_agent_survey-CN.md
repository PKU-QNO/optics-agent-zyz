# Hermes Agent 调研报告——设计、开源程度、自迭代系统与风险

> 调研日期：2026-07-13
> 调研方式：3 个并发子agent 分头深挖（A 概览+开源程度 / B 自迭代系统设计 / C 风险与局限）+ 主agent 交叉确认与消歧
> 用途：optics_agent / SEPR 自进化框架设计的业界对照系参考，**不作为本项目规则**
> 体例：关键事实后括注来源 URL；标注【事实】/【推断】/【未查到】/【planned 未落地】

---

## 摘要

Hermes Agent 是 Nous Research 出品的**开源（MIT）、自托管、长期运行** AI agent，定位"the agent that grows with you"——强调持久记忆、自动技能创建、跨平台消息入口与可迁移执行环境，**不是绑定 IDE 的 coding copilot，也不是 chatbot**。主仓库 `NousResearch/hermes-agent`（Python，约 213k stars），自迭代专用仓库 `NousResearch/hermes-agent-self-evolution`（DSPy + GEPA 进化 skill / prompt / tool description / tool code）。

关键结论：

1. **开源程度高**：主仓库 MIT、源码完整（agent/tools/gateway/tests/docs 全公开）、文档齐全、社区活跃；但 Nous Portal / Tool Gateway 是商业托管边界，且 self-evolution 子仓库根目录未见单独 LICENSE 文件（仅 README/pyproject 声明 MIT）。
2. **自迭代是"两层结构"**：① 主 agent 运行时**在线 closed learning loop**（会话后 background review fork 增量 patch memory/skill）；② **离线 self-evolution pipeline**（独立仓库，DSPy+GEPA 批量进化，产 PR 经人工 merge）。二者共享对象与数据源，但不是同一执行循环。
3. **"self-improving" 的实际含义被第三方修正**：Hermes 运行时**没有自动改 source code / 自动重写 prompt template / 自评分 tight loop**，是"durable behavior artifact"（持久化行为产物），**不是 recursive self-improver**。
4. **implemented vs planned 落差大**：自迭代 5 phase 中仅 Phase 1（SKILL.md 进化）已实现，Phase 2-5（tool desc / system prompt / tool code / continuous loop）均 planned；且 Phase 1 自身仍在修 semantic preservation、holdout integrity、reward hacking 等基础问题。
5. **风险集中在 4 类**：自迭代内生风险（reward hacking / drift / 自指 / 成本失控）、AGPL 传染（Darwinian Evolver）、长时运行多平台安全面（API server 误配置可 RCE）、学术界对 self-evolving agent 的普遍警告。
6. **对 SEPR 的核心启示**：Hermes 的 trace-driven 变异、Pareto 多目标、benchmark-as-gate、PR 审查模板可借鉴；但其 Phase 4 代码进化、Phase 5 无人值守 loop、在线 skill 直接写 store、rubric overlap fitness 是**反面教材**，SEPR 应拒绝或更硬约束。

---

## 1. 项目概览

### 1.1 定位与核心理念

- 【事实】Hermes Agent = 自托管、长期运行、带 "closed learning loop" 的个人/通用 agent；官方标语 "the agent that grows with you"。([github.com/NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent), [hermes-agent.org](https://hermes-agent.org/))
- 【事实】"closed learning loop" 含：agent-curated memory、周期性记忆提醒、复杂任务后自主 skill 创建、skill 在使用中自改进、FTS5 历史会话搜索 + LLM 摘要、Honcho 用户建模、兼容 agentskills.io 开放标准。([hermes-agent README](https://github.com/NousResearch/hermes-agent))
- 【事实】"lives where you do" = 单一 gateway 连接 CLI、Telegram、Discord、Slack、WhatsApp、Signal 等 20+ 平台。([docs](https://hermes-agent.nousresearch.com/docs/))
- 【事实】"runs anywhere" = 6 种 terminal backend：local、Docker、SSH、Daytona、Singularity、Modal；Daytona/Modal 提供 serverless 持久化/休眠。([README](https://github.com/NousResearch/hermes-agent))
- 【事实】与 Claude Code / Codex / OpenCode / Cursor / Aider 的差异：Hermes 更像长期个人/团队 agent runtime + messaging gateway + memory/skills loop；第三方评测认为其代码智能、IDE/LSP/AST 能力弱于 Claude Code/Codex/Cursor，但多平台消息、持久记忆、自改进技能、BYO model/self-hosting 更强。([gist](https://gist.github.com/michaeloboyle/10461598db36066e4c366413d5416f83), [techsona](https://techsona.dev/blog/ai-coding-agents-comparison-2026), [ssojet](https://ssojet.com/blog/ai-coding-agents-compared))

### 1.2 团队与时间线

- 【事实】Nous Research 自称美国开源 AI 机构，做 open-source LLM 与分布式训练基础设施。([nousresearch.com](https://nousresearch.com))
- 【事实】teknium1 是 Nous Research co-founder，GitHub profile 说当前重点即 Hermes Agent。([github.com/teknium1](https://github.com/teknium1/teknium1))
- 【事实】主仓库创建 2025-07-22；Nous releases 页列 "Hermes Agent, 02/25/26"，与官网 "released in February 2026" 一致。([releases](https://github.com/NousResearch/hermes-agent/releases), [hermes-agent.org](https://hermes-agent.org/))
- 【事实】版本节奏为日期 tag：v0.13.0 `v2026.5.7`、v0.18.0 `v2026.7.1`、latest v0.18.2 `v2026.7.7.2`；pyproject 版本 `0.18.2`。([releases](https://github.com/NousResearch/hermes-agent/releases), [pyproject.toml](https://github.com/NousResearch/hermes-agent/blob/main/pyproject.toml))

### 1.3 技术栈与部署形态

- 【事实】Python 项目（`requires-python >=3.11,<3.14`），GitHub 语言占比 Python ~82.3%、TypeScript ~14.9%（web/website/ui-tui/桌面前端），另有 Shell/PowerShell/Rust/CSS/Nix。([pyproject](https://github.com/NousResearch/hermes-agent/blob/main/pyproject.toml))
- 【事实】Gateway 已覆盖 20+ 平台：CLI、Telegram、Discord、Slack、WhatsApp、Signal、Matrix、Mattermost、Email、SMS、DingTalk、Feishu、WeCom、Weixin、QQ Bot、Yuanbao、BlueBubbles、Home Assistant、Microsoft Teams、Google Chat 等。([docs](https://hermes-agent.nousresearch.com/docs/))
- 【事实】Model providers：Nous Portal、OpenRouter（200+）、OpenAI、z.ai/GLM、Kimi/Moonshot、MiniMax、HuggingFace、自有 endpoint 等 18+；`hermes model` 切换无需改代码。([README](https://github.com/NousResearch/hermes-agent), [architecture](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/architecture.md))
- 【事实】Tools/MCP：70+ registered tools、28 toolsets；MCP 支持 stdio/HTTP/OAuth/mTLS、tool filtering、dynamic discovery、parallel tool calls；Hermes 也能**作为 MCP server** 把 messaging tools 暴露给 Claude Code/Cursor/Codex。([architecture](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/architecture.md), [mcp docs](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/mcp.md))
- 【事实】Context files：支持 `.hermes.md`/`HERMES.md`、`AGENTS.md`、`CLAUDE.md`、`SOUL.md`、`.cursorrules`、`.cursor/rules/*.mdc`，并支持子目录 AGENTS/CLAUDE 渐进发现。([context-files docs](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/context-files.md))

---

## 2. 开源程度

### 2.1 License

- 【事实】主仓库 `LICENSE` 为 MIT，Copyright 2025 Nous Research；`pyproject.toml` 也写 `license = "MIT"`。([LICENSE](https://github.com/NousResearch/hermes-agent/blob/main/LICENSE), [pyproject](https://github.com/NousResearch/hermes-agent/blob/main/pyproject.toml))
- 【事实】self-evolution 子仓库 README 与 `pyproject.toml` 声明 MIT，但根目录抓取**未发现单独 LICENSE 文件**——合规上略弱于主仓库。([self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution), [self-evolution pyproject](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/pyproject.toml))
- 【事实】自迭代依赖的 Darwinian Evolver 为 **AGPL v3**（external CLI only），见 §4.2 license 风险。([imbue-ai/darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver))

### 2.2 代码完整性

- 【事实】主仓库非论文壳，包含 `agent/`、`tools/`、`gateway/`、`hermes_cli/`、`providers/`、`plugins/`、`skills/`、`optional-skills/`、`tests/`、`website/`、Docker/packaging 等；架构文档说明核心 `AIAgent`、70+ tools、20 gateway adapters、SQLite+FTS5 session storage 都在仓库内。([README](https://github.com/NousResearch/hermes-agent), [architecture](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/architecture.md))
- 【事实/边界】Nous Portal、Tool Gateway/OAuth 订阅服务是**商业/托管边界**；开源客户端可 BYO keys，但 Portal 后端本身未在主仓库开源。([README](https://github.com/NousResearch/hermes-agent))

### 2.3 社区活跃度

| 仓库 | Stars | Forks | Contributors | Open Issues | Releases | 最近活动 |
|---|---|---|---|---|---|---|
| `hermes-agent` | ~213,553 | ~39,548 | ~390 | ~27,344 | 21 (latest `v2026.7.7.2`) | 2026-07-12/13 附近 push |
| `hermes-agent-self-evolution` | ~4,623 | ~527 | 3 | 95 | — | 创建 2026-03-09，最近 push 2026-06-17 |

【事实】来源：[hermes-agent](https://github.com/NousResearch/hermes-agent)、[self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution)。注：27,344 open issues 是显著的 issue backlog 信号（见 §4.5）。

### 2.4 文档

- 【事实】docs 覆盖 installation、quickstart、configuration、messaging、security、tools、skills、memory、MCP、cron、context files、architecture、contributing、CLI/env reference，并提供 `/llms.txt` 与 `/llms-full.txt`。([docs](https://hermes-agent.nousresearch.com/docs/))

### 2.5 商业边界

- 【事实】README 明确 "Skip the API-key collection — Nous Portal"，一个 OAuth 覆盖 300+ models 与 Tool Gateway（web search、image generation、TTS、cloud browser）；同时强调仍可 BYO keys，gateway 是 per-backend 而非 all-or-nothing。([README](https://github.com/NousResearch/hermes-agent))

### 2.6 隐私立场

- 【事实】官网明确 "No Tracking / Zero telemetry, zero data collection"、"All memory stored in `~/.hermes/` on your machine"、"All data stays on your machine. No telemetry, no tracking, no cloud lock-in."([hermes-agent.org](https://hermes-agent.org/))
- 【事实/注意】第三方 gist 指出 trajectory capture / RL components 是 Nous training data pipeline 的一部分，对 end-user data governance 有影响——隐私立场面向"本机数据"，但 trajectory 飞轮仍可能外溢。([gist](https://gist.github.com/michaeloboyle/10461598db36066e4c366413d5416f83))

### 2.7 生态

- 【事实】官方指向 Discord、Skills Hub、agentskills.io；skills docs 支持 official optional skills、skills.sh、well-known skill endpoints、GitHub taps、ClawHub、LobeHub、browse.sh。([skills docs](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md))
- 【事实】第三方：`Euraika-Labs/hermes-agent` 是主仓库 fork；`Lumio-Research/hermes-agent-rs` 是 Rust port（基于 `v2026.4.13`，MIT，v0.1 core loop/providers/tools/adapters/memory/CLI production-ready，其 self-evolution 表述为 multi-armed bandit model selection + prompt/memory shaping，**不等同** Nous 官方 GEPA pipeline）。([Lumio](https://github.com/Lumio-Research/hermes-agent-rust), [Euraika](https://github.com/Euraika-Labs/hermes-agent))

---

## 3. 自迭代系统设计（重点）

### 3.1 两层结构：在线 loop + 离线 pipeline

Hermes 的"自改进"由两个独立机制承担，**不是单一自迭代循环**：

| 层 | 仓库 | 时机 | 对象 | 强度 |
|---|---|---|---|---|
| **在线 closed learning loop** | `hermes-agent` 主仓库 | 每轮会话后 | memory / skill 增量 patch | 轻量、即时、可写入审批 |
| **离线 self-evolution pipeline** | `hermes-agent-self-evolution` | 手动 CLI 触发 | skill / prompt / tool desc / tool code 文本与代码 | 批量、GEPA、产 PR 人工 merge |

- 【事实】主 agent 在线 loop 的核心实现是 **background review fork**：每轮后 `AIAgent.run_conversation` 可 spawn daemon thread，fork 一个 agent replay conversation snapshot，问自己是否应保存/更新 memory 或 skill；写入 memory/skill stores；**主会话和 prompt cache 不被触碰**；工具白名单限制为 memory 和 skill management。([background_review.py](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/background_review.py))
- 【事实】在线 loop 可用 auxiliary `background_review` provider/model 路由到便宜模型；`memory.write_approval: true` 时 background 写入会 staged，用 `/memory pending/approve/reject` 审核。([memory docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory))
- 【事实】在线 loop 的 protected skills 不编辑：bundled skills、hub-installed skills；agent-created/pinned skills 可 patch，**pin 只防 curator 删除/归档，不防内容更新**。([background_review.py](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/background_review.py))
- 【事实】离线 self-evolution 明确声明 **"standalone optimization pipeline"、"operates ON hermes-agent — not part of it"**，读取主仓库的 skill/tool/prompt，输出分支/PR 给人工审查。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))

### 3.2 离线 self-evolution pipeline 架构

【事实】离线 pipeline 步骤（[README](https://github.com/NousResearch/hermes-agent-self-evolution), [PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md)）：

```
选择目标 skill/prompt/tool
  → 构建 eval dataset（synthetic / sessiondb / golden / skill-specific auto-eval）
  → 包装为 DSPy module（SkillModule）
  → validate baseline constraints（size/growth/structure）
  → 运行 optimizer（GEPA / MIPROv2 fallback / Darwinian Evolver for code）
  → held-out test 比较 baseline vs evolved
  → validate evolved constraints
  → Constraint gates
  → Best variant → git branch evolve/<target>-<timestamp> → gh pr create
  → 人工 review → merge
```

组件职责（[evolution/](https://github.com/NousResearch/hermes-agent-self-evolution/tree/main/evolution)）：

| 文件 | 职责 |
|---|---|
| `dataset_builder.py` | synthetic/golden train-val-holdout 数据集 |
| `external_importers.py` | 从 Claude Code `~/.claude/history.jsonl`、Copilot `~/.copilot/session-state/*/events.jsonl`、Hermes `~/.hermes/sessions/*.json` 导入真实会话；heuristic prefilter + LLM relevance + **secret pattern 过滤** |
| `fitness.py` | LLM-as-judge 多维分数 + 快速 metric（当前实现是 keyword overlap proxy） |
| `constraints.py` | size/growth/non-empty/skill frontmatter structure/pytest gate |
| `skill_module.py` | 把 `SKILL.md` body 包成 DSPy module；`reassemble_skill` 只替换 body、保留 YAML frontmatter |
| `evolve_skill.py` | 编排 Phase 1 skill evolution；尝试 `dspy.GEPA`，异常 fallback `dspy.MIPROv2(auto='light')` |

【事实/未完全落地】`pr_builder.py` 在 PLAN 中有设计，但当前仓库实现目录未见该文件；`evolve_skill.py` 目前保存 `output/<skill>/<timestamp>/evolved_skill.md` + baseline + metrics 并提示人工 review diff，**自动 PR 生产属于规划/未完全落地**。([evolve_skill.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/evolve_skill.py))

### 3.3 进化对象与边界（5 phase）

| Phase | 目标 | 引擎 | 状态 | 风险分级 |
|---|---|---|---|---|
| 1 | Skill files (`SKILL.md`) | DSPy + GEPA | ✅ Implemented | Tier 1 低 |
| 2 | Tool descriptions | DSPy + GEPA | 🔲 Planned | — |
| 3 | System prompt sections | DSPy + GEPA | 🔲 Planned | Tier 3 higher risk |
| 4 | Tool implementation code | Darwinian Evolver | 🔲 Planned | **Tier 4 highest risk** |
| 5 | Continuous improvement loop | Automated pipeline | 🔲 Planned | — |

【事实】来源：[self-evolution README](https://github.com/NousResearch/hermes-agent-self-evolution)、[PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md)。

边界与约束：

- 【事实】Phase 1 **只替换 skill body，保留 YAML frontmatter**（`reassemble_skill(frontmatter, evolved_body)`）。([skill_module.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/skill_module.py))
- 【事实】**Size limits**：skill 默认 `max_skill_size=15000` chars；tool description ≤500 chars；parameter description ≤200 chars；system prompt section growth max 20%。([config.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/config.py), [PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**冻结项**：tool description 阶段不改 schema 参数名/类型/required；system prompt 不热替换 active conversation；Phase 4 代码进化冻结 function signatures 与 `registry.register()` calls。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**Prompt caching 边界**：所有 evolved content 只在新 session 生效，**不 mid-conversation hot-swap**。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**Drift 约束**：PLAN 称用 semantic similarity checks 强制 evolved text 不偏离原 purpose；**但当前 `constraints.py` 实现只看到 size/growth/non-empty/frontmatter structure/pytest，未见 semantic similarity 代码**——应标为 planned 未落地。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md), [constraints.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/constraints.py))

### 3.4 GEPA 机制

- 【事实/论文】**GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning**, Agrawal, Tan, Soylu, Ziems, Khare, Opsahl-Ong, Singhvi, Shandilya, Ryan, Jiang, Potts, Sen, Dimakis, Stoica, Klein, Zaharia, Khattab, **arXiv:2507.19457**, ICLR 2026 Oral。([arxiv.org/abs/2507.19457](https://arxiv.org/abs/2507.19457), [ICLR oral page](https://iclr.cc/virtual/2026/oral/10009494))
- 【事实】**核心思想**：GEPA 不只看 scalar score，而读取 **full execution traces**（reasoning / tool calls / tool outputs / error messages / natural-language feedback），反思**为什么失败**，再提出 targeted prompt updates——不是只看 pass/fail。([dspy GEPA overview](https://dspy.ai/api/optimizers/GEPA/overview/), [gepa-ai/gepa](https://github.com/gepa-ai/gepa))
- 【事实】**Genetic 含义**：维护候选池，从候选中选 parent，执行 minibatch，reflect，mutate 产生新文本候选；候选可继承 ancestor lessons。
- 【事实】**Pareto 含义**：默认 `candidate_selection_strategy='pareto'`，从每个 validation example/objective 的 **Pareto frontier** 中采样；候选被多少 frontier keys 认为最佳影响选中概率——不是简单贪心全局最优。
- 【事实】**变异/选择**：可自定义 `instruction_proposer`；选择策略有 `pareto` / `current_best` / `top_k_pareto` / `epsilon_greedy` / custom selector。
- 【事实】**终止**：要求 `auto` / `max_full_evals` / `max_metric_calls` 三选一；可用 `stop_callbacks` 接 timeout / no-improvement / file / signal stopper。
- 【事实】**默认参数**：`reflection_minibatch_size=3`、`skip_perfect_score=True`、`use_merge=True`、`max_merge_invocations=5`、`component_selector='round_robin'`。
- 【事实】**与 MIPROv2 区别**：MIPROv2 主要用 Bayesian optimization 搜 instruction/few-shot；GEPA 用 full trace + 自然语言反馈。论文称 GEPA 平均优于 GRPO 6pp（最多 19pp），用最多 35x fewer rollouts，优于 MIPROv2 10pp+。([ICLR oral](https://iclr.cc/virtual/2026/oral/10009494))
- 【事实/兼容性注意】Hermes `evolve_skill.py` 调用 `dspy.GEPA(metric=..., max_steps=iterations)`，异常 fallback `dspy.MIPROv2(auto='light')`；但 `max_steps` 参数与当前 DSPy 文档的 `max_metric_calls/max_full_evals/auto` 不完全一致，可能依赖特定 DSPy 版本或尚未同步。([evolve_skill.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/evolve_skill.py))

### 3.5 触发与循环

- 【事实】**当前触发是手动 CLI**：`python -m evolution.skills.evolve_skill --skill github-code-review --iterations 10 --eval-source synthetic/sessiondb`。([README](https://github.com/NousResearch/hermes-agent-self-evolution))
- 【事实/planned】PLAN 设想 agent 可 self-invoke（"I notice this skill could be improved. Let me run GEPA optimization on it."），但当前实现未查到主仓库自动调用该仓库优化的落地路径。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**单次 run 结构**：load skill → build/load dataset → validate baseline constraints → configure DSPy/GEPA → compile optimized module → extract evolved text → validate evolved constraints → holdout baseline/evolved scoring → save evolved/baseline/metrics。([evolve_skill.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/evolve_skill.py))
- 【事实】**Phase 1 完成门**：至少 1 个 skill eval dataset 上 ≥10% score increase；TBLite 无 regression（score within 2%）；evolved diff 人类读起来合理；pipeline 可复用于任意 skill。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实/planned】**Phase 5 continuous loop**：performance monitor 追踪 per-skill success rate、tool selection accuracy、benchmark scores、user corrections；auto-triage 按 `potential improvement × usage frequency` 排序；cron weekly benchmark；超阈值自动触发 GEPA；**仍 PR/human merge**。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))

### 3.6 评估体系

- 【事实】**Eval 来源 4 类**（[PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md), [dataset_builder.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/dataset_builder.py), [external_importers.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/external_importers.py)）：
  - **Synthetic**：强模型读 skill 文件生成 15-30 task_input + expected_behavior rubric（非 exact text）；config 默认 `eval_dataset_size=20`，split 50/25/25。
  - **Sessiondb/external**：从 Claude Code / Copilot / Hermes session 导入，heuristic prefilter + LLM relevance + secret pattern 过滤。
  - **Golden**：手写 JSONL golden sets。
  - **Skill-specific auto-eval**：如 systematic-debugging 种 bug 看 tests pass，arxiv 查 known papers，github-code-review planted issues。
- 【事实】**指标**：LLM-as-judge 多维分数 correctness 0.5 + procedure_following 0.3 + conciseness 0.2，再减 length_penalty；**但当前快速优化 metric 实现是 keyword overlap proxy，不是完整 LLM judge**。([fitness.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/fitness.py))
- 【事实】**Benchmark 是 gate，不是主 fitness**：task-specific fitness 评估目标本身，TBLite/YC-Bench/pytest 防 broad regression；"提升 20% 但 TBLite 掉 5%"的 variant reject。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**防 overfitting**：train/val/holdout split + held-out test + benchmark gate + PR 含 train/validation/holdout scores。
- 【事实/落差】**防 reward hacking 的已规划措施**：holdout、benchmark regression gate、semantic preservation、length penalty、human review；**但当前代码已实现 length/growth/structure/holdout，semantic preservation 与 benchmark gate 多数仍是 PLAN 层**。

### 3.7 Human gate 与安全边界

- 【事实】**离线 self-evolution 部署原则：PR，never direct commit**。PLAN 给出 `git checkout -b evolve/<target>-<timestamp>`、commit message 含 optimizer/dataset/before/after/holdout、`gh pr create` 流程。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**Rollback**：Git history tracks lineage，`git revert`。
- 【事实】**Phase 4 代码进化要求 "every line of evolved code reviewed before merge"**；但"每个被淘汰 variant 都人工审"未查到要求。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**主仓库 command approval 提供 runtime 安全底座**：`smart/manual/off` approval、YOLO mode、hardline blocklist、user deny rules、cron `deny|approve`；但**与自迭代无直接耦合**。([security docs](https://hermes-agent.nousresearch.com/docs/user-guide/security))
- 【事实/弱gate】**在线 skill patch 的 human gate 弱于离线 PR gate**：background review 的 writes go straight to memory + skill stores；memory 有 `write_approval` 审批，但 **skill patch 是否同等强 gate 未查到完整配置**——应标为"未查到强 PR 型 human gate"。([background_review.py](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/background_review.py))
- 【事实/重要】**官方 SECURITY.md 明确**：approval gate、redaction、Skills Guard **都不是 security boundary**，只是 in-process heuristic；**唯一对 adversarial LLM load-bearing 的边界是 OS-level isolation**。([SECURITY.md](https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md))

### 3.8 "self-improving" 的实际含义

- 【事实/第三方】Saulius 审查结论：Hermes "self-improving" 主要是 **skills、memory、offline RL pipeline、update protocol**；运行时**没有自动改 source、自动重写 prompt、自评分 tight loop**——是 **durable behavior artifact**，**不是 recursive self-improver**。([saulius.io](https://saulius.io/blog/hermes-agent-self-improving-ai-architecture))
- 【推断】因此对 SEPR 而言，Hermes 的"self-evolution"更接近"离线 prompt/skill 文本优化器 + 在线经验库增量"，而非"agent 自我重写架构"——这与 SEPR "自迭代只碰经验层"的定位**同构**，是可对照的诚实参考，但营销话术（"the only agent with a built-in learning loop"）需打折。

---

## 4. 风险与局限（重点）

### 4.1 自迭代内生风险

| 风险 | Hermes 现状 | 来源 |
|---|---|---|
| **Reward hacking / 评估过拟合** | 【事实】PR #150 指出当时核心 fitness 是 keyword overlap，会奖励"复述 rubric 词汇"而非真实正确性；`LLMJudge` 存在主观/循环评价问题 | [PR #150](https://github.com/NousResearch/hermes-agent-self-evolution/pull/150), [evolve_skill.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/evolve_skill.py) |
| **Drift（偏离原目的）** | 【事实】README/PLAN 宣称 semantic preservation，但 PR #151 指出当时 "only on paper"，`validate_all` 只查 size/growth/non-empty/structure，skill 甚至可漂成 poem 仍过门控 | [constraints.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/constraints.py), [PR #151](https://github.com/NousResearch/hermes-agent-self-evolution/pull/151) |
| **模式坍塌 / 多样性丢失** | 【推断】Hermes 自身无明确 diversity-preservation 机制；Darwinian Evolver 用 performance + novelty bonus 选 parent，但承认 batch mutations 降低 diversity、难逃 local optima | [imbue-ai/darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver) |
| **不可控修改** | 【事实/planned】Phase 4 进化 tool code，PLAN 承认 "highest risk"，要求 full tests + signature/registry frozen + human review；Phase 5 continuous loop 自动检测弱项触发优化（仍 human merge）。roadmap 落地后 blast radius 从 skill 文本扩到 prompt/tool code | [PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md) |
| **自指风险** | 【事实】PLAN 明确 self-evolution repo "operates ON hermes-agent — not part of it"、独立仓库；但**未查到形式化禁止 self-evolution 修改自身**。相对 SEPR "自迭代不迭代自己"红线，Hermes 是分仓隔离而非形式化禁止 | [PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md), [saulius.io](https://saulius.io/blog/hermes-agent-self-improving-ai-architecture) |
| **成本失控** | 【事实】README 写 GEPA ~`$2-10/run`；PLAN 另写 TBLite `$20-50`、TerminalBench2/YC-Bench `$50-200`；Phase 5 weekly benchmark + 阈值触发会持续累积，若不受预算硬约束长期费用远高于单 run 估算 | [README](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/README.md), [PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md) |
| **在线 active update bias** | 【事实】Hermes prompt 曾明确 "most sessions produce at least one skill update"；issue #30220 指出会导致 false positives、memory/skill/user store misclassification | [issue #30220](https://github.com/NousResearch/hermes-agent/issues/30220), [background_review.py](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/background_review.py) |

### 4.2 License 风险

- 【事实】self-evolution README/PLAN 标注 DSPy+GEPA 为 MIT，Darwinian Evolver 为 **AGPL v3** 且 "external CLI only"；`pyproject.toml` 主项目 license MIT，`darwinian-evolver` 放在 optional extra `darwinian`。([self-evolution README](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/README.md), [pyproject](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/pyproject.toml))
- 【推断/非法律意见】仅作外部 CLI 调用通常比 import/link 风险低；但若分发、修改、托管 Darwinian Evolver，或把 AGPL 代码深度集成为网络服务，需满足 AGPL 源码提供义务。AGPL 通常不自动把"输出 patch"变成 AGPL，但若输出物是 AGPL 代码派生物或混入 AGPL 片段则有合规风险。
- 【事实/缺口】当前 README/PLAN 只写 "external CLI only"，**未见更详细 license compliance policy**。Phase 4 落地前应补齐文档化边界（"可选依赖、外部进程、未 vendored、未修改/若修改则公开"）。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))

### 4.3 安全 / 对齐风险

- 【事实】**长时运行 + 多平台攻击面**：CLI、gateway、API server、cron、20+ 消息平台、70+ tools、6 terminal backends、cron unattended jobs——攻击面远大于单 CLI agent。([README](https://github.com/NousResearch/hermes-agent/blob/main/README.md), [architecture](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture))
- 【事实/重要】**SECURITY.md 自认边界有限**：approval gate / redaction / Skills Guard **都不是 security boundary**，只是 in-process heuristic；**唯一对 adversarial LLM load-bearing 的边界是 OS-level isolation**。([SECURITY.md](https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md))
- 【事实/严重】**Issue #6439**：API server 在 `API_SERVER_HOST=0.0.0.0` 且无 `API_SERVER_KEY` 时**可 unauthenticated RCE**；默认 localhost 相对安全，但误配置严重。([issue #6439](https://github.com/NousResearch/hermes-agent/issues/6439))
- 【事实】**Issue #40889 posture review**：无 rate limiting、CORS wildcard、Windows plaintext secrets、issue backlog 难筛安全问题；同时列 supply-chain audit、OSV scanner、SECURITY.md 等强项。([issue #40889](https://github.com/NousResearch/hermes-agent/issues/40889))
- 【推断】**Prompt injection 经进化固化**：若 self-evolution 从 contaminated traces/sessiondb 构建 eval 或 skill，prompt injection 可能被固化为 skill/prompt，除非有外部 verifier、negative controls、人审。([SECURITY.md](https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md), [issue #115](https://github.com/NousResearch/hermes-agent-self-evolution/issues/115))
- 【事实/推断】**多平台隐私**：Hermes 可从消息平台、email、webhook、API server 接收内容并调 shell/file/network；SECURITY.md 建议 untrusted surfaces 用 whole-process wrapper。

### 4.4 学术界风险讨论

| 论文 | 核心观点 | 与 Hermes 的关联 | 来源 |
|---|---|---|---|
| **GEPA: Reflective Prompt Evolution Can Outperform RL** (Agrawal et al., 2026, ICLR Oral) | rollout-efficient，但 optimizer 直接读失败 trace 优化可观测指标，**指标错配则 proxy hacking 风险** | Hermes 自迭代核心引擎 | [arXiv:2507.19457](https://arxiv.org/abs/2507.19457) |
| **Feedback Loops With LMs Drive In-Context Reward Hacking** (Pan et al., 2024) | 反馈回路中 LLM 输出影响后续输入，导致 test-time/in-context reward hacking；静态数据集评估不足以捕捉 | Hermes Phase 5 continuous loop + sessiondb reingestion | [arXiv:2402.06627](https://arxiv.org/pdf/2402.06627) |
| **On Safety Risks in Experience-Driven Self-Evolving Agents** (Zhao et al., 2026) | 经验驱动自进化即便只积累 benign tasks，也可能在 high-risk scenarios 降低 safety；benign/harmful 混合又导致 over-refusal | Hermes 在线经验 loop 的根本性风险 | [arXiv:2604.16968](https://arxiv.org/pdf/2604.16968) |
| **SEVerA: Verified Synthesis of Self-Evolving Agents** (Banerjee et al., 2026) | 现有 self-evolving agent 对 autonomous unseen inputs **缺 formal safety/correctness guarantee**，提出 verified synthesis | 支持 SEPR 需 verifier/gate 而非仅文本约束 | [arXiv:2603.25111](https://arxiv.org/pdf/2603.25111v2) |
| **Correlated Proxies** (Laidlaw et al., 2024) | proxy reward 优化导致 true objective 退化 | Hermes fitness proxy 风险的理论支撑 | [arXiv:2403.03185](https://arxiv.org/pdf/2403.03185v4) |

### 4.5 社区与第三方评价

- 【事实/第三方】**Leif Markthaler 技术审查**：架构文档好，但 `AIAgent` 是 10k+ 行 god object；context compression 有 death spiral、silent data loss、provider mismatch、config key mismatch；主导模式 fail-silent，适合个人 VPS 但**不适合 system-of-record / regulated context**。([Medium](https://medium.com/@leif.markthaler/hermes-agent-a-deep-technical-review-of-nousresearchs-self-improving-ai-agent-b48c64f8e3cc))
- 【事实/第三方】**Saulius 架构审查**：见 §3.8——durable behavior artifact，非 recursive self-improver。([saulius.io](https://saulius.io/blog/hermes-agent-self-improving-ai-architecture))
- 【事实/第三方】**Michael O'Boyle gist**：多平台 gateway 强项、security hardening 值得借鉴，但 code intelligence 弱于 Claude Code/Codex，monolithic、issue backlog、trajectory data flywheel、single-tenant/operator-trust security model 是红旗。([gist](https://gist.github.com/michaeloboyle/10461598db36066e4c366413d5416f83))
- 【事实/社区】**HN 讨论**：有用户反馈 sluggish、slow startup、over-engineered、不喜欢 MEMORY.md 摘要、担心 upstream master；也有用户说个人助手有用。HN 出现 plagiarism allegation 指向 issue #10232 和 EvoMap，**本次未核实真伪**，仅作为"社区争议存在"记录。([HN](https://news.ycombinator.com/item?id=48419000))
- 【未查到】Reddit 评价：Exa 对 `reddit.com` 返回 403，未取得可引用证据。

### 4.6 Hermes 自述 limitation

- 【事实】**Phase status**：仅 Phase 1 implemented，Phase 2-5 均 planned。([self-evolution README](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/README.md))
- 【事实】**风险分级**：PLAN 自述 Tier 1 skill 低风险、Tier 3 system prompt "higher risk"、Tier 4 code evolution "highest risk"；Phase gates 若不能证明有效会 stop/reassess。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
- 【事实】**当前成熟度**：self-evolution issues/PRs 显示截至 2026-07 仍在修 GEPA compatibility、validator false positives、semantic preservation、holdout integrity、objective verifier 等基础问题，**Phase 1 pipeline 仍不成熟**。([PR #142](https://github.com/NousResearch/hermes-agent-self-evolution/pull/142), [PR #150](https://github.com/NousResearch/hermes-agent-self-evolution/pull/150), [PR #151](https://github.com/NousResearch/hermes-agent-self-evolution/pull/151))

### 4.7 implemented vs planned 落差汇总

| 声称 | 实际 | 证据 |
|---|---|---|
| Semantic preservation / must not drift | **planned 未落地**，`validate_all` 无 semantic check | PR #151, constraints.py |
| Benchmark regression gate | 多数 PLAN 层 | PLAN.md vs fitness.py |
| 自动 PR 生产 | `pr_builder.py` 设计但未实现，当前人工 review diff | evolve_skill.py |
| Phase 2-5 自迭代能力 | 全部 planned | README phase 表 |
| "the only agent with a built-in learning loop" | 在线 loop 是 durable artifact，非 recursive self-improver | Saulius 审查 |
| 强 human gate | 离线 PR gate 强，**在线 skill patch gate 弱**（直接写 store） | background_review.py |

---

## 5. 对 SEPR / optics_agent 的启示

### 5.1 可借鉴

1. **trace-driven 变异**：SEPR 的复现失败日志、verifier 输出、gate 失败原因可作为 GEPA 式 ASI（anchored self-improvement），不只记录 pass/fail，而读"为什么失败"提出 targeted skill 改动。([GEPA overview](https://dspy.ai/api/optimizers/GEPA/overview/))
2. **Pareto 多目标**：SEPR 可把物理正确性、论文图拟合、成本、可审计性、run 稳定性作为多 frontier keys，避免只优化单一 success score。([gepa candidate-selection](https://github.com/gepa-ai/gepa/blob/main/docs/docs/guides/candidate-selection.md))
3. **benchmarks as gates, not fitness**：SEPR 的 deterministic verifier / 物理硬约束应是 gate，skill 改进的局部指标不能绕过物理守门。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
4. **PR 审查模板**：每次 SEPR skill update 要求——before/after diff、train/val/holdout case、失败 variant 摘要、成本、是否触发 drift/size gate、是否影响已有论文复现回归。([PLAN.md PR body 设计](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
5. **不 mid-session 热替换**：SEPR 也应避免复现 run 中途改规则导致审计不可复现。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
6. **drift/size 硬预算**：引入 15KB/500 chars/20% growth 类硬预算和"不可偏离原复现 skill purpose"审查项——但**必须真正实现，不能像 Hermes 那样 only on paper**。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md), [PR #151](https://github.com/NousResearch/hermes-agent-self-evolution/pull/151))
7. **分仓隔离**：self-evolution repo "operates ON hermes-agent — not part of it" 是好做法，SEPR 的 evolution-agent 也应与复现 main-agent 隔离。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
8. **eval 数据来源多元化 + secret 过滤**：external_importers 的 secret pattern 过滤、heuristic prefilter + LLM relevance 是 SEPR 接真实复现 trace 时可参考的数据卫生设计。([external_importers.py](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/external_importers.py))

### 5.2 警惕 / 拒绝

1. **拒绝 Phase 4 式代码进化进入主闭环**：Hermes 自列 "highest risk"；SEPR 原则是"不改 workflow 拓扑/agent 自身"。若未来引入代码 evolution，应限定 disposable copy、sealed verifier、append-only manifest、human PR review，**禁止自动写主线**。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
2. **拒绝 Phase 5 无人值守 cron loop**：自动检测→优化→PR 增加 Goodhart 风险和噪音；SEPR 在论文复现初期应**人工开启、case-by-case**，不 cron 自动优化。([PLAN.md](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md))
3. **拒绝在线 skill 直接写 store**：Hermes background review 可直接写 skill store 是弱 gate；SEPR 应坚持**所有 skill 更新进 human gate**，不让后台 agent 直接改 canonical skills。([background_review.py](https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/background_review.py))
4. **拒绝 rubric/keyword overlap 作 fitness**：Hermes #150 是反面教材；SEPR 论文复现应优先**物理硬约束、数值复算、图表定量比较、negative controls**。([PR #150](https://github.com/NousResearch/hermes-agent-self-evolution/pull/150))
5. **拒绝 active update bias**：Hermes "most sessions produce at least one skill update" 导致 false positives；SEPR 应让 **"Nothing to update" 成为强一等选项**。([issue #30220](https://github.com/NousResearch/hermes-agent/issues/30220))
6. **拒绝把 approval/regex scanner 当安全边界**：Hermes SECURITY.md 说得很清楚，真正边界是 OS-level isolation；SEPR 跑代码/仿真应用 workspace/container/权限边界，不靠 prompt 说"不要做坏事"。([SECURITY.md](https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md))
7. **AGPL 组件慎用**：SEPR 若引入 Darwinian Evolver 类 AGPL 工具进化代码，需文档化"外部进程、未 vendored、未修改"边界，否则合规风险。([imbue-ai/darwinian_evolver](https://github.com/imbue-ai/darwinian_evolver))

### 5.3 风险防范清单（SEPR 落地对照）

| SEPR 原则 | Hermes 对应做法 | 启示 |
|---|---|---|
| 自迭代只碰经验层 | Phase 1 skill 文本 ✅；Phase 4 code ❌ | 保持经验层，不扩到代码 |
| 走 human gate | 离线 PR gate ✅；在线 skill patch gate 弱 ⚠ | 所有更新进 PR gate |
| 自迭代不迭代自己 | 分仓隔离 ✅；无形式化禁止 ⚠ | SEPR 应**形式化禁止** E-flow 改自身/gate/verifier/AGENTS |
| 不改拓扑 | Hermes 无拓扑概念 | SEPR 拓扑写死原则不变 |
| deterministic verifier | fitness 用 keyword overlap ❌ | SEPR 用物理硬约束 + 数值复算 |
| 可审计失败分类 | fail-silent ⚠ | SEPR 失败显式化、result_class 口径 |
| implemented vs planned 标注 | 营销 vs 实际有落差 ❌ | SEPR 文档强制标注 implemented/planned/not_run |
| 成本与停机点 | $2-10/run 易低估 ⚠ | SEPR 设 run budget / token budget / max candidates / 熔断 |
| 防 holdout contamination | PR #151 显示曾缺 ⚠ | seeded split + 去重 + negative-control probes + accepted-trace-only reingestion |
| 安全边界 | OS-level isolation ✅ | SEPR 用 container/workspace 权限边界 |

---

## 6. 来源

### 6.1 Hermes 仓库与官方文档

- 主仓库：https://github.com/NousResearch/hermes-agent
- 主仓库 README：https://github.com/NousResearch/hermes-agent/blob/main/README.md
- LICENSE：https://github.com/NousResearch/hermes-agent/blob/main/LICENSE
- SECURITY.md：https://github.com/NousResearch/hermes-agent/blob/main/SECURITY.md
- pyproject.toml：https://github.com/NousResearch/hermes-agent/blob/main/pyproject.toml
- releases：https://github.com/NousResearch/hermes-agent/releases
- 官网：https://hermes-agent.org/
- 官方文档：https://hermes-agent.nousresearch.com/docs/
- Architecture 文档：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/architecture.md
- Security 文档：https://hermes-agent.nousresearch.com/docs/user-guide/security
- Skills 文档：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/skills.md
- Memory 文档：https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
- MCP 文档：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/mcp.md
- Context files 文档：https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/context-files.md
- background_review.py：https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/background_review.py
- Nous Research：https://nousresearch.com ，releases：https://nousresearch.com/releases/
- teknium1：https://github.com/teknium1/teknium1

### 6.2 自迭代仓库与代码文件

- self-evolution 仓库：https://github.com/NousResearch/hermes-agent-self-evolution
- PLAN.md：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/PLAN.md
- evolve_skill.py：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/evolve_skill.py
- skill_module.py：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/skills/skill_module.py
- config.py：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/config.py
- constraints.py：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/constraints.py
- dataset_builder.py：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/dataset_builder.py
- external_importers.py：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/external_importers.py
- fitness.py：https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/evolution/core/fitness.py
- PR #150：https://github.com/NousResearch/hermes-agent-self-evolution/pull/150
- PR #151：https://github.com/NousResearch/hermes-agent-self-evolution/pull/151
- issue #115：https://github.com/NousResearch/hermes-agent-self-evolution/issues/115
- GEPA：https://github.com/gepa-ai/gepa ，candidate-selection：https://github.com/gepa-ai/gepa/blob/main/docs/docs/guides/candidate-selection.md
- DSPy GEPA overview：https://dspy.ai/api/optimizers/GEPA/overview/
- Darwinian Evolver：https://github.com/imbue-ai/darwinian_evolver
- Lumio Rust port：https://github.com/Lumio-Research/hermes-agent-rust
- Euraika fork：https://github.com/Euraika-Labs/hermes-agent

### 6.3 第三方评价与社区

- Leif Markthaler 技术审查：https://medium.com/@leif.markthaler/hermes-agent-a-deep-technical-review-of-nousresearchs-self-improving-ai-agent-b48c64f8e3cc
- Saulius 架构审查：https://saulius.io/blog/hermes-agent-self-improving-ai-architecture
- Michael O'Boyle gist：https://gist.github.com/michaeloboyle/10461598db36066e4c366413d5416f83
- HN 讨论：https://news.ycombinator.com/item?id=48419000
- issue #6439（unauthenticated RCE）：https://github.com/NousResearch/hermes-agent/issues/6439
- issue #40889（security posture review）：https://github.com/NousResearch/hermes-agent/issues/40889
- issue #30220（active update bias）：https://github.com/NousResearch/hermes-agent/issues/30220
- AI coding agents 对比：https://techsona.dev/blog/ai-coding-agents-comparison-2026 ，https://ssojet.com/blog/ai-coding-agents-compared

### 6.4 学术论文

- GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning, Agrawal et al., 2026, arXiv:2507.19457, ICLR 2026 Oral —— https://arxiv.org/abs/2507.19457 , https://iclr.cc/virtual/2026/oral/10009494
- Feedback Loops With Language Models Drive In-Context Reward Hacking, Pan et al., 2024, arXiv:2402.06627 —— https://arxiv.org/pdf/2402.06627
- On Safety Risks in Experience-Driven Self-Evolving Agents, Zhao et al., 2026, arXiv:2604.16968 —— https://arxiv.org/pdf/2604.16968
- SEVerA: Verified Synthesis of Self-Evolving Agents, Banerjee et al., 2026, arXiv:2603.25111 —— https://arxiv.org/pdf/2603.25111v2
- Correlated Proxies: A New Definition and Improved Mitigation for Reward Hacking, Laidlaw et al., 2024, arXiv:2403.03185 —— https://arxiv.org/pdf/2403.03185v4
