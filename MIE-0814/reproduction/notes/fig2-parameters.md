# Alaee 2018 Fig.2 复现参数提取（step01）

> 生成：2026-08-07（第 2 轮）
> 输入：权威 PDF `Alaee_2018_An_Electromagnetic_Multipole_Expansion_Beyond_the_Long-Wavelength_Approximation.pdf`（页4，pdf-mcp 逐字）+ 4 子 agent 金数据源调研 + 主 agent 亲算交叉核对
> 状态：**完成**。金数据已按用户拍板用 ≥3 独立公认源核对（非读图提取）。

---

## 1. Fig.2 结构确认（PDF 页4 caption 逐字）

**Fig.2 仅 (a)(b) 两面板，无误差子图**（不同于 Fig.1 的 4 面板）：

| 面板 | 内容 | x 轴 | 材料 |
|------|------|------|------|
| (a) | 介电球各多极贡献 vs 尺寸参数 | 2a/λ | ε_r = 2.5² = 6.25（n=2.5） |
| (b) | 金球各多极贡献 vs 尺寸参数 | 2a/λ | a=250nm，论文材料源为 JC [38] |

caption 原文：「Fig. 2. Contribution of each multipole moment to the scattering cross section calculated with Mie theory and calculated with the exact expressions (Table 2). (a) For a dielectric sphere with a relative permittivity of ε_r= 2.5² as a function of the particle's size parameter 2a/λ. (b) For a gold sphere with a fixed radius of a=250 nm.」

**正文关键句**（页2，逐字）：「It can be seen that the results from our exact expressions are in excellent agreement with those from Mie theory, irrespective of the particle's size parameter. Indeed, they are **indistinguishable up to a numerical noise level**.」

→ **验收标准**：高信号区最大相对误差 <1%，p95 <0.1%；近零点不用相对误差，全点最大绝对误差 <2×10⁻³。

**⚠️ PDF 文字层把 ε_r 写成 "2.52"**（丢上标），finding-mie-1 已确认 = 2.5² = 6.25（第 1 轮 gate 已核，此处不再重复核）。

### Fig.2 与 Fig.1 的关系
- **同一物理**：都是"表2 精确多极矩 vs Mie 理论"的 per-multipole 贡献对比
- Fig.1 = 表1（近似）vs 表2 vs Mie 三曲线（含误差面板 c/d）
- Fig.2 = **仅表2 vs Mie**（精确性验证，表1 不参与）
- 同一归一化：C_sca/(λ²/2π)；同一普适上限：(2j+1)λ²/2π
- 介电球 (a) 物理上 = Fig.1(a) 的表2 vs Mie 部分 → **数据可直接复用**

## 2. 归一化与普适上限（复用 Fig.1 结论）

- 归一化：C_sca/(λ²/2π)（与 Fig.1 同）
- 普适上限：(2j+1)λ²/2π → ED/MD（偶极 j=1）→ 3、EQ/MQ（四极 j=2）→ 5
- 介电球峰位锚点（第 1 轮实测）：ED a_1 @2a/λ=0.50、MD b_1 @0.385、EQ a_2 @0.647、MQ b_2 @0.543

## 3. 金介电函数数据源（用户拍板：≥3 独立公认源，非读图提取）

### 3.1 数据源与获取
| 源 | 文献 | 覆盖 | 点数 | 获取 |
|----|------|------|------|------|
| **JC** | Johnson & Christy, PRB 6, 4370 (1972)（论文引用[38]） | 188-1937nm | 49 | refractiveindex.info YAML（CC0） |
| **Olmon-ev** | Olmon et al., PRB 86, 235147 (2012)（光谱椭偏） | 300nm-24.9µm | 448 | 同上 |
| **McPeak** | McPeak et al., ACS Photonics 2, 326 (2015)（等离激元金膜） | 300-1700nm | 141 | 同上 |
| Rakić-LD（参考） | Rakić et al., Appl. Opt. 37, 5271 (1998)（COMSOL 内置） | 248nm-6.2µm | 200 | 同上 |

原始 YAML 存 `data/_gold_sources/`，CC0 公共领域。

### 3.2 550nm 交叉核对（主 agent 亲算，与子 agent 调研一致）
| 源 | n | k | ε₁ | ε₂ |
|----|-----|-----|------|------|
| JC | 0.424 | 2.472 | -5.93 | +2.10 |
| Olmon-ev | 0.326 | 2.507 | -6.18 | +1.63 |
| McPeak | 0.324 | 2.597 | -6.64 | +1.68 |
| Rakić-LD（参考） | 0.498 | 2.370 | -5.37 | +2.36 |

- 若把“互差”严格定义为 **max pairwise range / |arithmetic mean|**，则按 CSV 未舍入数据计算：ε₁ 为 **11.35%**，ε₂ 为 **25.75%**（用上表两位小数重算则约为 11.36%/26.06%）。
- 这说明三篇文献在 ε₁ 上中度一致，但损耗 ε₂ 有明显样品/工艺依赖；不再表述为“三源完全一致”。
- ⚠️ 任务早期的 "ε≈-8.9+1.5i@550nm" 是错误值（与 JC 582nm 或他人数据混淆），已纠正

### 3.3 全谱段一致性（400-1000nm，ε 物理指标）
| 波段 | ε₁ 三源最大偏差 | ε₂ 三源最大偏差 |
|------|----------------|----------------|
| 400-600nm（带间边缘） | JC 26.9% / Olmon 15.0% / McPeak 14.2% | JC 29.3% / Olmon 10.1% / McPeak 19.8% |
| 600-800nm | JC 5.6% / Olmon 1.9% / McPeak 7.5% | 好 |
| 800-1000nm | JC 5.8% / Olmon 1.8% / McPeak 7.4% | 好 |

**结论**：
- **600-1000nm 的 ε₁ 趋势较接近**，但 ε₂ 仍需作材料敏感性而不是真值平均
- **400-600nm 短波区（带间跃迁边缘 ~500nm）三源偏差大**：JC 1972 蒸发膜在带间区损耗偏高是文献已知特性（Olmon 2012 论文明确讨论）；Olmon 与 McPeak 相互一致较好（ε₁ <15%）
- **解析等价与数值验收要分开**：同一 ε 下 Table2 与 Mie 理论上等价；但不同 ε 会改变共振、近零点与数值条件，仍会影响固定网格验收和论文曲线相似度。
- **计算策略**：JC 用于论文形状对比（500-1935nm）；Olmon-EV 用于 500-2500nm 全区间方法验收；JC/Olmon/McPeak 在 500-1700nm 分别计算 min-max 包络。

### 3.4 落盘
- `data/gold_epsilon.csv`：400-2500nm @5nm 共 421 点，列 = `lambda_nm, jc_n, jc_k, olmon_n, olmon_k, mcpeak_n, mcpeak_k, mean_n, mean_k`。`mean_*` 是 legacy 诊断列，不是主计算输入。
- 抽查 550nm 行：mean n=0.358, k=2.525（ε≈-6.25+1.81i）
- 断点证据：1700→1705nm 时 legacy mean 从三源均值切到 Olmon 单源，ε₁ 由 -143.22 跳到 -136.16，ε₂ 由 10.80 跳到 8.85。此时 JC 仍覆盖至约 1937nm，因此该切换无法作为物理连续的主输入。
- 原始文件版本见 `data/_gold_sources/manifest.yaml`（URL、DOI、获取日期、SHA256）。

## 4. Fig.2 轴类型（2026-08-07 vision-mcp 双通道确认，早期 log 判定作废）

**y 轴 = linear 1, 3, 5, 7（双面板）** —— 2 通道收敛：
- 通道 1（image_analysis 整图裁剪 `_fig2_panels.png`）：y 双面板 = linear 1,3,5,7；x (b) = 0.2,0.4,0.6,0.8,1.0；图例 8 项（4 色 × Mie 实线/exact 表2 标记）；y 标题 C_sca(λ²/2π)；x 标题 2a/λ
- 通道 2（extract_text y 轴带放大 `_fig2_ylabel_strip.png`）：双面板 y 刻度 7,5,3,1；y 标题 $C_{\rm sca}(\lambda^2/2\pi)$

**x 轴**：双面板均为 **2a/λ**（linear，刻度 0.2,0.4,0.6,0.8,1.0）
- ⚠️ **Fig.2(b) 金球 x 轴是 2a/λ 而非波长**（与 Fig.1(b) 的 λ 轴不同）
- 金球 a=250nm 固定 → 2a/λ∈[0.2,1.0] ↔ λ∈[500,2500]nm

**对实现的影响**：
- 金球面板 (b) 需扫 2a/λ∈[0.2,1.0]（λ=500-2500nm），gold_epsilon.csv 已扩展至 2500nm
- 归一化 C_sca/(λ²/2π)，值域 1-7 linear 轴即可显示，普适上限参考线 (2j+1) 直接可视

## 5. 实现要点（供 step02/04）

1. **介电球 (a)**：复用 `data/fig1a_multipole_{table2,mie}.csv`（200 点），物理与 Fig.1(a) 相同，无需重扫
2. **金球 (b)**：a=250nm，在 2a/λ∈[0.2,1.0] 上均匀取 200 点，再反算 λ=500/(2a/λ) nm；数据源按 JC/Olmon/三源敏感性三种用途分开。
3. **复折射率 Mie**：直接用 m=n+iκ（κ>0）；host=air 时 ε=m²，电流前因子是 m²-1，严禁误用 |m|²-1。
4. **x_Mie 换算**：host=air，x_Mie = π·(2a/λ)（gate③ 硬要求，金球同样适用）
5. **归一化**：C_sca/(λ²/2π) + 普适上限 (2j+1)λ²/2π 参考线

## 6. gate② 数据源裁决（2026-08-08 对抗审查）

- **论文保真层**：Johnson & Christy 1972，仅 500-1935nm；不外推，不将更长波段冒充为论文 JC 输入。
- **方法验收层**：Olmon-EV，500-2500nm 全覆盖。
- **材料敏感性层**：JC/Olmon/McPeak 在 500-1700nm 分别跑同一套 Table2/Mie，展示包络，不做均值材料。
- 插值固定为波长域对 n、κ 分别线性插值，严禁静默外推和 1700nm 切源。
