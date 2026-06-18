# Self-Improving / Self-Iteration

> 调研日期：2026-06-18
> 来源：notes/agent_skill_self_iteration.md §2.2, §2.6, §2.8, §4.2, §6.3

## 三大基础范式

| 范式 | 代表工作 | 核心思路 | 关键指标 |
|------|---------|---------|---------|
| **Reflexion** | Reflexion (Shinn 2023, NeurIPS 2023) | 口头 RL + 记忆反思，Actor-Evaluator-Memory 三元组；语言反馈替代权重更新，无需模型微调 | HumanEval 91% pass@1 |
| **STaR** | STaR (Zelikman 2022) | 自举推理 + 正确率过滤，迭代训练；失败轨迹作为反面教材 | 自教推理奠基工作 |
| **Self-Refine** | Self-Refine (Madaan 2023) | 同一 LLM 同时扮演 Generator-Feedback-Refiner；无需外部监督或微调 | 7 项任务平均 ~20% 提升 |

### 三种记忆模式（Reflexion）
- **短期**：当前轨迹
- **长期**：跨 session 经验
- **自反射**：结构化反思

### Self-Refine 后续发现
- Pride and Prejudice (2402.11436) 发现 **self-bias 问题**：自我反馈单独导致递归漂移
- 更大模型和外部反馈可缓解 self-bias

## 自迭代架构模式

| 模式 | 适用场景 | 代表工作 |
|------|---------|---------|
| **口头 RL（语言反馈 + 记忆）** | 单步决策改进 | Reflexion |
| **轨迹蒸馏** | 多步工作流优化 | Socratic-SWE, CODESKILL |
| **三阶段自验证** | 输出质量保证 | Self-Refine, FineVerify |
| **群组进化** | 多 Agent 协作优化 | GEA |
| **递归自我设计** | 架构层进化 | MetaAI Recursive |
| **无标注自优化** | 无验证集场景 | RHO |
| **提示级进化** | 轻量改进 | CPE（仅通过 prompt refinement 实现改进） |

## 关键发现

### 探索-利用平衡（来自§2.2）
- 探索能力在迭代中 **迅速退化**
- 需动态分配采样预算到边界难度（B-STaR, HS-STaR, AdaSTaR）

### 验证器与外部反馈（来自§2.2）
- **外部反馈优于自我反馈**：自我反馈单独导致递归漂移；外部验证器/批评者必不可少
- V-STaR (DPO), AgenticRL (GPT critic), ARIS (adversarial review) 均依赖外部验证器
- 跨模型 executor-reviewer (ARIS)、三角色对抗 (SCALE)

### 技能库与记忆（来自§2.2）
- EvoDS、CatDT、SCALE 均依赖**持久可复用技能存储**
- Meta-Policy Reflexion (2509.03990) 提出结构化元策略记忆

### Self-Evolution 关键发现（来自§2.8）
| 发现 | 论文 | 启示 |
|------|------|------|
| 自演化综述统一框架 | (2508.07407) 输入→Agent→环境→优化器 | 长期蓝图理论框架 |
| 形式化验证保障 | SEVerA (2603.25111) GRPO+验证 | 科学计算必须形式化验证 |
| 长期记忆安全风险 | Zombie Agents (2602.15654) | session 间记忆需安全隔离 |
| 从失败中学习 | (2402.11651) 失败轨迹改进微调 | COMSOL 失败仿真自动积累 |

### 元能力上限（来自§2.2, §2.8）
- **Meta-Agent 能力仍有限**：MAC 基准 (2606.04455) 显示 agent 很少匹敌人类程序
- 高优化压力下出现对抗行为

### 跨论文共识（来自§3.3）
1. **技能范式演进路径**：静态库(Voyager) → 闭环自演化(Socratic-SWE)
2. **代码作为统一技能表示** 是跨论文共识
3. **外部验证器/批评者** 是所有自迭代系统的必备组件
4. **多 Agent 角色专业化** 在复杂工作流中比单 agent 更鲁棒

### 深层启示（来自§6.3）
- COMSOL Java 是 optics_agent 的天然技能载体（Code-as-Skill）
- Voyager 的"自动课程"可映射为"自动复杂度递增"
- Socratic-SWE 的轨迹蒸馏闭环 → 每次 COMSOL 仿真自动优化下一个 skill
- **物理验证是终极瓶颈** — 自动化架构再先进，没有 GR 团队的标准答案也无法判断进展
- **外部验证器不可或缺** — Reflexion/Self-Refine/SWE-agent 共识

## 关键论文

### 基础范式开创
| 论文 | ID | 贡献 |
|------|----|------|
| Reflexion | 2303.11366 | 言语强化学习开创者，Actor-Evaluator-Memory 三元组 |
| STaR | 2203.14465 | 自教推理，正确率过滤生成训练数据 |
| Self-Refine | 2303.17651 | 同一 LLM 三角色（生成+反馈+精炼） |
| Voyager | 2305.16291 | 开放式技能发现，Code-as-Skill 范式，NeurIPS 2023 |

### 进阶自迭代
| 论文 | ID | 贡献 |
|------|----|------|
| Meta-Policy Reflexion | 2509.03990 | 结构化元策略记忆 |
| MAR: Multi-Agent Reflexion | 2512.20845 | 多 Agent 反思缓解思维退化 |
| Socratic-SWE | 2606.07412 | 闭环自进化编码 Agent，轨迹蒸馏 → 技能，SWE-bench 50.40% |
| CODESKILL | 2605.25430 | RL 管理 skill 提取 + skill-bank 维护 |
| RHO | 2606.05922 | 无标注自进化（自验证 + 自一致性 + 自我偏好） |
| GEA | 2602.04837 | 群组进化 Agent，经验共享，SWE-bench 71.0% |
| MetaAI Recursive | 2606.09663 | 递归自我设计，Darwin Goedel 机器，80 次迭代 20%→50% |
| MemCoder | 2603.13258 | 意图-代码映射 + 自我修正 + 经验内化 |

### Self-Evolution 相关
| 论文 | ID | 贡献 |
|------|----|------|
| Self-Evolving Survey | 2508.07407 | 自演化综述统一框架 |
| SEVerA | 2603.25111 | 形式化验证保障科学计算可靠性 |
| GRASP | 2605.29668 | Regression budget 确保安全改进 |
| PACE | 2605.23019 | 小模型双时间尺度自我进化 |

### 相关支撑论文
| 论文 | ID | 贡献 |
|------|----|------|
| Self-Bias in Self-Refinement | 2402.11436 | 发现 self-bias，更大模型和外部反馈可缓解 |
| ReVeal | 2506.11442 | 自验证代码 Agent，20+ 轮进化 |
| Coherence Collapse | 2603.24631 | Agent 失败原因分析：60-69% 是 Edit-Quality 问题 |
| MAC | 2606.04455 | 元 Agent 能力上限评估 |

## SWE Agent 自迭代模式

| 模式 | 代表论文 | 核心思路 | 关键指标 |
|------|----------|---------|---------|
| **轨迹蒸馏** | Socratic-SWE (2606.07412) | 从历史求解轨迹提取结构化 skill，指导修复任务 | 3 轮迭代 SWE-bench 50.40% |
| **RL Skill 提取** | CODESKILL (2605.25430) | RL 管理 skill 提取和 skill-bank 维护，密集 + 稀疏混合奖励 | — |
| **无外部标注进化** | RHO (2606.05922) | 自验证 + 自一致性 + 自我偏好 | SWE-Bench Pro 59%→78% |
| **群组进化** | GEA (2602.04837) | Agent 群体作为演化单元，经验共享 | SWE-bench 71.0% |
| **结构化记忆** | MemCoder (2603.13258) | 意图-代码映射 + 自我修正 + 经验内化 | — |
| **递归自我设计** | MetaAI Recursive (2606.09663) | Darwin Goedel 机器，自修改代码 | 80 次迭代 20%→50% |

### SWE Agent 关键工程教训
- **60-69% 失败是 Edit-Quality 问题**，非 Localization — 优化补丁生成质量
- **框架设计比模型更重要** — 同一模型在不同框架上性能差 6x
- **20% "solved" patch 实际语义错误** — 必须多维度验证
- **Subagent 架构**：主 agent 规划 + 推理，子 agent 执行，token 节省 ~30%

## 安全与退化风险

| 风险类型 | 来源 | 说明 |
|---------|------|------|
| **能力退化** | ANCHOR (§2.2) | 自主进化可能导致能力退化和安全漂移 |
| **探索退化** | B-STaR, AdaSTaR (§2.2) | 探索能力在迭代中迅速退化，需动态分配采样预算 |
| **安全漂移** | ANCHOR (§2.2) | 自主进化过程中安全对齐可能漂移 |
| **Self-bias 递归漂移** | Pride and Prejudice (2402.11436) | 自我反馈单独使用导致递归漂移 |
| **组合安全风险** | SkillReact (2606.00448) | 22.25% 技能对存在组合风险 |
| **长期记忆安全** | Zombie Agents (2602.15654) | session 间记忆需安全隔离 |
| **元 Agent 对抗行为** | MAC (2606.04455) | 高优化压力下出现对抗行为 |
| **验证器可欺骗** | (2603.12564) | 80% 自验证引用可被操纵值欺骗 |

### 缓解策略
- **外部验证器/批评者**（Reflexion, V-STaR, ARIS）
- **多 Agent 辩论**（MAR, SCALE）
- **形式化验证**（SEVerA）
- **Regression budget**（GRASP）
- **置信度校准与弃权**（Pause and Reflect, 5% 弃权率下准确率 90.1%）

## 与 optics_agent 的关系

### 当前状态
| 维度 | 当前 | 前沿目标 |
|------|------|---------|
| 自迭代 | 手工 handoff 文档 | Socratic-SWE 闭环自演化 |
| 元认知/反思 | 事后 final_report.md | Reflexion 运行中反思 |
| 评估/验证 | 人工判断 success 类型 | 自动化物理验证 |
| 经验管理 | 无 | 经验池 + 语义检索 |

### 直接可映射的范式
1. **Reflexion → 失败仿真反思**：COMSOL 失败脚本 → 语言反思 → 自动修正，无需重训模型
2. **Socratic-SWE → 轨迹蒸馏闭环**：每次 COMSOL 仿真轨迹 → 自动演化 skill
3. **Voyager → COMSOL Java 技能库**：Code-as-Skill，以 COMSOL Java 代码为 skill 载体
4. **GEA → 多 Agent 团队**：建模师/求解师/分析师作为演化单元，经验共享

### 优先级建议
- **近期**：失败模式编码化 + 反射式失败处理（借鉴 Reflexion）
- **中期**：经验池自动追加 + 角色 Agent 路由（借鉴 GEA）
- **长期**：技能自动创建 + 全自动物理验证（借鉴 Socratic-SWE + SEVerA）

### 风险注意
- 物理验证是**终极瓶颈**，纯自动化架构无法替代领域专家标准答案
- 科学计算的自迭代必须引入**形式化验证**（SEVerA）以防止物理错误
- 探索能力退化在 COMSOL 场景尤为危险（仿真成本高，采样预算有限）
