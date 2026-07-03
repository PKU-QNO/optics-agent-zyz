# SEPR Cleanup A 清理日志

> 日期：2026-07-02  
> 范围：按 `DESIGN-GAP-AUDIT-CN_latest.md` 的精确定位，清理 SEPR 纯文本/口径 bug。  
> 约束：不改架构、不改 workflow 拓扑、不处理 capsule 契约、路径统一、leaf 深度硬约束或治理增量；未 commit。

## 1. result_class 旧口径

已改文件：
- `self-evo-paper-repro/.claude/skills/main-agent/references/main_report_template.md:255`
- `self-evo-paper-repro/.human/skills/main-agent/references/main_report_template.md:255`
- `self-evo-paper-repro/todo.md:10`
- `self-evo-paper-repro/.claude/skills/sub-agent/references/report_template.md:63`
- `self-evo-paper-repro/.human/skills/sub-agent/references/report_template.md:63`
- `self-evo-paper-repro/.claude/skills/sub-E-agent/references/report_template.md:59`
- `self-evo-paper-repro/.human/skills/sub-E-agent/references/report_template.md:59`

改前 -> 改后：
- `sweep_manifest.yaml` 示例中的 `success | partial | fallback | blocked | failed | archived` 改为 7 级枚举：`not_run / pipeline_completed / simulation_completed / diagnostic_only / surrogate_fallback / partial_physical_match / physical_reproduction_success`。
- `todo.md` 日志模板中的旧口径改为 7 级 `result_class`；Eflow 无物理复现结果时写 `not_run` 或 `N/A`。
- sub/sub-E 报告模板里的 `status: completed | blocked | failed` 改名为 `execution_status`，并注明 `execution_status` 是任务执行状态，不是 `result_class`。

## 2. 四选一改六维

已改文件：
- `self-evo-paper-repro/.claude/skills/evolution-agent/SKILL.md:36`
- `self-evo-paper-repro/.human/skills/evolution-agent/SKILL.md:36`
- `self-evo-paper-repro/.claude/skills/evolution-agent/SKILL.md:103`
- `self-evo-paper-repro/.human/skills/evolution-agent/SKILL.md:103`

改前 -> 改后：
- “治理报告 + 四选一裁决”改为“治理报告 + 六维裁决（Save/Improve/Absorb/Fork/Archive/Drop）”。
- human gate 中“ 四选一裁决给用户看”改为“六维裁决（Save/Improve/Absorb/Fork/Archive/Drop）给用户看”。

## 3. step11 矛盾 spawn 块

已改文件：
- `self-evo-paper-repro/.claude/skills/main-agent/workflow/11-main_agent_report/SKILL.md:70`
- `self-evo-paper-repro/.human/skills/main-agent/workflow/11-main_agent_report/SKILL.md:70`

改前 -> 改后：
- 删除 `.claude` step11 中“本步由主 agent 自己执行，不 spawn sub-agent”之后残留的完整“你是 sub-agent...”spawn 指令块。
- 现状保留为：step11 明确由主 agent 自己执行，不 spawn sub-agent；`.human` 侧同处一致。

## 4. PyMieScatt 残留

已删除脚本：
- `self-evo-paper-repro/.claude/skills/optics-mie-reproduction/scripts/compare_pymiessatt.py`
- `self-evo-paper-repro/.human/skills/optics-mie-reproduction/scripts/compare_pymiessatt.py`
- `optics_agent/.codex/skills/optics-mie-reproduction/scripts/compare_pymiessatt.py`

已改文本：
- `self-evo-paper-repro/.claude/skills/main-agent/workflow/08-result_analysis/SKILL.md:14`
- `self-evo-paper-repro/.human/skills/main-agent/workflow/08-result_analysis/SKILL.md:14`
- `self-evo-paper-repro/.claude/skills/main-agent/workflow/09-reproducibility_selfcheck/SKILL.md:12`
- `self-evo-paper-repro/.human/skills/main-agent/workflow/09-reproducibility_selfcheck/SKILL.md:12`
- `self-evo-paper-repro/.claude/skills/sub-agent/workflow/09-reproducibility_selfcheck/SKILL.md:8`
- `self-evo-paper-repro/.human/skills/sub-agent/workflow/09-reproducibility_selfcheck/SKILL.md:8`
- `self-evo-paper-repro/.claude/skills/optics-mie-reproduction/agents/openai.yaml:2`
- `self-evo-paper-repro/.human/skills/optics-mie-reproduction/agents/openai.yaml:2`
- `optics_agent/.codex/skills/optics-mie-reproduction/agents/openai.yaml:2`

改前 -> 改后：
- “PyMieScatt 三方叠加/独立验证/cross-check”改为“独立实现 + 物理硬约束 + 教材公式 + 论文图量化”的交叉验证。
- `agents/openai.yaml` 的 short description 删除 PyMieScatt cross-check 字样，改为 physical verifiers and quantitative paper-figure checks。

## 5. 根状态过时

已改文件：
- `self-evo-paper-repro/CLAUDE.md:100`
- `self-evo-paper-repro/PROJECT_STATUS.md:7`
- `self-evo-paper-repro/PROJECT_STATUS.md:68`

改前 -> 改后：
- “`.claude/skills` 是英文待写/镜像 `.human`”改为事实状态：`.claude/skills` 是中文详细执行版，4 身份约 6465 行已完成；`.human/skills` 是中文审查稿；英文 prompt-engineered 版是可选后期优化，不是当前阻塞项。
- `PROJECT_STATUS.md` 的待办改成“可选后期优化英文版”，不再把英文执行版当作未完成阻塞任务。

## 6. .human/.claude 定位

已改文件：
- `self-evo-paper-repro/CLAUDE.md:102`
- `self-evo-paper-repro/CLAUDE.md:105`
- `self-evo-paper-repro/PROJECT_STATUS.md:11`
- `self-evo-paper-repro/PROJECT_STATUS.md:73`

改前 -> 改后：
- 删除“镜像/同为中文”的误导定位。
- 改为：`.human/skills` 是中文审查稿，`.claude/skills` 是中文详细执行版；二者不是逐字镜像，但关键协议字段必须双写同步，包括 `result_class`、路径约定、报告 schema、human gate、权限/安全红线。

## 7. OpenCode 顶层 skill permission

已改文件：
- `self-evo-paper-repro/opencode.json:15`
- `self-evo-paper-repro/CLAUDE.md:230`

改前 -> 改后：
- `opencode.json` 顶层 `permission.skill` 在 `*: deny` 下新增放行：`pdf`、`magnus`、`optics-agent-core`。
- `CLAUDE.md` 路由表后新增说明：OpenCode 顶层显式放行这些 skill，因为它们在路由表中是 step01/step06/项目基础路由的可加载 skill；实际写入和命令仍受 agent 级 `edit: ask` / `bash: ask` 约束。

## 记忆记录

本次清理结论已存入 memento：
- 记忆 ID：`1894f7f9-de30-43a2-a79b-e6f71ffec9b8`
