# v3-final/ — SEPR 设计 / 审计 / 演进谱系（canonical 汇总）

> 本文件夹把散落在 `papers/SEPR/`、`notes/`、`notes/Gemini/`、`project/to-do-future/DSL/` 的 **V1→V2→V3 设计、风险审计、演进文档**汇总在一处。
> 这里的副本是 **canonical（正式版）**；原位置的同名文件已改名带 `_moved` 后缀并冻结（只作面包屑，不再更新）。
> 例外：`WORK_LOG.md` 是 living 操作日志，仍在 optics_agent 根，未移动——本索引直接指向它。

## 文件名后缀约定（tag）

| 后缀 | 含义 | 用在哪 |
|------|------|--------|
| `_latest` | 正在更新的最新版本 | v3-final 内的活文档 |
| `_archive` | 废案/完结但**有价值**，保留参考 | v3-final 内的完结报告、V1/V2 废案 |
| `_deprecated` | 废案**无价值且易误导** | 当前无 |
| `_moved` | 别处有 canonical 版、此处不再更新 | 原位置被搬走的文件 |
| `_V1_finished` | 历史版本完结 | 预留（当前 V1 用 `_archive`） |

## 跨谱系综合（通用化）

| 文件 | 内容 |
|------|------|
| `AGENT-SELF-ITERATION-COMPENDIUM-CN_latest.md` | **《Agent 自迭代经验大全》**——把 V1→V4 三代设计 + 127/94/反驳文献风险审计 + 首跑实测经验综合为一份**领域无关**的通用 agent 自迭代参考（10 章 + 附录：演进谱系、风险全景、八条铁律、参考架构、状态版本控制、自迭代流程、记忆治理、验证评估、多 agent/运维/模型路由、模式图谱、术语表+文献索引）。淡化了光学/COMSOL 背景，可迁移到其它领域。489 条 arxiv 引用。素材提取+编写由子 agent/codex 完成，编排与结构由 CC 定。 |

## 演进谱系

### V3（当前，SEPR Claude 三层子 agent 方案）

**活文档 `_latest`**
| 文件 | 内容 |
|------|------|
| `V3-HARDENING-DESIGN-CN_latest.md` | V3 加固设计提案（sub-leaf / skills 预加载 / hooks / OpenCode 撤销），含官方核验 §7 与待决 §9 |
| `V3-CHANGELOG-SINCE-HUMAN-CN_latest.md` | 从最早 `.human` 到现在的人话变更总览 |
| `V4-ROADMAP-CN_latest.md` | 跑完 Mie 后 V3→V4 改进路线 |
| `DESIGN-GAP-AUDIT-CN_latest.md` | 2026-07-02 设计 gap 审计（A1/C1/D 等） |
| `BORROWABLE-EXPERIENCE-CN_latest.md` | 6 路文献可借鉴经验 + 8 条铁律 + §6.1「先跑通再加治理」 |
| `V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md` | V3 外部证据增量审查（v2 深度版，6 篇反驳论文全文 + PINN 局限，R1-R4 修正） |
| `V3-AUDIT-2026-07_latest.md` | V3 实现+计划对抗性静态审计（声称vs实际、A1/A2/D 仍开、C1 半修、无真跑数据） |

**完结报告 `_archive`**
| 文件 | 内容 |
|------|------|
| `REVIEW-REPORT_archive.md` | 94 篇 v3 文献风险审查报告 |
| `CATEGORY-READING-NOTES_archive.md` | 文献分类阅读笔记 |
| `CONTEXT-for-subagent_archive.md` | 文献审查子 agent 上下文 |
| `CLEANUP-A-LOG-CN_archive.md` | 2026-07-02 口径 bug 清理日志 |
| `Gemini-CLI_archive.md` | Claude Code CLI 能力综述（低置信度，部分待核） |
| `Gemini-agent-team_archive.md` | Agent Teams 能力核验（已核 v2.1.196） |
| `Gemini-pre-subagent_archive.md` | Subagent 预配置/嵌套能力核验（已核 v2.1.196） |

### V2（已废，固定拓扑 workflow runner）— `_archive` 有价值废案
| 文件 | 内容 |
|------|------|
| `workflow_v2_plan-CN_archive.md` | V2 简化版设计方案 |
| `workflow_v2_risks-CN_archive.md` | V2 风险清单 |
| `project_flow_plan-CN_archive.md` | 项目状态树版本控制（project-flow）设计 |

### V1（已废，自动 DSL）— `_archive` 有价值废案
| 文件 | 内容 |
|------|------|
| `V1-workflow_risk_review-CN_archive.md` | **127 篇 arxiv 自演化文献风险审查（R-1~R-49，价值高）** |

### living（未移动）
- `../WORK_LOG.md` — SEPR 工作日志（living，仍在 optics_agent 根，本处不复制）。
- SEPR 本体 `self-evo-paper-repro/WORK_LOG.md` — SEPR 侧独立工作日志。

## 未收入 v3-final 的（仍在原位，未打 `_moved`）
更早研究输入笔记留在 `notes/`：`ECC_analysis-CN.md`、`ECC_takeaways_human_language-CN.md`、`advisor_report-CN.md`、`agent_skill_self_iteration.md`、`HANDOFF_for_new_context-CN.md`、`memory_system_literature_review-CN.md`、`subagent_policy_comparison-CN.md`、`workflow_risks_logic_order.md`；V1 其余 `project/to-do-future/DSL/`（引擎设计等）。需要时再纳入。
