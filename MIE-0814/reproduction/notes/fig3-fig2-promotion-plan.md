# Fig.3 晋级 + Fig.2 补 UQ 计划（2026-08-12 用户拍板）

> 用户决定：①Fig.3 晋级（补晋级材料）②Fig.2 补 UQ 数据。本计划两线并行推进。

## 线 1：Fig.3 晋级（B31 裁决的 5 项缺口）

| # | 缺口 | 动作 | 阻塞/注意 |
|---|------|------|-----------|
| 1 | **0.7/0.5 网格收敛** | 释放远端空间 → 提交 0.7/0.5 网格 job（coarse 133,782 → baseline 292,687 → 更细） | 需清理远端旧输出（B20-B28 的大 MPH） |
| 2 | **4000nm 外域收敛** | 扩域 4000nm 提交（当前 SBC，pml=false） | 求解时间更长 |
| 3 | **远场/功率闭合** | 直接远场/散射功率 vs 体积分闭合（Fig.3 科学核心） | 需 builder 加远场积分节点 |
| 4 | **高阶 multipole 收敛** | l>4 高阶通道检查（确认 l≤4 截断合理） | 后处理加阶数 |
| 5 | **vector paper trace** | 论文 Fig.3 曲线 vector 提取（或 human 批准 raster 替代） | **需用户批准 raster 替代**（B31 用 raster，formalization 要求 vector） |

**目标**：Fig.3 从 PARTIAL_PASS → partial_physical_match（若全部过）

## 线 2：Fig.2 补 UQ 数据（B3 DENIED 的 3 项缺口）

| # | 缺口 | 动作 | 依据 |
|---|------|------|------|
| 1 | **校准不确定性**（calibrated uncertainty） | 按 A5-v2 spec 重算误差带（统计校准，非简单区间） | `A5-recompute/preregister/` |
| 2 | **有效覆盖率**（effective coverage） | 不确定区间覆盖论文点比例的计算 | A5-v2 SPEC.md |
| 3 | **dense-mode 专属门槛** | dense 模式的门槛定义 + 计算 | A5-v2 |

**目标**：8 条 lane 从 UNRESOLVED → 可判 PASS/FAIL → promotion 可评估

## 执行顺序（并发 2 CODEX）

1. **B32（Fig.3 晋级）**：释放远端空间 + 0.7/0.5 网格 + 4000nm 外域 + 远场闭合 + 高阶收敛（一项 CODEX 多步）
2. **B33（Fig.2 UQ）**：按 A5-v2 补校准不确定性 + 有效覆盖率 + dense 门槛

两者独立（不同数据/文件），可并行。完成后 → 验收 → Fig.3/Fig.2 最终裁决。

## 人工停点
- **raster vs vector trace**：B32 需要你批准 raster 替代（若 vector 提取不可行）
- **最终裁决**：B32/B33 结果 → Fig.3/Fig.2 晋级裁决

## 风险
- 远端空间：需清理 B20-B28 大输出（几十 GB）——先确认哪些可删
- UQ 计算量大：8 lane × 校准 → 可能耗时
- Fig.3 求解时间：0.7/0.5 网格 + 4000nm 外域 → 每点可能 2-5 分钟
