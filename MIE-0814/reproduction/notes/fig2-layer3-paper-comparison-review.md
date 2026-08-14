# Fig.2 Layer3 论文 vector 曲线对比审查与执行报告

## 审查结论

原拟方案“高 DPI 渲染后由 vision-mcp 描点”不适合作为数值主证据。源 PDF 第 4 页实测含 840 个 drawing object，Fig.2 四种颜色的 Mie polyline 与 exact 圆形 marker 均保留为 vector path。因此本轮改用 PyMuPDF 直接提取路径；vision/raster 只保留为 `DESCRIPTIVE_ONLY` fallback。

strict vector 总状态为 **`UNRESOLVED`**，gate④ 最终状态为
**`PASS_WITH_LIMITATIONS / partial_physical_match`**，但这不表示表2/Mie 方法复现失败：

- 金球 JC 有效区内四条 Mie 实线全部为 `PASS_VECTOR_CONSISTENT`；
- 介电球 ED/MD/EQ 实线通过，MQ 实线的 RMSE 和 p95 略高于预注册阈值；
- 金球 $2a/\lambda<500/1935\approx0.2584$ 因 JC 数据越界，状态固定为 `MATERIAL_DOMAIN_LIMITED`；未用 Olmon 静默补齐；
- 独立的 Table2/Mie 数值 gate 已通过，因此 Layer3 未决项首先归因于尖锐 MQ 的论文路径采样/绘图离散，而不是反向推翻方法复现。

## A. Vector 提取与轴标定

源文件 SHA256：`c79e243e9b0d05e2800223dea8552df03bbbf0318c134839e9e7ebcc8dda973e`。

- 页码：物理 PDF 第 4 页；
- 提取模式：`vector`；共输出 1578 行曲线点；
- Mie：彩色 `l` polyline；exact：同色 `c` 圆形 marker；
- x 轴用 0.2、0.4、0.6、0.8、1.0 五个 vector tick 拟合；
- y 轴用 1、3、5、7 四个 vector tick 拟合；
- panel (a) x/y 数据坐标最大拟合残差分别约 0.00044/0.00657；panel (b) 约 0.00045/0.00637；换算为 PDF point 后最大约 0.068/0.053，均低于 0.5 pt gate；
- 坐标框确实延伸到第一个 0.2 tick 左侧，主比较仍严格截为 $[0.2,1.0]$。

机器可读提取证据见 `data/fig2_paper_vector_metadata.json` 和 `data/fig2_paper_vector_curves.csv`。

## B. 逐多极主结果

以下是论文 Mie vector 实线与本地解析 Mie 的主 gate。阈值为 RMSE≤0.02、p95 绝对误差≤0.05、峰位差≤0.01。

### Panel (a)：介电球

| 通道 | RMSE | p95 绝对误差 | 峰位差 | 状态 |
|---|---:|---:|---:|---|
| ED | 0.01001 | 0.01932 | 0.00014 | PASS_VECTOR_CONSISTENT |
| MD | 0.01070 | 0.02051 | 0.00029 | PASS_VECTOR_CONSISTENT |
| EQ | 0.01282 | 0.02606 | 0.00009 | PASS_VECTOR_CONSISTENT |
| MQ | 0.02556 | 0.05695 | 0.00002 | UNRESOLVED |

MQ 的峰位几乎完全一致，但尖锐路径附近的幅值残差使 RMSE/p95 分别超过门槛约 0.0056/0.0070。当前共同域实际为 212 点，其中 14 点绝对误差大于 0.05。

旧归因中“最大点间距 0.23 导致尖峰被切掉”不成立：0.23026 的间距位于
$x=0.13945\to0.36971$ 的断段，不在峰区；第一峰与第二峰窗口的最大间距分别仅约
0.00225 和 0.00879。因此只能写成“差异集中在高曲率区，可能包含绘图、坐标标定或原始数值采样效应”，不能声称具体根因已被证明。

独立 graphical-floor 诊断显示，在相同的 23 个 MQ marker x 位置，论文 Mie 实线与论文 exact marker 的 RMSE/p95 已达 0.02430/0.06187，而本地 Mie 与论文 Mie 实线仅为 0.00933/0.02104。因此本地结果为 `CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR`，但此诊断不覆盖预注册 strict gate。

### Panel (b)：金球 JC 共同区间

| 通道 | RMSE | p95 绝对误差 | 峰位差 | 状态 |
|---|---:|---:|---:|---|
| ED | 0.00801 | 0.01438 | 0.00010 | PASS_VECTOR_CONSISTENT |
| MD | 0.00633 | 0.01168 | 0.00365 | PASS_VECTOR_CONSISTENT |
| EQ | 0.00836 | 0.01590 | 0.00050 | PASS_VECTOR_CONSISTENT |
| MQ | 0.00626 | 0.01127 | 0.00000 | PASS_VECTOR_CONSISTENT |

金球域内 vector 曲线与 JC 复现一致。但完整 panel 仍不能给 `PASS`，因为论文 $[0.2,0.2584)$ 对应波长大于 1935 nm，超出 JC 原始覆盖。

## C. exact marker 的限制

exact marker 的典型 x 间距约 0.0296，大于峰位 gate 0.01。它们可以验证曲线形状和点值，但不足以独立裁决峰位。所有通道的 `peak_verdict` 因此统一为 `DESCRIPTIVE_ONLY`；RMSE/p95 作为 `shape_metrics_status` 单独保留，不覆盖同色 Mie 实线的主 gate 裁决。

## D. 风险、fallback 与归因纪律

fallback 顺序已固定：PDF vector → 确定性 RGB 分割 → vision/人工复核。栅格结果只能输出 `DESCRIPTIVE_ONLY`，不能产生 vector PASS。

若后续继续调查 MQ，应按以下顺序：轴/路径身份 → polyline 子路径与坐标变换 → marker/实线内部差异 → 论文原始数值采样 → 最后才审查本地物理实现。当前没有证据支持把 MQ 的小幅 Layer3 残差升级为表2公式错误，也没有证据支持把它唯一归因于 polyline 稀疏。

## 最终裁决

1. Layer3 vector 提取流程可行且已形成可审计产物；vision 描点方案已废弃为 fallback。
2. Panel (b) 在 JC 有效区为 `PASS_VECTOR_CONSISTENT`，完整 panel 为 `MATERIAL_DOMAIN_LIMITED`。
3. Panel (a) 因 MQ 严格 RMSE/p95 略超阈值保持 `UNRESOLVED`；ED/MD/EQ 均通过。
4. 论文内部 graphical floor 与本地结果一致，但不追溯性覆盖 strict gate。
5. gate④ 以 `PASS_WITH_LIMITATIONS` 关闭；方法声称为 `PASS`，论文 fidelity 为 `UNRESOLVED`，最终 SEPR `result_class=partial_physical_match`，不得宣称完整 Fig.2 已达到 `physical_reproduction_success`。
