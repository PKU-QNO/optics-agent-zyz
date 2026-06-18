# Workflow Engine 指南

## 概述
optics_agent 的工作流引擎是基于 YAML 拓扑的指令式任务编排系统。工作流定义是一个 `*.workflow.yaml` 文件，Agent 启动时载入并按节点顺序执行。

## 工作流执行模式

### 启动
```
1. 载入 workflows/<name>.workflow.yaml
2. 创建 workflows/state/<session_id>.yaml 状态文件
3. 从第一个节点开始执行
```

### 节点执行
```
每个节点执行流程：
1. 读取节点的 instruction（或 prompt_file）
2. 读取节点 produces 中的输入文件（如存在）
3. 执行任务（LLM 推理 + 工具调用）
4. 写入节点 produces 中的输出文件
5. 更新 state.yaml 中的 current_node 和已完成节点列表
6. 根据 next/branches 确定下一节点
```

### 分支逻辑
```
分支节点执行流程：
1. 读取 instruction 作为判断依据
2. LLM 评估分支条件
3. 输出 branch_name（如 pass/fail）
4. 查找 branches 映射，确定下一节点
5. 如超过 max_retries，终止并报告
```

### 状态文件格式
```yaml
# workflows/state/<session_id>.yaml
workflow: paper_reproduction
version: 0.1.0
session_id: <uuid>
start_time: 2026-06-18T10:00:00Z
current_node: theory_derivation
completed_nodes:
  - paper_reading
node_outputs:
  paper_reading:
    status: completed
    output_files:
      - reproduction/private/case/params.yaml
      - reproduction/private/case/paper_notes.md
    duration_seconds: 300
    timestamp: 2026-06-18T10:05:00Z
```

## 节点类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `prompt` | 执行指令，然后进入 next 节点 | 论文阅读、报告生成 |
| `branch` | 评估条件，按分支路由 | 理论检查、数值检查 |
| `tool` | 调用预定义工具 | 提交 Magnus 作业 |
| `parallel` | 并行执行多个子节点 | 同时检查多个结果 |

## 自迭代
工作流文件本身是自迭代的。`update_artifacts` 节点会：
1. 分析本次执行的 lessons
2. 修改 `.workflow.yaml`（拓扑、prompt、分支条件）
3. 递增 version
4. 记录变更 history

## 当前可用工作流
- `paper_reproduction.workflow.yaml` — 论文复现标准工作流
