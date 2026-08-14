# A2 W1 spec-contract 工作报告

- role：W-sub
- task_scope：W1 spec-contract；为 `formalization/grahn.yaml` v4 建立 JSON Schema、命令行 validator 与专门合同测试
- evidence_refs：`formalization/grahn.yaml`、`code/schemas/grahn_schema.json`、`code/validate_grahn_spec.py`、`tests/test_grahn_spec.py`
- confidence：高；当前权威 spec 与三类预注册负例均由实际命令验证
- blocked_by：none
- recommended_action：主 agent 将 W1 收据交给后续只读对抗审查；后续数值 runner 在运行前先调用 validator，验证失败即停机

## 1. 身份声明

- 我是：子 agent（被主 agent spawn）
- 做哪一步：W1 spec-contract
- 任务：机器锁定 Grahn v4 的顶层结构和指定 verification gate 合同。

## 2. 做了什么

- 新增 Draft 2020-12 JSON Schema，要求当前 12 个 SEPR 顶层区段，并锁定 `meta.version` 为当前 v4 字符串。
- 对 geometry、materials、equations、solver、observables、verification、provenance 的关键结构设置必需键和基本类型。
- 对 `acceptance_contract` 的 path A/path B、`miepython_gate`、`analytic_benchmarks`、`dependency_graph`、`grahn_optical_theorem` 和数组内唯一 `rayleigh_limit` 设置结构合同；阈值、采样点数、角网格、Rayleigh 数值等字段使用 number/integer 类型。
- 新增 validator，使用 `yaml.safe_load`、Draft 对应的 `jsonschema` validator 和 SHA-256 收据；验证失败返回非零退出码并列出 JSON path。
- 新增四项合同测试：当前 v4 正例，以及删除必需字段、版本漂移、数值阈值改成字符串三类负例。
- 未修改权威输入 `formalization/grahn.yaml`，也未修改现有 scattering、数值测试、数据或报告。

## 3. 用了什么

- 参数：schema draft 2020-12；版本常量 `v4 (2026-08-10, review 12 revised)`；默认 spec 为 `formalization/grahn.yaml`。
- 工具/脚本：Python 3、PyYAML 6.0.3、jsonschema 4.25.0、pytest；文件编辑仅用 `apply_patch`。
- 输入文件：`formalization/grahn.yaml`、`codex-prompts/CODEX-A2-round3-implementation.md`、`.claude/skills/agent-workflow/references/report_template.md`、现有 `tests/test_grahn.py`。

## 4. 遇到什么问题

- 权威 YAML 的 `verification.acceptance_contract.path_B_vs_mie.per_m_tolerances.EQ_MQ.absolute_floor` 与 `zero_targets.absolute_zero` 当前本来是字符串。由于本任务禁止修改 spec 且当前 spec 必须 PASS，schema 将这两个 legacy 字段锁为“可解析数值的字符串”；其余实际 YAML 数值字段严格要求 JSON number/integer。
- YAML 文件头注释仍写 v3，但语义字段 `meta.version` 已是 v4；JSON Schema 只能验证 YAML 数据节点，不能验证注释。
- 当前工作区不是 Git 仓库，未能用 `git status` 提供变更基线；本轮以父任务限定的四个产物路径控制写范围。

## 5. 结果

- 产物路径：
  - `code/schemas/grahn_schema.json`
  - `code/validate_grahn_spec.py`
  - `tests/test_grahn_spec.py`
  - `sub-report/a2-w1-spec-contract.md`
- 关键数值：
  - spec SHA-256：`41b57d80b4b33b23f68d13ba44bb1c14b49e94f43eb0844a37018271b14ac2ad`
  - schema SHA-256：`36e448a08ff209e06d240b54ec03d7119c9d0ea95c36bb1fa3155a6ee84d96f0`
  - validator：`PASS`，退出码 0
  - 子 agent 专门测试：`4 passed in 1.73s`
  - 主 agent 独立复验：validator `PASS`；`4 passed in 1.68s`
- 验证状态：pass（仅 W1 spec-contract；未运行 A2 数值 gate 或全量回归）

## 6. 决策性回答 ★关键

### 当前 v4 是否可被机器识别并拒绝结构漂移？

- 回答：是。当前 spec 正例通过；指定的必需路径删除、`meta.version` 漂移、真实数值阈值字符串化均以非零退出码失败。
- uncertainty：低；四类行为均经 subprocess 实测，收据包含版本和双 SHA-256。
- missing_evidence：尚缺 CI/主 runner 实际接线证据；目前 validator 是可调用入口，但未修改 runner（不在 W1 授权范围）。

### 该 schema 是否验证物理公式和所有 prose 语义？

- 回答：否。它验证结构、必需键和指定 gate 的数值类型，不证明公式、阈值科学合理性或 range 上下界次序正确；D1（Qe 与 STF 映射约定）明确不在 W1 覆盖范围。
- uncertainty：低；这是 JSON Schema 合同的明确能力边界。
- missing_evidence：prose 公式正确性与 D1 仍需 D1/D2 物理审查和独立数值 verifier；阈值值域/跨字段关系若要硬锁，需要后续版本加入语义检查。

## 7. 下一步需要的输入

- 后续 agent 应读取 validator 的 JSON stdout，不解析人类 prose；`status != PASS` 或进程非零时停止数值运行。
- 对抗审查需重点检查：两个 legacy 数值字符串是否应在下一版 formalization 中改为 YAML number，以及 runner 是否确实 fail-closed 调用 validator。
- 不应把本报告的 W1 PASS 解读为 Grahn 映射物理 gate 通过。

## 8. 长期记忆更新

- 已经过去重后写入 memento：`59d6924d-88ee-41e6-9fe1-10f0059acd92`。内容记录 Grahn v4 已有独立 schema/validator 合同与三类负例，以及两个 legacy 字符串容差和 YAML 头注释 v3 的边界。

---
report_meta:
  agent_role: sub-agent
  step: W1
  task: Grahn v4 spec-contract schema, validator, and negative tests
  spawned_by: root
  timestamp: 2026-08-10T12:26:53+08:00
  execution_status: completed
artifacts:
  - path: papers/mie-f/reproduction/code/schemas/grahn_schema.json
    type: code
    description: Draft 2020-12 contract for the current Grahn v4 formalization
  - path: papers/mie-f/reproduction/code/validate_grahn_spec.py
    type: code
    description: Fail-closed CLI validator with SHA-256 JSON receipt
  - path: papers/mie-f/reproduction/tests/test_grahn_spec.py
    type: code
    description: Current-spec positive test and three contract-drift negative tests
  - path: papers/mie-f/reproduction/sub-report/a2-w1-spec-contract.md
    type: report
    description: W1 execution receipt and scope boundary
key_values:
  - name: validator_status
    value: PASS
    unit: status
  - name: dedicated_tests_passed
    value: 4
    unit: tests
  - name: negative_test_categories
    value: 3
    unit: categories
result_class: diagnostic_only
provenance:
  source_artifact: formalization/grahn.yaml v4 plus the W1 validator and dedicated tests
  evidence_type: JSON Schema validation receipt and subprocess negative tests
  timestamp_version: 2026-08-10T12:26:53+08:00
  scope_applicability: Grahn A2 round3 W1 structural contract only
  confidence_result_class: high for structural validation; no physical-result claim
---
