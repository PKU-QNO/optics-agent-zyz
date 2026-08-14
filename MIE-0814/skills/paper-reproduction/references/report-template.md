# 子 agent 工作报告模板

> 子 agent 任务结束前必须填这份报告，写到 `reproduction/sub-report/<paper>-<case>-<step>-<timestamp>.md`。
> 人看 Markdown 部分，agent 读末尾 yaml 字段。报告是给主 agent 和下一个子 agent 接力的。

## 报告正文（Markdown，人看）

### 固定头（6 字段，必须放在正文最前）
- role：W-sub
- task_scope：`<做哪一步、什么任务>`
- evidence_refs：`<引用了哪些 artifact/数据/报告路径>`
- confidence：低 / 中 / 高
- blocked_by：`<被什么卡住；无则写 none>`
- recommended_action：`<建议主 agent 下一步做什么>`

### 1. 身份声明
- 我是：子 agent（被 `<父agent>` spawn）
- 做哪一步：`{step}`
- 任务：`<一句话>`

### 2. 做了什么
（事实陈述，不评价）

### 3. 用了什么
- 参数：`<列出关键参数和值>`
- 工具/脚本：`<用了什么>`
- 输入文件：`<读了哪些>`

### 4. 遇到什么问题
（没有写"无"。有问题写清楚什么问题、怎么处理的；没问题写"未遇到阻碍"）

### 5. 结果
- 产物路径：`<输出文件>`
- 关键数值：`<列表>`
- 验证状态：`<pass/fail/pending>`

### 6. 决策性回答 ★关键
（回答主 agent 列出的"本步必须回答的决策问题"。子 agent 给建议，主 agent 拍板。）

每个决策性回答必须显式写：
- `uncertainty`：本次判断的不确定度（低/中/高 + 理由）
- `missing_evidence`：还缺什么证据才能更确定（列出要补的文件、数值、verifier、人工确认等）

不能只写"基本一致"、"看起来对"、"应该可行"；必须说明不确定度和缺证据。

### 7. 下一步需要的输入
（给下一个子 agent 的接力信息：它需要什么文件、什么参数、注意什么）

### 8. 长期记忆更新
（写 memento 的内容摘要：本次沉淀了什么事实/决策/教训）

---

## yaml 字段（末尾，agent 读）

```yaml
---
report_meta:
  agent_role: sub-agent
  step: {step}
  task: <一句话>
  spawned_by: <父agent>
  timestamp: <ISO>
  execution_status: completed | blocked | failed
  # execution_status 是任务执行状态，不是 result_class。
artifacts:
  - path: <产物路径>
    type: code | data | figure | note | report
    description: <一句话>
key_values:
  - name: <物理量>
    value: <数值>
    unit: <单位>
result_class: <not_run|pipeline_completed|simulation_completed|diagnostic_only|surrogate_fallback|partial_physical_match|physical_reproduction_success>
provenance:
  source_artifact: <来源>
  evidence_type: <证据类型>
  timestamp_version: <ISO>
  scope_applicability: <适用范围>
  confidence_result_class: <置信度>
---
```
