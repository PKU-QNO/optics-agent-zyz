# Grahn gate④ closure receipt (2026-08-12)

Receipt ID: `GRAHN-G4-20260812-PASS_WITH_NOTES`

## 裁决

**用户接受 `PASS_WITH_NOTES (method consistency only)`**，2026-08-12 关闭 Grahn 第 3 轮 gate④。

## 接受的 3 个 notes

1. **Path B 通道 mask 口径**：四通道相对误差只在 Mie 通道贡献 C≥10⁻⁴ 时计算（被 mask 点数 ED/MD/EQ/MQ=13/31/44/63）；逐 m 用 spec 预注册加权目标 mask——预注册合理口径，非隐藏误差
2. **Path-A EQ 1.385%**：rank-4 截断诊断，非总截面 gate 失败
3. **ceiling = method_consistency**：Grahn 纯理论论文（无数值图/实验），无法论文结果对比；**但有 B21 external support**（arXiv:2508.16545，28 点曲线 vs 我们的 Mie/精确核一致）——ceiling 有外部数值支撑

## 支撑证据（数值全 PASS）

| 项 | 值 |
|---|---|
| Path A 总截面（43/150 点） | max 5.706e-7 |
| Path B 总截面（200 点） | max 2.935e-4 |
| 逐 m 复系数（1298/1470 行） | max 1.517e-3 |
| Rayleigh slope | 6.098（目标 6.0±0.1） |
| 光学定理 Eq.(22) vs (20) | rel 5.963e-7 |
| 解析 fixture | 6/6 PASS，max 1.185e-14 |
| miepython | rel 1.593e-15 |
| 独立远场投影 | max 7.744e-15 |
| B21 外部对比（2508.16545） | 28 点峰位 ≤2THz / Q <3% 一致 |

## 最终状态

- `overall_gate = PASS_WITH_NOTES`（机器层，用户已确认）
- `result_class = method_consistency`（+ external_numerical_support）
- **Grahn 第 3 轮正式完结**（gate④ 关闭）

## 完整性

- 材料：`codex-prompts/out/B18-grahn-gate4-material.md` + `B21-grahn-external-compare.md`
- 用户裁决：2026-08-12 对话（"接受"）
