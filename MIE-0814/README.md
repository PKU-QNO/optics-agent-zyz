# MIE-0814：电磁多极展开的理论推导与数值复现

本目录是电磁多极展开（multipole expansion）理论推导与数值复现的公开交付包，时间 2026-08-14。

## 复现的论文

| 论文 | 核心内容 |
|---|---|
| Grahn 2012, *New J. Phys.* 14 093033 | 电流多极矩到散射场多极系数的映射关系（Eq.(1)–(16)） |
| Fernandez-Corbaton 2015, *Opt. Express* 23 33044 | 局域电流分布的精确偶极矩 |
| Fernandez-Corbaton 2017, *Sci. Rep.* 7 7527 | toroidal 多极非独立性的严格证明 |
| Alaee 2018, *Opt. Commun.* 407 17 | 超越长波近似的精确多极展开（Table 1/Table 2） |

## 目录结构

```
MIE-0814/
├── reports/                           # 六个 PDF（可直接阅读）
│   ├── professor-report.pdf           #   给教授的汇报 v1（正文 7 页 + 附录 4 页）
│   ├── professor-report-v2.pdf        #   给教授的汇报 v2（补公式+示意图+复现图对比，14 页）
│   ├── agent-usage-report.pdf         #   给 LLM 学长的 agent 使用报告（10 页）
│   ├── technical-manual.pdf           #   备查技术手册（含 Q&A）
│   ├── vector-multipole-derivation.pdf #  理论推导笔记（66 页）
│   └── reproduction-report.pdf        #   完整复现报告（20 页）
├── reproduction/                      # 复现工程
│   ├── code/                          #   核心代码（Mie/Table1/Table2/Grahn/光学定理）
│   ├── tests/                         #   回归测试（能量守恒/光学定理/退化）
│   ├── data/                          #   冻结数值数据（CSV/JSON）
│   ├── formalization/                 #   SEPR 形式化 spec
│   ├── notes/                         #   推导与验收笔记
│   ├── report-final/  report-round1/2/3/  # LaTeX 报告源码
│   └── sub-report/                    #   Grahn 子报告
├── report-professor/                  # 给教授报告的 LaTeX 源码
├── report-technical-manual/           # 备查手册的 LaTeX 源码
├── report-agent-usage/                # agent 使用报告的 LaTeX 源码
├── skills/                            # 10 个可复用 skill（6 自建 + 4 通用）
└── vector-multipole-derivation/       # 理论推导笔记的 LaTeX 源码
```

## 核心结论

- **球体（Fig.1/2）**：Table 2 精确多极矩与 Lorenz–Mie 解析解逐通道对比，四通道最大误差 <0.21%（介电球）/ <0.03%（金球）。
- **Grahn 映射**：双路径映射（长波 5.7e-7、有限核 2.9e-4）+ 逐 m 系数 + 解析 fixture 全部通过。
- **双金盘（Fig.3）**：COMSOL 频域有限元真解谱（ED 主导 + MD/EQ 磁共振）+ 边界元 128G 替代路径。

## 物理验证（为什么相信算对了）

1. **多近似方法对比**：Table 2 体积分 vs Mie 级数、Grahn 双路径 + miepython + 独立远场、FEM(900G) vs BEM(128G)。
2. **极限退化**：Table 2 → Table 1（长波）、Mie → Rayleigh(x⁴)、Q_ext→2。
3. **能量守恒/光学定理**：C_ext=C_sca+C_abs、S(0) 双路、Eq(22)↔Eq(20)、功率闭合 balance=1.0。

## 已知限制

- Fig.3 MD/EQ 网格残差 ~2%（表面场奇异性，Richardson p≈1.3）
- BEM 为 PEC 近似（丢金损耗，MD/EQ 磁共振被抑制）
- Fig.2 严格 UQ 未闭合（读图数据退役后契约缺口）
- 高阶 l>4 未逐阶

## 复现方式

代码用 Python（numpy/scipy），测试入口：

```bash
cd reproduction
python -m pytest tests -q -p no:cacheprovider
```

COMSOL 构建器（双金盘 FEM/BEM）在 `comsol/runtime/cases/alaee2018_fig3/`（本仓库根，非本目录）。

## Skill 沉淀（10 个）

复现结束后把经验提炼为可复用 skill，`skills/` 目录含 10 个（6 自建 + 4 通用），也已上传 Magnus（gustation.phybench.cn 的 skill 库）：

- **paper-reproduction** / **figure-reading** / **comsol-scattering** / **magnus-submit** / **numeric-verification** / **third-party-cross-validation**（自建）
- **adversarial-review** / **transition-wrapup** / **doc-sync** / **grill-me**（通用）

详见 `reports/agent-usage-report.pdf`（给 LLM 学长的 agent 使用报告）。
