# 分文档 02：CODEX 任务体系（A1-B19）

> [⬆ 返回主文档](PROJECT-SYNC-2026-08-11.md)

## 体系结构

```
A 批 (探索/审计) → B 批 (执行) → 审查批 (B12-B14) → 修复批 (B15) → 收尾批 (B16-B19)
```

## A 任务（6/6，主 agent 验收通过）

| 任务 | 内容 | 结果 |
|------|------|------|
| A1 | 前两轮审计 + A2 独立复核 | Fig.1 gate 需重裁；Fig.2 维持 |
| A2 | 第 3 轮实现 v4 | 105 passed；PASS_WITH_NOTES |
| A3 | magnus+COMSOL 探索 | GUI 模板是唯一硬前置 |
| A4 | Fig.3 规划草案 | fig3.yaml 草案 + plan |
| A5 | MQ 根因 + UQ 预注册 | 峰区 90.67% 贡献 |
| A6 | Fano 文献 | 587 行 + 23 BibTeX |

## B 任务（19/19，全部验收）

| 批次 | 任务 | 结果 |
|------|------|------|
| 执行批 | B1 重 gate / B2 光学定理 / B3 UQ / B4 勘误 / B5 round2 修复 / B6 round3 报告 / B7 Fig.3 Mie | 全过 |
| 收尾批 | B8 COMSOL 骨架 / B9s 文档（绕 B9）/ B10 总报告 | 全过 |
| 审查批 | B11 fig3 spec / B12 审查 / B13 Fig.1 口径审查 | B12 批2调5拒1 + Eq(1) 风险；B13 复矩口径 |
| 修复批 | B14 全栈审查 / B15 修复 | B14 5🔴+8🟡；B15 全修 |
| 收尾批 | B16 官方 MPH / B17 Java builder / B18 Grahn 材料 / B19 交叉验证 | 全过 |

## 调度方式

- 并发 2-3 个（phybench 修复后单并发更稳）
- 断线 resume：`codex exec resume <session-id> --dangerously-bypass-approvals-and-sandbox`
- 产物全落盘 codex-prompts/out/
- 验收纪律：主 agent 亲读产物 + 现场重算关键数字

## 踩坑

1. `codex exec --resume` ❌ → `codex exec resume <id>`
2. resume 不支持 -s → 用 --dangerously-bypass-approvals-and-sandbox
3. 串行恢复脚本卡死 → 必须并行发
4. 服务端过载 → 60-120s 退避重试，最多 3-4 次
5. 会话窗口识别：session 文件第一条 user 消息含 prompt 路径
