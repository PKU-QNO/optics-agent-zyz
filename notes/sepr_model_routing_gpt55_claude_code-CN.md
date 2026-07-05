# SEPR 模型路由：GPT-5.5[400k] + Claude Code 1M

更新时间：2026-07-05

用途：给 optics-lead-agent 讨论具体实现方案。本文是运行策略 note。

## 落地状态（optics-lead 评估后，2026-07-05；模型档位同日晚更新为全 Sonnet）

**已落地（当前生效）：**
- **7 个 agent frontmatter `model` 字段全部 = `claude-sonnet-5[1m]`**（SEPR 6 个：main-agent / sub-agent / sub-leaf / evolution-agent / sub-E-agent / sub-e-leaf + optics_agent 的 optics-lead）。**Fable 5 与 Opus 4.8 均不作常驻 model。** 已 YAML parse 核过 7 个文件全为 sonnet。
- **档位从「fable 编排 / sonnet 执行」两档收敛为「全 Sonnet 单档 + effort 分级补性能」**（2026-07-05 晚，用户拍板）。理由：
  - **Fable 5 下架**：refusal-fallback 自动降级 Opus 4.8 → 跨模型缓存不共享 → 整段前缀重写（真实成本浪费）；且 Fable 单价超 Opus 档，常驻太贵。
  - **Opus 4.8 下架**：tool-call malformed ~1.5%（自回归级联，见 CLAUDE.md 熔断节）。
  - **Sonnet 5 选它**：无 refusal-fallback、长上下文稳定、$2/$10 引导价（比 Opus 便宜 3–5×）。弱于 Fable 的部分**用 effort 分级补**。
- **effort 补偿（跟 session 走，不切 agent）**：全局 `high`；复杂推导（formalization / 物理口径 / 跨报告矛盾）`xhigh`；最终裁决（Gate3/4 终裁、result_class、公式有效性、E05 六维裁决）`max`。启动即 `claude --model claude-sonnet-5[1m] --effort <档>`。详见 `sepr_claude_effort_routing-CN.md`（其"常驻 Fable"裁决已被本决定 override 为全 Sonnet）。
- **安全阀**：若 E05 六维裁决反复证明 Sonnet+max 判断力不够，**只把那一个停机点临时升 Fable**（短会话、少工具、落盘后 gate），不改全局常驻档。Opus 4.8 仅作 Fable 不可用时的应急短会话 fallback。
- **codex = GPT-5.5 cheap worker 术语统一**：SEPR `CLAUDE.md`「模型路由与 codex 委托」节已写明「codex」等同本 note 的 `gpt-5.5[400k]`（经 `codex-cli` CLI-MCP），合并为同一套委托规范（回答 §「需要讨论」#7）。分工表 + 安全规范 + malformed 熔断已在 CLAUDE.md 生效。

**关键技术澄清（落地时发现）**：agent 的 `model` 字段**只能设 Claude 模型**——GPT-5.5 跑不了 Claude Code 的 agent 壳，它是 agent 内部**委托 codex-MCP**的行为，不是 model 字段能选的。所以本 note 下面「四层」表的编排/裁决层落到 frontmatter 上 = Claude 单档（全 Sonnet 执行壳 + effort 分级）+ GPT-5.5 委托层；原「fable 编排 / sonnet 执行」两档设想已被全 Sonnet 决定取代（下面正文的 `claude-fable-5[1m]` 均指"需临时升级时的启动参数"，不是常驻 frontmatter）。

**尚未落地（留待，多数需先跑通再决定，符合「先跑通再加治理」）：**
- §「需要讨论的实现点」#1-6：CLI-MCP 安全执行模板固化、spawn 模板加 `model_route` 字段、sub 报告记 `model_used`、Gate 文件强制标「哪些证据 Claude 亲读」、run_manifest 加 `model_routing` 节、CLI-MCP worker 独立 malformed fingerprint。
- W-flow / E-flow 逐步路由表尚未逐条写进各 step SKILL（当前靠 CLAUDE.md 分工表 + agent model 兜底；逐步细化留待首次真按此路由跑一篇后据实调）。

以下为原始运行策略正文（未改）。

## 结论

把 `gpt-5.5[400k]` 通过 Claude Code CLI-MCP 纳入后，模型路由应从“Claude 内部三档选择”改成“四层分工”：

| 层级 | 默认模型 | 用途 |
|---|---|---|
| 默认执行层 | `gpt-5.5[400k]` | 代码实现、文件读写、日志扫描、批量审查、verifier 编写、报告初稿、fan-out |
| Claude 原生编排层 | `claude-sonnet-5[1m]` | 需要 Claude Code hooks/subagent/skill 语境的普通主会话；需要 1M 但判断密度不最高 |
| 高价值裁决层 | `claude-fable-5[1m]` | Gate 终裁、物理推导、跨 case 失败归因、V4/框架复盘、GPT/Sonnet 分歧裁决 |
| 例外层 | `claude-opus-4-8[1m]` | 基本下架；只在 Fable 不可用且必须 Opus 档推理时短会话少工具使用 |

关键变化：`Sonnet 5` 不再是全局默认执行层，`gpt-5.5[400k]` 才是。Sonnet 5 的位置变成 Claude Code 内部默认壳，而不是主要算力来源。

## 判断原则

核心原则仍是：

```text
判断密度决定谁干活。
```

但加入 GPT-5.5 后，成本断层改变执行层默认值：

- GPT-5.5 token 单价按用户当前可用价格约为 Opus 4.8 的 1/50，适合作为可消耗 worker。
- Claude 侧模型均支持 1M，上下文优势应留给真正需要单上下文 1M 的任务。
- 400k 足够绝大多数节点任务；超过 400k 时优先 capsule / 文件化切分，不要第一反应升级 Claude 1M。
- Claude 亲自读写只保留在 gate 裁决、verifier 输出、关键报告、契约文件等必须亲审位置。

## W-flow 路由

| 步骤 | 推荐模型 | 说明 |
|---|---|---|
| W01 PDF 预处理、文本抽取、数字化 | GPT-5.5 | 机械量大，判断密度低。 |
| W02 论文阅读、参数表、图表候选 | GPT-5.5 多 pass；Fable/Sonnet 审关键证据 | GPT 负责抽取和交叉核对，Claude 只看 gate 必需证据。 |
| W03 formalization spec | GPT-5.5 起草；Fable 审 spec 风险 | spec 进入后续物理和代码路径，最终口径需高阶裁决。 |
| W04 theory + implementation | GPT-5.5 写代码/verifier；Fable 审物理推导 | 代码由测试和 verifier 兜底；物理口径不能只靠 worker。 |
| W05 theory_check / Gate3 | GPT-5.5 cheap adversarial review；Fable 终裁 | 先用便宜异构审查扩大覆盖，再让 Fable 聚焦关键分歧。 |
| W06 run_and_monitor | GPT-5.5 | 跑命令、读日志、整理产物。 |
| W07 physical_verification | GPT-5.5 跑量化；deterministic verifier 为硬裁判 | 任何模型都不能覆盖 verifier 失败。 |
| W08 result_analysis / Gate4 | GPT-5.5 归因初稿；Fable 裁 `result_class` | 防止把 `diagnostic_only` / `surrogate_fallback` 说成物理成功。 |
| W09 reproducibility_selfcheck | GPT-5.5 | 重跑、扰动、文件核验偏工程执行。 |
| W10 summary/report | GPT-5.5 起草；Claude 终审 | Claude 终审 provenance、result_class、toEflow 口径。 |
| W11 main_agent_report/run_manifest | Claude 亲写或终审 | 契约文件，不经 worker 转述直接定稿。 |

## E-flow 路由

| 步骤 | 推荐模型 | 说明 |
|---|---|---|
| E01 concurrent_review | GPT-5.5 fan-out | 并发 capsule 审查成本主导。 |
| E02 cluster_and_plan | GPT-5.5 聚类初稿；Fable 裁决冲突 | conflict_ledger 和经验分流会影响 skill 演化。 |
| E03 concurrent_skill_work | GPT-5.5 起草 skill 草稿 | 进入 `.claude/.human` 前必须 human/Claude gate。 |
| E04 validate_and_replay | GPT-5.5 执行 replay；Fable 解读退化 | replay 靠脚本，判断“是否退化”再升级。 |
| E05 六维裁决/三级治理 | Fable | 自迭代最怕 reward hacking、记忆污染、自我偏好。 |
| E06 `.E-history` / run_manifest | Claude 亲写或终审 | 契约文件，保留可审计口径。 |

## CLI-MCP 调用口径

Claude 调 GPT-5.5 时，优先传：

- 文件路径
- 明确任务边界
- 输出文件路径
- 产物 schema / 报告字段
- 禁止项和 result_class 约束

不要把大文件内容塞回 Claude context。GPT 应把产物落盘，Claude 只亲读以下材料：

- GATE 决定
- verifier 输出
- 关键报告
- run_manifest
- capsule
- 会进入规则面的 skill / AGENTS / CLAUDE 变更

GPT 产物必须经过 deterministic verifier 或 Claude/human gate 才能进入 `.result`、skill、AGENTS/CLAUDE 规则面。

## 400k 与 1M 的升级规则

默认不要因为“文件多”就升级 Claude 1M。建议顺序：

1. 让 GPT-5.5 读文件路径并产出 capsule。
2. 让 GPT-5.5 分块核对并落盘证据索引。
3. Claude 亲读 capsule + 关键证据文件。
4. 只有当任务确实要求单模型同时持有跨阶段全局上下文，才升级 Sonnet/Fable 1M。

适合升级 1M 的任务：

- 跨 case 失败模式综合
- V4/V5 架构复盘
- 多份 gate/verifier/报告之间的矛盾裁决
- 复杂物理推导与工程实现同时耦合的上游裁决

不适合升级 1M 的任务：

- 代码实现
- 日志扫描
- PDF 文本抽取
- 批量表格核对
- 报告初稿
- 普通 fan-out 审查

## Opus 4.8 处理

Opus 4.8 不再进入默认路径。原因不是单轮能力不够，而是端到端运行风险不合适：

- Claude Code 长 session / tool-call malformed 风险已经在本项目记录为高风险。
- SEPR 正好是长上下文、工具密集、CJK 文本、gate 断点密集的负载。
- 一旦 transcript 被 malformed 输出污染，继续 `--resume` 会放大错误。

使用规则：

- 只在 Fable 不可用且确实需要 Opus 档推理时使用。
- 使用短会话。
- 少工具或 tool-free。
- 不跑长 agent。
- 不 resume 已污染 session。
- 同 session 累计 2 次 malformed 立即熔断，写 handoff，开新会话。

## 需要讨论的实现点

1. CLI-MCP 是否能为 GPT-5.5 固定安全执行模板：workspace、输出路径、禁止读取 secret、禁止直接改规则面。
2. main-agent / evolution-agent 的 spawn 模板是否要新增 `model_route` 字段。
3. sub-agent 报告模板是否要记录 `model_used`、`context_window`、`input_artifacts`、`output_artifacts`。
4. Gate 文件是否要强制写明“哪些证据 Claude 亲读，哪些来自 GPT worker”。
5. `run_manifest.yaml` 是否要扩展 `model_routing` 节，记录 GPT/Claude 分工。
6. malformed 熔断是否只针对 Claude Code session，还是也要对 CLI-MCP worker 异常建立独立 fingerprint。
7. 400k 溢出时是否强制先 capsule 化，禁止直接把完整上下文升级到 Claude 1M。

## 建议的默认启动口径

普通执行：

```text
GPT-5.5[400k] via CLI-MCP
```

Claude Code 普通编排：

```powershell
claude --model claude-sonnet-5[1m]
```

高价值裁决：

```powershell
claude --model claude-fable-5[1m]
```

Opus 4.8：

```text
Only short, low-tool fallback sessions.
```

## 当前建议

先不要直接改 `AGENTS.md` 和 SEPR skill。下一步应由 optics-lead-agent 评估具体落地方式，重点看：

- CLI-MCP worker 的安全边界
- spawn 模板字段怎么扩展
- report/run_manifest 如何记录模型路由
- gate 亲读证据如何防转述漂移
- 现有 codex 委托规则与 GPT-5.5 worker 是否合并成同一套“cheap worker”规范
