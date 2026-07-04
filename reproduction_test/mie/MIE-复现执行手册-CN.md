# Mie 复现执行手册（人话中文）

> 2026-07-03
> 这是 `mie_reproduction_plan-FINAL-CN.md`（下称 **FINAL 计划**）的**执行 companion**，不覆盖它。
> FINAL 计划回答"复现什么、7 阶段是什么、每篇论文简介"；本手册回答"**在 SEPR 里怎么真跑、11 篇按什么顺序、人怎么判对错**"。
> **诚实口径**：这套 W-flow + 3 层验证 + 4 gate 的组合**一次都没真跑过**。下文全部是「计划/预期动作」，不是「已验证流程」。第一篇（Akimov）跑完之前，任何"应该会通过"都当假设看。

---

## 0. 读者定位与前置引用

本手册假设你已读过（**不重复其内容，只引用**）：

- FINAL 计划 `reproduction_test/mie/mie_reproduction_plan-FINAL-CN.md`：7 阶段、每篇论文简介、代码组织、教材依赖、启动指令。
- SEPR `.human/skills/main-agent/SKILL.md` + `sub-agent/SKILL.md`：main/sub agent 身份、spawn 模版拼接机制、fan-out 并发、失败防护（5 轮上限）。
- SEPR `.human/skills/{main,sub}-agent/workflow/0X-*/SKILL.md`：10 步 W-flow 每步的局部模版。
- SEPR `.claude/skills/optics-mie-reproduction/references/verification.md`：3 层物理验证的表格与容差。
- SEPR `CLAUDE.md`：result_class 7 级枚举、4 个人工 gate、双写同步、记忆纪律。

本手册只做三件 FINAL 计划没展开的事：**A. 工作流怎么真跑**、**B. 11 篇实现顺序**、**C. 人怎么判对错**。

---

## A. 如何使用工作流跑 Mie

### A.1 用户怎么启动（一句话触发）

启动指令见 FINAL 计划末尾"启动指令（给 CC）"节，照抄即可。要点：

1. 用户在 SEPR 工作区对 Claude Code 说：**"你是 main-agent，复现 `.paper/mie/2401.04146.pdf`（阶段 1：单球 Mie）"**。
2. CC 以 **main-agent** 身份启动：读 SEPR `CLAUDE.md`（路由+红线）+ `main-agent/SKILL.md`（编排规范）+ `WORK_LOG.md`（恢复上下文）。
3. main-agent **不亲自写代码**，它按 10 步 W-flow 推进，每步 spawn 一个 **sub-agent** 干活，在 4 个 gate 停下来问用户。

**判定**：不是每个请求都进 10 步。只有"复现一篇新论文/新图"才进完整 W-flow；调试、问问题、跑单脚本直接做（见 `main-agent/SKILL.md` "进入 workflow 的判定"）。

### A.2 10 步在 Mie 场景下具体干啥（含 gate / spawn 标注）

下表把 W-flow 10 步（+11 主 agent 定稿）落到 Mie 阶段 1（单球）的具体动作。**"简化"列专门标出：因为 Mie 阶段 1 是纯 Python 解析、不碰 COMSOL/Magnus，哪些步骤被压缩。**

| 步 | 名 | Mie 场景具体动作 | spawn 子 agent? | 人工 gate? | 纯 Python 带来的简化 |
|---|---|---|---|---|---|
| 01 | pdf_preprocessing | 提取 Akimov 2401.04146 的正文/公式/**全部图清单**（⚠ 2026-07-04 修订：论文实际**无** $Q_{sca}(x)$ 过渡曲线图，目标图由 step02/03 从真实图清单定，首跑候选为 Fig3 loci / Fig5(c)(f) $\|a_1\|,\|b_1\|$ / Fig6）；`_src.tar.gz` 有 LaTeX 源，公式直接从源取比 OCR 准 | 是 | 否 | 无 COMSOL 参数表要抽，只抽物理公式与图数据 |
| 02 | paper_reading | 读论文+WoS 补经典，抽物理参数（半径、折射率、波长/尺寸参数范围、介质）成参数表 | 是 | **Gate 1（参数核对）** | 参数少（单球只有 $n$、$x$ 或半径+波长），无网格/求解器/license 参数 |
| 03 | reproduction_design | 定复现目标（复现哪张图/哪个量），写结构化 formalization spec（geometry/materials/equations/BC） | 是 | **Gate 2（spec 核对）** | geometry 只是"一个球"，无 COMSOL 几何/网格设计；直接定死"纯解析、不上 magnus" |
| 04 | theory_and_implementation | 从 Maxwell 推到 $a_n,b_n$ 与截面公式；写 `code/mie_coefficients.py`+`scattering.py`+`tests/`；`scipy.special` 求 Bessel/Hankel | 是 | Gate 3 前置 | 无 `.java`/`.mph`，无 Magnus 提交；本地秒级跑完，不需要云计算 |
| 05 | theory_check | 对抗式审查：$a_n,b_n$ 分子分母、阶数、符号、切/法向 BC 双向归因核 | 是 | **Gate 3（公式核对）** | 审查对象是解析公式而非 COMSOL 设置，审查面更小但更关键 |
| 06 | run_and_monitor | 跑 `code/` 生成目标量 CSV（$Q_{sca}(x)$ 基线曲线 + step03 定的论文目标图数据）；本地跑 | 是 | 否 | **最大简化**：无 Magnus 排队/日志监控/job retry，本地直接跑出数 |
| 07 | physical_verification | 跑预制 verifier（能量守恒/瑞利/大尺寸）= Layer 1；再 Layer 2 极限退化 | 是 | fail 时停问 | 无"Magnus success ≠ COMSOL success"的多态歧义，只剩物理对错 |
| 08 | result_analysis | 数字化 Akimov 图，算 RMSE/峰位误差 = Layer 3；四类偏差归因 | 是 | **Gate 4（误差核对）** | 无 COMSOL 数值收敛伪影要排，偏差来源更干净 |
| 09 | reproducibility_selfcheck | 换 $n_{\max}$ 截断/波长网格/随机种子重跑，排除"瞎猫碰死耗子" | 是 | 否 | 解析结果对网格不敏感，自检快 |
| 10 | summary_and_report | 写双报告 + benchmark.yaml 条目 + 更新记忆 + skill 草稿标 `candidate` | 是 | 否 | 报告里明确"纯解析基准，未涉 COMSOL 验证" |
| 11 | main_agent_report | main-agent 写全局总结，问用户哪些进 `.result/`，同步过 gate 的 skill 草稿，更新 memento | 否（main 亲写） | 进 `.result` 前停问 | — |

**纯 Python 简化总结（一句话）**：阶段 1-7 全是解析/半解析 Python，**step 06 从"提交 Magnus job + 监控日志 + 防 retry 用旧码"退化为"本地 `python` 跑一下"**；step 03 无 COMSOL 几何/网格/求解器设计；step 04 无 `.java`/`.mph`/license 挂载；step 07 无"Magnus success != COMSOL solve success != 物理复现"的三态陷阱，只剩物理对错。COMSOL/Magnus 的复杂度要等 Mie 基准建成、后续做数值验证时才回来。

### A.3 spawn 与并发的机械动作

- 每步 main-agent 走"模版拼接"：全局模版（`references/spawn_template_global.md`）+ 局部模版（该步 `main-agent/workflow/0X-*/SKILL.md` 的 spawn 局部模版块）+ 本篇论文的具体参数/注意。拼成一条完整 spawn 指令给 sub-agent。
- sub-agent 读 `sub-agent/workflow/0X-*/SKILL.md`（怎么干+预制脚本），写 8 字段报告到 `.work/.sub-report/`，**第 6 字段"决策性回答"**是 main-agent 拍板依据。
- **并发**：一篇论文若有两张互相独立的图（如 Akimov 的 Fig3 loci 与 Fig5 系数谱），main-agent 可在同一步 fan-out 多个 sub-agent，各写各的报告文件。**必须真独立**（无数据/文件/逻辑依赖），有依赖就串行。唯一汇聚点是 main-agent，无 supervisor/worker 双对话。
- **失败防护**：同一步重跑 5 轮仍不过 → 标 blocked 写失败报告，不硬跑；重跑必须带新证据（相同 fingerprint 第二次失败即 blocker）；case 级超限（4h / spawn 20 / 搜索 30）→ 停问用户。

---

## B. 11 篇论文按什么顺序实现

### B.1 PDF 文件 → 论文 → 阶段 映射（先认清手上有什么）

`.paper/mie/` 里 11 个 PDF（配 6 个 `_src.tar.gz` LaTeX 源）：

| # | PDF 文件名 | 论文 | 在 FINAL 计划的位置 |
|---|---|---|---|
| 1 | `2401.04146.pdf` | Akimov, Mie scattering review (2024) | 阶段 1 主 |
| 2 | `1112.2814.pdf` | Colas des Francs, Mie plasmons (2011) | 阶段 2 主 |
| 3 | `204703_1_online.pdf` | Tam, Mesoscopic nanoshells (JCP 2007) | 阶段 4 主 |
| 4 | `2406.06800.pdf` | Arruda, core-shell toroidal dipole (2024) | 阶段 4 参考 |
| 5 | `PhysRevLett.101.143902.pdf` | Auguié & Barnes, gold NP array SLR (PRL 2008) | 阶段 5 主 |
| 6 | `2007.13317.pdf` | Gerasimov, plasmonic lattice Kerker (2020) | 阶段 5 参考 |
| 7 | `oe-18-17-17684.pdf` | Li J, Ag/Au binary arrays (OE 2010) | 阶段 6 主 |
| 8 | `Rybin_NatComm2015.pdf` | Rybin, PhC→metamaterial phase diagram (2015) | 阶段 7 主 |
| 9 | `1201.6146.pdf` | Nieto-Vesperinas, Si sphere Kerker (2011) | 选做 |
| 10 | `1808.10708.pdf` | Shamkhi, generalized transverse Kerker (2018) | 选做 |
| 11 | `0910.3305.pdf` | Tagviashvili, ENZ-limit Mie (2009) | 选做 |

（`Li_J_OE2010.pdf` 只有 598 字节，是坏文件/占位符，用 `oe-18-17-17684.pdf`。）

**重要缺口（诚实标注）**：FINAL 计划**阶段 3（介质球 Mie 模式）在 `.paper/mie/` 里没有对应 PDF**——计划写的是"优先 Web of Science 补 García-Etxarri 2011 / Kuznetsov 2012&2016 / Evlyukhin 2012"。所以阶段 3 需要先在 step 02 用 WoS 检索并下载一篇经典代表，才能进 step 03。启动阶段 3 前先把这篇 PDF 落地。

### B.2 推荐实现顺序（按能力依赖递进，一行一篇）

排序原则：**单球解析核 → 加色散 → 加介质多极 → 加第二层边界 → 加周期耦合 → 加第二材料 → 抽等效参数**。每篇只在前一篇能力上加一个新维度。选做篇挂在与其最近的主篇之后（能力就绪时再做，非阻塞）。

1. **`2401.04146` Akimov（阶段 1，第一篇 / benchmark 基石）** — 交付单球 Mie 核（$a_n,b_n$+截面+$Q_{sca}(x)$ 教学基线曲线），**论文图比对目标从 step02 真实图清单定**（⚠ 2026-07-04 修订：论文无 $Q_{sca}(x)$ 过渡曲线图；首跑候选 Fig3 loci / Fig5(c)(f) $|a_1|,|b_1|$ / Fig6，见 SEPR `.work/.todo/2401.04146/0703-01-akimov-mie-v1/figures.md`）。依赖：无（从 Maxwell + 教材 $a_n,b_n$ 起）。新增能力：Lorenz-Mie 系数 + 截面 + 能量守恒/瑞利/大尺寸 verifier。**这一篇跑通即建立整个 Mie benchmark 与 verifier 基础设施。**
2. **`1112.2814` Colas des Francs（阶段 2）** — 复现金属球 LSPR 波长-半径关系、Purcell 谱。依赖：#1 的 Mie 核。新增能力：Drude 色散 `drude.py`、LSPR、准静态 vs 完整 Mie 对比。
3. **`1201.6146` Nieto-Vesperinas（选做，接阶段 2/3 之间）** — 复现 Si 球第一 Kerker 条件（前向/后向散射比、$a_1=b_1$）。依赖：#1 核 + 介质材料参数。新增能力：电/磁偶极相对相位、角分布、Kerker 判据。**放这里是因为它是"单球定向散射"，比周期阵列简单，且为阶段 3 介质多极热身。**
4. **阶段 3 介质球 Mie 模式（先 WoS 补 PDF，如 García-Etxarri 2011 / Kuznetsov 2012）** — 复现高折射率介质球磁偶极/电偶极多极分解消光谱。依赖：#1 核 + #3 的介质 Kerker 直觉。新增能力：多极分解、磁偶极可视化。**阻塞点：PDF 未在库，需先下载。**
5. **`204703_1_online` Tam（阶段 4 主）** — 复现核壳消光谱、壳厚-共振相图、准静态失效。依赖：#1 单球核（扩成两层边界递推）。新增能力：`core_shell_mie.py` 双层边界条件、壳厚→∞/核→0 退化验证。
6. **`2406.06800` Arruda（阶段 4 参考，接 #5）** — 复现核壳 toroidal（环形）偶极贡献。依赖：#5 核壳递推。新增能力：环形偶极多极项、更细多极分解。
7. **`PhysRevLett.101.143902` Auguié & Barnes（阶段 5 主）** — 复现周期金颗粒阵列的 SLR：Rayleigh 异常位置、线宽-周期曲线。依赖：#2 单颗粒极化率（金 LSPR）。新增能力：`coupled_dipole.py`（CDA）、衍射耦合、大周期→单球退化验证。
8. **`2007.13317` Gerasimov（阶段 5 参考，接 #7）** — 复现 plasmonic lattice Kerker（阵列级定向散射）。依赖：#7 CDA + #3 Kerker 判据。新增能力：阵列散射角分布、晶格 Kerker 条件。
9. **`oe-18-17-17684` Li J（阶段 6）** — 复现 Ag/Au 二元阵列几何共振随尺寸比调控。依赖：#7 CDA 框架（引入两种单颗粒极化率）。新增能力：`binary_cda.py` 双材料/双尺寸极化率、尺寸比扫描。
10. **`Rybin_NatComm2015` Rybin（阶段 7）** — 复现 PhC↔超材料相图：Mie 波长 vs Bragg 波长在 $(\varepsilon, P/\lambda)$ 平面分区。依赖：#1 Mie 共振位置 + #7/#9 阵列。新增能力：`effective_medium.py`（S 参数反演 $\varepsilon_{eff},\mu_{eff},n_{eff}$）、`phase_diagram.py`、低填充率→Maxwell-Garnett 验证。
11. **`1808.10708` Shamkhi（选做，收尾）** + **`0910.3305` Tagviashvili（选做，收尾）** — Shamkhi：广义横向 Kerker（接 #8 阵列角分布）；Tagviashvili：ENZ 极限 Mie（接 #10 有效介质 $n_{eff}\to0$）。依赖各自最近的主篇，能力全部就绪后收尾做，非阻塞。

### B.3 "先跑通一篇建 benchmark，再扩"的节奏

- **第一篇（Akimov）是回归测试基石**：它跑通 = 拿到 Lorenz-Mie 核 + 3 个 Layer-1 verifier 脚本 + `benchmark.yaml` 第一条标准答案 + `optics-mie-reproduction` skill 标 `status: candidate`（明写"仅单球验证，未覆盖核壳/阵列"，见 FINAL 计划 skill 生命周期节）。
- **不要并行铺开多篇**：每篇加一个新能力维度，前一篇的 verifier 是后一篇的回归护栏（如核壳的壳厚→∞必须退化回单球，用的就是 #1 的单球结果）。
- **skill 升级节奏**：阶段 1 出 `candidate`；等阶段 4（核壳）也过再升 `active`（避免 Degiron 那种"一次成功就写死通用规律"的教训）。每条 skill 带 `applies_when` / `does_not_apply_when` + 来源 case。
- **失败也是产出**：某篇 blocked，step 10 照写失败报告，标原因+走到哪步+下次怎么改，进 `.E-history` 当负面知识，不删。

---

## C. 如何人工判断复现正确性

### C.1 3 层物理验证：每层通过/不通过意味着什么

细则见 `verification.md`，本节只讲**人怎么读结果**。3 层**从易到难顺序跑，任一层 fail 立即停**，不继续下一层。

| 层 | 查什么 | **通过意味着** | **不通过意味着** |
|---|---|---|---|
| **Layer 1 物理硬约束**（参数无关，如能量守恒 $C_{ext}=C_{sca}+C_{abs}$、无损→零吸收、光学定理、瑞利 $Q_{sca}\propto x^4$、大尺寸 $Q_{ext}\to2$） | AI 糊弄不了、外行也能凭常识判的硬物理 | **只代表"没犯大错"，不代表数值准**。必须继续 Layer 2/3 | **代码有结构性 bug**（系数写错、单位错、符号错）。**result_class 直接封顶 `diagnostic_only`**，禁止声明成功，回 step 04 修 |
| **Layer 2 极限退化**（已知答案的极限：准静态 LSPR $\mathrm{Re}(\varepsilon)=-2\varepsilon_d$、壳厚→∞退化单球、核→0退化壳、周期→∞退化单球、低填充→Maxwell-Garnett） | 代码在已知解析极限下给出正确答案 | 实现的结构逻辑对（边界递推、耦合项没接错） | **结构性实现错误**（如核壳边界条件接反）。回 step 04 |
| **Layer 3 论文图量化**（数字化论文曲线，算 RMSE<5% 峰值、峰位<5nm(vis)/<1%(IR)、Q 相对误差<10%、峰幅<10%） | 与论文在**定量容差内**一致 | 未过容差**不等于失败**，先做四类归因（见 C.4） | 定量偏差需归因，不能"看着差不多"就算过 |

**铁律**：Layer 1 任一适用项 fail → result_class 不得高于 `diagnostic_only`；"目视叠合像"**不算**Layer 3 通过，必须报 RMSE 和峰位误差数字。

### C.2 4 个人工 gate：分别核什么、卡在哪步

gate 之间 agent 自由跑，gate 处 main-agent **必须停下来问用户**（除非用户明说全自动）。

| gate | 卡在哪步 | 用户核什么 | 不过的后果 |
|---|---|---|---|
| **Gate 1 参数核对** | step 02 末 | 半径、折射率（实/虚部）、波长/尺寸参数范围、介质 $\varepsilon_d$、单位对不对。**错一个量级全错** | 参数错则后面全白跑，退回重抽 |
| **Gate 2 spec 核对** | step 03 末 | formalization spec：geometry/materials/equations/边界条件写成结构化对不对，复现目标（哪张图/哪个量）明确否 | spec 含糊则 step 04 实现跑偏 |
| **Gate 3 公式核对** | step 04/05 末 | **核心 $a_n,b_n$ 表达式对着教材 Bohren & Huffman `.paper/scattering.pdf` 逐行核**（AI 常搞反分子分母、漏阶数、切/法向 BC 搞混）。**这是最不可替代的 10 分钟** | 公式错则所有数字物理无意义 |
| **Gate 4 误差核对** | step 08 末 | **看量化误差数字，不听"基本一致"**。读 RMSE、峰位误差(nm)、Q 相对误差，判是否进 `.result` | 误差大或归因不清则不得标成功 |

**30 分钟人工 check（每篇，见 verification.md）**：跑 3 个 verifier（自动 5min）→ 对教材核公式 2-3 行（人 10min，最关键）→ 读量化对比数字（自动+人 5min）→ 物理直觉检查（人 5min，峰在该在的地方吗）。第 2、4 步不可自动化替代。

### C.3 result_class 7 级：怎么对应"跑通 vs 物理复现成功"

用 SEPR `CLAUDE.md` 强制的 7 级枚举，**禁用** success/partial/fallback/blocked/failed 等旧口径：

| result_class | 含义 | 在 Mie 里的典型场景 |
|---|---|---|
| `not_run` | 未跑 | 阶段还没启动 |
| `pipeline_completed` | 流程跑完，无物理判断 | W-flow 10 步走完但没过 Layer 1-3——**不是复现成功** |
| `diagnostic_only` | 只做诊断，无复现声明 | Layer 1 硬约束 fail 时封顶到这——**不是复现成功** |
| `surrogate_fallback` | 用代理/简化方案 | 用了简化模型代替真实计算——**不是复现成功** |
| `partial_physical_match` | 部分物理量匹配，未全过 | 峰位对了但线宽差太多、只过 Layer 1-2 没过 Layer 3 |
| `physical_reproduction_success` | 物理复现成功 | **Layer 1 硬约束 + Layer 2 极限 + Layer 3 论文图量化 + 4 gate 全过**才能标 |

**最高优先级红线（照抄 CLAUDE.md）**：LLM/agent **不得**把 `surrogate_fallback` / `diagnostic_only` / `pipeline_completed` 当成 `physical_reproduction_success`。"W-flow 跑完了" = `pipeline_completed`，**不等于**物理复现成功。这是 Degiron v1/v2 血的教训（v1 的 `surrogate_fallback`、v2 的 `diagnostic_only` 都不是复现成功）在 Mie 侧的对应纪律。

### C.4 Layer 3 偏差的四类来源：怎么区分

论文图对不上时，**不能一句"数值误差"糊过去**，必须归到以下四类之一（决定下一步动作完全不同）：

| 偏差来源 | 特征信号 | 怎么确认 | 下一步动作 |
|---|---|---|---|
| **参数缺失** | 论文没给全某参数（如具体 $n_{\max}$、介质 $\varepsilon_d$、Drude 阻尼 $\gamma$），你猜了一个 | 扫参数：换合理范围能对上论文 | 回 Gate 1，或在报告注明"论文未给 X，取值 Y"，标 `partial_physical_match` |
| **模型简化** | 你用了论文没用的近似（准静态代替完整 Mie、忽略基底、CDA 忽略多极） | 换更完整模型偏差缩小 | 记录为已知简化，若无法去除则不得标 `physical_reproduction_success` |
| **数值错误** | Layer 1/2 本应过却没过，或曲线形状根本错 | 回 Layer 1/2 复查；对教材核公式（Gate 3） | 回 step 04 修代码，**这是唯一"我们的错"、必须修** |
| **论文本身不可复现** | 参数自洽、模型完整、公式对教材核过，仍系统性偏离；或论文图内部矛盾 | 交叉另一篇/教材；WoS 查是否有勘误/后续质疑 | 报告如实写"论文疑不可复现"，标 `partial_physical_match` 并留证据，**不是我们的失败** |

**判定顺序**：先确认不是"数值错误"（Layer 1/2 过 + 公式对教材核过），再依次排"参数缺失""模型简化"，最后才敢说"论文不可复现"。顺序颠倒会把自己的 bug 甩锅给论文。

---

## 附：本手册的诚实边界

- 全文是**执行计划**，SEPR 侧 W-flow + verifier + benchmark **尚未真跑过任何一篇**。第一篇 Akimov 跑通前，A/B/C 三块都是预期。
- 阶段 3 缺 PDF、`Li_J_OE2010.pdf` 是坏文件，这两个是启动前要处理的已知阻塞点。
- 预制 verifier 脚本（`optics-mie-reproduction/scripts/check_*.py`）在 verification.md 里被引用为"已存在"，实际跑前需确认脚本落地且能 import `reproduction_test/mie/code/`。
- 本手册若与 FINAL 计划冲突，以 FINAL 计划为准（它是基准，本手册是 companion）。
