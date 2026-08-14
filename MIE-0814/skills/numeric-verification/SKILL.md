---
name: numeric-verification
description: 数值散射/多极矩计算的物理验证框架——回答「为什么相信自己算对了」。三条相互独立的物理判据（多近似方法对比 / 极限退化 / 能量守恒与光学定理）+ Richardson 外推估网格收敛 + result_class 诚实标注。Use when 要验证一个数值复现结果是否物理正确（不只是「画图看起来像」），要设计验证矩阵、要判断网格收敛、要披露残差而不假装收敛、要判定 result_class 该标什么。
---

# Numeric Verification — 物理验证三元组

> 从 zotero mie-f 复现沉淀。核心问题不是「公式算对了吗」，而是「凭什么相信算对了」——用三条**相互独立**的判据排除三类错误（实现 bug / 公式抄错 / 物理不自洽）。

## 1. 三条判据（任何一条不过都不放过）

### ① 多近似方法对比（排除实现 bug）

同一物理对象用两条**独立数学路径**算，交叉比对：

- 球体：Table 2 精确多极矩体积积分 vs Mie 级数求和（两条独立路径，四通道 <0.03%）。
- 非球形无解析解：两种数值求解器互验（如 FEM 900G vs BEM 128G 双金盘）。
- 公式转录后配**独立库交叉**（如 miepython / scipy.special），不自己实现特殊函数。

> 判据：双实现相对差 < 阈值（偶极/磁四极 <1%，四极可放宽到 ~2% 取决于网格）。两条路一致才排除「抄错公式/实现 bug」。

### ② 极限退化（排除公式抄错）

每个公式要求它在已知极限退化回已知结果：

- 精确 Table 2 在 `kr→0` 退化回长波 Table 1（`j_l/(kr)^l → 1/(2l+1)!!`），逐条 <1%。
- Mie 消光退化回 Rayleigh `x⁴`；大尺寸极限 `Q_ext→2`（消光悖论）。
- 多极矩系数（ED 的 3、MQ 的 15）由退化固定，**不是照抄论文**——任何系数错都会在退化里暴露。

### ③ 能量守恒 / 光学定理（排除物理不自洽）

- 消光 = 散射 + 吸收：`C_ext = C_sca + C_abs`，守恒到 1e-10 量级。
- 光学定理 `C_ext = (4π/k²)Re[S(0)]`：前向散射振幅 S(0) 双路（级数求和 vs 前向极限）差 1e-14。
- 功率闭合：远场积分功率 balance = 1.0（<1% 即可）。
- 若论文有消光/散射两式，交叉比对（Grahn Eq22↔Eq20 相对差 5.96e-7）。

## 2. Richardson 外推（网格收敛 + 表面场奇异性）

h-refinement（网格尺寸 h 缩小）时误差 `∝ C·h^p`。取两档网格外推收敛值：

- **收敛阶 p**：从步进误差反推。磁共振峰表面场奇异 → p≈1.3（一阶收敛，h 减半误差只减 40%），细网格收益递减。
- **外推收敛值**：`f(h→0) ≈ f(h) + (f(h)-f(h/2))/(2^p-1)`，给出「继续加密会收敛到哪」。
- **诚实披露**：若 p 低、继续加密需超资源上限（如 0.2 网格需 2TB），就外推估收敛值 + 如实披露剩余残差（如 MD 2.37%），**不要假装收敛**。改用 p-refinement（高阶基函数）对表面场收敛更快。

## 3. result_class 诚实标注（7 级枚举）

`not_run` / `pipeline_completed` / `simulation_completed` / `diagnostic_only` / `surrogate_fallback` / `partial_physical_match` / `physical_reproduction_success`。

铁律：
- 「跑通了管道」（pipeline_completed）≠ 物理结论复现成功。
- 「诊断性结果」（diagnostic_only）≠ 验收。
- 「替代方案」（surrogate_fallback，如读图数据）≠ 物理复现。
- 缺网格收敛 / 远场闭合 / 人工 gate → 最多 partial_physical_match，不晋升。

## 4. 验证报告必备

| 项 | 说明 |
|----|------|
| 相对误差 | 各通道逐一列 |
| 绝对误差 | 防相对误差在近零区爆炸的误导 |
| 分母大小 | 近零区相对误差无意义，标注分母 |
| 密集扫描 | 峰位/形态，不是单点 |
| 网格收敛 | 至少两档 + Richardson 外推 |

## 5. references

- `references/verification-numbers.md` — mie-f 实际验证数字（三项 × 四轮），作「达标线」参照
- `references/analytic-benchmark-migration.md` — 解析基准校验（validate-then-trust）+ 长波近似适用边界，Fig.3 类非解析结构的验证迁移
