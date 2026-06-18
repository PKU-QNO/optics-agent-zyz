# Skill System 架构

> 调研日期：2026-06-18

## 核心发现

| 维度 | 发现 |
|------|------|
| **标准抽象层** | Skill 已成为 Agent 架构的标准抽象层——Anthropic SKILL.md 规范已成事实标准，被 Claude Code、OpenAI Codex、Gemini CLI、Cursor 等采纳 |
| **注册中心** | 社区驱动（tech-leads-club/agent-skills 4.6k⭐）与企业自托管（iflytek/skillhub 3.5k⭐）两种模式并存；Observal (2.1k⭐) 添加沙箱+分析能力 |
| **安全风险** | AgentGuard (429⭐) 专攻恶意 skill 检测；26.1% 社区 skill 存在漏洞（arXiv:2601.10338）；组合安全风险被严重低估——22.25% 技能对存在组合风险（2606.00448），SCR_Bench 发现单个无害 skill 组合后可能有害 |
| **技能获取** | 三种范式并存：手工编写（主流）、RL 组合学习（PRIME-RL/RL-Compositionality）、从 GitHub 自动挖掘（arXiv:2603.11808） |
| **渐进式暴露** | 所有 skill 系统的核心性能模式：先加载轻量指令(name+description) → 按需暴露完整内容/代码 |
| **组合路由** | EMNLP 2026 有 Compositional Skill Routing 专门研究，研究 skill 的自动选择与组合路径 |
| **MCP 关系** | Skill 与 MCP 互补：Skill 定义"做什么"（能力包），MCP 定义"怎么访问外部资源"（工具/数据访问协议） |
| **多 Agent 技能** | Swarm Skills 将多 Agent 工作流作为可分发资产，含自进化算法 |
| **标准规范** | SKILL.md 已成事实标准，社区 42,447+ 公开技能包 |
| **模块化框架** | Haystack (25.6k⭐), Griptape (2.5k⭐), MoFA (Rust), ADK-Rust (467⭐) |
| **学术调查** | "Agent Skills for LLMs" 系统综述 (arXiv:2602.12430) 提出 4 轴框架：架构基础、获取、部署、安全 |
| **Skill 粒度** | 原子技能（单工具调用）vs 复合技能（多步工作流）|
| **Skill-First 架构** | Agent 核心变为轻量级编排器，所有领域能力外化到可插拔 Skill 模块（OpenPersonalAgent, Swarm Skills, STEM Agent）|

## 关键仓库

| 仓库 | Star | 核心特性 |
|------|------|---------|
| tech-leads-club/agent-skills | 4.6k⭐ | 安全、验证的社区 skill registry |
| iflytek/skillhub | 3.5k⭐ | 企业自托管 skill registry，RBAC 审计 |
| deepset-ai/haystack | 25.6k⭐ | 模块化 AI 编排框架 |
| griptape-ai/griptape | 2.5k⭐ | 带推理/工具/记忆的 agent 框架 |
| GoPlusSecurity/agentguard | 429⭐ | Skill 安全检测专用工具 |
| rscheiwe/open-skills | 31⭐ | 动态 skill 发现/选择/执行 |
| frank-luongt/faos-skills-marketplace | 22⭐ | 930+ skill 市场 |

## 关键论文

| 论文 | ID | 核心贡献 |
|------|----|---------|
| **Agent Skills for LLMs: Architecture, Acquisition, Security** | arXiv:2602.12430 | 4 轴系统综述（架构基础、获取、部署、安全）|
| **SoK: Agentic Skills — 7 Design Patterns** | arXiv:2602.20867 | 总结 7 种 skill 设计模式 |
| **Towards Secure Agent Skills** | arXiv:2604.02837 | 安全威胁分类 |
| **From Human Guidance to Autonomy: Agent Skill System** | arXiv:2606.07586 | 8 阶段 skill 全生命周期流程 |
| **STEM Agent** | arXiv:2603.22359 | 自适应 skill 成熟生命周期 |
| **Swarm Skills** | arXiv:2605.10052 | 可移植自进化多 Agent 系统 |
| **Automating Skill Acquisition through Large-Scale Mining** | arXiv:2603.11808 | 从 GitHub 自动挖掘技能 |
| **LEGO: LLM Skill-Based EDA Platform** | arXiv:2604.23355 | 领域技能 RAG |
| **Compositional Skill Routing** | EMNLP 2026 | Skill 的自动选择与组合路径 |

## 设计模式

SoK: Agentic Skills (arXiv:2602.20867) 总结的 7 种设计模式：

| # | 模式 | 描述 | optics_agent 对应 |
|---|------|------|-------------------|
| 1 | **Metadata-driven progressive disclosure** | 先加载 name+description，按需加载完整 SKILL.md | 当前 SKILL.md 已有基本格式，需补充元数据（version/dependencies/last_updated）|
| 2 | **Executable code skills** | Skill 内容含可直接执行的代码 | COMSOL Java 代码是天然的可执行 skill 载体 |
| 3 | **Self-evolving libraries** | 自动演化 skill 库，轨迹蒸馏→技能→任务→自演化 | 长期目标：Socratic-SWE 风格闭环 |
| 4 | **Marketplace distribution** | 社区市场分发 | tech-leads-club/agent-skills (4.6k⭐) |
| 5 | **Representation×Scope taxonomy** | NL / Code / Policy / Hybrid 四种表示 | COMSOL Java + 自然语言描述混合 |
| 6 | **Compositional skill synthesis** | 组合已有 skill 创造新能力 | 需引入 DAG 编排（AgentSkillOS 模式）|
| 7 | **Trust-tiered execution** | 基于来源的安全分级执行 | 需引入 allow/deny/ask 权限模型 |

## 安全分析

- **社区 skill 漏洞率高**：26.1% 社区 skill 存在安全漏洞（arXiv:2601.10338）
- **组合攻击面**：SCR_Bench 发现单个无害 skill 组合后可能产生有害行为；22.25% 技能对存在组合风险（SkillReact, arXiv:2606.00448）
- **专用检测工具**：AgentGuard (429⭐) 专攻恶意 skill 检测
- **沙箱执行**：Observal (2.1k⭐) 在 registry 层面添加沙箱执行和分析能力
- **企业级控制**：iflytek/skillhub (3.5k⭐) 提供 RBAC 审计
- **科学计算特殊性**：形式化验证（SEVerA, arXiv:2603.25111）对科学计算可靠性至关重要；科学仿真代码的安全性涉及物理正确性而非仅代码注入

## MCP 关系

| 维度 | Skill | MCP |
|------|-------|-----|
| **定义** | "做什么"——能力包（领域知识+执行逻辑） | "怎么访问"——工具/数据访问协议 |
| **粒度** | 原子或复合能力单元 | 单工具/数据源接口 |
| **关系** | **互补**：Skill 封装领域逻辑，MCP 提供外部资源访问通道 |
| **编排** | Skill 可调用 MCP 工具实现外部交互 |
| **标准化** | SKILL.md 标准（Anthropic 事实标准） | MCP 协议标准（Anthropic 发起） |
| **opencode 支持** | 原生支持目录自动发现 | 原生支持 MCP 协议 |

## 注册与发现

**两种主流模式：**

| 模式 | 代表 | 特点 | 适用场景 |
|------|------|------|---------|
| **社区 Registry** | tech-leads-club/agent-skills (4.6k⭐) | 开放、安全验证、42,447+ 公开技能包 | 通用 skill 共享 |
| **企业自托管** | iflytek/skillhub (3.5k⭐) | RBAC 审计、私有部署 | 企业内部 skill 管理 |

**发现机制对比（SWE Agent）：**

| Agent | 发现机制 |
|-------|---------|
| **opencode** | 目录自动发现（项目+全局），`AGENTS.md` 路由表 |
| **Claude Code** | 项目根 `CLAUDE.md` + 自动记忆系统 |
| **Cursor** | 项目根 `.cursorrules` + `.cursor/rules/` |
| **open-skills** | 动态 skill 发现/选择/执行 |

**渐进式暴露模式（所有 skill 系统共享）：**
1. 先加载轻量元数据（name + description）
2. 按需加载完整 SKILL.md 指令
3. 按需加载关联代码/资源文件
4. 执行时按权限策略控制

## 与 optics_agent 的关系

**当前状态：**
- 已有 8 个手工 Skill（core, paper-reproduction, comsol-runtime, comsol-batch, comsol-java-api, magnus-platform, magnus-artifacts, docker-images）
- 正确事项：技能路由表、NTFS 同步、验证脚本、标准报告格式、失败状态码定义、Java 参考库

**核心差距分析：**

| 维度 | 当前 | 前沿 | 差距 |
|------|------|------|------|
| 注册/发现 | 静态 AGENTS.md 路由表 | Voyager 语义检索技能库 | 严重 |
| 组合/编排 | 手动顺序提示 | DSPy 管道、CrewAI 层级编排 | 严重 |
| 自迭代 | 手工 handoff 文档 | Socratic-SWE 闭环自演化 | 严重 |
| 多 Agent 协作 | 单 Agent | MetaGPT 角色分工 | 严重 |
| 评估/验证 | 人工判断 success 类型 | AgentBench 自动化评测 | 严重 |
| 元认知/反思 | 事后 final_report.md | Reflexion 运行中反思 | 中等 |
| 工作流自动化 | submit_comsol.py 单入口 | Prefect 有状态工作流引擎 | 中等 |

**设计模式映射：**

| SoK 模式 | optics_agent 当前 | 改进方向 |
|----------|------------------|---------|
| Metadata-driven progressive disclosure | SKILL.md 基本格式 | 补充 version/dependencies/last_updated (近期) |
| Executable code skills | COMSOL Java 代码（天然载体） | 完善 Java 代码的 skill 封装 |
| Self-evolving libraries | 无 | Socratic-SWE 风格闭环（长期蓝图）|
| Marketplace distribution | 无 | 可对接 agent-skills 社区 |
| Representation×Scope taxonomy | NL+Code 混合 | 补充 Policy/Hybrid 表示 |
| Compositional skill synthesis | 手动顺序调用 | DAG 编排引擎（中期目标）|
| Trust-tiered execution | 无显式权限 | allow/deny/ask 模型（近期）|

**opencode 作为宿主：**
opencode 是目前最系统化的开源 Agent Skill 框架——同时支持 opencode/claude/agents 三个命名空间、细粒度权限控制、目录自动发现、MCP 集成、multi-path 发现，是 optics_agent skill 系统的理想宿主平台。
