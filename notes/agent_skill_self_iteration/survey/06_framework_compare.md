# 开源框架对比

> 调研日期：2026-06-18
> 来源：agent_skill_self_iteration.md §2.7, §2.8, §3, §4.3

## 框架 Skill 系统哲学

开源 Agent 框架的 Skill 系统可分为三大哲学流派：

| 哲学 | 代表框架 | 特点 |
|------|---------|------|
| **Tool-as-Skill** | LangGraph, CrewAI, AutoGen | 工具即技能，灵活但需外部编排 |
| **Role-as-Skill** | MetaGPT, ChatDev | 角色自带技能边界，天然分工但灵活性受限 |
| **Program-as-Skill** | DSPy | 编译式 LM 编程，Signature→Module→Optimizer 自动优化策略 |

### 哲学对比（含 optics_agent 路径）

| 哲学 | 代表 | 优点 | 缺点 | optics_agent 选择 |
|------|------|------|------|-----------------|
| Tool-as-Skill | LangGraph/CrewAI | 灵活 | 需外部编排 | **短期**：采用此模式 |
| Role-as-Skill | MetaGPT/ChatDev | 自带分工 | 灵活性受限 | **中期**：引入角色分工 |
| Program-as-Skill | DSPy | 自动优化 | 学习曲线陡 | **长期**：编译式管道 |

## 自迭代能力排名

| 框架 | 自迭代能力 | 核心机制 |
|------|-----------|---------|
| **DSPy** | ⭐⭐⭐⭐⭐ 核心特性 | Optimizer 自动调优 prompt/权重 |
| **ChatDev** | ⭐⭐⭐⭐ 经验重用 | Co-Learning + IER 经验累积 |
| **Agno** | ⭐⭐⭐⭐ 平台级 | Auto-improving 平台教程 |
| **MetaGPT** | ⭐⭐⭐ 研究级 | AFlow 自动化 workflow 生成 (ICLR 2025 Oral) |
| **LangGraph** | ⭐⭐ 外部 | LangSmith tracing + HITL |
| **CrewAI** | ⭐ 有限 | Telemetry 可观测性 |
| **AutoGen** | ⭐ 有限 | Bench 评估，维护模式 |

## 详细对比

### DSPy — ⭐⭐⭐⭐⭐

- **架构**：Compiler 式 LM 编程，Signature→Module→Optimizer 管道
- **自迭代**：Optimizer 自动调优 prompt/权重，自迭代作为一等公民
- **组合方式**：声明式管道组合，自动优化策略
- **模式**：Program-as-Skill，将 LM 调用视为可编译程序
- **适用**：需要自动 prompt 优化的场景；对声明式工作流 DSL 有参考价值（§3.2）
- **optics_agent 映射**：声明式 YAML 替代隐式 prompt 编排（§6.3-5）
- **局限**：学习曲线陡峭，面向 NLP/文本任务多于科学计算

### ChatDev — ⭐⭐⭐⭐

- **架构**：零代码多 Agent 可视化编排，支持 DAG/条件分支/循环
- **自迭代**：Co-Learning + IER 经验累积机制，经验重用
- **组合方式**：角色化多 Agent 协作，可视化 DAG 编排
- **模式**：Role-as-Skill，每个角色有独立技能边界
- **适用**：非技术人员可视化工作流构建；多 Agent 编排参考（§3.2）
- **optics_agent 映射**：可视化工作流编排参考（§3.3-6）
- **局限**：灵活性受限于角色定义，扩展成本高

### Agno — ⭐⭐⭐⭐

- **架构**：平台级 Agent 框架，内置 auto-improving 能力
- **自迭代**：平台教程级自优化
- **组合方式**：平台内置组合机制
- **适用**：需要平台级管理能力的场景

### MetaGPT — ⭐⭐⭐

- **架构**：软件公司角色分工（PM/架构师/工程师/测试），SOP = Code(Team)，68.9k⭐
- **自迭代**：AFlow 自动化 workflow 生成（ICLR 2025 Oral）
- **组合方式**：SOP 流水线角色协作（§3.1-6）
- **模式**：Role-as-Skill，角色天然定义技能边界
- **适用**：复杂软件开发流水线模拟；多 Agent 角色设计参考（§3.2）
- **optics_agent 映射**：COMSOL 仿真 SOP 映射为角色流水线：物理阅读→建模→求解→后处理→报告（§3.1-6）
- **局限**：Role 结构固定后扩展成本高

### LangGraph — ⭐⭐

- **架构**：图状态机 Agent 框架，Subgraph 嵌套 + 状态持久化
- **自迭代**：外部依赖 LangSmith tracing + HITL
- **组合方式**：图结构编排，最成熟的长运行 Agent
- **模式**：Tool-as-Skill
- **适用**：复杂长运行 Agent 流程；需要状态持久化的场景
- **关键优势**：Subgraph 嵌套 + 状态持久化，最成熟的长运行 Agent（§2.7 关键发现）

### CrewAI — ⭐

- **架构**：Crew+Flow 双模式，Crew 自治协作 + Flow 精确控制，可嵌套
- **自迭代**：仅有 Telemetry 可观测性
- **组合方式**：层级团队编排
- **模式**：Tool-as-Skill
- **适用**：简单的多 Agent 协作场景
- **关键优势**：Crew+Flow 双模式当前最优——Crew 自治协作 + Flow 精确控制（§2.7 关键发现）

### AutoGen — ⭐

- **架构**：多 Agent 对话框架
- **自迭代**：Bench 评估，维护模式
- **组合方式**：Agent 对话驱动协作
- **模式**：Tool-as-Skill（§3.2）
- **适用**：多 Agent 对话/谈判场景
- **局限**：当前处于维护模式，框架演进缓慢

### Semantic Kernel

- **架构**：微软企业级 AI 编排框架
- **编排**：Plugin 系统最企业级，同时支持 Native/Prompt/OpenAPI/MCP 四种扩展（§2.7 关键发现）
- **定位**：企业级应用场景，非自迭代优先

## 关键发现

1. **DSPy 唯一将自迭代作为一等公民**：Signature→Module→Optimizer 编译器式管道，其他框架自迭代多为附加功能
2. **CrewAI 的 Crew+Flow 双模式当前最优**：Crew 自治协作 + Flow 精确控制，可嵌套，兼顾灵活与可控
3. **MetaGPT 的"软件公司隐喻"**：天然 Skill 分工框架，但 Role 结构固定后扩展成本高
4. **Semantic Kernel Plugin 系统最企业级**：同时支持 Native/Prompt/OpenAPI/MCP 四种扩展
5. **ChatDev 零代码可视化编排**：最适合非技术人员，支持 DAG/条件分支/循环
6. **LangGraph Subgraph 嵌套+状态持久化**：最成熟的长运行 Agent
7. **框架设计比模型更重要**：同一模型在不同框架上性能差 6x（Claw-SWE, 2606.12344，§4.4）
8. **Agent 协作中简单通信协议比课程学习更有效**：协作率 0%→96.7%（2510.05748，§2.8）
9. **能力分解优于单一大模型**：planner/caller/summarizer 分解模式（2401.07324，§2.8）
10. **声明式 DSL 分离规范与执行**：开发时间减 60%（2512.19769，§2.8）

## Agent 协作与编排发现

| 发现 | 论文 | 启示 |
|------|------|------|
| 简单通信协议比课程学习更有效 | (2510.05748) 协作率 0%→96.7% | Agent 间通信协议设计优先于复杂训练 |
| 能力分解优于单一大模型 | (2401.07324) planner/caller/summarizer | COMSOL 建模/求解/后处理分解为子 Agent |
| 企业多 Agent 协作 90% 成功率 | (2412.05449) AWS Bedrock | COMSOL-Magnus 工作流编排参考架构 |
| 多 Agent 辩论缓解思维退化 | MAR (2512.20845) | 多角色辩论产生多样化反思 |
| 声明式 DSL 分离规范与执行 | (2512.19769) 开发时间减 60% | COMSOL 工作流声明式配置 |
| 动态难度感知编排 | DAAO (2509.11079) | 简单/复杂仿真不同策略 |
| 不确定性下编排理论保证 | (2605.27073) O(√T) regret | Agent 调度引入在线学习框架 |
| Agent 编排故障实证 | (2509.23735) 307 真实故障 | 建立故障监控+自动回退 |

## 框架选择建议

| 需求场景 | 推荐框架 | 原因 |
|---------|---------|------|
| 自动 Prompt 优化 | **DSPy** | 唯一将自迭代作为一等公民 |
| 非技术人员可视化编排 | **ChatDev** | 零代码 DAG/条件分支/循环 |
| 复杂长运行 Agent | **LangGraph** | 最成熟的 Subgraph 嵌套+状态持久化 |
| 快速多 Agent 原型 | **CrewAI** | Crew+Flow 双模式最灵活 |
| 企业级 Plugin 集成 | **Semantic Kernel** | 4 种扩展方式最企业级 |
| 软件流水线模拟 | **MetaGPT** | 最成熟的角色分工框架 |
| 多 Agent 对话/谈判 | **AutoGen** | 专注对话驱动协作 |
| 需要平台级管理 | **Agno** | 内置 auto-improving 平台能力 |

## 与 optics_agent 的关系

optics_agent 的长期 Skill 系统应该融合三种哲学的优点：

- **短期**：Tool-as-Skill 模式，将现有 8 个 Skill 作为工具集使用
- **中期**：引入 Role-as-Skill 角色分工（paper-reader, model-builder, magnus-submitter, result-validator），参考 MetaGPT 的 SOP 流水线
- **长期**：Program-as-Skill 编译式管道，以 DSPy 的 Signature→Module→Optimizer 为蓝图设计声明式 YAML 工作流 DSL

具体映射建议：
- **编排引擎参考**：CrewAI 的 Crew+Flow 双模式 + LangGraph 的状态持久化
- **自迭代参考**：DSPy Optimizer 哲学 + ChatDev 经验重用
- **角色分工参考**：MetaGPT 的 SOP 流水线模式
- **Agent 通信**：遵循"简单通信协议优于复杂训练"原则（2510.05748）
- **能力分解**：planner/caller/summarizer 模式，将 COMSOL 建模/求解/后处理分解为子 Agent
