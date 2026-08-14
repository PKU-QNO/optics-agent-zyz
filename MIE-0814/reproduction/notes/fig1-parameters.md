# Alaee 2018 Fig.1 复现参数提取（step01 路线 B：文本参数提取）

> 生成：2026-08-04
> 输入：OCR 校对版 `optics_agent/papers/mie-f/01-主论文/Alaee_2018.ocr/Alaee_2018.md`（行号 = OCR 文件行号）
> 交叉核对：原始 PDF `Alaee_2018_An_Electromagnetic_Multipole_Expansion_Beyond_the_Long-Wavelength_Approximation.pdf`（文字 PDF，pdf-mcp 可读）＋ Fig.1 栅格 `figs/fig1.png`（2481×1488）
> 状态：**完成**。凡 OCR 缺失、已从 PDF/图补充处均显式标注来源。

---

## 1. Fig.1 参数总表

| # | 参数 | 值 | 来源 |
|---|------|-----|------|
| 1 | 介电球相对介电常数 ε_r | **6.25**（= 2.5²，n=2.5 高折射率） | OCR L37「The permittivity of the dielectric sphere is assumed to be $\epsilon_{\tau} = 2.5^2$.」；PDF 页2 同句（文字层）。**注**：OCR 写作 `2.5^2`，个别笔记误抄成 `2.52`，实际是 2.5 的平方 = 6.25。opus 审查 R1 已确认。 |
| 2 | 介电球尺寸参数 x = 2a/λ 范围 | **0.2 ～ 0.8** | Fig.1 面板 (a) x 轴刻度（权威 fig1.png 2481×1488 实测：**0.2, 0.4, 0.6, 0.8**，gate① 亲眼看权威图修正）。OCR **未给出**该数值（正文只定性说「increasing the a/λ ratio」），**需从图补充** → 已从权威图提取。⚠️ **早期低分辨率 OCR 渲染误读为 0→2.0（0,0.5,1.0,1.5,2.0），作废**。 |
| 3 | 金球半径 a | **250 nm** | OCR L63 Fig.1 caption「For a gold sphere with a fixed radius of $a=250$ nm.」；PDF 页3 caption 同。 |
| 4 | 金球 x = 2a/λ 对应范围 | **λ = 400 ～ 1000 nm**（由 a=250nm 固定，对应 x = 2a/λ = 0.5 ～ 1.25） | Fig.1 面板 (b) x 轴刻度（fig1.png 实测：400, 600, 800, 1000 nm，实为 400–1000，步长 100）。OCR **未给出**波长范围，**需从图补充** → 已从图提取。对应 x = 2×250/λ：λ=400→x=1.25，λ=1000→x=0.5。 |
| 5 | 入射 | **x 偏振平面波，沿 z 传播** | OCR L37「Both are illuminated with a linearly x-polarized plane wave that propagates in the z-direction.」；PDF 页2 同。 |
| 6 | host 介质 | **air，ε_host = 1** | OCR L37「We assume air as the host medium.」；PDF 页2 同。 |
| 7 | 金材料色散 | **Johnson & Christy 1972**（文献 [38]） | OCR L37「Dispersive material properties as documented in the literature are considered for gold [38].」 |
| 8 | 数值工具（原文采场） | **COMSOL Multiphysics 有限元**（文献 [39]） | OCR L37「We used a numerical finite element solver to obtain the electric field distributions [39].」；本复现改用 analytic_mie。 |
| 9 | 纵轴 | **归一化 C_sca（除以 λ²/2π），线性刻度，取值 1, 3, 5, 7** | OCR L63 caption「the contribution of each multipole moment to the scattering cross section is normalized to $\lambda^2/2\pi$.」；图实测面板 (a) y 轴为 **linear** 刻度，标签 **1, 3, 5, 7**（= (2j+1) 普适上限：j=0→1, j=1→3, j=2→5, j=3→7，见参数 #10，与 linear 轴完全自洽）。⚠️ 早期误判为 log（10⁻²~10²），系把竖排轴标题 "(C_sca/(λ²/2π))" 笔画误读为指数刻度，已由 vision-mcp 多通道核实作废。 |
| 10 | 每多极普适上限 | **(2j+1)λ²/2π**（j=1 偶极 → 3λ²/2π） | OCR L63 caption「For spherical particle, there is a universal limit for each multipole, i.e. $(2j+1)\lambda^2/2\pi$. For example, for a dipolar particle (i.e. $j=1$), the maximum cross section is $3\lambda^2/2\pi$ [24,40].」 |
| 11 | 面板 (a) | 介电球各多极贡献 vs 2a/λ | OCR L63 caption「(a) For a dielectric sphere as a function of the particle's size parameter $2a/\lambda$.」 |
| 12 | 面板 (b) | 金球各多极贡献 vs 波长（a=250nm 固定） | OCR L63 caption「(b) For a gold sphere with a fixed radius of $a=250$ nm.」 |
| 13 | 面板 (c) | 相对误差（介电球，vs 2a/λ，x 轴同 (a)：0.2–1.0） | OCR L63 caption「(c) and (d) Relative error between the multipole moments calculated with the Mie theory and calculated with the approximate expressions.」；图实测面板 (c) x 轴同 (a) 刻度。 |
| 14 | 面板 (d) | 相对误差（金球，vs λ，x 轴同 (b)：400–1000nm） | OCR L63 caption（同上）；图实测面板 (d) x 轴同 (b) 刻度。 |
| 15 | 面板 (c)/(d) 纵轴 | **相对误差（%），线性，刻度 0, 25, 50, 75, 100** | 图实测（fig1.png 面板 (c) y 轴刻度 **0,25,50,75,100**，linear）；OCR 未给数值刻度，caption 只写「Relative error」。 |
| 16 | 2a/λ≈0.75 处误差 | **>100%**，且**电、磁偶极都超** | OCR L47–49「The relative error is more than 100% for the dielectric sphere at $2a/\lambda \approx 0.75$ for both electric and magnetic dipole moments.」；PDF 页2 同。 |

### 图结构说明（panel 布局）
Fig.1 为 2×2 子图（fig1.png 实测 + caption 佐证）：
- **左列**：(a) 介电球（ε_r=6.25）各多极（ED/MD/EQ/MQ）贡献 vs 2a/λ（0.2–1.0），**linear 纵轴 1,3,5,7**；(b) 金球（a=250nm）各多极贡献 vs λ（400–1000 nm），linear 纵轴 1,3,5,7。
- **右列**：(c) 介电球相对误差 vs 2a/λ；(d) 金球相对误差 vs λ。纵轴 linear，0,25,50,75,100（%）。
- 布局实测：**左列 (a)(b) 为散射截面（纵轴 1,3,5,7），右列 (c)(d) 为相对误差（纵轴 %）**。⚠️ 早期 yaml 把 a/b 记为上排、c/d 为下排（745×302 低清图），权威图实际是**左/右分列**，vision-mcp 整图核实。
- 每面板内曲线为 Mie 理论（基准）与表 1 近似表达式两组对照。

---

## 2. Table 1（长波长近似多极矩）逐字公式

来源：**PDF 页3 文字层 + 表格抽取**（权威；OCR L69–74 有严重 OCR 错误，见 §4）。Table 1 标题行 OCR L65–67 原文：「Multipole moments in long-wavelength approximation; electric dipole moment (ED, i.e. p_α), magnetic dipole moment (MD, i.e. m_α), electric quadrupole moment (EQ, i.e. Q_e_αβ) and magnetic quadrupole moment (MQ, i.e. Q_m_αβ) where α, β = x, y, z.」

### 逐字公式（LaTeX）

**ED（T1-1）**：
$$p_\alpha \approx -\frac{1}{i\omega}\left\{\int d^3\mathbf{r}\, J_{\omega\alpha} + \frac{k^2}{10}\int d^3\mathbf{r}\left[(\mathbf{r}\cdot\mathbf{J}_\omega)r_\alpha - 2r^2 J_{\omega\alpha}\right]\right\}$$

**MD（T1-2）**：
$$m_\alpha \approx \frac{1}{2}\int d^3\mathbf{r}\,(\mathbf{r}\times\mathbf{J}_\omega)_\alpha$$

**EQ（T1-3）**：
$$Q^e_{\alpha\beta} \approx -\frac{1}{i\omega}\Biggl\{\int d^3\mathbf{r}\left[3(r_\beta J_{\omega\alpha} + r_\alpha J_{\omega\beta}) - 2(\mathbf{r}\cdot\mathbf{J}_\omega)\delta_{\alpha\beta}\right] + \frac{k^2}{14}\int d^3\mathbf{r}\left[4r_\alpha r_\beta(\mathbf{r}\cdot\mathbf{J}_\omega) - 5r^2(r_\alpha J_\beta + r_\beta J_\alpha) + 2r^2(\mathbf{r}\cdot\mathbf{J}_\omega)\delta_{\alpha\beta}\right]\Biggr\}$$

**MQ（T1-4）**：
$$Q^m_{\alpha\beta} \approx \int d^3\mathbf{r}\left\{r_\alpha(\mathbf{r}\times\mathbf{J}_\omega)_\beta + r_\beta(\mathbf{r}\times\mathbf{J}_\omega)_\alpha\right\}$$

### 系数速查
| 多极 | 前置系数 | k² 项系数 | 备注 |
|------|---------|-----------|------|
| ED | −1/(iω) | k²/10 | k² 项 = toroidal 偶极修正 |
| MD | 1/2 | — | 无 k² 项 |
| EQ | −1/(iω) | k²/14 | k² 项 = toroidal 四极修正 |
| MQ | 1 | — | 无 k² 项 |

任务要求中提到的「k²/10、1/2、k²/14 等系数」均已确认：k²/10 在 ED，1/2 在 MD，k²/14 在 EQ。

---

## 3. Eq.(1) 散射截面公式（含量纲修正）

来源：OCR L41–45 + PDF 页2 文字层。原文（OCR L41–43）：

```
C_sca^total = C_sca^p + C_sca^m + C_sca^{Qe} + C_sca^{Qm} + ⋯
            = k⁴/(6πε₀²|E_inc|²) [ Σ_α (|p_α|² + |m_α|²/c)
              + (1/120) Σ_αβ (|kQ_e_αβ|² + |kQ_m_αβ/c|²) + ⋯ ]   (1)
```

### 逐字 LaTeX（原文照录，未改）
$$C_{\mathrm{sca}}^{\mathrm{total}} = \frac{k^4}{6\pi\epsilon_0^2|\mathbf{E}_{\mathrm{inc}}|^2}\left[\sum_\alpha\left(|p_\alpha|^2 + \frac{|m_\alpha|^2}{c}\right) + \frac{1}{120}\sum_{\alpha\beta}\left(|kQ^e_{\alpha\beta}|^2 + \left|\frac{kQ^m_{\alpha\beta}}{c}\right|^2\right) + \cdots\right]$$

### 量纲自洽版（复现实现用）
$$C_{\mathrm{sca}}^{\mathrm{total}} = \frac{k^4}{6\pi\epsilon_0^2|\mathbf{E}_{\mathrm{inc}}|^2}\left[\sum_\alpha\left(|p_\alpha|^2 + \frac{|m_\alpha|^2}{c^2}\right) + \frac{1}{120}\sum_{\alpha\beta}\left(|kQ^e_{\alpha\beta}|^2 + \left|\frac{kQ^m_{\alpha\beta}}{c}\right|^2\right) + \cdots\right]$$

**差异说明（task 要求核对项）**：
- 原文印刷磁偶极项为 `|m_α|²/c`，**量纲不成立**（p 与 m/c 同量纲 → 应为 `|m|²/c²`）。这是论文 typo，复现实现必须用 `|m|²/c²`。见 §6 与讲义对照。
- 四极系数 `1/120` 已确认（OCR 与 PDF 均清晰显示 1/120）。

---

## 4. J_ω 电流密度公式与符号约定

### 公式（逐字）
OCR L37 / PDF 页2：
$$J_{\omega}(\mathbf{r}) = i\omega\epsilon_0(\epsilon_r - 1)\mathbf{E}_{\omega}(\mathbf{r})$$

### 符号约定分析（task 要求核对项）

| 文献 | 公式 | 时间约定 | 来源 |
|------|------|---------|------|
| **Alaee 2018**（本文） | J_ω = **+iω**ε₀(ε_r−1)E | 隐含 **e^{+iωt}**（或与其自洽的约定） | OCR L37 / PDF 页2 |
| **Grahn 2012** Eq.(6) | J_S = **−iω**ε₀(ε_r−ε_rd)E | 隐含 **e^{−iωt}** | 讲义 §05 `05_scattering_current.tex` L12（Grahn Eq.6）；阅读笔记 `mie-f-reading-synthesis.md` L36、L207 |
| **讲义 §10**（本工作） | 沿用 Grahn：J ∝ −iω…，且 Mie 入射场取 E_i = E₀ e^{ikz} x̂ | **e^{−iωt}** | 讲义 §02 `02_mie_strict.tex` L84；§10 `10_lwa_derivation.tex` L51（ρ = ∇·J/(iω)） |

**结论**：
- 两个公式的**物理电流相同**，仅差时谐约定。在 e^{−iωt} 约定下 ∇×H = −iωε₀ε_r E；在 e^{+iωt} 约定下 ∇×H = +iωε₀ε_r E。把 Alaee 的 iω 换成 −iω 即得 Grahn 形式，反之亦然。二者不是矛盾，而是互为复共轭约定。
- **复现建议**：若按讲义 e^{−iωt} 约定实现，则 J 应取 **J_S = −iωε₀(ε_r−1)E**，与 Grahn/讲义一致；若严格照抄 Alaee 的 iω，则 e^{+iωt} 约定下一切多极矩公式（含 −1/(iω) 前置系数）自动一致。**关键是 J 公式与表 1 的前置系数 −1/(iω) 必须同约定**，否则整体差一个符号。
- 讲义 §10 推导用 ρ = ∇·J/(iω)（`10_lwa_derivation.tex` L51），与 Alaee 表 1 的 −1/(iω) 前置系数**在同一 e^{−iωt} 约定下自洽**。

---

## 5. 与讲义 §10（表 1 推导）逐条对照

讲义文件：`vector-multipole-derivation/sections/10_lwa_derivation.tex`

| 项 | Alaee 表 1（PDF 页3 权威） | 讲义 §10（L16–25 汇总表） | 一致性 |
|----|--------------------------|--------------------------|--------|
| ED | −(1/iω){∫J_α + (k²/10)∫[(r·J)r_α − 2r²J_α]} | p_α ≈ −(1/iω){∫J_α + (k²/10)∫[(r·J)r_α − 2r²J_α]} | ✅ 完全一致（含 k²/10） |
| MD | (1/2)∫(r×J)_α | m_α ≈ (1/2)∫(r×J)_α | ✅ 完全一致 |
| EQ | −(1/iω){∫[3(r_βJ_α+r_αJ_β)−2(r·J)δ_αβ] + (k²/14)∫[4r_αr_β(r·J)−5r²(r_αJ_β+r_βJ_α)+2r²(r·J)δ_αβ]} | Q^e_αβ ≈ −(1/iω){∫[3(r_βJ_α+r_αJ_β)−2(r·J)δ_αβ] + (k²/14)∫[4r_αr_β(r·J)−5r²(r_αJ_β+r_βJ_α)+2r²(r·J)δ_αβ]} | ✅ 完全一致（含 k²/14） |
| MQ | ∫{r_α(r×J)_β + r_β(r×J)_α} | Q^m_αβ ≈ ∫{r_α(r×J)_β + r_β(r×J)_α} | ✅ 完全一致 |
| 前置系数 | ED/EQ 为 −1/(iω) | 讲义同 −1/(iω) | ✅ |
| toroidal 解释 | ED k² 项 = toroidal 偶极；EQ k² 项 = toroidal 四极 | 讲义 L72–102 将 k²/10 项解释为 toroidal dipole（T_α 定义，L80）；L144–150 EQ k² 项为 toroidal quadrupole | ✅ 物理解释一致 |
| 适用边界 | 长波长近似，D ≪ λ；2a/λ≈0.75 时偶极误差>100% | 讲义 L44「ka≳0.5 时近似失效（Alaee Fig.1：偶极误差可超 100%）」 | ✅ 一致（0.5 与 0.75 是不同阈值口径：0.5 是失效开始，0.75 是误差超 100% 的点，不矛盾） |

**发现的不一致/需注意点**：
1. **OCR 表 1 严重 OCR 错误**（OCR L69–74）：ED 前置系数被 OCR 读成 `-1/10`（应为 −1/(iω)，iω 被误识别为 10），EQ 同理。PDF 文字层（权威）与讲义均确认是 **−1/(iω)**。复现实现**必须用 −1/(iω)**，不能用 OCR 的 1/10。此点已在 yaml 备注中显式警告。
2. **Eq.(1) 磁偶极项量纲 typo**：原文 `|m|²/c` → 应为 `|m|²/c²`（见 §3）。讲义 §10 汇总表未重抄 Eq.(1)，故讲义无此错误；复现实现直接用量纲自洽版。
3. 讲义表 2 与 Alaee 表 2 的对照（ED 系数 3/2 等）不在本任务范围（Fig.1 只需表 1 近似 + Mie 基准），未展开。

---

## 6. 复现实现要点（供 step02 代码）

1. **两条曲线集**：Mie 理论（基准，analytic Mie 各阶贡献）＋ 表 1 近似（用数值场积分或直接展开）→ 逐多极（ED/MD/EQ/MQ）对比。
2. **介电球**：ε_r=6.25 常数（无色散），x = 2a/λ ∈ **[0.2, 0.8]**（权威图实测）；**金球**：JC 色散，a=250nm，λ ∈ [400, 1000] nm。
3. **归一化**：每条曲线除 λ²/2π；叠加普适上限 (2j+1)λ²/2π 参考线。
4. **误差图**：相对误差 = |C_approx − C_Mie|/C_Mie × 100%，面板 (c)/(d) 纵轴 0–100+%。
   - **分母依据（gate② 🟡2）**：论文 caption 只写 "Relative error between multipole moments calculated with Mie theory and approximate expressions"，未明示分母。选择 **C_Mie 作分母**：因论文声称 2a/λ≈0.75 处误差 >100%，只有分母是 C_Mie（且 C_approx 远超 C_Mie）才能突破 100%；若分母为 C_approx 则误差封顶 <100%，与论文声称矛盾。实现按 C_Mie 分母，step03 notes 若见论文/图另有约定则以论文为准。
5. **符号约定**：统一 e^{−iωt}（与讲义/Grahn 一致）→ J = −iωε₀(ε_r−1)E，表 1 前置系数 −1/(iω)。
6. **验证点**：x≈0.75 处 ED、MD 相对误差均 >100%。
