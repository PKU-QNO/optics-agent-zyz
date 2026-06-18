# optics_agent 项目映射

> 摘自 Agent Skill 系统与工作流自迭代调研 (2026-06-18)，Section 5

---

## 5.1 现有 Skill 系统状态

**8 个 Skill**: core, paper-reproduction, comsol-runtime, comsol-batch, comsol-java-api, magnus-platform, magnus-artifacts, docker-images

**正确事项**:
- 技能路由表
- NTFS 同步（`.claude/skills` → `.codex/skills`）
- 验证脚本
- 标准报告格式
- 失败状态码定义
- Java 参考库

**核心差距**:
- 无动态注册/发现
- 无自动组合/编排
- 无自迭代
- 无多 Agent 协作
- 无自动评估

---

## 5.2 差距分析

| 维度 | 当前 | 前沿 | 差距 |
|------|------|------|------|
| 注册/发现 | 静态 AGENTS.md 路由表 | Voyager 语义检索技能库 | 严重 |
| 组合/编排 | 手动顺序提示 | DSPy 管道、CrewAI 层级 | 严重 |
| 自迭代 | 手工 handoff 文档 | Socratic-SWE 闭环自演化 | 严重 |
| 多 Agent 协作 | 单 Agent | MetaGPT 角色分工 | 严重 |
| 评估/验证 | 人工判断 success 类型 | AgentBench 自动化评测 | 严重 |
| 元认知/反思 | 事后 final_report.md | Reflexion 运行中反思 | 中等 |
| 工作流自动化 | submit_comsol.py 单入口 | Prefect 有状态工作流引擎 | 中等 |

---

## 5.3 与前沿论文的具体映射

| 前沿工作 | 核心思想 | optics_agent 对应 | 差距 | 优先级 |
|----------|---------|-------------------|------|--------|
| **Voyager** | 自动技能发现/迭代 | 现有 8 个手工 skill | 无自动技能创建 | 中长期 |
| **Reflexion** | 自我反思+重试 | `final_report.md` 事后文档 | 无运行中反思 | 中期 |
| **Socratic-SWE** | 轨迹蒸馏→自演化 | 无对应 | 缺失闭环引擎 | 长期 |
| **DSPy** | 声明式管道+自动优化 | 无管道抽象 | 无声明式 DSL | 中期 |
| **MetaGPT** | 多角色分工 | 单 Agent | 无角色分离 | 中期 |
| **CrewAI** | 层级团队编排 | 无 | 无编排框架 | 中长期 |
| **SoK Skills** | 7 种设计模式 | SKILL.md 基本格式 | 无元数据/权限/自演化 | 近期 |
| **SWE-agent ACI** | Agent-Computer Interface | 无 | Magnus 接口未适配 Agent | 中期 |

---

## 5.4 改进路线图

### 近期（1-2 周）— 快速夯实基础

1. **Skill 元数据标准化** — 给每个 SKILL.md 加 `version`, `dependencies`, `last_updated`（~2 小时）
2. **自动校验脚本** — `validate_all_skills.py` 统一验证所有 skill + AGENTS.md 路由表一致性（~1 天）
3. **失败模式编码化** — 矩阵分解失败自动进入"请求 GUI 模板"状态（~4 小时）
4. **AGENTS.md 依赖图** — Mermaid 标注技能间依赖关系（~1 小时）

### 中期（1-2 月）— 管道化 + 角色化

1. **工作流 DSL** — YAML 定义复现管道（`.repro.yaml`），步骤映射到 skill（~1 周）
2. **执行引擎** — `repro_runner.py` 解析执行 YAML 管道（~1 周）
3. **验证节点** — 程序化检查 `Im(neff)` 非零、数值范围、`surrogate_fallback` 标记（~3 天）
4. **角色 Agent 模板** — paper-reader, model-builder, magnus-submitter, result-validator（~2 周）
5. **经验池** — `.codex/experience/` 自动追加失败模式+检索机制（~2 天）

### 长期（3-6 月）— 自适应 + 自进化

1. **技能自动创建** — 从失败分析自动生成新 skill 文件（~1 月）
2. **反思层** — Reflexion 风格任务自评 → 技能差异补丁（~3 周）
3. **多 Agent 对话图** — AutoGen/CrewAI 集成（~1 月）
4. **技能语义检索** — 嵌入索引自动路由（~2 月）
5. **全自动物理验证** — 预期曲线 vs 计算结果匹配评分（~3 月）
