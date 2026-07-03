# Claude Code Subagents 预配置与嵌套能力核验笔记

> 来源说明：原始内容来自 Gemini 低置信度总结，已按 Claude Code 官方文档重新整理。本文用于 SEPR 设计核验，不是最终项目规则。使用前请让 `claude-code-docs-agent` 再次核对最新官方文档。

## 0. 结论摘要

Claude Code custom subagents 适合 SEPR 当前设计：用 `.claude/agents/*.md` 定义项目级 agent，通过 `name`、`description`、`tools`、`disallowedTools`、`model`、`skills`、`maxTurns` 等 frontmatter 控制角色、工具、模型和上下文。官方已支持 nested subagents，最多 5 层。SEPR 只使用 3 层是保守且合理的。

对 SEPR 的直接建议：保留 `.claude/agents/` + `.claude/skills/` 双层结构；把调用名统一为 lowercase hyphen-case；对第 3 层 leaf 省略 `Agent` 工具；尽量用 `skills:` 预加载关键 skill，而不是指望子 agent 运行后总能主动加载。

## 1. Subagent 定义位置与优先级

Claude Code subagents 是带 YAML frontmatter 的 Markdown 文件，可位于多个 scope。官方文档给出的优先级大致为：

| 位置 | 作用 | 优先级 |
|---|---|---|
| managed settings | 组织级 | 最高 |
| `--agents` CLI flag | 当前 session | 高 |
| `.claude/agents/` | 当前项目 | 项目级 |
| `~/.claude/agents/` | 用户全局 | 用户级 |
| plugin `agents/` | 插件 | 较低 |

项目级 `.claude/agents/` 适合 SEPR，因为 agent 身份强绑定当前 workspace。

官方要求 `name` 使用 lowercase letters and hyphens。文件名可以不同，但实际身份来自 frontmatter 的 `name`。因此 SEPR 应避免用 `sub-E-agent` 作为调用名，统一调用 `sub-e-agent`。

## 2. Frontmatter 字段

官方文档说明 file-based subagents 支持的字段包括：`name`、`description`、`tools`、`disallowedTools`、`model`、`permissionMode`、`mcpServers`、`hooks`、`maxTurns`、`skills`、`initialPrompt`、`memory`、`effort`、`background`、`isolation`、`color`。

SEPR 当前最相关字段：

| 字段 | 用途 | SEPR 建议 |
|---|---|---|
| `name` | subagent 标识符 | 必须 lowercase hyphen-case，如 `sub-e-agent` |
| `description` | Claude 判断何时委派 | 写清触发条件和禁止场景 |
| `tools` | allowlist 工具 | 编排/执行层可含 `Agent`，leaf 不含 `Agent` |
| `disallowedTools` | denylist 工具 | 可禁 `NotebookEdit`、不需要的 MCP |
| `model` | 指定模型 alias 或完整 ID | 可用 `inherit`、`sonnet`、`opus`、`haiku` 等 |
| `maxTurns` | 最大 agentic turns | SEPR 编排层 50、执行层 15 合理 |
| `skills` | 启动时预加载 skill 完整内容 | 建议给 4 个核心 agent 加对应 skill |
| `permissionMode` | 权限请求模式 | 保守使用 `default` 或 plan/read-only 流程 |

## 3. 模型选择规则

官方文档给出 subagent 模型解析顺序：

1. `CLAUDE_CODE_SUBAGENT_MODEL` 环境变量，若设置为模型 alias 或模型 ID。
2. 每次调用 Agent 时的 per-invocation `model` 参数。
3. subagent definition 的 `model` frontmatter。
4. main conversation 的模型。

官方还说明 v2.1.196 起，`CLAUDE_CODE_SUBAGENT_MODEL=inherit` 等价于未设置；早期版本中 `inherit` 可能强制所有 subagents 使用主对话模型并忽略 invocation/frontmatter。

因此，原文“Env > Invocation Param > Agent Config > Main Agent Model”这个顺序总体与当前官方文档一致，但必须补充版本差异，且不能声称所有版本都严格一致。

## 4. `opusplan` 的正确理解

官方文档确认 `opusplan` 是**真实存在的 model alias**：plan mode 用 `opus` 做复杂推理/架构决策，进入 execution 时**自动切换到 `sonnet`** 做实现。原始 Gemini 的描述是对的，无需存疑。

正确的限定只有一条：`opusplan` 是**会话级 model setting**（`/model opusplan` 或 settings），不是 per-subagent 的 workflow 机制。若 SEPR 要按 agent 做高推理/低成本分工，仍应用各 subagent 的 `model` 字段或 per-invocation `model`，而不是指望 `opusplan` 去按“编排层/执行层”分流。边界：`availableModels` 排除 Opus 时 `opusplan` 在 plan mode 也留在 Sonnet；需两阶段都 1M 用 `opusplan[1m]`。

## 5. Skills 与子 agent

官方文档说明 subagent 可通过 `skills` 字段在启动时预加载 skill 完整内容。这个字段控制预加载，不等于限制可访问 skill。

如果 subagent 工具中包含 `Skill`，即使未列在 `skills:` 中，也仍可在执行期间调用项目、用户或插件 skills。若要防止 subagent 调用 skills，应从 `tools` 中移除 `Skill` 或加入 `disallowedTools`。

对 SEPR 的建议：

```yaml
---
name: sub-agent
description: SEPR paper-reproduction execution subagent for one assigned workflow step.
tools: Read, Write, Edit, Bash, Glob, Grep, Skill, Agent
skills:
  - sub-agent
  - optics-mie-reproduction
model: inherit
maxTurns: 15
---
```

这比要求子 agent 自己先运行 `skill-print.py` 再手动读取 skill 更稳。但是否同时保留 `skill-print.py` 作为兜底，需要实际测试。

## 6. 嵌套 subagents

官方文档明确支持 nested subagents。深度计数为 main conversation 下的 subagent levels，不区分 foreground/background。深度为 5 的 subagent 不会收到 `Agent` 工具，因此不能继续 spawn。该限制固定且不可配置。

允许某 subagent 继续 spawn 的条件：它必须可用 `Agent` 工具。阻止继续 spawn 的方式：从 `tools` 中省略 `Agent`，或用 `disallowedTools` 禁止。

SEPR 的三层限制是保守设计：

```text
main-agent / evolution-agent     depth 0, 编排层
  -> sub-agent / sub-e-agent     depth 1, 执行层，允许 spawn leaf
       -> leaf subsubagent       depth 2, 叶子层，不允许再 spawn
```

注意：官方最多 5 层不代表 SEPR 应用满 5 层。科学复现场景中，3 层更可控、更容易审计。

## 7. 上下文隔离

官方文档说明 subagent 收到自己的 system prompt、Agent tool prompt、项目 `CLAUDE.md`、可用工具定义；不接收父对话历史或父工具结果。除非通过 `skills` 字段预加载，否则不接收父会话中已加载的 skill 完整内容。

subagent 完成后只把最终结果返回给调用者。这个机制正适合 SEPR：用 subagent 隔离 PDF 读取、搜索、日志、验证输出，避免污染 main-agent 的上下文。

风险：如果父 agent 没有在 spawn prompt 中给足输入路径、任务边界、输出 schema、禁止动作，子 agent 会缺上下文而猜测。因此 SEPR 的 spawn template 仍然必要。

## 8. 工具限制与 MCP 注意事项

官方文档支持 `tools` allowlist 和 `disallowedTools` denylist。`mcp__server` 或 `mcp__server__*` 可用于移除某个 MCP server；`mcp__*` 可移除所有 MCP tools。

对 SEPR 的关键影响：如果 agent frontmatter 写 `disallowedTools: mcp__*`，就不要在该 agent 的 skill 或 spawn template 中要求它调用 memento MCP。否则规则自相矛盾。

可选设计：

| 方案 | 做法 | 适用 |
|---|---|---|
| 父 agent 代记忆 | 父 agent 调 memento，子 agent 只写 `memory_search_summary` 和待存草稿 | 最安全，子 agent 无 MCP |
| 显式开放 memento | 不用 `mcp__*` 全禁，改为只禁无关 MCP，或显式 allow memento 工具 | 需要子 agent 自己读写记忆 |
| 全禁 MCP | 子 agent 只做文件/脚本任务，不写长期记忆 | 叶子层最适合 |

## 9. Agent Teams 与 subagents 的关系

Agent Teams 是另一套实验性多会话协作机制。它使用 lead、teammates、shared task list、inter-agent messaging。它不等价于 nested subagents，也不应混入 SEPR 当前 `.claude/agents/` 三层设计。

当前建议：SEPR 主路径用 custom subagents；Agent Teams 仅作为后期人工打开的审查/研究模式。

## 10. CLI 适配器 agent 的可行性与风险

用 custom subagent 包装外部 CLI 是可行思路，但不应声称它会“真正无干预自愈”。建议写成保守模式：

```yaml
---
name: chart-cli-adapter
description: Use only to run the approved chart analysis CLI on explicitly provided local image paths and return compact structured results.
tools: Bash
model: haiku
maxTurns: 5
---
```

安全要求：

1. 只允许运行白名单命令。
2. 输入路径必须由父 agent 提供，不能自行扫描 secret/private 路径。
3. CLI 输出必须压缩成结构化 JSON/Markdown 摘要。
4. 报错最多重试有限次数，且每次重试必须有新假设。
5. 不允许执行 `rm`、`mv`、`curl`、`scp`、`git push` 等无关或破坏性命令。

## 11. 对 SEPR `.claude/agents` 的具体建议

1. 统一调用名：`sub-E-agent` 显示名可以保留，但 frontmatter `name` 和所有 spawn 指令应统一为 `sub-e-agent`。
2. 给核心 agent 加 `skills:` 预加载，至少：`main-agent` 预加载 `main-agent`；`sub-agent` 预加载 `sub-agent` 和当前领域 skill；`evolution-agent` 预加载 `evolution-agent`；`sub-e-agent` 预加载 `sub-e-agent`。
3. 明确 memento 策略，避免 `disallowedTools: mcp__*` 与 memory rules 冲突。
4. 第 3 层 leaf agent 的 `tools` 必须省略 `Agent`。
5. 保持 `maxTurns`：编排层 50、执行层 15、叶子层 15 或更低。
6. 不使用 5 层嵌套；5 层是上限，不是推荐深度。

## 12. 仍需官方核验的问题

请让 `claude-code-docs-agent` 重点确认：

1. `skills:` 字段在 file-based `.claude/agents/*.md` 中的准确 YAML 写法，是否为列表，是否用 skill name 而非路径。
2. `Skill` 工具名在 `tools` allowlist 中是否仍是正确写法；是否需要 `Skill(<name>)` specifier 控制。
3. `CLAUDE_CODE_SUBAGENT_MODEL` 与 per-invocation `model` 参数的最新优先级，特别是 v2.1.196 后 `inherit` 的行为。
4. nested subagents 的 depth 计数、background 子 agent 恢复后 depth 是否固定、是否仍最高 5 层。
5. custom subagents 是否在当前版本稳定继承/使用 MCP tools、ToolSearch 和 Skill；若存在版本 bug，应记录 workaround。
6. `permissionMode`、`mcpServers`、`isolation: worktree` 在 file-based subagents 中的实际支持范围和限制。

## 13. 当前置信度

| 内容 | 置信度 |
|---|---|
| `.claude/agents/*.md` frontmatter 支持 | 高 |
| 模型解析顺序 | 高，但版本差异需标注 |
| `skills:` 可预加载 skill 完整内容 | 高，需核验 YAML 示例 |
| nested subagents 最多 5 层 | 高 |
| 省略/禁用 `Agent` 可阻止继续 spawn | 高 |
| 子 agent 上下文隔离与只返回 summary | 高 |
| Agent Teams 与 subagents 不同 | 高 |
| CLI adapter agent 可行 | 中，安全策略需实测 |
| `opusplan` = plan 用 Opus、execution 自动切 Sonnet | 高（官方 model-config 明确；属会话级 setting，非 per-subagent 机制） |
