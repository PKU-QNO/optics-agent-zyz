# mie-phase1-reproduction — Mie 第一阶段复现（Akimov 2401.04146）

## 基础状态
- state: dormant
- priority: P1
- last_followed: 2026-07-15（WORK_LOG 最后更新）
- last_active_before_dormant: 2026-07-05（阶段十四闭环）
- blockers: 暂无
- waiting_on: 用户启动 Fig5(c)(f)/Fig6 复现或下一轮复现
- session_refs: [阶段十三、十四、十五]

## meta_trace 字段
- quest_ref: quest-1
- goal_urgent: Akimov Fig3 Gate1-4 已全部裁决完成（partial_physical_match 锁定），闭环交付
- goal_general: Mie 复现为 blueprint 迭代做回归测试
- plan_agent: 已就绪可启动 Fig5(c)(f)/Fig6 复现，需用户发话后到 SEPR 工作区执行
- behavior_rules: result_class 全程锁 partial_physical_match（CLAUDE.md 红线封顶），不声明 physical_reproduction_success

## 重大决策
- decision-1: Gate3 大尺寸 verifier 从点阈值改为趋势判据 — Q_ext 单调趋 2 + 末点 x=800 |Q-2|<0.05；原点阈值误判合法收敛为 FAIL
  - see memento:4bb12bfb
  - 见 WORK_LOG.md#阶段十三
- decision-2: Gate4 完全独立重求 sr locus 根 — optics-lead 用 Gate3 验过的 scattering.py 重算，与 SEPR CSV 逐点 delta=0.0000
  - 见 WORK_LOG.md#阶段十三

## 待决策
- pending-1: 轮次 2 启动 （Fig5(c)(f)/Fig6 复现） | 状态: 待用户
- pending-2: 数字化偏差方向性检验未做透（Gate4 已知遗留，不阻塞） | 状态: 待下轮

## session-history
- session-history-1: 见 WORK_LOG.md#阶段十三
- session-history-2: 见 WORK_LOG.md#阶段十四
