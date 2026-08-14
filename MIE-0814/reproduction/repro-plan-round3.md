# mie-f 第 3 轮（Grahn 映射验证）执行计划（v3，审查 12 修订）

> 基于第 1/2 轮经验 + **对抗审查 09/10/11/12（四轮 BLOCKED → 全部接受修订）**。审查结果见 `opus-prompts/09/10/11/12-*-RESULT.md`。
> 权威路线图：`repro-plan-v2.md`（4 轮×7 步 + 4 gate）。本文件只写第 3 轮差异与复用。
> ⚠️ 计划与 spec 同步：formalization/grahn.yaml 是唯一权威（当前 v4）；本计划任何条款与 spec 冲突以 spec 为准（审查 12 🟡13 版本同步）。

## 目标（审查 🔴3 修订：拆成两个验收对象，不再混比）

验证 **Grahn 2012 映射**：散射电流 → 电流矩 M^(l) → a_E/a_M。**两条独立路径**：

### 路径 A（低-kr 张量映射，长波）
Grahn 电流矩 M^(l)（无 Bessel 核）→ 张量分解 → a_E/a_M → C_sca
- **对照**：Alaee Table 1（长波近似）——同一低-kr 域
- **验收**：低-kr 下两者一致（报告截断误差）

### 路径 B（全域 Bessel 核，精确）
Grahn Eq.(13)(14) 直接核积分（含球 Bessel 核 j_l(kr)；实现首选分部积分形式 Eq.(15)(16)）→ a_E/a_M → C_sca
- **对照**：Mie 理论 per-multipole / 远场投影
- **验收**：全域一致（<1%）

> ⚠️ **禁混**：Grahn 无核张量映射 ≠ Alaee Table 2（精确核）。Table 2 精确 Q^e 不得直接喂 Grahn 张量映射（审查 🔴2）。

### 验证目标（审查 09/10/11/12 修订）
1. 路径 A ↔ Table 1（低-kr，**各自对 Mie 真值**——审查 12 🟡10）；路径 B ↔ Mie（全域）
2. **独立路径**：远场 Eq.(3)(4) 投影（独立 VSH + 相位契约）+ miepython（gate 不 skip）+ 解析电流基准（防共同错误）
3. C1/C2/C3 系数：ε 是 **host 绝对介电常数** ε_d=ε₀ε_rd（机器可读）
4. **逐 m 复系数目标**：a_E(l,+1)=−a_l、a_E(l,−1)=+a_l、a_M(l,±1)=−b_l（审查 12 🔴4 相位锁定）
5. **Rayleigh**：完整 Mie 总截面 canonical 斜率 6±0.3（x_alaee log 网格 [0.02,0.2]，observed 6.079——审查 12 🔴3）

## 理论核心（讲义 §8 + Grahn 原文，审查修订）

### 电流矩（Grahn Eq.(27)，讲义 L36-40）
$$M^{(l)} = \frac{i}{(l-1)!\,\omega} \int \mathbf{J}(\mathbf{r})\,\mathbf{r}\cdots\mathbf{r}\,d^3r$$
- l=1：M^(1) = p（电偶极）
- l=2：M^(2) = i/ω ∫ J_α r_β d³r —— **9 分量一般 3×3 原始矩，不对称**（审查 🔴1：讲义 L44 "无迹对称"标签错误，已确认要修）

### 张量分解（M^(2) 四对象，审查 🔴1/🟡4）
实现显式区分四个归一化对象：
- `M2_raw[αβ]` = i/ω ∫J_α r_β（9 分量原始矩）
- `M2_sym_traceless` = ½(M2+M2ᵀ) − ⅓I·trM2（对称无迹 → Q^e 相关，5 维）
- `M2_antisym` = ½(M2−M2ᵀ)（反对称 → 磁偶极 m，3 维对偶）
- `M2_trace` = ⅓I·trM2（迹 → 暗模式，1 维）

### M^(2) ↔ Q^e 换算（审查 🔴2）
$$Q^e = 6\,\mathrm{STF}(M2_{\rm raw}),\quad \mathrm{STF}(M2)=\tfrac12(M2+M2^T)-\tfrac13 I\,\mathrm{tr}M2$$
- **仅长波（无 Bessel 核）成立**；Alaee Table 2 的 Q^e 含 j₁(kr)/(kr)、j₃(kr)/(kr)³，有限 kr 下**不等同**
- spec 写明：Table 2 精确矩禁喂 Grahn 张量映射

### 映射公式（审查 🔴5/🔴4 修订）
- **a_E(1,m) 不是 p-only**：含 7C₃·O 八极修正（Grahn Eq.42–43）；p-only 仅最低阶截断开关
- a_E(2,m) + a_M(1,m) 含 Q；a_M(2,m) 磁四极**原文有**（Grahn 主文 §3.3.4 Eq.44–46 / 译本 grahn2012-chinese.tex:379-392 Eq.26–28），**必须纳入**：
  - a_M(2,±2) = 7C₃[±(−O_xxz+O_yyz+O_zxx−O_zyy) + i(O_xyz+O_yzx−2O_zxy)]
  - a_M(2,±1) = 7C₃[−O_xyy+O_xzz+O_yyx−O_zzx ∓ i(−O_yxx+O_yzz+O_xxy−O_zzy)]
  - a_M(2,0) = 7√6 iC₃(O_xyz−O_yzx)
  - 式号双记录：source_equation（原文 Eq44-46）+ local_equation（译本 Eq26-28）（🟢3）

### m 求和（审查 🟡1）
- **通用**：任意入射全 Σ_{m=−l}^{l}
- **球体简化**：仅居中球、x 偏振、z 传播 → m=±1；因子 2 仅此限定
- 测试锁定双路径：通用全 m + 球体简化；四极 m=0,±2 不静默丢

### C1/C2/C3（审查 🟡2）
- C₁=−ik³/(6πεE₀)、C₂=−k⁴/(60πεE₀)、C₃=−ik⁵/(210πεE₀)
- **ε 是 host 绝对介电常数**：ε_d=ε₀ε_rd；同步 k_d=ω√(μ₀ε_d)、η_d=√(μ₀/ε_d)、J_S=−iω(ε−ε_d)E；host=air 才退化 ε₀

## 复用清单（第 1/2 轮已验证）

| 模块 | 复用 | 说明 |
|------|------|------|
| `code/params.py` | ✅ | ε_r=6.25、x 换算、Wiscombe |
| `code/baseline_mie.py` | ✅ | Mie 系数/截面（+ 独立 Mie 库 miepython 交叉） |
| `code/mie_theory.py` | ✅ | 内部场 c_n/d_n + E_in + J |
| `code/multipole_moments.py` | ✅ | Table 2 精确矩（路径 B 对照 + 独立解析基准参考） |
| `code/multipole_approx.py` | ✅ | Table 1 近似（路径 A 对照） |
| `tests/` | ✅ | 67 tests 保持 pass（回归；skip = 200 点慢扫描） |

新增：
- `code/scattering.py`：M2 四对象 + STF 换算 + Grahn 映射（含 a_M(2,m)）+ C1/C2/C3 + 远场投影 + 双路径 C_sca
- `notes/grahn-mapping.md`：张量分解 + m 求和 + C 系数 host ε + 磁四极收录 + 式号双记录
- `tests/test_grahn.py`

## 7 步执行

| 步 | 动作 | 产物 | gate |
|----|------|------|------|
| 01 | 读 Grahn 关键公式（译本 tex:250-256 全 m + 379-392 磁四极 + 原文 Eq.(13)(14) 核路径 + (15)–(19) 定义） | `notes/grahn-formulas.md` | — |
| 02 | formalization grahn.yaml（SEPR 9 字段 + M2 四对象 + Q^e=6STF 长波限定 + m 域 + ε_d host + 双路径验收 + 容差） | `formalization/grahn.yaml` | **gate② 停** |
| 03 | notes/grahn-mapping.md（推导 + 式号双记录 + 磁四极收录） | `notes/grahn-mapping.md` | — |
| 04 | scattering.py + tests（M2 四对象逐层断言 + STF 长波限定测试 + 独立解析基准 + 远场投影 + 故意错误注入） | `code/scattering.py` | — |
| 05 | run：路径 A ↔ Table 1（低-kr）+ 路径 B ↔ Mie（全域） | `data/grahn_*.csv` | — |
| 06 | 3 层验证（双路径各自验收 + 光学定理 + miepython 交叉 + 网格收敛） | `sub-report/verify-grahn.md` | — |
| 07 | 报告 + gate④ | `report-round3/` | **gate④ 停** |

## gate 计划（审查 🟢2 修订）

- **gate① 跳过**（记录原因）：参数已确认（ε_r=6.25、x_Mie 换算）
- **gate③ 部分跳过**：a_n/b_n/c_n/d_n 已核；但 **Grahn 映射公式（M2 四对象/磁四极/C 系数）是本轮新公式 → gate② 重点核**
- **gate② 重点核**：grahn.yaml（M2 区分、Q^e=6STF 长波限定、双路径拆分、磁四极收录、ε_d host、m 域）
- **gate④ 重点核**：路径 A/B 各自验收量化误差

## 验证硬化（lessons 10/11 + 审查 🟡4/🟡5）

- **M2 四对象逐层测试**（随机复 3×3 张量）：9 分量重构、STF 5 维性质、反对称 3 维对偶 m、迹 1 维暗模；Q^e=6STF 仅长波极限测试；反对称使 a_M(1,m) 非零、迹使 l=2 映射全零
- **独立解析电流基准**（平滑有限支撑，防 δ 不可积）：均匀极化球（验 p，居中 M2=0）、双斑（STF/迹）、环流（反对称 M2→m_z）、上下双环（M3→a_M(2,m)）；每个给闭式 + 数值 + 收敛
- **故意错误注入**：a/b 标签互换、m=0/±1/±2 丢弃、坐标平移、相位约定——测试能抓到
- **独立路径**：远场 Eq.3-4 投影 + miepython（🟡3）
- 光学定理（Y8）+ 网格收敛 + 200 点 + 绝对误差

## 前置修正（gate② 前完成）

1. **讲义 §8 L44**："无迹对称" → "一般 3×3 原始矩（9 分量，不对称）"（审查 🔴1，讲义 bug）
2. **讲义 §12** 残留 |m|²/c（L190 对照表 + L368 速查）→ 改 |m|²/c²（审查 🟡6）
3. **讲义 §8 L293**："附录 A" → "主文 Eq.(44–48)"（审查 🟢1）

## 风险

- 磁四极含 O 八极张量：需要 M3 电流矩（27 分量）——实现量增大；若只做 l≤2 需明确标 range（审查 🔴4）
- 双路径若不一致 → 先查 M2 四对象区分 → 再查 STF 换算域 → 再查 C 系数 ε → 再查 m 求和（归因顺序）
- 讲义 bug（L44 标签）若不修 → M2 错喂 Q^e → 磁偶极消失（R2 反例，test 锁定）

## 图标准（lessons 12，若画图）

- 双路径 C_sca 叠加（路径 A/B + 对照），按多极着色
- 标题 "Grahn mapping reproduction"；近零断线/clip 按 lessons 12
