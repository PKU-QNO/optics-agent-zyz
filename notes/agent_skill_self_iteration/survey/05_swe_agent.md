# SWE Agent 实践

> 调研日期：2026-06-18

## 主流 SWE Agent Skill 系统对比

| 维度 | opencode | Claude Code | Cursor | Devin |
|------|----------|-------------|--------|-------|
| 格式 | `SKILL.md` + YAML frontmatter | Markdown skill + `CLAUDE.md` + auto memory | `.cursorrules` + `.cursor/rules/` | 闭源 |
| 发现机制 | 目录自动发现（项目+全局） | 项目根+自动记忆 | 项目根 .cursorrules | 闭源 |
| 权限控制 | allow/deny/ask + wildcard + per-agent | 第三方集成 | 无显式权限 | 闭源 |
| MCP 集成 | 原生支持 MCP | 原生支持 MCP | 通过 VS Code 扩展 | 通过 ACP 协议 |
| 兼容性 | 兼容 Claude/Agents 路径 | 不兼容其他 | 不兼容 | 闭源 |
| 开源 | Apache 2.0 | 闭源（免费使用） | 闭源 | 闭源 |
| 自迭代 | 通过 AGENTS.md 持久指令 | auto memory + skills | .cursorrules 手动维护 | 闭源自迭代 |

## SWE Agent 自迭代关键模式

| 模式 | 代表论文 | 核心思路 |
|------|----------|---------|
| 轨迹蒸馏 | Socratic-SWE (2606.07412) | 从历史求解轨迹提取结构化 skill，指导修复任务，3轮迭代SWE-bench 50.40% |
| RL Skill 提取 | CODESKILL (2605.25430) | RL 管理 skill 提取和 skill-bank 维护，密集+稀疏混合奖励 |
| 无外部标注进化 | RHO (2606.05922) | 自验证+自一致性+自我偏好，SWE-Bench Pro 59%→78% |
| 群组进化 | GEA (2602.04837) | Agent 群体作为演化单元，经验共享，SWE-bench 71.0% |
| 结构化记忆 | MemCoder (2603.13258) | 意图-代码映射 + 自我修正 + 经验内化 |
| 递归自我设计 | MetaAI Recursive (2606.09663) | Darwin Goedel 机器，80次迭代 20%→50% SWE-bench |

## 关键发现

- **opencode 是目前最系统化的开源 Agent Skill 框架**：同时支持 opencode/claude/agents 三个命名空间，细粒度权限控制
- **渐进式上下文加载是所有 skill 系统的核心模式**：只加载 name+description，按需加载完整内容
- **七种 Skill 设计模式**：arXiv:2602.20867 SoK 综述总结 metadata-driven progressive disclosure、executable code skills、self-evolving libraries、marketplace distribution 等
- **Subagent 架构**：主 agent 规划+推理，子 agent 执行（搜索/调试/终端），token 节省 ~30%
- **阶段化轨迹分解 Search→Read→Edit**：60-69% 失败是 Edit-Quality 问题，非 Localization (2603.24631)
- **ACP 协议成为 Agent 互操作开放标准**：opencode + Devin Desktop 均支持
- **SWE-bench 生态快速膨胀**：从 Lite→Verified→Live→Pro→Mobile→5G，2023.10 1.96%→2026.04 78.4%

## SWE-bench 生态

- **演化路径**：Lite → Verified → Live → Pro → Mobile → 5G
- **性能提升**：2023.10 1.96% → 2026.04 78.4%
- **防污染方法论**：生态快速膨胀，需关注 benchmark 污染问题
- **20% "solved" patch 实际错误** (SWE-ABS, 2603.00520)：必须区分 pipeline 完成和物理复现成功
- **框架设计比模型更重要** (Claw-SWE, 2606.12344)：同一模型在不同框架上性能差 6x

## SWE-agent (2405.15793) — Agent-Computer Interface 范式

- **核心**：ACI（Agent-Computer Interface）设计——不是让 Agent 适应工具，而是设计工具接口适配 Agent
- **关键组件**：文件查看器（逐行+上下文窗口）、编辑器（替换而非追加）、执行 shell（状态隔离）
- **SWE-bench 12.5% pass@1**（当时 SOTA）
- **对 optics_agent**：Magnus 提交接口 → ACI 重新设计，COMSOL CLI 输出解析器适配 Agent

## 关键工程教训

- **60-69% 失败是 Edit-Quality 问题**，非 Localization — 优化补丁生成质量
- **框架设计比模型更重要** — 同一模型在不同框架上性能差 6x
- **20% "solved" patch 实际语义错误** — 必须多维度验证
- **Subagent 节省 ~30% token** — 主 agent 规划，子 agent 执行

## 关键论文/文档

- SWE-agent (2405.15793) — Yang et al., 2024
- Socratic-SWE (2606.07412) — 闭环自进化编码 Agent
- CODESKILL (2605.25430) — RL 提取编码技能
- RHO (2606.05922) — 无标注自进化
- GEA (2602.04837) — 群组进化 Agent
- MemCoder (2603.13258) — 结构化记忆 Agent
- MetaAI Recursive (2606.09663) — 递归自我设计
- Coherence Collapse (2603.24631) — Agent 失败原因分析
- SoK: Agentic Skills (2602.20867) — 7 种设计模式
- From Translation to Superset (2604.11518) — Codex CLI 架构
- opencode docs (opencode.ai/docs/skills/) — Skill 系统官方文档
- Claude Code docs (docs.anthropic.com) — Skills 官方文档

## 与 optics_agent 的关系

| 维度 | SWE Agent | 科学计算 Agent (optics_agent) |
|------|-----------|------------------------------|
| 目标 | 功能正确 | 物理正确 |
| 验证方式 | 单元测试/集成测试 | 物理规律一致性 + 数值收敛性 |
| 工作流特点 | 逐步修复 | 参数化流水线 |
| 计算成本 | 低（秒级） | 高（小时级仿真） |
| 领域壁垒 | 编程语言语法 | 多物理场耦合 + API 深度 |
| 可复现性要求 | 可接受概率性 | 必须确定性能复现 |
| 从失败学习 | bug 修复模式 | 仿真配置参数调优 |

**核心启示**：
- SWE Agent 的 ACI 设计思路可直接用于 Magnus 提交接口和 COMSOL CLI 输出解析器的改造
- Socratic-SWE 的轨迹蒸馏闭环是 optics_agent 长期自迭代蓝图的直接参考——每次 COMSOL 仿真轨迹自动演化 skill
- Subagent 架构节省 ~30% token 的经验可迁移至 COMSOL 建模/求解/后处理的角色分解
- 但需注意：SWE Agent 的 benchmark 成功不等于物理复现成功，必须建立独立的物理验证标准
