# 工程模式汇总

> 摘自 Agent Skill 系统与工作流自迭代调研 (2026-06-18)，Section 4

---

## 4.1 Skill 系统设计模式（SoK 综述 7 种）

| # | 模式 | 说明 |
|---|------|------|
| 1 | **Metadata-driven progressive disclosure** | 先加载 name+description，按需加载完整 SKILL.md |
| 2 | **Executable code skills** | Skill 内容含可直接执行的代码（COMSOL Java） |
| 3 | **Self-evolving libraries** | 自动演化 skill 库（Socratic-SWE 轨迹蒸馏→技能→任务→自演化） |
| 4 | **Marketplace distribution** | 社区市场分发（tech-leads-club/agent-skills 4.6k⭐） |
| 5 | **Representation×Scope taxonomy** | NL / Code / Policy / Hybrid 四种表示 |
| 6 | **Compositional skill synthesis** | 组合已有 skill 创造新能力 |
| 7 | **Trust-tiered execution** | 基于来源的安全分级执行 |

**来源**: SoK: Agentic Skills (arXiv:2602.20867)

---

## 4.2 Agent 自迭代架构模式

| 模式 | 适用场景 | 代表工作 |
|------|---------|---------|
| 口头 RL（语言反馈+记忆） | 单步决策改进 | Reflexion |
| 轨迹蒸馏 | 多步工作流优化 | Socratic-SWE, CODESKILL |
| 三阶段自验证 | 输出质量保证 | Self-Refine, FineVerify |
| 群组进化 | 多 Agent 协作优化 | GEA |
| 递归自我设计 | 架构层进化 | MetaAI Recursive |
| 无标注自优化 | 无验证集场景 | RHO |

---

## 4.3 主流框架 Skill 哲学

| 哲学 | 代表 | 优点 | 缺点 | optics_agent 选择 |
|------|------|------|------|-----------------|
| Tool-as-Skill | LangGraph/CrewAI | 灵活 | 需外部编排 | **短期**：采用此模式 |
| Role-as-Skill | MetaGPT/ChatDev | 自带分工 | 灵活性受限 | **中期**：引入角色分工 |
| Program-as-Skill | DSPy | 自动优化 | 学习曲线陡 | **长期**：编译式管道 |

---

## 4.4 SWE Agent 的关键工程教训

- **60-69% 失败是 Edit-Quality 问题**，非 Localization — 优化补丁生成质量
- **框架设计比模型更重要** — 同一模型在不同框架上性能差 6x
- **20% "solved" patch 实际语义错误** — 必须多维度验证
- **Subagent 节省 ~30% token** — 主 agent 规划，子 agent 执行

来源: Coherence Collapse (2603.24631), Claw-SWE (2606.12344), SWE-ABS (2603.00520)
