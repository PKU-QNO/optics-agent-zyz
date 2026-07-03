# Claude Code Agent Teams 功能核验笔记

> 来源说明：原始内容来自 Gemini 低置信度总结，已按 Claude Code 官方文档重新整理。本文仍是工作笔记，不是项目规则。已核对至官方 ~v2.1.196（code.claude.com/docs/en 的 agent-teams / sub-agents / model-config / hooks），最后核对 2026-07-03；再次改动前请复核最新官方文档。

## 0. 结论摘要

Agent Teams 是 Claude Code 的实验性多会话协作功能。它不是 SEPR 当前三层子 agent 设计的直接替代品，更适合“多个独立 Claude Code 会话需要相互通信、共享任务列表、自主协调”的场景。

对 SEPR 的当前建议：暂不把 Agent Teams 放进主路径。SEPR 近期仍应使用固定三层 subagent 架构：`main/evolution -> sub/sub-e -> leaf`。Agent Teams 可作为后期人工研究工具，用于多视角审查、设计讨论或并行调研，但不应作为可审计论文复现 workflow 的执行底座。

## 1. 已由官方文档明确支持的能力

### 1.1 实验性功能，默认关闭

Agent Teams 默认关闭，需要设置环境变量或 settings：

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

未启用时，Claude 不会创建 team，不会写 team 目录，也不会 spawn 或提议 teammates。

官方明确提示该功能仍有已知限制，尤其涉及 session resumption、task coordination、shutdown behavior。

### 1.2 与 subagents 的核心区别

| 维度 | Subagents | Agent Teams |
|---|---|---|
| 所属范围 | 单个 Claude Code session 内的 delegated workers | 多个协调的 Claude Code sessions |
| 通信方式 | 子 agent 只把 summary 返回给调用者 | teammates 可直接互相通信，也可被用户直接进入对话 |
| 协调方式 | 主会话负责委派与汇总 | lead + shared task list + inter-agent messaging |
| 成本 | 较低，适合隔离搜索/日志/局部任务 | 较高，每个 teammate 是独立 Claude 实例 |
| 适用任务 | 单点隔离任务、并发探索、避免污染主上下文 | 多角色协作、跨层开发、彼此需要讨论和同步的任务 |

### 1.3 启动方式是自然语言，而非显式内部 API

启用 Agent Teams 后，用户用自然语言要求 Claude spawn teammates，例如：

```text
Spawn three teammates to explore this design from UX, architecture, and devil's advocate perspectives.
```

官方文档说明 v2.1.178 后不再需要显式 setup step，`TeamCreate` 和 `TeamDelete` 已移除。旧文档或猜测中出现的 `TeamCreate`、`TeamDelete` 不应写入当前设计。

### 1.4 显示模式

Agent Teams 支持两类显示模式：

| 模式 | 含义 | 备注 |
|---|---|---|
| `in-process` | 所有 teammates 在主终端内运行 | 默认模式，任意终端可用 |
| split panes | 每个 teammate 单独窗格 | 需要 tmux 或 iTerm2 |

可通过 `~/.claude/settings.json` 设置：

```json
{
  "teammateMode": "auto"
}
```

也可单次启动：

```bash
claude --teammate-mode auto
```

官方文档指出 split-pane 不支持 VS Code integrated terminal、Windows Terminal、Ghostty 等环境。对本项目 Windows 主环境而言，不能假设 split panes 可用。

### 1.5 基本交互键位

在 `in-process` 模式中，官方文档给出的交互包括：

| 操作 | 作用 |
|---|---|
| Up / Down | 在 agent panel 中选择 teammate |
| Enter | 打开选中 teammate 的 transcript 并直接发送消息 |
| Escape | 中断选中 teammate 当前轮次 |
| x | 停止选中的 teammate |
| Ctrl+T | 切换 task list 显示 |

注意：不要写成 `Shift+Up/Down` 或“拓扑图快捷键”，除非后续官方文档再次确认。

### 1.6 shared task list 与任务状态

Agent Teams 使用 shared task list 协调 work。官方文档确认 task 有 `pending`、`in progress`、`completed` 三类状态，并支持 dependencies。pending task 若依赖未完成，不能被 claim。

Agent Teams 的状态文件是**用户级**、按 session 派生名存储（`session-` + sessionID 前 8 位）：

- team config：`~/.claude/teams/{team-name}/config.json`
- task list：`~/.claude/tasks/{team-name}/`

官方明确：**不要手工编辑或预写**这些文件，下一次状态更新会覆盖你的改动；task 状态可“手动更新”，但走 lead / UI，不是靠改 JSON。项目级 `.claude/teams/*.json` **不被识别为配置**，Claude 只当普通文件。因此不存在“手改项目级 tasks.json 热篡改状态”的官方入口。

### 1.7 teammate 模型与 effort

官方文档说明：teammates 默认不继承 lead 的 `/model` 选择。若 prompt 未指定 teammate 模型，可在 `/config` 里设置 Default teammate model；也可选择 Default 让 teammates 跟随 lead 当前模型。

官方说明：teammates 继承 lead 的 effort level（通用行为）；其中 **split-pane 模式**自 v2.1.186 起才传递 effort，更早版本不向 split-pane teammate 传 lead 的 session effort。

### 1.8 plan approval

Agent Teams 可要求 teammates 在实施前先 plan。teammate 在 read-only plan mode 中工作，计划提交给 lead 审查。lead 可以 approve 或 reject；reject 后 teammate 继续改计划，approve 后才退出 plan mode 开始实现。

这对 SEPR 的启发是：如果未来用 Agent Teams 做设计审查，应该强制 plan approval，并把“必须包含验证方法、回滚策略、不会修改规则文件”作为 lead 审批标准。

### 1.9 hooks quality gates

官方文档提到可用 hooks 对 Agent Teams 质量门禁做约束：

| Hook | 触发点 | 用途 |
|---|---|---|
| `TeammateIdle` | teammate 即将 idle | 退出码 2 可反馈并要求继续工作 |
| `TaskCreated` | task 创建时 | 可阻止不合规 task 创建 |
| `TaskCompleted` | task 标记完成时 | 可阻止低质量完成声明 |

这比“手工篡改状态文件”更接近官方支持的治理入口。

## 2. 原始 Gemini 文档中应删除的说法

以下内容目前没有官方依据，或已被官方文档明确否定，不应进入 SEPR 设计：

| 原说法 | 处理 |
|---|---|
| `TeamCreate` / `TeamDelete` 是当前核心 API | 删除。官方称 v2.1.178 后已移除 |
| `TaskCreate` / `TaskUpdate` / `TaskList` / `SendMessage` 是可**人类**直接调用的公开 API | 降级。`SendMessage` 与任务管理工具是 **teammate 侧内建 agent 工具（真实存在、始终可用）**，但不是人类直接调用的稳定接口；SEPR 不要把它们当可编排的外部 API。仅 `TeamCreate`/`TeamDelete` 是真正已移除 |
| 可直接编辑 `.claude/teams/<team_id>/tasks.json` 热篡改状态 | 删除。真实路径是 `~/.claude/teams/{name}/config.json` + `~/.claude/tasks/{name}/`（用户级、session 派生名），官方禁止手改且会被覆盖；项目级 `.claude/teams/*.json` 不被识别 |
| `Shift+Up/Down` 切换 teammate | 改为官方 Up/Down |
| `Ctrl+T` 显示任务依赖拓扑图 | 改为 task list toggle；不要声称有拓扑图 |
| Agent Teams 可作为 zero-touch 黑盒长期自动流水线 | 删除或降级。官方标实验性且有恢复、协调、关闭限制 |
| 可让某 teammate 独占某 MCP 作为稳定隔离 enclave | 删除。官方：subagent 定义作为 teammate 运行时 `skills`/`mcpServers` 被忽略，teammate 的 MCP/skills 一律从项目+用户设置加载，无法给单个 teammate 独占 MCP |

## 3. 对 SEPR 的设计启发

### 3.1 不把 Agent Teams 放进主执行路径

SEPR 的论文复现需要可审计、可 replay、可控 fan-out。Agent Teams 的共享任务列表和 teammate 自协调会增加不确定性，不适合当前 Mie 第一阶段复现主路径。

当前 SEPR 更适合：

```text
main-agent -> sub-agent -> leaf subsubagent
evolution-agent -> sub-e-agent -> leaf subsubagent
```

Agent Teams 可作为“人工打开的研究/审查模式”，而不是 workflow 的固定执行机制。

### 3.2 可借鉴但要脚本化的部分

Gemini 原文提到的 contract-first 和 QA gate 是合理设计思想，但不是 Agent Teams 独有功能。SEPR 应通过确定性脚本和 human gate 实现：

| 需求 | SEPR 推荐实现 |
|---|---|
| 接口/参数契约 | `formalization/*.yaml`、`benchmark.yaml`、typed blueprint schema |
| 输出格式约束 | markdown/schema validator、quick_validate、报告模板字段检查 |
| 防止假完成 | result_class + verifier + human gate |
| 并发任务不踩文件 | 每个 sub-agent 独立 `.work/.todo/<paper>/<case>/<step>/` 路径 |
| 多视角审查 | 多个 sub-agent 或后期人工 Agent Teams 审查，不自动写正式规则 |

### 3.3 若未来试用 Agent Teams 的安全边界

如果未来在 SEPR/optics_agent 中实验 Agent Teams，建议只用于下列低风险任务：

| 可尝试 | 不建议 |
|---|---|
| 多视角审查 SEPR 设计文档 | 实际跑论文复现主路径 |
| 并行读文献并产独立观点 | 自动改 `.claude/skills/` 或 `CLAUDE.md` |
| 对一个复现报告做 devil's advocate | 提交 Magnus/COMSOL 作业 |
| 比较多个候选 workflow 策略 | 直接判定 physical_reproduction_success |

必须设置：plan approval、明确文件所有权、禁止改规则文件、禁止提交高风险作业、所有结论回到主 agent/human gate。

## 4. 仍需官方核验的问题

请后续让 `claude-code-docs-agent` 重点确认：

1.（已解答）teammate 复用 subagent 定义时，官方**只应用 `tools` allowlist 与 `model`**；`skills`、`mcpServers` frontmatter **被忽略**，teammate 的 skills/MCP 一律从项目+用户设置加载，无法给单个 teammate 独占 MCP。permission 在 spawn 时统一继承 lead，**不能设 per-teammate permissionMode**。
2.（已解答）teammate 不继承 lead 的会话历史，但加载相同项目上下文（CLAUDE.md、MCP、skills）；不存在“按 teammate 限定 MCP”的官方机制。此外官方硬限制：一个 session 只有一个 team、lead 固定、**teammate 不能再 spawn teammate（无嵌套 team）**，故 Agent Teams 无法替代 SEPR 的多层 fan-out。
3. shared task list 的底层文件是否有官方支持的可读 artifact 路径；是否允许用户编辑，或只能通过 UI/hooks/lead 自然语言控制。
4. `TaskCreated`、`TaskCompleted`、`TeammateIdle` hook payload 的正式字段名和可阻断语义。
5. Windows + PowerShell + Windows Terminal 环境下，Agent Teams 的可用模式、键位和限制。
6. teammate shutdown、session resume、rewind 的最新限制是否仍与当前文档一致。

## 5. 当前置信度

| 内容 | 置信度 |
|---|---|
| 实验性、默认关闭、启用变量 | 高 |
| subagents vs Agent Teams 区别 | 高 |
| in-process / split panes 模式 | 高 |
| Up/Down、Enter、Escape、x、Ctrl+T task list | 中高，需按实际版本复核 |
| shared task list、三状态、dependencies | 高 |
| teammate 模型默认不继承 lead `/model` | 高 |
| plan approval | 高 |
| hooks gate | 中高，payload 细节需核验 |
| teammate MCP 隔离/独占访问 | 低，需官方核验 |
| 手工编辑 team 状态文件 | 极低，不采用 |
