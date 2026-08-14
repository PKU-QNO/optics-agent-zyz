# A2 W2 D1 — Grahn/Alaee 二阶矩归一化独立审查

| 固定头字段 | 值 |
|---|---|
| `role` | D1 独立代数审查员；不参与 A2 实现，不把 A2 自报完成当作 gate receipt |
| `task_scope` | 只审查 Grahn 原始二阶电流矩、其 STF 投影、Alaee 长波电四极矩 $Q^e$，以及 Grahn (39)–(41) 的归一化接口 |
| `evidence_refs` | Grahn PDF 页图 `tmp/pdfs/grahn-d1/page-08.png`、`page-10.png`；`../vector-multipole-derivation/sections/08_current_multipole.tex:88-108`；`formalization/grahn.yaml:76-111`；`code/scattering.py:268-288`；`codex-prompts/out/A2-evidence-manifest.json` |
| `confidence` | high：核心结论是逐分量线性代数恒等式；实现审查限定于冻结证据所显示的 API、注释与 spec |
| `blocked_by` | 当前 `q_for_mapping="qe"` 复用 Grahn (39)–(41) 系数但没有 $1/6$ 换算；符号层同时混用 Grahn 原始 $Q=M^{(2)}$、STF 投影与 Alaee $Q^e$ |
| `recommended_action` | Gate 2 置为 `BLOCKED_PENDING_HUMAN_FIX`；修正前删除/禁用 `qe` 生产路径，或在 (39)–(41) 前显式换算 $Q^e/6$，并分层命名 raw/STF/Alaee 对象 |

## 1. 身份声明

本报告是小型、独立、只读的 D1 归一化审查。审查只使用任务指定的六组冻结证据，没有继续检索、运行测试或修改实现。`A2-evidence-manifest.json` 自己把快照标为 `UNVERIFIED_A2_SELF_REPORT`，所以这里给出候选 gate 裁决，不把实现者自报状态提升为独立 PASS。

## 2. 做了什么

我完成了三项检查：

1. 从两个定义直接推导 Alaee 长波电四极矩与 Grahn 原始二阶电流矩 STF 投影的比例；
2. 对 Grahn (39)–(41) 的五个线性组合逐类检查迹部分和反对称部分是否消失；
3. 把该代数结论对照冻结 spec 与 API，判断 `stf` 和 `qe` 两条输入路径的数值归一化及生产可用性。

## 3. 用了什么

- `page-08.png`：Grahn (27) 定义 $M^{(l)}$，并明确对 $l=2$ 命名 $M^{(2)}=Q$。因此 Grahn 后文的 $Q$ 是无核原始二阶电流矩，不是 Alaee 规范化后的 $Q^e$。
- `page-10.png`：Grahn (39)–(41) 直接把上述 $Q$ 的分量组合映射为 $a_E(2,m)$；(47)–(48) 还使用 $Q$ 的反对称组合，进一步证明原论文的 $Q$ 不是对称无迹的 $Q^e$。
- `08_current_multipole.tex:88-108`：给出 $M^{(2)}$ 的 STF、反对称和迹分解，并把 STF 部分关联到 $Q^e$。
- `formalization/grahn.yaml:76-111`：已记录四对象分层与 $Q^e=6\,\mathrm{STF}(M2_{raw})$，但 (39)–(41) 仍只写未分层的符号 `Q`。
- `code/scattering.py:268-288`：API 接受 `q_for_mapping in ("stf", "qe")`，默认选 STF；`qe` 分支直接选 `parts["Qe"]`，但注释把它错误称为“literal source formula”。
- `A2-evidence-manifest.json`：冻结了上述 spec/code 快照，并声明它不是独立 gate receipt。

## 4. 遇到什么问题

问题不是默认 `stf` 数值路径本身，而是三层符号没有在 API、注释和 spec 映射处闭合：

- Grahn 原论文：$Q_{raw}=M^{(2)}$，一般既不对称也不无迹；
- Grahn 电四极组合的有效输入：$Q_{STF}=\mathrm{STF}(Q_{raw})$；
- Alaee 长波电四极矩：$Q^e=6Q_{STF}$。

冻结代码默认把 $Q_{STF}$ 送入 Grahn (39)–(41)，数值上与送入 $Q_{raw}$ 完全等价，因此默认 E2 映射是物理正确的。可是 `qe` 分支把六倍张量送入同一系数体系；同时注释把 Alaee $Q^e$ 错说成 Grahn 的 literal source $Q$。这会让调用者误以为两个枚举值只是等价命名，而不是需要系数换算的不同规范。

## 5. 结果

令 Grahn (27) 的原始二阶矩为

$$
M_{\alpha\beta}=\frac{i}{\omega}\int J_\alpha r_\beta\,d^3r,
$$

并定义

$$
S_{\alpha\beta}=\operatorname{STF}(M)_{\alpha\beta}
=\frac{M_{\alpha\beta}+M_{\beta\alpha}}{2}
-\frac{\delta_{\alpha\beta}}{3}\operatorname{tr}M.
$$

Alaee 的长波电四极定义为

$$
Q^e_{\alpha\beta}
=-\frac{1}{i\omega}\int
\left[3(r_\alpha J_\beta+r_\beta J_\alpha)
-2(\mathbf r\!\cdot\!\mathbf J)\delta_{\alpha\beta}\right]d^3r.
$$

由于 $-1/i=i$，且

$$
\frac{i}{\omega}\int r_\alpha J_\beta\,d^3r=M_{\beta\alpha},
\qquad
\frac{i}{\omega}\int(\mathbf r\!\cdot\!\mathbf J)d^3r=\operatorname{tr}M,
$$

所以

$$
Q^e_{\alpha\beta}
=3(M_{\alpha\beta}+M_{\beta\alpha})
-2\delta_{\alpha\beta}\operatorname{tr}M
=6S_{\alpha\beta}.
$$

再写

$$
M=S+A+\frac{t}{3}I,
\qquad A^T=-A,
\qquad t=\operatorname{tr}M.
$$

Grahn (39)–(41) 只出现以下类型的组合：

$$
M_{xx}-M_{yy},\quad
M_{xy}+M_{yx},\quad
M_{xz}+M_{zx},\quad
M_{yz}+M_{zy},\quad
2M_{zz}-M_{xx}-M_{yy}.
$$

对角差和 $2zz-xx-yy$ 消去各向同性迹项；非对角和消去反对称项。故每个组合都满足

$$
F_m(M)=F_m(S),
$$

即 Grahn (39)–(41) 对 $M$ 的迹部分和反对称部分不敏感，使用原始 $Q=M$ 与使用 $\mathrm{STF}(M)$ 完全等价。反之，若不改系数而代入 Alaee $Q^e=6S$，则

$$
F_m(Q^e)=6F_m(S)=6F_m(M).
$$

因此同一 (39)–(41) 的整体系数必须除以 6，等价地先做 $Q^e\mapsto Q^e/6$。否则每个 E2 复振幅放大 6 倍；按 $|a_E(2,m)|^2$ 计的电四极部分截面放大 36 倍。

## 6. 决策性回答

**候选裁决：`BLOCKED_PENDING_HUMAN_FIX`。**

- **数值物理**：当前默认 `q_for_mapping="stf"` 对 Grahn (39)–(41) 是正确的，因为这些组合天然投影到 STF 子空间。
- **API/注释/spec**：不合格。`qe` 被列为可接受路径，却没有在同一映射系数前除以 6；“literal source formula” 注释也与 Grahn (27) 的 $M^{(2)}=Q$ 相冲突；spec 的 `mapping_E2` 未声明其中 `Q` 的对象层。
- **生产结论**：修正前不得把 `qe` 路径当作生产选项，也不得用当前接口的双枚举声称 raw/STF/Alaee 三种规范已实现互换。
- **最小修订**：首选移除或显式拒绝 `q_for_mapping="qe"`，把默认输入命名为 `m2_stf`，并在 spec 的 (39)–(41) 标注 `Q := M2_raw`（等价可用 `M2_stf`）。若必须保留 `qe`，只在 E2 (39)–(41) 前使用 `Qe/6` 或把相应系数除以 6，并同步改正注释和 API 文档；不要把对称的 $Q^e$ 误用于依赖反对称原始 $Q$ 的 (47)–(48)。
- **uncertainty**：本结论没有运行时不确定性；只存在证据边界不确定性，即未检查指定行以外是否另有隐藏的 $1/6$ 补偿。冻结的选择逻辑和注释没有显示这种补偿，故不足以给生产 PASS。
- **missing_evidence**：需要修订后的精确 diff，以及证明 `qe` 已被禁用或仅在 E2 前规范化的定向回归 receipt；在它们出现前保持 BLOCKED。

## 7. 下一步输入

异构审查应读取本报告和同一冻结证据，优先尝试反驳以下三点：$Q^e=6\,\mathrm{STF}(M2_{raw})$；(39)–(41) 对迹/反对称部分不敏感；当前 `qe` 分支存在六倍振幅风险。若无法反驳，要求给出最小实现/spec 修订并输出 BLOCKED；只有在冻结实现中定位到明确的 $1/6$ 补偿且符号契约无歧义时才可输出 PASS。异构审查提示词见 `opus-prompts/14-grahn-d1-implementation-gate-review.md`。

## 8. 长期记忆更新

未执行。任务明确禁止 memory；本次只把可审计结论落入本地 sub-report 和异构审查提示词，不声称已更新任何长期记忆系统。

```yaml
report_meta:
  report_id: a2-w2-d1-normalization
  reviewer_role: independent_algebra_reviewer
  evidence_boundary: frozen_named_sources_only
  test_execution: none
artifacts:
  report: sub-report/a2-w2-d1-normalization.md
  hetero_review_prompt: opus-prompts/14-grahn-d1-implementation-gate-review.md
key_values:
  alaee_longwave_conversion: "Qe = 6 * STF(M2_raw)"
  grahn_e2_projection: "F_m(M2_raw) = F_m(STF(M2_raw))"
  uncorrected_qe_amplitude_factor: 6
  uncorrected_qe_partial_cross_section_factor: 36
  default_stf_numeric_status: physically_correct_for_grahn_39_41
  qe_production_status: forbidden_pending_fix
result_class: BLOCKED_PENDING_HUMAN_FIX
provenance:
  source_snapshot: codex-prompts/out/A2-evidence-manifest.json
  source_snapshot_status: UNVERIFIED_A2_SELF_REPORT
  derivation_type: exact_componentwise_linear_algebra
```
