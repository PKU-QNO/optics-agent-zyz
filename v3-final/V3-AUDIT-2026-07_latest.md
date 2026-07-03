# SEPR V3 对抗性实现审计（2026-07-03）

> **元信息**
> - 日期：2026-07-03
> - 审计者：optics_agent 编排者 CC（元工作区侧）
> - 审计对象：SEPR V3 框架的**当前实现**（`self-evo-paper-repro/.claude/agents/` + `.claude/skills/` + 根配置）+ **未来计划**（`V4-ROADMAP` / `V3-HARDENING` §9）
> - 证据基线：SEPR 本体工作树实际文件（下引 `文件:行`）；内部设计文档 `V3-HARDENING-DESIGN-CN_latest.md` / `V4-ROADMAP-CN_latest.md` / `DESIGN-GAP-AUDIT-CN_latest.md`（2026-07-02）/ `BORROWABLE-EXPERIENCE-CN_latest.md`；外部审查 `V3-EXTERNAL-REVIEW-DELTA-2026-07_latest.md`（v2 深度版，已就绪，本审计引用）
> - **真跑数据状态：无。** `.work/mie`、`.work/comsol`、`.work/.result`、`.work/.todo`、`.result/mie` 全空；`todo.md` 无任何日志段。**本审计 100% 静态**——所有实现结论来自文件核对，所有「预期收益」均未经一次真复现验证。
> - 长期记忆：本会话未挂载 `memento-mcp` 工具，改用 `memory/MEMORY.md` 索引 + 文件核对；结束后按纪律补写记忆文件。

---

## §0 判决摘要（一屏）

**V3 现在健不健康？** **实现层健康、验证层空白。** 加固批次（sub-leaf 硬化 / skills 预加载 / OpenCode 撤销）**真落地了、且与设计自洽**；口径 bug（PyMieScatt/四选一/result_class 旧枚举/step11 自相矛盾）已被 CLEANUP-A 清干净。但两个 P0 自洽 bug（A1 capsule 生产者、A2 路径漂移）**仍未修**，D 空骨架仍在，且**一篇 Mie 都没跑通**——这正是 BORROWABLE §6.1 反复警告的状态：治理/加固投资持续增加，价值一次都没验证过。

**最严重的 3 条**

1. **零真跑数据 = 整套 V3（6465 行 skill + 全套治理 + 本轮加固）从未执行过一次复现。** 每条「预期收益」都是假设。这不是新问题，是 §6.1 铁律仍然成立的证明。审计只能静态，无法判断骨架在真实负载下会先断哪里。
2. **A1（capsule 无生产者）+ A2（路径三套并存）两个 P0 自洽 bug 未修。** A2 比设计文档承认的更急：它不只卡 E-flow，`step10` 同一文件内 `.work/<case>`、`.work/self-iteration`、`.work/.todo` 三套路径并存（`main-agent/workflow/10-summary_and_report/SKILL.md:12,17,65-66` vs canonical `.work/.todo`），**第一次 Mie W-flow 就会踩到**——会让首跑产物落错位、capsule 找不到，污染最宝贵的「什么断了」信号。
3. **C1「深度上限」只堵住了叶子层，sub→leaf 的身份选择仍是软约束。** `sub-leaf`/`sub-e-leaf` 确实无 `Agent`（框架硬约束 ✓），但 `sub-agent` 仍带 `Agent`（`sub-agent.md:4`），「只准派 leaf 身份」仍靠 prompt。sub 若误派另一个 sub，深度可沿官方上限爬到 5 层。设计说 C1「大半消解/堵住」——**overclaim**。

**最该改的 3 条**

1. **A2 路径收敛到一套 canonical，且必须在跑 Mie 前做**（不是设计文档说的「修 A1 时连带、E-flow 前」）。这是让第一次真复现信号干净的前提，低成本 Tier-2。
2. **A1 的「生产侧」拆出、也放到跑 Mie 前**：让 `step11` 就产 `capsule.md`（带 `processed`/`run_id`/`result_class`/`evidence_refs`），否则第一次 Mie 跑完没 capsule，将来开 E-flow 还得回填或重跑。消费侧可留到 E-flow 前。
3. **C1 残留诚实收口**：要么把 `Agent` 从 sub 拿掉、由编排层直接派 leaf；要么补 lineage/depth 硬帽（外部审查 §2.2 的 `maxDescendants`）；至少**停止在文档里说 C1 已堵住**。

**一句话**：方向对、防线（human gate + deterministic verifier + 拓扑写死 + 只碰经验层）经外部 6 篇反驳论文全文阅读后反被强化；但**还欠一次真复现**，且欠修两个 P0 自洽 bug。别再加治理/加固——去跑 Mie。

---

## §1 声称 vs 实际（逐机制核对表）

| # | V3 文档声称 | 实际配置（证据 `文件:行`） | 判定 |
|---|---|---|---|
| 1 | 新增 `sub-leaf`/`sub-e-leaf`，`tools` 省略 `Agent`，框架层禁第 3 层 spawn（C1） | `sub-leaf.md:4` `tools: Read, Write, Edit, Bash, Glob, Grep, ToolSearch, Skill`（**无 Agent**）；`sub-e-leaf.md:4` 同；正文明确「工具清单不含 Agent，框架层无法再 spawn」 | ✅ **真落地，硬约束成立** |
| 2 | 执行层只派 leaf 身份，不再复用带 Agent 的 sub | `sub-agent.md:4` **仍含 `Agent`**；`sub-agent.md` 正文「你 spawn 的 subsubagent 必须使用独立的 sub-leaf 身份」= **prompt 软约束** | ⚠️ **半真**：leaf 侧硬、sub→leaf 身份选择仍软（见 §0-3、§2 C1） |
| 3 | 4 身份 `skills:` frontmatter 预加载；sub-agent 预加载「sub-agent + 当前领域 skill」 | 4 agent frontmatter 均有 `skills:`（`main-agent.md:9-10`=main-agent；`sub-agent.md:9-10`=**仅 sub-agent**；`evolution`=evolution-agent；`sub-e`=sub-e-agent）；leaf 无 `skills:`（保持轻） | ⚠️ **落地但偏离文档**：实际只预加载身份 skill，**未含领域 skill**。此偏离**反而更优**（对齐 §9 D3「领域 skill 用 per-invocation 覆盖避免耦合」+ 外部审查 R1/R3「skill 精简」）；但设计文档 §4.2 文字与实现不一致，应回改文档 |
| 4 | hooks 红线（PreToolUse/SubagentStop/PostToolUse）——最高价值 | `.claude/settings.local.json` 只有隔离配置（autoMemory/bundledSkills/claudeMdExcludes），**无 hooks 字段、无 hooks 脚本** | ✅ **符合计划**：V3 §9 已把 hooks 搁置到 Mie 跑通后，未落地是**正确的**（见 §2 搁置项） |
| 5 | `disable-model-invocation` 防误触发危险 skill | 未见任何 skill frontmatter 设该字段 | ✅ **符合计划**：阶段十一明确搁置（blanket disable 会破坏 COMSOL case 自动加载，正解是 hooks 的 PreToolUse），搁置合理 |
| 6 | 放弃 OpenCode、撤销三文件同步 | `opencode.json`/`.opencode/`/`scripts/start-opencode-sepr.ps1` **已删除**；`AGENTS.md` 为 308 字节 stub；`CLAUDE.md:16` 明确「OpenCode 已撤销、不再有三文件同步约束、DeepSeek 应急」 | ✅ **完全落地、自洽** |
| 7 | result_class 7 级硬规则贯穿 step07/08/10 | `main-agent.md` 正文含「不得把 pipeline_completed/diagnostic_only/surrogate_fallback 当物理复现成功」；`main_report_template.md:271` sweep_manifest 已用 7 级枚举；`todo.md` 模板 7 级 | ✅ **口径已统一**（旧枚举已清，见 §2 B3） |
| 8 | leaf 报告用简化 3 字段、不填 8 字段、禁写 `.result/`/禁声明物理成功 | `sub-leaf.md`/`sub-e-leaf.md` 正文逐条写明 | ✅ **自洽** |

**§1 小结**：本轮加固的 4 项第一层改动（sub-leaf/skills 预加载/OpenCode 撤销/disable-invocation 搁置）**实现与设计基本一致**，唯二偏差是：(a) C1 半软（机制 2，真问题）；(b) skills 预加载未含领域 skill（机制 3，实现更优但文档需回改）。hooks/disable-invocation 未落地是**计划内正确搁置**，非实现缺陷。

---

## §2 已知 gap 现状 + 搁置项正确性

### 2.1 DESIGN-GAP-AUDIT（2026-07-02）已知 gap 的当前状态

| Gap | 优先级 | 2026-07-02 状态 | **2026-07-03 实测状态** | 证据 |
|---|---|---|---|---|
| **A1 capsule 产/消断裂** | P0 | bug | ❌ **仍未修** | `grep capsule step10/11` = 空；消费侧仍在 `evolution/01`、`sub-E/01` |
| **A2 路径漂移** | P0 | bug | ❌ **仍未修，范围确认为三套+裸路径** | `.work/.result`(E输入) + `.work/self-iteration`(旧W) + `.work/.todo`(canonical) 并存；`step10:12,17,65-66` 裸 `.work/<case>` |
| B1 根状态过时 | P0 | bug | ✅ 已修（`CLAUDE.md`/WORK_LOG/PROJECT_STATUS 已同步「中文详版已完成」） | 阶段十一 doc-sync |
| B2 四选一残留 | P1 | bug | ✅ **已修** | `grep 四选一 .claude/skills` = 空 |
| B3 result_class 旧枚举 | P1 | bug | ✅ **已修**（含 sweep_manifest） | `main_report_template.md:271` 为 7 级枚举 |
| B4 OpenCode 白名单 | P0 | bug | ✅ **消解**（OpenCode 已撤销，B4 moot） | `opencode.json` 已删 |
| **C1 深度上限软约束** | P0 | bug | ⚠️ **半修**：leaf 硬、sub→leaf 软 | `sub-leaf.md:4` 无 Agent（硬）；`sub-agent.md:4` 有 Agent（软） |
| C2 PyMieScatt 残留 | P1 | bug | ✅ **已修** | `grep PyMieScatt .claude .human` = 空 |
| **D pdf/magnus 空骨架** | 跑通前 | bug | ❌ **仍未修** | `pdf/SKILL.md:6` `magnus/SKILL.md:6` 仍「空白待填」；无 `scripts/*.py` |
| step11 自相矛盾 | P1(§4.1) | bug | ✅ **已修** | `step11:72`「本步由主 agent 自己执行，不 spawn」；矛盾的 sub spawn 块已删 |

**净状态**：CLEANUP-A + 阶段十一修了 B1/B2/B3/C2/step11 矛盾（口径类），消解了 B4；**A1、A2、D 三个自洽 bug 仍开着**，C1 半修留残。这与 `DESIGN-GAP-AUDIT §5.3` 的判断一致——「最大问题不是治理不够，而是若干设计契约未闭环」。

### 2.2 三个仍开 gap 的堵塞性判断（对抗性）

- **A1（capsule 无生产者）**：**只堵 E-flow 首跑，不堵 Mie**——判断正确。但设计把「产 capsule」整体推到 E-flow 前，是个隐患：第一次 Mie 跑完若不产 capsule，将来开 E-flow 得回填/重跑首篇。**生产侧应前移到 Mie 前**（cheap），消费侧留 E-flow 前。
- **A2（路径三套）**：设计文档把它归为「修 A1 时连带、E-flow 前」——**低估了**。`step10` 是 W-flow（跑 Mie 必经）步骤，同一文件三套路径，第一次真复现的 sub-agent 就要在运行时二选一，产物可能落到 E-flow 找不到的位置。不是硬 block，但**直接污染首跑信号质量**，应升级为「跑 Mie 前必修」。
- **D（pdf/magnus 空骨架）**：`magnus` Mie 阶段大概率不碰（纯 Python），可留「待实现不可依赖」。但 `pdf` 骨架**声称了不存在的脚本**（`extract_pdf.py`/`digitize_figure.py`，实测无 `.py`）——这是 BORROWABLE §6.5 的 declared-vs-actual 坑。Mie step01 若真要读 Akimov 提参/图数字化，会误以为脚本就位。**开跑前应把不存在的脚本一行标「不可依赖」**（Tier-1），别等运行时才发现。

### 2.3 搁置项（hooks / disable-model-invocation）的正确性

**判定：搁置正确，重启条件合理。**

- **hooks 搁置**：V3 §9.1 的理由站得住——(a) hooks 是新框架级强制层，撞 §6.1「跑通前别过度投资治理」；(b) Hook #2/#3 要 gate 的 verifier 产物**现在还不存在**（D gap），等于给没造出来的东西装门禁。**这是本审计最认同的一个判断**：一个团队在没跑通一篇复现前，先造框架级门禁，是典型的「验证前过度投资」。
  - **一个补充异议**：Hook #3（报告字段 schema 校验）**不依赖 verifier 产物**，只依赖报告存在（首跑即有）。它是三个 hook 里最便宜、且直接对治 §2.1「子 agent 漏字段」的固有弱点（子 agent 架构报告靠自觉、非 100% fire）。可考虑在首跑**并行**试点 Hook #3，而非把三个 hook 捆绑一起等。但这属 nice-to-have，不推翻「hooks 作为一类搁置」的主结论。
- **disable-model-invocation 搁置**：正确。阶段十一的理由（blanket disable 会破坏 COMSOL case 自动加载，正解是 hooks 的 PreToolUse 拦 submit）是对的——这个字段粒度太粗，会误伤。
- **重启条件（V4-ROADMAP §3）合理性**：Hook #2 需「Mie 跑通 + verifier 存在 + 出现 result_class 误判」、A1 需「开首次 E-flow 前」、D 需「开跑前 5 分钟核」——**信号驱动、条件明确、可证伪**，符合 §6.1。唯一要修正的是 A2 的时机（见 §2.2）。

---

## §3 未来计划（V4-ROADMAP）风险审查

**总评：V4-ROADMAP 是三份文档里纪律性最强的一份**——L1/L2/L3 分层清晰，每条改进标「重启条件 + 堵哪个 gap」，反复强调「没信号=不做」，E-flow 六前置条件合理。以下是对抗性风险点：

1. **【中】A2 时机误判（已在 §2.2 展开）**：roadmap D3 把 A2 列为「修 A1 时连带（E-flow 前）」，低估其对 W-flow 首跑的污染。**建议改为跑 Mie 前必修。**
2. **【中】meta-risk：文档在增殖，Mie 没在跑。** V3-HARDENING(327行) + V4-ROADMAP(342行) + BORROWABLE + 本审计——workspace 持续产出设计/审计文档，而 §6.1 说的「先跑通」始终没发生。roadmap 自己诊断了这个病（§0「一篇 Mie 都没跑通，正是 R2 警告的状态」），但**产出又一份规划文档本身就是症状**。**这份审计的唯一有价值行动项就是：停止写文档，去跑 Mie。**
3. **【中】信号盘依赖操作者自觉记录，无硬 gate。** §5 人工预训练循环第 2 步「什么真的断了」清单是「本轮最有价值产物」，但它靠单个 Claude Code 操作者**自觉**对照 §2 五类信号逐类填——这正是 roadmap 自己引用的「子 agent 报告靠自觉、非 100% fire」弱点的翻版，只是换到了人身上。没有机制保证信号日志被填。**建议**：把「什么断了」清单做成 W-flow step11 的强制产出字段（run_manifest 里），而非事后人工回忆。
4. **【低】E-flow 前置条件 3「verifier 稳定（多 case 验证）」与条件 6「baseline 有数」互相耦合且门槛高**——都要多个 case。这是**正确的高门槛**（防过早自迭代），但要诚实告诉用户：按 §6.3 的时间感，E-flow 是 V5/V6 的事，别在 V4 期待它。roadmap 已如实标注，无需改，仅确认。
5. **【低】L3 项（anytime-valid/utility_score/baseline ABCD）投资风险**：这些是「攒够 case 后」的远景，roadmap 正确地没让它们进 V4 必做。风险不在 roadmap，在**未来不要被外部文献（GRASP/PACE/Assay）诱导提前实现**——它们学术上诱人，但都是「跑通后按真断点加」的东西。保持 §6.1 纪律。

**§3 结论**：V4-ROADMAP 无结构性缺陷，风险集中在「A2 时机」和「继续写文档而不跑」两点。计划本身是可执行的、诚实的、不过度承诺的。

---

## §4 外部证据对照（引 `V3-EXTERNAL-REVIEW-DELTA` v2）

外部审查（v2 深度版，6 篇反驳论文全文阅读）**已就绪并通读**。其净结论与本审计一致：**V3 防线大多被强化，反驳是「归因/前提/结构需修正」而非推翻**。逐条采纳/噪声判定：

### 4.1 采纳（真信号，动摇了 V3 的某个具体假设）

| 外部条目 | 来源可信度 | 对 V3 的动摇 | 本审计裁决 |
|---|---|---|---|
| **R1**：「禁全量预加载」理由从「撑爆上下文」改「skill shadowing/选择空间污染」 | 高（More Skills Worse Agents arXiv 全文，Δ_shd 占降幅 67%） | 结论对、**归因错** | **采纳**：改文档一句话，零成本。且 SEPR 实测**只预加载身份 skill**（§1 机制 3），已在正确方向 |
| **R3**：verifier+结构化反馈是核心资产，skill 精简验证驱动 | 中（When Skills Don't Help，单 CTF 域 +8.9pp n.s.） | 挑战「6465 行 skill 是核心资产」前提 | **采纳（重要）**：与 §6.1「先跑通」同向。Mie 是高带宽反馈域→优先投 verifier。SEPR 已朝此走（预加载精简） |
| **R4**：物理硬约束 verifier 自身有 silent failure（低 loss 解错/soft constraint 不保证） | 中高（PINN 失败模式一批，NeurIPS/arXiv） | 警告铁律#1/#2 的 verifier 也要被验证 | **部分采纳**：SEPR 走**解析 Mie 路线**（非 PINN），外部审查自己承认这本身规避了大半 PINN 风险。采纳「verifier 也要 MMS/同构扰动/held-out 交叉验」，与既有 D10/held-out 重合，跑通后落地 |
| **R2**：skill 分 protected/identity/task-conditional，第三类按任务 mask | 高（Assay arXiv 全文，跨任务符号反转） | 挑战「固定预加载对该身份所有任务非负」 | **采纳但延后**：这是治理结构改动，属跑通后。SEPR 现在预加载最小（仅身份），风险已低，不急 |

### 4.2 噪声 / 不采纳（不动摇 V3）

- **产品性能数字**（Sponsio <0.01ms、AGT 26.67%→0%、supergood 17.2×、Evolvent 相变阈值）：全部单源自述、未独立复现，外部审查自己标 `unverified`。**当噪声**，落地前必自测，不作决策依据。
- **单实验室 n 小博客**（Halt Authority n=17、Taste-Governed RSI n=32，MiniMax-M3 单模型）：方向（无锚自迭代必崩、keep-best 门有效）可信，**确切数字当噪声**。且这些是「支持 V3 治理」的证据，不构成反驳。
- **Agent Teams 社会结构/多 agent 辩论类**：V3 flat fan-out 不适用，N/A。
- **maxDescendants/cascade 控制/记忆 trust-label 传播**（外部 §2.2/§2.5/§2.6）：真信号但属**跑通后/E-flow 前**治理，本轮不动（唯一例外是 C1 残留可借 `maxDescendants` 思路，见 §5）。

### 4.3 外部证据的元诚实边界

外部审查由检索子 agent 用 exa+firecrawl_scrape 抓 arXiv HTML 全文产出（`firecrawl_research_read_paper` API key 不可用）。**本审计未独立复核这些 fetch**——我采信搜索 agent 的全文阅读结论。多数为 2026 年新预印本（2605.xxx/2606.xxx），引用数低。因此外部证据的**方向**可信（多篇互相印证 V3 防线），但**任何单篇的确切数字不应写进 SEPR 本体做硬依据**，与外部审查 §3.3 自己的告诫一致。

**§4 结论**：外部证据净效应是**强化 V3 核心防线 + 4 条边际修正（R1-R4）**。最强的 R3 与 V3 §6.1「先跑通再加治理」同向，V3 可无痛吸收。没有任何一条外部证据推翻 V3 的骨架决策（human gate / deterministic verifier / 拓扑写死 / 只碰经验层）。

---

## §5 排好序的行动清单（现在 / 等 Mie / 丢）

> human gate 级别沿用 SEPR 口径：Tier-1=例行审阅；Tier-2=人工审查后合入；Tier-3=人工评审+首跑验证。

### 现在做（跑 Mie 前，都是低成本堵自洽 bug，不是新治理）

| # | 行动 | 理由 | gate |
|---|---|---|---|
| N1 | **A2 路径收敛到一套 canonical**（`.work/.todo/{paper}/{case}/{ts}/` + `.work/.evolution/{ts}/` + `.result/{paper}/`），删/迁 `.work/<case>`、`.work/self-iteration`、`.work/.result` | W-flow step10 就踩，污染首跑信号；`DESIGN-GAP-AUDIT A2` 建议动作现成 | **Tier-2** |
| N2 | **A1 生产侧前移**：`step11` 必产 `capsule.md`（`processed`/`run_id`/`result_class`/`evidence_refs`/provenance 五要素），路径与 E-flow 输入统一 | 否则首篇 Mie 跑完无 capsule，将来开 E-flow 要回填/重跑 | **Tier-2** |
| N3 | **D pdf 骨架诚实化**：把 `extract_pdf.py`/`digitize_figure.py` 等不存在脚本一行标「待实现，不可依赖」；开跑前 5 分钟核 Mie step01 是否真需 PDF 提参/图数字化 | declared-vs-actual 坑（BORROWABLE §6.5）；别让 workflow 误以为脚本就位 | **Tier-1** |
| N4 | **C1 残留收口（二选一）**：(a) 从 sub 拿掉 `Agent`、编排层直接派 leaf；或 (b) 至少改文档停止说「C1 堵住」，登记「sub→leaf 身份仍软、深度硬帽是官方 5 层非 SEPR 3 层」 | 现文档 overclaim；真硬帽只在 leaf | **Tier-2**（(a) 是执行层安全约束改动） |
| N5 | **回改设计文档**：V3-HARDENING §4.2「sub-agent 预加载 sub-agent + 领域 skill」→ 改为「仅身份 skill，领域 skill per-invocation」，与实现对齐（且外部 R1/R3 支持精简） | 声称 vs 实际不符（§1 机制 3） | **Tier-1** |

### 等 Mie 跑通后按信号做（信号出现才做，没信号不做）

| 行动 | 重启信号 | 依据 |
|---|---|---|
| Hook #3 报告字段校验（可提前试点，不依赖 verifier） | §2.1 子 agent 漏字段 | V4-ROADMAP §3.1 + 本审计 §2.3 补充异议 |
| Hook #2 完成门禁（拦无 verifier 产物报物理成功） | result_class 误判 + verifier 脚本已存在 | V4-ROADMAP §3.1 |
| Hook #1 拦作业提交 + `maxDescendants`/lineage 硬帽 | SEPR 真碰 Magnus/COMSOL + 越权提交 | V4-ROADMAP §3.1 + 外部 §2.2 |
| A1 消费侧 + result_class 机理维/V&V 分离 + held-out/同构扰动 | 开首次 E-flow 前 / result_class·verifier 信号 | V4-ROADMAP §4.2 L2 |
| 记忆治理（valid_to/quarantine/utility_score） | 第 2-3 个 case 出现记忆污染 | V4-ROADMAP §4.2/4.3（库还空，本轮看不到） |
| 「什么断了」清单做成 step11 强制字段 | 首跑后发现信号日志靠自觉会漏 | 本审计 §3-3 |

### 丢 / 长期冻结（不投资）

| 项 | 理由 |
|---|---|
| 外部审查的产品性能数字、单实验室 n 小博客确切数值 | 未独立复现，噪声（§4.2） |
| Agent Teams 进复现主路径 | 已否决，红线 |
| OpenCode 恢复准备（§6.3 恢复点）| 已撤销；`opencode.json` 等已删，恢复点登记留档即可，不投资 |
| L3 治理（baseline ABCD / anytime-valid / utility_score / 执行真实性分级）提前实现 | V5/V6 远景；别被 GRASP/PACE/Assay 诱导提前造（§3-5） |
| 再写一份设计/规划文档 | meta-risk（§3-2）；下一个动作应是跑 Mie，不是写文档 |

---

## §6 诚实边界

**没有真跑数据的部分（本审计的最大局限）**：
- 整个 §1「实现自洽」只证明**静态配置正确**，不证明**运行时正确**。sub-leaf 无 Agent 是文件事实，但「运行时该 agent 上下文真无 Agent 工具」我未实跑验证（官方文档核验说成立，我采信 `claude-code-docs-agent` 的核验，未亲测）。
- 所有「A2 会污染首跑」「A1 首跑无 capsule」是**基于文件的推断**，不是观测——第一次 Mie 跑完才能证实/证伪。
- skills 预加载在 fan-out 下的真实上下文成本（sub skill 1650 行 × N 并发）未实测（V3 §9.3-3 的技术未知仍未知）。

**推测而非事实的部分**：
- 「A2 升级为跑 Mie 前必修」是我的优先级判断，不是硬 blocker——A2 不会让运行**崩**，只会让产物落错位/信号变脏。若用户认为首跑就是探路、脏一点无所谓，可接受不修先跑（但那样首跑信号价值打折）。
- 「Hook #3 可提前试点」是补充异议，非主结论；捆绑等 Mie 也合理。
- C1 残留的严重性取决于「sub 会不会误派 sub」——正常 prompt 下不会，但这正是「靠 prompt 不靠框架」的软肋，攻击面存在。

**采信未复核的部分**：
- 外部审查 6 篇反驳论文全文阅读结论（§4）我采信搜索 agent，未独立复核 fetch。
- 官方 Claude Code 能力核验（hooks 30 事件 / skills 字段 / disable-model-invocation 属 skill frontmatter）采信 `claude-code-docs-agent`（changelog 至 2.1.199），未亲测。

**确定的部分（文件事实，可复核）**：sub-leaf/sub-e-leaf 无 Agent；sub/sub-E 有 Agent；4 agent 有 skills 预加载（仅身份）；opencode.json 已删；A1 无 capsule 生产者；A2 三套路径并存；D 空骨架无脚本；B2/B3/C2/step11 矛盾已清；无任何真跑产物；无 hooks。

---

**本报告结束。** 定位：SEPR V3 实现+计划的对抗性静态审计（无真跑数据）；下一步唯一有价值的动作是**在 SEPR 跑通第一篇 Mie（Akimov 2401.04146）**，跑前先做 §5「现在做」的 N1-N5（尤其 A2 路径收敛），跑后按 §5「等 Mie」信号驱动增量加治理。核心判据不变：**先跑通，再加护栏。**
