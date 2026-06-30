# Codex / OpenCode / Claude Code 子 Agent 机制对比

本文记录本次讨论和 Exa 检索得到的结论，重点比较三个 coding-agent 系统的子 agent 细节：Skill 注入、MCP/tool 可见性、嵌套子 agent、权限控制，以及对 SEPR 类三层 agent 架构的含义。

## 一句话结论

Claude Code 的子 agent 政策最不一样：它更偏“启动时把子 agent 的工具面、MCP 和预加载 skill 配齐”，而 Codex / OpenCode 更偏“先暴露 skill metadata 或 tool 描述，再按需加载或调用”。

对三层架构的直觉判断：

- Claude Code：最贴近 `main-agent -> sub-agent -> sub-sub-agent` 原生层级委派。
- Codex：适合主 agent 统一 fan-out 多个子 agent；默认不鼓励子 agent 再委派。
- OpenCode：能做层级委派，但必须严格收紧 `permission.task`，否则有递归风险。

## 总览表

| 维度 | Codex | OpenCode | Claude Code |
|---|---|---|---|
| 子 agent 启动方式 | 用户显式要求 subagents / parallel agents | primary agent 可按描述调用，也可 `@` 手动调用 | 通过 `Agent` tool、`/agents`、SDK、`/fork` 等方式 |
| Skill 默认呈现 | skill metadata：`name` + `description` | `skill` tool 描述中列出 `<available_skills>` | 不以“简介列表注入”为核心机制 |
| 完整 Skill 加载 | progressive disclosure，按需加载 `SKILL.md` | 通过 `skill` tool 按需加载 | `skills:` 字段会在启动时完整预加载指定 skill |
| 未指定 Skill | 可由 agent 根据 metadata 选择加载 | 可由 agent 调 `skill` tool 加载 | 只要 `Skill` tool 可用，仍可发现/调用未预加载 skills |
| MCP / tool | 文档说 `mcp_servers` 可从父会话继承，但公开 issue 显示版本实现可能不稳 | MCP 工具作为普通 tool 受 permission 控制 | 子 agent 默认继承主会话可用 internal tools 和 MCP tools |
| Inline MCP | custom agent 可配置 `mcp_servers` | 通过 OpenCode MCP 配置和权限暴露 | subagent `mcpServers` 可单独声明，启动时连接、结束时断开 |
| 子子 agent | `agents.max_depth` 默认 1，防止更深嵌套 | 取决于 `permission.task`；放开会有递归风险 | v2.1.172 起支持嵌套 subagents，最多 5 层 |
| 禁止继续委派 | 保持 `agents.max_depth=1` 或不提供相关能力 | `permission.task: {"*": "deny"}` | 从 `tools` 省略 `Agent` 或加入 `disallowedTools` |
| 权限风格 | config / sandbox / approval 继承和覆盖 | permission-driven，所有 tool/skill/task 都可 pattern 控制 | tools allowlist、disallowedTools、mcpServers、skills、maxTurns 组合控制 |

## Codex 子 Agent 细节

### Skill

Codex 的 Skill 更像 progressive disclosure：

1. 首先让 agent 看到 skill metadata，主要是 `name` 和 `description`。
2. 当任务匹配时，再加载完整 `SKILL.md`。
3. references、scripts 等资源继续按需读取或运行。

这意味着 Codex 子 agent 通常不需要一开始携带完整 skill 内容；它先拥有“有哪些技能可用”的索引。

### MCP / tool

Codex 官方文档说 custom subagent 的可选字段 `mcp_servers` 和 `skills.config` 在省略时继承父 session。也就是说，设计意图是：不显式覆盖时，子 agent 继承父会话的 MCP 和 skill 配置。

但 Exa 检索到的公开 issue 显示，不同版本或配置中 MCP 继承可能存在实现不一致：

- 有 issue 报告 subagents 没有继承父 session 的 MCP tools。
- 也有 issue 反过来抱怨 subagents 继承 MCP 后缺少 opt-out / 清空继承的机制。

因此在设计上可以认为“Codex 文档语义是继承”，但工程上要做版本实测。

### 嵌套子 agent

Codex 有 `agents.max_depth`：

- root session depth = 0。
- 默认 `agents.max_depth = 1`。
- 默认允许直接 child agent，但阻止更深层嵌套。

所以 Codex 默认不适合让子 agent 自己继续 spawn 子子 agent。更稳妥的用法是：主 agent 负责统一拆分任务，直接 fan-out 多个子 agent，最后汇总。

## OpenCode 子 Agent 细节

### Agent 类型

OpenCode 区分 primary agents 和 subagents：

- primary agents：用户主会话直接交互，例如 Build / Plan。
- subagents：由 primary agents 通过 Task tool 调用，也可由用户用 `@agent` 手动调用。

内置 subagents 包括：

- `general`：复杂问题研究和多步任务，工具面较全。
- `explore`：快速只读代码探索。
- `scout`：外部文档和依赖研究，只读。

### Skill

OpenCode 明确把 available skills 放在 `skill` tool 描述中，格式类似：

```xml
<available_skills>
  <skill>
    <name>git-release</name>
    <description>Create consistent releases and changelogs</description>
  </skill>
</available_skills>
```

因此 OpenCode 的默认模式很清楚：

1. agent 先看到所有允许访问的 skill 名称和描述。
2. 需要时调用 `skill({ name: "..." })` 加载完整内容。
3. 可以通过权限隐藏或禁止某些 skill。

关键配置：

- `permission.skill`：控制 skill allow / ask / deny。
- `tools.skill: false`：完全禁用 skill tool，此时 `<available_skills>` 会被省略。

### MCP / tool

OpenCode 的 MCP 工具进入统一 tool permission 系统。权限匹配底层 tool name，支持通配符，因此可以控制整个 MCP server 或单个 MCP tool。

例如：

- `"mymcp_*": "deny"`：禁用某 MCP server 的所有工具。
- `"mymcp_search": "ask"`：只让某个 MCP tool 需要确认。

### 嵌套子 agent

OpenCode 的子 agent 是否能继续 spawn 子 agent，核心取决于 `permission.task`。

如果某个 subagent 拥有 Task tool，它理论上可以继续调用其他 subagent。公开 issue 中已经出现过“Task tool 导致无限递归”的风险，因此建议：

```json
{
  "agent": {
    "explore": {
      "permission": {
        "task": { "*": "deny" }
      }
    }
  }
}
```

对 SEPR 这类层级架构，如果使用 OpenCode，应采用“默认禁止 task，只有 orchestrator 类 agent 显式允许 task”的策略。

## Claude Code 子 Agent 细节

Claude Code 是三者中政策最不一样的系统。

### Skill

Claude Code 子 agent 的 `skills:` 字段不是简单注入 skill 简介，而是把指定 skill 的完整内容在启动时预加载进子 agent 上下文。

这和 Codex / OpenCode 差异很大：

- Codex / OpenCode：默认先暴露 skill metadata / description，完整内容按需加载。
- Claude Code：`skills:` 中列出的 skill 会启动时完整进入上下文。

但这并不意味着 Claude Code 子 agent 不能使用其他 skills。只要 `Skill` tool 没有被禁用，未列在 `skills:` 中的 project / user / plugin skills 仍可被发现并调用。

因此更严谨的表述是：

> Claude Code 不把“自动注入所有 skill 简介列表”作为主要 subagent skill 机制；它更强调通过 `skills:` 预加载完整 skill 内容，同时保留 `Skill` tool 的按需调用能力。

### MCP / tool

Claude Code 文档明确说：subagents 默认继承 main conversation 可用的 internal tools 和 MCP tools。

控制方式包括：

- `tools`：allowlist，只给指定工具。
- `disallowedTools`：denylist，从继承工具集中移除某些工具。
- `mcpServers`：给某个 subagent 单独声明可用 MCP server。

Claude Code 的 inline `mcpServers` 是偏 eager 的模型：

- subagent 启动时连接。
- subagent 结束时断开。
- 如果希望某个 MCP 不污染主会话，可以只在子 agent 的 `mcpServers` 里声明。

因此可以把 Claude Code 理解为：子 agent 启动时工具面和 MCP 面就已基本配齐，而不是等模型临时发现后再懒加载。

### 嵌套子 agent

Claude Code v2.1.172 起支持 nested subagents，最多 5 层。

如果不希望某个 subagent 继续委派，应显式禁用：

- 从该 subagent 的 `tools` 列表中省略 `Agent`。
- 或把 `Agent` 加入 `disallowedTools`。

Claude Code 更适合自然表达三层委派：

```text
main-agent
  -> sub-agent
       -> sub-sub-agent
```

但这也意味着权限面更复杂。每一层都应明确：

- 可用 `tools`。
- 可用 `mcpServers`。
- 预加载 `skills`。
- 最大轮数 `maxTurns`。
- 是否允许 `Agent` 继续 spawn。

## 对 SEPR / 论文复现 Agent 架构的含义

### 如果选择 Claude Code

Claude Code 最适合当前 SEPR 设想的 3 层 agent 架构：

```text
main-agent：任务编排、状态判断、最终 synthesis
sub-agent：论文参数提取、代码实现、验证、报告等阶段执行
sub-sub-agent：叶子级阅读、局部验证、对抗审查、并行搜索
```

推荐策略：

- main-agent 保留 `Agent`，负责大粒度委派。
- sub-agent 只有在确实需要局部 fan-out 时才保留 `Agent`。
- sub-sub-agent 默认不允许 `Agent`，作为叶子 agent。
- 关键 workflow skill 用 `skills:` 预加载到对应 agent，而不是依赖自然语言触发。
- 高风险 MCP 只挂到需要它的 agent，不要默认给所有层。

### 如果选择 Codex

Codex 更适合固定由主 agent 统一 fan-out：

```text
main-agent
  -> paper-reader
  -> code-explorer
  -> verifier
  -> reviewer
```

不建议默认让 Codex 子 agent 继续 spawn 子子 agent。若确实需要，应先显式调高 `agents.max_depth`，并记录递归深度、工具权限和成本控制策略。

### 如果选择 OpenCode

OpenCode 可做层级委派，但安全默认值应是：

- 所有普通 subagent：`permission.task: { "*": "deny" }`。
- 只有 orchestrator 类 subagent：允许调用有限几个 subagent。
- 每个 subagent 单独收紧 `skill` 和 MCP tool 权限。

OpenCode 的优势是权限模型统一、可控；风险是误开 `task` 后容易递归。

## 最重要的差异总结

最值得记住的几点：

1. Claude Code 的 `skills:` 是完整 skill 预加载，不只是 skill 简介注入。
2. Codex / OpenCode 更偏 skill metadata / description 先可见，再按需加载完整 skill。
3. Claude Code 的 MCP/tool 对子 agent 默认继承，inline MCP 在子 agent 启动时连接，偏 eager。
4. Codex 默认 `max_depth=1`，不鼓励子子 agent。
5. OpenCode 通过 `permission.task` 控制嵌套；误开可能无限递归。
6. Claude Code v2.1.172 起支持最多 5 层 nested subagents，最适合三层 SEPR 设计，但也最需要显式权限收缩。
