# mie-f 文献阅读完整交付

> 生成时间：2026-07-26
> 阅读执行：主 agent 精读 4 篇核心论文 + 4 个子 agent 并行处理参考与工具材料

---

## 一、文件索引总表

### 1.1 核心论文（已精读）

| 文件 | 路径 | 阅读方式 | 可信度 |
|------|------|---------|--------|
| **综合阅读摘要** | `papers/mie-f/mie-f-reading-synthesis.md` | — | — |
| **Grahn 2012** | `papers/mie-f/02-理论核心/Grahn_2012_Electromagnetic_Multipole_Theory_for_Optical_Nanomaterials.pdf` | pdf-mcp 直读 | 原生 LaTeX PDF，12 页全文可读 |
| **Alaee 2018** | `papers/mie-f/01-主论文/Alaee_2018.ocr/Alaee_2018.md` | OCR Markdown | C 级（页 2-4 公式需复核） |
| **FC2015** | `papers/mie-f/02-理论核心/Fernandez-Corbaton_2015.ocr/Fernandez-Corbaton_2015.md` | OCR Markdown | **A 级** |
| **FC2017** | `papers/mie-f/02-理论核心/Fernandez-Corbaton_2017_On_the_Dynamic_Toroidal_Multipoles_from_Localized_Electric_Current_Distributions.pdf` | pdf-mcp 直读 | 原生 PDF，8 页全文可读 |

### 1.2 参考与工具（子 agent 产出摘要）

| 文档 | 摘要路径 | 原文 OCR 路径 | OCR 可信度 |
|------|---------|--------------|-----------|
| **Bohren & Huffman 1983** | `papers/mie-f/reference-summaries/Bohren_Huffman_1983.md` | `papers/mie-f/03-参考与工具/Bohren_Huffman_1983.ocr/Bohren_Huffman_1983.md` | **B 级**（11146 行，扫描书） |
| **Jackson 1999 Ch4/9/10** | `papers/mie-f/reference-summaries/Jackson_1999_Ch4_9_10.md` | `papers/mie-f/03-参考与工具/Jackson_1999_Ch4_9_10.ocr/Jackson_1999_Ch4_9_10.md` | **C 级**（2932 行，扫描教材） |
| **Johnson & Christy 1972** | `papers/mie-f/reference-summaries/Johnson_Christy_1972.md` | `papers/mie-f/03-参考与工具/Johnson_Christy_1972.ocr/Johnson_Christy_1972.md` | **B 级**（227 行，原生文字 PDF） |
| **Mühlig 2014** | `papers/mie-f/reference-summaries/Muhlig_2014.md` | `papers/mie-f/03-参考与工具/Muhlig_2014.ocr/Muhlig_2014.md` | **B 级**（2220 行，混合型 PDF） |

### 1.3 OCR 可信度说明参考

另见 `papers/mie-f/README-OCR.md`（详细逐文档可信度分析）。

---

## 二、阅读路线

```
Grahn 2012 ─────（框架基础）─────→ Alaee 2018
    ↑                                  ↑
    │                         ┌────────┴────────┐
    │                    FC2015             FC2017
    │               （偶极精确公式）    （toroidal 澄清）
    └─────── 参考材料 ────────┘
                     ↓
     Bohren & Huffman / Jackson（当公式字典）
     Johnson & Christy（材料常数）
     Mühlig（多极分析 + T-matrix）
```

---

## 三、核心论文精读发现

### 3.1 Grahn 2012 — 电流多极理论框架

**阅读方式**：pdf-mcp 直读（原生 LaTeX PDF，12 页，全文字可读）

**核心贡献**：建立"散射电流密度 → 电流多极张量 $p,Q,O$ → 场展开系数 $a_E,a_M$"的完整映射。

**关键公式**：
- 散射电流密度定义：$\mathbf{J}_S(\mathbf{r}) = -i\omega\epsilon_0[\epsilon_r(\mathbf{r})-\epsilon_{r,d}]\mathbf{E}(\mathbf{r})$ (Eq 6)
- 直接从 $J_S$ 算 $a_E(l,m)$ / $a_M(l,m)$ 的体积分公式 (Eqs 15-16) — 数值计算直接用
- 电流多极张量 $p \equiv M^{(1)}$, $Q \equiv M^{(2)}$, $O \equiv M^{(3)}$ (Eq 27)
- $p,Q,O$ → $a_E(l,m),a_M(l,m)$ 的**完整映射表** (Eqs 35-48)

**两大发现**：
1. **暗模式**：球对称四极 $Q_{xx}=Q_{yy}=Q_{zz}$ 不产生电磁场；八极中也有 3 组暗模式
2. **高阶伪装成低阶**：零偶极矩的八极电流分布可产生和偶极完全一样的场（$\tilde{p}_z = 2O_{xxz}k^2$）

**与 Alaee 2018 的关系**：Grahn 的 Eqs 15-16 是"从电流算系数"；Alaee 的 Table 2 是"从电流算多极矩"——两套公式在偶极阶等价。

---

### 3.2 FC2015 — 精确偶极矩推导

**阅读方式**：OCR Markdown（A 级高可信）

这是 Alaee 2018 精确偶极公式的源论文（合著者 FC 与 Alaee 2018 相同）。

**方法学**：
- 从动量空间出发，利用 **Devaney-Wolf 定理**：源产生的辐射场仅由 $|\mathbf{p}|=\omega/c$ 动量壳上的 Fourier 分量决定
- 球贝塞尔函数在此起 **Dirac delta $\delta(|p|-k)$** 作用，从电流的全体 Fourier 分量中筛选出 $\omega/c$ 壳上的贡献 (Eq 25)

**产出公式**：

磁偶极 (Eq 20)：
$$
b_{1m}^\omega = -\frac{\sqrt{3}}{2\pi}\int d^3r\ \hat{r}\times \mathbf{J}_\omega(\mathbf{r})\,j_1(kr)
$$

电偶极 (Eq 21)：
$$
a_{1m}^\omega = -\frac{1}{\pi\sqrt{3}}\int\mathbf{J}_\omega j_0(kr) - \frac{1}{2\pi\sqrt{3}}\int\{3[\hat{r}^\dagger\mathbf{J}_\omega]\hat{r} - \mathbf{J}_\omega\}j_2(kr)
$$

**近似展开**：$j_0\approx 1-(kr)^2/6$, $j_1\approx kr/3$, $j_2\approx(kr)^2/15$ → 标准小源近似 + toroidal 项（次高阶）+ 更高阶修正 (Eqs 32-34)

**螺度 (helicity) 偶极**：$g_{jm\pm}^\omega = (b_{jm}^\omega \pm a_{jm}^\omega)/\sqrt{2}$，对应确定偏振手性的辐射 (Eqs 40-41)

---

### 3.3 FC2017 — Toroidal 不是独立多极类

**阅读方式**：pdf-mcp 直读（原生文字 PDF，8 页全文可读）

**核心命题**：动态 toroidal 多极**没有独立物理意义**——它们是电宇称多极系数 $a_{jm}^\omega$ 做小源尺寸展开时的次高阶项。

**证明路线**：
1. 精确式 (Eq 4)：$a_{1m}^\omega$ = $\int j_0(kr)$ 项 + $\int j_2(kr)$ 项
2. 小 $kr$ 展开 → 零阶项 = 标准电偶极 (Eq 5)，$k^2$ 项 = toroidal dipole (Eq 6)
3. **壳外分量渗漏**：完整 $j_0(kr)$ 通过 $\delta(|p|-k)$ 滤除非辐射分量；拆开后单项 $(kr)^0$ 失去此过滤，拆分两部分各含不辐射的壳外分量 → 无法通过远/近场测量单独确定
4. 即使采用无壳外分量的拆分（完整球贝塞尔函数），两部分仍含**纵向分量**不可检测——纵向电场被电荷密度场精确抵消
5. **反驳光谱分离**：若 $k^2$ 因子可用来分离不同阶，则会推出无穷多独立多极族 —— 荒谬

**结论**：双宇称（electric + magnetic）足以完整描述电磁跃迁。Toroidal 仅用于改进小源近似精度。

**与 FC2015 的关系**：FC2015 精确推导了偶极，FC2017 用这个精确表达式分析了 toroidal 的本质。

---

### 3.4 Alaee 2018 — 精确多极矩公式集大成

**阅读方式**：OCR Markdown（C 级，页 2-4 公式需复核）

**核心产出**：精确多极矩公式 Table 2，将所有近似式中的常数替换为球贝塞尔函数：

| 极次 | 近似 (Table 1) | 精确 (Table 2) |
|------|---------------|---------------|
| ED $p$ | $\propto \int \mathbf{J}$ | $\propto \int \mathbf{J} j_0(kr) + \int[3(\hat{r}\cdot\mathbf{J})\hat{r}-\mathbf{J}]j_2(kr)$ |
| MD $m$ | $\propto \int \mathbf{r}\times\mathbf{J}$ | $\propto \int \mathbf{r}\times\mathbf{J}\,j_1(kr)/(kr)$ |
| EQ/MQ | 含 $k^2 r^2$ 项 | 含 $j_1, j_2$ |

**验证**：
- 与 Mie 理论在**所有** $2a/\lambda$ 下完美吻合 (Fig 2)
- 近似公式在 $2a/\lambda\approx 0.75$ 时误差超 100% (Fig 1c/d)
- 耦合金纳米盘 ($a=250$nm) 误差达 25% (Fig 3b)

**Toroidal 澄清**："不需要引入第三类多极（toroidal）。精确表达式揭示 toroidal 多极是电多极展开的次高阶项。"

> **关键提醒**：Table 2 中的精确多极矩公式在本 OCR 中的保真度为 C 级。页 2-4 的公式/表格如果要用作数值实现，建议重新从 PDF 提取公式或人工核对。

---

## 四、参考材料摘要内容概览

### 4.1 Bohren & Huffman 1983（663 行摘要）

**关键内容**：
- Ch4 完整的 Mie 理论 (Eqs 4.42-4.90) — $a_l,b_l$ 系数定义、散射截面、消光截面
- VSH 定义、角函数 $\pi_l(\theta),\tau_l(\theta)$ 递推
- Rayleigh 近似 ($x\ll1$) 的完整级数展开
- Aden-Kerker 涂层球 Mie 系数
- 非球形方法（T-matrix, DDA, 分离变量法）
- 光学常数模型（Lorentz, Drude, K-K）
- Wiscombe 收敛判据：$l_{\max} = x + 4x^{1/3} + 2$

**与 mie-f 的关系**：Grahn 2012 中散射截面公式 (Eq 20) 直接引用此书 [11]；所有 Mie 系数、散射截面公式的标准参考文献。

**信任须知**：B 级。后半段公式密集页 (124-140/142/144-150/152/154/156/158-160/188/197-200/212-215) 的 UNCERTAIN 公式需人工核实。

### 4.2 Jackson 1999 Ch4/9/10（450 行摘要）

**关键内容**：
- Ch4 — 静电多极（球谐展开、多极矩、勒让德展开）
- Ch9 — 辐射（VSH 定义、多极辐射场 Eq 9.165、多极矩与辐射功率 Eq 9.169-170）
- Ch10 — 散射（Mie 散射 Eq 10.56-10.57、光学定理、Rayleigh 散射）

**与 mie-f 的关系**：
- Alaee 2018 引用 Jackson Eq 9.165（不含磁化电流版本，即不含 $+\nabla\times M$ 项）
- Grahn 2012 全篇基于 Jackson 的多极展开框架 (Eqs 1-5 = Jackson §9.10)
- Grahn Eqs 11-12（$J_S$ 满足的波动方程）对应 Jackson 的处理

**信任须知**：C 级。$Y_{l0}$ 被误识别为 $Y_{I0}$，长公式有 OCR 错误，§10.5-§10.10 缺失。关键公式必须核对原 PDF。

### 4.3 Johnson & Christy 1972（232 行摘要）

**数据**：
- 三种金属：Cu, Ag, Au
- 能量范围 0.5-6.5 eV (190-2480 nm)
- Table I: n, k 在约 21 个离散能量点的测量值（OCR 仅捕获到 Au 的 0.64-3.12 eV 段）
- 介电函数曲线为图内嵌图像
- Drude 参数 $m^*/\tau$?

**在 mie-f 中的用途**：Alaee 2018 引用为 ref [38]，用于金球 ($a=250$nm) 的 Mie 仿真。

**备选数据源**：Palik (1985/1998), Rakic et al. (1998), Olmon et al. (2012, Au), Babar & Weaver (2015)

**信任须知**：B 级。页 5-10 仅有视觉核对。已知修复：$m_0$, $\epsilon_2$, $\omega_p$ 的 OCR 错误。

### 4.4 Mühlig 2014（277 行摘要）

**结构**：5 章，147 页博士论文，自组装超材料方向。

**关键方法**：
- 多极分析：近场投影法 $a_{nm}/b_{nm}$ → 笛卡尔矩
- T-matrix：球簇 T-matrix（Stein/Cruzan 平移加法定理 + Wigner 3jm 符号）
- Clausius-Mossotti 有效介质理论
- VSH 定义 (Eqs 2.16-2.17)，Mie 系数 (Eq 2.21)，投影公式 (Eq 2.28)，转换规则 (Eqs 2.29-2.30)
- 截断准则 $N = x + 4x^{1/3} + 2$

**与核心论文的关系**：
- 作者属于同一 KIT 组（Rockstuhl/Lederer）
- Grahn 2012 引用了更早的 Mühlig 2011 [8]
- Alaee 2018 是这个统一框架的进一步发展
- Mühlig 比 Alaee 多 T-matrix 完整推导 + EMA 应用

**信任须知**：B 级。页 21-40 OCR baseline 访问被拒，该段无硬保证。符号表 LaTeX 严重损坏。

---

## 五、四篇核心论文的递进关系

```
                 支撑┌─────────────────────┐
       ┌───────────┤  FC2015 — 偶极精确公式  │
       │            │  动量空间法·Devaney-Wolf│
       │            └─────────────────────┘
       │                       │
┌──────────────┐              ├── 提供 a_1,m 精确闭式 ──→ ┌──────────────┐
│  Grahn 2012  │              │                            │  Alaee 2018  │
│  电流多极框架  │── 提供 a_E,a_M ──→               │  精确多极矩   │
│  J_S → a_E,a_M│    映射 + J_S 方法               │  Table 2 全集 │
│  p,Q,O 可视化 │              │                            │  与 Mie 验证  │
└──────────────┘              ├── 提供 a_1,m 展开分析 ──→ └──────────────┘
       │            │                                     （澄清 toroidal）
       │            └─────────────────────┐
       └───────────┤  FC2017 — Toroidal 澄清 │
                    │  高阶项·非独立·壳外分量   │
                    └─────────────────────┘
```

**关键理解**：
- Grahn 2012 给框架（全场→电流→系数映射）
- FC2015 给偶极精确公式（Alaee Table 2 中 ED/MD 的来源）
- FC2017 给 toroidal 的本质分析（不是独立族，是展开高阶项）
- Alaee 2018 统一产出 Table 2（全部极次的精确公式），与 Mie 完美验证

**对比近似 vs 精确的本质**：近似公式是精确式中球贝塞尔函数取 $kr\to0$ 极限的结果：
$$
j_0(kr) \approx 1 - \frac{(kr)^2}{6},\quad j_1(kr) \approx \frac{kr}{3},\quad j_2(kr) \approx \frac{(kr)^2}{15}
$$
当 $2a/\lambda \gtrsim 0.3$ 时，近似误差开始显著；到 $0.75$ 时超过 100%。

---

## 六、如何进行 Mie 理论复现（参考索引）

| 需要什么 | 去哪里查 |
|---------|---------|
| Mie 系数 $a_l, b_l$ 定义 | Bohren Ch4 / Jackson §10.3-10.4 / Mühlig Eq 2.21 |
| 从电流算多极 $a_E, a_M$ | Grahn Eqs 15-16 |
| 精确多极矩 $p, m, Q^e, Q^m$ | Alaee Table 2 |
| 偶极精确公式推导 | FC2015 Eqs 20-22 |
| 散射/消光截面公式 | Grahn Eqs 20/22-23 / Bohren |
| Toroidal 是否独立 | FC2017 → 否 |
| 球贝塞尔函数递推 | Jackson / Bohren / 数值库 |
| 收敛判据 | Bohren / Mühlig: $l_{\max} = x + 4x^{1/3} + 2$ |
| 贵金属 $\epsilon(\omega)$ | Johnson & Christy（或备选: Palik, Rakic） |
| T-matrix 数值实现 | Mühlig Ch3 |
