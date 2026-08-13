# MEMORY — optics_agent

> 恢复上下文用，短时态。正文全沉 `memory/` markdown，本头只记"何时读什么" + "索引" + "task 骨架"。
> 创建于 2026-07-26（L1.5-curate 首次实跑构建）。

## quest-N（本源追求，长期少变）

- quest-1: **设计论文复现自进化 agent（SEPR）** — 人工预训练循环：OA 设计框架 → SEPR 复现执行 → 经验反馈 → OA 改进 → 重跑
- quest-2: **自身 COMSOL/Magnus 运行时** — plasmonics 笔记孵化，科学计算 workflow 可迁移

## 活动任务（每 task 3 行：名 + 一句话目标 + 状态行）

- task-active-1: `sepr-execution-feedback-loop` — 维持 OA 作为 SEPR 上游身份，审核复现结果并反馈改进框架 design | state=active / priority=P0 / last_followed=2026-07-15
- task-dormant-1: `mie-phase1-reproduction` — 在 SEPR 执行 Akimov Fig3 首轮完整闭环（已跑完）| state=dormant / waiting_on=用户启动 Fig5/Fig6 或下一轮
- task-archived-1: `sepr-design-complete` — SEPR 框架设计阶段（4 agent 架构 + 10/6 步 workflow + 落地验证）已完成 | archived_at=2026-07-15 / location=memory/archived-tasks/sepr-design-complete-2026-07-15.md

## topic 索引（何时读什么干什么）

- 见任务正文 + meta_trace → Read `memory/tasks/<task-name>.md`
- 见已验证结论 → Read `memory/findings.md`（## 已验证重要 / ## 已验证一般）
- 见未验证猜测 → Read `memory/findings-unverified.md`（90 天清）
- 见踩坑教训 → Read `memory/lessons.md`（同步 see pitfalls_log:<id>）
- 见操作历史 → Read `memory/worklog/00-index.md` 入口，按需深读 01-..
- 跨会话语义召回 → memento `memory_search`/`decisions_log`/`pitfalls_log`

## 路由表（场景信号 → 读什么）

- 我在哪 / 当前做什么 → 看本头 task-active + 当前 cwd
- 恢复 SEPR 框架设计上下文 → Read `C:\Users\27370\Desktop\project\optics_agent\WORK_LOG.md`（749 行 §0-§11）
- 查规则 / 红线 → Read `CLAUDE.md`（16 节，hardlink 与 AGENTS.md 同步）
- 查 codex 委托方案 → Read `notes/codex_exec_delegation_plan-CN.md`
- 查 Mie 复现计划 → Read `reproduction_test/mie/mie_reproduction_plan-FINAL-CN.md`
- 查 v3-final 设计谱系 → Read `v3-final/README.md`
- 查 skill 路由 → Read `CLAUDE.md#Skill-System` 节
