# Fig.3 路径候选采纳注记（2026-08-11）

主 agent 依据 B12 对抗审查，将 `formalization/alaee2018-fig3.yaml` 采纳为 `APPROVED_AS_PATH_CANDIDATE`。这只表示 B12 路径设计被采纳，不是正式执行批准；执行与任何 result-class 晋升仍须完成 FIG3-G0--G6：
- 基础 = B11 修订稿（SEPR 9 字段 + FIG3-G0~G6）
- B12 审查（`codex-prompts/out/B12-review-fig3-defaults.md`）调整项采纳：

## B12 五项调整（路径候选已采纳，需在实现中落实）
1. **#2 JC 缺口双轨**：主 paper-fidelity gate 只用 JC 支持域 x≥500/1937≈0.25813（201 点网格从 x=0.26125 起进 gate）；全轴只输出带 unsupported mask 的诊断图，前三点（x=0.25/0.25375/0.25750）不进数值 gate；1935 nm 只作保守标签
2. **#3 contrast-domain 限定**：积分域 = "所有相对统一 host 有材料反差的物理局域域"，排除 PML/外域/数值域；J=−iω(ε−ε_host)E；spacer≠host 时积分其全部非零诱导电流；分层/非均匀 host → 停机换 Green 张量口径
3. **#4 panel(b) metric**：主定义 e_M=100||M1−M2||/||M2||（ED/MD complex L2、EQ/MQ complex Frobenius、Table2 分母）；加模长差旁路 100|||M1||−||M2|||/||M2||；冻结复张量布局/STF/独立分量；floor/mask 只用于聚合 gate 不改源曲线；未消歧前标 source-compatible engineering reconstruction
4. **#5 采样**：201 点=base scan 非最终充分性；必须自适应/嵌套收敛（201→401）+ 确定性 UQ（spectral/mesh/PML/材料插值/solver/raster）；峰位阈值用绝对 x 或局部线宽比例，不用网格点数
5. **#6 证据层级**：COMSOL truth 需 hash-bound 实际成功求解 .mph + GUI-exported .java + 版本/module + solver/log + 非零基准输出；B9s 只有升级为可执行已运行等价证据包才可替代；B8 skeleton 仍 diagnostic

## B12 拒绝项（#7 数值门槛）
Mie-COMSOL 数值阈值（NRMSE 0.25/Pearson 0.80/|Δx_peak|=0.05/dominant 0.75/panel-b 10/25）**拒绝为晋升硬 gate**，降为明确标注的探索性诊断带；FIG3-G5 只硬验公共合同一致/mask 诚实/五类指标完整报告

## B12 补第 9 项：Eq.(1) 版本冻结（新增）
- 临时批准 **hash-bound arXiv v2** 的 |m/c|²、|kQ^m/c|² 为唯一实现版本，**禁止混用**另一转录 |m|²/c
- 最终 physical_reproduction_success 评议前完成期刊终版 glyph 核验
- SI 单位、时间因子、诱导电流符号一并写入方程 receipt
- 未冻结前：磁通道只能计算性诊断，不能通过方程/晋升 gate

## B12 批准项
- #1 spec scope（四通道 Table1/2 为主 + Fano 默认关闭不 gate）✅
- #8 result-class（首次晋升上限 partial_physical_match；source-equivalence 条件满足后才人工评议 physical_reproduction_success）✅

## 当前 gate 状态（B12）
FIG3-G0 可批 / G1 BLOCKED-PARTIAL / G2 可批定义 / G3 可批 / G4 NOT RUN / G5 INACTIVE / G6 BLOCKED
→ 完整 Fig.3 = NOT_ACHIEVED；B7=surrogate_fallback、B8=diagnostic_only
