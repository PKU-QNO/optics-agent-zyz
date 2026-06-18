# Agent Skill 系统与工作流自迭代：前沿调研

> 调研日期：2026-06-18
> 目标：系统梳理 AI Agent 的 Skill 系统设计、工作流自迭代机制的前沿实践与学术进展，为 optics_agent 项目提供设计参考。

---

## 1. 核心概念 & Taxonomy

### 1.1 Skill 定义
- **Skill** = Agent 可调用的原子能力单元，封装特定领域知识 + 执行逻辑
- 粒度：原子技能（单工具调用） vs 复合技能（多步工作流）
- 前沿共识：Skill 已成为 Agent 架构的**标准抽象层**（Anthropic SKILL.md 规范已成为事实标准，被 Claude Code、OpenAI Codex、Gemini CLI、Cursor 等采纳）

### 1.2 Skill 系统组件
- **Skill 注册 / 发现** — 社区 registry (tech-leads-club/agent-skills 4.6k⭐) 和企业自托管 (iflytek/skillhub 3.5k⭐) 两种模式
- **Skill 路由 / 选择** — 渐进式暴露（Progressive Disclosure）：先加载轻量指令 → 按需暴露重代码/资源；Compositional Skill Routing (EMNLP 2026)
- **Skill 组合 / 编排** — 安全风险被低估（SCR_Bench：单个无害 skill 组合后可能有害）；MCP + Skills 互补（Skill 定义"做什么"，MCP 定义"怎么访问外部资源"）
- **Skill 学习 / 优化** — 手工/RL/自动挖掘三种范式

### 1.3 自迭代定义
- Agent 从执行历史中学习 -> 改进自身行为 -> 形成正反馈循环
- 层次：单步反思 -> 工作流优化 -> 技能库演进

### 1.4 关键架构模式
- **Skill-First 架构**：Agent 核心变为轻量级编排器，所有领域能力外化到可插拔 Skill 模块（OpenPersonalAgent, Swarm Skills, STEM Agent）
- **多 Agent 技能协调**：单 Agent Skill 可标准化分发，但多 Agent 协作协议仍锁定在框架内部；Swarm Skills 提出将多 Agent 工作流作为可分发资产
- **渐进式暴露**：SKILL.md（指令）→ 代码/资源文件 → 按需执行

---

## 2. Web / Blog 实践调研

### 2.1 Skill System 架构 (W1) — 8 变体词，92 唯一 repo + 16 papers

#### 核心发现
| 维度 | 发现 |
|------|------|
| 注册中心 | tech-leads-club/agent-skills (4.6k⭐) 社区驱动；iflytek/skillhub (3.5k⭐) 企业自托管；Observal (2.1k⭐) 添加沙箱 + 分析 |
| 安全分析 | AgentGuard (429⭐) 专攻恶意 skill 检测；26.1% 社区 skill 存在漏洞（arXiv:2601.10338）|
| 技能获取 | 手工编写（主流）→ RL 组合学习（PRIME-RL/RL-Compositionality）→ 从 GitHub 自动挖掘（arXiv:2603.11808）|
| 模块化框架 | Haystack (25.6k⭐), Griptape (2.5k⭐), MoFA (Rust), ADK-Rust (467⭐) |
| 学术调查 | "Agent Skills for LLMs" 系统综述 (arXiv:2602.12430)：4 轴框架（架构基础、获取、部署、安全）|
| 技能组合 | EMNLP 2026 有 Compositional Skill Routing 专门研究；SCR_Bench 发现组合攻击面 |
| MCP 关系 | MCP 标准化工具/数据访问协议，Skill 标准化能力包；两者互补 |
| 多Agent 技能 | Swarm Skills 将多 Agent 工作流作为可分发资产，含自进化算法 |
| 标准规范 | SKILL.md 已成事实标准（Anthropic），社区 42,447+ 公开技能包 |

#### 关键仓库列表
- tech-leads-club/agent-skills (4.6k⭐) — 安全、验证的 skill registry
- iflytek/skillhub (3.5k⭐) — 企业自托管 skill registry，RBAC 审计
- deepset-ai/haystack (25.6k⭐) — 模块化 AI 编排框架
- griptape-ai/griptape (2.5k⭐) — 带推理/工具/记忆的 agent 框架
- GoPlusSecurity/agentguard (429⭐) — skill 安全检测
- rscheiwe/open-skills (31⭐) — 动态 skill 发现/选择/执行
- frank-luongt/faos-skills-marketplace (22⭐) — 930+ skill 市场

#### 关键论文
- "Agent Skills for LLMs: Architecture, Acquisition, Security" (arXiv:2602.12430) — 系统综述
- "Towards Secure Agent Skills" (arXiv:2604.02837) — 安全威胁分类
- "From Human Guidance to Autonomy: Agent Skill System" (arXiv:2606.07586) — 8 阶段 skill 流程
- "STEM Agent" (arXiv:2603.22359) — 自适应的 skill 成熟生命周期
- "Swarm Skills" (arXiv:2605.10052) — 可移植自进化多 Agent 系统
- "Automating Skill Acquisition through Large-Scale Mining" (arXiv:2603.11808)
- "LEGO: LLM Skill-Based EDA Platform" (arXiv:2604.23355) — 领域 skill RAG

---

### 2.2 Self-Improving / Self-Iteration (W2) — 8 变体词，~40 有效论文/项目

#### 三大基础范式
| 范式 | 代表工作 | 核心思路 |
|------|---------|---------|
| **Reflexion** | Reflexion (Shinn 2023) | 口头RL+记忆反思，HumanEval 91% pass@1 |
| **STaR** | STaR (Zelikman 2022) | 自举推理+正确率过滤，迭代训练 |
| **Self-Refine** | Self-Refine (Madaan 2023) | 自我反馈+迭代精炼，7项任务平均~20%提升 |

#### 关键发现
- **探索-利用平衡**：探索能力在迭代中迅速退化，需动态分配采样预算到边界难度（B-STaR, HS-STaR, AdaSTaR）
- **外部反馈优于自我反馈**：自我反馈单独导致递归漂移；外部验证器/批评者必不可少
- **技能库+记忆**：EvoDS、CatDT、SCALE 均依赖持久可复用技能存储
- **验证器组件不可或缺**：V-STaR (DPO), AgenticRL (GPT critic), ARIS (adversarial review)
- **安全退化风险**：ANCHOR 发现自主进化可能导致能力退化和安全漂移
- **提示级进化是轻量手段**：CPE 仅通过 prompt refinement 实现改进；SGDe 编译确定性结构到小模型
- **Meta-Agent 能力仍有限**：MAC 基准显示 agent 很少匹敌人类程序，高优化压力下出现对抗行为
- **多Agent对抗协作**：跨模型 executor-reviewer (ARIS)、三角色对抗 (SCALE)

#### 关键论文
- Reflexion (2303.11366) — 言语强化学习开创者
- STaR (2203.14465) — 自教推理
- Self-Refine (2303.17651) — 自我反馈迭代精炼
- Voyager (2305.16291) — 开放式技能发现
- Meta-Policy Reflexion (2509.03990) — 结构化元策略记忆
- MAR: Multi-Agent Reflexion (2512.20845) — 多Agent反思

---

### 2.3 Tool Use & Composition (W3) — 8 变体词，40 唯一论文

#### 三大关键转变
1. **从 skill → skill tree/ecosystem**：构建结构化、可组合、可演化的技能树，通过树搜索+DAG编排实现技能发现
2. **从 stateless → persistent "Workspace + Skill"**：持久化运行时（Python 状态内核、记忆系统、Workspace）
3. **从单一准确率 → 多目标 Pareto 优化**：效率+安全性+认知开销+完成质量联合优化

#### 核心发现
- **Skill Tree 搜索成主流**：OpenClaw-Skill (2606.16774) 多模型协作树搜索构建可复用技能树
- **代码即动作接口收敛**：SpatialClaw (2606.13673), CaveAgent (2601.01569) 维护有状态 Python 运行时
- **经验知识分三阶段**：KATE (2606.10875) 发现知识获取→激活→内化，实例级知识优于意图级
- **记忆机制成工具调用核心**：MemToolAgent (2606.07909) 结构化记忆检索无需微调提升29%
- **多目标优化**：ParetoPO (2606.16111, ICML 2026) 将效率与准确率作为竞争目标
- **课程学习是关键杠杆**：SKILL0 (2604.02268) 全技能上下文逐步退出；Tool-R0 (2602.21320) Generator-Solver 共演化
- **元认知工具使用**：HDPO/Metis (2604.08545) 解耦准确率和效率通道
- **工具描述质量成瓶颈**：Trace-Free+ (2602.20426) 发现 agent 能力受限于接口描述
- **组合安全风险**：22.25% 技能对存在组合风险 (2606.00448)

#### 关键论文
- OpenClaw-Skill (2606.16774) — 协作技能树搜索
- ParetoPO (2606.16111, ICML 2026) — 多目标工具优化
- KATE (2606.10875) — 经验知识三阶段理论
- MemToolAgent (2606.07909) — 记忆驱动工具调用
- SKILL0 (2604.02268) — 技能内化课程学习
- AgentSkillOS (2603.02176) — DAG 技能编排
- SpatialClaw (2606.13673) — 代码即动作接口
- Tool-R0 (2602.21320) — 零数据自演化工具学习
- HDPO/Metis (2604.08545) — 元认知工具使用

---

### 2.4 Meta-Cognition & Reflection (W4) — 8 变体词，85 去重论文

#### 关键发现
- **Self-Refine 范式已成基础**：但会放大 self-bias (2402.11436)，更大模型和外部反馈可缓解
- **元认知架构呈分层趋势**：Sophia 的 System 3（持久身份层）、SMARt 的四层状态机、DS-MCM 双速监控
- **元认知与 RL 深度耦合**：E-SPL (2602.14697) 联合进化系统提示+RL权重；MMPO (2605.30159) 信念熵自监督
- **CoT 从链式→树→图**：Tree of Thoughts (2305.10601)、ReasoningFlow (2606.05402) DAG 推理轨迹
- **7种通用推理算子**：ReasonOps (2605.29192) backtracking, inferring, hypothesizing 等
- **LLM 规划是短视的**：Extracting Search Trees (2605.06840) 性能由搜索广度而非深度预测
- **小模型元认知局限**："Right for Wrong Reasons" (2601.00513) 50-69% 正确含缺陷推理，self-critique 有害
- **自验证从被动→主动**：SmartSnap (2512.22322) 主动现场验证；FineVerify (2606.00660) 细粒度子问题分解
- **多Agent 反思缓解退化**：MAR (2512.20845) 单 LLM 反思陷入思维退化
- **置信度校准与弃权**：Pause and Reflect (2605.14098) 共形风险控制，5%弃权率下选择性准确率90.1%

#### 关键论文
- Self-Refine (2303.17651) — 自精炼开创
- Tree of Thoughts (2305.10601, NeurIPS 2023) — CoT→树搜索
- Sophia (2512.18202) — System 3 元认知层
- DOLORES (2605.11388) — 形式语言元推理，8B超越32B
- MedCoG (2602.07905, ICML 2026) — 医学元认知
- ReasonOps (2605.29192) — 7种推理算子
- Self-Bias in Self-Refinement (2402.11436) — 自偏见的发现
- ReVeal (2506.11442) — 自验证代码Agent，20+轮进化
- SmartSnap (2512.22322) — 主动现场自验证
- FineVerify (2606.00660) — 细粒度自验证搜索

---

### 2.5 Arxiv 论文综合 (P1-P2) — 6 搜索词，77 论文

#### 与 optics_agent 最相关论文 (Top 8)
| 论文 | ID | 相关性 | 核心贡献 |
|------|----|--------|---------|
| **GRAFT-ATHENA** | 2605.11117 | ⭐⭐⭐⭐⭐ | 科学发现领域 self-improving agent |
| **NORA** | 2605.02092 | ⭐⭐⭐⭐⭐ | Skills-first 科学领域 agent 架构 |
| **SADE** | 2605.04530 | ⭐⭐⭐⭐⭐ | 领域知识→技能库编码方法论 |
| **EvoDS** | 2606.03841 | ⭐⭐⭐⭐⭐ | 科学工作流自动化+技能自学习 |
| **SkillGraph** | 2605.12039 | ⭐⭐⭐⭐ | 技能依赖图，适合多物理场建模 |
| **GRASP** | 2605.29668 | ⭐⭐⭐⭐ | Regression budget 确保安全改进 |
| **PACE** | 2605.23019 | ⭐⭐⭐⭐ | 小模型双时间尺度自我进化 |
| **SEVerA** | 2603.25111 | ⭐⭐⭐⭐ | 形式化验证保障科学计算可靠性 |

#### 系统发现
- 科学/工程领域的 Agent 技能系统正在形成独立子方向
- Skills-first 架构特别适合需要多步工作流的科学计算场景
- 技能依赖图 (SkillGraph) 与 COMSOL 多物理场工作流天然匹配
- 形式化验证 (SEVerA) 对科学计算可靠性至关重要

---

### 2.6 SWE Agent 实践 (W5) — 8 变体词，20+ 论文/文档

#### 主流 SWE Agent Skill 系统对比
| 维度 | opencode | Claude Code | Cursor | Devin |
|------|----------|-------------|--------|-------|
| 格式 | `SKILL.md` + YAML frontmatter | Markdown skill + `CLAUDE.md` + auto memory | `.cursorrules` + `.cursor/rules/` | 闭源 |
| 发现机制 | 目录自动发现（项目+全局） | 项目根+自动记忆 | 项目根 .cursorrules | 闭源 |
| 权限控制 | allow/deny/ask + wildcard + per-agent | 第三方集成 | 无显式权限 | 闭源 |
| MCP 集成 | 原生支持 MCP | 原生支持 MCP | 通过 VS Code 扩展 | 通过 ACP 协议 |
| 兼容性 | 兼容 Claude/Agents 路径 | 不兼容其他 | 不兼容 | 闭源 |
| 开源 | Apache 2.0 | 闭源（免费使用） | 闭源 | 闭源 |
| 自迭代 | 通过 AGENTS.md 持久指令 | auto memory + skills | .cursorrules 手动维护 | 闭源自迭代 |

#### SWE Agent 自迭代关键模式
| 模式 | 代表论文 | 核心思路 |
|------|----------|---------|
| 轨迹蒸馏 | Socratic-SWE (2606.07412) | 从历史求解轨迹提取结构化 skill，指导修复任务，3轮迭代SWE-bench 50.40% |
| RL Skill 提取 | CODESKILL (2605.25430) | RL 管理 skill 提取和 skill-bank 维护，密集+稀疏混合奖励 |
| 无外部标注进化 | RHO (2606.05922) | 自验证+自一致性+自我偏好，SWE-Bench Pro 59%→78% |
| 群组进化 | GEA (2602.04837) | Agent 群体作为演化单元，经验共享，SWE-bench 71.0% |
| 结构化记忆 | MemCoder (2603.13258) | 意图-代码映射 + 自我修正 + 经验内化 |
| 递归自我设计 | MetaAI Recursive (2606.09663) | Darwin Goedel 机器，80次迭代 20%→50% SWE-bench |

#### 关键发现
- **opencode 是目前最系统化的开源 Agent Skill 框架**：同时支持 opencode/claude/agents 三个命名空间，细粒度权限控制
- **渐进式上下文加载是所有 skill 系统的核心模式**：只加载 name+description，按需加载完整内容
- **七种 Skill 设计模式**：arXiv:2602.20867 SoK 综述总结 metadata-driven progressive disclosure、executable code skills、self-evolving libraries、marketplace distribution 等
- **Subagent 架构**：主 agent 规划+推理，子 agent 执行（搜索/调试/终端），token 节省 ~30%
- **阶段化轨迹分解 Search→Read→Edit**：60-69% 失败是 Edit-Quality 问题，非 Localization (2603.24631)
- **ACP 协议成为 Agent 互操作开放标准**：opencode + Devin Desktop 均支持
- **SWE-bench 生态快速膨胀**：从 Lite→Verified→Live→Pro→Mobile→5G，2023.10 1.96%→2026.04 78.4%

#### 关键论文/文档
- opencode docs (opencode.ai/docs/skills/) — Skill 系统官方文档
- Claude Code docs (docs.anthropic.com) — Skills 官方文档
- SoK: Agentic Skills (2602.20867) — 7 种设计模式
- Socratic-SWE (2606.07412) — 闭环自进化编码 Agent
- CODESKILL (2605.25430) — RL 提取编码技能
- RHO (2606.05922) — 无标注自进化
- GEA (2602.04837) — 群组进化 Agent
- Coherence Collapse (2603.24631) — Agent 失败原因分析
- MetaAI Recursive (2606.09663) — 递归自我设计
- From Translation to Superset (2604.11518) — Codex CLI 架构

---

### 2.7 开源框架对比 (W6) — 10 框架深度对比

#### 框架 Skill 系统哲学对比
| 哲学 | 代表框架 | 特点 |
|------|---------|------|
| **Tool-as-Skill** | LangGraph, CrewAI, AutoGen | 工具即技能，灵活需外部编排 |
| **Role-as-Skill** | MetaGPT, ChatDev | 角色自带技能边界，灵活性受限 |
| **Program-as-Skill** | DSPy | 编译式 LM 编程，自动优化策略 |

#### 自迭代能力排名
| 框架 | 自迭代能力 | 核心机制 |
|------|-----------|---------|
| **DSPy** | ⭐⭐⭐⭐⭐ 核心特性 | Optimizer 自动调优 prompt/权重 |
| **ChatDev** | ⭐⭐⭐⭐ 经验重用 | Co-Learning + IER 经验累积 |
| **Agno** | ⭐⭐⭐⭐ 平台级 | Auto-improving 平台教程 |
| **MetaGPT** | ⭐⭐⭐ 研究级 | AFlow 自动化 workflow 生成 (ICLR 2025 Oral) |
| **LangGraph** | ⭐⭐ 外部 | LangSmith tracing + HITL |
| **CrewAI** | ⭐ 有限 | Telemetry 可观测性 |
| **AutoGen** | ⭐ 有限 | Bench 评估，维护模式 |

#### 关键发现
- **DSPy 唯一将自迭代作为一等公民**：Signature→Module→Optimizer 编译器式管道
- **CrewAI 的 Crew+Flow 双模式当前最优**：Crew 自治协作 + Flow 精确控制，可嵌套
- **MetaGPT 的"软件公司隐喻"**：天然 Skill 分工框架，但 Role 结构固定后扩展成本高
- **Semantic Kernel Plugin 系统最企业级**：同时支持 Native/Prompt/OpenAPI/MCP 四种扩展
- **ChatDev 零代码可视化编排**：最适合非技术人员，支持 DAG/条件分支/循环
- **LangGraph Subgraph 嵌套+状态持久化**：最成熟的长运行 Agent

---

### 2.8 Agent 协作/演化/编排/基准 (P5-P8) — ~50 论文深度覆盖

#### Agent 协作关键发现
| 发现 | 论文 | 对 optics_agent 启示 |
|------|------|-------------------|
| 简单通信协议比课程学习更有效 | (2510.05748) 协作率 0%→96.7% | Agent 间通信协议设计优先于复杂训练 |
| 能力分解优于单一大模型 | (2401.07324) planner/caller/summarizer | COMSOL 建模/求解/后处理分解为子 Agent |
| 企业多 Agent 协作 90% 成功率 | (2412.05449) AWS Bedrock | COMSOL-Magnus 工作流编排参考架构 |
| 多 Agent 辩论缓解思维退化 | MAR (2512.20845) | 多角色辩论产生多样化反思 |

#### Self-Evolution 关键发现
| 发现 | 论文 | 对 optics_agent 启示 |
|------|------|-------------------|
| 自演化综述统一框架 | (2508.07407) 输入→Agent→环境→优化器 | 长期蓝图理论框架 |
| 形式化验证保障 | SEVerA (2603.25111) GRPO+验证 | 科学计算必须形式化验证 |
| 长期记忆安全风险 | Zombie Agents (2602.15654) | session 间记忆需安全隔离 |
| 从失败中学习 | (2402.11651) 失败轨迹改进微调 | COMSOL 失败仿真自动积累 |

#### 编排模式关键发现
| 发现 | 论文 | 对 optics_agent 启示 |
|------|------|-------------------|
| 声明式 DSL 分离规范与执行 | (2512.19769) 开发时间减 60% | COMSOL 工作流声明式配置 |
| 动态难度感知编排 | DAAO (2509.11079) | 简单/复杂仿真不同策略 |
| 不确定性下编排理论保证 | (2605.27073) O(√T) regret | Agent 调度引入在线学习框架 |
| Agent 编排故障实证 | (2509.23735) 307 真实故障 | 建立故障监控+自动回退 |

#### 基准评估关键发现
| 发现 | 论文 | 对 optics_agent 启示 |
|------|------|-------------------|
| SWE-bench 生态膨胀 | Live/Pro/Mobile/5G | 关注防污染方法论 |
| 20% "solved" patch 实际错误 | SWE-ABS (2603.00520) | 必须区分 pipeline 完成和物理复现 |
| 框架设计比模型更重要 | Claw-SWE (2606.12344) 差异 6x | 谨慎 benchmark Agent 框架 |
| 元 Agent 能力仍有限 | MAC (2606.04455) | Agent 自改进上限需评估 |
| MCP Agent 评估 | MCP-AgentBench (2509.09734) | MCP 协议 Agent 标准化评估 |

---

## 3. 关键论文精读 (16 篇深度解析)

### 3.1 最高相关度论文（optics_agent 设计蓝图）

#### 1. Voyager (2305.16291) — 开放式技能发现范式
- **核心**：Minecraft 中通过 GPT-4 驱动 Agent 自动探索、技能迭代、课程式学习
- **三大组件**：自动课程（根据技能水平逐步提高任务难度）、技能库（Code-as-Skill，每次成功生成可执行代码存入）、迭代提示（失败时自动反思修正）
- **关键创新**：技能库使用语义嵌入检索（text-embedding-ada-002），自动课程通过"发现新事物"驱动，无需人工奖励函数
- **对 optics_agent**：Code-as-Skill + 技能库范式可直接映射——COMSOL Java 代码作为 skill 载体，每次成功的仿真脚本自动入库

#### 2. Reflexion (2303.11366) — 语言反馈替代权重更新
- **核心**：Actor（生成动作）+ Evaluator（评估结果）+ Memory（存储经验）三元组
- **关键创新**：通过自然语言反馈强化 agent，无需模型微调；三种记忆模式：短期（当前轨迹）、长期（跨 session 经验）、自反射（结构化反思）
- **HumanEval 91% pass@1**：证明语言反馈可以达到甚至超过 RL 效果
- **对 optics_agent**：失败仿真脚本 → 语言反思 → 自动修正工作流，无需重训模型

#### 3. SWE-agent (2405.15793) — Agent-Computer Interface 范式
- **核心**：ACI（Agent-Computer Interface）设计——不是让 Agent 适应工具，而是设计工具接口适配 Agent
- **关键组件**：文件查看器（逐行+上下文窗口）、编辑器（替换而非追加）、执行 shell（状态隔离）
- **SWE-bench 12.5% pass@1**（当时 SOTA）
- **对 optics_agent**：Magnus 提交接口 → ACI 重新设计，COMSOL CLI 输出解析器适配 Agent

#### 4. Self-Refine (2303.17651) — 同一 LLM 三角色
- **核心**：同一 LLM 同时扮演生成器（Generator）、反馈器（Feedback）、精炼器（Refiner）
- **7项任务平均提升 ~20%**；无需外部监督或微调
- **后续发现**：Pride and Prejudice (2402.11436) 发现 self-bias 问题，更大模型和外部反馈可缓解
- **对 optics_agent**：论文复现报告生成后，Agent 自动审查并从数值合理性角度自我修正

#### 5. Generative Agents (2304.03442) — 社交 Agent 架构
- **核心**：25 个 Agent 在 Stanford 小镇自由活动，展现涌现社交行为
- **四大组件**：记忆流（所有经历的流式记录）、检索（相关性+时间+重要性加权）、反射（高层次抽象）、计划（逐级分解）
- **对 optics_agent**：多 Agent 角色设计（建模师/求解师/分析师）可借鉴此架构

#### 6. MetaGPT (2308.00352) — SOP 流水线
- **核心**：软件公司角色分工（PM/架构师/工程师/测试），SOP = Code(Team)
- **68.9k stars**，ICLR 2025 有 AFlow 自动化 workflow 生成
- **对 optics_agent**：COMSOL 仿真 SOP 映射为角色流水线（物理阅读→建模→求解→后处理→报告）

#### 7. Socratic-SWE (2606.07412) — 闭环自进化编码 Agent
- **核心**：从历史求解轨迹提取结构化 agent skills → 指导生成针对性修复任务 → execution-based validation → 更新 solver
- **SWE-bench Verified 50.40%**（3 轮迭代）
- **对 optics_agent**：长期架构直接蓝图——每次 COMSOL 仿真轨迹自动演化 skill

#### 8. SoK: Agentic Skills (2602.20867) — 7 种设计模式
- **7 patterns**：metadata-driven progressive disclosure, executable code skills, self-evolving libraries, marketplace distribution, representation×scope taxonomy, compositional skill synthesis, trust-tiered execution
- **对 optics_agent**：设计模式可直接映射到现有 8 个 skill 的重构

### 3.2 重要支撑论文
| 论文 | 核心 | 对 optics_agent |
|------|------|----------------|
| **STaR** (2203.14465) | 自举推理，正确率过滤生成训练数据 | 失败轨迹作为反面教材训练 agent |
| **Toolformer** (2302.04761) | 自监督决定何时调用何 API | COMSOL API 调用的自监督学习 |
| **ReAct** (2210.03629) | 推理-行动交织，现代 agent 基础 | 所有 agent 架构的基础模式 |
| **Code as Policies** (2209.07753) | Code 作为策略表示，自然语言→代码 | COMSOL Java 代码作为动作策略 |
| **AutoGen** (2308.08155) | 多 Agent 对话框架 | 角色 Agent 间通信协议 |
| **ChatDev** (2307.07924) | 零代码多 Agent 编排 | 可视化工作流编排参考 |
| **AgentBench** (2308.03688) | 8 维度 Agent 评估 | agent 能力评估方法论 |
| **DSPy** (2310.03714) | 签名→模块→优化器，编译式 LM 编程 | 声明式工作流 DSL 的设计参考 |

### 3.3 跨论文核心发现
1. **技能范式演进路径**：静态库(Voyager) → 闭环自演化(Socratic-SWE)，optics_agent 应直接采纳后者
2. **代码作为统一技能表示**是跨论文共识，COMSOL Java 是 optics_agent 的天然技能载体
3. **ReAct 推理-行动交织**是一切现代 agent 的基础模式
4. **外部验证器/批评者** 是所有自迭代系统的必备组件
5. **渐进式上下文加载**是所有 skill 系统共享的核心性能模式
6. **多 Agent 角色专业化** 在复杂工作流中比单 agent 更鲁棒

---

## 4. 工程模式汇总

### 4.1 Skill 系统设计模式（SoK 综述 7 种）
1. **Metadata-driven progressive disclosure** — 先加载 name+description，按需加载完整 SKILL.md
2. **Executable code skills** — Skill 内容含可直接执行的代码（COMSOL Java）
3. **Self-evolving libraries** — 自动演化 skill 库（Socratic-SWE 轨迹蒸馏→技能→任务→自演化）
4. **Marketplace distribution** — 社区市场分发（tech-leads-club/agent-skills 4.6k⭐）
5. **Representation×Scope taxonomy** — NL / Code / Policy / Hybrid 四种表示
6. **Compositional skill synthesis** — 组合已有 skill 创造新能力
7. **Trust-tiered execution** — 基于来源的安全分级执行

### 4.2 Agent 自迭代架构模式
| 模式 | 适用场景 | 代表工作 |
|------|---------|---------|
| 口头 RL（语言反馈+记忆） | 单步决策改进 | Reflexion |
| 轨迹蒸馏 | 多步工作流优化 | Socratic-SWE, CODESKILL |
| 三阶段自验证 | 输出质量保证 | Self-Refine, FineVerify |
| 群组进化 | 多 Agent 协作优化 | GEA |
| 递归自我设计 | 架构层进化 | MetaAI Recursive |
| 无标注自优化 | 无验证集场景 | RHO |

### 4.3 主流框架 Skill 哲学
| 哲学 | 代表 | 优点 | 缺点 | optics_agent 选择 |
|------|------|------|------|-----------------|
| Tool-as-Skill | LangGraph/CrewAI | 灵活 | 需外部编排 | 短期：采用此模式 |
| Role-as-Skill | MetaGPT/ChatDev | 自带分工 | 灵活性受限 | 中期：引入角色分工 |
| Program-as-Skill | DSPy | 自动优化 | 学习曲线陡 | 长期：编译式管道 |

### 4.4 SWE Agent 的关键工程教训
- **60-69% 失败是 Edit-Quality 问题**，非 Localization — 优化补丁生成质量
- **框架设计比模型更重要** — 同一模型在不同框架上性能差 6x
- **20% "solved" patch 实际语义错误** — 必须多维度验证
- **Subagent 节省 ~30% token** — 主 agent 规划，子 agent 执行

---

## 5. optics_agent 项目映射

### 5.1 现有 Skill 系统状态
- **8 个 Skill**：core, paper-reproduction, comsol-runtime, comsol-batch, comsol-java-api, magnus-platform, magnus-artifacts, docker-images
- **正确事项**：技能路由表、NTFS 同步、验证脚本、标准报告格式、失败状态码定义、Java 参考库
- **核心差距**：无动态注册/发现、无自动组合/编排、无自迭代、无多 Agent 协作、无自动评估

### 5.2 差距分析（严重项）
| 维度 | 当前 | 前沿 | 差距 |
|------|------|------|------|
| 注册/发现 | 静态 AGENTS.md 路由表 | Voyager 语义检索技能库 | 严重 |
| 组合/编排 | 手动顺序提示 | DSPy 管道、CrewAI 层级 | 严重 |
| 自迭代 | 手工 handoff 文档 | Socratic-SWE 闭环自演化 | 严重 |
| 多 Agent 协作 | 单 Agent | MetaGPT 角色分工 | 严重 |
| 评估/验证 | 人工判断 success 类型 | AgentBench 自动化评测 | 严重 |
| 元认知/反思 | 事后 final_report.md | Reflexion 运行中反思 | 中等 |
| 工作流自动化 | submit_comsol.py 单入口 | Prefect 有状态工作流引擎 | 中等 |

### 5.3 与前沿论文的具体映射
| 前沿工作 | 核心思想 | optics_agent 对应 | 差距 | 优先级 |
|----------|---------|-------------------|------|--------|
| **Voyager** | 自动技能发现/迭代 | 现有 8 个手工 skill | 无自动技能创建 | 中长期 |
| **Reflexion** | 自我反思+重试 | `final_report.md` 事后文档 | 无运行中反思 | 中期 |
| **Socratic-SWE** | 轨迹蒸馏→自演化 | 无对应 | 缺失闭环引擎 | 长期 |
| **DSPy** | 声明式管道+自动优化 | 无管道抽象 | 无声明式 DSL | 中期 |
| **MetaGPT** | 多角色分工 | 单 Agent | 无角色分离 | 中期 |
| **CrewAI** | 层级团队编排 | 无 | 无需编排框架 | 中长期 |
| **SoK Skills** | 7 种设计模式 | SKILL.md 基本格式 | 无元数据/权限/自我演化 | 近期 |
| **SWE-agent ACI** | Agent-Computer Interface | 无 | Magnus 接口未适配 Agent | 中期 |

### 5.4 改进路线图

**近期（1-2 周）— 快速夯实基础**
1. **Skill 元数据标准化** — 给每个 SKILL.md 加 `version`, `dependencies`, `last_updated`（~2 小时）
2. **自动校验脚本** — `validate_all_skills.py` 统一验证所有 skill + AGENTS.md 路由表一致性（~1 天）
3. **失败模式编码化** — 矩阵分解失败自动进入"请求 GUI 模板"状态（~4 小时）
4. **AGENTS.md 依赖图** — Mermaid 标注技能间依赖关系（~1 小时）

**中期（1-2 月）— 管道化 + 角色化**
1. **工作流 DSL** — YAML 定义复现管道（`.repro.yaml`），步骤映射到 skill（~1 周）
2. **执行引擎** — `repro_runner.py` 解析执行 YAML 管道（~1 周）
3. **验证节点** — 程序化检查 `Im(neff)` 非零、数值范围、`surrogate_fallback` 标记（~3 天）
4. **角色 Agent 模板** — paper-reader, model-builder, magnus-submitter, result-validator（~2 周）
5. **经验池** — `.codex/experience/` 自动追加失败模式+检索机制（~2 天）

**长期（3-6 月）— 自适应 + 自进化**
1. **技能自动创建** — 从失败分析自动生成新 skill 文件（~1 月）
2. **反思层** — Reflexion 风格任务自评 → 技能差异补丁（~3 周）
3. **多 Agent 对话图** — AutoGen/CrewAI 集成（~1 月）
4. **技能语义检索** — 嵌入索引自动路由（~2 月）
5. **全自动物理验证** — 预期曲线 vs 计算结果匹配评分（~3 月）

---

## 6. 启发性想法与 Next Steps

### 6.1 最值得立即采纳的 5 个想法
1. **Skill 元数据标准化**（2 小时）— skill frontmatter + AGENTS.md 依赖图联动
2. **反射式失败编码**（4 小时）— 将 Degiron v2 矩阵分解失败模式正式写入技能
3. **简易工作流 DSL**（1 周）— YAML 定义 extract→generate→submit→parse→validate→report
4. **角色 Agent 路由**（2 周）— paper-reader/model-builder/magnus-submitter/result-validator
5. **经验池自动追加**（2 天）— 每次失败 COMSOL 任务自动写入经验文件

### 6.2 科学计算 Agent 的特殊设计需求（vs 通用 SWE Agent）
| 维度 | SWE Agent | 科学计算 Agent (optics_agent) |
|------|-----------|------------------------------|
| 目标 | 功能正确 | 物理正确 |
| 验证方式 | 单元测试/集成测试 | 物理规律一致性 + 数值收敛性 |
| 工作流特点 | 逐步修复 | 参数化流水线 |
| 计算成本 | 低（秒级） | 高（小时级仿真） |
| 领域壁垒 | 编程语言语法 | 多物理场耦合 + API 深度 |
| 可复现性要求 | 可接受概率性 | 必须确定性能复现 |
| 从失败学习 | bug 修复模式 | 仿真配置参数调优 |

### 6.3 对 optics_agent 的深层启示
1. **COMSOL Java 是 optics_agent 的天然技能载体** — Code-as-Skill 范式的最佳映射，可直接采用 Voyager 模式
2. **Voyager 的"自动课程"可映射为"自动复杂度递增"** — 简单几何→多物理场耦合→全参数扫描
3. **Swarm Skills 自进化算法 + AgentSkillOS DAG 编排** → optics_agent 的未来技能架构
4. **Socratic-SWE 的轨迹蒸馏闭环** → 每次 COMSOL 仿真自动优化下一个 skill
5. **DSPy 编译器式 LM 编程哲学** → optics_agent 用声明式 YAML 替代隐式 prompt 编排
6. **openCode 本身是 optics_agent skill 系统的理想宿主** — 已提供目录自动发现、MCP 集成、权限控制、multi-path 发现
7. **物理验证是终极瓶颈** — 自动化架构再先进，没有 GR 团队的标准答案也无法判断进展
8. **外部验证器不可或缺** — Reflexion/Self-Refine/SWE-agent 共识：自反馈导致递归漂移，需外部批评者

### 6.4 关键开放性问题的引用
- "自我反馈单独使用会导致递归漂移"（Self-Bias, 2402.11436）
- "Agent 框架设计比底层模型更重要"（Claw-SWE, 2606.12344，性能差 6x）
- "技能组合安全风险被严重低估"（SkillReact, 2606.00448，22.25% 技能对有组合风险）
- "探索能力在迭代中迅速退化"（B-STaR, AdaSTaR — 需动态分配采样预算）
- "元 Agent 能力仍有限，很少匹敌人类专家"（MAC, 2606.04455）
- "简单通信协议比复杂训练更有效"（2510.05748，协作率 0%→96.7%）
- "LLM 规划是短视的，由搜索广度而非深度预测"（2605.06840）
- "80% 自验证引用可被操纵值欺骗"（2603.12564）

---

## 7. 参考文献

### Web / Blog 引用
- opencode Skill 系统文档: https://opencode.ai/docs/skills/
- Claude Code Skills 文档: https://code.claude.com/docs/skills
- Claude Code Overview: https://docs.anthropic.com/en/docs/claude-code/overview
- tech-leads-club/agent-skills: https://github.com/tech-leads-club/agent-skills
- iflytek/skillhub: https://github.com/iflytek/skillhub
- GoPlusSecurity/agentguard: https://github.com/GoPlusSecurity/agentguard
- deepset-ai/haystack: https://github.com/deepset-ai/haystack
- griptape-ai/griptape: https://github.com/griptape-ai/griptape

### Arxiv 论文引用
- Voyager (2305.16291) — Wang et al., NeurIPS 2023
- Reflexion (2303.11366) — Shinn et al., NeurIPS 2023
- Generative Agents (2304.03442) — Park et al., 2023
- SWE-agent (2405.15793) — Yang et al., 2024
- Self-Refine (2303.17651) — Madaan et al., 2023
- Toolformer (2302.04761) — Schick et al., 2023
- ReAct (2210.03629) — Yao et al., ICLR 2023
- STaR (2203.14465) — Zelikman et al., 2022
- Code as Policies (2209.07753) — Liang et al., 2023
- AutoGen (2308.08155) — Wu et al., 2023
- ChatDev (2307.07924) — Qian et al., 2023
- MetaGPT (2308.00352) — Hong et al., 2023
- AgentBench (2308.03688) — Liu et al., ICLR 2024
- DSPy (2310.03714) — Khattab et al., 2023
- SoK: Agentic Skills (2602.20867) — 2026
- Agent Skills Survey (2602.12430) — Xu & Yan, 2026
- Towards Secure Agent Skills (2604.02837) — 2026
- STEM Agent (2603.22359) — 2026
- Swarm Skills (2605.10052) — 2026
- EvoDS (2606.03841) — 2026
- Socratic-SWE (2606.07412) — 2026
- CODESKILL (2605.25430) — 2026
- RHO (2606.05922) — 2026
- GEA (2602.04837) — 2026
- MemCoder (2603.13258) — 2026
- Self-Evolving Survey (2508.07407) — 2025
- SEVerA (2603.25111) — 2026
- Coherence Collapse (2603.24631) — 2026
- Agentic SDLC Survey (2604.26275) — 2026
- MAC (2606.04455) — 2026
- SkillReact (2606.00448) — 2026
- OpenClaw-Skill (2606.16774) — 2026
- ParetoPO (2606.16111) — 2026
- KATE (2606.10875) — 2026
- SKILL0 (2604.02268) — 2026
- AgentSkillOS (2603.02176) — 2026
- Sophia (2512.18202) — 2025
- DOLORES (2605.11388) — 2026
- MedCoG (2602.07905) — ICML 2026
- Communication Enables Cooperation (2510.05748) — 2025
