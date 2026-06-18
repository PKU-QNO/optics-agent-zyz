# Agent Skill 系统与工作流自迭代：前沿调研

> 调研日期：2026-06-18
> 方法：Web 搜索 (6 主题 × 8 变体词) + Arxiv MCP 搜索 (8 方向 ~50 查询) + 16 篇关键论文精读 + 10 框架深度对比

## 文件导航

```
index.md                    # 本文件：总览 + 核心概念 + 搜索方法论
│
survey/                     # 方向调研（每方向独立文件）
├── 01_skill_system.md      # Skill System 架构
├── 02_self_improving.md    # Self-Improving / Self-Iteration
├── 03_tool_use.md          # Tool Use & Composition
├── 04_meta_cognition.md    # Meta-Cognition & Reflection
├── 05_swe_agent.md         # SWE Agent 实践
├── 06_framework_compare.md # 开源框架对比
└── 07_scientific_computing.md # 科学计算 Agent
│
papers/                     # 论文精读（每篇独立文件）
├── voyager.md              # Voyager (2305.16291)
├── reflexion.md            # Reflexion (2303.11366)
├── swe_agent.md            # SWE-agent (2405.15793)
├── self_refine.md          # Self-Refine (2303.17651)
├── generative_agents.md    # Generative Agents (2304.03442)
├── metagpt.md              # MetaGPT (2308.00352)
├── socratic_swe.md         # Socratic-SWE (2606.07412)
└── sok_skills.md           # SoK: Agentic Skills (2602.20867)
│
patterns.md                 # 工程模式汇总
optics_agent_mapping.md     # optics_agent 项目映射
inspiring_ideas.md          # 启发性想法与 Next Steps
references.md               # 全部参考文献
```

## 核心发现速览

### 1. Skill 系统已成 Agent 架构标准抽象层
- SKILL.md 规范（Anthropic）已成事实标准，被 Claude Code、opencode、Cursor 等采纳
- 社区 42,447+ 公开技能包，26.1% 存在安全漏洞
- **opencode 是目前最系统化的开源 Skill 框架**：目录自动发现 + MCP 集成 + 权限控制 + multi-path

### 2. 自迭代三大范式
| 范式 | 代表 | 核心 |
|------|------|------|
| 言语强化学习 | Reflexion | 语言反馈替代权重更新 |
| 自举推理 | STaR | 正确率过滤自训练 |
| 自我反馈精炼 | Self-Refine | 同一 LLM 三角色迭代 |

### 3. Tool Use 三个关键转变
- skill → skill tree/ecosystem
- stateless → persistent "Workspace + Skill"
- 单目标 → 多目标 Pareto 优化

### 4. 元认知向分层架构演进
- Sophia System 3、SMARt 四层状态机、DS-MCM 双速监控
- 外部验证器不可或缺（self-bias 导致递归漂移）

### 5. 12 个开源框架 Skill 哲学
- Tool-as-Skill（LangGraph/CrewAI）→ Role-as-Skill（MetaGPT/ChatDev）→ Program-as-Skill（DSPy）
- **DSPy 唯一将自迭代作为一等公民**：Signature→Module→Optimizer

### 6. 科学计算 Agent 为独立子方向
- GRAFT-ATHENA / NORA / EvoDS / FermiLink 等专门面向科学发现的 Agent
- COMSOL Java 是 optics_agent 的**天然技能载体**
- 物理验证是终极瓶颈

## optics_agent 改进路线图

| 阶段 | 关键动作 | 时间 |
|------|---------|------|
| 近期 | Skill 元数据标准化 + 自动校验 + 失败模式编码 | 1-2 周 |
| 中期 | 工作流 DSL + 角色 Agent + 经验池 | 1-2 月 |
| 长期 | 技能自动创建 + 反思层 + 多 Agent 对话图 | 3-6 月 |

详见 `optics_agent_mapping.md`

## MCP 搜索执行统计
- Arxiv 搜索查询：~30 次（D1-D8 方向），max_results=50
- 新发现论文：~150 篇（去重后），其中 50+ 篇为之前 webfetch 未覆盖的
- 关键新增：Skill Ret/Shadowing/Skill-as-Pseudocode/Library Drift/SkillDAG 等最新 skill 系统论文
- 科学计算 Agent：FermiLink, MIND, LARA, OpenFOAMGPT, Battery-Sim-Agent 等 optics 相关论文
