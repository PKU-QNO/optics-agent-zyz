# Tool Use & Composition

> 调研日期：2026-06-18

## 三大关键转变

1. **从 skill → skill tree/ecosystem**：构建结构化、可组合、可演化的技能树，通过树搜索+DAG编排实现技能发现
2. **从 stateless → persistent "Workspace + Skill"**：持久化运行时（Python 状态内核、记忆系统、Workspace）
3. **从单一准确率 → 多目标 Pareto 优化**：效率+安全性+认知开销+完成质量联合优化

## 核心发现

- **Skill Tree 搜索成主流**：OpenClaw-Skill (2606.16774) 多模型协作树搜索构建可复用技能树
- **代码即动作接口收敛**：SpatialClaw (2606.13673), CaveAgent (2601.01569) 维护有状态 Python 运行时
- **经验知识分三阶段**：KATE (2606.10875) 发现知识获取→激活→内化，实例级知识优于意图级
- **记忆机制成工具调用核心**：MemToolAgent (2606.07909) 结构化记忆检索无需微调提升29%
- **多目标优化**：ParetoPO (2606.16111, ICML 2026) 将效率与准确率作为竞争目标
- **课程学习是关键杠杆**：SKILL0 (2604.02268) 全技能上下文逐步退出；Tool-R0 (2602.21320) Generator-Solver 共演化
- **元认知工具使用**：HDPO/Metis (2604.08545) 解耦准确率和效率通道
- **工具描述质量成瓶颈**：Trace-Free+ (2602.20426) 发现 agent 能力受限于接口描述
- **组合安全风险**：22.25% 技能对存在组合风险 (2606.00448)

## 关键论文

| 论文 | ID | 核心贡献 |
|------|----|---------|
| OpenClaw-Skill | 2606.16774 | 协作技能树搜索 |
| ParetoPO | 2606.16111 (ICML 2026) | 多目标工具优化 |
| KATE | 2606.10875 | 经验知识三阶段理论 |
| MemToolAgent | 2606.07909 | 记忆驱动工具调用 |
| SKILL0 | 2604.02268 | 技能内化课程学习 |
| AgentSkillOS | 2603.02176 | DAG 技能编排 |
| SpatialClaw | 2606.13673 | 代码即动作接口 |
| Tool-R0 | 2602.21320 | 零数据自演化工具学习 |
| HDPO/Metis | 2604.08545 | 元认知工具使用 |

## Code-as-Skill 范式

**Code as Policies** (Liang et al., 2209.07753) — Code 作为策略表示，自然语言→代码。对 optics_agent：COMSOL Java 代码作为动作策略的直接映射。

**Voyager** (Wang et al., 2305.16291, NeurIPS 2023) — 开放式技能发现范式。三大组件：自动课程、技能库（Code-as-Skill，每次成功生成可执行代码存入）、迭代提示。技能库使用语义嵌入检索（text-embedding-ada-002）。对 optics_agent：Code-as-Skill + 技能库范式可直接映射，COMSOL Java 代码作为 skill 载体，每次成功的仿真脚本自动入库。

**ReAct** (Yao et al., 2210.03629, ICLR 2023) — 推理-行动交织，现代 agent 基础模式。所有 agent 架构的基础模式，opencode、Claude Code 等均基于此。

**Toolformer** (Schick et al., 2302.04761) — 自监督决定何时调用何 API。对 optics_agent：COMSOL API 调用的自监督学习参考。

**SpatialClaw** (2606.13673) / **CaveAgent** (2601.01569) — 维护有状态 Python 运行时，代码即动作接口。

## 函数调用与 MCP

- **MCP + Skills 互补**：Skill 定义"做什么"，MCP 定义"怎么访问外部资源"
- **MCP 标准化工具/数据访问协议**，Skill 标准化能力包
- **ACP 协议成为 Agent 互操作开放标准**：opencode + Devin Desktop 均支持
- **MCP-AgentBench** (2509.09734) — MCP 协议 Agent 标准化评估

## 组合安全风险

- **22.25% 技能对存在组合风险**（SkillReact, 2606.00448）
- **SCR_Bench** 发现组合攻击面：单个无害 skill 组合后可能有害
- **26.1% 社区 skill 存在漏洞**（arXiv:2601.10338）
- **AgentGuard** (429⭐) 专攻恶意 skill 检测
- 对 optics_agent：代码生成 skill（COMSOL Java）+ 执行 skill（Magnus 提交）的组合需安全审查

## 与 optics_agent 的关系

现有关联：
- COMSOL Java 是 optics_agent 的天然技能载体，Code-as-Skill 范式的最佳映射
- ReAct 推理-行动交织是现代 agent 基础模式，opencode 本身即采用此架构
- MCP 集成已在 opencode 中原生支持

差距：
- 无持久化 Workspace/Skill 运行时
- 无技能树搜索或 DAG 编排（AgentSkillOS 模式）
- 无多目标优化（当前仅关注 pipeline 完成，未优化安全/效率/认知开销）
- 工具调用无记忆机制，每次 session 从零开始

近期可采用：
1. 引入记忆机制存失败模式（Reflexion 风格）
2. COMSOL Java skill 代码化（Code-as-Skill 完整实现）
3. 声明式工作流 DSL 替代隐式 prompt 编排
