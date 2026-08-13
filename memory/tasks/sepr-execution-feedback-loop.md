# sepr-execution-feedback-loop — SEPR 执行反馈与上游审核

## 基础状态
- state: active
- priority: P0
- last_followed: 2026-07-15
- blockers: 等待用户启动下一轮复现（Fig5/Fig6 或新论文）
- waiting_on: 用户指示
- session_refs: [阶段十三、十四、十五]

## meta_trace 字段
- quest_ref: quest-1
- goal_urgent: 维持 optics-lead 上游审核就绪状态，随时可审 SEPR 复现结果
- goal_general: 持续基于复现经验改进 SEPR 框架设计直到 E-flow 上线
- plan_agent: 保持只读恢复状态，等待用户指派——默认为汇报现状 + 列待办 + 问用户
- plan_user: 1) 启动下一轮复现（Fig5/Fig6）2) 推进 codex 委托二期/三期 3) 决定 E-flow 上线时间

## 重大决策
- decision-1: full Sonnet 收敛 — 7 agent 全切 claude-sonnet-5，effort 分档补（high/xhigh/max），安全阀 E05 反复才升 Fable
  - see memento:164d89a9
  - 见 WORK_LOG.md#阶段十三
- decision-2: codex 委托方案落地 — codex exec（架构委托）+ codex-cli MCP（一次性问答），SEPR 11 步分档 A/B/C，approval never（exec）
  - see memento:74c52808
  - 见 WORK_LOG.md#阶段十五
- decision-3: main-agent 偏离流程须先问 human gate — structural issue 不等 evolution batch，human_intervention 立即落地
  - see memento:4a094a7a
  - 见 WORK_LOG.md#阶段十四

## 待决策
- pending-1: codex 委托二期/三期启动时机 — 下一个真 case 试 01 pdf_preprocessing 用 codex exec | 状态: 待用户
- pending-2: E-flow 上线条件 — 攒够 case 后用户开专门 evolution session | 状态: 待攒 case + 用户决定

## session-history
- session-history-1: 见 WORK_LOG.md#阶段十三
- session-history-2: 见 WORK_LOG.md#阶段十四
- session-history-3: 见 WORK_LOG.md#阶段十五
