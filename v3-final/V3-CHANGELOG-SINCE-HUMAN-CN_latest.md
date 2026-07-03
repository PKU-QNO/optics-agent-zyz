# SEPR 设计变更总览：从 `.human` 到现在（说人话）

> **用途**：你只清楚记得最早的 `.human` 设计，中间迭代了好几轮已经记不清。这份把「从 `.human/DESIGN.md` 那版 → 现在」的所有改动，按主题重新讲成人话，替代散落各处的零碎报告。
> **基准（你记得的那版）**：`self-evo-paper-repro/.human/DESIGN.md`（14 章核心架构 + §15 文献审查）。
> **终点**：截至 2026-07-03 的当前设计，含本次 V3 加固提案。
> **一句话**：架构没变（4 agent + 两套 workflow + 三层子 agent 一直是对的）；变的是**把设计「焊死」得更硬、写出了可执行详版、试过又放弃了 OpenCode、最新一轮把红线下沉到 hooks**。

---

## 0. 一分钟看懂：你记得的 vs 现在

| | 你记得的 `.human` 版 | 现在 |
|---|---|---|
| **架构** | 4 agent（main/sub + evolution/sub-E）+ 复现 10 步 / 自迭代 6 步 + 三层子 agent | **没变** |
| **经验治理** | 六维裁决 + 三级治理 + 经验 4 type + validate_replay | **没变，但加了强制字段/枚举把它焊死** |
| **执行版** | `.claude/skills/` 还是「待写的英文版」（任务9待办） | **已写成中文详细版 6465 行、42 文件，agent 真的在读** |
| **多系统** | 只有 Claude Code | 加过 OpenCode 双系统 + 三文件同步 → **本次又决定放弃** |
| **子 agent 深度** | 「第 3 层不再 spawn」写在 prompt 里 | 落成 `.claude/agents/` 配置文件 → **本次要用 `sub-leaf` 从框架层焊死** |
| **红线** | 写在 skill/prompt 正文，靠 agent 遵守 | **本次提案：下沉到 hooks（框架层强制）** |
| **体检** | 无 | 做过两轮：设计审计 + 文献可借鉴经验，**发现一批 gap 大多未修** |

**三句话总结**：① 中间几轮主要在做「防翻车加固」——给流程加强制字段、枚举、上限、schema；② 把设计从纸面写成了 agent 能跑的详版，并试验了 OpenCode 备选又放弃；③ 最新一轮（本次）方向是把红线从「求 agent 遵守」变成「框架强制」。

---

## 1. 基准回顾：你的 `.human` 设计到底是什么（30 秒）

`.human/DESIGN.md` 定的东西（这些一直没变，是地基）：

- **4 agent 两套对称 workflow**：复现（main-agent 编排 10 步 + sub-agent 执行）/ 自迭代（evolution-agent 编排 6 步 + sub-E-agent 执行）。互不交叉，执行者不总结自己（防 self-bias）。
- **三层子 agent**：编排者不干隔离活，执行者 spawn 子子 agent 干单点小活，第 3 层不再 spawn。
- **经验治理**：ECC 6 条改动 + 六维裁决（Save/Improve/Absorb/**Fork/Archive**/Drop）+ 三级治理（Tier-1/2/3 按 case 数×证据）+ 经验 4 type（GUIDING/CAUTIONARY/FACT/PROCEDURE）。
- **E-flow 不调 W-flow**：validate_replay 分 A/B/C 层，核心方法改动标「需人工重跑」。
- **留痕**：`.work/` 沙箱、`toEflow/` 只增不删、`.E-history/`、`todo.md`、记忆 provenance 五要素。
- **物理验证**：PyMieScatt 弃用，改 3 层物理检验。
- **§15**：94 篇文献审查 + 16 条风险建议已落地。

**注意**：`.human/DESIGN.md` 停在这里就没再更新了——它里面 §1 还说「`.claude/` 会写英文版」、§14 还把「任务9 转 .claude」列为**待办**。这些在后面几轮全变了，但 `.human` 文档本身没同步（下面第 5 节会点这个「基准文档本身也过时了」的问题）。

---

## 2. 变更时间线（一张表看全）

| 阶段 | 时间 | 干了什么 | 记录在哪 |
|---|---|---|---|
| 六 | 2026-06-29 | 94 篇 v3 文献审查（A–K 11 类），出 REVIEW-REPORT | `REVIEW-REPORT_archive.md`，已并入 `.human` §15 |
| 七 | 2026-06-29 | 16 条风险建议全部落地（P0/P1/P2）+ 失败防护 | `.human` §15 表格 + 各 skill |
| 八 | 2026-06-30 | **写出 `.claude/skills/` 中文详版 6465 行** + **加 OpenCode 双系统** + 三文件同步规则 | WORK_LOG 阶段八 |
| 九 | 2026-06-30 | 子 agent 深度/工具落成 `.claude/agents/` 配置（+ OpenCode 6 agent 对齐） | WORK_LOG 阶段九 |
| 审计A | 2026-07-02 | 设计审计：发现 capsule 断裂/路径漂移/文档过时/深度软约束等 gap | `DESIGN-GAP-AUDIT-CN_latest.md` |
| 审计B | 2026-07-02 | 6 路文献「可借鉴经验+风险」总汇，8 条铁律 | `BORROWABLE-EXPERIENCE-CN_latest.md` |
| 清理 | 2026-07-02 | 修 7 处口径 bug（result_class 旧口径、四选一残留等） | `CLEANUP-A-LOG-CN_archive.md` |
| **十（本次）** | 2026-07-03 | **放弃 OpenCode + V3 加固提案（hooks 红线/leaf 硬化/skills 预加载）+ 官方核验** | `V3-HARDENING-DESIGN-CN_latest.md` |

---

## 3. 逐块讲人话

### 3.1 风险审查把设计「焊死」了一批（阶段六–七，§15 的 16 条）

**原来**：六维裁决、Tier 治理、报告、result 判断这些机制**写在流程说明里**，靠 agent 照做。
**变成**：给它们加了**强制字段和枚举**，不照做就打回：

- **result_class 变成 7 级强制枚举**（`not_run` → `physical_reproduction_success`），**禁止**把 fallback/diagnostic/pipeline_completed 当物理复现成功。这是最重要的一条——防 AI 自己把「跑通了」说成「复现成功了」。
- **verifier 每条加适用条件**（Applicable/Tolerance/Failure means/Not applicable），硬约束失败自动把 result_class 压到 ≤ diagnostic_only。
- **冲突台账 conflict_ledger**：经验打架不自动和稀泥，进 Tier-2/3 人审。
- **Tier 改成二维**（case 数 × 决策级别）。
- **报告字段焊死**：子 agent 报告固定头 6 字段 + 每条判断带 uncertainty + missing_evidence；provenance 五要素统一字段名。
- **防空跑**：每步 retry_budget + blocker_condition，同一步最多重跑 5 轮且每轮要有新证据，run_manifest 记 fan_out/depth/result_class。
- **蓝图**：补全 schema（参数/单位/范围/资源上限/verifier_hooks/stop_rules）+ sweep_manifest 支持复跑单点。

**一句话**：这一轮没改架构，是把「可能被 AI 钻空子」的地方全部加了硬字段/硬上限。**已落地**（写进了 skill 文本）。

### 3.2 `.human` → `.claude` 详细执行版真写出来了（阶段八）

**原来**：`.human/DESIGN.md` 把「任务9：把中文设计稿转成 `.claude` 执行版」列为**后期待办**。agent 当时没有可直接读的详版。
**变成**：写出了 **`.claude/skills/` 中文 prompt-engineered 详细版，4 身份共 6465 行、42 个文件**，每个 workflow 步骤都有拼好的完整 spawn 指令 + retry_budget + blocker_condition + 决策问题 + gate。**这是 agent 现在实际运行时读的东西**。

**注意**：原计划说要写「英文版」，实际写的是「中文详版」——够用，英文版降级为可选后期优化。所以 `.human`（大纲）和 `.claude`（详版）现在是**同义不同详细度**，不是逐字镜像。**已落地**。

### 3.3 加了 OpenCode 双系统，然后本次又放弃它（阶段八 → 阶段十）

**原来**：只面向 Claude Code（Opus）。
**中间加了**：因为担心 Opus 不稳定，加了 **OpenCode（GPT-5.5 备选）**——`opencode.json`（6 agent 配置）+ `.opencode/prompts/`（6 角色）+ 启动脚本。并因此立了**三文件同步规则**：`CLAUDE.md`/`AGENTS.md`/`opencode.json` 改一个必须同步改另两个，否则两系统行为分叉。
**本次（阶段十）决定**：**暂时放弃 OpenCode 兼容**。理由：① 可以放心用 Claude 专属的 hooks；② 卸掉三文件同步这个持续负担；③ 双系统本身制造了不对称 gap（见 3.5 的 C1）。**只是暂时**——不删文件，只标 deprecated，撤销点登记在提案 §6。**决定已定，文件清理未执行**。

### 3.4 子 agent 深度/工具：从「口头约定」到「配置文件」（阶段九）

**原来**：「第 3 层不再 spawn」「子 agent 只给这些工具」写在 prompt/说明里。
**变成**：落成 **`.claude/agents/` 4 个配置文件**（main/sub/evolution/sub-E），带 `tools`/`disallowedTools`/`maxTurns`（编排层 50、执行层 15）；OpenCode 侧对应 6 agent + 2 个 leaf（`task: deny`）。
**遗留问题**：Claude 侧当时**没有独立的叶子 agent**——第 3 层复用 `sub-agent` 身份，而它带 `Agent` 工具，所以「叶子不再 spawn」在 Claude 侧其实**还是软约束**（OpenCode 侧才是硬的）。这个不对称就是下面审计抓到的 C1，也正是本次要修的。**已落地（但留了 C1 这个洞）**。

### 3.5 做了两轮「体检」，发现一批洞（阶段审计，2026-07-02）

这两轮是**分析**，不是改代码——所以发现的 gap **大多还没修**，等你拍板：

**设计审计**（`DESIGN-GAP-AUDIT-CN_latest.md`）抓到的主要洞：
- **A1（首跑阻断级）**：自迭代要读 `capsule.md`，但复现流程从不产出它，路径也不在目录约定里——**E-flow 首跑会找不到输入**。
- **A2**：路径约定三套打架（`.work/.todo/<paper>/` vs `.work/<case>/` vs `.work/self-iteration/`）。
- **B 级漂移**：`.human`/PROJECT_STATUS 说 `.claude` 是「待写英文版」（其实中文详版已完成）；evolution skill 里还残留「四选一裁决」（实为六维）；todo 模板还用违禁旧口径。
- **C1**：就是 3.4 说的深度软约束不对称。
- **C2/D**：PyMieScatt 已弃用但残留脚本；`pdf`/`magnus` 域 skill 是空骨架（预制脚本「待填」不存在），首跑 Mie 会缺脚本。

**文献可借鉴经验**（`BORROWABLE-EXPERIENCE-CN_latest.md`）提炼的 8 条铁律，最关键几条：裁判权归外部确定性 verifier（AI 自评只出候选不定论）；跑通≠物理复现；AI 自动攒技能几乎无用、human gate 才是价值来源；记忆会被过期经验语义污染；**红线要写死成代码不靠 prompt**（← 这条直接催生了本次的 hooks 方向）。还有个扎心结论：**「先跑通再加治理」——SEPR 有 6465 行治理却一篇 Mie 没跑通，属于在验证价值前过度投资治理**。

**状态：发现了，多数未修**（尤其 A1 是首跑阻断级，最该先处理）。

### 3.6 清理了 7 处口径 bug（阶段清理）

`CLEANUP-A-LOG-CN_archive.md`：把纯文本级的口径 bug 修了——result_class 旧口径→7 级、四选一→六维、step11 矛盾块删除、PyMieScatt 脚本删除、OpenCode skill 白名单补齐等。**不动架构/拓扑，已执行未 commit**。

### 3.7 【本次，阶段十】V3 加固提案

方向：**把红线从「求 agent 遵守」下沉到「Claude 框架强制」**，非重架构。详见 `V3-HARDENING-DESIGN-CN_latest.md`。四项第一层改动（**均已过官方文档核验，成立可落地**）：

1. **新增 `sub-leaf`/`sub-e-leaf`**（`tools` 省略 `Agent`）→ 从框架层禁止第 3 层再 spawn，**堵 C1**。
2. **`skills:` 预加载** → 替掉「子 agent 跑起来自己 `skill-print.py` 手动读」的脆弱启动。
3. **hooks 做红线（最高价值）** → 3 类：① `PreToolUse` 拦执行层/叶子提交 Magnus/COMSOL 作业；② `SubagentStop`/`Stop` 门禁拦「无 verifier 产物却报物理成功」；③ `PostToolUse` 校验报告字段。对齐铁律「红线写死成代码」。
4. **`disable-model-invocation`** 给危险 skill（如提交作业）防误触发。

**状态：提案，未落地 SEPR**。放弃 OpenCode 后这些没有双系统同步负担。

---

## 4. 净变化：现在和 `.human` 比，实质差在哪

抛开过程，收敛成 5 条：

1. **同样的架构，但「防翻车」硬了一大截**：result_class 7 级、verifier 适用条件、报告强制字段、防空跑上限、蓝图 schema——都是 `.human` 之后加的焊接。
2. **从纸面变成能跑**：`.claude/skills/` 6465 行详版是新的、真实运行的执行层。
3. **多系统进了又退**：OpenCode 双系统曾是重点，本次决定放弃，回归 Claude 单系统。
4. **深度/红线从软到硬**：`.human` 靠 prompt 约定，现在方向是 `.claude/agents` 配置 + hooks 框架强制。
5. **有了「已知洞清单」**：两轮体检产出的 gap（A1 首跑阻断、路径漂移、空骨架 skill、C1）——`.human` 时代还不知道这些，现在知道了但大多没修。

---

## 5. 状态诚实标注（审核时重点看这个）

| 项 | 状态 |
|---|---|
| 4 agent 架构 + 两 workflow + 三层子 agent | ✅ 已落地（设计+skill） |
| §15 的 16 条风险焊接（result_class/verifier/字段/上限/蓝图） | ✅ 已落地（写进 skill 文本） |
| `.claude/skills/` 中文详版 6465 行 | ✅ 已落地（文件在，agent 读它） |
| `.claude/agents/` 4 身份深度/工具配置 | ✅ 已落地（但留 C1 软约束洞） |
| OpenCode 双系统 + 三文件同步 | ⚠️ 已落地，但**本次决定放弃**（文件未清理） |
| 7 处口径 bug 清理 | ✅ 已执行（未 commit） |
| **审计发现的 gap（A1/A2/B/C1/C2/D）** | ❌ **大多未修**（A1 首跑阻断级最急） |
| **V3 加固（sub-leaf/skills 预加载/hooks/disable-invocation）** | 📋 **仅提案，未落地 SEPR** |
| Mie 第一阶段实际复现 | ⏳ 未启动（教材+论文就位） |

**两个必须知道的诚实点**：
- **基准文档 `.human/DESIGN.md` 本身已过时**（说 `.claude` 待写、任务9 待办，其实早完成）——审核时别把它当现状，它是「起点快照」。
- **最扎心的一条**（BORROWABLE §6.1）：治理写了一大堆，**一篇 Mie 还没真跑通**。所有加固的价值都要等第一次真复现才能验证。

---

## 6. 下一步（建议顺序）

1. **先处理 A1**（首跑阻断级）：让复现流程真产出 `capsule.md`、统一路径约定——否则自迭代根本跑不起来。
2. **补 `pdf`/`magnus` 空骨架 skill**（D）：否则首跑 Mie 会缺脚本。
3. **落地 V3 加固**：按 `V3-HARDENING-DESIGN-CN_latest.md` §4 逐条走 human gate（先做低风险的 sub-leaf + skills 预加载，hooks 是 Tier-3 谨慎上）。
4. **执行 OpenCode 撤销**：按提案 §6 清单。
5. **然后才是真跑 Mie 第一阶段**——用真复现去检验前面所有加固到底值不值。

> 相关文档：起点 `self-evo-paper-repro/.human/DESIGN.md`；过程 `WORK_LOG.md` 阶段六–十；体检 `DESIGN-GAP-AUDIT-CN_latest.md` + `BORROWABLE-EXPERIENCE-CN_latest.md`；本次提案 `V3-HARDENING-DESIGN-CN_latest.md`。
