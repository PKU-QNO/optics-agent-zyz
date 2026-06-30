# Mie 理论复现计划（最终版）

> 2026-06-30
> 这是给 main-agent（CC）执行用的最终版计划。重点是 7 阶段执行顺序 + 每篇论文简介。
> agent 执行时读 `.claude/skills/main-agent/SKILL.md` 走 10 步 workflow，4 个人工 gate 停下来问用户。
> 3 层物理检验规则见 `.claude/skills/optics-mie-reproduction/references/verification.md`。

---

## 一句话目标

手动实现单球/核壳/球点阵的 Mie 散射解析/半解析计算，构建有效介质折射率等物理量的基准数据集，作为后续 COMSOL 数值计算的验证基准。全程 Python，不用 COMSOL。

---

## 执行顺序（7 阶段递增，难度从易到难）

每阶段产 `code/*.py` + `tests/test_*.py` + benchmark 条目 + formalization spec + 推导笔记。每阶段跑完追加 benchmark.yaml 条目。

### 阶段 1：单球 Mie 基础（从这里开始）

**主论文**：Akimov, "Mie scattering theory: a review of physical features and limitations" (arXiv 2401.04146, 2024)
- **论文简介**：系统回顾 Mie 散射中电多极/磁多极系数的物理起源，分析球贝塞尔/汉克尔函数渐近行为对散射效率的影响。是 review 性质，适合入门。
- **目的**：实现 Lorenz-Mie 核心公式，观察 Rayleigh/Mie/几何光学三区平滑过渡，多极共振出现顺序
- **产出**：`code/mie_coefficients.py`（$a_n,b_n$）、`code/scattering.py`（截面）、$Q_{sca}(x)$ 曲线、能量守恒+瑞利极限检验
- **检验**：能量守恒 $C_{ext}=C_{sca}+C_{abs}$、瑞利 $Q_{sca}\propto x^4$、大尺寸 $Q_{ext}\to 2$
- **注意**：Akimov 是 review，偶有笔误，核心公式以教材（Bohren & Huffman `.paper/scattering.pdf`）为主源，Akimov 做交叉
- **gate**：①参数核对 ②spec 核对 ③公式 $a_n,b_n$ 对教材核 ④误差核对

### 阶段 2：金属球 LSPR

**主论文**：Colas des Francs, "Mie plasmons: modes volumes, quality factors and coupling strengths" (arXiv 1112.2814, 2011)
- **论文简介**：用 Mie 展开计算金属纳米球 LSPR，给出模体积、品质因子、Purcell 因子闭式表达。引入 Drude 色散。
- **目的**：引入 Drude 色散，考察介电函数实部/虚部如何影响 LSPR 位置和线宽
- **产出**：`code/drude.py`（Au/Ag Drude）、`code/lspr.py`、LSPR 波长 vs 半径、Purcell 因子谱
- **检验**：准静态 LSPR $\mathrm{Re}(\varepsilon)=-2\varepsilon_d$
- **物理要点**：准静态近似（$a_1$ 主导）与完整 Mie 展开的差异

### 阶段 3：介质球 Mie 模式

**主论文**：优先 Web of Science 补经典代表，参考 García-Etxarri (2011)、Kuznetsov "Magnetic light" (Sci. Rep. 2012)、Evlyukhin (Nano Lett. 2012)、Kuznetsov "Optically resonant dielectric nanostructures" (Science 2016)
- **论文简介**：高折射率介质小球内部位移电流可形成磁偶极/电偶极/磁四极/电四极等多种 Mie 模式，损耗通常低于金属。
- **目的**：比较金属 LSPR 与介质 Mie 共振的物理差异，理解介质纳米结构更丰富的电/磁多极模式
- **产出**：介质球消光谱、多极分解、磁偶极模式可视化
- **物理要点**：磁偶极来自球内环形位移电流；共振位置由尺寸参数和折射率决定；电/磁偶极相对强度决定 Kerker 条件

### 阶段 4：核壳结构 Mie

**主论文**：Tam, "Mesoscopic nanoshells: geometry-dependent plasmon resonances beyond the quasistatic limit" (JCP 127, 2007) — PDF 在 `papers/mie/204703_1_online.pdf`
- **论文简介**：双层球 Lorenz-Mie 计算核壳消光谱，发现准静态近似在壳层较厚/较薄时均失效。
- **目的**：单球扩展为核壳，理解两层边界条件递推
- **产出**：`code/core_shell_mie.py`、不同壳厚消光谱、壳厚-共振波长相图、准静态 vs 完整 Mie 对比
- **检验**：壳厚→∞ 退化为单球（核材料），核→0 退化为单球（壳材料）
- **参考**：Arruda, "Toroidal dipole in core-shell spheres" (arXiv 2406.06800)

### 阶段 5：周期阵列集体共振（SLR）

**主论文**：Auguie & Barnes, "Collective Resonances in Gold Nanoparticle Arrays" (PRL 101, 2008) — PDF 在 `papers/mie/PhysRevLett.101.143902.pdf`
- **论文简介**：周期阵列中 Rayleigh 异常与 LSPR 耦合产生高品质因子表面晶格共振（SLR），线宽由阵列周期精确控制。
- **目的**：单球过渡到周期体系，理解衍射耦合如何改变共振性质
- **产出**：`code/coupled_dipole.py`（CDA）、不同周期消光谱（标注 Rayleigh 异常和 SLR）、线宽-周期曲线
- **检验**：Rayleigh 异常位置 $\lambda=P\cdot n_{\text{eff}}$；大周期退化为单球
- **参考**：Gerasimov, "Plasmonic lattice Kerker effect" (arXiv 2007.13317)

### 阶段 6：二元阵列几何共振

**主论文**：Li J et al., "Tuning of narrow geometric resonances in Ag/Au binary nanoparticle arrays" (Opt. Express 18, 2010) — PDF 在 `papers/mie/Li_J_OE2010.pdf` 或 `oe-18-17-17684.pdf`
- **论文简介**：两种不同材料/尺寸颗粒组成二元阵列，通过尺寸比独立控制几何共振位置和线宽。
- **目的**：CDA 框架引入两种单颗粒极化率，理解材料色散和几何参数耦合调控
- **产出**：`code/binary_cda.py`、不同尺寸比消光谱、线宽-尺寸比曲线
- **检验**：大周期退化为单颗粒结果

### 阶段 7：有效折射率提取与相图

**主论文**：Rybin, "Phase diagram for the transition from photonic crystals to dielectric metamaterials" (Nat. Commun. 6, 2015) — PDF 在 `papers/mie/Rybin_NatComm2015.pdf`
- **论文简介**：比较 Mie 共振波长和 Bragg 共振波长相对大小，在介电常数-填充率平面建立区分光子晶体区/超材料区的相图。
- **目的**：球阵列散射响应浓缩为等效光学参数，得到有效折射率色散曲线
- **产出**：`code/effective_medium.py`（S 参数反演 $\varepsilon_{\text{eff}},\mu_{\text{eff}}$）、`code/phase_diagram.py`、$n_{\text{eff}}$ 色散、$(\varepsilon,P/\lambda)$ 相图
- **检验**：低填充率→Maxwell-Garnett

### 选做（接入点已明确）

| 论文 | arXiv | 内容 | 接入点 |
|------|-------|------|--------|
| Tagviashvili | 0910.3305 | ENZ 极限 Mie 散射 | 连到有效介质 $n_{\text{eff}}\to0$ |
| Shamkhi | 1808.10708 | 广义 Kerker 横向散射 | 连到阵列散射角分布 |
| Arruda | 2406.06800 | 核壳 toroidal 偶极 | 核壳深入拓展 |
| Nieto-Vesperinas | 1201.6146 | Si 球 Kerker 条件 | 单球定向散射 |

---

## 3 层物理检验（每阶段必跑）

1. **Layer 1 物理硬约束**：能量守恒 / 无损吸收 / 光学定理 / 瑞利极限 / 大尺寸极限 / 球对称性（每条带适用条件/容差/失败解释/不适用）。任一适用 Layer 1 失败 → result_class ≤ diagnostic_only
2. **Layer 2 极限退化**：Rayleigh 极限 / 大尺寸 extinction paradox / 准静态 LSPR / 壳厚→∞退化 / 低填充率→Maxwell-Garnett
3. **Layer 3 论文图量化**：RMSE、共振峰位误差（nm）、Q 值相对误差，区分参数缺失/模型简化/数值错误/论文不可复现

---

## 4 个人工 gate（中间 agent 自由跑）

1. **参数抽取后**（step 02 末）：半径、折射率、波长范围对不对，单位对不对
2. **物理 formalization 后**（step 03 末）：geometry/materials/equations/边界条件写成结构化 spec
3. **关键公式推导后**（step 04/05 末）：Mie 系数 $a_n,b_n$ 表达式对着教材 `.paper/scattering.pdf` 核
4. **曲线与论文图对比后**（step 08 末）：看量化误差数字，不听"基本一致"

---

## 哪些信任 AI，哪些不行

**可以信任 AI**（低风险，跑完扫一眼）：PDF 提取/公式 OCR、`scipy.special` 特殊函数求值、代码框架/绘图/单位换算、文献检索

**不能信任 AI**（高风险，必须人工确认）：
- Mie 系数 $a_n,b_n$ 最终表达式——必须对教材核，AI 经常搞反分母分子、漏阶数
- 边界条件——切向 vs 法向连续，AI 容易搞混
- 物理参数选取——单位/折射率实虚部/波长范围，错一个量级全错
- "成功"判定——AI 倾向说"looks good"，看 verifier 数字
- 容差阈值——你定，不是 AI 定
- 论文图对比结论——看 RMSE 和峰位误差数字
- 单次经验上升为通用规律——不能直接写长期 skill

---

## 代码组织

```text
reproduction_test/mie/
├── code/           # 实现代（mie_coefficients.py / scattering.py / drude.py / core_shell_mie.py / coupled_dipole.py / binary_cda.py / effective_medium.py）
├── tests/          # 物理 verifier（和代码同步写）
├── formalization/  # 每篇论文的物理 spec（人工 gate ②）
├── data/           # benchmark.yaml 标准答案
├── figs/           # 输出图
└── notes/          # 推导笔记
```

---

## skill 生命周期（避免 Degiron 教训）

阶段 1 产出 `optics-mie-reproduction` skill 标 `status: candidate`，明确写"仅单球 Mie 验证，未覆盖核壳/阵列"。等阶段 4（核壳）也过了再升 `active`。skill 内容带适用边界（applies_when / does_not_apply_when）和来源 case。

---

## 教材依赖

核心公式（尤其 $a_n,b_n$）以教材为主源：
- **Bohren & Huffman**, *Absorption and Scattering of Light by Small Particles*（首选）— 在 `.paper/scattering.pdf`（27.8MB）
- **Kerker**, *The Scattering of Light*（备选）

Akimov 等 review 论文做交叉验证，不当唯一来源。

---

## 启动指令（给 CC）

```
读 C:\Users\27370\Desktop\project\self-evo-paper-repro\WORK_LOG.md 恢复上下文
读 CLAUDE.md 知道路由
你是 main-agent，开始复现 .paper\mie\ 里的 Akimov 2401.04146（阶段 1：单球 Mie 基础）
读 .claude\skills\main-agent\SKILL.md 走 10 步 workflow
4 个人工 gate 停下来问我
教材在 .paper\scattering.pdf（Bohren & Huffman），核心公式 an,bn 对教材核
```

---

**本计划结束。阶段 1 从 Akimov 2401.04146 开始。**
