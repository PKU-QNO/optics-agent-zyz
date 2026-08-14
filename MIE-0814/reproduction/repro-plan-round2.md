# mie-f 第 2 轮（Fig.2 多极分解）执行计划

> 基于第 1 轮 Fig.1 经验（lessons 8-13 + finding-mie-6）。第 1 轮已确认：介电球 ε_r=6.25、x=[0.2,1.0]、Mie 系数/内部场/多极矩代码全部验证。
> 权威路线图：`repro-plan-v2.md`（4 轮×7 步 + 4 gate）。本文件只写第 2 轮差异与复用。

## 目标

复现 **Alaee 2018 Fig.2**：介电球多极分解（ED/MD/EQ/MQ）的散射截面，表2 精确 vs Mie 理论。
验证目标：**表2 与 Mie indistinguishable（<1%）**——这是 Fig.1 已证核心的独立复现（同一物理，不同图）。

> ⚠️ 与 Fig.1 差异：Fig.1 是"表1 vs 表2 vs Mie"（含近似对比）；Fig.2 是"表2 vs Mie"多极分解（精确性验证，Fig.1 中表2 vs Mie 已 <1%，Fig.2 是同样的物理换图呈现）。

## 复用清单（第 1 轮已验证，直接 import）

| 模块 | 复用 | 说明 |
|------|------|------|
| `code/params.py` | ✅ | ε_r=6.25、x 换算、Wiscombe |
| `code/baseline_mie.py` | ✅ | Mie 系数/截面（33 tests 验证） |
| `code/mie_theory.py` | ✅ | 内部场 c_n/d_n + E_in + J |
| `code/multipole_moments.py` | ✅ | 表2 多极矩（Eq.1 解析常数） |
| `code/multipole_approx.py` | ✅ | 表1 近似（Fig.2 可能不用，若只表2 vs Mie） |
| `tests/` | ✅ | 33 tests 保持 pass |

## 7 步执行

| 步 | 动作 | 产物 | gate |
|----|------|------|------|
| 01 | 读 Fig.2 参数（介电球同 ε_r=6.25；确认 Fig.2 是否也是 2a/λ 横轴 + 多极分解输出） | `notes/fig2-parameters.md` | — |
| 02 | formalization fig2.yaml（对齐 SEPR 9 字段） | `formalization/alaee2018-fig2.yaml` | **gate② 停** |
| 03 | notes fig2 推导（复用讲义 §11 表2） | `notes/alaee2018-fig2.md` | — |
| 04 | 复用 code + 可能 plot_fig2.py；无新数值代码则跳过实现 | `code/plot_fig2.py` | — |
| 05 | run 收集数据（若复用则直接读 Fig.1 CSV 或重扫） | `data/fig2_*.csv` | — |
| 06 | 3 层验证（重点：表2 vs Mie <1% + 200 点收敛） | `sub-report/verify-fig2.md` | — |
| 07 | 报告 + gate④ | `report-round2/` | **gate④ 停** |

## gate 跳过（第 1 轮已确认）

- **gate① 跳过**（记录原因）：参数同 Fig.1（ε_r=6.25、x=[0.2,1.0]），图提取参数已在 Fig.1 gate④ 复核过
- **gate③ 跳过**（记录原因）：a_n/b_n/c_n/d_n 已对 B&H 原书核 + miepython 交叉验证
- **gate② 重点核**：Fig.2 spec 输出（多极分解）与论文 Fig.2 物理一致
- **gate④ 重点核**：表2 vs Mie <1%（indistinguishable）

## 图标准（lessons 12）

- 按多极着色 + 线型区分（Mie 实线/表2 虚线）；若只画表2 vs Mie 则无表1 点线
- 普适上限标一次（dipole=3、quadrupole=5）
- 标题 "Fig.2 reproduction"
- 近零断线/clip 标注按 lessons 12

## 验证（lessons 10/11）

- 表2 vs Mie：200 点扫描 + 网格收敛（40/41/80 → 60/61/120）+ 绝对误差 + 分母大小
- 复用代码无回归（33 tests pass）
- 峰位锚点（实测）：ED@0.50/MD@0.385/EQ@0.647/MQ@0.543

## 风险

- Fig.2 若涉及金球（a=250nm, JC 数据）→ 需提取 JC ε(λ)（本地 Zotero WAEZQ8P3），可能阻塞；若 Fig.2 仍是介电球则零依赖
- 复用代码若有 Fig.1 特定假设 → 检查后复用
