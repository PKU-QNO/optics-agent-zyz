# Fig.2 数值复现与 gate②/③ 验收记录

## 运行契约

- 横轴统一为 $s=2a/\lambda\in[0.2,1.0]$，200 点在 $s$ 上均匀采样；金球 $a=250\,\mathrm{nm}$，所以计算波长为 $\lambda=500/s\,\mathrm{nm}$。
- 表2辐射核使用 host 波数，内部场才使用 $k_{\mathrm{in}}=m k_{\mathrm{host}}$。
- 金材料在波长域对 $n(\lambda),\kappa(\lambda)$ 线性插值，越界直接报错；复介电函数为 $\varepsilon=m^2$。
- 主方法验收使用 Olmon-EV（500--2500 nm）；JC 仅在 500--1935 nm 作为论文形状对比；JC/Olmon/McPeak 在 500--1700 nm 分别计算后取包络，不将均值当作材料真值。
- 归一化量为 $C_{\mathrm{sca}}/(\lambda^2/2\pi)$。相对误差只在 Mie 值 $\ge10^{-4}$ 时统计，另报全点绝对误差。

## Olmon-EV 主验收

结果文件：

- `data/fig2_gold_olmon.csv`：基线网格 $(40,41,80)$；
- `data/fig2_gold_olmon_summary.json`：基线统计；
- `data/fig2_gold_olmon_refined.csv`：加密网格 $(60,61,120)$；
- `data/fig2_gold_olmon_refined_summary.json`：最终统计。

基线网格的 200 点结果中，ED/MD/EQ 均满足最大相对误差、p95 和最大绝对误差契约；MQ 的最大相对误差为约 0.115%，p95 为约 0.114%，略高于 p95=0.1% 的门槛，但最大绝对误差仍为 $3.15\times10^{-4}$。这不是物理公式漂移，而是体积分辨率效应。

加密网格用于最终 gate。200 点实际结果如下（百分数均相对 Mie）：

| 通道 | 最大相对误差 | p95 相对误差 | 最大绝对误差 | 近零 mask 点 | 裁决 |
|---|---:|---:|---:|---:|---|
| ED | 0.01186% | 0.01136% | $1.74\times10^{-4}$ | 0 | PASS |
| MD | 0.01699% | 0.01654% | $1.28\times10^{-4}$ | 0 | PASS |
| EQ | 0.01610% | 0.01606% | $2.63\times10^{-4}$ | 4 | PASS |
| MQ | 0.02414% | 0.02399% | $6.33\times10^{-5}$ | 16 | PASS |

因此四通道同时满足最大相对误差小于 1%、p95 小于 0.1%、全点最大绝对误差小于 $2\times10^{-3}$。

## 网格收敛抽样

对完整 200 点比较 $(40,41,80)\to(60,61,120)$，高信号区最大变化依次为 ED 0.0452%、MD 0.0642%、EQ 0.0608%、MQ 0.0907%，全部低于 0.1%。机器可读结果见 `data/fig2_gold_olmon_grid_convergence.json`。

## 三源材料敏感性

- JC 与 McPeak 各自完成 80 点 Table2/Mie 扫描；Olmon 使用上述 200 点加密扫描。
- 三源只在共同覆盖 500--1700 nm（$s\in[500/1700,1]$）内对齐，生成 `data/fig2_gold_material_envelope.csv` 和 `figs/fig2_gold_material_sensitivity.png`。
- 包络是三种独立样品数据的 min--max，不是均值材料；Mie 和 Table2 永远使用同一源、同一 $m(\lambda)$ 互比。
- JC/McPeak 的 80 点基线网格中 MQ 的 p95 略高于 0.1%，但这些运行用于材料敏感性而非全区间方法 gate；其余通道及绝对误差通过。方法 gate 由 Olmon 加密 200 点给出。

## 复数 Mie 交叉

在 550、1000、1700、1935、2500 nm，Olmon-EV 路径均满足 $\operatorname{Im}(m)>0$、$C_{\mathrm{abs}}\ge0$，并通过 miepython 的 $a_n,b_n,c_n,d_n$ 逐项交叉。JC 在 1935 nm 之外和 McPeak 在 1700 nm 之外均禁止外推。

## 裁决

formalization 的数据用途、采样、误差掩膜和复数电流定义已具备机器可执行契约；Olmon-EV 加密 200 点主 gate 与全区间网格收敛均通过。Fig.2 formalization 可提交 gate②，后续只剩论文像素曲线 RMSE 的 gate④ 人工阈值裁决，不再存在表2/Mie 方法 blocker。
