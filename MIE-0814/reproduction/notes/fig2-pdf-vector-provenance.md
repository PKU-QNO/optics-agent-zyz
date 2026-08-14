# Fig.2 Layer3 论文 vector 曲线：PDF 来源与可重建性说明

> 目的：落实 B14 全栈审查 ⚪2 建议（`codex-prompts/out/B14-fullstack-review.md:165`）——
> Fig.2 Layer3 论文对比用到的论文 PDF 原路径在 reproduction 根之外，需补充 checkout 内
> 可移植的来源或重建说明。本文档是 notes（只读梳理），不改动任何冻结数据/代码。

## 0. 一句话结论

Fig.2 的论文曲线不是"读图/描点"，而是从论文 PDF **第 4 页的矢量路径（vector path）** 用
PyMuPDF 直接提取的。提取结果已冻结为 `data/fig2_paper_vector_curves.csv` +
`data/fig2_paper_vector_metadata.json`（含源文件 SHA-256），因此 checkout 内可复算
"CSV → 指标"，但不能单独重建"PDF → CSV"——原始 PDF 位于 reproduction 根之外（见 §1）。

## 1. 论文 PDF 的原始位置与可用副本

### 1.1 原始位置（reproduction 根之外）

源 PDF 唯一现存位置（`find` 全桌面确认无第二份副本）：

```
C:/Users/27370/Desktop/project/optics_agent/papers/mie-f/01-主论文/Alaee_2018_An_Electromagnetic_Multipole_Expansion_Beyond_the_Long-Wavelength_Approximation.pdf
```

- 文件名（Alaee 2018, Optics Communications 407, 17–21, DOI 10.1016/j.optcom.2017.08.064）
- 大小 709,862 bytes；**SHA-256 = `c79e243e9b0d05e2800223dea8552df03bbbf0318c134839e9e7ebcc8dda973e`**
  （2026-08-11 现场重算与原 metadata 逐位一致）
- 该路径写死在三处：
  - `data/fig2_paper_vector_metadata.json` → `source_pdf`
  - `code/extract_fig2_vector.py:72-81` → `find_source_pdf()` 的候选根
    `Path("C:/Users/27370/Desktop/project/optics_agent/papers/mie-f")`
    （另有 `ROOT.parent.parent.parent / "optics_agent" / "papers" / "mie-f"` 相对兜底，
    以及环境变量 `ALAEE_FIG2_PDF` 覆盖）
  - `report-final/sections/05_cross_validation.tex:41-43`（B14 引用的诚实披露）
- 同一目录 `01-主论文/Alaee_2018.ocr/` 下还有分页 OCR 图片（仅用于文字层，不作 vector 数据源）。

### 1.2 reproduction 根内的可用"副本"（已冻结的提取产物，非 PDF 本体）

| 文件 | 内容 | 角色 |
|---|---|---|
| `data/fig2_paper_vector_curves.csv` | 1578 行曲线点（panel/multipole/curve/x_alaee/y_norm/source/page） | **冻结的论文曲线数据**，比较脚本唯一读取源 |
| `data/fig2_paper_vector_metadata.json` | mode=vector、源 SHA-256、轴拟合、每通道 line/marker 计数、palette | 提取过程收据 |
| `data/fig2_layer3_summary.json` | 最终对比指标（strict vector gate、逐通道 RMSE/p95/峰位差、graphical floor、coverage、result_class） | Layer3 裁决结果 |
| `figs/fig2_layer3_overlay.png`（= `report-round2/figures/fig2_layer3_overlay.png`，同文件） | 论文 vector 虚线 vs 本地 Mie 实线叠加图 | 视觉对照 |

PDF 本体未纳入 checkout（不在 reproduction/ 内）。如需 checkout 自包含，两种重建路径见 §4。

## 2. 提取方法（PyMuPDF 矢量提取，非 vision-mcp，非人工描点）

- **实现**：`code/extract_fig2_vector.py`（333 行，`extract_vector()`，主入口 `main()`）。
- **动机**（`notes/fig2-layer3-paper-comparison-review.md` §审查结论）：原拟"高 DPI 渲染 +
  vision-mcp 描点"，但源 PDF 第 4 页实测含 ~840 个 drawing object，Fig.2 四色 Mie polyline 与
  exact 圆形 marker 均保留为 **vector path**。因此 vision/raster 降级为
  `DESCRIPTIVE_ONLY` fallback，vector 路径是**唯一主证据**。
- **步骤**：
  1. `fitz.open(source)`，取 `page_number = 4`（物理页 4；metadata 记录 page_count=5）。
  2. 每个 panel 用 PDF 绘图对象拟合坐标变换：x 轴取 5 个竖直短 tick（数据值 0.2/0.4/0.6/0.8/1.0），
     y 轴取 4 个水平短 tick（数据值 7/5/3/1）。tick 位置从路径本身重发现、与预登记 frame 坐标
     `PANELS` 校验，残差 gate <0.5 PDF pt。
  3. 按 PDF 颜色精确匹配（`_close_color`，RGB 容差 2e-4）区分四通道：
     ED=橙(0.847,0.322,0.094)、MD=蓝(0.0,0.443,0.737)、EQ=黄(0.925,0.690,0.122)、MQ=紫(0.490,0.180,0.553)。
  4. 同一颜色的 drawing 里，`l` polyline（≥20 items）→ `curve=mie`；`c` Bezier（4 items）→
     `curve=exact`（圆形 marker 中心）。每点标记 `source`（PDF 绝对路径）与 `page`。
  5. 用轴拟合把 PDF page 坐标映射到数据坐标 `(x_alaee, y_norm)`。
- **提取收据**（metadata `panels.*`）：panel (a) x/y 拟合残差 0.000443/0.006570（数据单位）、
  0.0678/0.0532 PDF pt；panel (b) 0.000446/0.006373、0.0683/0.0516 PDF pt——均远低于 0.5 pt gate。
  每通道 line/marker 计数见 metadata `counts`（如 panel-a ED: 3 line drawings / 333 点、26 markers）。
- **为何不用 vision-mcp 当主证据**：vision/人工描点误差（~像素级）大于 vector 精确路径；且
  论文字体是 outlined（无文本层），只有路径可靠。raster fallback `extract_raster_fallback()`
  存在但明确 `confidence=descriptive_only`、不分离 solid/marker，不能产出 vector PASS。

## 3. 对齐方式（与本地曲线怎么比）

`code/compare_fig2_paper.py`（548 行，`compare_all()`）把论文 vector 曲线与本地解析 Mie 曲线对齐比较：

- **本地曲线**：panel (a) 介电球 `mie_multipoles(π·x, 2.5)` 在 x∈[0.2,1.0] 取 4000 点；
  panel (b) 金球 `mie_multipoles(π·x, interpolate_gold_m("jc", 500/x))` 在
  x∈[500/1935, 1.0]（JC 有效域起点，`JC_MIN_X≈0.2584`）。
- **对齐方式**：取论文与本地共同 x 域 `[max(domain0, min_x), min(domain1, max_x)]`，把本地曲线
  `np.interp` 到论文点，逐点误差。同 x 重复 PDF 点用 median y 合并（`load_paper_curves`）。
- **预注册 strict gate**：RMSE ≤0.02、p95 absolute error ≤0.05、峰位差 ≤0.01
  （`VECTOR_THRESHOLDS`）。`classify_metrics` 全过 → `PASS_VECTOR_CONSISTENT`。
- **辅助诊断**（不覆盖 strict gate）：
  - `graphical_floor_metrics`：在论文 exact marker 同一 x 支撑上比较"论文 line vs 论文 marker"
    与"本地 Mie vs 论文 line"，给出 graphical floor 判定；
  - `compare_q_factor`：FWHM→Q 因子（supplemental_only）；
  - `derive_panel_coverage`：由本地曲线实际 x 支撑推出 `PASS`/`MATERIAL_DOMAIN_LIMITED`/`UNRESOLVED`。
- **最终状态推导**（`derive_final_statuses`）：方法 gate（refined 方法 summary）+ strict gate +
  coverage 三合一 → `gate4_decision`/`result_class`。
- **结果**（`data/fig2_layer3_summary.json` + `notes/fig2-layer3-paper-comparison-review.md`）：
  - strict_vector_fidelity_status = `UNRESOLVED`；paper_fidelity_status = `UNRESOLVED`
  - coverage_status = `MATERIAL_DOMAIN_LIMITED`（JC 只到 ~1935 nm，x<0.2584 缺域不外推）
  - gate4_decision = `PASS_WITH_LIMITATIONS`；result_class = `partial_physical_match`
  - 逐通道：panel (a) 介电 ED/MD/EQ `PASS_VECTOR_CONSISTENT`，**MQ `UNRESOLVED`**
    （RMSE 0.02556 / p95 0.05695 超阈值；峰位差 2.09e-5 却几乎为零——差异集中在高曲率峰区）；
    panel (b) 金球 JC 有效域内四通道 `PASS_VECTOR_CONSISTENT`。

## 4. 从零重建步骤（checkout 自包含路径）

若第三方 checkout 无根外原 PDF，两种重建方式：

**方式 A（推荐，需原始 PDF）**：把原 PDF 放入 checkout（建议 `data/_gold_sources/Alaee_2018...pdf`
或 `figs/src/`），再跑：

```powershell
$env:ALAEE_FIG2_PDF = "path\to\Alaee_2018....pdf"   # 或修改 extract_fig2_vector.py 的候选根
python code/extract_fig2_vector.py --pdf "path\to\Alaee_2018....pdf" --page 4 `
  --csv data/fig2_paper_vector_curves.csv --metadata data/fig2_paper_vector_metadata.json
python code/compare_fig2_paper.py
```

重建后必须核对 `metadata.source_sha256` 与
`c79e243e9b0d05e2800223dea8552df03bbbf0318c134839e9e7ebcc8dda973e` 一致，且
`fig2_paper_vector_metadata.json` 的 counts/残差与 §2 收据一致，才能复现冻结 CSV。

**方式 B（无 PDF，只复算指标）**：直接用冻结的 `data/fig2_paper_vector_curves.csv` +
`data/fig2_paper_vector_metadata.json` 跑 `compare_fig2_paper.py`（比较脚本只读这两个文件），
可完整复算全部 Layer3 指标与 result_class。这是当前 checkout 能独立完成的极限——它验证
"vector CSV → metric"，不验证"PDF → vector CSV"。

**注意**：`find_source_pdf()` 默认会先找 `C:/Users/27370/Desktop/project/optics_agent/papers/mie-f`；
若该根目录不在第三方机器，必须显式传 `--pdf` 或设 `ALAEE_FIG2_PDF`，否则抛
`FileNotFoundError("Alaee 2018 source PDF not found")`。

## 5. 已知局限（读图/提取误差声明）

1. **高曲率区残差**：panel (a) 介电 MQ strict RMSE/p95 超预注册阈值（0.02556/0.05695 vs
   0.02/0.05），峰位差极小。归因纪律（`fig2-layer3-paper-comparison-review.md` §D）：
   只写"差异集中在高曲率区，可能包含绘图、坐标标定或原始数值采样效应"，**不声称单一根因**。
   旧"最大 polyline gap=0.23026 导致削峰"的说法已被 Opus #08 推翻（该 gap 位于断段
   x=0.13945→0.36971，不在峰区；峰区最大 gap 仅 0.00225/0.00879）。
2. **exact marker 过疏**：exact marker 典型 x 间距 ~0.0296 > 峰位 gate 0.01，因此所有通道
   `peak_verdict=DESCRIPTIVE_ONLY`——marker 只能验证形状/点值，不能独立裁决峰位。
3. **论文内部 graphical floor**：论文 Mie line vs exact marker 在同一 23（MQ）个支撑上
   RMSE/p95 已达 0.02430/0.06187，本地 Mie vs 论文 line 仅 0.00933/0.02104。诊断支持
   `CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR`，但**不追溯性覆盖预注册 strict gate**。
4. **材料域缺口**：JC 数据只覆盖到 ~1935 nm（x≥500/1935≈0.2584）；金球面板
   x∈[0.2,0.2584) 不外推、不拼 Olmon（明确禁止 Olmon 静默补齐），故完整面板为
   `MATERIAL_DOMAIN_LIMITED`。
5. **字体/文本层**：论文使用 outlined 字体（无文本层），轴标签只能靠 tick 路径识别；
   本提取不依赖文字 OCR，因此也不受 OCR 误差影响。
6. **raster fallback 不作数**：任何像素级提取（`extract_raster_fallback`/vision）都只能是
   `DESCRIPTIVE_ONLY`，不能产生 vector PASS。

## 6. 相关文件索引

- 提取代码：`code/extract_fig2_vector.py`
- 比较代码：`code/compare_fig2_paper.py`
- 冻结数据：`data/fig2_paper_vector_curves.csv`、`data/fig2_paper_vector_metadata.json`、`data/fig2_layer3_summary.json`
- 叠加图：`figs/fig2_layer3_overlay.png`
- 审查/执行说明：`notes/fig2-layer3-paper-comparison-review.md`
- UQ 晋级（B3）：`notes/fig2-uq-promotion.md`、`data/fig2_uq_summary.json`、`codex-prompts/out/B3-promotion-verdict.md`
- 总报告披露：`report-final/sections/05_cross_validation.tex:41-43`
- B14 ⚪2 建议出处：`codex-prompts/out/B14-fullstack-review.md:165`

*本文档仅记录来源与重建方式，未修改任何冻结数据、代码或报告。*
