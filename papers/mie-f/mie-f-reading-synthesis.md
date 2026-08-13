# mie-f 文献阅读综合摘要

> 阅读时间：2026-07-26
> 阅读方式：Grahn 2012 / FC2017 用 pdf-mcp 读原生 PDF；Alaee 2018 / FC2015 用 OCR markdown（FC2015 为 A 级，Alaee 2018 为 C 级）
> 4 份参考与工具材料由子 agent 并行处理后落盘至 `reference-summaries/`

---

## 1. 阅读路线

```
Grahn 2012 ────（框架基础）────→ Alaee 2018
                                      ↑
                              ┌───────┴───────┐
                          FC2015          FC2017
                      （偶极精确公式）   （toroidal 澄清）
```

---

## 2. Grahn 2012 — 电流多极理论框架（已精读全文12页）

**核心贡献**：建立"散射电流密度 → 电流多极张量 → 场展开系数"的完整映射。

### 2.1 散射电流密度法 (Sec 2)

定义：
$$
\mathbf{J}_S(\mathbf{r}) = -i\omega\epsilon_0\left[\epsilon_r(\mathbf{r}) - \epsilon_{r,d}\right]\mathbf{E}(\mathbf{r})
$$

此电流密度是**每个颗粒的自洽散射源**，只需知道颗粒内部的 $\mathbf{E}(\mathbf{r})$ 即可计算多极系数，无需像传统方法那样在包围球面上积分散射场。

### 2.2 场展开系数与电流的直接关系 (Eqs 15-16)

电场多极系数 $a_E(l,m)$ 和磁场多极系数 $a_M(l,m)$ 直接表达为 $\mathbf{J}_S$ 的体积分，含 Riccati-Bessel 函数 $\Psi_l(kr) = kr j_l(kr)$：

- $a_E(l,m)$ — 涉及 $\hat{r}\cdot\mathbf{J}_S$、$\hat{\theta}\cdot\mathbf{J}_S$、$\hat{\phi}\cdot\mathbf{J}_S$ 三项，含 $\Psi_l$ 及其一阶二阶导数
- $a_M(l,m)$ — 涉及 $\hat{\theta}\cdot\mathbf{J}_S$ 和 $\hat{\phi}\cdot\mathbf{J}_S$，含 $j_l(kr)$

### 2.3 电流多极张量 (Sec 3)

用**点电流元素法**（Harrington 1961）构造正交电流模式：

- 一阶 $M^{(1)} = \mathbf{p}$：偶极
- 二阶 $M^{(2)} = \mathbf{Q}$：四极
- 三阶 $M^{(3)} = \mathbf{O}$：八极

通过圆坐标系 $(w, w^*, z)$ 推导出 $p, Q, O$ 到 $a_E(l,m), a_M(l,m)$ 的显式映射 (Eqs 35-48)。

### 2.4 两大核心发现

**发现① — 暗模式**：球对称四极激发 $Q_{xx}=Q_{yy}=Q_{zz}$ 不产生任何电磁场（径向振荡正电球壳 + 中心负电）。八极中也有 3 组对称暗模式。

**发现② — 高阶伪装成低阶**：八极矩可产生与偶极完全相同的辐射场。例如 $\tilde{p}_z = 2O_{xxz}k^2$，即一个零偶极矩的八极电流分布可以产生与偶极相同的场。Eq. 49 的矢势推导展示：梯度项不贡献辐射。

> **对理论复现的意义**：Eqs 15-16 是数值计算 Mie 多极系数的直接公式；Eqs 35-48 是电流模式 → 多极系数的完整映射表。

---

## 3. Alaee 2018 — 超越长波长近似的精确公式（已精读全文5页）

### 3.1 核心信息

| 对比 | 近似公式（Table 1） | 精确公式（Table 2） |
|------|-------------------|-------------------|
| ED | $p \approx \int J d^3r$ | $p = -\frac{1}{i\omega}\int J j_0(kr) d^3r + \frac{k^2}{i\omega}\int[3(\hat{r}\cdot J)\hat{r} - J]j_2(kr)d^3r$ |
| MD | $m \approx \frac{1}{2}\int(r\times J)d^3r$ | $m = \frac{3}{2}\int(r\times J)j_1(kr)d^3r/[kr]$ |
| EQ | 含 $k^2$ 和 $r^2$ 项 | 含 $j_1(kr)$ 和 $j_2(kr)$ |
| 本质 | $j_0\approx1$, $j_1\approx kr/3$, $j_2\approx(kr)^2/15$ | 完整球贝塞尔函数 |

### 3.2 验证结果

- 与 Mie 理论在**所有尺寸参数 $2a/\lambda$** 下完美吻合（Fig 2）
- 近似公式在 $2a/\lambda \approx 0.75$ 时误差超 100%（Fig 1c/d）
- 耦合金纳米盘（$a=250$nm，$g=120$nm）的误差也达 25%（Fig 3b）

### 3.3 Toroidal 澄清

"不需要引入第三类多极（toroidal）。精确表达揭示 toroidal 多极仅是电多极展开的次高阶项。"

---

## 4. FC2015 — 精确偶极矩的推导（已读全文744行，A级可信）

### 4.1 方法

从动量空间出发：利用 Devaney-Wolf 定理——源产生的电磁场完全由 $|\mathbf{p}|=\omega/c$ 动量壳上的 Fourier 分量决定。通过球贝塞尔函数的 Dirac delta 性质 $\int r^2 j_l(pr)j_l(kr)dr = (\pi/2k^2)\delta(p-k)$ 自然实现动量筛选。

### 4.2 精确偶极公式 (Eqs 20-22)

**磁偶极** $b_{1m}^\omega$：
$$
b_{1m}^\omega = -\frac{\sqrt{3}}{2\pi}\int d^3r\ \hat{r}\times J_\omega(r)\,j_1(kr)
$$

**电偶极** $a_{1m}^\omega$：
$$
a_{1m}^\omega = -\frac{1}{\pi\sqrt{3}}\int J_\omega j_0(kr) - \frac{1}{2\pi\sqrt{3}}\int\left\{3[\hat{r}^\dagger J_\omega]\hat{r} - J_\omega\right\} j_2(kr)
$$

**纵向** $c_{1m}^\omega$：形式类似（不对辐射场贡献）。

### 4.3 小源近似

- 一阶：$j_0\approx1$，$j_1\approx kr/3$ → 标准偶极近似
- 二阶：含 $j_2\approx(kr)^2/15$ → toroidal dipole 出现
- 高阶修正：$k^3$ 磁修正（Eq 32）、$k^4$ 电/toroidal 修正（Eqs 33-34）

### 4.4 螺度（helicity）多极

变换到 helicity 基矢 $g_{jm\pm}^\omega = (b_{jm}^\omega \pm a_{jm}^\omega)/\sqrt{2}$，给出确定偏振手性辐射的偶极公式。

> **与 Alaee 2018 的关系**：FC2015 的 Eq. 21 正是 Alaee 2018 Table 2 中精确偶极公式的源头。合著者 FC 同是两篇论文的作者。

---

## 5. FC2017 — Toroidal 不是独立多极类（已读全文8页，A级可信）

### 5.1 核心命题

**Toroidal 多极没有独立的物理意义**——它们是对电宇称多极系数 $a_{jm}^\omega$ 做小源展开时的次高阶项。

### 5.2 证明路线

1. **精确表达式出发点** (Eq 4)：$a_{1m}^\omega$ 含 $j_0(kr)$ 和 $j_2(kr)$ 两项积分
2. **小参数展开**：$j_0\approx1-(kr)^2/6$，$j_2\approx(kr)^2/15$ → 零阶项 $e_1$（标准电偶极）+ $k^2$ 项 $t_1$（toroidal dipole）
3. **壳外分量渗漏**：原始的 $j_0(kr)$ 在完整形式中通过 $\delta(|p|-k)$ 滤除 $|p|\neq\omega/c$ 的分量；拆开后的单项 $(kr)^0$ 不具备此过滤功能
4. **拆分的两部分各含不辐射的壳外分量** → 无法通过远/近场测量单独确定

### 5.3 对"无壳外分量拆分"的分析

即使采用完整球贝塞尔函数拆分（无壳外分量泄漏），两部分仍因含有**纵向分量**而不可分离——纵向电场被电荷密度产生的场精确抵消。

### 5.4 对"光谱分离"的反驳

若利用 $k^2$ 因子来分离不同阶项，则会推出**无穷多个独立多极族**的荒谬结论。

### 5.5 结论

> Toroidal 多极就是电宇称多极系数在源电磁尺寸展开中的高阶项。完整的双宇称（electric + magnetic）足以描述所有电磁跃迁。

---

## 6. 四篇文献的递进关系

```
Grahn 2012                FC2015                      FC2017
│                          │                           │
│ 电流多极张量映射         │ 偶极精确公式推导           │ toroidal 非独立证明
│ a_E/a_M ← p/Q/O          │ 动量空间方法                │ 壳外分量/纵向分量
│ (全场→电流→场)           │ (Devaney-Wolf 定理)         │
│                          │                           │
└──────────┬───────────────┴───────────┬───────────────┘
           │                           │
           ▼                           ▼
       Alaee 2018                 （参考整合）
        精确公式 Table 2
        超越 LWA
        与 Mie 完美吻合
```

- **Grahn 2012** 提供了完整的 $\mathbf{J}_S \to a_E, a_M$ 映射框架和电流模式可视化
- **FC2015** 在偶极阶给出了精确闭式，是 Alaee 2018 偶极公式的直接来源
- **FC2017** 从基本原理上澄清了 toroidal 的数学本质（高阶展开项，非独立族）
- **Alaee 2018** 是集大成者：把偶极、四极公式统一给出 Table 2，是直接可用于数值计算的最终公式

---

## 7. 对 Mie 理论复现的参考价值

| 需要什么 | 去哪里查 |
|---------|---------|
| Mie 系数 $a_l, b_l$ 定义 | Grahn 2012 Eq 1-2 / Bohren & Huffman |
| 从电流算 Mie 系数 | Grahn 2012 Eqs 15-16 |
| 精确多极矩公式（数值计算用） | Alaee 2018 Table 2 |
| 偶极精确公式的推导来源 | FC2015 Eqs 20-22 |
| Toroidal 是否独立 | FC2017 → 不需要，是电偶极的高阶项 |
| 暗模式/等价性 | Grahn 2012 Sec 3 |
| 材料光学常数 | Johnson & Christy 1972 |
| T-matrix 应用 | Mühlig 2014 |
