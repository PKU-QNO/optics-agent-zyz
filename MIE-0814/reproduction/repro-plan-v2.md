# mie-f 数值复现计划 v2（Alaee 2018 Fig.1–3 + Grahn 2012 验证）

> 版本：2026-08-03 · 计划主文件 · 人类与 agent 通用
> 目标论文：Alaee 2018（`papers/mie-f/` 讲义 §9–§12 已推完理论）
> 执行框架：参考 `self-evo-paper-repro` 的 main-agent/sub-agent 编排 + 3 层物理验证
> 本文档是**权威路线图**；各步详细规范见子目录。

---

## 0. 文档定位与阅读顺序

| 文档 | 用途 |
|------|------|
| `repro-plan-v2.md`（本文件） | 总计划：目标、流程、公式、验证、路径 |
| `formalization/` | 每 case 的参数 yaml（物理形式化，gate ② 停点） |
| `notes/` | 每 case 的推导笔记（公式来源 + 推导，gate ③ 停点） |
| `code/` | 每 case 的 Python 实现（含 tests） |
| `verifiers/` | 3 层物理验证脚本 |
| `data/` | 材料数据 CSV + benchmark.yaml |
| `figs/` | 复现图 + 论文图对比图 |
| `worklog/` | 逐日执行日志 |
| `sub-report/` | 子 agent 报告落盘区 |

**启动动作**：新上下文开工第一件事读 `WORK_LOG.md`（`papers/mie-f/` 下）+ 本文件；继续某 case 再读 `worklog/00-index.md`。

---

## 1. 目标与成功标准

### 1.1 复现对象

复现 **Alaee 2018 的 Fig.1、Fig.2、Fig.3**，并同时验证 **Grahn 2012 的散射电流→多极矩→a_E/a_M 映射**数值正确。

### 1.2 成功标准（result_class 上限）

- **`physical_reproduction_success`** 仅在以下全部满足时可用：
  1. 3 层验证全过（硬约束 / 极限退化 / 论文图量化）
  2. 论文图量化：`RMSE`、共振峰位置误差、Q 因子相对误差均落在容忍带内
  3. 4 个人工 gate 全部通过
- 任何一层 fail → 降级为 `diagnostic_only` 或 `partial_physical_match`，**不得向上包装**。

---

## 2. 工作流程（对接 self-evo-paper-repro 11 步，裁剪 + 按图多轮循环）

> 参考：`self-evo-paper-repro/.claude/skills/main-agent/SKILL.md` 的 11 步 workflow。
> 本任务不需要 COMSOL 全流程（Fig.1/2 的独立球用纯 Python）。

### 2.0 核心结构：按图多轮循环（不是线性跑一次）

**每个复现目标（图）单独走一轮完整 7 步循环**，多轮之间独立、各自累积经验：

```
┌─ 第 1 轮：Fig.1（介电球散射截面）─→ 完成、验证、报告
│
├─ 第 2 轮：Fig.2（多极分解）─────→ 复用 Fig.1 的 mie_theory.py
│
├─ 第 3 轮：Grahn 映射验证 ────────→ 复用 Fig.1/2 的 code，独立验证 a_E/a_M
│
└─ 第 4 轮（可选，延后）：Fig.3 Fano → 需求解器或降级，单独决策
```

每轮内部仍走 7 步；轮与轮之间共享 `code/` 的公共模块（mie_theory、materials），
但每轮有自己的 `formalization/`、`notes/`、`verifiers/`、报告，不混用。
**一轮的经验（踩坑、公式核对结论）沉淀进 `worklog/`，供下一轮直接复用**，避免重复踩坑。

### 2.1 单轮内的 7 步

| 步 | 名 | 类型 | 一句话 |
|----|----|------|--------|
| 01 | pdf_preprocessing | agent→script | 从 Alaee 2018 / Grahn 2012 PDF 提取参数、公式、图数据 |
| 02 | formalization | agent | 确认参数/单位，写 `formalization/<fig>.yaml` |
| 03 | theory_notes | agent | 写 `notes/<fig>.md`：公式来源、推导、与讲义 §9–§12 对标 |
| 04 | implementation | agent | 写 `code/<fig>.py` + `tests/test_<fig>.py`（TDD：物理约束先硬编码） |
| 05 | run_and_monitor | agent→script | 运行 + 收集数据 |
| 06 | physical_verification | agent→script | 3 层验证（硬约束→极限→论文图量化） |
| 07 | analysis_and_report | agent | 归因 + 双报告 + 记忆 |

**每轮开头**：先读上一轮的 `worklog/` 经验 → 决定本轮复用 vs 新建。

### 2.2 baseline 基准（新增，防"自己验证自己"）

在写任何复现代码前，**先实现一个独立的最小 Mie 基准** `code/baseline_mie.py`：
直接用 `scipy.special` 直算 a_n/b_n + C_sca/C_ext/C_abs（不依赖复现代码的递推/多极部分）。

用途：
- Layer1 物理硬约束（能量守恒/光学定理/瑞利/大尺寸）先在 baseline 上跑通，**证明 verifier 脚本本身正确**
- 复现代码跑出的 Mie 结果与 baseline 对比 → 隔离"复现代码 bug" vs "Mie 理论本身"
- **顺序**：baseline 先过 Layer1 → 再跑复现代码 → 复现代码再过 Layer1 → 最后 Layer3 对齐论文

### 2.3 人工 gate（4 个，agent 自由跑、gate 必须停）

| gate | 触发点 | 用户核对内容 |
|------|--------|-------------|
| ① 参数 gate | step 02 末 | 参数、单位、范围（介电球 ε=6.25 (n=2.5)？λ 范围？） |
| ② spec gate | step 02 末（formalization 后） | 物理形式化 spec 与论文物理问题一致 |
| ③ 公式 gate | step 04/05 末 | Mie 系数 a_n,b_n 对着 B&H 教材核，不只看综述 |
| ④ 误差 gate | step 07 末 | 看量化误差数字，不接受"看起来一致" |

> 每轮循环内 4 个 gate 都要停。**第二轮起可跳过已确认的 gate**（如 Fig.1 已确认参数 → Fig.2 参数 gate 可快速带过），但要记录"为什么跳过"。

### 2.4 执行方式（用户拍板，2026-08-03）

| 任务类型 | 执行方 |
|----------|--------|
| 多模态（读论文图/图表数据点） | **codex**（多模态能力） |
| 普通写代码 | **Claude 内置子 agent**（general-purpose/Explore） |
| 高能力计划/验证/对抗审查 | **用户开 claude-opus 独立对话**（Claude 只落盘 prompt + 给路径） |
| 物理判断、归因、gate 裁决 | **Claude 主循环**（保留判断层） |

> **prompt 按需写**：不预写所有审查 prompt。到具体时机（需要核对某公式、审查某验证结果）时，Claude 针对性写一条 prompt 落盘 `opus-prompts/`，给路径让用户去发 opus/kimi 独立对话。

### 2.5 blocker 防护

同一步重跑 5 轮不通过 → 停、标 blocked、写失败报告；重跑必须带新证据/新假设；case 超限（wall-clock 4h / spawn 20）→ 停、问用户。**一轮 fail 不阻塞下一轮**——每轮独立验收。

### 2.6 计算平台策略（用户拍板，2026-08-03）

- **COMSOL = 备选项**（Fig.3 Fano 用，或 Fig.1/2 交叉验证用）。链路可行性由子 agent 探索中（结论将落 `sub-report/explore-comsol-magnus.md`），**落盘即备查，不阻塞主线**。
- **Gustation/Magnus = 远程云计算平台**：大计算量 Python 任务（精细波长扫描、密集网格多极积分等）可提交到 Gustation 上跑，避免本地强行算。连接与提交方式（magnus SDK request vs ssh 直连）在 COMSOL 探索结论中一并确认。
- 主线 Fig.1/2 先本地跑（计算量预计可控）；若某步本地跑不动 → 切 Gustation。

---

## 3. 子 agent 编排（如何用）

### 3.1 角色

- **主 agent（Claude）** = 编排者。不亲自做隔离活（写码/跑脚本/读图），只做：
  - 读本计划 + 读子 agent 报告
  - spawn 子 agent（拼完整指令）
  - 校验子报告 8 字段（含"决策性回答"）
  - 在 4 个 gate 处停、问用户
  - 第 07 步写主 agent 总结报告 + 更新 memento
- **子 agent** = 执行者。spawn 时**必须明确告知"你是子 agent"**；读 `sub-agent` skill；报告写 `sub-report/`；可 spawn 第 3 层叶子 subsubagent（只做单点小活）。

### 3.2 spawn 指令拼接模板（主 agent 每次 spawn 用）

```
你是 sub-agent，不是编排者。
step=<步号>  paper=alaee2018  case=<fig1|fig2|fig3>  timestamp=<ts>
task_scope=<该步只做 X，不决定 workflow 走向>
input_paths=<...>  output_paths=<...>
先做：读 repro-plan-v2.md 相关节；搜索 memento（查询词含 alaee2018/case 名/关键物理量）。
执行：按本步要求完成，产物落盘。
禁止：写 .result/；改正式 skill；跳过 verifier；把 fallback/diagnostic 当成功；删沙箱草稿。
报告：写 sub-report/<paper>-<case>-<step>-<ts>.md，含 8 字段固定头、uncertainty、missing_evidence、result_class、provenance 五字段。
结束：先 memory_dedup_check，再按需 memory_store/decisions_log/pitfalls_log。
```

### 3.3 并发策略

- **Fig.1 与 Fig.2 独立**（都是介电球，但分析目标不同）→ 可并发 spawn 2 个子 agent，各写各的报告。
- **Fig.3（金纳米盘耦合）依赖 COMSOL 场** → 与 Fig.1/2 串行；先确认用户是否本机可跑 COMSOL，否则降级为 `surrogate_fallback`（孤立盘近似）并明确标注。

### 3.4 复述纪律（防转述漂移）

主 agent 向用户转述任何 verifier 数字 / gate 裁决时，**必须现场重开原始文件核对**，不得凭记忆转述。格式：先点信息来源文件，再紧贴原文复述量化数值。

---

## 4. 产物与过程文件路径（完整约定）

```
papers/mie-f/reproduction/
├── repro-plan-v2.md          ← 本文件（权威路线图）
├── WORK_LOG.md               ← 全局执行日志（追加式，不删减）
├── formalization/
│   └── alaee2018-fig1.yaml   ← gate② 停点
│   └── alaee2018-fig2.yaml
│   └── alaee2018-fig3.yaml
├── notes/
│   ├── alaee2018-mie-coeff.md    ← a_n,b_n 对照 B&H Ch.4（gate③ 停点）
│   ├── alaee2018-table2-impl.md  ← 表2 积分实现推导
│   └── grahn-mapping.md          ← 散射电流→多极矩→a_E/a_M
├── code/
│   ├── baseline_mie.py           ← 独立最小 Mie 基准（scipy 直算，Layer1 锚点，先跑通）
│   ├── mie_theory.py             ← Mie 系数 + C_ext/C_sca/C_abs + 内部场
│   ├── multipole_moments.py      ← 表1/表2 精确多极矩体积分
│   ├── multipole_approx.py       ← 表1 近似多极矩（对比用）
│   ├── scattering.py             ← 从多极矩算 a_E/a_M + 散射截面
│   ├── materials.py              ← 材料介电函数（含 JC 数据加载+插值）
│   ├── params.py                 ← 共享参数
│   └── plot_fig1.py / plot_fig2.py / plot_fig3.py
├── tests/
│   ├── test_mie.py               ← 能量守恒、瑞利极限、大尺寸极限
│   └── test_multipole.py         ← 小 x 退化、暗模式、对称性
├── verifiers/                    ← 3 层验证脚本（预制）
│   ├── check_energy_conservation.py
│   ├── check_rayleigh_limit.py
│   ├── check_large_size_limit.py
│   ├── check_optical_theorem.py
│   ├── check_degeneracy.py       ← 表2→表1 退化、j_l/(kr)^l 极限
│   └── compare_paper_fig.py      ← 论文图数据点 vs 我们的（RMSE/峰值/Q因子）
├── data/
│   ├── jc_Au.csv                 ← Johnson & Christy 金数据（本地 Zotero 提取）
│   ├── jc_Ag.csv                 ← 银（可选）
│   └── benchmark.yaml            ← 复现基准表（追加式，永不覆盖）
├── figs/
│   ├── fig1_sca_<case>.png
│   ├── fig2_decomp_<case>.png
│   ├── fig3_fano_<case>.png
│   └── compare_<case>.png        ← 论文 vs 我们 对比图
├── worklog/
│   └── 00-index.md               ← 逐日日志入口
└── sub-report/                   ← 子 agent 报告
```

**命名规范**：产物文件名带 `{case}` + `{timestamp}`，避免覆盖；`.work` 沙箱与正式产物分离；benchmark.yaml 只追加不覆盖。

---

## 5. 原始数据来源（重要：材料数据已在本地）

| 数据 | 来源 | 状态 |
|------|------|------|
| **金/银/铜复介电函数** | **Johnson & Christy 1972**（Alaee 2018 Ref[38]） | ✅ **已在本地 Zotero**，key `WAEZQ8P3`，含中文摘要 `reference-summaries/Johnson_Christy_1972.md`。**用户无需下载**。需执行：从文字 PDF 提取表格 → `data/jc_Au.csv`（含 ε(λ) 插值函数） |
| 介电球 ε_r | **6.25**（= 2.5²，n=2.5，高折射率；Alaee 2018 Fig.1/2） | 常数，无需外部数据 |
| 金球半径 | 250 nm | 常数 |
| 耦合纳米盘 | a=250nm, t=80nm, g=120nm | 常数 |
| ε_host | 1（air） | 常数 |
| Mie 系数公式 | Bohren & Huffman Ch.4 | 本地扫描 PDF，key `S9DSIDNN` |
| 论文图数据点 | Alaee 2018 文字 PDF | 本地 Zotero，key `TWGIRDAT` |

**结论**：**不需要下载任何新论文**。JC 数据本机已有，唯一工作是把 PDF 里的数据表转成 CSV（执行时用 pdf-mcp + vision-mcp 读，人工核对几个已知点）。

---

## 6. 理论公式与最终计算公式

> 完整推导见 `vector-multipole-derivation` 讲义 §9–§12（75+8 页，已双审查）。此处只列**编码要用的最终形式**。

### 6.1 Mie 理论（参考基准，B&H Ch.4 约定）

尺寸参数与折射率：
$$
x = ka = \frac{2\pi a}{\lambda}\sqrt{\epsilon_{r,d}},\qquad m = \frac{\sqrt{\epsilon_r}}{\sqrt{\epsilon_{r,d}}}
$$

Mie 系数（B&H 4.61–4.62，**a_n=电多极/TM，b_n=磁多极/TE**）：
$$
a_n = \frac{m\psi_n(mx)\psi'_n(x) - \psi_n(x)\psi'_n(mx)}{m\psi_n(mx)\xi'_n(x) - \xi_n(x)\psi'_n(mx)}
$$
$$
b_n = \frac{\psi_n(mx)\psi'_n(x) - m\psi_n(x)\psi'_n(mx)}{\psi_n(mx)\xi'_n(x) - m\xi_n(x)\psi'_n(mx)}
$$
其中 Riccati–Bessel $\psi_n(\rho)=\rho j_n(\rho)$，$\xi_n(\rho)=\rho h_n^{(1)}(\rho)$。

截面：
$$
C_{\text{sca}} = \frac{2\pi}{k^2}\sum_{n=1}^{\infty}(2n+1)\bigl(|a_n|^2+|b_n|^2\bigr),\qquad
C_{\text{ext}} = \frac{2\pi}{k^2}\sum_{n=1}^{\infty}(2n+1)\,\mathrm{Re}(a_n+b_n)
$$
$$
C_{\text{abs}} = C_{\text{ext}} - C_{\text{sca}}
$$

**内部场**（算 J_S 必需）：球内电场（B&H 4.53–4.54 内部场系数 c_n, d_n），用 $j_n$（正则）展开。

### 6.2 散射电流（Grahn Eq.6）

$$
\mathbf{J}_S(\mathbf{r}) = -i\omega\epsilon_0\bigl(\epsilon_r(\mathbf{r}) - \epsilon_{r,d}\bigr)\mathbf{E}(\mathbf{r})
$$
只在粒子内部非零；$\mathbf{E}$ = 总场（孤立球 = 入射 + 散射，即 Mie 内部场解析解）。

### 6.3 精确多极矩（Alaee 表 2，讲义 §11）

**ED**（电偶极）：
$$
p_\alpha = -\frac{1}{i\omega}\Bigl\{\int J_\alpha\,j_0(kr)\,d^3r
  + \frac{k^2}{2}\int\bigl[3(\mathbf{r}\cdot\mathbf{J})r_\alpha - r^2J_\alpha\bigr]\frac{j_2(kr)}{(kr)^2}\,d^3r\Bigr\}
$$

**MD**（磁偶极）：
$$
m_\alpha = \frac32\int(\mathbf{r}\times\mathbf{J})_\alpha\,\frac{j_1(kr)}{kr}\,d^3r
$$

**EQ**（电四极）：
$$
Q^e_{\alpha\beta} = -\frac{3}{i\omega}\Bigl\{
  \int\bigl[3(r_\beta J_\alpha + r_\alpha J_\beta) - 2(\mathbf{r}\cdot\mathbf{J})\delta_{\alpha\beta}\bigr]\frac{j_1(kr)}{kr}\,d^3r
  + 2k^2\int\bigl[5r_\alpha r_\beta(\mathbf{r}\cdot\mathbf{J}) - (r_\alpha J_\beta + r_\beta J_\alpha)r^2 - r^2(\mathbf{r}\cdot\mathbf{J})\delta_{\alpha\beta}\bigr]\frac{j_3(kr)}{(kr)^3}\,d^3r
\Bigr\}
$$

**MQ**（磁四极）：
$$
Q^m_{\alpha\beta} = 15\int\bigl\{r_\alpha(\mathbf{r}\times\mathbf{J})_\beta + r_\beta(\mathbf{r}\times\mathbf{J})_\alpha\bigr\}\frac{j_2(kr)}{(kr)^2}\,d^3r
$$

### 6.4 近似多极矩（Alaee 表 1，讲义 §10，退化基准）

用 $kr\to0$ 替换：$1\to j_0$、$\tfrac13\to\tfrac{j_1}{kr}$、$\tfrac1{15}\to\tfrac{j_2}{(kr)^2}$、$\tfrac1{105}\to\tfrac{j_3}{(kr)^3}$：
$$
p_\alpha = -\frac{1}{i\omega}\int J_\alpha\,d^3r - \frac{k^2}{10i\omega}\int\bigl[(\mathbf{r}\cdot\mathbf{J})r_\alpha - 2r^2J_\alpha\bigr]d^3r
$$
$$
m_\alpha = \frac12\int(\mathbf{r}\times\mathbf{J})_\alpha\,d^3r
$$

### 6.5 多极矩 → 散射系数 a_E/a_M（Grahn 映射，讲义 §8）

$$
a_E(1,0) = \sqrt{2}C_1 p_z + 7\sqrt{2}C_3[\cdots],\quad
a_M(1,0) = 5\sqrt{2}iC_2(-Q_{xy}+Q_{yx})
$$
$$
C_1 = -\frac{ik^3}{6\pi\epsilon E_0},\quad
C_2 = -\frac{k^4}{60\pi\epsilon E_0},\quad
C_3 = -\frac{ik^5}{210\pi\epsilon E_0}
$$

### 6.6 散射截面（统一，讲义 §12）

**从多极矩出发**（Alaee Eq.1 形式，**量纲自洽版**，见讲义 §12 noteworthy 勘误）：
$$
C_{\text{sca}} = \frac{k^4}{6\pi\epsilon_0^2|\mathbf{E}_0|^2}\Bigl[
  \sum_\alpha\Bigl(|p_\alpha|^2 + \frac{|m_\alpha|^2}{c^2}\Bigr)
  + \frac{1}{120}\sum_{\alpha\beta}\Bigl(
    |kQ^e_{\alpha\beta}|^2 + \frac{|kQ^m_{\alpha\beta}|^2}{c^2}\Bigr) + \cdots
\Bigr]
$$

> **⚠️ 系数勘误（opus 审查 Y1）**：磁偶极项 `|m|²/c²`（**不是** `/c`，量纲自洽）；四极系数 `1/120`（**不是** `k²/30`，`|kQ|²=k²|Q|²`）。这两处分别对应讲义 §12 早期 typo 与计划 §6.6 早期笔误，现已统一为量纲自洽版。

**从 a_E/a_M 出发**（Grahn Eq.20 形式）：
$$
C_{\text{sca}} = \frac{\pi}{k^2}\sum_{l,m}(2l+1)\bigl(|a_E(l,m)|^2 + |a_M(l,m)|^2\bigr)
$$

> **⚠️ m 求和（opus 审查 Y3）**：Grahn 公式的求和是**对 m 全求和**（偶极 $m=\pm1$、四极 $m=\pm1,\pm2$）。球体下 $\sum_{m=\pm1}(|a_E|^2+|a_M|^2)=2(|a_l|^2+|b_l|^2)$ 恰好补偿 Mie 的 $\pi$ vs $2\pi$ 因子。漏掉 m 求和或只取一个 m → 因子 2 错误。
>
> **两条路径应给同一结果** —— 这本身就是最强的交叉验证（能自动抓 c 幂次、a/b 标签、系数错），前提是 R2 的桥梁修好（见 §6.7）。

### 6.7 opus 审查专项（R2/Y2/Y4/Y5/Y6/Y7/Y8/Y9/Y10，2026-08-04）

> 完整审查见 `opus-prompts/01-plan-adversarial-review-RESULT.md`，处理见 `01-review-triaged.md`。

**R2（Grahn 轮的 Q 是电流矩，非对称 Q^e）——启动 Grahn 轮前必须落实**
- Grahn 映射（§6.5）里的 $Q$ 是**电流矩** $M^{(2)}_{\alpha\beta}=\frac{i}{\omega}\int J_\alpha r_\beta\,d^3r$（**不对称**），不是表2 的对称无迹 $Q^e_{\alpha\beta}$。
- 反例：$a_M(1,0)=5\sqrt2\,iC_2(-Q_{xy}+Q_{yx})$ 里 $-Q_{xy}+Q_{yx}$ 是**反对称组合**，若把对称 $Q^e$ 代入恒等于 0，磁偶极贡献凭空消失。
- **实施**：`scattering.py` 显式区分 `M2[a,b]=(1j/ω)∫J_a·r_b`（喂 Grahn 映射）与 `Qe_sym[a,b]`（喂 Alaee C_sca）；`notes/grahn-mapping.md` 补张量分解换算（对称无迹→Q^e、反对称→m、迹→暗，讲义 §8 L85-110 已给全）；双路径验证前先单元测试"两套多极矩定义能相互换算"。

**Y2（m=±1 分量）——Grahn 轮前落实，Fig.1/2 不阻塞**
- x 偏振平面波只激发 $m=\pm1$。计划 §6.5 只列了 $m=0$（对 x 偏振贡献为零），直接用会算出全零。
- 讲义 §8 L230-283 已给全 $a_E(1,\pm1),a_M(1,\pm1),a_E(2,\pm2),a_E(2,\pm1),a_E(2,0)$；磁四极 $a_M(2,m)$ 讲义没给，需查 Grahn 2012 附录 A。

**Y4（C1/C2/C3 的 ε 是 host）**
- $C_1=-\frac{ik^3}{6\pi\epsilon E_0}$ 等里的 $\epsilon$ = **host** $\epsilon_0\epsilon_{r,d}$。air host → $\epsilon=\epsilon_0$。与 §6.2 的 $J_S$ 定义保持一致。

**Y5/Y6（baseline 不完备 + 约定错误传染）**
- baseline_mie.py 抓不到 $a_n\leftrightarrow b_n$ 标签互换（能量守恒对称），也不覆盖多极矩体积分。
- **补两件事**：①独立的解析多极矩基准（已知电流分布解析矩 vs 数值积分，如均匀极化小球/纯磁偶极环流）；②**per-multipole 峰位验证提前到 Fig.1 轮**（电偶极峰位≠磁偶极峰位），把 gate③ 核对标准从"总截面对齐"升级为"per-multipole 分量对齐"，共享 mie_theory 在第一轮就被钉死。

**Y7（暗模式是构造性测试）**
- 孤立球在 x 偏振平面波下内部场有明确偏振方向性，不会自然产生球对称四极子电流。暗模式验证需**人为构造**迹型电流分布（$\mathbf{J}\propto f(r)\hat{r}$）作单元测试，喂多极矩→C_sca 代码，验证输出为零。不是从球 Mie 场提取。

**Y8（光学定理独立约束）**
- $S(0)$ 若用同一套 $a_n,b_n$ 算 → 与 $C_{ext}$ 公式恒等，光学定理成自我一致。需从**角分辨散射振幅**（$S_1(\theta),S_2(\theta)$ 在 $\theta=0$）独立算 $S(0)$ 再对比。

**Y9（内部场系数 c_n/d_n）**
- 内部场错则所有多极矩全错。B&H 内部场系数（分母差一个 m 位置）：分子 $m\psi_n(x)\xi'_n(x)-m\xi_n(x)\psi'_n(x)$，分母 $c_n$: $\psi_n(mx)\xi'_n(x)-m\xi_n(x)\psi'_n(mx)$，$d_n$: $m\psi_n(mx)\xi'_n(x)-\xi_n(x)\psi'_n(mx)$。**gate③ 必须对 B&H 原书核，不得凭记忆定稿**。

**Y10（Fig.2 容忍带收紧）**
- 原文"表2 与 Mie indistinguishable up to numerical noise"（误差 <0.1%）。Fig.2 的 per-multipole 曲线容忍带**收紧到 <1%**（理想 <0.1%）；Fig.1 的"x≈0.75 误差>100%"要**定量复现**（不只符号一致）。

**G 系列（改进项，实现时纳入）**
- G1：$kr<10^{-4}$ 时 $j_l/(kr)^l$ 直接用 Taylor 首项 $1/(2l+1)!!\cdot(1-(kr)^2/[2(2l+3)])$，避免精度损失。
- G2：网格加倍收敛测试（相对变化 $<$tol）；$r$ 向随 $x$ 增大加密（内部场 $j_n(mx\cdot r/a)$ 高 $x$ 振荡）。
- G3：$n_{max}=x+4x^{1/3}+2$（Wiscombe）；per-multipole 只需 $l\le2$，别混淆两个截断。
- G4：JC 数据按 eV 列表，需 λ↔eV 换算；Au 550nm 抽查点强制核对。

---

## 7. 数值计算手段

| 项 | 手段 |
|----|------|
| 球 Bessel / Hankel | `scipy.special.spherical_jn` / `spherical_yn`，`spherical_yn` 与 `spherical_jn` 组合出 $h_n^{(1)}$。**用 scipy，不自己写**（self-evo 经验：信任 scipy.special，不信 AI 生成的特殊函数） |
| 勒让德 / 球谐 | `scipy.special.lpmv`、`sph_harm` |
| 体积分（多极矩） | `scipy.integrate`：球坐标 `(r,θ,φ)` 三重积分；$r\to0$ 处 `j_l/(kr)^l→1/(2l+1)!!` 有限，用极限值替换避免除零 |
| Mie 系数递推 | B&H 的 Richmond 向下递推；或用 scipy 的 `spherical_*` 直接算低阶验证，高阶用递推 |
| 材料插值 | JC 数据 `scipy.interpolate.interp1d`（三次样条），在 ε(λ) 上插值 |
| 场求解（Fig.1/2） | 孤立球 = **解析 Mie 内部场**，无需数值求解器 |
| 场求解（Fig.3） | 需 COMSOL/FDTD；**若本机不可用 → 降级**（孤立盘或 CDA），标 `surrogate_fallback` |
| 图对比 | matplotlib；论文图数据点从 PDF 渲染 + vision-mcp 提取，存 `data/` |

---

## 8. 验证体系（3 层，self-evo 核心纪律）

> 核心原则：**永远不靠"看起来像"判断成功**。用 3 层，由易到难。

### Layer 1：物理硬约束（参数无关，AI 无法造假）

| 检查 | 公式 | 适用 |
|------|------|------|
| 能量守恒 | $C_{\text{ext}} = C_{\text{sca}} + C_{\text{abs}}$（1e-10 内） | 所有 case |
| 无吸收零吸收 | $\mathrm{Im}(\epsilon_r)=0 \Rightarrow C_{\text{abs}}=0$ | 介电球（ε=6.25 实） |
| 光学定理 | $C_{\text{ext}} = \frac{4\pi}{k}\,\mathrm{Im}\,S(0)$ | 所有 case |
| 瑞利极限 | 小 $x$：$Q_{\text{sca}}\propto x^4$（log-log 斜率 4） | 介电球 |
| 大尺寸极限 | $x\to\infty$：$Q_{\text{ext}}\to 2$ | 介电球 |
| 球对称 | 各向同性球散射与 φ 无关 | 所有 case |

### Layer 2：极限退化 / 已知极限

| 检查 | 内容 |
|------|------|
| 表2→表1 | $x\ll1$ 时精确矩退化为近似矩（<1%） |
| 小宗量 j_l | $j_l/(kr)^l \to 1/(2l+1)!!$ 极限正确 |
| 暗模式 | 球对称四极子对 C_sca 零贡献 |
| 准静态 LSPR | 小 x 金球 $\mathrm{Re}(\epsilon)\approx-2\epsilon_d$ 处共振 |
| 偶极主导 | 小 x 时高阶多极贡献 → 0 |

### Layer 3：论文图量化对比

| 指标 | 定义 | 容忍 |
|------|------|------|
| RMSE | 散射截面曲线均方根误差 | 用户定（默认目标 <5% 或绝对差<某值） |
| 共振峰位置误差 | 论文峰 λ vs 我们的峰 λ | <2nm（或用户定） |
| Q 因子相对误差 | $\Delta Q/Q$ | <10% |
| 误差放大点 | Alaee 报告"近似>100% 误差"的 $x\approx0.75$ 处，精确 vs 近似差异复现 | 定性符号一致 |

**对比数据来源**：Alaee 2018 文字 PDF → pdf-mcp 读图 → vision-mcp 提取数据点 → `data/alaee_fig1_points.csv`。子 agent 读图时用 `pdf_render_pages`（高 DPI）保证分辨率。

---

## 9. 报告呈现方式

1. **benchmark.yaml**（机器可读）：每 case 一条，含参数、期望值、容忍、两方一致状态。
2. **复现图**（`figs/`）：我们的结果（实线）+ 论文数据点（散点）同图对比。
3. **主报告**（`REPORT.md`）：量化数字（RMSE/峰位/Q 因子/硬约束 pass/fail），不含"看起来一致"。
4. **result_class** 判定写进报告头部，缺证据写更低等级并标 `missing_evidence`。

---

## 10. 人工 gate 与 result_class（沿用 SEPR 硬规则）

**result_class 七级**：`not_run` / `pipeline_completed` / `simulation_completed` / `diagnostic_only` / `surrogate_fallback` / `partial_physical_match` / `physical_reproduction_success`。

- 只要没真跑仿真/数值验证 → 最高 `pipeline_completed`
- 只要仿真完成但没物理判断 → 最高 `simulation_completed`
- 只要任一 Layer1 硬约束失败 → 最高 `diagnostic_only`
- 只要用代理/简化 → 必须 `surrogate_fallback`（如 Fig.3 无 COMSOL 时）
- 只有硬约束+极限+论文图量化+4 gate 全过 → 才允许 `physical_reproduction_success`

**provenance 五字段**（每条记忆/报告）：`source_artifact` / `evidence_type` / `timestamp_version` / `scope_applicability` / `confidence_result_class`；未知写 `unknown`/`pending` 不省略。

---

## 11. 风险、blocker 与降级

| 风险 | 影响 | 对策 |
|------|------|------|
| Fig.3 需 COMSOL，本机不可用 | Fig.3 无法完整复现 | 降级：孤立盘近似或 CDA，标 `surrogate_fallback`；Fig.1/2 不受影响 |
| JC 数据表提取困难（PDF 排版） | 材料数据不准 | vision-mcp 读图核对 + 人工抽查已知点（如 Au 在 550nm ε≈-8.9+1.5i） |
| Mie 系数 a_n/b_n 标反 | 全盘错误 | gate③ 对 B&H 教材核；电/磁标签用 §2 已修约定（a_n=电↔a_E） |
| 多极矩积分除零（r=0） | 数值 NaN | 用 $j_l/(kr)^l$ 极限值 |
| x 增大需高阶 l 收敛 | 截断误差 | $n_{\max}\approx x+4x^{1/3}+2$（Wiscombe） |
| 子 agent 转述漂移 | 决策错误 | 复述纪律：重开原文件核对 |

---

## 12. 执行顺序检查单

- [ ] gate① 前：pdf 预读 Alaee Fig.1–3 + Grahn 关键公式（step01）
- [ ] 参数确认：介电球 ε=6.25 (n=2.5)、金球 250nm、盘 a=250/t=80/g=120、ε_host=1
- [ ] gate① 用户核对参数
- [ ] formalization yaml ×3（step02）
- [ ] gate② 用户核对 spec
- [ ] notes 推导 ×3（step03）
- [ ] 实现 code + tests（step04）
- [ ] gate③ 用户核对 a_n,b_n vs B&H
- [ ] 运行 + 3 层验证（step05–06）
- [ ] 论文图量化对比（Layer3）
- [ ] gate④ 用户看误差数字
- [ ] REPORT.md + benchmark.yaml + memento 记忆
