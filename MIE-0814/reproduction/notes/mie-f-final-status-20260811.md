# mie-f 最终状态盘点（2026-08-11）

> 本文档是收尾快照，汇总整个 Alaee 2018 复现的诚实状态。所有数字均从源文件核实并标注
> 来源路径（见每项后的 `来源:`）。状态以冻结数据、当前 spec、审查收据和报告为准，不采信
> 转述。**总体结论（B14 全栈审查）：四轮工作流均有可审计产物、方法链强数值支持，但
> 不能无修饰称"复现完成"；Fig.3 非代理物理复现为 NOT_ACHIEVED。**
> 来源: `codex-prompts/out/B14-fullstack-review.md:5-6`

---

## 1. 四轮结果（result_class / gate 状态 / 关键数字）

### 第 1 轮：Fig.1 散射（介电球 ε_r=6.25，x=2a/λ∈[0.2,1.0]，200 点）

- **result_class**：`PASS_WITH_LIMITATIONS / metric_decision_pending`
  来源: `report-round1/sections/08_conclusion.tex`、`codex-prompts/out/B1-regate-verdict.md:5`
- **gate 状态**：gate①--③ 通过；历史 gate④（2026-08-09）`PASS_WITH_LIMITATIONS` 不可变收据
  存在；A1 发现矩/C 口径漂移后 B1 受控重开 metric 条款，**2026-08-11 已由 superseding receipt
  关闭**（见 §5 争议点）。canonical SEPR class 未签发。
  来源: `report-round1/GATE4-FIG1-CLOSURE-RECEIPT.md`、`report-round1/GATE4-FIG1-SUPERSEDING-RECEIPT-20260811.md`
- **关键数字**：
  - Table 2--Mie 200 点逐通道最大相对误差（masked, <1% 合同）：
    ED **0.140419%**、MD **0.038324%**、EQ **0.202006%**、MQ **0.125188%**
    来源: `report-final/sections/03_rounds.tex:20`、`report-round1/sections/01_overview.tex:21-25`
  - exact s=0.75 复矩向量口径（论文主 gate）：ED **136.1669%**、MD **277.7424%**、EQ 42.5195%、MQ 24.7950%
    来源: `codex-prompts/out/B1-regate-verdict.md`（精确直接计算）、`report-final/sections/03_rounds.tex:28-34`
  - exact s=0.75 C 分项诊断（不参与论文 gate）：ED 86.9148%、MD 215.9110%、EQ 103.0775%、MQ 55.7510%
    来源: `codex-prompts/out/B1-regate-verdict.md`
  - 已作废旧值：169.7%/167.7%/2275%/2453%
    来源: `report-round1/sections/08_conclusion.tex`（历史值作废标记）
- 3 层物理验证、W-sub 独立审查通过；blocker（表2 径向因子）已解。
  来源: `report-round1/sections/01_overview.tex`

### 第 2 轮：Fig.2 多极分解（介电球 a + 金球 b；金数据 3 源核对）

- **result_class**：`partial_physical_match`
  来源: `data/fig2_layer3_summary.json`、`report-round2/sections/08_conclusion.tex`
- **gate 状态**：gate①③ 跳过（记录原因，复用 Fig.1 参数/公式）；gate② 放行；
  **gate④ = `PASS_WITH_LIMITATIONS`**；promotion `DENIED`。
  来源: `report-round2/sections/02_workflow.tex`、`data/fig2_layer3_summary.json`
- **关键数字**：
  - Olmon-EV refined 200 点 Table 2--Mie max rel：ED **0.011856%**、MD **0.016992%**、
    EQ **0.016104%**、MQ **0.024139%**；p95 <0.024%；max abs <2.64e-4
    来源: `report-final/sections/03_rounds.tex:38`、`data/fig2_gold_olmon_refined_summary.json`
  - 网格收敛 (40,41,80)→(60,61,120) 最大变化：0.045213/0.064187/0.060844/0.090694%（<0.1%）
    来源: `data/fig2_gold_olmon_grid_convergence.json`、`report-final/sections/03_rounds.tex:38`
  - Layer3 PDF-vector strict gate（RMSE≤0.02/p95≤0.05/峰位差≤0.01）：
    介电 panel-a ED/MD/EQ `PASS_VECTOR_CONSISTENT`、**MQ `UNRESOLVED`**
    （RMSE 0.02556 / p95 0.05695 / 峰位差 2.089e-5）；金球 JC 有效域（x≥500/1935≈0.2584）四通道 PASS；
    完整金球面板 `MATERIAL_DOMAIN_LIMITED`。
    来源: `data/fig2_layer3_summary.json`、`notes/fig2-layer3-paper-comparison-review.md`
  - graphical floor（23 个 MQ marker）：论文 line-vs-marker RMSE/p95=0.024302/0.061866；
    本地-vs-论文 line=0.009327/0.021042 → `CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR`，不覆盖 strict gate
    来源: `report-final/sections/03_rounds.tex:47-49`
  - **B3 最新 fail-closed UQ**：`layer3_uq_status=UNRESOLVED`；panel (a)/(b) 八条正式 lane 全
    `UNRESOLVED`（dense 阈值 null、axis/interp 仅 proxy、缺独立 physics uncertainty）；
    promotion `DENIED`；`uq_model_validity=false`。
    来源: `data/fig2_uq_summary.json`、`codex-prompts/out/B3-promotion-verdict.md`、`notes/fig2-uq-promotion.md`
- 金材料 550 nm 三源核对：ε₁ 互差 11.35%、ε₂ 互差 25.75%（样品敏感性，非同一真值）；
  金数据 3 源（JC 1972 论文层 / Olmon-EV 2012 方法层 / McPeak 2015 敏感性层 + Rakic 参考）
  来源: `report-round2/sections/08_conclusion.tex`、`report-round2/sections/02_workflow.tex`

### 第 3 轮：Grahn 映射（2012 New J. Phys.）

- **result_class**：`PASS_WITH_NOTES / method_consistency`（ceiling = method_consistency，不宣称物理复现）
  来源: `data/grahn_gates.json`（tail：`overall_gate=PASS_WITH_NOTES`、`result_class=method_consistency`）、
  `report-round3/sections/08_conclusion.tex`
- **gate 状态**：gate① 跳过（复用参数）；gate② 放行（等效替代审查 #13 + A1/A2 独立复核）；
  gate③ 部分跳过；**gate④ 材料齐全，停在人 gate**（用户未关闭）。
  来源: `report-round3/sections/02_workflow.tex`、`codex-prompts/out/B6-report.md`
- **关键数字**：
  - Path A vs Table 1 总截面（x≤0.1，43/150 点）：max **5.705589e-7**，p95 4.493e-7
    来源: `sub-report/verify-grahn.md:7`、`report-round3/sections/05_numerical.tex:33-35`
  - Path B vs Mie 总截面（200 点 [0.02,1.0]）：max **2.935185e-4**，p95 1.322e-4
    来源: `sub-report/verify-grahn.md:8`、`report-round3/sections/05_numerical.tex:33-35`
  - 逐 m 复系数：1298/1470 行保留，max **1.517084e-3**，p95 3.185e-4
    来源: `sub-report/verify-grahn.md:9`
  - Rayleigh canonical slope = **6.098392**（目标 6±0.1）
    来源: `sub-report/verify-grahn.md:10`
  - Grahn Eq.(22) vs Eq.(20) 光学定理 relative = **5.963e-7**；6 解析 fixture max 1.185e-14；
    独立远场 max complex rel 7.744e-15；miepython rel 1.593e-15
    来源: `sub-report/verify-grahn.md`、`report-round3/sections/05_numerical.tex`
  - Path A EQ 逐通道 1.385% = 预注册 rank-4 截断诊断（披露，非总量 FAIL）
    来源: `codex-prompts/out/B6-report.md`、`report-round3/sections/08_conclusion.tex`
- 对抗审查链：09/10/11/12（前期 BLOCKED 全项接受，逐版修订到 v4）+ D1 #14 BLOCKED→#14b PASS
  来源: `report-round3/sections/02_workflow.tex`、`formalization/grahn.yaml`（历史注记）

### 第 4 轮：Fig.3（耦合金纳米盘，非代理目标）

- **result_class**：B7 = `surrogate_fallback`；B8 = `diagnostic_only`；**full Fig.3 = `NOT_ACHIEVED`**
  来源: `data/fig3_mie_surrogate_summary.json`（`result_class: surrogate_fallback`）、
  `codex-prompts/out/B8-report.md`（`result_class: diagnostic_only`）、`report-final/sections/03_rounds.tex:71-84`
- **gate 状态**：专属 FIG3-G0--G6——G0/G2/G3 `PENDING_HUMAN_APPROVAL`（可批），
  G1 `BLOCKED_BY_HOST_SPACER_AND_MATERIAL_GAP`，G4 `BLOCKED_NO_CONFIGURED_FIG3_PHYSICAL_SOLVE`，
  G5 `BLOCKED_BY_FIG3-G2_AND_FIG3-G4`，G6 `BLOCKED_BY_UPSTREAM_GATES`。
  来源: `formalization/alaee2018-fig3.yaml:366-395`、`notes/fig3-spec-promotion.md`
- **关键数字（surrogate/诊断，全部可复算）**：
  - 301 请求点，297 有材料覆盖（4 uncovered）
    来源: `data/fig3_mie_surrogate_summary.json`（`n_points=301, covered_points=297`）
  - 方向交叉项：min **-24.9256**（x=0.82）到 max **+4.48683**（x=0.5275）
    来源: `report-final/sections/03_rounds.tex:82`、`data/fig3_mie_surrogate_summary.json`
  - Tribelsky comparator（q=-1, x0=1.34, Γ=0.04）：峰/谷 **1.32002/1.35998**（vs 1.32/1.36，位置差 2e-5）
    来源: `report-final/sections/03_rounds.tex:82`、`data/fig3_mie_surrogate_summary.json`
  - Fu 2013 sanity：F/B=11.0443（文献约 8，偏高 38.05%，仅 `sanity_only`）
    来源: `report-final/sections/03_rounds.tex:82`
  - COMSOL：generic runtime smoke PASS（Job a624ec1976397ee9，COMSOL 6.3.0.290）；
    Fig.3 skeleton 因 FileSecret staging 前置失败未 compile；无配置好的 physical solve、
    无功率闭环、无 Mie--COMSOL crosspath
    来源: `codex-prompts/out/B8-report.md`
- Fig.3 不是"Fano 谱图"：主 observable 是双盘 ED/MD/EQ/MQ 的 Table 1/Table 2 分通道
  C_sca 及相对误差；Fano 默认关闭、不 gate。
  来源: `codex-prompts/out/B11-report.md`、`codex-prompts/out/B12-review-fig3-defaults.md`

---

## 2. CODEX 任务全清单（A1--A6、B1--B15）

### A 任务（6/6 完成，主 agent 验收通过）
来源: `mie-f-completion/OVERVIEW.md:8-15`

| 任务 | 做什么 | 结果 |
|---|---|---|
| **A1** | 前两轮（Fig.1+Fig.2）独立审计 | `result_class: completed`；Fig.1 矩/C 口径漂移需重 gate；Fig.2 方法 gate 维持 PASS；重算 67 passed/1 skipped → `codex-prompts/out/A1-audit-r1r2.md` |
| **A2** | 第 3 轮（Grahn）v4 独立复核 | `PASS_WITH_NOTES / method_consistency`（高）；定向 38 passed、规范 105 passed/1 skipped → `A2-independent-review-v4.md` |
| **A3** | Magnus/COMSOL 平台探索 | `diagnostic_only`；平台只读控制面可用；GUI 模板是唯一硬前置 → `A3-magnus-comsol-report.md` |
| **A4** | Fig.3 规划草案 | fig3.yaml 草案 + repro-plan-round4.md → `A4-notes/` |
| **A5** | Fig.2 MQ 根因 + UQ 预注册 | MQ 差异 90.67% 平方误差集中在两峰区；多因素不可唯一归因；A5-v2 预注册 spec supersede 旧 UQ → `A5-mq-rootcause.md`、`A5-recompute/preregister/` |
| **A6** | Fig.3 / Fano / 多极干涉文献 | 587 行 + 23 BibTeX；确认 Fig.3 非 Fano 谱图 → `A6-fig3-fano-literature.md` |

### B 任务（全部完成；B9 人工项以 B9s 研究绕过）
来源: `codex-prompts/out/*-report.md`（逐文件）、`mie-f-completion/OVERVIEW.md:19-37`

| 任务 | 做什么 | 结果 |
|---|---|---|
| **B1** | Fig.1 范围受控重 gate（双口径裁决材料） | `PASS_WITH_LIMITATIONS / metric_decision_pending`；复矩 ED/MD >100% 成立 → `B1-regate-verdict.md` |
| **B2** | 光学定理 S(0) 独立实现 | `PASS_WITH_NOTES`；双路差 1.2e-14，18 passed → `B2-report.md` |
| **B3** | Fig.2 UQ 晋级轮 | `promotion: DENIED`；`partial_physical_match`；8/8 lane UNRESOLVED → `B3-promotion-verdict.md` |
| **B4** | 源文件勘误 9 处 + 重编译 | 6 个源文件落地；讲义 83 页 PDF 编译通过 → `B4-errata-report.md` |
| **B5** | round2 报告修复（3 处 🟡） | 修复；`partial_physical_match` 维持；round2 重编译 17 页 → `B5-report.md` |
| **B6** | 第 3 轮报告（Grahn） | `overall_gate=PASS_WITH_NOTES`、`method_consistency`；gate④ 材料齐全待用户 → `B6-report.md` |
| **B7** | Fig.3 Mie 代理路径 | `surrogate_fallback`；297/301、Tribelsky 峰谷 1.32002/1.35998 → `B7-report.md` |
| **B8** | Fig.3 COMSOL Java 骨架 + Magnus smoke | `diagnostic_only`；runtime probe PASS、skeleton staging FAIL、物理 solve 未跑 → `B8-report.md` |
| **B9** | （人工项）COMSOL 6.3 GUI 模板 | 由 **B9s**（COMSOL 6.3 Java API 深搜报告）研究性绕过；GUI 模板仍是 Fig.3 COMSOL 真路径唯一人工硬前置 → `B9s-comsol-java-docs.md`、`B9s.log` |
| **B10** | 四轮最终总报告 | `PASS_WITH_NOTES`；report-final 编译 18 页；61 项数字台账 → `B10-report.md`、`B10-audit-numbers.md`、`B10-audit-gates.md` |
| **B11** | Fig.3 spec 晋升修订待批稿 | `draft_pending_human_approval`；full NOT_ACHIEVED；SEPR-9 修订候选 → `B11-report.md`、`B11-fig3-spec-revised.yaml` |
| **B12** | 对抗审查 B11 八项默认 | 8 项批准/调整/拒绝 + 第 9 项 Eq.(1) 版本冻结；G0--G6 状态厘清 → `B12-review-fig3-defaults.md` |
| **B13** | 对抗审查 Fig.1 metric 裁决 | **复矩向量/张量口径为论文主 gate**；ED/MD s=0.75 单点 PASS → `B13-review-fig1-metric.md` |
| **B14** | 全栈最终审查（4 轮验收） | **BLOCKED 总裁决**（5🔴+8🟡 全闭环）；现场重算逐位一致；根 pytest 126 通过由 B15 落地 → `B14-fullstack-review.md` |
| **B15** | 修复 B14 可修项 | 🔴1 YAML / 🔴3 fig3 状态 / 🔴4 pytest.ini / 🟡1-10 全部落地；**126 passed, 1 skipped** → `B15-fix-report.md` |

---

## 3. 最终产物清单

### formalization/（4 份 spec）
| 文件 | 顶层字段数 | 状态 |
|---|---|---|
| `formalization/alaee2018-fig1.yaml` | 13 | 状态行仍写 "draft—待 gate②"；B15 修复 YAML 可解析；含 B1 复矩口径（L165-176） |
| `formalization/alaee2018-fig2.yaml` | 12 | 状态 "gate④ PASS_WITH_LIMITATIONS — partial_physical_match" |
| `formalization/grahn.yaml` | 12 | v4；"当前实现已完成；38 passed / 105 passed,1 skipped"；ceiling=method_consistency |
| `formalization/alaee2018-fig3.yaml` | 9（唯一 exact SEPR-9） | "APPROVED_AS_PATH_CANDIDATE"（B15 修正）；正文 draft_pending_human_approval；G0--G6 pending/blocked |

来源: `formalization/*.yaml`（head）、`codex-prompts/out/B14-fullstack-review.md:21-25`、`B15-fix-report.md:5-10`
注意：SEPR-9 是语义集合（Fig.1/2/Grahn 历史 13/12/12 区段下的语义 9 字段，仅 Fig.3 exact-9）
来源: `notes/sepr-schema-contract.md`

### 报告（LaTeX 工程 + PDF）
| 报告 | 路径 | PDF |
|---|---|---|
| 第 1 轮 | `report-round1/` | `main_aux/main.pdf`（23 页） |
| 第 2 轮 | `report-round2/` | `main_aux/main.pdf`（17 页） |
| 第 3 轮 | `report-round3/` | `main_aux/main.pdf`（12-13 页） |
| 最终总报告 | `report-final/` | `main_aux/main.pdf`（18 页，SHA-256 6CACF624... 由 B10 记录） |

来源: `report-round{1,2,3}/main_aux/main.pdf`、`report-final/main_aux/main.pdf`、
`codex-prompts/out/B10-report.md:317-326`、`B15-fix-report.md:436`
另含：`sub-report/a2-*`（spec 契约/归一化/核心审计）、`sub-report/verify-grahn.md`（第 3 轮验证）、
`sub-report/explore-comsol-magnus.md`。

### 测试
- **tests/ 限定树：126 passed, 1 skipped**（pytest.ini 指定 `testpaths=tests`，排除 `codex-prompts/out`）
  来源: `codex-prompts/out/B15-fix-report.md:434-435`、`pytest.ini`
- 唯一 skip = 默认不跑的 Fig.1 200 点慢扫描（`tests/test_multipole.py:213-227`）
  来源: `codex-prompts/out/B14-fullstack-review.md:80`
- 历史里程碑：67（A1 期）→ 105（A2 v4 期）→ 123（B2/B5 期）→ 126（B15 期）
  来源: `A1-audit-r1r2.md`、`A2-independent-review-v4.md`、`B5-report.md`、`B15-fix-report.md`
- 注意：repo-root 裸 `pytest .` 仍会收集 `codex-prompts/out/A3-file-secret-hardening/tests/`
  并因 `case_importer` 导入失败（collection error）；这是审查产物夹具，非项目测试失败
  来源: `codex-prompts/out/B14-fullstack-review.md:88`

---

## 4. 剩余人工项（CODEX 不可代）

| 项 | 状态 | 说明 |
|---|---|---|
| **Grahn gate④ 关闭** | 待用户 | 机器材料齐全（逐路径/逐通道/逐 m/mask/错误注入），用户接受 notes 与 method_consistency ceiling 后关闭 → `report-round3/sections/08_conclusion.tex` |
| **Fig.3 G0--G6** | G0/G2/G3 可批；G1/G4/G5/G6 blocked | 需人工冻结输入（host/spacer/JC 缺口/panel-b metric/Eq.(1) 版本）+ COMSOL 6.3 GUI 模板 + 真实频域散射求解 → `formalization/alaee2018-fig3.yaml:366-395`、`notes/fig3-spec-promotion.md` |
| **Fig.2 B3 UQ 晋级** | DENIED（人工裁决） | 8/8 lane fail-closed；需预注册 uncertainty-aware dense/physics UQ 后重新过 gate 4 → `codex-prompts/out/B3-promotion-verdict.md` |
| **Fig.1 canonical class** | 治理层 | 方法/单点声明 PASS 已有证据；如需 unrestricted physical success 需预注册全域 paper-vector 目标（B13 只关单点条款）→ `report-final/sections/08_promotion_conclusion.tex:12` |

---

## 5. 争议点与已修复项（诚实声明）

### 5.1 B14 🔴 五项 → 现状
| # | B14 发现 | 现状 |
|---|---|---|
| 1 | Fig.1 spec 非法 YAML（L26 多余 `}`） | **已修复**（B15 删除；四 spec yaml.safe_load 全过）→ `B15-fix-report.md:5` |
| 2 | Fig.1 gate④ 收据链错位、post-B1 未重签 | **已补 superseding receipt** `GATE4-FIG1-SUPERSEDING-RECEIPT-20260811.md`（2026-08-11 11:39，用户"自行决定"授权依据 B13 采纳复矩口径）；但 report-final 各 section（01/03/06/08）仍写"缺 post-B1 人工 superseding receipt"——**报告正文与收据目录不同步**，需主 agent 在 report-final 补一句引用 → `report-final/sections/06_gates.tex:17` |
| 3 | Fig.3 晋升状态自相矛盾 | **已修复**（header→`APPROVED_AS_PATH_CANDIDATE`，note 同步；正文 draft + G0--G6 pending/blocked 保留）→ `B15-fix-report.md:6` |
| 4 | 根 pytest 非绿 | **已修复**（pytest.ini 限定 tests/，126 passed/1 skipped）→ `B15-fix-report.md:8` |
| 5 | Gate 全流程未关闭 | **部分**：Fig.1 单点条款已重签；Grahn gate④、Fig.3 G0--G6 仍待用户（§4） |

### 5.2 B14 🟡（B15 已落地的 8 项）
SEPR schema 合同（`notes/sepr-schema-contract.md`）、Fig.3 注记同步（201→401/峰位/B9s）、
Grahn 陈旧状态、B3 UQ 八 lane 披露、round2 tab+exttt、Fig.3/UQ 测试回归 + pytest.ini、
bib metadata（Grahn 标题/McPeak/Bohren--Huffman 年份）、WORK_LOG 最终阶段索引
→ `B15-fix-report.md:5-10`

### 5.3 已确认 NOT_ACHIEVED / 不可声称
- **Fig.3 完整物理复现**：无配置完成的 COMSOL 频域散射 solve、无功率闭环、无 Mie--COMSOL crosspath
  → `report-final/sections/03_rounds.tex:82-84`、`07_limitations.tex`
- **Fig.2 完整面板**：介电 MQ strict fidelity UNRESOLVED + 金球 JC 域外缺口（MATERIAL_DOMAIN_LIMITED）
- **Fig.2 正式 UQ 晋级**：8/8 lane UNRESOLVED，promotion DENIED
- **repo-root 裸 pytest 全绿**：仍因审查夹具 collection error
- **期刊终版 Eq.(1) glyph**：当前以 hash-bound arXiv-v2 为 implementation authority，journal-final 未核

### 5.4 已确认完成 / 可声称
- Table 2--Mie 球体方法合同（Fig.1/Fig.2 双轮，逐通道 <1%）
- Fig.1 exact s=0.75 复矩 ED/MD >100% 单点论文声明（B13 强审 + superseding receipt）
- Fig.2 金球 JC 有效域四通道 paper-vector + 介电 ED/MD/EQ（graphical floor 一致）
- Grahn 双路径/逐 m/解析 fixture/光学定理/独立远场映射（method_consistency）
- Fig.3 surrogate + 方向干涉 + Tribelsky strict-feature/Fu sanity（可复算，不提升 class）
- 126 passed/1 skipped 测试树、四轮 LaTeX 报告 + 最终总报告

---

## 6. 总评（B14 最终裁决原文要义）

> 当前不能称"mie-f 复现完成"。可以称"mie-f 四轮工作流已有可审计产物，方法链验证完成，
> 结果按轮分级；Fig.1/Grahn 仍有治理 gate，Fig.3 非代理物理复现未完成"。只有消除上述
> 🔴 项、补齐人工 gate 收据并让标准测试入口通过后，才可重新申请"全流程完成"验收。
来源: `codex-prompts/out/B14-fullstack-review.md:176`

*本文档为收尾快照（2026-08-11），只读梳理，不修改任何冻结数据/代码/报告。*
