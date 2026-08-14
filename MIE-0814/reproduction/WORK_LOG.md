# mie-f 数值复现 WORK_LOG

> 全局执行日志，追加式永不删减。新上下文先读本文件恢复全局框架。
> 详细逐日记录见 `worklog/00-index.md`。

## 2026-08-03 | 计划落盘

- **产出**：`repro-plan-v2.md`（权威路线图，7 步 workflow + 4 gate + 3 层验证）
- **目录骨架**：`formalization/ notes/ code/ tests/ verifiers/ data/ figs/ worklog/ sub-report/` 已建
- **材料数据确认**：Johnson & Christy 1972 已在本地 Zotero（`WAEZQ8P3`），**无需下载**，只需从 PDF 提取表 → `data/jc_Au.csv`
- **与旧文档关系**：旧的 `repro-plan.tex`（7-27 精读版）是理论精读路线图，本计划 v2 是**数值执行版**，两者互补
- **下一步**：step01 PDF 预读 → gate① 参数确认（等用户启动数值阶段）

## 2026-08-03 | 设计修正（grill-me 共识）

- **workflow 改为按图多轮循环**：Fig.1 → Fig.2 → Grahn 映射 → Fig.3(延后)，每图独立走 7 步，轮间共享 code/、经验沉淀 worklog/
- **新增 baseline_mie.py**：独立 Mie 基准先跑通 Layer1，防"自己验证自己"
- **执行方式拍板**：多模态→codex；普通写码→Claude 内置子 agent；高能力计划/验证/对抗审查→用户开 claude-opus 独立对话（Claude 落盘 prompt + 给路径）；判断/归因/gate→Claude 主循环
- **prompt 按需写**：不预写，到时机针对性写一条落盘 opus-prompts/ 给路径
- **共识决策**：Fig.3 延后；验收=量化对齐论文图（RMSE/峰位）；主线完整含 Grahn 映射验证

## 2026-08-03 | 计算平台策略

- **COMSOL = 备选项**：链路可行性探索中（子 agent 后台跑，结论落 `sub-report/explore-comsol-magnus.md`），落盘即备查不阻塞主线
- **Gustation/Magnus = 远程云计算平台**：大计算量 Python 丢上去跑（用户拍板），避免本地硬扛
- 主线 Fig.1/2 先本地，跑不动切 Gustation
- 已在 repro-plan-v2.md 加 §2.6 计算平台策略

## 2026-08-04 | opus 对抗性审查 #01 + 修复

- opus 审查报告：`opus-prompts/01-plan-adversarial-review-RESULT.md`（含 2 🔴 + 10 🟡 + 4 🟢）
- 主 agent 核实后全盘接受，triage 见 `opus-prompts/01-review-triaged.md`
- **已修（计划 + 讲义）**：
  - R1：介电球 ε_r 2.52 → **6.25**（=2.5²，n=2.5）——原文是 2.5²，PDF 提取丢上标。计划/formalization/检查单全改
  - R2：Grahn 轮 Q 区分电流矩 M² 与对称 Q^e（讲义 §8 有警告，计划 §6.5 漏）
  - Y1：讲义 §12 量纲 typo `|m|²/c`→`|m|²/c²`（原文印错，讲义照抄），Eq.1 四极系数 k²/30→k²/120
  - Y2-Y10 + G1-G4 全部标注进计划 §6.7（m=±1、m求和、ε=host、per-multipole提前、暗模式构造、光学定理独立、c_n/d_n、Fig.2容忍<1%）
- **讲义 bug 发现并修复**：§12 Alaee Eq.1 磁偶极/磁四极量纲（讲义早期照抄原文 typo）
- 讲义重新编译通过

## 2026-08-04 | step01 执行（opus 审批修订版）

- **opus 审批**（`02-fig1-step01-execution-review.md`）：3 陷阱（y 轴 log/8条同色曲线分不开/叠加依赖轴精确）+ 2 残留（wavelength→size_param、金球不阻塞）
- **用户拍板**：跳过 --agent 机制（删了 3 个 agent toml，改 codex exec -c 内联）；验收基准=自洽验证为主（表1/表2/Mie 三曲线自洽 <0.1% + 目视叠加）；坐标轴两阶段法
- **路线 A（像素定轴）**：`code/pixel_axis_detect.py` 修好 bug，Fig.1 四子图 a/b/c/d 坐标轴定位成功（±1px），产物 `data/alaee_fig1_axes.yaml` + `notes/fig-axes.md`。子 agent 正在补 x_scale/y_scale/confidence + 刻度值
- **路线 B（文本参数）**：`notes/fig1-parameters.md` 完成。关键发现：
  - ε_r=6.25 确认；x=2a/λ ∈ [0,2.0]（fig1.png 实测刻度 0,0.5,1.0,1.5,2.0）
  - **OCR 表1 严重误读**：ED/EQ 前置系数被 OCR 读成 -1/10，PDF 文字层确认是 **-1/(iω)**（iω 被识别成 10）。复现必须用 -1/(iω)
  - Eq.1 磁偶极项量纲 typo（|m|²/c → 应为 |m|²/c²），四极系数 1/120 确认
  - J_S 符号约定：Alaee +iω（e^{+iωt}）vs 讲义/Grahn −iω（e^{−iωt}），复现统一 e^{−iωt} → J=−iωε₀(ε_r−1)E
  - Table 1 四条公式与讲义 §10 完全一致
- fig1.yaml：range 修正 0-2.0，wavelength→size_param 完成

## 2026-08-04 | step01 完成（双路线）

- **路线 A（像素定轴）完成**：`pixel_axis_detect.py` 补全 3 字段 + tick 间距分析。Fig.1 四面板：a/b y=log（C_sca 跨量级）、c/d y=linear（误差%），x 全 linear，confidence 全 high。判 log 依据：高分辨率 fig1.png 字形（10/5/2 十进位尾数）+ 刻度间距不等 + 量纲跨 10⁻⁴~10²。产物 `data/alaee_fig1_axes.yaml` + `fig-axes.md`
- **路线 B（文本参数）完成**：`fig1-parameters.md`。OCR 表1 前置系数误读 -1/10→实为 -1/(iω)；J_S 符号约定 e^{−iωt}→J=−iωε₀(ε_r−1)E；Table1 与讲义 §10 完全一致
- **opus 审查 prompt** `02-param-formalization-review.md` 已落盘（gate① 前）
- **gate① 待用户确认**：ε_r=6.25、x 范围 [0,2.0]、y=log、表1 公式

## 2026-08-04 | gate① opus 审查 + 权威图核实（重要轴修正）

- **opus 审查**（gate① 对抗）判定 1 硬错 + 1 待澄清：y 轴说 linear[0,7]（疑 log）、x 轴端点待查
- **主 agent 亲眼看权威图** `figs/fig1.png`（2481×1488，像素统计定位面板(a) x 轴 row 506 + 放大裁剪）：
  - **y 轴 = log**（10⁻²~10²）——**opus 的 linear 修正错**（opus 自认陷阱1 是猜的）【❌ 本行判定 2026-08-05 被推翻，见下】
  - **x 轴 = 0.2 → 0.8**（刻度 0.2,0.4,0.6,0.8）——**原报告 0→2.0 错**（低分辨率 OCR 渲染 jpg 误读刻度）
- **教训（重要）**：低分辨率 OCR 渲染读刻度不可靠（745×302），必须用权威图 figs/fig1.png（2481×1488）。此前 pixel_axis_detect 读低清图 + 我收敛指令判 log 都基于不完整信息
- **修正**：fig1.yaml size_param.range [0.2,0.8]；fig1-parameters.md 参数表 x 范围 0.2-0.8（4 处）；axes yaml tick_label_hint 同步
- **物理自洽**：x∈[0.2,0.8] 含 0.75（论文声称误差>100% 点）✅
- gate① 重新待用户确认

## 2026-08-05 | y 轴判定大翻案：全部 linear（vision-mcp 核实）

- **用户指出**：原图四张，y 轴不是 log。左侧两图刻度 **1,3,5,7**（C_sca/(λ²/2π) 归一化），右侧两图 **0,25,50,75,100**（Percentage of relative error）。错误根源 = 竖排轴标题与刻度竖写混读。
- **vision-mcp 多通道核实**（4 通道收敛）：
  - 面板(a)/(b) y 轴 = **linear，1, 3, 5, 7**（= (2j+1) 普适上限：j=0→1, j=1→3, j=2→5, j=3→7，归一化 C_sca/(λ²/2π) 的 linear 轴取此刻度完全自洽）
  - 面板(c)/(d) y 轴 = **linear，0, 25, 50, 75, 100（%）**
  - 布局 = **左列 (a)(b) 截面、右列 (c)(d) 误差**（非早期 yaml 的上排/下排）
  - x 轴 = **0.2, 0.4, 0.6, 0.8, 1.0**（数据范围 [0.2,0.8]，轴上刻度到 1.0）
- **推翻记录**：2026-08-04 的 "y 轴 = log" 判定（我亲看权威图得出）**错误**。当时把竖排轴标题 "(C_sca/(λ²/2π))" 笔画误读为指数刻度。**opus 的 linear[0,7] 反而是对的**（非"猜"，是读到了 1,3,5,7）。教训：竖排标题 + 刻度竖写容易混读，判刻度必须逐标签放大亲读 + vision-mcp 交叉，不能凭笔画像"10 的幂"就判 log。
- **修正文件**（4 处）：
  - `data/alaee_fig1_axes.yaml`：4 面板 y_scale → linear，tick_label_hint 更新（1,3,5,7 / 0,25,50,75,100）
  - `notes/fig1-parameters.md`：#9 纵轴 log→linear 1,3,5,7；#15 刻度 0,25,50,75,100；图结构说明改左/右分列
  - `notes/fig-axes.md`：速查表 Fig.1 全 linear，判 log 依据段作废，Fig.2/3 标"待核"
  - `formalization/alaee2018-fig1.yaml`：normalization + multipole_universal_limit 注释更新
- **对实现的影响**：归一化 C_sca/(λ²/2π) 的值域 1~7，linear 轴即可全部显示；各多极曲线叠加 (2j+1) 普适上限参考线（1/3/5/7 三条水平线）直接可视。
- **待办**：Fig.2/Fig.3 的 y_scale 早期 medium 置信度判定（判 log）不可信，需用权威高清图 + vision-mcp 重核（不阻塞 Fig.1 主线）。
- gate① 仍待用户确认（参数内容更新：y=linear 1,3,5,7）

## 2026-08-05 | gate① 用户通过 + agent-workflow skill 搬迁 + 进 gate②

- **gate① 用户通过**（2026-08-05），要求写明经验教训：从论文图提取的参数**下一步开工前必须人工复核 + workflow 结束前整体复核**。
- **经验教训落盘**：`memory/lessons.md` 教训 9 新增第 6 点（流程硬化：图提取参数人工复核 + 结束前复核）；skill 的 gate 规则写入同一硬化。
- **agent-workflow skill 搬迁**（SEPR/optics-lead 裁剪 → zotero）：
  - `.claude/skills/agent-workflow/`（主 agent）：SKILL.md（4轮×7步 + 4 gate + 复述纪律 + 人工复核硬化）+ references/（spawn 全局模板 + 8字段报告模板 + 主报告模板）
  - `.claude/skills/sub-agent/`（子 agent 身份）
  - `.claude/agents/{main-agent,sub-agent,sub-leaf}.md`（三层，裁剪 SEPR 骨架）
  - 路径改 zotero `reproduction/`，步骤改 mie-f 7 步
- **formalization yaml 完善**（step02 推进）：
  - size_param.range 注释更新（刻度到 1.0，vision-mcp 核实）
  - 新增 `panel:`（布局/轴类型）、`truncation:`（l_max=2 + n_max Wiscombe）、`curves:`（三曲线定义 + 样式）、`verification_points:`（x=0.75 误差>100% + y 轴普适上限）
- **下一步**：gate② spec gate——用户核对 formalization yaml 的物理 spec（几何/材料/照明/输出/截断）是否与论文 Fig.1 物理一致。

## 2026-08-05 | gate② formalization spec 对齐 SEPR 9 字段 + per-multipole 映射修正

- **formalization yaml 对齐 SEPR 9 字段标准**（参考 gold standard：SEPR case 0703-01-akimov-mie-v1）：
  - 新增 meta / boundary_conditions / sources / assumptions / missing_fields / provenance
  - equations 结构化：primary_BH_mie（a_n/b_n/c_n/d_n）+ cross_sections + table1_approx + table2_exact + eq1_multipole + limit_identities
  - solver 补 problem_statement/strategy/environment；verification 三层结构化
  - 公式与讲义 §10（表1）/§11（表2）逐字核对
- **发现并修正 per-multipole Mie 映射错误**：
  - ❌ 初稿写反：ED=b_n(1)/MD=a_n(1)/EQ=b_n(2)/MQ=a_n(2)
  - ✅ 正确（repro-plan §6.1 + B&H 约定）：**ED=a_n(n=1)/MD=b_n(n=1)/EQ=a_n(n=2)/MQ=b_n(n=2)**（a_n=电多极/TM，b_n=磁多极/TE）
  - 这是 gate③ 会核对的公式，提前在 spec 层修正，避免污染后续代码
- **产物**：`formalization/alaee2018-fig1.yaml`（完整 spec，gate② 停点）
- **gate② 待用户核对**：6 组物理 spec（几何/材料/方程/边界/源/求解/可观测）

## 2026-08-05 | gate② 用户审查回复：2 硬伤 + 2 待澄清，修复完成

**🔴 硬伤1（致命）per-multipole Mie 映射自相矛盾**：
- `observables.per_multipole` 正确（ED=a_n(1)/MD=b_n(1)/EQ=a_n(2)/MQ=b_n(2)），但 `solver.strategy` 写反（ED=b_n(1)/MD=a_n(1)）
- 我此前只改了 per_multipole，漏改 strategy——同一文件两处不一致，正是"对照原文件核对"该抓的
- **修复**：strategy 改成与 per_multipole 一致（ED=a_n(1), MD=b_n(1), EQ=a_n(2), MQ=b_n(2)）

**🔴 硬伤2 截断混用**：Wiscombe n_max（总 C_sca）与 per-multipole l≤2（逐多极曲线）混淆，三曲线自洽 <0.1% 口径未写明
- **修复**：strategy 加"截断分界"块——总 C_sca 用 Wiscombe n_max≈7；per-multipole 三曲线自洽只对逐多极分项比对（Mie(l) vs 表2(l) vs 表1(l)），不拿"表1/表2 到四极总和"比"Mie 全阶总和"

**🟡1 x 数据范围 [0.2,0.8] → [0.2,1.0]**：
- 像素统计：面板(a) 曲线彩色像素延伸到 col 1114 ≈ x 轴右端 col 1116 → 曲线画到 x≈1.0
- 0.75 验证点不再卡在边缘，留余量
- 更新 size_param.range、problem_statement、strategy n_max 注释

**🟡2 相对误差分母**：论文未明示。选择 C_Mie 作分母（|C_approx−C_Mie|/C_Mie，才能复现 >100%）；notes 补充判断依据

- **gate② 修复完成，重新待用户核对**

## 2026-08-05 | gate② 放行 + step03 推导笔记完成（gate③ 停点）

- **gate② 用户放行** step03（硬伤已修 + 待澄清按证据/物理定稿合理）
- **顺手动作完成**：formalization scope_applicability 残留 [0.2,0.8] → [0.2,1.0]
- **B&H 原书核对**（本地 Zotero S9DSIDNN，扫描件 533 页）：
  - 用 pdf-mcp OCR + PyMuPDF 渲染 + pytesseract 多轮精读
  - PDF 页偏移确认：PDF 页 109 = 书页 100（公式 4.51-4.53），PDF 页 110 = 书页 101（4.56-4.57）
  - **a_n/b_n（B&H 4.56/4.57，μ 相等 Riccati-Bessel 形式）确认与讲义 §2/spec 逐字一致** ✅
  - **B&H 用 e^{−iωt} 时谐约定**（页 101 原文确认），与 spec 一致 ✅
  - **c_n/d_n（B&H 4.52）扫描件 OCR 数学公式噪声大**，转录标注"待 gate③ 对原书核"；用 B&H 原文结构约束（c_n 分母=b_n 分母、d_n 分母=a_n 分母）自检通过
- **step03 产物**：
  - `notes/alaee2018-mie-coeff.md`：a_n/b_n/c_n/d_n 对照 B&H Ch.4 + Riccati-Bessel + scipy 实现 + per-multipole 映射 + gate③ 核对清单
  - `notes/alaee2018-table2-impl.md`：表2 四式球坐标体积分展开 + r→0 极限 + φ 降维方案 + 退化验证
- **gate③ 待用户核对**：c_n/d_n 对 B&H 原书核（Y9，内部场关键）+ a_n/b_n 复核 + 尺寸参数换算

## 2026-08-05 | gate③ 裁决通过：c_n/d_n 核实 + 引文措辞纠正 + x_Mie 硬要求

- **gate③ 用户对扫描件逐字核**：c_n/d_n 公式转录正确（c↔b、d↔a 分母配对、分子两项带 m 都对）；a_n/b_n 一致；时谐 e^{−iωt} 确认
- **⚠️ 引文措辞纠正**：我曾把 B&H 4.53 那句英文改写成 "denominators of c_n and b_n are identical as are those of a_n and d_n"，扫描件原文是 "denominators of the internal coefficients c_n and d_n are identical to those of the scattering coefficients b_n and a_n, respectively"。已改回逐字。教训：引用原文必须逐字，凭理解改写是转录风险（正是 gate③ 要防的）
- **🔴 step04 硬性要求**：x_Mie = π·(2a/λ)（host=air），不得直接拿 2a/λ 当 x_mie（峰位偏 π 倍）。已写进 spec geometry.mie_size_param_conversion + mie-coeff 笔记 §8。**test 锚点**：介电球 n=2.5，第一磁偶极 Mie 共振峰应落 2a/λ≈0.5–0.7（x_mie≈1.6–2.2）
- **产物更新**：notes/alaee2018-mie-coeff.md（§4 引文逐字 + §8 gate③ 裁决）+ formalization/alaee2018-fig1.yaml（geometry 尺寸参数换算）
- **下一步**：step04 实现 code + tests（baseline_mie.py 先行 → mie_theory → multipole；test 含 x_Mie 峰位锚点）

## 2026-08-05 | step04 实现开始（TDD，baseline 先行）

- 环境确认：numpy 2.3.5 / scipy 1.16.3 / pytest 8.4.2，复宗量球 Bessel 支持
- **顺序**（repro-plan §2.2）：baseline_mie.py 先过 Layer1 → mie_theory → multipole → 复现再过 Layer1 → Layer3
- 子 agent 已派：params.py + baseline_mie.py + test_mie.py（Layer1 锚点）

## 2026-08-05 | step04 阶段1 完成 + 锚点峰位重大修正

- **阶段1 交付**：params.py（x_Mie 换算 + Wiscombe）+ baseline_mie.py（独立 Mie 基准）+ tests/test_mie.py（9 项 Layer1 全过：能量守恒 1e-10/瑞利 x⁴/零吸收/大 x Q_ext→2/光学定理/x_Mie 换算/峰位锚点）
- **🔴 锚点峰位修正（重要）**：spec/notes 早期记"磁偶极峰 2a/λ≈0.5-0.7"是**凭直觉猜错**。step04 实测（主 agent 独立核实）：
  - ED a_1 峰 2a/λ=0.500（x_mie=π/2≈1.571，Fröhlich 偶极共振）
  - **MD b_1 峰 2a/λ=0.385**（x_mie≈1.209，ka·n≈π 球内驻波，物理自洽）
  - EQ a_2 峰 0.647（x_mie=2.033）；MQ b_2 峰 0.543（x_mie=1.705）
  - 0.5-0.7 区间实为 EQ/MQ 峰混合区，非 MD。已更新 spec + mie-coeff 笔记
- **教训**：锚点/峰位必须实测或算过，不能凭直觉/记忆写。子 agent 实测 + 主 agent 独立复核（跑代码确认）双确认后才可信
- 下一步：阶段2 mie_theory.py（内部场 c_n/d_n）+ test_xmie.py（峰位锚点）

## 2026-08-05 | step04 阶段2 完成 + d_n 分子转录修正（重要）

- **阶段2 交付**：mie_theory.py（internal_field_coefficients c_n/d_n + internal_E_field 矢量球谐展开 + internal_current_density J=−iωε₀(ε_r−1)E）+ tests/test_xmie.py（6 项）
- **全部 15 项测试 PASS**（test_mie 9 + test_xmie 6）
- **🔴 d_n 分子转录修正（重要）**：spec/notes 早期 d_n 分子第二项写"不带 m"（−ξψ'），**违背球面切向边界条件**。子 agent 用独立库 miepython + 边界条件发现，主 agent 独立复核：
  - 错误版（spec）：d_n 分子 [mψξ' − ξψ']，与 miepython.cn_dn 差异 0.736 ❌
  - 正确版：分子两项都带 m [mψξ' − mξψ']（与 c_n 分子相同），差异 1.4e-15 ✅
  - gate③ 当时只核了分母结构约束（c↔b、d↔a 配对），未逐字核分子第二项——教训：转录校对要逐项，不只核结构
- **修正**：spec d_n_internal + notes mie-coeff §4（3 处）
- 下一步：阶段3 multipole_moments.py（表2）+ multipole_approx.py（表1）+ test_multipole.py（退化）

## 2026-08-05 | step04 全部完成：20 项测试全过 + 核心物理验证成立

- **阶段3 完成**（子 agent 卡死后主 agent 接手）：multipole_moments.py（表2 精确多极矩）+ multipole_approx.py（表1 近似）+ test_multipole.py
- **修复过程**（主 agent 独立诊断）：
  - 子 agent 报"∫Ex dV=139 异常"卡死——实为积分 bug（非 mie_theory 问题，内部场本身验证正确 m→1=1.7e-08）
  - _integrate_3d 修 ComplexWarning（复数积分保虚部）
  - **前置系数对齐**：表2 MD/EQ/MQ 补乘 3/2、3、15；表1 MD/EQ/MQ 用 1/2、1、1——两者退化才成立
  - **标定系数**：ED x⁶=0.00865（理论 1/12π²=0.00844 吻合）、MD x⁸=0.00558、EQ x⁸=4.2e-5、MQ x¹⁰=8e-6（跨 x 稳定）
- **核心物理验证**：
  - 表2→表1 退化：x→0 时全部多极矩一致（<0.3%）✅
  - **表2 vs Mie 交叉**：ED 0.999-1.005、MD 0.998-1.015（独立实现一致 <1.6%）✅
  - **作废（B1 重 gate）**：~~2a/λ=0.75 处表1 C 误差 ED=169.7%、MD=2275%~~；该旧快照不被当前代码支持。以 B1 精确值替代：C 口径 ED=86.9148%、MD=215.9110%；复矩向量口径 ED=136.1669%、MD=277.7424%。
- **全部 20 项测试 PASS**（test_mie 9 + test_multipole 5 + test_xmie 6）
- 下一步：step05 run（收集 C_sca vs 2a/λ 数据）→ step06 3 层验证 → 最终自检查 → gate④

## 2026-08-05 | step05 数据异常：表2 大 x 失效（规范等价边界项缺失）→ blocker

- **step05 run 完成**：200 点扫描落盘 3 CSV（mie/table2/table1）
- **Mie 数据完美**：ED 峰 2.999@0.502、MD 峰 3.000@0.385、EQ 4.999@0.646、MQ 4.981@0.542（普适上限 3/5）✅
- **作废（B1 重 gate）**：~~表1 误差复现：2a/λ=0.75 ED=167.7%、MD=2453%~~；旧数据生成于修复前路径，改以 `codex-prompts/out/B1-fig1-s075-evidence.json` 的最近点/精确点证据为准。
- **🔴 表2 大 x 失效（严重）**：表2/Mie 比值随 x：0.2→1.02、0.5→1.28、0.65→35、0.8→0.013（崩溃）。表2 应在全 x 精确等于 Mie，但大 x 严重偏离
- **根因诊断（主 agent）**：
  - 网格加密不改善（40→80 网格比值不变）→ 非网格问题
  - 只 j_0 项在 x=0.65 比值 11.6 → j_0 项本身也崩
  - 完整表2 ED 在 x=0.65：j_0 项 0.38（应小）、j_2 项 1.03（应抵消但反而大）
  - **理论根源**：讲义 §11 明确警告——表2 的 j_2 项（对称无迹形式）与中间形式 eq:p_partial 之间是"积分意义下的规范等价"，需分部积分+总导数项（FC2015 补充材料）。我逐点实现 j_2 项漏了边界项 → 准静态对、大 x 崩
- **方案**：用讲义 §11 eq:p_partial（第 98-99 行，逐点成立）重实现表2 ED；其他多极同理需检查。这是高难度物理推导，按执行方式应主循环处理或 opus 深挖
- **blocker**：表2 是主验收一部分（"表1/表2/Mie 三曲线自洽"），必须修复才能 gate④

## 2026-08-07 | step05 blocker 解阻：径向坐标因子与解析归一化修复

- **最终根因改判**：`multipole_moments.py`、`multipole_approx.py` 和 `multipole_ppartial.py` 把 `r/a` 的笛卡尔分量误写成纯方向余弦，导致 `r·J`、`r×J`、EQ/MQ 张量缺少径向因子；不是普通网格密度问题，也不是需要经验拟合的 `K(x)` 漂移。
- **积分器修复**：φ 使用不含重复端点的周期求和，U/θ 使用 Simpson；默认验收网格为 `(40,41,80)`。
- **波数结论**：表2球 Bessel 辐射核默认使用 host `k`；`kernel_k="internal"` 仅作错误分支回归。
- **Eq.1 归一化**：删除 `.00865/.00558/.000042/.000008`，改为 `1/(12π²)` 与 `1/(1440π²)` 解析常数及 `x⁶/x⁸/x¹⁰` 幂次。
- **验收**：原有 20 项 `pytest` 全过；扩展快速测试 `33 passed`；200 点全区间慢测 `1 passed in 298.67s`。旧未掩码统计 ED 0.9624%、MD 0.03834%、EQ 0.6157%、MQ 0.6585% 仅作历史审计对照；B1 统一 near-zero mask 后图/合同统计为 ED 0.1404%、MD 0.0383%、EQ 0.2020%、MQ 0.1252%（全部 <1%）。
- **报告**：详见 `notes/table2-large-x-blocker-resolution.md`。`baseline_mie.py` 与 `mie_theory.py` 未修改。
- **数据重生成**：用 `(40,41,80)` 网格完成 200 点 Fig.1 三曲线重算，`data/fig1a_multipole_{mie,table2,table1}.csv` 均为 200 行；CSV 复核的最大误差与慢测一致。

## 2026-08-05 | 表2 blocker 解除：根因 = 坐标分量漏乘径向 U（用户修复 + 主 agent 独立复核）

- **用户修复**：表2 大 x 失效根因是 r_α/a 被误写成纯方向余弦（漏乘 U 径向因子），破坏大 x 处径向相消。非 host-k 错误或边界项缺失。
- **修复内容**：
  - multipole_moments.py：_cartesian_position 返回 U·方向；host-k 波数 ρ=x_mie·U；Eq.1 解析常数（ED=x⁶/12π²、MD=x⁸/12π²、EQ=x⁸/1440π²、MQ=x¹⁰/1440π²）；积分器 φ 周期+Simpson
  - multipole_approx.py：表1 同步坐标修正
  - multipole_ppartial.py：改为诊断路径（排除"补边界常数"解释）
  - test_multipole.py：新增九点/200点测试
- **主 agent 独立复核**：
  - 九点表2/Mie 比值全部 ≈1.000（最大 0.17% @EQ 0.8）✅（之前 0.65→35、0.8→0.013 已修复）
  - 全套 33 passed 1 skipped 无回归 ✅
- **用户 200 点验收**：ED 0.96%、MD 0.04%、EQ 0.62%、MQ 0.66% 最大误差（<5% 达标）
- 子 agent 独立审查进行中（核坐标修正/host-k/Eq.1 常数推导）
- **blocker 解除，表2 与 Mie 全区间一致** → 三曲线自洽成立

## 2026-08-05 | 子 agent 独立审查通过：表2 修复六项全过，blocker 完全解除

- **子 agent 独立审查**（只读，核坐标修正/host-k/Eq.1 常数/积分器/r→0/回归）：
  - 坐标修正（U 因子）：✅ 逐项核对 + 独立复现旧 bug（34.5@0.65 吻合）
  - host-k：✅ 正确（internal 分支复现 390.85 吻合，仅诊断用）
  - **Eq.1 解析常数 1/1440 = 1/(120·12)**：✅ 双路径确认（分析推导 + 准静态数值锁定）。1/120 来自四极系数，12 来自 6·2 归一化组合；MQ 用 x¹⁰（磁项 1/c² 引入 k²）正确
  - 积分器：✅ 6 个解析积分测试通过（φ 周期求和精确消 m=±1）
  - r→0：✅ 所有核极限正确
  - 回归：✅ 33 passed 1 skipped；200 点误差与报告逐位一致（ED 0.96/MD 0.04/EQ 0.62/MQ 0.66%）
  - 旧经验常数已删除（生产路径 grep 干净）
- **非阻塞问题修复**：multipole_ppartial.py 第 80 行误导文案（ratio 最差 155 却打印"恒≈1"）→ 改为诚实诊断说明
- **总评（旧结论，B1 后部分作废）**：~~修复可信，可放行；表1 在 s≈0.75 ED 误差 169%>100%~~。Mie/Table2 <1% 路径保留；论文 s=0.75 的主口径改由 B1 复矩向量表决，C 误差仅作诊断。
- **下一步**：step06 3 层验证（Layer1/2/3 脚本）→ 最终自检查 → gate④

## 2026-08-07 | 第 2 轮启动：step01 完成（Fig.2 参数重核 + 金数据 3 源）+ step02 fig2.yaml 重写（gate② 停）

- **用户拍板**：金介电函数不用读图提取，改用 ≥3 独立公认源核对一致；本轮范围 (a)+(b) 双面板；数据源 JC+Olmon+McPeak
- **4 子 agent 并行调研金数据源**：JC 1972 / Olmon 2012 / McPeak 2015 / Rakić 1998 + Palik 汇编评估
  - 全部可从 refractiveindex.info YAML 直接下载（CC0）；Palik 是汇编翻版不作独立源
  - 重要更正："Babar & Rakić 2005 (PRB 71, 205109)" 不存在 → 实为 Babar & Weaver 2015（不入主源）
- **金数据落盘**：data/gold_epsilon.csv（400-2500nm @5nm 421 点，列=JC/Olmon/McPeak/mean）
  - 550nm 三源：ε₁=-5.93/-6.18/-6.64（互差<7.4%）、ε₂=+2.10/+1.63/+1.68（互差<13%）→ 一致通过
  - 全谱段：600-1000nm ε₁<8% 一致；400-600nm 带间区 JC ε₂ 偏高 29%（文献已知特性，不影响表2 vs Mie 方法对比）
- **Fig.2 论文原文确认**（PDF 页4 caption 逐字）：仅 (a)(b) 两面板、无误差子图；表2 vs Mie "indistinguishable up to a numerical noise level" → 验收 <1%
- **Fig.2 轴类型 vision-mcp 双通道重核**：y = linear 1,3,5,7（双面板）✅；x = 2a/λ（0.2-1.0，**非波长轴**，与 Fig.1(b) 不同）→ 金球 λ∈[500,2500]nm
  - 旧 fig2_axes.yaml y=log 判定作废（教训 8/9 应用），axes yaml + fig-axes.md 已更新
- **fig2.yaml 重写**（formalization/alaee2018-fig2.yaml，SEPR 9 字段）：
  - 修正旧 draft 硬伤：radius_nm:250 全局错放 → 分面板；outputs 表2vs表1 → 表2 vs Mie；补归一化/普适上限/金材料
  - 介电球 (a) 数据复用第 1 轮 fig1a CSV（同一物理）
- **gate② 停点**：用户核对 fig2.yaml（双面板 spec + 金数据 3 源结论）

## 2026-08-08 | Fig.2 formalization 对抗审查与 gate② 解阻修订

- **原论文视觉核实**：Fig.2 为 2×1 上下双面板，双面板横轴均为 2a/λ；金球 a=250nm 对应 λ=500–2500nm。
- **金数据政策修正**：原 mean 列在 1700→1705nm 有三源均值→Olmon 单源跳变，且 JC 仍覆盖至约 1937nm；现改为 JC 论文形状对比、Olmon-EV 全区间方法验收、三源分别敏感性包络。
- **550nm 统计口径修正**：按 max pairwise range / |mean| 计算ε₁=11.35%、ε₂=25.75%，不再宣称三源完全一致。
- **复数电流修正**：`mie_theory.internal_current_density` 由 |m|²−1 改为 m²−1；新增复数金球回归。
- **可审计产物**：`data/_gold_sources/manifest.yaml`、`notes/fig2-formalization-review.md`、修订后 fig2.yaml/fig2-parameters.md。
- **测试**：`42 passed, 1 skipped`；新增 15 项 Fig.2 数据/复数 Mie 测试全过；skipped 为既有 200 点表二慢测（需 `RUN_TABLE2_SLOW=1`）。
- **裁决**：formalization 已备齐用户 gate② 核准；图二 200 点体积分数值验收仍属 step04，本轮不宣称其数值通过。

## 2026-08-08 | Fig.2 数值实现与 200 点加密 gate 通过

- 新增 `code/run_fig2.py`：按 $2a/\lambda$ 等距采样、在波长域线性插值 $n/\kappa$、越界硬失败，并保证 Mie/Table2 每点使用同一复数 $m$。
- Olmon-EV 全区间 200 点：基线网格 `(40,41,80)` 仅 MQ p95=0.114% 略超 0.1%；加密网格 `(60,61,120)` 四通道全部通过。
- 加密最大相对误差：ED 0.01186%、MD 0.01699%、EQ 0.01610%、MQ 0.02414%；p95 均小于 0.024%；最大绝对误差均小于 $2.64\times10^{-4}$。
- 完整 200 点网格变化最大值：ED 0.0452%、MD 0.0642%、EQ 0.0608%、MQ 0.0907%，均小于 0.1%。
- JC/McPeak 各完成 80 点 Table2/Mie 敏感性扫描；三源在 500--1700 nm 共同区间生成 min--max 包络，不取均值材料。
- 新增 `code/plot_fig2.py`、`code/build_fig2_sensitivity.py`，生成 `figs/fig2_reproduction.png` 与 `figs/fig2_gold_material_sensitivity.png`。
- 新增 `code/report_fig2_ratios.py`，输出九个指定点的介电球与 Olmon-EV 金球四多极 `Table2/Mie` 比值表：`notes/fig2-nine-point-ratios.md` / `data/fig2_nine_point_ratios.csv`。
- 裁决：Fig.2 Table2/Mie 方法 blocker 已解除，formalization 可提交 gate②；论文像素 RMSE 阈值仍留 gate④ 人工裁决。

## 2026-08-08 | Fig.2 Layer3 PDF vector 曲线提取与论文对比

- 推翻“只能视觉描点”的假设：源 PDF 第4页实测 840 个 drawing，Fig.2 四色 Mie polyline 与 exact marker 均可直接提取。
- 新增 `code/extract_fig2_vector.py`：vector 主路径、tick 轴拟合、PDF SHA256 与路径计数审计；栅格分割只允许 `DESCRIPTIVE_ONLY`。
- 新增 `code/compare_fig2_paper.py`：介电球全区间、金球 JC 有效区的 RMSE/MAE/p95/峰位/峰高比较，并明确 mask `x<500/1935`。
- 主结果：介电 ED/MD/EQ vector PASS；MQ RMSE=0.02556、p95=0.05695，略超 0.02/0.05 gate，状态 `UNRESOLVED`；金球 JC 域内四条 Mie 实线全部 PASS。
- 金球完整 panel 状态 `MATERIAL_DOMAIN_LIMITED`；未用 Olmon 补齐 JC 越界段。
- 产物：`data/fig2_paper_vector_curves.csv`、`data/fig2_paper_vector_metadata.json`、`data/fig2_layer3_summary.json`、`figs/fig2_layer3_overlay.png`、`notes/fig2-layer3-paper-comparison-review.md`。

## 2026-08-08 | gate② 放行 + 补 step03 + Layer3 论文图对比（像素级）

- **Codex 异构审查完成**（用户发强模型，结论回传）：Fig.2 formalization + 数值验收闭环，gate② 可放行
- **主 agent 独立核实**（复述纪律）：fig2-numerical-acceptance.md + fig2_gold_olmon_refined_summary.json 数字逐位一致
  - Olmon-EV 200 点加密网格 (60,61,120)：ED 0.01186% / MD 0.01699% / EQ 0.01610% / MQ 0.02414%（max rel，p95 <0.1%）；abs <2e-3；网格收敛 <0.1%；52 passed 1 skipped
  - 介电球 (a) 复用 fig1a CSV + 九点比值 0.99907-1.00049
  - miepython 复数路径交叉过（550/1000/1700/1935/2500nm）
- **gate② 用户放行**（合并到计划批准 2026-08-08）：formalization fig2.yaml reviewed-ready
- **金数据方案定稿**（Codex 对抗审查修正）：JC 保真层（500-1935nm）/ Olmon-EV 方法验收（500-2500nm）/ 三源敏感性包络（500-1700nm min-max 非均值）；ε=m² 禁 |m|²；波长域插值禁外推；550nm 严格口径 ε₁ 互差 11.35%/ε₂ 25.75%
- **下一步**：补 step03 notes（alaee2018-fig2.md）→ Layer3 论文图像素级 RMSE（用户拍板）→ report-round2 → gate④

## 2026-08-08 | Layer3 完成（Codex vector 提取）+ report-round2 + gate④ 停

- **Codex Layer3 完成**（vector 提取替代 vision 描点）：
  - 从源 PDF 页4 提取 1578 行 vector 曲线（PyMuPDF 路径，840 drawing objects；x/y 数据坐标残差 0.00044/0.00657，换算后最大约 0.068/0.053 PDF point）
  - 源 SHA256 c79e243e...；vision 描点降级 DESCRIPTIVE_ONLY fallback
  - **介电球 (a)**：ED/MD/EQ PASS_VECTOR_CONSISTENT（RMSE 0.010-0.013）；**MQ UNRESOLVED**（RMSE 0.02556 超 0.02、p95 0.05695 超 0.05，但峰位差 2.1e-5 几乎完美）
  - **金球 (b)** JC 有效域（2a/λ≥0.2584）四通道全 PASS；域外 MATERIAL_DOMAIN_LIMITED（JC 1935nm 越界，未静默用 Olmon）
  - **旧归因已由 gate④ 复算推翻**：共同域实际为 212 点、误差>0.05 为14点；max gap=0.23026 位于 x=0.13945→0.36971 断段而非峰区，不能用来证明尖峰被稀疏 polyline 削顶。最终只保留“误差集中在高曲率区、具体来源未唯一归因”。
  - 完整回归 62 passed, 1 skipped（+10 Layer3 专项）
- **report-round2 完成**：main.tex + 5 sections（01 概述/02 金数据/03 数值验收/04 Layer3/05 结论），实际编译为 11 页 PDF
  - ⚠️ 编译坑：`\include` 写 sections/*.aux 失败（Desktop 同步/权限，round1 正常）→ 改 `\input` 绕过
- **gate④ 停点**：用户裁决 MQ UNRESOLVED（是否阻塞）+ result_class + RMSE 阈值；对抗审查 prompt 08 已落盘可发强模型

## 2026-08-08 | gate④ 最终对抗审查：带限制放行

- 新增 `opus-prompts/08-fig2-final-acceptance-review-RESULT.md`，逐字核对论文、讲义、报告、CSV 和机器摘要。
- **方法/图形分层裁决**：`method_claim_status=PASS`；`strict_vector_fidelity_status=UNRESOLVED`；`paper_fidelity_status=UNRESOLVED`；金球完整域 `MATERIAL_DOMAIN_LIMITED`。
- **MQ graphical floor**：同一 23 个 marker x 上，论文 Mie vs exact 的 RMSE/p95=0.02430/0.06187，本地 Mie vs 论文 Mie=0.00933/0.02104 → `CONSISTENT_WITH_PAPER_GRAPHICAL_FLOOR`，但不覆盖预注册 strict gate。
- **exact marker**：中位间距约 0.0296>峰位 gate 0.01，所有通道峰位裁决统一为 `DESCRIPTIVE_ONLY`；形状指标单独保留。
- **Q 因子补充**：仅有两侧域内半高交点才计算；介电四通道与金 ED 通过 5% 补充容差，金 MD/EQ/MQ 为 `NOT_EVALUABLE`；该后补指标不用于追溯性晋级。
- **最终 SEPR 裁决**：`gate4_decision=PASS_WITH_LIMITATIONS`，`result_class=partial_physical_match`，`promotion_to_physical_reproduction_success=DENIED`。MQ 不阻塞“表2/Mie 方法复现成功”，但阻塞本轮完整 Fig.2 晋级。
- **路径纠错**：任务书所写 `report-round1/main.pdf` 实际应为 `report-round1/main_aux/main.pdf`。
- **最终回归**：67 passed, 1 skipped；Layer3/gate④ 专项 15 项全过。

## 2026-08-09 | 讲义修正（审查 09 驱动）+ 第 3 轮计划 v2

- **对抗审查 09 返回 BLOCKED**（gate② 前，强模型审查第 3 轮 Grahn 映射 spec）：5🔴+7🟡，全部接受（主 agent 逐项独立核实全部属实）
  - 讲义 §8 L44 M^(2) "无迹对称"标签错误（实为 9 分量一般不对称原始矩）
  - Q^e=6·STF(M2) 仅长波成立；Table 2 精确 Q^e 禁喂 Grahn 张量映射
  - 双路径混比不同近似阶 → 拆：低-kr Grahn 张量映射↔Table 1；全域 Grahn Eq.8-9 核积分↔Mie
  - 磁四极 a_M(2,m) 原文有（grahn2012-chinese.tex:379-392 Eq.26-28）不可降级
  - a_E(1,m) 非 p-only 含 O 八极修正；m 求和通用全 m + 球体简化；C 系数 ε 是 host 绝对介电常数
- **讲义 3 处修正**（用户批准）：
  - §8 L44：无迹对称 → 一般不对称原始矩（9 分量）
  - §12 L190/L368：|m|²/c → |m|²/c²（残留清除）
  - §8 L293：附录 A → 主文 Eq.(44)-(48)
  - 讲义重新编译成功（80 页，\input 方案绕 include aux 坑），PDF 验证修正生效
- **第 3 轮计划 v2**：repro-plan-round3.md 全面修订（双路径拆分 + M2 四对象 + 磁四极收录 + m 域 + ε_d host + 独立路径）
- **memento**：073b9885（讲义 bug + 审查教训）
- **下一步**：批准后执行 step01（读 Grahn 公式）→ step02（建 grahn.yaml）→ 重新发审查

## 2026-08-09 | 第 2 轮收尾完成：用户批准复现通过 + 完整报告 17 页 + 讲义修正

- **用户最终批准复现通过**（2026-08-09）：gate④ 关闭，接受 PASS_WITH_LIMITATIONS（partial_physical_match，不晋级）
- **完整报告**：report-round2/main_aux/main.pdf 17 页（8 节结构：概述/流程/公式/实现/验证/论文对比/审查/结论 + 参考文献）
  - 新增论文 Fig.2 原图（PDF 提取）+ 复现图并排对比
  - bib 8 条目（Alaee/B&H/Grahn/Wiscombe/JC/Olmon/McPeak/Rakić）全部解析
  - 编译修复坑：章节标题裸 \lambda（hyperref）、\path 宏包不兼容（改 \texttt）、批处理 \t 转义
- **讲义 3 处修正**（审查 09 驱动，用户批准）：§8 L44 M^(2) 标签、§12 L190/L368 /c→/c²、§8 L293 附录→主文
- **第 3 轮计划 v2 就绪**：repro-plan-round3.md（审查 09 全部接受修订：双路径拆分/M2 四对象/磁四极收录/m 域/ε_d host/独立路径）
  - 对抗审查 09 gate② BLOCKED → 已修订 → 待重新提交
- **memento**：7f1b9b0b（收尾完整化）+ b19ecca2（金数据方案）+ 073b9885（Grahn 讲义教训）+ 33840e86（编译坑）
- **下一步**：压缩后启动第 3 轮（Grahn 映射）——先重提交 gate② 审查（09 修订版）

## 2026-08-09 第 3 轮 step01+02（Grahn 映射）

- **step01 ✅**：`notes/grahn-formulas.md` 落盘
  - 原文 PDF（33KFYX34，12 页）逐式编号核对：Eq.(3)(4) 远场投影、(6) J_S、(13)(14) 核积分（含 j_l(kr)）、(15)(16) 分部积分、(20) C_sca、(21) 入射场、(22) C_ext、(27) M^(l)、(35)–(48) 映射全 14 式
  - **审查 09 编号勘误**：09 所引 "Eq.(8–9) 含 Bessel 核" 实为原文 (13)(14)；原文 (8)(9) 是 Maxwell 方程。语义正确、编号错误，计划/yaml 已改正
  - 译本文字引用 = 原文编号；译本 LaTeX 自动编号另套（错位）
  - 讲义 3 处修正（§8 L44 / §12 L190+L368 / §8 L293）亲读确认落盘 ✅
- **step02 ✅**：`formalization/grahn.yaml` 落盘（SEPR 9 字段 + M2 四对象 + Q^e=6STF 长波限定 + 双路径拆分 + 磁四极 (44)–(46) + ε_d host + m 全求和 + 独立路径 + 4 解析基准 + 错误注入 + 容差预注册 + result_class_ceiling=method_consistency）
- **gate② 停 ⏸**：审查 prompt `opus-prompts/10-grahn-mapping-formalization-review.md` 落盘（09 修订版复核 + 编号勘误验证 + 09 盲区找茬 18 问），等用户发强模型

## 2026-08-09 第 3 轮 gate② 审查 10 BLOCKED → v2 修订

- **审查 10 回来**：gate2_decision: BLOCKED（5🔴+9🟡+3🟢），核心：Eq.(13) 转录错误、Eq.(15)-(19) 未机器化、编号残留、归一化未闭环、解析基准不可执行、边界分布项
- **主 agent 独立核实（全部证实）**：
  - 🔴1 Eq.(13)：字形级（rawdict 字符 bbox）确认原文第一项 k²**r**·J_S 的 r 是位置向量（y=692.1 无 hat accent）；第二项是 **(2+rd/dr)(∇·J_S)**（词级 "2 +r d dr [∇·JS]"）—— 译本 tex 转录错误（写 (d²/dr²+k²)r∇·J），yaml v1 抄了译本
  - 🔴2 计划残留：L16 "Eq.(8–9)"、L29 "Eq.12"、L83 "Eq.8-9" grep 证实
  - 🔴3 alaee2018-chinese.tex L206-207 残留 /c（grep 证实）；🟢1 12_unified.tex L374 "1/c 因子"（grep 证实）
  - 🟡6 Q^m-O 恒等式：代数验证对称/无迹自洽（ε 全反对称 + O 后两指标对称 → ΣQ^m_αα=0 ✓）
- **triage：5🔴+9🟡+3🟢 全项接受**（无拒绝——审查质量高）
- **v2 修订落盘**：grahn.yaml v2（Eq.13/14 原文逐字 + Eq.15-19 完整 + 归一化闭环 + 解析基准可执行 + MQ 三构造 + 边界分布 + 依赖图 + Grahn Eq.22 光学定理 + path B 低端段 + SEPR 结构化）；repro-plan-round3.md 编号残留清除（L16/L29/L83 + 62→67）；notes/grahn-formulas.md 补转录勘误 + Eq.15-19 定义
- **待用户批准源文件勘误**：① 12_unified.tex L374；② alaee2018-chinese.tex L206-207；③ grahn2012-chinese.tex L207-212
- **gate② 重停**：审查 prompt `opus-prompts/11-grahn-mapping-formalization-review.md`（24 问，含 Eq.13↔15 等价性 + MQ 闭式核对 + Ψ'' 数值 + 10 盲区）等用户发强模型

## 2026-08-09 第 3 轮 gate② 审查 11 BLOCKED → v3 修订

- **审查 11 回来**：gate2_decision: BLOCKED（6🔴+9🟡+3🟢），核心：YAML 解析失败（analytic_benchmarks 混列）、bump 闭式积分全错（SymPy 独立复核）、canonical Rayleigh 斜率 6 非 4、低端段 EQ/MQ 空 gate、逐 m 目标未结构化
- **主 agent 独立核实（全部证实）**：
  - 数值复核 bump 闭式：I0=64πR³/315、I2=64πR⁵/3465、I4=64πR⁷/15015、I22=64πR⁷/45045（I4=3I22）全部与审查一致（我 v2 心算闭式错）
  - 五案例闭式复核：bump_polarized p_z=(iJ₀/ω)I0、double_blob M2_zz=(iJ₀d/ω)I0、circulating m_z=J₀I2、MQ_m0=-(iJ₀/ω)I22、MQ_m2=(iJ₀/ω)(I4-I22)、MQ_m1=(iJ₀/ω)(I22-I4) 全部一致
  - 有限-kr 反例：sixSTF=0.174080 vs 审查 0.1740796（吻合）；相对差 ~0.97%（kR=0.5 时 <1%，v2 断言 >1% 错）→ 改断言 >0.5% + 明确范数/分母
  - Rayleigh：canonical C_sca/(λ²/2π) 斜率 = 6.0008（非 4；4 是 Q_sca 效率）；v2 写 4±0.1 错 → 改 6±0.1
- **triage：6🔴+9🟡+3🟢 全项接受**（无拒绝）
- **v3 修订落盘**：grahn.yaml v3（YAML 结构合法化 bump_function/cases/numerical_scale + 闭式修正 + 斜率 6 + 逐 m 目标 + 低端绝对阈值 + π_lm 极点/Ψ'' 递推/ρ→0 级数 + spherical_jn+1j*yn + 等价性 m=±1 absolute-zero + miepython gate 不 skip + source/local equation 结构化）；safe_load 通过
- **gate② 重停**：等用户发审查 #12（11 修订复核 + 闭式 oracle 核验）

## 2026-08-10 第 3 轮 gate② 审查 12 BLOCKED → v4 修订

- **审查 12 回来**：gate2_decision: BLOCKED（4🔴+10🟡+1🟢），核心：讲义 4 文件残留错误 Eq.(13)/O_lm 简写、相位契约未锁、低端逐通道容差缺失、Rayleigh 口径不一致、双斑 d 几何矛盾、MQ kR 截断、远场契约缺失、path A 阈值未机器化、计划版本漂移
- **主 agent 独立核实（全部证实）**：
  - 🔴1 讲义残留 grep 逐行证实：06_current_integral.tex L122/181、07_integration_parts.tex L119/136/145/150/264、12_unified.tex L315 写 (d²/dr²+k²)r∇·J（错，应为 (2+rd/dr)(∇·J)）；07 L119/264 + 12 L330 O_lm 简写漏 1/√(l(l+1))·√((2l+1)/4π)；04_projection L289-295 X_lm 相位差 i
  - 🔴3 Rayleigh：完整 Mie 总截面重算 lin [0.02,0.2]=6.101、log=6.079、lin [0.02,0.1]=6.036——与审查 6.103/6.078 吻合；v3 的 6.0008 是 ED 单通道解析近似旧口径，作废
  - 🟡6 双斑：d=0.5R 两 bump 重叠（不重叠需 d≥2R）——几何矛盾证实
- **triage：4🔴+10🟡+1🟢 全项接受**
- **v4 修订落盘**：phase_convention（Condon-Shortley/Y_lm/X_lm 相位/sph_harm_y 顺序/探针）+ forbidden_source_paths 黑名单 7 条 + 逐 m 数值容差 + 低端 mask/渐近 oracle + Rayleigh 6±0.3（observed 6.079）+ 双斑 d=2.5R + MQ kR 扫描 + 远场契约 + path A 阈值 + Eq.(22) 域/mask + cases 澄清；repro-plan-round3.md 同步 v3（版本条款 + 逐 m + Rayleigh + path A 真值）
- **待用户批准源文件勘误新增 4 处讲义残留**（06/07/12 的 Eq.13 + O_lm 简写 + 04 X_lm 相位）
- **gate② 重停**：审查 prompt #13 待写，等用户发强模型

## 2026-08-10 21:30 mie-f 完成计划收尾（用户压缩前）

- **A1-A6 全部完成并验收**（6 个 Codex）：A1 审计（Fig.1 🔴 需重 gate + A2 独立复核逐位一致）、A2 第3轮实现 v4（105 passed）、A3 magnus 探索（GUI 模板硬前置）、A4 Fig.3 规划草案、A5 MQ UQ 预注册（峰区 90.67%）、A6 Fano 文献（587 行+23 BibTeX）
- **第一批 B 任务已启动并发**：B2 光学定理 S(0) / B3 Fig.2 UQ 晋级 / B4 源文件勘误 9 处
- **用户授权**：08-11 12:00 前 2-3 CODEX 并发 + magnus 无限制（gustation.phybench.cn，≤256G，token 不落盘）
- **落盘**：`mie-f-completion/OVERVIEW.md`（任务标记 + codex 并发/resume 方式 + 踩坑）+ `B{1,5,6,7,8,10}-*.md` 剩余 prompt
- **人工停点**：B9 COMSOL 6.3 GUI 模板（唯一纯人工硬前置）、B1 指标口径裁决、gate 放行
- memento: e6b1f4d2（handoff）

## 最终阶段索引（2026-08-11）

本节只追加导航，不改写上述历史记录。最终状态以冻结数据、当前 spec、对应审查收据和报告正文为准；人工 gate 未在此索引中自动关闭。

| 阶段 | 主要产物路径 |
|---|---|
| A1--A2：前两轮审计、Grahn v4 独立复验 | `codex-prompts/out/A1-*`、`codex-prompts/out/A2-*` |
| A3：Magnus/COMSOL 可行性与硬前置 | `codex-prompts/out/A3-*` |
| A4--A5：Fig.3 规划、Fig.2 UQ 预注册/重算 | `codex-prompts/out/A4-*`、`codex-prompts/out/A5-*` |
| A6：Fano/比较器文献与 claim ledger | `codex-prompts/out/A6-*` |
| B1--B9s：Fig.1 re-gate、UQ、勘误、数值审计、Fig.3 surrogate/COMSOL 探索 | `codex-prompts/out/B1-*` 至 `codex-prompts/out/B9s-*` |
| B10：四轮最终报告与独立审查 | `codex-prompts/out/B10-*`、`report-final/main_aux/main.pdf` |
| B11--B13：Fig.3 spec 路径候选审查、Fig.1 metric 强审 | `codex-prompts/out/B11-*`、`codex-prompts/out/B12-*`、`codex-prompts/out/B13-*` |
| B14：全栈最终审查与现场重算 | `codex-prompts/out/B14-fullstack-review.md`、`codex-prompts/out/B14-numeric-recompute.py` |
| B15：可修项落地与验证收据 | `codex-prompts/out/B15-fix-report.md` |
| 最终整合报告 | `report-final/main.tex`、`report-final/sections/`、`report-final/bib/references.bib`、`report-final/main_aux/main.pdf` |

## 2026-08-12 收尾（transition-wrapup）
- Fig.3 COMSOL 真解谱闭环（B29-B31）：9 点谱 + MD 磁共振（x=0.36）+ ED r=0.999 vs 论文 + PARTIAL_PASS 诚实裁决
- Grahn gate④ 关闭（用户接受 PASS_WITH_NOTES + 3 notes；收据 GRAHN-G4-20260812 + B21 external support）
- 用户拍板：Fig.3 晋级（B32）+ Fig.2 补 UQ（B33）——两线并发中
- doc-sync 全套已更新（主文档 216 行 + 00 决策 4 项 + 05 COMSOL）
- memento: 3ed09a14（session_summary）+ b45971b4（安全模型终版）
