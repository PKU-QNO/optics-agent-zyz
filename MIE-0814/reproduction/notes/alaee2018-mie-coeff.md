# Alaee 2018 Fig.1 — Mie 系数推导笔记（step03，gate③ 停点）

> 生成：2026-08-05
> 用途：a_n/b_n/c_n/d_n 的 Mie 系数对照 Bohren & Huffman（B&H）Ch.4，作为 step04 实现的公式真值源。
> 权威：**B&H 原书**（本地 Zotero S9DSIDNN，扫描件 533 页）。gate③ 必须对 B&H 原书核，不只看本笔记转录。
> 交叉：讲义 `vector-multipole-derivation` §2（a_l/b_l 闭式）+ formalization spec（参数）。

---

## 0. 公式位置索引（B&H 原书）

| 公式 | 内容 | B&H 位置 |
|------|------|---------|
| (4.51) | 边界条件四线性方程 | 书页 100（PDF 页 109） |
| (4.52) | **内部场系数 c_n / d_n**（一般 μ） | 书页 100（PDF 页 109） |
| (4.53) | **散射系数 a_n / b_n**（一般 μ） | 书页 100（PDF 页 109） |
| (4.56) | **a_n**（μ 相等，Riccati-Bessel 形式） | 书页 101（PDF 页 110） |
| (4.57) | **b_n**（μ 相等，Riccati-Bessel 形式） | 书页 101（PDF 页 110） |
| 4.4 | Cross Sections（截面，4.61-4.62 后续） | 书页 101-103 |

> **PDF 页 ↔ 书页偏移**：PDF 页 109 = 书页 100，PDF 页 110 = 书页 101（差 9）。B&H 书页 100 公式 4.51-4.53，书页 101 公式 4.56-4.57（μ 相等简化），书页 103 附近是截面公式。

---

## 1. 时谐约定（B&H 原文确认）

B&H 页 101 原文（OCR 转写）：
> "we have followed as much as possible van de Hulst (1957) and Kerker (1969), with the exception of the **opposite sign convention for the time-harmonic factor exp(−iwt)**"

**B&H 用 e^{−iωt} 时谐约定**——与我们 spec/讲义/Grahn 一致，无需符号翻转。✅

---

## 2. 记号与定义

| 符号 | 定义 | 来源 |
|------|------|------|
| $x = ka$ | 尺寸参数（B&H：$x = \frac{2\pi N a}{\lambda}$，N=介质折射率） | B&H 页 100 |
| $m = n/n_d$ | 相对折射率 = $\sqrt{\epsilon_r/\epsilon_{r,d}}$ | B&H 页 100 |
| $\psi_n(\rho) = \rho j_n(\rho)$ | Riccati-Bessel（正则） | B&H 页 101 原文 |
| $\xi_n(\rho) = \rho h_n^{(1)}(\rho)$ | Riccati-Bessel（出射） | B&H 页 101 原文 |
| $'$ | 对宗量求导 | B&H 页 100 |

> ⚠️ 注意：Alaee/讲义用 **2a/λ** 作尺寸参数（spec size_param），B&H 用 **ka**。关系：2a/λ = ka/π。x_Mie = (2π/λ)√ε_d · a = π(2a/λ)√ε_d。对 host=air（ε_d=1），x_Mie = π·(2a/λ)。

---

## 3. a_n / b_n（散射系数，μ 相等）

### B&H (4.56) a_n（电多极/TM）——已对原书 OCR 核
$$
a_n = \frac{m\psi_n(mx)\,\psi'_n(x) - \psi_n(x)\,\psi'_n(mx)}
         {m\psi_n(mx)\,\xi'_n(x) - \xi_n(x)\,\psi'_n(mx)}
$$

### B&H (4.57) b_n（磁多极/TE）——已对原书 OCR 核
$$
b_n = \frac{\psi_n(mx)\,\psi'_n(x) - m\,\psi_n(x)\,\psi'_n(mx)}
         {\psi_n(mx)\,\xi'_n(x) - m\,\xi_n(x)\,\psi'_n(mx)}
$$

**交叉验证**：
- 讲义 §2（`02_mie_strict.tex` L145-159）a_l/b_l 闭式与上式**逐字一致** ✅
- spec formalization `primary_BH_mie` 同 ✅
- B&H 页 101："Note that a_n and b_n vanish as m approaches unity"（m→1 时散射消失，物理自洽）✅

---

## 4. c_n / d_n（内部场系数）——gate③ 必核

### B&H (4.52) 一般 μ 形式（OCR 噪声大，转录待 gate③ 核）
B&H 原书 (4.52) 给的是带 μ_p/μ 比的内部场系数。**μ 相等（μ_p=μ）时**化简为：

### c_n（电/TM 内部场，分母同 b_n）✅ gate③ 用户已核（2026-08-05）
$$
c_n = \frac{m\psi_n(x)\,\xi'_n(x) - m\,\xi_n(x)\,\psi'_n(x)}
         {\psi_n(mx)\,\xi'_n(x) - m\,\xi_n(x)\,\psi'_n(mx)}
$$

### d_n（磁/TE 内部场，分母同 a_n）✅ gate③ 已核 + step04 分子修正（2026-08-05）
$$
d_n = \frac{m\psi_n(x)\,\xi'_n(x) - m\,\xi_n(x)\,\psi'_n(x)}
         {m\psi_n(mx)\,\xi'_n(x) - \xi_n(x)\,\psi'_n(mx)}
$$
> ⚠️ **step04 转录修正**：早期 spec/notes 把 d_n 分子第二项写成不带 m（−ξψ'），**违背球面切向边界条件**。正确是分子两项都带 m（与 c_n 分子相同）。已用 miepython 独立库交叉验证：修正版与 miepython.cn_dn 差异 1.4e-15，错误版差异 0.736。gate③ 当时只核了分母结构约束（c↔b、d↔a 配对），未逐字核分子第二项——教训：转录校对要逐项，不只核结构。

**B&H 原文结构约束（gate③ 用户对照扫描件逐字核）**：书页 100 原文（4.53 下方，逐字）：
> "Note that the denominators of the internal coefficients $c_n$ and $d_n$ are identical to those of the scattering coefficients $b_n$ and $a_n$, respectively."

自检：c_n 分母 = b_n 分母（$\psi_n(mx)\xi'_n - m\xi_n\psi'_n$）✅；d_n 分母 = a_n 分母（$m\psi_n(mx)\xi'_n - \xi_n\psi'_n$）✅；c_n/d_n 分子相同（$m\psi_n\xi'_n - m\xi_n\psi'_n$，两项都带 m）✅。

> ✅ **gate③ 裁决（2026-08-05）**：c_n/d_n 公式转录正确（分母 c↔b、d↔a 配对、分子两项带 m 都对）。⚠️ 引文措辞曾被我改写过（非逐字），已纠正为原文。内部场对则多极矩才可靠（Y9）。

---

## 5. 散射截面（B&H 4.4，讲义 §2 交叉）

$$
C_{\text{sca}} = \frac{2\pi}{k^2}\sum_{n=1}^{\infty}(2n+1)\bigl(|a_n|^2 + |b_n|^2\bigr)
$$
$$
C_{\text{ext}} = \frac{2\pi}{k^2}\sum_{n=1}^{\infty}(2n+1)\,\Re(a_n + b_n)
$$
$$
C_{\text{abs}} = C_{\text{ext}} - C_{\text{sca}}
$$

讲义 §2（L200-203）与上式一致 ✅。

**截断**：总 C_sca 用 Wiscombe $n_{\max} = \lceil x + 4x^{1/3} + 2\rceil$（x≤1.0 → n_max≈7）；per-multipole 分项只取 n=1,2。

---

## 6. per-multipole 映射（与 spec 一致）

| 多极 | Mie 系数 | 说明 |
|------|---------|------|
| ED 电偶极 | **a_n(n=1)** | a_n=电多极/TM |
| MD 磁偶极 | **b_n(n=1)** | b_n=磁多极/TE |
| EQ 电四极 | **a_n(n=2)** | |
| MQ 磁四极 | **b_n(n=2)** | |

> B&H 页 101 原文确认 a_n=电多极、b_n=磁多极（"a_l 电多极/TM 对应 Grahn a_E；b_l 磁多极/TE 对应 a_M"——讲义 §2 的 important 框）。

---

## 7. scipy.special 实现方案

| B&H 符号 | scipy | 备注 |
|---------|-------|------|
| $j_n(\rho)$ | `scipy.special.spherical_jn(n, rho)` | 正则球 Bessel |
| $y_n(\rho)$ | `scipy.special.spherical_yn(n, rho)` | Neumann |
| $h_n^{(1)}(\rho)$ | `spherical_jn + 1j*spherical_yn` | $h^{(1)} = j + iy$ |
| $\psi_n(\rho)=\rho j_n(\rho)$ | `rho * spherical_jn` | |
| $\xi_n(\rho)=\rho h_n^{(1)}(\rho)$ | `rho * (sj + 1j*sy)` | |
| $\psi'_n$ | `spherical_jn(n, rho, derivative=True)` 组合 | 或数值/递推 |
| $\xi'_n$ | 同上（h^{(1)} 导数） | |

> 用 scipy.special，不自写特殊函数（self-evo 纪律）。复宗量 mx 直接支持（Akimov case 已验证）。

---

## 8. gate③ 核对结果（2026-08-05 用户对扫描件逐字核）

| # | 项 | 裁决 |
|---|----|------|
| 1 | **c_n/d_n** 对 B&H 书页 100 (4.52) | ✅ 公式转录正确（c↔b、d↔a 分母配对、分子两项带 m 都对） |
| 2 | **a_n/b_n** 对 B&H 页 101 (4.56/4.57) | ✅ 一致 |
| 3 | **尺寸参数 x_Mie** | ✅ host=air 时 x_Mie = π(2a/λ)；**step04 必须用此换算，test 用磁偶极峰位锚点校验** |
| 4 | 相对误差分母 | 现定 C_Mie，论文另有约定则以论文为准 |
| 5 | ⚠️ 引文措辞 | 4.53 那句英文曾被我改写（非逐字），已纠正为原文 "cₙ and dₙ … bₙ and aₙ respectively" |

> 🔴 **step04 硬性要求（gate③ 裁决）**：x_Mie = π·(2a/λ)（host=air），不得直接拿 2a/λ 当 x_mie。
> **test 锚点（step04 实测，2026-08-05，n=2.5）**：
> - ED a_1 峰 2a/λ=0.500（x_mie=π/2≈1.571，Fröhlich 偶极共振）
> - MD b_1 峰 2a/λ=0.385（x_mie≈1.209，ka·n≈π 球内驻波，物理自洽）
> - EQ a_2 峰 0.647（x_mie=2.033）；MQ b_2 峰 0.543（x_mie=1.705）
> ⚠️ 早期 spec 记"MD 峰 2a/λ≈0.5–0.7"是凭直觉猜错（该区间实为 EQ/MQ 峰混合区），已按实测修正。若峰位偏 π 倍 = x_Mie 换算错。
