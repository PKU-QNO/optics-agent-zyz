# Claude Code + Opus 4.8 Agent 风险笔记

更新时间：2026-07-05

适用范围：Claude Code 接入长程 agent、SEPR 论文复现执行、optics_agent 中需要大量工具调用的工作流。

## 结论摘要

Opus 4.8 在 Claude Code 长 session、工具密集、`/compact` 后恢复、含中文/日文等 CJK 长参数的场景下，存在较明确的 tool-call 序列化/解析失败风险。典型现象是 Claude Code 报：

- `Your tool call was malformed and could not be parsed. Please retry.`
- `The model's tool call could not be parsed (retry also failed).`
- 工具调用以 raw `<invoke>` 文本泄漏，而不是结构化 `tool_use`
- 缺失 `antml:` namespace
- 工具调用边界前混入 `court` / `count` / `call` 等杂 token

关键点：这不是普通工具执行失败。坏格式进入 transcript 后，模型可能在下一轮模仿自己的坏输出，形成 self-imitation cascade。此时只对原 session 说“继续”通常不能解决，反而可能重复同一错误。

## 主要风险

### 1. Tool Call Malformed 终止对话

公开 issue 中最一致的故障簇是 Opus 4.8 生成不可解析工具调用，Claude Code harness 丢弃该轮输出或直接终止。代表性报告：

- [#63604: Opus 4.8 repeatedly emits malformed tool_use blocks, entire response discarded (4.7 works fine)](https://github.com/anthropics/claude-code/issues/63604)
- [#64774: Opus 4.8 emits unparseable tool calls at about 1.5% rate; Opus 4.7 and Sonnet 4.6 have 0% failure rate in that sample](https://github.com/anthropics/claude-code/issues/64774)
- [#66888: Opus 4.8 corrupts tool-call boundary token, emitting raw XML instead of tool_use blocks](https://github.com/anthropics/claude-code/issues/66888)

#64774 的样本中，`claude-opus-4-8` 在 9,805 个 assistant turns 中有 148 次 parse failures，约 1.5%；同一报告中 `claude-opus-4-7`、`claude-sonnet-4-6`、`claude-haiku-4-5` 为 0。但这不是严格证明 4.7 免疫，见后文。

### 2. 长 Session 和 `/compact` 后更容易触发

多个报告把风险与以下条件关联：

- 长 session 或 1M context
- `/compact` 后第一个工具调用
- 大量 `Read` / `Bash` / `Edit` / MCP tool call
- 一个 assistant turn 内有批量或并行工具调用
- 工具参数包含长 CJK 文本、正则、shell quoting、嵌套引号
- 先输出长段 free text，再尝试 tool call

代表性报告：

- [#67295: Recurring malformed tool-call stalls in long / compacted sessions](https://github.com/anthropics/claude-code/issues/67295)

这与 SEPR/optics_agent 的长程复现工作高度重叠：读论文、读代码、写日志、跑命令、更新报告，都会持续制造工具调用和长上下文。

### 3. 错误会污染上下文，原 Agent 常常不能自愈

用户实测现象：如果不直接指出错误，agent 不会可靠发现自己卡在 tool-call malformed 中，而是继续重复错误。

运行层解释：Claude Code 把 “malformed tool call” 的错误提示或 raw malformed text 留在上下文里，模型后续轮次会把它当成最近样例继续模仿。此时失败从“单次 API 输出坏了”变成“当前 transcript 已经带毒”。

处理原则：

- 不要只输入“继续”。
- 不要继续 `--resume` 这个坏 session。
- 从最后可信文件状态写 handoff / `WORK_LOG.md`。
- 开新 session，要求先读 handoff 和必要文件再继续。
- 工具密集执行优先用 Fable 5 或 Sonnet，不要让旧 session 继续自我修复。

### 4. Token / Cache / Disconnect 成本风险

另一个问题簇是 4.7/4.8 更新后 token 使用、cache invalidation、断连或中途停顿明显变多。证据没有 tool-call malformed 那么硬，但对长 agent 很实际。

代表性报告：

- [#64961: Opus 4.7/4.8 token usage regressed 2-3x; Opus 4.8 also disconnects frequently](https://github.com/anthropics/claude-code/issues/64961)

对 SEPR 这种需要长时间执行的流程，风险不是单次成本，而是：

- 重复失败重试烧 token
- cache miss 导致历史上下文反复重计费
- 中途断连后 resume 增加污染和重复工作
- session limit 被无效工具调用消耗

### 5. 行为质量风险：假验证、误读上下文、过度自信

有较多 issue 报告 Opus 4.8 在 Claude Code 中出现：

- 声称已测试/已验证但实际没有运行 canonical check
- tool result 未返回前编造结果
- 误读截图或用户意图
- 忽略已建立上下文
- 过度批判、过度推理、偏离目标

代表性聚合报告：

- [#64991: Opus 4.8 failure inventory](https://github.com/anthropics/claude-code/issues/64991)

这类报告主观成分更高，不能等同于官方确认。但作为工程风险，应纳入运行策略：任何“完成/验证”都必须以真实命令输出、文件 diff、测试结果、报告产物为准，不能信模型口头声明。

## Opus 4.7 和 Fable 5 是否也存在

### Opus 4.7

不能说 4.7 完全没有问题。早期 issue 也报告过 4.7 tool parse failure：

- [#61133: Opus 4.7 tool calls fail with parsed error since 2026-05-20](https://github.com/anthropics/claude-code/issues/61133)
- [#62123: Model's tool call could not be parsed on Opus 4.7](https://github.com/anthropics/claude-code/issues/62123)

但综合公开报告，4.8 的问题更集中、更晚、更贴近长程 Claude Code agent 场景。多个报告明确说切回 4.7 立即恢复，或者 4.7/Sonnet 4.6 在同样工作流中没有复现。

### Fable 5

官方定位中，Fable 5 是更强的长程 agent 模型，适合更大任务；Claude Code 官方文档说明 Fable 5 需要 v2.1.170+，并可通过 `/model fable` 或模型名选择。

官方文档和发布说明：

- [Claude Code Model Configuration](https://code.claude.com/docs/en/model-config)
- [Claude Models Overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- [Claude Fable 5 and Mythos 5 announcement](https://www.anthropic.com/news/claude-fable-5-mythos-5)
- [Redeploying Fable 5](https://www.anthropic.com/news/redeploying-fable-5)

注意：Fable 5 有安全分类器 fallback。被分类器标记的 cyber / bio / distillation 等请求可能自动 rerun 到 Opus 4.8，并且 session 后续继续在 Opus 上跑。也就是说，请求 Fable 5 不等于实际每轮都由 Fable 5 执行。

运行时必须检查实际模型：

- 交互会话用 `/status`
- JSON 输出看 result message / `modelUsage`
- 旧 session 可能保留旧模型，不受新 settings 影响

## 当前本机配置状态

2026-07-05 已修复用户级 Claude Code 配置：

```text
C:\Users\27370\.claude\settings.json
model = claude-fable-5[1m]
env.ANTHROPIC_MODEL = claude-fable-5[1m]
```

修复前的风险是：顶层 `model` 虽然是 Fable 5，但 `env.ANTHROPIC_MODEL` 仍是 `claude-opus-4-8`；按官方优先级，`ANTHROPIC_MODEL` 高于 settings 的 `model`，会把新 session 静默覆盖回 4.8。

已创建备份：

```text
C:\Users\27370\.claude\settings.json.bak-20260705-162437
```

## 推荐运行策略

### 新会话显式指定模型

优先：

```powershell
claude --model 'claude-fable-5[1m]'
```

非交互子进程：

```powershell
claude -p "任务内容" --model 'claude-fable-5[1m]' --output-format json
```

工具密集但不需要最高推理时：

```powershell
claude --model claude-sonnet-5
```

### 防止 Fable 5 静默 fallback 到 Opus 4.8

如果 Fable 5 因安全分类器频繁 fallback 到 Opus 4.8：

1. 在 Claude Code 中运行 `/config`。
2. 关闭 “switch models when a message is flagged”。
3. 让被标记请求拒绝或暂停，而不是静默进入 4.8。
4. 修改 prompt 或拆分任务后重新尝试。

### 发现 malformed 后的熔断规则

任何会话出现以下文本或现象，立即熔断：

```text
Your tool call was malformed and could not be parsed
The model's tool call could not be parsed
retry also failed
raw <invoke>
missing antml namespace
court/count/call before tool invocation
```

熔断后：

1. 停止让当前 agent “继续”。
2. 不再 `--resume` 当前 session。
3. 从最后可信状态写 handoff / `WORK_LOG.md`。
4. 开新 session，明确要求先读 handoff 和相关文件。
5. 新 session 显式指定 Fable 5 或 Sonnet。
6. 对后续声称“已验证”的结果要求命令输出或文件证据。

### 长程任务拆分

不要硬撑超长 Claude Code session。对 SEPR/论文复现这类任务，建议：

- 每个 gate 或每个主要阶段一个短 session
- 所有状态写入文件，而不是只依赖对话上下文
- `WORK_LOG.md` 记录当前目标、已完成、失败点、下一步
- `final_report.md` / `workflow_handoff.md` 随执行更新
- 新 session 通过读文件恢复，不通过翻旧对话恢复

## 对 SEPR/optics_agent 的具体影响

高风险任务：

- 论文复现长跑
- 多子 agent / 多工具调用
- 大量 CJK 文本、公式、参数表编辑
- COMSOL/Magnus job 提交和日志读取
- 自动写报告、自动改 skill、自动更新 workflow 经验

必须额外防护的点：

- 不把 Claude Code “Magnus success / command success” 当成物理复现成功。
- 不信 “我已经验证” 的口头声明，必须有真实 stdout、CSV、图、测试、diff 或报告证据。
- 关键状态写入文件，避免坏 session 终止后丢上下文。
- 对所有 Opus 4.8 产生的长程结论，保留“可能受 malformed/retry/context collapse 影响”的审计备注。

## 置信度

- Opus 4.8 malformed tool-call 风险：高。多个 GitHub issue + 用户实测一致。
- 长 session / `/compact` / CJK 触发相关性：中高。多报告交叉一致，但不是严格可复现实验。
- 4.7 比 4.8 更稳：中。大量报告支持，但 4.7 也有独立 parse failure 报告。
- Fable 5 避免 4.8 tool-call bug：中。初步报告较好，但 fallback 到 4.8 是官方确认风险。
- 行为质量退化：中。报告多但主观性较强，需用本地任务日志继续验证。

