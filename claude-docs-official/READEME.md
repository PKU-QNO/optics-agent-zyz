# Claude Code 官方文档总阅读引导

本目录是 `claude-docs-official` 的本地整理版，用来快速理解 Claude Code 的核心机制、使用方法、配置体系和高级扩展能力。官方完整文档索引见：<https://code.claude.com/docs/llms.txt>。

> 注意：本文件按用户要求命名为 `READEME.md`。若后续需要让 GitHub 自动识别，可另建或重命名为 `README.md`。

## 一句话理解

Claude Code 不是普通聊天助手，而是一个运行在开发环境中的 agentic coding tool：它会读取代码库、搜索文件、编辑文件、运行命令、调用外部工具，并通过“收集上下文 -> 执行动作 -> 验证结果”的循环完成开发任务。

最重要的心智模型：上下文窗口是核心资源，权限模式决定安全边界，`CLAUDE.md`/rules/skills/MCP/hooks/subagents 是扩展层。

## 推荐阅读顺序

### 1. 快速上手

先读：

- `get-started/overview.md`
- `get-started/quick-start.md`

重点掌握：

- Claude Code 可在 Terminal、VS Code、JetBrains、Desktop、Web、CI/CD 等界面使用。
- 终端基本入口是 `claude`，一次性任务可用 `claude "task"` 或 `claude -p "query"`。
- 初学流程是安装、登录、进入项目目录、询问代码库结构、让 Claude 做第一个小改动、再学习 Git/测试/文档等常见任务。
- `claude --version` 用于检查版本，`/help` 查看会话内命令，`/login` 切换或重新认证。

适合目标：确认 Claude Code 能做什么，以及如何开始一个本地项目会话。

### 2. 核心工作机制

再读：

- `core-concepts/How-Claude-Code-works.md`
- `core-concepts/Explore-the-context-window.md`
- `core-concepts/How-Claude-Code-uses-prompt-caching.md`

重点掌握：

- Agentic loop：Claude 会反复收集上下文、采取行动、验证结果。
- Claude 可访问当前项目文件、终端、Git 状态、`CLAUDE.md`、auto memory、MCP/skills/subagents 等扩展。
- 会话是独立的，历史存储在本地 JSONL transcript 中，可 resume、fork、branch。
- 上下文包含系统提示、项目说明、memory、技能描述、MCP 工具名、文件读取结果、命令输出等。
- `/context` 用于查看上下文占用，`/compact` 压缩会话，`/clear` 开新上下文。
- Prompt caching 是前缀缓存；切换模型、切换 effort、连接/断开部分 MCP、全量 deny 工具、升级 Claude Code、compact 后首轮都会影响缓存。
- 编辑仓库文件、切换 permission mode、调用 skills/commands、spawn subagent 通常不会破坏父会话缓存前缀。

适合目标：建立“为什么 Claude 会越来越慢、为什么上下文会满、为什么某些改动要重启/clear/compact 才生效”的底层理解。

### 3. 日常高效使用

再读：

- `claude-code/best-practices.md`
- `claude-code/common-workflows.md`
- `claude-code/prompt-library.md`

重点掌握：

- 给 Claude 一个可运行的验证信号：测试、构建、lint、截图、fixture diff、命令退出码。
- 复杂任务优先“探索 -> 计划 -> 实现 -> 验证/提交”，简单任务可直接做。
- 提示词要具体：说明文件范围、症状、复现命令、约束、现有模式、成功标准。
- 对陌生代码库，先问 overview、架构、数据模型、认证流程、入口点。
- bug 修复应给出错误输出和复现命令，并要求修 root cause，不要压制错误。
- 长会话要主动管理上下文：无关任务用 `/clear`，自然断点用 `/compact`，探索型任务交给 subagent。
- 多次纠正仍失败时，不要继续污染上下文；应 `/clear` 后用更好的初始 prompt 重开。
- prompt library 提供了 discover/design/build/test/refactor/review/debug/git/release/automate 等可复制模板。

适合目标：形成日常工程协作模式，而不是把 Claude 当问答机器人。

### 4. 持久指令与记忆

再读：

- `claude-code/sore-instructions&memories.md`
- `core-concepts/Explore-the-claude-directory.md`

重点掌握：

- Claude Code 读取 `CLAUDE.md`，不是 `AGENTS.md`；如果项目已有 `AGENTS.md`，可在 `CLAUDE.md` 中 `@AGENTS.md` 导入。
- `CLAUDE.md` 是行为指导，不是强制执行；必须强制执行的规则应放到 permissions 或 hooks。
- `CLAUDE.md` 应短而具体，目标控制在 200 行以内；过长会占上下文并降低遵循度。
- `CLAUDE.md` 适合放每次会话都需要的项目规则、构建命令、测试命令、代码风格、架构红线、常见坑。
- `.claude/rules/` 适合路径或主题作用域规则，可用 `paths:` frontmatter 只在匹配文件进入上下文时加载。
- skills 适合偶尔需要的参考材料或可复用工作流，避免塞进每次都加载的 `CLAUDE.md`。
- Auto memory 是 Claude 自己写的跨会话经验，默认位于 `~/.claude/projects/<project>/memory/`，每次只加载 `MEMORY.md` 前 200 行或 25KB。
- `.claude/` 目录可包含 `settings.json`、`settings.local.json`、`rules/`、`skills/`、`commands/`、`agents/`、`workflows/`、`agent-memory/`、`output-styles/` 等。

适合目标：设计项目级长期规则、团队协作规范、自动记忆和上下文分层。

### 5. 扩展能力选择

再读：

- `core-concepts/Extend-Claude-Code.md`

重点掌握：

- `CLAUDE.md`：每个会话都加载，放 always-on 项目规则。
- Skills：按需加载知识或工作流，适合 API 文档、部署流程、审查清单、重复 prompt。
- Subagents：隔离上下文，适合大范围搜索、独立审查、并行验证、避免主上下文膨胀。
- MCP：连接外部服务和数据源，如 GitHub、数据库、浏览器、Slack、Jira 等。
- Hooks：生命周期自动化和硬约束，适合每次编辑后格式化、阻止危险命令、记录日志。
- Plugins：把 skills/hooks/subagents/MCP 打包分发。
- Agent teams：更重的多会话协作，适合需要多个独立 Claude 会话互相通信的复杂任务。

选择规则：

| 需求 | 首选机制 |
| --- | --- |
| Claude 每次都要知道 | `CLAUDE.md` |
| 某类文件才需要规则 | `.claude/rules/` |
| 偶尔使用的流程/知识 | skill |
| 需要访问外部系统 | MCP |
| 必须每次自动执行 | hook |
| 探索会污染主上下文 | subagent |
| 多个 repo 复用配置 | plugin |

适合目标：避免把所有东西都塞进 `CLAUDE.md`，用正确机制控制上下文成本和执行可靠性。

### 6. 权限、安全与自动化

再读：

- `claude-code/permission-mode.md`
- `platforms&integrations/CLI.md`

重点掌握：

- Permission mode 决定 Claude 是否需要在编辑文件、运行 shell、联网、调用工具前暂停等待批准。
- `default`：只自动读，适合敏感工作和入门。
- `acceptEdits`：自动批准文件编辑和常见文件系统命令，适合你会事后看 diff 的普通开发。
- `plan`：只探索和写计划，不改源文件，适合不确定范围的复杂任务。
- `auto`：用后台安全 classifier 减少批准提示，适合长任务，但仍是 research preview，不等于安全保证。
- `dontAsk`：只允许预先批准的工具，适合 CI/脚本等无交互环境。
- `bypassPermissions`：跳过检查，只应在隔离容器/VM 中使用。
- `.git`、`.claude`、`.mcp.json`、`.envrc`、包管理配置、pre-commit 配置等 protected paths 在大多数模式下不会被自动批准写入。
- CLI computer use 是 macOS 研究预览功能，需要 Pro/Max、交互会话和 `computer-use` MCP server，可控制 GUI 应用，但安全边界不同于 sandboxed Bash。

适合目标：为不同风险等级的任务选择合适的权限模式，理解哪些操作必须人工或策略批准。

### 7. 会话管理与并行工作

再读：

- `claude-code/message-sessions.md`
- `claude-code/common-workflows.md` 中 session/worktree/subagent/headless 部分

重点掌握：

- `claude --continue` 恢复当前目录最近会话。
- `claude --resume` 打开会话选择器。
- `claude --resume <name>` 恢复命名会话。
- `claude --from-pr <number>` 回到创建某个 PR 的会话。
- `/rename` 给长任务命名，便于恢复。
- `/branch` 或 `--fork-session` 可复制当前会话历史并尝试另一条路线。
- `/export` 导出可读 transcript；脚本应优先用 `claude -p --output-format json` 或 hook/statusline 提供的 `transcript_path`，不要直接依赖 JSONL 内部结构。
- worktrees 适合并行多个独立分支，避免编辑冲突。
- fresh context 的 reviewer/subagent 更适合独立审查，因为不会被刚才的实现思路影响。

适合目标：让一个任务跨多天、多分支、多 Claude 会话稳定推进。

## 当前目录文件索引

### `get-started/`

| 文件 | 用途 |
| --- | --- |
| `overview.md` | 产品总览、安装入口、可用界面、主要能力、下一步导航 |
| `quick-start.md` | 终端 CLI 快速入门、登录、首次会话、常用命令、初学提示 |
| `change-log.md` | 版本更新日志，当前摘录到 2026-07-02 的 `2.1.199` |

### `core-concepts/`

| 文件 | 用途 |
| --- | --- |
| `How-Claude-Code-works.md` | agentic loop、工具类别、访问范围、环境、会话、上下文、安全机制 |
| `How-Claude-Code-uses-prompt-caching.md` | prompt caching 前缀机制、缓存失效动作、TTL、subagent 缓存关系 |
| `Extend-Claude-Code.md` | `CLAUDE.md`、skills、subagents、MCP、hooks、plugins 的选择与组合 |
| `Explore-the-context-window.md` | 交互式上下文窗口示意源码，说明什么进入上下文、何时进入、成本如何 |
| `Explore-the-claude-directory.md` | 交互式 `.claude/` 目录说明源码，覆盖项目级和用户级配置结构 |

### `claude-code/`

| 文件 | 用途 |
| --- | --- |
| `best-practices.md` | 官方最佳实践：验证、规划、上下文管理、CLAUDE.md、skills、subagents、自动化 |
| `common-workflows.md` | 常见任务配方：理解代码、修 bug、重构、测试、PR、文档、图片、计划、并行、脚本 |
| `message-sessions.md` | 会话管理：resume、rename、picker、branch、compact、export、transcript 位置 |
| `permission-mode.md` | 权限模式：default/acceptEdits/plan/auto/dontAsk/bypassPermissions 与 protected paths |
| `prompt-library.md` | 提示词库组件源码，内含大量任务模板和分类 |
| `sore-instructions&memories.md` | 持久指令与记忆。文件名疑似应为 `store-instructions&memories.md` |

### `platforms&integrations/`

| 文件 | 用途 |
| --- | --- |
| `CLI.md` | CLI computer use：macOS GUI 控制能力、启用方式、安全边界、示例、排错 |
| `VScode.md` | 当前内容与 `CLI.md` 重复，暂未包含真正 VS Code 专页内容 |

## 对本项目最有价值的阅读重点

对于本仓库这种复杂 agent/workflow/skill 设计项目，优先关注以下主题：

- `CLAUDE.md` 与 skills 的边界：常驻红线进 `CLAUDE.md`，长流程和领域知识进 skill。
- 上下文成本：大段参考资料不要常驻，优先用按需 skill、path-scoped rules、subagents。
- subagents：用于隔离大规模阅读、审查、验证，而不是把所有文件读进主会话。
- hooks/permissions：强制安全规则不能只写 prompt，要用 settings/hook/permission enforcement。
- session/worktree：长周期任务要命名会话，重要分支或并行实验用 worktree/fork。
- prompt caching：模型、effort、MCP/插件变更、compact、升级都会影响下一轮成本和延迟。

## 实用速查

| 场景 | 推荐做法 |
| --- | --- |
| 第一次理解项目 | `claude` 后问 `give me an overview of this codebase` |
| 复杂改动前 | 进入 plan mode，先探索和写计划 |
| 要求 Claude 自检 | 明确测试/构建/lint/截图等验收标准 |
| 会话变慢或跑偏 | 无关任务用 `/clear`，同一任务自然断点用 `/compact` |
| 同一错误重复出现 | 加入 `CLAUDE.md`、rules、skill，或用 hook 强制 |
| 大范围调研 | 让 subagent 调研并只返回摘要 |
| 自动化一次性任务 | `claude -p "prompt" --output-format json` |
| 恢复长任务 | `/rename` 命名，之后 `claude --resume <name>` |
| 并行开发 | 用 worktrees 或多个 sessions，必要时 fresh reviewer 审查 |
| 降低批准疲劳 | 普通开发用 `acceptEdits`，长任务谨慎用 `auto` |

## 已发现的本地整理问题

- `claude-code/sore-instructions&memories.md` 文件名疑似拼写错误，内容实际是“Store instructions and memories / How Claude remembers your project”。
- `platforms&integrations/VScode.md` 当前内容与 `CLI.md` 完全相同，不是 VS Code 文档。
- 多个 Markdown 文件保留了官网 Mintlify/React 组件源码，作为本地阅读材料时可重点看文字段落和表格，不必关注组件实现细节。
