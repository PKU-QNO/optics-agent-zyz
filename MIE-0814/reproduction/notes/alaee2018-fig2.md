# Alaee 2018 Fig.2 推导与实现笔记（step03）

> 生成：2026-08-08（第 2 轮 step03）
> 物理：Fig.2 多极分解——表2 精确多极矩 vs Mie 理论（indistinguishable）
> 完整数值验收见 `notes/fig2-numerical-acceptance.md`（Codex 对抗审查产物，已主 agent 核实）
> 参数与金数据源见 `notes/fig2-parameters.md`（step01）

---

## 1. Fig.2 与 Fig.1 的关系（同物理、不同呈现）

| | Fig.1 | Fig.2 |
|---|-------|-------|
| 曲线 | 表1（近似）vs 表2 vs Mie 三组 | **仅表2 vs Mie**（表1 不参与） |
| 面板 | 2×2：左列截面/右列误差 | 1×2 纵向：(a) 介电球 (b) 金球 |
| 横轴 | (a) 2a/λ；(b) λ | 双面板均 **2a/λ** |
| 物理目标 | 近似在 0.75 处 >100% 误差 | 表2 精确 = Mie（<1%，理想 <0.1%） |
| 验收 | 三曲线自洽 <1% + 0.75 处 >100% | 表2 vs Mie indistinguishable |

- Fig.2(a) 介电球 = Fig.1(a) 的表2 vs Mie 部分 → **数据直接复用** `data/fig1a_multipole_{table2,mie}.csv`
- 正文原文（PDF 页2，逐字）："results from our exact expressions are in excellent agreement with those from Mie theory, irrespective of the particle's size parameter. Indeed, they are **indistinguishable up to a numerical noise level**."

## 2. 表2 精确多极矩（Alaee Table 2，讲义 §11 推导）

四式（球 Bessel 核，逐字转录自 PDF 页3，第 1 轮 gate③ 已核）：

$$p_\alpha = -\frac{1}{i\omega}\Bigl\{\int J_\alpha\,j_0(kr)\,d^3r + \frac{k^2}{2}\int\bigl[3(\mathbf{r}\cdot\mathbf{J})r_\alpha - r^2J_\alpha\bigr]\frac{j_2(kr)}{(kr)^2}\,d^3r\Bigr\} \quad \text{(T2-1)}$$

$$m_\alpha = \frac32\int(\mathbf{r}\times\mathbf{J})_\alpha\,\frac{j_1(kr)}{kr}\,d^3r \quad \text{(T2-2)}$$

$$Q^e_{\alpha\beta} = -\frac{3}{i\omega}\Bigl\{\int\bigl[3(r_\beta J_\alpha + r_\alpha J_\beta) - 2(\mathbf{r}\cdot\mathbf{J})\delta_{\alpha\beta}\bigr]\frac{j_1(kr)}{kr}\,d^3r + 2k^2\int\bigl[5r_\alpha r_\beta(\mathbf{r}\cdot\mathbf{J}) - (r_\alpha J_\beta + r_\beta J_\alpha)r^2 - r^2(\mathbf{r}\cdot\mathbf{J})\delta_{\alpha\beta}\bigr]\frac{j_3(kr)}{(kr)^3}\,d^3r\Bigr\} \quad \text{(T2-3)}$$

$$Q^m_{\alpha\beta} = 15\int\bigl\{r_\alpha(\mathbf{r}\times\mathbf{J})_\beta + r_\beta(\mathbf{r}\times\mathbf{J})_\alpha\bigr\}\frac{j_2(kr)}{(kr)^2}\,d^3r \quad \text{(T2-4)}$$

### Mie per-multipole 对应（归一化 C_sca/(λ²/2π)）
- ED = 3|a₁|²（a_n=电多极/TM，n=1）
- MD = 3|b₁|²（b_n=磁多极/TE，n=1）
- EQ = 5|a₂|²（电四极，n=2）
- MQ = 5|b₂|²（磁四极，n=2）
- 系数 (2n+1) 来自 C_sca per-multipole 项归一化：C_sca^l/(λ²/2π) = (2n+1)|a_n|²（n=1→3, n=2→5）

### Eq.1 解析常数（从多极矩到 C_sca，禁经验标定）
- ED=x⁶/12π²、MD=x⁸/12π²、EQ=x⁸/1440π²、MQ=x¹⁰/1440π²（1/1440=1/(120·12)）

## 3. 金球复 ε 实现要点（第 1 轮没有的新内容）

1. **ε = m²，严禁 |m|²**：host=air 时 ε_r=m²=(n+iκ)²；J 前因子 (ε_r−1)=m²−1。用 |m|²−1 会丢失金复介电函数（Codex 对抗审查硬化）
2. **波长域插值，禁止外推**：对 n(λ)、κ(λ) 分别线性插值（波长域）；越界直接报错（run_fig2.py `interpolate_gold_m`）
3. **数据源三层用途**（fig2.yaml usage_policy）：
   - JC 保真层：500-1935nm（论文材料 Ref[38]），用于论文图形状对比
   - Olmon-EV：500-2500nm（全覆盖），用于方法验收
   - 三源敏感性：500-1700nm min-max 包络（非均值真值）
4. **辐射核波数 = host k**：表2 球 Bessel 核用 k_host（kr=x_mie·U）；内部波数 k_in=m·k_host 只进入 E_in/J 空间结构（第 1 轮 blocker 教训延续）
5. **x_Mie 换算**：host=air → x_mie = π·(2a/λ)（gate③ 硬要求，金球同样适用）
6. **同一 m 下双方法互比**：Mie 与表2 在同一插值 m(λ) 下计算（消除材料差异的纯方法对比）
7. **近零 mask**：相对误差只在 Mie≥10⁻⁴ 统计；近零点看绝对误差（<2×10⁻³）

## 4. 验收标准（对齐论文 "indistinguishable"）

- 高信号区最大相对误差 <1%（论文 Y10 容忍带收紧）
- p95 相对误差 <0.1%（indistinguishable 的严格化）
- 全点最大绝对误差 <2×10⁻³
- 网格收敛 (40,41,80)→(60,61,120) 最大变化 <0.1%
- 复数路径 passivity：Im(m)>0、C_abs≥0（miepython 交叉）

## 5. 实现/验证文件索引（Codex 产物）

| 文件 | 内容 |
|------|------|
| `code/run_fig2.py` | 金球扫描：波长域插值禁外推 + 同一 m 双方法 + 误差 mask + gate 摘要 |
| `code/plot_fig2.py` | 双面板复现图（图标准 lessons 12） |
| `code/build_fig2_sensitivity.py` | 三源敏感性包络 |
| `code/report_fig2_ratios.py` | 九点比值表 |
| `tests/test_fig2_reproduction.py` | 插值域/passivity/200 点 gate/网格收敛回归 |
| `data/fig2_gold_olmon_refined_summary.json` | 最终验收（200 点加密网格） |
| `data/fig2_gold_olmon_grid_convergence.json` | 网格收敛 |
| `notes/fig2-numerical-acceptance.md` | 验收报告（Codex，已核实） |
| `notes/fig2-nine-point-ratios.md` | 九点比值（介电球 + 金球三源） |
