# codex exec 委托方案（sub-agent 迁移 codex + 保留 Claude 判断层）

- 状态：`_latest`（活文档）
- 定稿日期：2026-07-07
- 拍板人：用户；实现：optics-lead（optics_agent 元工作区）
- 适用：两工作区通用，SEPR 落地为主
- 上游决策：本方案**精化**（非推翻）memento 决策 `5cf2c7b0`（2026-07-05 codex 委托规则）；谱系用 `supersedes`。

---

## 0. 一句话

把 SEPR 复现的**机械/确定性步骤**从 Claude sub-agent 迁到 **bash `codex exec`** 执行（GPT-5.5，单价约 Opus 1/50），**高判断密度的裁决步保留 Claude**；codex 执行步内部再用 **codex 原生 subagent** 干叶子机械活（sub-sub 层）。这是给 main-agent **加一条委托旁路**，不替换已审计的三层 Claude 架构。

---

## 1. 关键区分：`codex exec`（架构委托）vs `codex-cli` MCP（一次性问答）

实测（2026-07-07，`.tmp-codex-test/`，六点全绿见 §6）确立：**架构性 sub-agent 委托一律走 bash `codex exec`，不用 MCP**。理由是能力不对等——MCP 工具签名缺三样命门：

| 能力 | `codex exec` flag | MCP `codex-cli` | 为什么是命门 |
|---|---|---|---|
| 读 case 外共享代码（`.paper/`、`reproduction_test/mie/`） | `--add-dir <DIR>` | ❌ 无 | 解 sandbox/cwd 硬冲突（旧方案 Q1 blocker） |
| 结构化产物机械校验 | `--output-schema <FILE>` | ❌ 无 | 8 字段子报告 schema 化，Claude 不用肉眼读全文 |
| 结果落盘、不进 Claude context | `-o/--output-last-message <FILE>` | ❌ 无 | 正是"codex 读写不进 context"省钱原则 |
| 审计轨迹 | `--json`（JSONL 事件流） | ❌ 无 | spawn/MCP/command 全留痕 = 可审计执行卖点 |
| per-agent pin model+effort | `-p profile`（叠加 `<name>.config.toml`） | ⚠️ 只有单 `config` override | 分层 model（sub=5.5，leaf=mini） |

**MCP `codex-cli` 的唯一保留场景**：Claude 顶端身份想**当场读 codex 的答案**（如"帮我核个 API 语法/查一段文档"），这种"我要把答案读进 context"的一次性问答用 MCP 顺手。**凡是产出要落盘、要被后续步骤消费的委托，全走 `codex exec`。**

> 术语对齐：本方案的「codex exec 委托」= 决策 `5cf2c7b0` 分工表里的「codex（cheap worker 层）」，只是把**调用通道**从 MCP 收敛到 `codex exec`。委托规范（判断密度决定谁干活、契约留 Claude、产物落盘经 Claude 验收）完全不变。

---

## 2. 11 步分档（用户 2026-07-07 批准）

分档依据（三条已有原则的合成）：**判断密度**（产出质量取决于物理裁决/歧义决策的程度）+ **错误可发现性**（错了下游能不能抓到）+ **是否压 gate/result_class 红线**。

来源：SEPR `main-agent/SKILL.md` 磁盘真实 11 步 + 4 人工 gate 分布。

### ✅ A 档 — 整步交 codex exec（低判断密度，`agent→script`）

| 步 | 名 | 类型 | 交的理由 |
|---|---|---|---|
| 01 | pdf_preprocessing | agent→script | PDF 抽文字/公式/图表，纯机械，输出可直接校验 |
| 06 | run_and_monitor | agent→script | 跑脚本 + 监视日志，确定性执行 |
| 07 | physical_verification | agent→script | **物理"通用检查"脚本**（能量守恒/Rayleigh 极限等写死的 verifier），脚本判定非物理裁决 |

共性：确定性部分已固化成脚本，agent 只驱动。codex 执行 + Claude 看脚本输出验收，零质量损失。

### ❌ B 档 — 绝不交 codex，保留 Claude（高判断密度 + 错误难发现 + 压 gate/红线）

| 步 | 名 | 不交的理由 |
|---|---|---|
| 05 | theory_check | 对抗式审查、双向归因，压**公式 gate(gate3)**；要独立挑刺，交 codex = 让写码方自审上游 |
| 08 | result_analysis | 分析+归因+论文图定量比较，压**误差 gate(gate4)**；错误本身就是最终判断，下游抓不到（Akimov 转述漂移实证） |
| 09 | reproducibility_selfcheck | 排除"碰巧对上"，元级怀疑性推理；codex self-preference 恰会削弱它 |
| 11 | main_agent_report | main-agent 自己的全局裁决收口，压 result_class 红线，本就不下放 |

共性：判断密度最高 + 错误难被下游捕获 + 直接定 result_class/压 gate。它们承载 SEPR "deterministic verifier + 可审计"卖点。

### ⚠️ C 档 — 拆开：机械层交 codex，判断层/契约写保留 Claude

| 步 | 名 | 拆法 | 压的 gate |
|---|---|---|---|
| 02 | paper_reading | 读+搜交 codex；**抽出的参数/单位必须 Claude 在 gate1 前独立核** | 参数 gate(gate1) |
| 03 | reproduction_design | 拆分任务/列产出交 codex；**物理 formalization 保留 Claude** | spec gate(gate2) |
| 04 | theory_and_implementation | **理论推导保留 Claude，写代码交 codex**（原样落地"代码 codex 写 Claude 验"） | — |
| 10 | summary_and_report | 报告初稿可 codex；**记忆写入/result_class 定级/复述纪律是 Claude 契约写** | — |

### 判据总纲（写进 skill 的一句）

> **`agent→script` 步（01/06/07）整步交 codex exec；高判断裁决步（05/08/09/11）绝不交、保留 Claude；混合步（02/03/04/10）机械层交 codex + 判断层/契约写保留 Claude。**「保留 Claude 子 agent 特定情况用」的**特定情况 = B 档四步 + C 档判断层**。

---

## 3. codex exec 调用模板（定稿参数）

```bash
codex exec \
  -C <case目录>                        # 工作根 = 当前 case 文件夹
  --add-dir <shared只读需要的>          # 如 reproduction_test/mie、.paper（按需，最小授权）
  -s workspace-write                   # sandbox：可写 case，拦截 case 外
  -c approval_policy="never"           # 非交互必须 never（见 §3.1）
  --output-schema <schema.json>        # 结构化产物约束（8 字段子报告）
  -o <report.md 或 .json>              # 结果落盘，不进 Claude context
  --json > <events.jsonl>              # 事件流落盘（审计；可选，长任务建议开）
  -m gpt-5.5                           # 或经 -p profile pin；leaf 机械活可降 gpt-5.4-mini
  "<拼接的 spawn 指令：全局模板 + 局部任务 + 论文上下文>"
```

### 3.1 approval_policy 口径修正（对 `5cf2c7b0` 的精化）

- 决策 `5cf2c7b0` 写的是 `approval-policy: untrusted`——那是 **MCP 语境**（交互式，可中途弹批准）。
- **非交互 `codex exec` 必须 `approval_policy=never`**：官方 help 明说「on-request for interactive runs, **never for non-interactive runs**」；`untrusted`/`on-request` 会在非交互流里卡等一个永不到来的人工批准，直接挂死。
- 安全不靠 approval 靠 **sandbox**：`never` + `workspace-write` 是唯一正确组合——执行失败直接返回给模型，越界写被 sandbox 拦（实测 case 外 `should_fail.txt` 确未落盘）。
- **永不** `--dangerously-bypass-approvals-and-sandbox` / `-s danger-full-access`。

### 3.2 输出截断防护（bash stdout 上限）

Claude Code 对 bash stdout 有长度上限（超长砍中间）。**codex 委托一律不依赖 stdout**：
- 真结果读 `-o` 落盘文件（用 Read 工具带 offset/limit 分页，或 `rg`/`sed -n` 取片段）；
- 事件流读 `--json` 落盘的 `.jsonl`；
- stdout 只当进度条，`> run.log 2>&1` 整体重定向，只 `tail` 一眼收尾。

---

## 4. 分层 model（实测：子 agent 默认继承父模型）

| 层 | 身份 | 通道 | model |
|---|---|---|---|
| 编排 | main-agent | Claude（`.claude/agents/`） | claude-sonnet-5[1m] |
| 执行·判断层 | Claude sub-agent（B档 + C档判断层） | Claude spawn | claude-sonnet-5[1m] |
| 执行·机械层 | codex exec（A档 + C档机械层） | bash `codex exec` | gpt-5.5（默认继承父 config） |
| 叶子机械活 | codex 原生 subagent（sub-sub） | codex 内部 spawn | 默认 gpt-5.5；机械活可 pin **gpt-5.4-mini** 省钱 |

- 实测确认：codex spawn 子 agent **默认继承父 config 的 model**（本机 `gpt-5.5` + `model_reasoning_effort=xhigh`），无 override 就是它。
- **诚实边界**：codex 子 agent **自己看不到精确模型名**（只自报"Codex based on GPT-5"）。要精确控制 sub-sub 跑哪个 model，靠 **spawn 时显式传 model** 或 **`-p profile` / `.codex/agents/*.toml` 的 `model` 字段**锁定，不靠子 agent 自述确证。

---

## 5. `.codex/agents/*.toml` —— codex 预制 sub-agent 定义

### 5.1 格式（核实自 memento `ec9c0a97` + 官方文档）

codex 从 **`~/.codex/agents/*.toml`（用户级）** 或 **项目 `.codex/agents/*.toml`（从 cwd walk up 到 project root）** 加载预制 custom agents。每个 TOML 一个 agent：

| 字段 | 必需 | 说明 |
|---|---|---|
| `name` | ✅ | agent 名 |
| `description` | ✅ | 何时用 |
| `developer_instructions` | ✅ | 完整 prompt（= SEPR sub-agent skill 的 codex 版） |
| `model` | 可选 | pin 模型（如 `gpt-5.5` / `gpt-5.4-mini`） |
| `model_reasoning_effort` | 可选 | `low`/`medium`/`high` |
| `sandbox_mode` | 可选 | `workspace-write` 等 |
| `mcp_servers` | 可选 | 继承/限制哪些 MCP |
| `skills.config` | 可选 | 关联 skill |

### 5.2 定位澄清（重要，防下个 session 误解）

- **codex exec 通过 prompt 触发用哪个 agent**，顶层无 `--agent` flag（memento `ec9c0a97`/`54d5aef8` 已核实）。所以 `.codex/agents/*.toml` 的角色是：**codex 主 agent 在 exec 会话里按 prompt 指示 spawn / 复用某个预制 agent**，以及 sub-sub 层的身份来源。
- 放 **SEPR `.codex/agents/`**（项目级，随仓库版本化）最对：codex exec `-C` 指向 case，project root 是 SEPR 根，walk up 命中。
- 与 SEPR 现有 `.claude/agents/*.md`（Claude 三层）**并存不冲突**：`.claude/agents/` 定义 Claude sub（B档/判断层），`.codex/agents/` 定义 codex 执行 agent（A档/机械层）。两套通道，各管各的。

---

## 6. 实测证据（2026-07-07，`.tmp-codex-test/`）

六点全绿，每项做了客观落盘核验（不信 codex 自述）：

| # | 能力 | 结果 | 证据 |
|---|---|---|---|
| 1 | `--add-dir` 跨目录读 | ✅ | 读到 `shared_data_marker_42` |
| 2 | `workspace-write` 写 case 内 | ✅ | `wrote_by_codex.txt` 真落盘 |
| 3 | sandbox 拦 case 外写 | ✅ | 磁盘确无 `should_fail.txt` |
| 4 | `--output-schema` 结构化 | ✅ | 7 字段 JSON 合法 |
| 5 | codex 真 spawn 子 agent | ✅ | 两子 agent 各落盘，有 UUID/nickname（Plato/Singer） |
| 6 | exec 非交互调 MCP | ✅ | memento 查 SEPR 返回 3 条 + 事件流 6 次 mcp_tool_call |

附带：`--json` 51 行事件流可解析出 `spawn_agent`(15)/`mcp_tool_call`(6)/`command_execution`(4)，审计轨迹完整。

**未覆盖（诚实边界，全部标 pending，二期实测）**：
- codex 子 agent 精确 model 名不可自证（只自报"Codex based on GPT-5"）；
- `-p profile` 锁 model 未单测；
- **`.codex/agents/*.toml` 的 `model` 字段能否真 pin 住 exec/sub-sub 未实测**——现仅从 memento `ec9c0a97`（官方文档核实）推断，两个 toml 原型里的 `model="gpt-5.5"`/`"gpt-5.4-mini"` 是否真生效待验；
- codex exec 靠 prompt 触发用哪个预制 agent 的**实际触发词/机制未实测**（顶层无 `--agent`，具体怎么让 exec 用上 `codex-exec-worker` 而非默认 agent，二期要跑通）；
- 真实复现步（非玩具任务）的物理质量未验——靠首个真 case 试点。

---

## 7. 迁移分期（先跑通再加治理）

**不一次性整体迁移。** 分三期：

1. **一期（本方案）**：写死规则（本文档 + 两侧 CLAUDE.md + main-agent skill 分档表 + `.codex/agents/` 原型）。**不改已审计的三层 Claude 架构**——只给 main-agent 加 codex exec 旁路。
2. **二期（下个真 case）**：在一篇真实复现里，A 档某一步（建议 01 pdf_preprocessing，最机械）真用 codex exec 跑一次，Claude 验收，验证真实产物质量。跑通再扩到 06/07。
3. **三期（攒够证据）**：C 档拆分落地（04 代码交 codex 写 Claude 验）；`-p profile` 锁 sub-sub=mini；沉淀为 evolution batch 的正式 skill 更新。

**红线不变**：codex 产物落盘经 Claude 验收才作数；契约（8 字段/result_class/GATE 决定/WORK_LOG/记忆）永远 Claude 亲写；B 档绝不交；secrets 在 codex 可达范围外；计入 case 级资源上限（spawn 20 同口径，codex exec 每次计 1）。

---

## 8. 与旧决策/文档的关系

- **精化** memento `5cf2c7b0`：approval `untrusted`→非交互 exec 用 `never`；调用通道从 MCP 收敛到 `codex exec`。判断密度原则、契约留 Claude、产物验收全不变。→ 新记忆 `supersedes` 它。
- **纠正**我上一轮口头 premise（"`.codex/agents/` 只是 prompt 存档、codex 不自动加载"）：据 `ec9c0a97`，codex **确实**从 `.codex/agents/*.toml` 加载预制 agent；只是无 `--agent` 直启 flag，靠 prompt 触发。
- **并存** SEPR `.claude/agents/*.md` 三层硬化（堵 C1）：不动。codex sub-sub 在 codex 侧 spawn，不碰 Claude 叶子层硬约束。
- 相关 note：`notes/sepr_model_routing_gpt55_claude_code-CN.md`（全 Sonnet 路由）、`notes/codex_custom_agents_cli_support-CN.md`（toml 格式核验）、`notes/subagent_policy_comparison-CN.md`（三类 agent 子 agent 机制对比）。
