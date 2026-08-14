# mie-f 项目现状同步（2026-08-11）— 4 轮复现 workflow 总览

> 目的：快速同步 4 轮理论复现（Fig.1 散射 / Fig.2 多极分解 / Grahn 映射 / Fig.3 Fano）的设计全貌（workflow 级，非细节）。
> **👤 唯一 human 入口 = §8 待你决策清单**（详细在 [00-待决策清单.md](00-待决策清单.md)）——只需看那一节决定，其余读完即可。决策后主副文档自动同步。

## 📑 文档索引

| # | 主题 | 分文档 |
|---|------|--------|
| 0 | **待决策清单（唯一 human 入口）** | [00-待决策清单.md](00-待决策清单.md) |
| 1 | 4 轮复现 workflow（Fig.1/2/Grahn/Fig.3） | [01-四轮复现.md](01-四轮复现.md) |
| 2 | CODEX 任务体系（A1-B19，25 个） | [02-codex任务体系.md](02-codex任务体系.md) |
| 3 | Formalization spec 体系（4 份 SEPR） | [03-formalization体系.md](03-formalization体系.md) |
| 4 | 报告与产物（round1/2/3/final + 测试） | [04-报告与产物.md](04-报告与产物.md) |
| 5 | COMSOL 交叉验证路径（官方 MPH / Java / Magnus） | [05-comsol路径.md](05-comsol路径.md) |
| 6 | 风险清单与已验证/未验证 | [06-风险与验证.md](06-风险与验证.md) |
| 7 | 关键凭据与环境约束 | [07-凭据与环境.md](07-凭据与环境.md) |
| 8 | 数值方法与选型反思（频域 FEM / Mie / FDTD-BEM-DDA 对比） | [08-数值方法.md](08-数值方法.md) |

## 0.5 方向 × 阶段总览（项目全景）

> 阶段图例：🔵 调研 → 📋 计划 → 🟡 实现 → ✅ 已实现 / ⏸ 已推迟（全项目统一）
> ⚠️ `✅ 已实现` ≠ 已接入生产；原型完成 ≠ 已接入主系统

| 方向/项目 | 阶段 | 说明 | 详档 |
|-----------|------|------|------|
| Fig.1 散射（介电球） | ✅ 已实现 | 复矩口径 PASS + gate④ 重签 | [01-四轮复现](01-四轮复现.md) |
| Fig.2 多极分解 | ✅ 已实现 | partial_physical_match + B3 UQ DENIED | [01-四轮复现](01-四轮复现.md) |
| Grahn 映射 | ✅ 已实现 | method_consistency + external_numerical_support（B21） | [01-四轮复现](01-四轮复现.md) |
| Fig.3 Mode Analysis | ✅ 已实现 | 13 点 neff + live 场（B23 闭环） | [05-comsol路径](05-comsol路径.md) |
| Fig.3 Java 3-D（ED/MD/EQ/MQ） | ✅ 已实现 | **9 点 COMSOL 谱 + 磁共振**（B29-B31） | [05-comsol路径](05-comsol路径.md) |
| Fig.3 COMSOL 真解（完整） | 🟡 实现中 | 谱 PASS + 正式收敛/闭合待补 | [05-comsol路径](05-comsol路径.md) |
| Fig.3 COMSOL 真解（完整） | 🟡 实现中 | Mode Analysis PASS + Java 3-D 待通 | [05-comsol路径](05-comsol路径.md) |
| Grahn gate④ 关闭 | 📋 计划 | 材料齐（B18 + B21），等你裁决 | [00-待决策清单](00-待决策清单.md) |
| Fig.3 result_class 定论 | 📋 计划 | 依赖 B24 结果 | [00-待决策清单](00-待决策清单.md) |
| Fig.2 UQ 晋级 | ⏸ 已推迟 | B3 8 lane UNRESOLVED，promotion DENIED | [00-待决策清单](00-待决策清单.md) |
| report-final 更新 | 📋 计划 | 加 B21/B23 成果 | [04-报告与产物](04-报告与产物.md) |

---

## 1. 整个 flow 现状（核心）

> 📄 详细 → [01-四轮复现.md](01-四轮复现.md)

### 1.1 4 轮复现 pipeline

```
论文 → formalization spec (SEPR-9) → code (Mie/表1/表2) → data (csv/json)
  → 3 层验证 (方法/论文图/收敛) → 报告 (LATEX) → gate 裁决 → result_class
```

| 轮次 | 物理 | result_class | gate 状态 |
|------|------|------|------|
| Fig.1 散射 | 介电球 ε_r=6.25 | PASS_WITH_LIMITATIONS（复矩口径） | gate④ 已重签 ✅ |
| Fig.2 多极分解 | 介电球+金球 | partial_physical_match | gate④ limited；B3 UQ 8 lane DENIED |
| Grahn 映射 | 散射电流→多极矩 | method_consistency | gate④ 停人（材料已备） |
| Fig.3 Fano | 耦合金纳米盘 | surrogate_fallback / NOT_ACHIEVED | G0-G6 pending/blocked |

### 1.2 CODEX 任务生命周期

```
A 批 (探索/审计) → B 批 (执行) → 审查批 (B12-B14) → 修复批 (B15) → 收尾批 (B16-B19)
```

> 📄 详细 → [02-codex任务体系.md](02-codex任务体系.md)

### 1.3 Formalization → code → data

```
formalization/*.yaml (4 份) → SEPR-9 语义 → code 唯一物理输入源 → data 冻结 (42 文件)
```

> 📄 详细 → [03-formalization体系.md](03-formalization体系.md)

### 1.4 COMSOL 交叉验证路径

```
官方 MPH (B16) → Java builder (B17) → Magnus batch_mph/Java → Fig.3 G4 truth
```

> 📄 详细 → [05-comsol路径.md](05-comsol路径.md)

| 步骤 | 状态 | 阻塞 |
|------|------|------|
| 官方 6.3 rib MPH | ✅ 本地验证（10 neff + 场型） | — |
| Java builder（双金盘） | ✅ 写出（310 行静态过）+ 编译 PASS（Magnus） | 运行缺 libpskernel.so |
| SSH 直放挂载路径 | ✅ 打通（/data/public 被 job 读取，探针 PASS） | — |
| Magnus batch_mph | ⚠️ ENOSPC（临时盘声明不足） | 需 save→launch 显式声明 ephemeral_storage |
| Fig.3 G4 truth | ❌ 未完成（ENOSPC + 缺库） | B22 用 save→launch 重跑中 |

---

## 2. 工作历史

| 日期 | 事件 | 结果 |
|------|------|------|
| 08-01~08-08 | 第 1 轮（Fig.1） | 完成（gate④ 历史 limited） |
| 08-08~08-10 | 第 2 轮（Fig.2） | partial_physical_match |
| 08-10 | 第 3 轮（Grahn）+ A1-A6 | method_consistency；审查 09-12 修订 v4 |
| 08-10 夜 | B1-B8 执行批 + B9s 绕开 | 全验收 |
| 08-11 | B10-B15 审查+修复 | B14 5🔴+8🟡 全闭环 |
| 08-11 | B16-B19 收尾批 | 官方 MPH/Java builder/交叉验证 |
| 08-11 晚 | 三家调研 + B20 突破 | 挂载路径打通（探针 PASS + 编译 PASS）；莫子涵非 COMSOL 执行者；FileSecret 在 comsol 镜像不可用 |
| 08-11 晚 | B21 Grahn 外部对比 | vs arXiv:2508.16545（28 点一致 + 失效边界 + external support） |
| 08-12 | B22-B28 逐层突破 | ENOSPC→Parasolid 库→mesh→材料→后处理→背景场（全解） |
| 08-12 | B29-B31 Fig.3 真解 | 9 点 COMSOL 谱 + MD 磁共振 + ED r=0.999 vs 论文 |
| 08-12 | B31 裁决 | PARTIAL_PASS（缺正式收敛/闭合/vector trace/human gates） |

> 详细演进 → [02-codex任务体系.md](02-codex任务体系.md) + `notes/mie-f-final-status-20260811.md`

---

## 3. 未来目标计划

**目标**：4 轮复现全部以诚实 result_class 完结；Fig.3 若工具链可用则推进 COMSOL 真解。

**里程碑**：
- [x] M1：Grahn gate④ 材料（B18 + B21 external support 已齐，等你裁决）
- [x] M2：Fig.3 COMSOL 真解（9 点谱 + 磁共振，B29-B31）
- [ ] M2.5：Fig.3 正式晋级（0.7/0.5 网格 + 4000nm 外域 + 远场闭合 + vector trace + human gate）
- [ ] M3：Fig.2 B3 UQ 处理（维持/补充）
- [x] M4：4 轮报告 + 最终总报告（report-final 18 页）

> 详细计划 → [00-待决策清单.md](00-待决策清单.md)（3 项决策即里程碑）

---

## 4. 风险清单

| 风险 | 现状 | 对策 |
|------|------|------|
| Fig.3 COMSOL 工具链缺失 | ✅ 已解 | SSH 挂载 + Parasolid 库 + save→launch（B20-B29） |
| Fig.3 正式收敛/闭合 | ⚠️ | 0.7/0.5 网格 + 4000nm 外域 + 远场闭合待补（需释放远端空间） |
| Fig.2 UQ 证据不足 | ⚠️ | 预注册 fail-closed，维持 UNRESOLVED |
| Grahn gate④ 未关 | ⚠️ | 材料已备（B18），等你裁决 |
| 服务端过载（phybench） | ✅ 已修 | 单并发 + resume |
| 报告/收据不同步 | ✅ 已修 | B15 修复 + 主 agent 补 receipt |

---

## 5. 已验证 vs 未验证

- ✅ **已验证**：Fig.1 复矩口径 s=0.75 PASS（ED 136%/MD 278% >100%）；Fig.2 表2-Mie 四通道 <1%；Grahn 数值全 PASS（Path A 5.7e-7 等）；官方 MPH 本地校验 + 场型；根 pytest 126 passed
- ⏳ **未验证假设**：Fig.3 COMSOL 真解（surrogate 只是近似）；Fig.2 UQ 晋级（需更多数据）；Grahn 与实验/论文图直接对比（ceiling=method_consistency）

> result_class 口径：Fig.3 full=NOT_ACHIEVED，不夸大。

---

## 6. 关键凭据/链接索引

| 项 | 位置 |
|----|------|
| 总览 + 待决策 | `C:\Users\27370\Desktop\project\zotero\papers\mie-f\reproduction\mie-f-completion\OVERVIEW.md` |
| 状态盘点 | `C:\Users\27370\Desktop\project\zotero\papers\mie-f\reproduction\notes\mie-f-final-status-20260811.md` |
| 全栈审查 | `C:\Users\27370\Desktop\project\zotero\papers\mie-f\reproduction\codex-prompts\out\B14-fullstack-review.md` |
| 最终报告 | `C:\Users\27370\Desktop\project\zotero\papers\mie-f\reproduction\report-final\main_aux\main.pdf` |
| spec | `C:\Users\27370\Desktop\project\zotero\papers\mie-f\reproduction\formalization\` |
| CODEX 产物 | `C:\Users\27370\Desktop\project\zotero\papers\mie-f\reproduction\codex-prompts\out\` |
| Magnus/COMSOL | `C:\Users\27370\Desktop\project\optics_agent\comsol\runtime\cases\` |

---

## 7. 环境/约束

| 项 | 值 |
|----|------|
| 平台 | Windows 11 + 本地 python (D:/Download/anaconda) |
| Magnus | gustation.phybench.cn（≤256G/0GPU/B2）；token 经 ~/.magnus/config.json 只走环境变量，不落盘 |
| COMSOL | 6.3.0.290（Magnus runtime）；本地无 jar |
| 红线 | 不刷新 comsol-runtime docker；不提交 >256G/GPU/A 类 Job；不写 token/license 落盘 |
| 测试 | 根 pytest 126 passed（pytest.ini 排除 out/） |
| 服务端 | phybench 已修复（2026-08-11 14:00），优惠延至 16:00 |

---

## 8. 待你决策清单（唯一 human 入口）

> **这是你唯一需要拍板的地方**——详细在 [00-待决策清单.md](00-待决策清单.md)。

**当前 4 项待决策**（概要）：
1. **Grahn gate④ 关闭**——现新增外部基准（arXiv:2508.16545）对比，B21 结果回来后可能提升 ceiling
2. **Fig.3 COMSOL 推进**——已打通挂载路径，B22 save→launch 显式资源重跑中；成功则 G4 推进
3. **Fig.2 B3 UQ 处理**——8 lane UNRESOLVED，promotion DENIED 是否维持
4. **Grahn 外部对比是否采纳**——2508.16545 可作为 Grahn 轮外部数值支撑（B21 结果决定）

> 决策后：主文档状态表 + 相关副文档同步更新（按 doc-sync 同步规范）。

## 附录：任务状态简表

| 任务 | 状态 | 备注 |
|------|------|------|
| B2 光学定理 | ✅ | 18 passed |
| B3 UQ | ✅ | DENIED（诚实 fail-closed） |
| B4 勘误 | ✅ | 9 项落地 |
| B5 round2 修复 | ✅ | k 公式/口径 |
| B6 round3 报告 | ✅ | 13 页 |
| B1 Fig.1 重 gate | ✅ | 复矩口径裁决 |
| B7 Fig.3 Mie | ✅ | surrogate_fallback |
| B10 总报告 | ✅ | 18 页 |
| B13/B12 审查 | ✅ | 口径 + Fig.3 默认项 |
| B14 全栈审查 | ✅ | 5🔴+8🟡 闭环 |
| B15 修复 | ✅ | 全修 |
| B16 官方 MPH | ✅ | 本地验证 |
| B17 Java builder | ✅ | 编译 PASS |
| B18 Grahn 材料 | ✅ | gate④ 待裁 |
| B19 交叉验证 | ✅ | 方法学印证 |
| B20 SSH 挂载 | ✅ | 路径打通 |
| B21 Grahn 外部对比 | ✅ | 28 点一致 + 失效边界 |
| B22 显式资源 | ✅ | ENOSPC 消除 + 13 点 neff |
| B23 live 提取 | ✅ | Mode Analysis PASS |
| B24-B28 逐层突破 | ✅ | libpskernel/Parasolid/mesh/材料/后处理/背景场 |
| B29-B31 Fig.3 真解 | ✅ | 9 点谱 + ED r=0.999 vs 论文 + MD 磁共振 |
| Fig.3 正式晋级 | 📋 | 缺收敛/闭合/vector trace/human gate |
| Grahn gate④ | 📋 | 等你裁决 |
| Fig.3 class | 📋 | 等 B24 |
| Fig.2 UQ | ⏸ | 维持 DENIED |
