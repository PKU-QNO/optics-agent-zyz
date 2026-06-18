# 工作流引擎设计笔记

> 2026-06-18
> 本文档记录 optics_agent 工作流引擎的架构设计方案，是后续实现的技术蓝图。

---

## 1. 核心问题

我们用 YAML 文件（如 `paper_reproduction.workflow.yaml`）定义了论文复现的完整拓扑，但：
- **Agent 不能直接解析 YAML** — 不会理解节点拓扑和分支逻辑
- **需要 CLI 中间层** — 一个程序负责加载 YAML、驱动执行、管理状态
- **检查节点需要客观性** — 主 agent 对自己的输出有 bias，不适合自我评估

## 2. 双级架构

```
┌─────────────────────────────────────────────────────┐
│              主 agent（当前对话/模型）                │
│  上下文贯穿：paper_reading → theory_derivation → ...   │
│  只关心"当前节点要我做什么"，不关心拓扑                     │
├─────────────────────────────────────────────────────┤
│          CLI 引擎（workflow.py）                       │
│  加载 YAML、管理 state、路由分支、启动子进程              │
├─────────────────────────────────────────────────────┤
│           子 agent（新 CLI 进程）                      │
│  检查/高危节点时临时启动，独立上下文                      │
│  可以是不同模型/不同 CLI                                 │
└─────────────────────────────────────────────────────┘
```

### 2.1 主 agent

- 就是用户当前使用的 AI coding agent（opencode、Claude Code、Codex CLI 等）
- 所有**执行类节点**都在主 agent 的同一个对话上下文中完成
- 主 agent 不解析 YAML，只调用 `python workflow.py next` 等 CLI 命令
- 上下文持续整个工作流，中间产物（参数表、推导、Java 代码）都在上下文中

### 2.2 CLI 引擎

- 一个 Python 脚本（如 `comsol/automation/workflow.py`）
- 负责：加载 YAML → 创建/更新 state → 返回当前节点信息 → 接收完成信号 → 前进
- 到达检查/高危节点时：自动启动子 agent 进程 → 等待结果 → 写回 state → 主 agent 继续
- 不解析任何 Agent 输出文本，只接收结构化指令（`done`, `branch <name>`）

### 2.3 子 agent

- 检查/高危节点专用的**新 CLI 进程**
- CLI 可配置（如 `opencode`、`codex`、`claude-code`），模型也可不同
- context 只包含当前节点的输入产物（无主 agent 的历史，保证客观性）
- 执行完毕后自行退出，结果写回 state.yaml
- 主 agent 下次 `next` 时读到结果，自然前进

## 3. 节点分配规则

| 节点 | 归属 | 原因 |
|------|------|------|
| `paper_reading` | 主 agent | 需要对话上下文积累 |
| `theory_derivation` | 主 agent | 需要对话上下文积累 |
| `theory_check` | **子 agent** | 需要客观评估，避免"作者 bias" |
| `numerical_program` | 主 agent | 需要完整上下文（参数→代码） |
| `magnus_submit` | 主 agent | 简单提交操作 |
| `numerical_debug` | 主 agent | 需要知道修改历史 |
| `numerical_check` | **子 agent** | 需要客观评估，必要时可加脚本验证钩子 |
| `answer_verification` | 主 agent | 需要完整上下文做对比分析 |
| `generate_report` | 主 agent | 需要完整上下文 |
| `update_artifacts` | **子 agent** | 高危操作（改 SKILL/工作流），隔离保护 |
| `check_iteration` | **子 agent** | 需要独立判断迭代质量 |

### 判断原则

| 条件 | 归属 |
|------|------|
| 需要积累上下文 | 主 agent |
| 执行类任务（写代码、提作业、写报告） | 主 agent |
| **评估类任务**（检查是否正确、通过/不通过） | **子 agent** |
| **高危操作**（改文件、改工作流定义） | **子 agent** |
| 需要历史信息做决策 | 主 agent |
| 需要**无 bias 的独立判断** | **子 agent** |

## 4. 子进程机制

### 4.1 启动流程

```
主 agent 调 python workflow.py next
    │
CLI 引擎读 state.yaml → 当前节点是 theory_check
    │
节点定义中 subagent: true  → 进入子进程模式
    │
CLI 引擎:
  1. 读取节点的 instruction（评估标准）
  2. 读取 produces 中的输入文件（如 theory_derivation.md）
  3. 构建子 agent 的 system prompt
  4. 启动子进程: opencode --prompt "xxx"
  5. 等待子进程退出
  6. 读子进程输出 → 提取分支决策
  7. 更新 state.yaml（记录分支结果）
    │
主 agent 下次调 next → 读到已更新的 state → 知道下一节点
```

### 4.2 子进程的 CLI 和模型可配置

在 workflow.yaml 每个节点上可以指定：

```yaml
theory_check:
  type: branch
  subagent: true
  subagent_cli: "opencode --model gpt-4o"     # 可选：指定 CLI 和模型
  context:                                      # 子进程收到的 context
    files:
      - reproduction/private/<case>/theory_derivation.md
      - reproduction/private/<case>/params.yaml
    instruction_ref: "workflows/prompts/theory_check.md"

update_artifacts:
  type: prompt
  subagent: true
  subagent_cli: "opencode"                      # 使用默认 CLI
  context:
    files:
      - workflows/paper_reproduction.workflow.yaml
      - reproduction/private/<case>/final_report.md
    instruction_ref: "workflows/prompts/update_artifacts.md"
```

### 4.3 输出约定

子进程的输出不要求特定格式，CLI 引擎通过两种方式提取结果：

```
方式 A（首选）: 要求子进程在输出末尾写标记行
  ## 分支决策
  pass
  原因：xxx

方式 B（fallback）: 用小模型（如 gpt-4o-mini）读子进程全部输出
  输入：子进程的全部输出文本
  输出：{"branch": "pass", "confidence": 0.95}
  成本 < 0.01 元，仅在方式 A 失败时触发
```

## 5. CLI 接口设计

### 5.1 主 agent 用的命令

```bash
# 载入工作流（首次使用）
python workflow.py load paper_reproduction.workflow.yaml
# 输出：工作流名称、版本、节点数、第一个节点信息

# 查看当前节点
python workflow.py current
# 输出：
#   节点ID: theory_derivation
#   类型: prompt
#   描述: 推导理论模型
#   输入文件: params.yaml
#   输出文件: theory_derivation.md

# 完成后前进到下一节点
python workflow.py done
# 输出：
#   已完成: theory_derivation
#   下一节点: theory_check
#   类型: branch
#   提示: 系统将启动子进程进行评估...

# 分支决策（主 agent 自己做的轻量分支）
python workflow.py branch pass
# 输出：
#   分支: pass
#   路由到: numerical_program

# 查看整体状态
python workflow.py status
# 输出：
#   工作流: paper_reproduction v0.1.0
#   已完成: [paper_reading, theory_derivation]
#   当前: theory_check (branch)
#   总节点: 10
#   进度: 2/10

# 回退到上一节点
python workflow.py back
# 输出：已回退到 theory_derivation

# 重置
python workflow.py reset
```

### 5.2 CLI 引擎内部命令（自动调用）

```bash
# 启动检查子进程（由引擎自动调用）
python workflow.py _start-check <node_id>
# 内部行为：
#   1. 读节点配置
#   2. 构建子进程 context
#   3. 启动子 CLI 进程
#   4. 等待结果
#   5. 更新 state

# 提取分支决策（由引擎自动调用）
python workflow.py _extract-branch <node_id> <sub_output_path>
# 内部行为：
#   1. 尝试正则匹配标记行
#   2. 失败则用小模型提取
#   3. 返回 branch name
```

## 6. 分支决策的可靠性设计

### 6.1 三层方案

```
第 1 层（首选）: 输出标记
  子 agent 的 prompt 要求末尾写 "## 分支决策\npass"
  CLI 正则解析，零成本、零延迟
  预期覆盖率: ~90%

第 2 层（fallback）: 小模型提取
  未检测到标记时，调用 gpt-4o-mini 等小型模型
  输入：子 agent 全部输出
  输出：{"branch": "pass", "reason_summary": "..."}
  预期覆盖率: ~99%

第 3 层（安全网）: 脚本验证钩子
  某些可程序化验证的节点（如 numerical_check）：
  检测到 neff 全为零 → 自动覆盖为 fail
  检测到 NaN/Inf → 自动覆盖为 fail
  检测到 solver error → 自动覆盖为 fail
```

### 6.2 三种分支节点的可靠性对比

| 节点 | 默认提取方式 | 可加脚本钩子 | 可靠性 |
|------|-------------|-------------|--------|
| `theory_check` | 标记 + 小模型 | 否（纯文本评估） | 高 |
| `numerical_check` | 标记 + 小模型 | 是（数值验证脚本） | 最高 |
| `check_iteration` | 标记 + 小模型 | 否（纯文本评估） | 高 |

## 7. 状态文件格式

```yaml
# workflows/state/<session_id>.yaml

workflow: paper_reproduction
version: 0.1.0
session_id: "uuid-xxxx"

started_at: "2026-06-18T10:00:00Z"
updated_at: "2026-06-18T11:30:00Z"

current_node: theory_derivation

completed_nodes:
  - id: paper_reading
    status: completed
    duration_seconds: 480
    output_files:
      - reproduction/private/case/params.yaml
      - reproduction/private/case/paper_notes.md
  - id: theory_check
    status: completed
    duration_seconds: 90
    subagent: true
    subagent_model: "gpt-4o"
    subagent_output_files:
      - workflows/state/session_check_theory.txt
    branch_decision: pass
    branch_reason: "推导正确，量纲一致，边界条件合理"

node_outputs:
  params.yaml: reproduction/private/case/params.yaml
  theory_derivation_md: reproduction/private/case/theory_derivation.md

retry_counts:
  theory_check: 0
  numerical_check: 0
  check_iteration: 0

artifacts_updated: false
```

## 8. 与当前项目的映射

### 8.1 文件位置

```
comsol/automation/workflow.py       # CLI 引擎
workflows/                           # 工作流定义目录（已有）
├── paper_reproduction.workflow.yaml # 复现工作流（已有）
├── ENGINE.md                        # 引擎指南（已有）
├── schemas/                         # 格式定义（已有）
├── prompts/                         # 节点 prompt（已有）
└── state/                           # 执行状态（已有）
```

### 8.2 workflow.yaml 的扩展

当前节点的 `type` 字段需要增加 `subagent` 标记。考虑两种扩展方式：

```
方式 A: 直接在节点上加 subagent: true 字段
  theory_check:
    type: branch
    subagent: true  ← 新增

方式 B: 新增 subagent 类型
  theory_check:
    type: sub_branch   ← 新增类型
```

推荐方式 A，改动最小，向后兼容。

### 8.3 AGENTS.md 更新

在 AGENTS.md 的工作流系统部分补充子 agent 机制说明：

```
### 子 agent 机制
- 检查/高危节点（theory_check, numerical_check, update_artifacts, check_iteration）
  自动启动新 CLI 进程执行
- 子 agent context 只含当前节点的输入产物，保持客观性
- 子 agent 的 CLI 和模型可在 workflow.yaml 中按节点配置
- 子 agent 退出后结果写回 state.yaml，主 agent 自然前进
```

## 9. 后续实现步骤

```
Phase 1（MVP）
  1. 实现 workflow.py 的 load/current/done/status 命令
  2. 支持线性 prompt 节点执行
  3. 状态文件创建和更新
  4. 不需要子进程、不需要分支

Phase 2（分支）
  5. 实现 branch 命令
  6. 支持分支路由和 max_retries
  7. 实现 back 命令
  8. 不需要子进程

Phase 3（子进程）
  9. 实现子进程启动机制
  10. 实现输出标记解析
  11. 实现小模型 fallback 提取
  12. 数值检查的脚本验证钩子

Phase 4（自迭代）
  13. update_artifacts 节点完整实现
  14. 工作流文件自修改
  15. SKILL 文件自修改
```
