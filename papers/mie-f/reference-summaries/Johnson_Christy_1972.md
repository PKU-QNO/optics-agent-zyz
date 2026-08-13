# Johnson & Christy (1972) — Optical Constants of the Noble Metals

> P. B. Johnson and R. W. Christy, *Optical constants of the noble metals*, Phys. Rev. B 6 (1972) 4370–4379.

---

## 1. 数据内容

### 覆盖金属

| 金属 | 膜厚范围 | 备注 |
|------|---------|------|
| **Cu** (copper) | 297, 305, 486 A | 三个样品，厚膜值一致 |
| **Ag** (silver) | 304, 375 A | 两个样品，厚度无关性验证 |
| **Au** (gold) | 343, 456 A; 另186 A 异常膜 | 186 A 膜退火后仍不代表 bulk；>250 A 方可靠 |

**不含 Al, Ni, Cr, Pt, Pd, Ti** 等其他常用金属。只有三种贵金属 (noble metals): Cu, Ag, Au。

### 光谱范围

- **能量**: 0.5 – 6.5 eV
- **波长**: 约 190 – 2480 nm（\(\lambda\)[nm] = 1240 / \(E\)[eV]）
- **数据点**: 论文 Table I 列出约 21 个能量点 (0.64 – 3.12 eV)，其余范围仅有图形数据 (Fig. 2–4)

### 表格量

Table I 以 0.5 – 6.5 eV 全范围列了部分离散数据点，但 OCR 版仅捕获了 0.64 – 3.12 eV 段的 Au 数据（OCR 第 89-111 行）。完整 Table I 在 PDF 中，本 OCR 基线未完全捕捉。

### 提供的常数

| 符号 | 名称 | 说明 |
|------|------|------|
| \(n\) | 折射率实部 | 直接测量反演得到 |
| \(k\) | 消光系数 | 直接测量反演得到 |
| \(\epsilon_1 = n^2 - k^2\) | 介电常数实部 | 论文在图中给出，未在 Table I 直接列 |
| \(\epsilon_2 = 2nk\) | 介电常数虚部 | 论文在图中给出 |
| \(\epsilon_2^b\) | 带间贡献（虚部） | \(\epsilon_2^b = \epsilon_2 - \epsilon_2^f\)（减去 Drude 自由电子部分） |
| \(m_0\) | 有效光学质量 | Table II: Cu 1.49, Ag 0.96, Au 0.99 (单位 electron masses) |
| \(\tau\) | 弛豫时间 | Table II: Cu 6.9e-15, Ag 31e-12 (!), Au 9.3e-15 s |

> **注意**: OCR 中 Table II 的银弛豫时间显示为 \(31 \pm 12 \times 10^{-15}\) s，但原文可能不同，需复核。

### 提取参数

论文从红外区 Drude 模型拟合得到：
- \(\omega_p\) (等离子体频率)
- \(m_0\) (有效光学质量)
- \(\tau\) (弛豫时间)

方法：作 \(-\epsilon_1\) vs \(\lambda^2\) 图得斜率 \(\propto 1/m_0\)；作 \(\epsilon_2/\lambda\) vs \(\lambda^2\) 图得 \(\tau\)。

---

## 2. 数据存取方式

### 当前格式

| 来源 | 格式 | 质量 | 存取路径 |
|------|------|------|---------|
| OCR Markdown | `.md` | **B 级** | `03-参考与工具/Johnson_Christy_1972.ocr/Johnson_Christy_1972.md` |
| 原始 PDF | 原生文字 PDF | 好 | 同上目录下 `.pdf` 文件 |

### OCR 覆盖情况

- **全文 227 行**, 覆盖了标题、摘要、Introduction (I) 到 Summary (VI) 全部文本段落。
- **表格**: Table I 仅有片段 (Au 数据 0.64–3.12 eV，21 行)；Table II 完整 (m_0, tau) 但银弛豫时间 OCR 可能有误。
- **图形**: 全部为嵌入图片 (9 张 JPG)，未提取数值。图 Fig. 2–6, 图例保留但曲线数据不可直接读取。

### 数值 vs 图形数据

| 数据类型 | 存取方式 | 可用性 |
|---------|---------|-------|
| Table I (n, k) | OCR 文本部分捕获 | **仅 Au, 0.64-3.12 eV，其余需读 PDF** |
| Table II (m_0, tau) | OCR 文本 | 完整，已确认修复 `m_0` 下标 |
| \(\epsilon_1\), \(\epsilon_2\) 曲线 | 图形 (Fig. 2-4) | 仅视觉/图片，未提取数值 |
| \(\epsilon_2^b\) 曲线 | 图形 (Fig. 7-9) | 仅视觉/图片 |
| 原始反射/透射数据 | 未提供 | 论文未直接发表原始测量值 |

### 实用建议

要获取完整的 n, k 表格数据（覆盖全部三种金属和全谱段），**优先直接读原始 PDF**，而非依赖 OCR 片段。OCR 版本适用于粗检索和文本理解。

---

## 3. 可信度注意事项

**当前可信度等级: B**

依据 `README-OCR.md`:

### 已确认修复 (确定性错误，已被 `manual_actions.md` / `FINAL_REVIEW_SUMMARY.md` 记录)

| 位置 (行号) | 原 OCR 错误 | 修复 |
|------------|------------|------|
| 第 1 行标题 | `CONTANTS` | → `CONSTANTS` |
| 第 3 行作者行 | 空格异常 | 已修复间距 |
| Table II 表头 | `m 0` | → `m_0` |
| 第 19 页 (OCR) | `\epsilon_s` | → `\epsilon_2` (下标 2 误为 s) |
| 第 19 页 (OCR) | `\omega_{\rho}` | → `\omega_p` (下标 p 误为 rho) |

### 剩余已知问题

| 问题 | 说明 |
|------|------|
| **5-10 页仅有视觉核对** | 这 6 页正文经过了视觉检查（无缺页、旋转），但未做严格逐字 OCR 对照。公式符号仍可能有误。 |
| **PDF 实际止于第 10 页** | 当前 PDF 共 10 页；之前假设的 11-20 页不存在。页面 `13-20` 的 continued 报告是针对其他版本的 PDF。 |
| **Table I 不完全** | OCR 仅抓取了 Au 的 21 个能量点。全表需看 PDF |
| **图形数值未提取** | \(\epsilon_1\), \(\epsilon_2\) 曲线数据不可直接读 |

### 建议

- **普通检索、阅读、粗引用**: 可用。
- **关键数值引用（n, k, epsilon）**: 必须核对原始 PDF Table I / 图形。
- **严格逐字复用 5-10 页**: 需先恢复可用 OCR baseline 后重核。
- **Drude 公式 OCR**: 第 125-157 行的 Drude 公式已 OCR 但可能有符号歧义（如 `N` vs `\lambda` 混淆），须谨慎。

---

## 4. 在 mie-f 中的用途

### 主要引用

**Alaee 2018** 引用了本文作为金 (gold) 球 Mie 散射计算的介电函数来源：

> Ref [38]: P.B. Johnson, R.W. Christy, Optical constants of the noble metals, Phys. Rev. B 6 (1972) 4370–4379.

具体用法见 `01-主论文/Alaee_2018.ocr/Alaee_2018.md` Fig. 2 说明：
> "For a gold sphere with a fixed radius of a=250 nm"

### Mie 理论需求

在 `mie-f` 项目的 Mie 理论计算中，需要 \(\epsilon(\omega)\) 作为输入量。Johnson & Christy 数据提供：
1. **离散能量点的 \(\epsilon_1(\omega), \epsilon_2(\omega)\)** — 可直接用于 Mie 系数计算
2. **Drude 模型参数 (\(m_0, \tau, \omega_p\))** — 可通过拟合外推到未测量的波长范围

### 适用场景

| 场景 | 适用性 |
|------|-------|
| 可见-近紫外 Mie 散射 (0.5-6.5 eV) | 直接使用表格/图形数据 |
| 红外区 Mie 散射 (<0.5 eV) | 需 Drude 模型外推或使用其他源 |
| 金银对比 | JC 数据（同一实验条件、同方法）优于拼接多源 |
| 铜的 Mie 散射 | 同样覆盖，但应用中较少 |

### 参数表 (Alaee 2018 实际使用)

Alaee 2018 的具体 Drude 参数（来自 JC 或近似拟合）需要查看该论文正文。JC 本身提供的参数为：

| 参数 | Cu | Ag | Au |
|------|----|----|-----|
| \(m_0\) (electron masses) | 1.49 ± 0.06 | 0.96 ± 0.04 | 0.99 ± 0.04 |
| \(\tau\) (×10^{-15} s) | 6.9 ± 0.7 | 31 ± 12 | 9.3 ± 0.9 |

---

## 5. 备选数据源

### 常用贵金属光学常数数据源

| 数据源 | 覆盖范围 | 优点 | 缺点 |
|--------|---------|------|------|
| **Johnson & Christy (1972)** | Cu, Ag, Au; 0.5-6.5 eV | 经典引用，同一方法三金属 | 仅 21 个离散数据点，图形为主 |
| **Palik, *Handbook of Optical Constants* (1985/1998)** | 几乎所有固体; UV-far IR | 综合手册，多源汇编 | 间接数据，不同来源拼接 |
| **Rakic et al. (1998)** | Al, Cu, Ag, Au, Pd, Pt, Ti, Ni, ...; 0.1-24 eV | 多洛伦兹-德鲁德模型拟合，平滑且参数化 | 模型近似，不是直接测量 |
| **Olmon et al. (2012)** | Au; 0.05-6 eV | 精确金椭球薄膜测量 | 只含金 |
| **McPeak et al. (2015)** | Ag; 0.1-6 eV | 精确银数据，含制备方法影响 | 只含银 |
| **Babar & Weaver (2015)** | Cu, Ag, Au, Al, Ni, Cr, ...; 0.1-6 eV | 多金属、近期系统测量 | 覆盖面广但各有精度 |
| **SOPRA n&amp;k 数据库** | 数百种材料; 193 nm - 25 μm | 光谱椭偏仪高精度 | 非开放数据库，需商业许可 |

### 在 mie-f 中的选择建议

- **Au, Ag**: JC 仍是标准参照，尤其是需要三金属同方法比较时。
- **Au (近期需要)**: Olmon 2012 或 Werner 2009。
- **Ag (近期需要)**: McPeak 2015 (标注："plasmonic quality" Ag)。
- **参数化形式**: Rakic 1998 提供 Lorenz-Drude 模型参数，可直接调用无需查表。
- **红外外推**: 使用 JC 提供的 Drude 参数 (\(m_0, \tau\)) + 已知 \(\omega_p\)。

---

## 附录: OCR 已知修正记录

本 OCR 版本 (`Johnson_Christy_1972.md`) 自原始 OCR 输出已应用以下修正。记录存于 `_pdf_review/manual_actions.md` 和 `manual_actions_final.md`:

| 日期 | 操作 | 来源 |
|------|------|------|
| 2026-07-26 | `CONTANTS` → `CONSTANTS` (标题) | `manual_actions.md:19-21` |
| 2026-07-26 | 作者行间距修复 | `manual_actions.md:25-27` |
| 2026-07-26 | `m 0` → `m_0` (Table II) | `FINAL_REVIEW_SUMMARY.md:150` |
| 2026-07-26 | `\epsilon_s` → `\epsilon_2` | `FINAL_REVIEW_SUMMARY.md:150` |
| 2026-07-26 | `\omega_{\rho}` → `\omega_p` | `FINAL_REVIEW_SUMMARY.md:150` |

> 如需严格引用数值数据，建议同时参考原始 PDF 中 Table I 的完整数值。
