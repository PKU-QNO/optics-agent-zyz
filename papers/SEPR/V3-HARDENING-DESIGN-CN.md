# SEPR V3 加固设计（放弃 OpenCode 兼容 + 采纳 Claude 新能力）

> **元信息**
> - 日期：2026-07-03
> - 承接：`CLEANUP-A-LOG-CN.md`（上一轮清理日志）
> - 现状基准：`DESIGN-GAP-AUDIT-CN.md`（2026-07-02 gap 审计，本文按其 gap 编号引用）
> - 战略论证：`BORROWABLE-EXPERIENCE-CN.md` §6.1「先跑通再加治理」、§0 三条铁律、§4.2 缺口清单
> - 能力核验来源：`../notes/Gemini/pre-subagent.md`（subagent 能力，已核至官方 ~v2.1.196）、`../notes/Gemini/agent-team.md`（Agent Teams 能力，已核）、`../notes/Gemini/CLI.md`（CLI 综述，**低置信度、未核验**，尤其其 §9 待核验清单）
> - **文档性质：设计提案（design proposal）。本文不修改 SEPR 本体任何文件，落地一律走后续 human gate。本文只新增这一份提案。**
> - V3 定义：SEPR 的 Claude Code 三层子 agent 方案（`main`/`evolution` → `sub`/`sub-e` → `leaf`）。
> - **核验状态（2026-07-03）**：本文 §4/§5 依赖的能力已由 `claude-code-docs-agent` 对照官方文档（`code.claude.com/docs/en`，changelog 至 `2.1.199`）逐条核验。结论：第一层四项均**成立可落地**，另有若干写法修正已回填 §3/§4/§5/§7。完整逐条结论见 §7 与 `../notes/Gemini/CLI.md` 末尾。

---

## 0. 结论摘要（半屏读完）

本轮做两个决定，外加一份分层采纳结论。

- **决定 A：暂时放弃 OpenCode 兼容。** SEPR 只面向 Claude Code 一套系统。后果是可以放心用 Claude 专属能力（尤其 hooks），不再背「CLAUDE.md / AGENTS.md / opencode.json 三文件同步」的账；审计 gap 里的 C1（深度上限双系统不对称）大半消解，B4（OpenCode skill 白名单不对称）降级为非问题。仅「暂时」放弃，撤销点在 §6 登记，本次不删 SEPR 的 opencode 文件。
- **决定 B：分层采纳 Claude 新能力。** 三层结论已定，直接采用（见 §3）：
  - **第一层直接用**：`.claude/agents/*.md` 预制配置、`skills:` frontmatter 预加载、新增 `sub-leaf` / `sub-e-leaf` 硬化第 3 层、**hooks 做红线**（最高价值）、`disable-model-invocation` 防误触发。
  - **第二层参考/择机**：无头模式 `-p` + JSON 输出 + `--resume` 可审计流水线、`context: fork` skill、plan approval 治理范式、token 经济学实践、Agent Teams 仅作后期审查模式。
  - **第三层不用/谨慎**：Agent Teams 进复现主路径、OS 沙箱（Windows 不适用）、非本域 MCP、CLI.md 一切未核验声称。

**本轮最高价值项 = hooks 红线**：把红线从 prompt「求它遵守」下沉成 CLI 框架层的确定性代码，对齐 BORROWABLE §3 铁律 #8「红线/控制流写死成代码，不靠 prompt」。放弃 OpenCode 后 hooks 无双系统同步负担，是本轮性价比最高的加固。

**核验后确认（2026-07-03）**：第一层四项经官方文档核验均**成立可落地**，仅写法有小修正——`disable-model-invocation` 属 **skill frontmatter**（非 agent 字段）；hooks 是 **30 个事件**（非 25）；subagent 停止门禁用 **`SubagentStop`/`Stop`**（非 Agent Teams 的 `TeammateIdle`/`TaskCompleted`）；无头 JSON 字段用 **`total_cost_usd`**（非 `cost_usd`）；预加载用 `skills:`（非 `tools: Skill(name)`）。详见 §7。

**红线复述（本文不违反、SEPR 落地也不得违反）**：拓扑写死人工管；agent 不得自动改拓扑 / 规则；自迭代只碰经验层、全走 human gate；不把 Agent Teams 放进复现主路径。

---

## 1. 定位与前提

### 1.1 本文是什么 / 不是什么

- **是**：一份把「放弃 OpenCode」+「分层采纳 Claude 新能力」两个决定落成文字的设计提案，供后续人工审查后决定是否落地到 SEPR 本体。
- **不是**：不是对 SEPR 本体文件的修改，不是已完成的加固，不是自迭代自动产出。所有 §4 登记的改动都停在「提案」状态，逐条标注 human gate 级别，由人工在 SEPR 工作区落地并验证。

optics_agent 是「设计 SEPR 框架的元工作区」，SEPR 本体在姊妹目录 `C:\Users\27370\Desktop\project\self-evo-paper-repro`。本文在 optics_agent 侧起草，属于人工预训练循环里「读复现经验 → 人工改进设计」的一环。

### 1.2 重申架构红线（不可违反，落地必须继承）

1. **拓扑写死，人工管。** workflow 三层拓扑由人工写死，agent 不得自动改拓扑 / 节点指令 / 分支条件。本文提出的所有能力（hooks / leaf / 预加载）都在「节点内工具与护栏」层，不动拓扑。
2. **自迭代只碰经验层，全走 human gate。** 本文的 hooks、leaf、预加载都不改 workflow 拓扑、蓝图结构、根配置，也不是自迭代自动改，是人工设计改进。
3. **agent 不得自动改规则。** 失败防护、上限、验证器对 agent 只读（BORROWABLE §2 主题六「Sakana 改自己限制」红线）。本文 hooks 正是把这条从 prompt 硬化到框架。
4. **不把 Agent Teams 放进复现主路径。** 见 §3 第三层与 §8。

### 1.3 为什么现在做加固，而不是等跑通再说

BORROWABLE §6.1 是全文优先级最高的战略提醒：**最大的风险是「在验证价值之前就过度投资治理基础设施」**——SEPR 有 6465 行 skill + 全套治理，却一篇 Mie 都没跑通，建议先跑通再按「真断的」加治理。

这与本文并不冲突，关键在于区分两类改动：

- **过度治理**（应推迟到跑通后）：holdout / anytime-valid 接受规则 / 记忆 utility_score / baseline A/B/C/D 等——这些是 DESIGN-GAP-AUDIT §0.2「跑通后才值得加的治理」，本文**不碰**。
- **低成本堵已知阻断 gap**（现在就该做）：本文四项改动全部命中 DESIGN-GAP-AUDIT §0.1「让设计自洽必须修的 bug」（尤其 C1）或把已认定红线从 prompt 硬化到框架。leaf agent 是单文件新增，`skills:` 预加载是替换脆弱 bootstrap，hooks 是把已经写在 prompt 里的红线换个更可靠的执行层——这些不是新增治理机制，是**让已有设计更自洽 / 更可靠**，成本低、收益直接。

判据：凡本文提出的改动，都能回答「它堵的是 DESIGN-GAP-AUDIT 里哪个已认定 gap，或硬化的是 BORROWABLE 里哪条已认定铁律」。不能回答的，不进本文。

---

## 2. 决定 A：放弃 OpenCode 兼容

### 2.1 决定内容

SEPR 近期只面向 Claude Code 一套执行系统，暂时放弃对 OpenCode（GPT-5.5 备选）的兼容。

### 2.2 后果（收益）

- **可放心用 Claude 专属能力。** 最关键的是 hooks（§5）——OpenCode 无对等的稳定 hooks 治理入口，此前为保持双系统一致，红线只能停在 prompt。放弃 OpenCode 后 hooks 无同步负担。
- **卸下三文件同步的账。** 此前 SEPR 有三个根配置必须同步改：`CLAUDE.md`（规则主源）/ `AGENTS.md`（OpenCode 本地隔离入口）/ `opencode.json`（OpenCode permission/agent 配置），改一个必须同步审改其它两个，否则两系统行为分叉。放弃 OpenCode 后，规则主源收敛到 `CLAUDE.md`（optics_agent 侧 `CLAUDE.md` 与 `AGENTS.md` 仍是 hard link），维护面显著变窄。

### 2.3 对审计 gap 的简化

- **C1（深度上限双系统不对称，P0）大半消解。** 原 gap 的成因是：Claude 执行层 agent 仍含 `Agent` 工具（只靠 prompt 软约束不再 spawn），而 OpenCode 侧用 `sepr-sub-leaf` / `sepr-sub-e-leaf` 的 `task: deny` 做硬约束，两系统安全强度不对称（DESIGN-GAP-AUDIT §1 C1）。放弃 OpenCode 后，不再需要维护 OpenCode 的 leaf 定义，**只需在 Claude 侧补 leaf agent**（§4），C1 从「双系统对齐难题」退化为「Claude 侧单点新增」。
- **B4（OpenCode skill 白名单与根路由表不一致，P0）降级为非问题。** 原 gap 是 `opencode.json` 顶层 `permission.skill` 缺 `pdf` / `magnus` / `optics-agent-core`（DESIGN-GAP-AUDIT §1 B4）。OpenCode 不再是执行目标后，`opencode.json` 的 permission 白名单不再影响实际行为，B4 不必再修，仅在 §6 登记 `opencode.json` 标 deprecated。

### 2.4 「暂时」的含义

放弃是可撤销的：

- 本次**不删** SEPR 的任何 opencode 文件（`opencode.json`、`.opencode/prompts/` 等），只在 §6 登记「哪些文件后续若恢复 OpenCode 需要重做」并标注 deprecated / 撤销计划。
- 若未来恢复 OpenCode，需重新对齐的点集中在 §6 登记表：三文件同步规则、OpenCode 侧 leaf 的 `task: deny`、顶层 skill 白名单、以及本次用 hooks 硬化的红线在 OpenCode 侧的等价实现（OpenCode 无对等 hooks 时，这些红线在 OpenCode 侧会退回 prompt 软约束，属已知代价）。

---

## 3. 决定 B：Claude 新能力分层采纳

下表是已定的分层结论，直接采用。「堵哪个 gap」列对应 DESIGN-GAP-AUDIT 的 gap 编号或 BORROWABLE 的铁律编号。

| 能力 | 来源 | 用 / 参考 / 不用 | 理由 | 堵哪个 gap / 硬化哪条铁律 |
|---|---|---|---|---|
| `.claude/agents/*.md` 预制配置 | pre-subagent §1–2 | **用** | SEPR 已有 4 身份，继续用；项目级 scope 绑定 workspace | 维持现状，无退化 |
| `skills:` frontmatter 预加载 | pre-subagent §2、§5 | **用** | 替掉「子 agent 跑起来自己 `skill-print.py` 手动读」的脆弱 bootstrap；每身份只预加载自己那份 + 当前领域 skill | 加固 bootstrap 可靠性；对齐 pre-subagent §11 建议 2 |
| 新增 `sub-leaf` / `sub-e-leaf`（`tools` 省略 `Agent`） | pre-subagent §6、§11 建议 4 | **用** | 从框架层禁止第 3 层继续 spawn，取代 prompt 软约束 | **C1（P0）**，放弃 OpenCode 后为 Claude 侧单点改动 |
| **Hooks 做红线**（PreToolUse 拦作业 / 完成门禁 / 报告字段校验） | pre-subagent §2、agent-team §1.9、CLI.md §3；**已核验（§7）：官方 30 事件，PreToolUse/Stop/SubagentStop 属实** | **用（最高价值）** | 把红线从 prompt 下沉成确定性代码 | 硬化 BORROWABLE 铁律 #8 / #1 / #2；对应 DESIGN-GAP-AUDIT 落地清单 #8「失败防护硬化」 |
| `disable-model-invocation: true` | CLI.md §5.1；**已核验（§7）：属 skill frontmatter（非 agent 字段）** | **用** | 防模型闲聊误触发危险 skill（如提交作业的 skill），强制只能用户显式 `/skill` 触发 | 硬化 BORROWABLE 主题六「specification gaming 零样本出现」防线 |
| 无头模式 `-p` + `--output-format json` + `--resume` | CLI.md §1；**已核验（§7）：真实标志，JSON 字段用 `total_cost_usd`** | **参考/择机** | 可审计 / 可 replay 脚本化流水线，契合核心卖点 | 跑通后用于 baseline / CI 化 |
| `context: fork` skill | CLI.md §5.1；**已核验（§7）：真实 skill frontmatter** | **参考/择机** | 重 PDF / 数据 skill 隔离，避免污染主上下文 | 与 pre-subagent §7 上下文隔离同向 |
| plan approval / read-only plan mode | agent-team §1.8、CLI.md §4.1 | **参考** | 治理范式，可用 human gate 模拟；无需引入 Agent Teams | 已有 human gate 覆盖 |
| Token 经济学实践（定向 `/compact`、plan mode、`/model` 分层） | CLI.md §4（数字未核验） | **参考** | 控成本；具体百分比未核验，仅作实践习惯 | 不作硬约束 |
| Agent Teams | agent-team 全文 | **仅后期人工审查 / devil's-advocate** | 实验性、teammate 不能嵌套 spawn、状态文件不可手改；绝不进复现主路径 | 见 §8 |
| Agent Teams 进复现主路径 | agent-team §3.1 | **不用（否决）** | 实验性 + 不可审计 + 无嵌套 fan-out | 违反红线，见 §8 |
| OS 沙箱 Seatbelt / bwrap | CLI.md §3.2 | **不用** | macOS / Linux 专属，主环境是 Windows | 不适用 |
| Playwright / Figma / Notion MCP | CLI.md §5.2 | **不用** | 非本域 | 不适用 |
| CLI.md 一切未核验声称 | CLI.md 全文 | **§4/§5 依赖项已核（§7）；其余仍谨慎** | 本文依赖项已核验；`--json-schema`/`--bare`/`--max-turns`/`/batch`/`/simplify` 已确认真实，不再标疑似不实；未纳入本文的其它声称仍以 CLI.md 低置信度对待 | 见 §7 |

---

## 4. SEPR 改动登记表

本节登记 §3 第一层的具体 SEPR 改动。**全部为提案，落地在 SEPR 工作区进行，逐条走 human gate。** human gate 级别沿用 SEPR 口径：Tier-1 = 例行审阅即可；Tier-2 = 需人工审查后合入；Tier-3 = 需人工评审 + 首跑验证。

### 4.1 新增 `.claude/agents/sub-leaf.md` + `sub-e-leaf.md`

- **现状**：`self-evo-paper-repro/.claude/agents/sub-agent.md` 与 `sub-E-agent.md` 的 `tools` 仍含 `Agent`，第 3 层叶子只靠 prompt「spawn 叶子时省略 Agent」软约束（DESIGN-GAP-AUDIT §1 C1）。
- **改动**：新增两个 leaf agent 定义，`tools` 省略 `Agent`（并可 `disallowedTools` 显式禁），`maxTurns` ≤ 执行层；执行层派叶子时只派这两个 leaf 身份，不再复用带 `Agent` 的 sub 身份。调用名统一 lowercase hyphen-case（`sub-leaf` / `sub-e-leaf`）。
- **堵哪个 gap**：C1（P0，深度上限硬约束）。
- **验收标准**：leaf agent 运行时上下文中无 `Agent` 工具（无法再 spawn）；执行层 spawn 指令只出现 leaf 身份名。
- **human gate 级别**：**Tier-2**（新增执行层安全约束，需人工审查 tools 清单与 spawn 指令一致性）。

### 4.2 4 身份 `skills:` frontmatter 预加载

- **现状**：子 agent 靠运行后自己执行 `skill-print.py` 手动读 skill，是脆弱 bootstrap（pre-subagent §5、§11 建议 2）。
- **改动**：给 4 身份加 `skills:` 预加载——`main-agent` 预加载 `main-agent`；`sub-agent` 预加载 `sub-agent` + 当前领域 skill（如 `optics-mie-reproduction`）；`evolution-agent` 预加载 `evolution-agent`；`sub-e-agent` 预加载 `sub-e-agent`。**每身份只加载自己那份 + 当前领域 skill，禁止全量预加载**（会撑爆上下文）。是否保留 `skill-print.py` 作兜底需实测决定。
- **堵哪个 gap**：不是 §0.1 的自洽 bug，是加固 bootstrap 可靠性（间接降低「子 agent 缺 skill 上下文靠猜」的风险）。
- **验收标准**：子 agent 启动即持有对应 skill 正文，无需运行期手动读取；上下文未因全量预加载膨胀。
- **已核验（§7）**：`skills:` 是 subagent frontmatter 字段，写成 YAML list、值为 skill **name**（非路径）；**不要**用 `tools: Skill(name)` 做预加载（那是权限规则语法）。注意：设了 `disable-model-invocation: true` 的 skill **不能**被预加载（官方限制）——与 §4.4 的高危 submit skill 无冲突（它本就不该预加载）。
- **human gate 级别**：**Tier-1**（配置项替换，行为等价或更稳，例行审阅 + 实测）。

### 4.3 Hooks 做红线（详见 §5）

- **现状**：红线（禁越权提交作业、result_class 判据、报告字段完整性）主要写在 prompt / skill 正文，靠 agent「遵守」（BORROWABLE §2 主题六指出 prompt 级红线可被绕过 / 遗忘）。
- **改动**：新增 3 类 hook（PreToolUse 拦作业 / 完成停止门禁 / 报告字段校验），把红线下沉到 CLI 框架层。详见 §5。
- **堵哪个 gap**：硬化 BORROWABLE 铁律 #8 / #1 / #2；对应 DESIGN-GAP-AUDIT 落地清单 #8「失败防护硬化：限制和 verifier 对 agent 只读隔离」，把「prompt 级上限」升级为「框架级强制」。
- **验收标准**：见 §5 各 hook 的拦截行为可被测试用例触发（构造违规动作被 hook 挡下 + 记审计）。
- **已核验（§7）**：hook 机制与阻断语义官方确认——官方共 **30 个事件**（非「25 种」）；`PreToolUse` 可阻断工具调用（`exit 2` 或 JSON `hookSpecificOutput.permissionDecision: deny`）；完成门禁用 **`SubagentStop`/`Stop`**（非 `TeammateIdle`/`TaskCompleted`）。落地细节见 §7.3。
- **human gate 级别**：**Tier-3**（新增框架级强制护栏，改变执行边界，需人工评审 hook 逻辑 + 首跑验证不误伤正常流程）。

### 4.4 `disable-model-invocation: true`（危险 skill，**skill frontmatter**）

- **现状**：提交作业类 skill 可能被模型在闲聊中语义误触发（CLI.md §5.1）。
- **改动**：给「提交 Magnus / COMSOL 作业」类高危 skill 的 **`SKILL.md` frontmatter** 设 `disable-model-invocation: true`，强制只能用户显式 `/skill` 触发。**注意：这是 skill 字段，不是 `.claude/agents/*.md` 的 subagent 字段**——不要写进 agent 定义。
- **堵哪个 gap**：硬化 BORROWABLE 主题六「specification gaming / 误触发」防线。
- **验收标准**：模型在普通对话中无法自动触发该 skill；仅用户显式调用生效。
- **已核验（§7）**：官方确认为 skill frontmatter 字段；副作用是该 skill 同时无法被 subagent 预加载（与 §4.2 一致，无冲突）。
- **human gate 级别**：**Tier-1**（单键配置，收紧触发面，例行审阅）。

### 4.5 移除 / deprecate OpenCode（本次仅登记，不改文件）

- **现状**：SEPR 与 optics_agent 两侧都有 OpenCode 相关声明与配置（见 §6 清单）。
- **改动**：**本次不改任何文件**，仅在 §6 登记后续撤销点，并标注 deprecated / 撤销计划。
- **堵哪个 gap**：为 §2 决定 A 收尾；B4 降级、C1 简化的前提登记。
- **验收标准**：§6 清单完整，撤销/恢复路径可追溯。
- **human gate 级别**：**Tier-2**（涉及根配置定位变更，后续真正落地时需人工审查三文件；本次登记本身 Tier-1）。

---

## 5. Hooks 红线设计

本节详展 §4.3。三类 hook 各自的触发点、拦什么、对齐哪条铁律。**下述 hook 名称、阻断语义、payload 已于 2026-07-03 经官方文档核验（§7.3）：官方共 30 个事件；阻断用 `exit 2`（stderr 反馈）或退出码 0 时的 JSON `hookSpecificOutput.permissionDecision`（`allow`/`deny`/`ask`/`defer`）；hooks 可定义在 `.claude/settings.json` 或 skill/agent frontmatter 的 `hooks` 字段。**

### 5.1 Hook #1：PreToolUse 拦截 sub / leaf 提交 Magnus / COMSOL 作业

- **触发点**：任一 agent 尝试调用可提交远程作业的工具 / Bash 命令之前（`PreToolUse`）。
- **拦什么**：执行层 / 叶子层（sub / sub-e / leaf）提交 Magnus / COMSOL 作业的动作一律拦下并记审计；作业提交权收敛到编排层 + human gate。等价于「把资源上限 / 作业提交权对 agent 设为只读」。
- **阻断实现（已核验）**：`PreToolUse` 官方支持阻断——`exit 2` 阻断并把 stderr 反馈给 Claude，或退出码 0 输出 `hookSpecificOutput.permissionDecision: "deny"` + `permissionDecisionReason`。
- **对齐铁律**：BORROWABLE §2 主题六「失败防护把上限设 agent 只读、框架强制、禁 self-restart」；铁律 #8「控制流写死成代码」。
- **落地注意**：需精确枚举「提交作业」的命令 / 工具指纹（避免漏网或误伤只读查询）；hook 逻辑本身对 agent 只读。

### 5.2 Hook #2：完成 / 停止门禁——拦「无 verifier 产物却报物理成功」

- **触发点**：subagent 完成 / Claude 停止响应时。**已核验：SEPR 主路径用 subagent，完成门禁用 `SubagentStop`（子 agent 完成）或 `Stop`（主 agent 停止），其 `exit 2` 可阻止停止、继续对话。`TaskCompleted`/`TeammateIdle` 属 Agent Teams 侧，非本路径首选。**
- **拦什么**：拦住「没有 verifier 产物（如物理验证输出 / benchmark 比对结果）却在报告写 `result_class = physical_reproduction_success`」的假完成。无合规产物 → 禁止升到物理复现成功档。
- **对齐铁律**：BORROWABLE 铁律 #1「裁判权归外部确定性检查器，AI 自评不定论」、#2「跑通 / 无报错 / 数值对上 / 收敛都 ≠ 物理复现成功」。
- **落地注意**：需定义「verifier 产物存在」的确定性判据（文件路径 + 非空 + schema 合法），hook 只做存在性 / 格式校验，不做物理判断（物理判断仍归 verifier 脚本）。

### 5.3 Hook #3：报告字段校验——挡假完成

- **触发点**：子 agent / leaf 写出结构化报告时（PostToolUse on Write/Edit 命中报告路径，或完成门禁的一部分）。
- **拦什么**：校验报告固定头字段完整性——固定头 6 字段 + 8 字段（沿用 SEPR 报告模板口径）齐全，且 `result_class` 落在合法枚举（SEPR 7 级 `result_class`，禁旧口径 `success / partial / fallback / blocked / failed / archived`，见 DESIGN-GAP-AUDIT §1 B3）。缺字段 / 非法枚举 → 拦下要求补齐。
- **对齐铁律**：BORROWABLE §2 主题二「想让 agent 稳定吐固定字段，别在 prompt 里求它，用 schema 锁死」；DESIGN-GAP-AUDIT 落地清单 #1「报告 8 字段改工具 schema 强约束」的 hook 版轻实现。
- **落地注意**：这是「schema 校验的 hook 版」，比完整工具 schema 轻；跑通后可升级为 report submission tool + JSON schema（属 §0.2 跑通后治理，本文不做）。

### 5.4 三 hook 与红线的对应小结

| Hook | 官方事件名 | 触发点 | 拦什么 | 对齐铁律 |
|---|---|---|---|---|
| #1 | `PreToolUse` | 提交作业前 | sub/leaf 提交 Magnus/COMSOL 作业 | 失败防护只读 / #8 |
| #2 | `SubagentStop` / `Stop` | 声明完成 / 停止 | 无 verifier 产物却报 physical success | #1 / #2 |
| #3 | `PostToolUse`(Write/Edit) | 写报告时 | 缺 6+8 字段 / result_class 非法枚举 | 主题二 schema 锁死 |

> 共同前提：三类 hook 的逻辑与配置对 agent 只读，由 CLI 框架（不是 agent）强制；agent 不能改 hook 自身。这正是「红线写死成代码不靠 prompt」在 SEPR 的落点。

---

## 6. OpenCode 撤销登记

**以下文件本次都不改，只登记后续撤销 / 恢复点。** 落地由人工在对应工作区分别处理，走 human gate。

### 6.1 optics_agent 侧

| 位置 | 内容 | 优先级 | 后续动作（本次不做） |
|---|---|---|---|
| `CLAUDE.md` / `AGENTS.md`（约第 50 行，两者 hard link） | 「SEPR 双系统 + 三文件同步」声明 | P0 | 改为「SEPR 仅 Claude Code」，删除三文件同步表述；因 hard link，改一处即同步 |
| `notes/workflow_v2_plan-CN.md`（§42–102 附近） | 「CLI 选型 opencode」相关段落 | P1 | 标注 OpenCode 已暂缓，或加撤销注记 |

### 6.2 SEPR 本体侧（`self-evo-paper-repro`）

| 位置 | 内容 | 优先级 | 后续动作（本次不做） |
|---|---|---|---|
| `CLAUDE.md` + `AGENTS.md` | 「三文件同步规则」节 | P0 | 改为「仅 Claude Code」，规则主源收敛到 CLAUDE.md |
| `opencode.json` | OpenCode permission / agent 配置 | P1 | 标 deprecated（不删，留恢复用） |
| `.opencode/prompts/` 目录 | OpenCode 侧 prompt（含 `sepr-sub-leaf` / `sepr-sub-e-leaf`） | P1 | 可归档（不删） |
| `DESIGN-GAP-AUDIT-CN.md` 相关条目 | B4 / C1 中 OpenCode 相关状态 | P1 | 更新状态为「随 OpenCode 暂缓而降级 / 简化」 |

### 6.3 恢复 OpenCode 时需重做的点

若未来恢复 OpenCode 兼容，至少需重新对齐：三文件同步规则；OpenCode 侧 leaf 的 `task: deny` 硬约束；顶层 skill 白名单补 `pdf` / `magnus` / `optics-agent-core`（原 B4）；以及本次用 hooks 硬化的红线在 OpenCode 侧的等价实现（OpenCode 无对等 hooks 时退回 prompt 软约束，属已知代价）。

---

## 7. 官方文档核验结果（2026-07-03，已完成）

§4/§5 依赖的能力已由 `claude-code-docs-agent` 对照官方文档（`code.claude.com/docs/en`，changelog 至 `2.1.199` / 2026-07-02）逐条核验。完整逐条结论与汇总表见 `../notes/Gemini/CLI.md` 末尾。核心结论：**§4 四项第一层改动全部成立可落地**，另有若干写法需修正（已在 §3/§4/§5 更新）。

### 7.1 成立可落地（无需改方案）

- **`sub-leaf` 去 `Agent`**（§4.1）：官方确认 `tools` 省略 `Agent` 后 agent 不能 spawn 任何子 agent；depth 5 时也不再收到 Agent 工具。nested subagent 自 v2.1.172 起支持、最多 5 层；background 子 agent depth 自 v2.1.187 起在首次 spawn 时固定。
- **`skills:` 预加载**（§4.2）：官方确认为 subagent frontmatter 字段，写成 YAML list、值为 skill **name**（非路径），启动时注入 skill 全文。
- **三类 hooks 红线**（§5）：`PreToolUse` 可阻断工具调用；`Stop`/`SubagentStop` 可阻断「完成/停止」；均为官方事件。
- **`disable-model-invocation: true`**（§4.4）：官方确认，但**属 skill frontmatter 字段，不属 subagent**。
- **`context: fork`**、无头模式 `-p`/`--output-format json`/`--resume`、`--json-schema`/`--bare`/`--max-turns`、`/batch`、`/simplify`：均为官方真实能力（原 CLI.md 综述低估，不应再标疑似不实）。

### 7.2 需修正的写法（已在本文对应节更新）

- **hooks 不是「25 种」，官方是 30 个事件**（`SessionStart`/`PreToolUse`/`PostToolUse`/`SubagentStart`/`SubagentStop`/`Stop`/`TaskCompleted`/`PreCompact`/`CwdChanged` 等）；CLI.md 点名的四个名称均属实。
- **`disable-model-invocation` 放 skill 的 `SKILL.md` frontmatter，不放 `.claude/agents/*.md`。** 且它会同时阻止该 skill 被 subagent 预加载——即高危 submit skill 设了它就不能进 §4.2 的 `skills:` 预加载列表（本就不该预加载，无冲突）。
- **subagent 完成门禁用 `SubagentStop`（或 `Stop`），不是 Agent Teams 的 `TeammateIdle`/`TaskCompleted`**；`TaskCompleted` 存在但非普通 subagent 完成的首选。
- **预加载不要用 `tools: Skill(<name>)`。** `skills:` 负责预加载；`Skill(name)`/`Skill(name *)` 是权限规则语法，用于限制可调用哪些 skill。
- **无头 JSON 字段用 `total_cost_usd`（非 `cost_usd`）。** 已确认字段：`result`/`session_id`/`total_cost_usd`/`structured_output`；`num_turns`/`duration_ms` 官方页未找到明确定义，若方案依赖需运行时探测。

### 7.3 hooks 阻断机制细节（供 §5 落地）

- **退出码**：`exit 2` = blocking error；`PreToolUse` 阻断工具调用并把 stderr 反馈给 Claude；`Stop`/`SubagentStop` 的 `exit 2` 阻止停止、继续对话。
- **JSON**：退出码 0 时可输出 `hookSpecificOutput.permissionDecision`（`allow`/`deny`/`ask`/`defer`）+ `permissionDecisionReason`。
- **定义位置**：`.claude/settings.json`（会话/项目级）或 skill/agent frontmatter 的 `hooks` 字段（组件生命周期内 scoped），官方两者都支持。

---

## 8. 不做什么（红线复述）

- **不改拓扑。** 本文所有能力都在「节点内工具与护栏」层；不新增 / 删除 / 重排 workflow 节点，不改分支条件。
- **不把 Agent Teams 放进复现主路径。** 否决理由：实验性、teammate 不能嵌套 spawn（无法替代 SEPR 多层 fan-out，agent-team §4-2）、状态文件用户级且不可手改（agent-team §1.6、§2）。Agent Teams 仅作后期人工打开的审查 / devil's-advocate 模式，且须 plan approval + 禁改规则文件 + 禁提交高风险作业 + 结论回主 agent / human gate（agent-team §3.3）。
- **不让 agent 自动改规则 / 上限 / 验证器。** hooks、上限、verifier 对 agent 只读，由框架强制（BORROWABLE §2 主题六）。
- **不自迭代自己。** 自迭代 workflow 的拓扑、节点指令、专用 SKILL 人工写死；本文提出的 hooks / leaf / 预加载不进入自迭代自动改动范围。
- **不采用 CLI.md 未核验声称做落地依据。** 一切具体标志 / 命令 / 数字 / 模型 ID 先过 §7 核验，未核验前只作设计线索，不写进 SEPR 本体。
- **不删 OpenCode 文件。** 本次仅 §6 登记 deprecated / 撤销点。

---

**本文档结束。** 定位：SEPR V3 加固的设计提案；性质为提案而非已落地；下一步由人工在 SEPR 工作区按 §4 登记表逐条走 human gate 落地，落地前 §7 待核验项必过 `claude-code-docs-agent`。
