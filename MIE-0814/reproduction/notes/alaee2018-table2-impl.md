# Alaee 2018 Fig.1 — 表2 精确多极矩积分实现推导（step03）

> 生成：2026-08-05
> 用途：Alaee Table 2（精确多极矩，球 Bessel 核）→ 球坐标三重积分实现方案，供 step04 `multipole_moments.py`。
> 权威：讲义 §11（`11_exact_multipoles.tex` 完整推导）+ Alaee 表2（PDF 文字层）。
> 关联：`notes/alaee2018-mie-coeff.md`（Mie 系数）、`formalization/alaee2018-fig1.yaml`（spec）。

---

## 1. 表2 四式（讲义 §11，逐字）

**J = −iωε₀(ε_r−1)E**（内部场 → 电流，spec 约定 e^{−iωt}）。

| 多极 | 公式 | 球 Bessel 核 |
|------|------|-------------|
| ED | $p_\alpha = -\frac{1}{i\omega}\Bigl\{\int J_\alpha j_0(kr) + \frac{k^2}{2}\int\bigl[3(\mathbf{r}\cdot\mathbf{J})r_\alpha - r^2J_\alpha\bigr]\frac{j_2(kr)}{(kr)^2}\Bigr\}$ | $j_0$, $j_2/(kr)^2$ |
| MD | $m_\alpha = \frac{3}{2}\int(\mathbf{r}\times\mathbf{J})_\alpha\frac{j_1(kr)}{kr}$ | $j_1/(kr)$ |
| EQ | $Q^e_{\alpha\beta} = -\frac{3}{i\omega}\Bigl\{\int\bigl[3(r_\beta J_\alpha+r_\alpha J_\beta)-2(\mathbf{r}\cdot\mathbf{J})\delta_{\alpha\beta}\bigr]\frac{j_1(kr)}{kr} + 2k^2\int\bigl[5r_\alpha r_\beta(\mathbf{r}\cdot\mathbf{J})-(r_\alpha J_\beta+r_\beta J_\alpha)r^2-r^2(\mathbf{r}\cdot\mathbf{J})\delta_{\alpha\beta}\bigr]\frac{j_3(kr)}{(kr)^3}\Bigr\}$ | $j_1/(kr)$, $j_3/(kr)^3$ |
| MQ | $Q^m_{\alpha\beta} = 15\int\bigl\{r_\alpha(\mathbf{r}\times\mathbf{J})_\beta + r_\beta(\mathbf{r}\times\mathbf{J})_\alpha\bigr\}\frac{j_2(kr)}{(kr)^2}$ | $j_2/(kr)^2$ |

---

## 2. 内部场 E(r)（计算 J 的前提）

球内电场（B&H 4.53-4.54 内部场系数 + 矢量球谐展开，讲义 §2 L123-126）：
$$
\mathbf{E}_{\text{in}}(\mathbf{r}) = E_0\sum_{n=1}^{\infty} i^n\frac{2n+1}{n(n+1)}\Bigl[c_n\mathbf{M}^{(1)}_{o1n}(k_{\text{in}}\mathbf{r}) - i d_n\mathbf{N}^{(1)}_{e1n}(k_{\text{in}}\mathbf{r})\Bigr]
$$
其中 $k_{\text{in}} = k_0\sqrt{\epsilon_r}$，$\mathbf{M}^{(1)}/\mathbf{N}^{(1)}$ 用正则 $j_n$。**c_n/d_n 见 mie-coeff 笔记 §4（gate③ 必核）**。

> 内部场展开用 $\mathbf{N}^{(1)}_{e1n}$、$\mathbf{M}^{(1)}_{o1n}$（x 偏振 z 传播平面波激发，m=±1 分量，Y2）。实际实现可直接用 Mie 内部场解析式（B&H 4.53-4.54 对应球内场），或用 $J=-i\omega\epsilon_0(\epsilon_r-1)E$ 从内部场算电流。

---

## 3. 球坐标体积分展开

电流 $\mathbf{J}(\mathbf{r})$ 在球内（r≤a）非零。多极矩 = 对球体积分。球坐标 $(r,\theta,\phi)$：

$$
\int_V f(\mathbf{r})\,d^3r = \int_0^a\int_0^\pi\int_0^{2\pi} f(r,\theta,\phi)\, r^2\sin\theta\, dr\,d\theta\,d\phi
$$

**对称性降维**：x 偏振平面波 + 球对称 → 被积函数对 φ 有确定性依赖（m=±1），φ 积分可解析。实现时两种方案：
- **方案 A（全数值）**：$(r,\theta,\phi)$ 三维网格三重积分（scipy.integrate.tplquad 或数值求和）。最通用，验证方便。
- **方案 B（φ 解析）**：先解析掉 φ（$e^{i\phi}$ 项积分 = 0 除 m=±1），剩下 $(r,\theta)$ 二维。更快更准。

> **推荐方案 B**：x 偏振入射下，$J_x$ 分量 $\propto \cos\phi$，$J_y\propto\sin\phi$，$J_z$ 与 φ 无关（或 $J_r,J_\theta,J_\phi$ 有已知 φ 结构）。利用 φ 正交性把积分降到 2D，网格更密、误差更小。

---

## 4. r→0 极限（防除零，G1）

$j_l(kr)/(kr)^l$ 在 r→0 处 $0/0$ 形式，用极限值替换：
$$
\frac{j_l(kr)}{(kr)^l} \xrightarrow{kr\to0} \frac{1}{(2l+1)!!}
$$
| l | 极限值 |
|---|--------|
| 0 | 1 |
| 1 | 1/3 |
| 2 | 1/15 |
| 3 | 1/105 |

**实现**：网格最小半径 $r_{\min}$ 处（或 r=0 点）用极限值；Taylor 修正 $1 - (kr)^2/[2(2l+3)]$ 可选（G1）。

---

## 5. 数值积分策略

| 项 | 方案 |
|----|------|
| 球 Bessel | `scipy.special.spherical_jn(l, kr)`，比值 $j_l/(kr)^l$ 直接算（scipy 对 $kr\to0$ 可能不稳，用极限值兜底） |
| 网格 | r: $N_r$ 点（Gauss-Legendre 或均匀+加密近表面）；θ: $N_\theta$；φ: 解析 |
| 收敛 | 网格加倍测试：相对变化 < tol（G2）；r 向随 x 增大加密（内部场 $j_n(mx\cdot r/a)$ 高 x 振荡） |
| 积分器 | `scipy.integrate.quad`（1D）/ `dblquad`（2D）或直接求和 |

**内部场振荡**：$j_n(k_{\text{in}} r)$ 在球内，$k_{\text{in}} = k_0\sqrt{\epsilon_r}$。ε_r=6.25 → $k_{\text{in}} = 2.5 k_0$，内部场振荡 2.5×。r 向需足够密（G2）。

---

## 6. 退化验证（Layer2：表2 → 表1）

$kr\to0$ 时表2 精确矩退化为表1 近似矩（讲义 §11 完整推导 + 退化验证）：

| 表2 核 | kr→0 极限 | 表1 对应 |
|--------|----------|---------|
| $j_0(kr)$ | 1 | ED 主项 |
| $\frac{j_1(kr)}{kr}$ | 1/3 | MD 系数 $\frac32\cdot\frac13=\frac12$ ✅ |
| $\frac{j_2(kr)}{(kr)^2}$ | 1/15 | EQ/MQ 匹配 |
| $\frac{j_3(kr)}{(kr)^3}$ | 1/105 | EQ toroidal 匹配 |

> Layer2 verifier：小 x（如 x=0.05）下表2 vs 表1 各多极矩差异 <1%。这是"表2 实现正确"的关键独立验证（不依赖论文图）。

---

## 7. 与表1 近似的对比实现

表1（常数核）用于误差分析（面板(c) 的近似曲线）：
- ED: $p_\alpha \approx -\frac{1}{i\omega}\{\int J_\alpha + \frac{k^2}{10}\int[(r·J)r_\alpha - 2r^2J_\alpha]\}$
- MD: $m_\alpha \approx \frac12\int(r×J)_\alpha$
- EQ: $Q^e_{\alpha\beta} \approx -\frac{1}{i\omega}\{\int[3(r_\beta J_\alpha+r_\alpha J_\beta)-2(r·J)\delta_{\alpha\beta}] + \frac{k^2}{14}\int[4r_\alpha r_\beta(r·J)-5r^2(r_\alpha J_\beta+r_\beta J_\alpha)+2r^2(r·J)\delta_{\alpha\beta}]\}$
- MQ: $Q^m_{\alpha\beta} \approx \int\{r_\alpha(r×J)_\beta + r_\beta(r×J)_\alpha\}$

（讲义 §10 表1，与 spec `table1_approx` 一致。表1 是表2 的 kr→0 极限，用同一体积分框架，仅核函数替换。）

---

## 8. C_sca（从多极矩，Alaee Eq.1 量纲自洽版）

$$
C_{\text{sca}} = \frac{k^4}{6\pi\epsilon_0^2|E_0|^2}\Bigl[\sum_\alpha\Bigl(|p_\alpha|^2+\frac{|m_\alpha|^2}{c^2}\Bigr) + \frac{1}{120}\sum_{\alpha\beta}\Bigl(|kQ^e_{\alpha\beta}|^2+\frac{|kQ^m_{\alpha\beta}|^2}{c^2}\Bigr)\Bigr]
$$

**归一化**：除 λ²/2π（spec normalization），叠加 (2j+1) 普适上限参考线（1,3,5,7）。

> ⚠️ 量纲：磁多极项 `|m|²/c²`（B&H 原文印 |m|²/c 是 typo，讲义 §12 勘误）；四极系数 1/120（|kQ|²=k²|Q|²）。

---

## 9. 实现文件规划（step04 落点）

| 文件 | 内容 |
|------|------|
| `code/baseline_mie.py` | 独立最小 Mie 基准（scipy 直算 a_n/b_n + C_sca，Layer1 锚点） |
| `code/mie_theory.py` | Mie 系数 + C_sca/C_ext/C_abs + 内部场（c_n/d_n） |
| `code/multipole_moments.py` | 表2 精确多极矩体积分（本笔记 §3-5） |
| `code/multipole_approx.py` | 表1 近似多极矩（本笔记 §7） |
| `tests/test_multipole.py` | 退化验证（表2→表1）、暗模式、对称性 |

---

## 10. 待 gate③ 核对清单（承接 mie-coeff 笔记）

1. c_n/d_n 对 B&H 原书核（内部场，Y9）
2. 内部场展开式（讲义 §2 L123-126）与 B&H 4.53-4.54 一致
3. 表2 公式与讲义 §11/PDF 文字层一致（本笔记已逐字）
4. φ 降维方案（方案 B）的 m=±1 结构正确
