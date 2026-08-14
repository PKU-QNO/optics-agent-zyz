# Fig.1 gate④ superseding receipt (metric re-gate closure)

Receipt ID: `FIG1-G4-20260811-PASS-COMPLEX-MOMENT`

Supersedes: `FIG1-G4-20260809-PASS_WITH_LIMITATIONS`（历史收据，metric 口径漂移）

## 裁决依据链

1. **B13 对抗审查**（`codex-prompts/out/B13-review-fig1-metric.md`）：
   - 论文原话证据：`alaee2018-chinese.tex:231-234`"电偶极矩和磁偶极矩的相对误差均超过 100%"；原始英文 caption "Relative error between the multipole moments..."（`notes/fig1-parameters.md:26-29`）
   - 裁决：**Fig.1 论文 gate 应使用复多极矩向量/张量相对误差**（ED/MD 复向量 2-范数、EQ/MQ 复张量 Frobenius、Table2 分母），不需要第三种主口径
   - 阈值冻结：精确 s=2a/λ=0.75 处 ED>100% 且 MD>100%；EQ/MQ 只报告不参与双偶极判定
   - C 分项口径只作派生诊断，不替代论文矩 gate
2. **B1 双口径证据**（`codex-prompts/out/B1-regate-verdict.md` + `B1-fig1-s075-evidence.json`）：
   - exact s=0.75 复矩误差：ED=136.166897%、MD=277.742441%、EQ=42.519471%、MQ=24.795029%
   - exact s=0.75 C 分项诊断：ED=86.914764%、MD=215.910993%、EQ=103.077456%、MQ=55.750998%
   - gate 值 = exact 直接计算（插值仅作 CSV 复现检查，不入 gate）
3. **用户授权**：2026-08-11 用户指示"额外发一些 CODEX 审查默认项后 自行决定"——主 agent 依据 B13 独立审查裁决采纳复矩口径。

## 裁决结论

| 项 | 值 |
|---|---|
| 论文 gate 指标 | 复多极矩向量/张量相对误差（complex L2 / Frobenius，Table2 分母） |
| s=0.75 精确值 | ED=136.166897% >100% ✅ ／ MD=277.742441% >100% ✅ |
| 判定 | **PASS**（论文单点"ED/MD 均超过 100%"声明成立） |
| C 分项口径 | 仅诊断（ED 86.9%/MD 215.9%/EQ 103.1%/MQ 55.7%），不参与论文 gate |
| result_class | `PASS_WITH_LIMITATIONS`（方法合同 PASS + 单点论文声明 PASS；无 unrestricted physical success 宣称） |
| 新人类 gate 停点 | 无（本 receipt 即人工裁决记录；用户"自行决定"授权覆盖） |

## 生效范围

- 关闭 Fig.1 论文单点（s≈0.75）多极矩声明 gate；不证明全区间 Table1 精确，不替代 Table2↔Mie 独立数值质量合同
- 正式 spec `formalization/alaee2018-fig1.yaml` 的 `primary_paper_metric`（L165-176）已与此一致（B1 已更新）

## 完整性

- 旧 receipt（20260809）保留为历史证据，不编辑（immutable protocol）
- 本 receipt 是唯一新的 superseding 记录；SHA-256 sidecar 同目录
