# Codex custom agents 与 CLI 调用能力核验

日期：2026-07-05  
本机版本：`codex-cli 0.141.0`  
结论类型：公开文档 + 官方仓库源码 + 本机 CLI 帮助交叉核验

## 结论

Codex 可以预制类似 Claude Code `.claude/agents/` 的 agent 模板，但 Codex 的原生格式不是 Markdown frontmatter，而是 TOML：

```text
~/.codex/agents/*.toml       # 个人级 custom agents
.codex/agents/*.toml         # 项目级 custom agents
```

Codex CLI 支持 subagent workflow，当前本机 `codex features list` 显示 `multi_agent` 为 `stable true`。但 CLI 帮助中没有发现 `codex --agent <name>` 或 `codex exec --agent <name>` 这种直接指定 agent 启动的参数。实际调用方式是：让父 agent 在 prompt 中显式 spawn/use 某个 custom agent；交互 CLI 里用 `/agent` 管理和切换已经生成的 agent thread。

## 与 Claude Code 的差异

| 能力 | Claude Code | Codex |
|---|---|---|
| 预制 agent 目录 | `.claude/agents/*.md` | `.codex/agents/*.toml` 或 `~/.codex/agents/*.toml` |
| 文件格式 | Markdown + YAML frontmatter | TOML config layer |
| 直接启动参数 | Claude Code 有 `--agent` 类用法 | Codex CLI 未见 documented `--agent` |
| 运行方式 | 选择指定 agent 身份执行 | 父 Codex session 显式 spawn 子 agent |
| 管理界面 | Claude Code agent/session 机制 | Codex CLI `/agent` 切换 active agent thread |

## Codex custom agent 最小 schema

每个 standalone agent 文件必须包含：

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
developer_instructions = """
Review code like an owner.
Prioritize correctness, security, behavior regressions, and missing test coverage.
Lead with concrete findings and cite files.
"""
```

常用可选项：

```toml
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"
nickname_candidates = ["Atlas", "Delta", "Echo"]
```

也可以像普通 `config.toml` 一样给某个 agent 增加 MCP 或 skill 配置，例如：

```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

## CLI 调用方式

交互 CLI：

```text
Review this branch against main. Spawn the reviewer custom agent to inspect correctness and missing tests, then summarize findings.
```

查看或切换已 spawn 的 agent thread：

```text
/agent
```

非交互 CLI 也可以通过 prompt 触发：

```powershell
codex exec "Review this branch against main. Spawn the reviewer custom agent and summarize findings."
```

注意：`/agent` 是管理已存在的子 agent thread，不是“用某个 agent 开新会话”的 shell 参数。

## 官方内置 agent

Codex 文档列出内置 agent：

- `default`：通用 fallback agent
- `worker`：偏执行、实现和修复
- `explorer`：偏只读探索和代码库理解

如果自定义 agent 的 `name` 与内置 agent 同名，例如 `explorer`，自定义 agent 会优先生效。

## 对 optics_agent / SEPR 的建议

1. 如果要把 SEPR 的 `.claude/agents/*.md` 迁移到 Codex，应生成对应 `.codex/agents/*.toml`，不要直接复用 Markdown 文件。
2. Codex agent 文件适合表达“角色 + 模型 + sandbox + MCP/skills”，不适合承载过长的 workflow 说明；长流程仍应放在 `AGENTS.md`、skill 或 notes 中，再由 agent 引用。
3. Codex 没有已核验的 `--agent` 直启入口，因此自动化脚本里不要设计成 `codex exec --agent reviewer ...`。可靠写法是把“spawn reviewer”写入 prompt。
4. 对 SEPR 这种多 agent workflow，Codex 版应按“父 session 调度 custom agents”的模型设计，而不是照搬 Claude Code 的 agent 启动语义。

## 证据来源

- Codex 官方文档：`https://developers.openai.com/codex/subagents.md`
- Codex CLI slash commands：`https://developers.openai.com/codex/cli/slash-commands.md`
- 官方仓库源码：`openai/codex`
  - `codex-rs/core/src/config/agent_roles.rs`
  - `codex-rs/config/src/config_toml.rs`
  - `codex-rs/tui/src/slash_command.rs`
  - `codex-rs/app-server/src/config/external_agent_config_tests.rs`
- 本机命令核验：
  - `codex --version` -> `codex-cli 0.141.0`
  - `codex --help`
  - `codex exec --help`
  - `codex features list`
