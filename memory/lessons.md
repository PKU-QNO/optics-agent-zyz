# lessons — optics_agent 踩坑教训

> 每条同步 see pitfalls_log:<id> + 见 worklog/<序号>#<锚>。
> L1.5 首次整理，2026-07-26。已补存部分条目到 pitfalls_log。

## 教训清单

- lesson-1: **子 agent 空返回但标 completed** — 下次多试一遍（用户指示）。spawn 后校验固定头 6 字段 + 8 字段输出，缺实质内容拒绝接受。
  - see pitfalls_log:1052f58b
  - 见 WORK_LOG.md#10

- lesson-2: **PowerShell here-string 在中文环境报错** — 改用 write 工具建文件
  - see pitfalls_log:b7b77221
  - 见 WORK_LOG.md#10

- lesson-3: **bash 数行数对中文文件不准** — 用 PYTHONUTF8=1 + python 读
  - see pitfalls_log:65c06802
  - 见 WORK_LOG.md#10

- lesson-4: **quick_validate 要求 name lowercase hyphen-case** — sub-E-agent frontmatter name 用 `sub-e-agent`，文件夹名仍 `sub-E-agent`
  - see pitfalls_log:aabfddd2
  - 见 WORK_LOG.md#10

- lesson-5: **MCP 全量注入占 context** — 必须用 tools allowlist 控制，MCP 用 disallowedTools
  - see pitfalls_log:58c3e67f
  - 见 WORK_LOG.md#10

- lesson-6: **ToolSearch 必须显式包含** — 否则 MCP 工具注册了无法调用
  - see pitfalls_log:836244f6
  - 见 WORK_LOG.md#10

- lesson-7: **编辑工具破坏 hardlink** — edit/write 在 Windows 上可能替换文件而非原地改，每次改后验证 hash 一致，断裂用 Remove-Item + New-Item HardLink 重建
  - see pitfalls_log:038e43a4
  - 见 WORK_LOG.md#10

- lesson-8: **三文件必须同步（OpenCode 未撤销前）** — 改 CLAUDE.md/AGENTS.md/opencode.json 任何一个要审改其它两个。OpenCode 撤销后不再适用。
  - see pitfalls_log:ec566c34
  - 见 WORK_LOG.md#10

- lesson-9: **OpenCode skill 懒加载差异** — 和 Claude Code 的 skills: 预加载不同，OpenCode 子 agent 要靠 .opencode/prompts/ 强制先调 skill tool。
  - see pitfalls_log:49f80247
  - 见 WORK_LOG.md#10

- lesson-10: **JSON 路径反斜杠报错** — 派子 agent 时 prompt 里的 Windows 路径反斜杠触发 JSON 错误，改用正斜杠或让子 agent 读文件。
  - see pitfalls_log:61067a8f
  - 见 WORK_LOG.md#10

- lesson-11: **PowerShell grep UTF-8 不稳定** — 用 python json.load / Python UTF-8 读取比 PowerShell grep 更可靠
  - see pitfalls_log:abcce16f
  - 见 WORK_LOG.md#10

- lesson-12: **agent frontmatter model 只在 --agent 启动时生效** — /skill 斜杠命令不切 model。claude（全局）+ /身份名 路径 model 不生效，须先 /model 再 /身份名，或直接 --agent。
  - see pitfalls_log:5dacf95a
  - 见 WORK_LOG.md#阶段十三

- lesson-13: **memento 工具须用 mcp__memento-mcp__ 全名** — 裸名 memory_search 报 No such tool，别误判成整批 MCP outage。
  - see pitfalls_log:dd4591d8
  - 见 WORK_LOG.md#阶段十二

- lesson-14: **改 agent frontmatter 不热加载** — 改 tools/MCP 须完全退出 claude 重开，--resume 不够。
  - see pitfalls_log:a3cd353e
  - 见 WORK_LOG.md#阶段十三
