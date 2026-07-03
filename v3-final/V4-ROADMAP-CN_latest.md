# SEPR V4 路线图：跑完 Mie 后如何把 V3 改进到 V4（前瞻规划，人话版）

> **元信息**
> - 日期：2026-07-03
> - 产出侧：optics_agent（设计 SEPR 框架的元工作区）。SEPR 本体在 `C:\Users\27370\Desktop\project\self-evo-paper-repro`。
> - 承接：`V3-HARDENING-DESIGN-CN_latest.md`（V3 加固提案，尤其 §9 待决问题与再排序）、`DESIGN-GAP-AUDIT-CN_latest.md`（gap 审计）、`BORROWABLE-EXPERIENCE-CN_latest.md`（可借鉴经验，尤其 §6.1「先跑通再加治理」、§4.2 缺口清单）、`V3-CHANGELOG-SINCE-HUMAN-CN_latest.md`（从 .human 到现在的净状态）。
> - **文档性质：前瞻规划（forward-looking roadmap），不是承诺。本文是「跑通后再定」的地图，不修改 SEPR 本体任何文件。很多分支取决于 Mie 第一阶段实跑结果——凡标『取决于实跑』的条目，实跑没发生前都只是候选，不落地。**
> - **诚实口径**：本文所有「预期收益」都是假设，未经第一次真复现验证；本文所有「重启条件」都是触发器，触发器没出现就不做。这与 BORROWABLE §6.1 铁律一致——先证明价值，再加护栏。

---

## 0. 一屏结论

**V4 不是推倒重来。** V4 = 「据第一次真复现（Akimov 2401.04146 Mie 第一阶段）暴露出的经验，人工改进 V3」。V3 是 SEPR 的 Claude Code 三层子 agent 方案（`main`/`evolution` → `sub`/`sub-e` → `leaf`）；V4 是它的下一个人工迭代版本，改动都走 human gate。

**核心判据（贯穿全文，来自 BORROWABLE §6.1）**：**只有第一次真复现暴露出的问题才值得投入治理**。不要在验证价值前继续堆治理。SEPR 现在有 6465 行 skill + 全套治理，却一篇 Mie 都没跑通——这正是 V2 废案审计 R2 警告的状态。所以本文的结构不是「治理清单」，而是「先看什么信号 → 哪些信号触发哪些改进」。

**四条不可违反的红线（V4 必须继承，本文不违反）**：
1. **拓扑写死，人工管。** agent 不得自动改拓扑 / 节点指令 / 分支条件。V4 所有改动都在「节点内工具与护栏」层。
2. **自迭代只碰经验层，全走 human gate。** 不改 workflow 拓扑、蓝图结构、根配置。
3. **agent 不得自动改规则 / 上限 / 验证器。** 失败防护、上限、verifier 对 agent 只读。
4. **不把 Agent Teams 放进复现主路径。** 仅后期人工审查 / devil's-advocate 模式。

**本文回答五个问题**（对应五个小节）：
- §2：跑完 Mie 第一阶段后，**先看什么信号**（哪些运行现象/失败告诉我们该改什么）。
- §3：**被搁置项的重启条件**（hooks / A1 capsule / D 空骨架 skill）。
- §4：**V3→V4 候选改进方向**，按「跑通后才值得加的治理」分层，每条标重启条件 + 预期收益。
- §5：**人工预训练循环怎么转**（跑 Mie → 反馈 → 人工审改 → 重跑，每步产出什么、谁审）。
- §6：**什么时候才考虑真开 E-flow 自迭代**。

---

## 1. 前提对齐：现在的净状态（V4 的起点）

从 `V3-CHANGELOG-SINCE-HUMAN-CN_latest.md` §5 收敛，V4 起跑线如下：

| 项 | 状态 | 对 V4 的含义 |
|---|---|---|
| 4 agent + 两 workflow + 三层子 agent | 已落地 | V4 不动这套骨架 |
| 16 条风险焊接（result_class 7 级 / verifier 适用条件 / 报告字段 / 上限 / 蓝图 schema） | 已落地（写进 skill 文本） | 这些是 prompt/文本级约束，V4 可能把最关键几条升级为框架强制 |
| `.claude/skills/` 中文详版 6465 行 | 已落地（agent 真在读） | V4 的经验层改动主要改这里的正文 |
| `.claude/agents/` 4 身份配置 | 已落地，**留 C1 软约束洞** | V4 的 sub-leaf 补这里 |
| OpenCode 双系统 + 三文件同步 | 已落地，但 V3 已决定放弃（文件未清理） | V4 需连带处理三文件同步红线 |
| 审计 gap（A1/A2/B/C1/C2/D） | **大多未修** | A1 是 E-flow 首跑阻断级；跑 Mie（W-flow）不被 A1 挡 |
| V3 加固（sub-leaf / skills 预加载 / hooks / disable-invocation） | **仅提案，未落地** | hooks 已被 V3 §9 搁置到 Mie 跑通后 |
| Mie 第一阶段实际复现 | **未启动**（教材 + 论文就位） | **这是 V4 一切改进的信息来源** |

**关键边界重申（来自 V3 §9.1）**：跑 Mie = W-flow（复现），A1 只阻断 E-flow（自迭代）——**跑 Mie 不必先修 A1**。V3 已把 hooks 从「第一层直接用」拆出、推迟到首篇 Mie 跑通后；`sub-leaf` + `skills` 预加载是真·低成本，可在跑 Mie 前先做（可选）。V4 继承这个排序。

---

## 2. 问题一：跑完 Mie 第一阶段后，先看什么信号

**原则**：不带答案去跑。跑之前不预设「该改 hooks / 该改记忆」，而是让第一次真复现自己暴露断点。下面是「该盯的信号盘」——每类信号出现，才对应触发某类改进（触发的具体条目见 §4）。信号分五类，对应 SEPR 五个最可能先断的地方。

### 2.1 子 agent 空跑 / 假完成信号

**盯什么**：
- 子 agent 是否「跑起来但没干实事」——报告写了但没有对应产物落盘；retry 打满 5 轮却每轮换汤不换药（语义循环）；fan_out 派了但 leaf 回传的是自然语言总结而非路径 + 数值。
- 报告固定头 6+8 字段是否真的每次都齐——SEPR 是 claude 子 agent 架构，报告靠 agent 在 prompt 要求下**自觉**写，天然会漏写/不写（V3-CHANGELOG §3.4 + BORROWABLE §6.3 capsule 100% fire 那条：子 agent 架构相对 runner 的固有弱点）。

**若出现 → 触发**：报告字段 schema 强约束（§4 D1）；Hook #3 报告字段校验（§3.1 hooks 重启）；capsule 100% fire 机制（§4 D6）。

### 2.2 result_class 误判信号（最高优先级信号）

**盯什么**：
- 有没有把 `pipeline_completed` / `diagnostic_only` / `surrogate_fallback` 写成或暗示成 `physical_reproduction_success`（Degiron v2 的历史病：跑到本征求解器但 neff 全零，却差点被当成功）。
- 「跑通 / 无报错 / 数值对上 / 收敛」有没有被当物理复现成功（BORROWABLE 铁律 #2）。
- verifier 三层判据实际执行了没有——硬约束失败有没有真的把 result_class 压到 ≤ diagnostic_only，还是 agent 绕过了。

**若出现 → 触发**：Hook #2 完成门禁（拦「无 verifier 产物却报物理成功」，§3.1 hooks 重启）；result_class 补机理维/诚实维（§4 D4）；verifier V&V 分离（§4 D8）。

> 这是**最该盯的信号**。核心卖点就是「可验证物理复现」；result_class 误判 = 核心卖点直接失守。

### 2.3 记忆污染信号

**盯什么**：
- memento 检索有没有把「失败/代用/过期」经验按语义相似捞回来当成功经验用（BORROWABLE §2 主题五头号坑：向量相似分不清「已作废」和「又说了一遍」）。
- fallback / surrogate / failed probe 的记忆有没有带强 result_class 标签——没标签的话，未来会被当「成功复现经验」检索回来。
- 有没有「每次写回重压全库」的动作（BORROWABLE 头号坑：越压越烂，实验从 100% 压到 46% 错）。

**若出现 → 触发**：记忆治理落地（`valid_to` / quarantine / trace，§4 D5）；记忆 utility_score / forbidden_region（§4 D9）。

> **注意**：Mie 第一阶段是**第一篇**，记忆库还空，污染信号大概率**这轮看不到**——它是攒到 2-3 个 case、开始跨 case 检索时才炸的。所以本类信号更可能在 §5 循环第 2-3 轮才出现，Mie 首轮先记录「记忆写了什么、带没带标签」即可，不急着建治理。

### 2.4 spawn 模板不够信号

**盯什么**：
- spawn 四要素（目标 / 格式 / 工具 / 边界）够不够——子 agent 有没有因为边界没说清而越权（比如去提交作业、去改规则文件）。
- 红线在模板里的位置有没有「迷失在中间」——夹在中段的红线被无视（BORROWABLE §2 主题二 Lost in the Middle）。
- 一次压 9 类约束，子 agent 有没有漏做某几条（ManyIFEval：一次塞十条规矩成功率骤降）。
- leaf 身份 spawn 出来的东西，`Agent` 工具在不在（C1 软约束是否真的漏了）。

**若出现 → 触发**：sub-leaf 硬化（§3.2 A1/C1 相关）；红线三明治 + 显式优先级（§4 D2）；spawn 结束前逐条自检清单（§4 D2 附带）。

### 2.5 verifier 漏判 / 误判信号

**盯什么**：
- 物理 verifier 该抓的抓住了没有——silent incorrect computation（跑完不报错、结果看着合理其实物理错，BORROWABLE §2 主题六）有没有溜过去。
- verifier 会不会误杀正确模型 / 放过错误模型（Physics Constraint Paradox 2512.22261：约束不是加得越多越好）。
- 三层验证（能量守恒 / Rayleigh + large-size 极限 / 论文图定量比较）各层实际触发了没有、失败含义写清了没有。
- 有没有「过拟合论文那几个数据点」的迹象——换论文没标注的中间点会不会崩。

**若出现 → 触发**：verifier V&V 分离 + 每层失败含义（§4 D8）；同构扰动 / held-out 点（§4 D10）；蓝图 verifier_hooks 物理契约反推（§4 D11，主要对 COMSOL case，Mie 纯 Python 可能用不上）。

### 2.6 信号盘小结

| 信号类 | 一句话 | 触发的主要改进 | 本轮 Mie 能否看到 |
|---|---|---|---|
| 子 agent 空跑/假完成 | 报告写了没干活 / 字段漏写 | 报告 schema / Hook #3 / capsule fire | 能 |
| result_class 误判 | 把跑通当物理成功 | Hook #2 / 机理维 / V&V | 能（最该盯） |
| 记忆污染 | 过期经验按语义捞回 | 记忆治理 / utility_score | **大概率看不到**（库还空） |
| spawn 模板不够 | 边界没说清/红线被无视 | sub-leaf / 三明治 / 自检清单 | 能 |
| verifier 漏判 | silent 算错溜过去 | V&V 分离 / held-out / 契约反推 | 能 |

> **诚实标注**：Mie 第一阶段是纯 Python 解析复现，大概率**不碰** COMSOL/Magnus（作业提交类信号、蓝图契约反推信号本轮多半看不到）。开跑前 5 分钟应核一遍 Mie 一阶段是否触及 `pdf`/`magnus` 空骨架 skill（V3 §9.3-4）。

---

## 3. 问题二：被搁置项的重启条件

V3 §9 明确搁置了三类东西。下面逐类给出「什么信号出现才值得做」+「先做哪一类」。

### 3.1 Hooks 的重启条件

**为什么搁置（V3 §9.1）**：hooks 是新的框架级强制层，不是「低成本堵 gap」，撞 BORROWABLE §6.1「跑通前别过度投资治理」；且 Hook #2/#3 要 gate 的 verifier 脚本**现在还不存在**（审计 D）——等于给还没造出来的东西装门禁。

**重启总条件**：**第一篇 Mie 跑通之后**（W-flow 完成一次真复现，verifier 脚本已实际存在）。

**先做哪一类 hook**（按信号优先级）：

| Hook | 官方事件 | 重启条件（哪个信号出现才做） | 预期收益 | 前置依赖 |
|---|---|---|---|---|
| **Hook #2 完成门禁** | `SubagentStop`/`Stop` | §2.2 出现 result_class 误判（把跑通当物理成功）**且** verifier 脚本已存在 | 把「无 verifier 产物却报物理成功」从 prompt 求它变框架拦下 | verifier 脚本存在（D gap 已补）；需定义「verifier 产物存在」的确定性判据（V3 §9.2 D7） |
| **Hook #3 报告字段校验** | `PostToolUse`(Write/Edit) | §2.1 出现子 agent 漏写字段 / result_class 非法枚举 | schema 校验的 hook 轻版，挡假完成 | 报告模板字段口径已稳（B3 旧口径已清理） |
| **Hook #1 拦作业提交** | `PreToolUse` | §2.4 出现子 agent 越权提交作业**且** SEPR 开始真碰 Magnus/COMSOL（Mie 纯 Python 大概率不碰，可能整个 Mie 阶段都不触发） | 作业提交权收敛到编排层 + human gate | 需枚举「提交作业」命令指纹（V3 §9.2 D6）；需先核 §9.3-1（agent-frontmatter PreToolUse 能否拦该 agent 自身工具调用） |

**先做顺序建议**：Hook #2 > Hook #3 > Hook #1。理由：#2 直接守核心卖点（result_class）；#3 是 #2 的轻量前置（字段齐了 #2 才好判）；#1 只有真碰作业提交才需要，Mie 阶段大概率排最后。

**技术未知（重启前必核，V3 §9.3）**：
1. agent-frontmatter 的 `PreToolUse` 能否阻断该 agent **自身**发起的工具调用（决定 Hook #1 是「叶子定向硬拦」还是退回全局方案）。
2. hooks 在 Windows / Git Bash 下 shell out 脚本是否可靠（WORK_LOG 记过多处路径/PowerShell 坑）。

### 3.2 A1（capsule 产/消断裂）的重启条件

**是什么（DESIGN-GAP-AUDIT A1）**：E-flow 明确消费 `.work/.result/<case>/capsule.md`，但 W-flow step10/11 从不稳定生产该文件，E-flow 首跑缺输入。**这是 P0 首跑阻断级 gap，但只阻断 E-flow（自迭代），不阻断 W-flow（跑 Mie）。**

**重启条件**：**开第一次 evolution session（自迭代）之前必修**——不卡 Mie。也就是说，Mie 复现全程可以不修 A1；等攒够 case、准备真开 E-flow 时（见 §6）才必须修。

**怎么修 capsule 产/消契约**（DESIGN-GAP-AUDIT A1 建议动作 + 本文细化）：
1. **定义唯一 capsule 契约**：W-flow step10 或 step11 **必须产** `capsule.md`，路径与 E-flow 输入统一（不能一个写 `.work/.result/`、一个写 `.work/.todo/`——先连带修 A2 路径漂移，收敛到一套 canonical 路径）。
2. **capsule 必须带字段**：`processed`（防重复处理）/ `run_id` / `result_class`（7 级枚举）/ `evidence_refs`（指向 provenance）/ provenance 五要素。
3. **100% fire 不靠自觉**（BORROWABLE §6.3）：子 agent 架构下报告靠 agent 自觉写，会漏——要么用 hook 在 `SubagentStop`/`Stop` 强制留痕（与 §3.1 Hook 同源），要么在编排层 step11 逐一校验「本 case 是否产出 capsule」，缺则打回。
4. **A1 修的是 E-flow 输入契约，属经验层/流程产物，不改拓扑**——符合红线。

**前置**：先修 A2 路径漂移（三套路径并存会让 capsule 写错/找错位置）。A1 和 A2 打包一起修。

### 3.3 D（pdf / magnus 空骨架 skill）的重启条件

**是什么（DESIGN-GAP-AUDIT D）**：`pdf`/`magnus` 域 skill 是空白骨架（`scripts/*.py` 列了但不存在，标注「待填」），step01/step06 关键路径依赖它，首跑会靠临时实现。

**重启条件（分域判断，哪些真需要补）**：

| 域 skill | Mie 第一阶段是否需要 | 重启条件 | 建议 |
|---|---|---|---|
| `pdf` | **可能需要**——step01 读 Akimov 论文提参数、可能要图数字化（从论文图读定量点做比较） | **开跑前 5 分钟核**（V3 §9.3-4）：Mie 一阶段是否真要 PDF 提参 / 图数字化 | 若需要：先补**最小可执行**脚本（`extract_pdf.py` / `digitize_figure.py`），或明确改成「用现有工具临时执行，不承诺脚本存在」——**不要让 workflow 误以为脚本已就位**（declared-vs-actual capability 检查，BORROWABLE §6.5） |
| `magnus` | **大概率不需要**——Mie 是纯 Python 解析，不碰 Magnus/COMSOL | 只有 SEPR 真要提交远程作业才补 | Mie 阶段**不补**；标为「待实现，不可依赖」即可 |

**判据**：D 的重启不是「跑通后」，而是「**开跑前核依赖**」——因为它是首跑路径上的脚本缺口，属「跑通前」类 gap（DESIGN-GAP-AUDIT 把 D 标为「跑通前」）。但**只补 Mie 真用到的那一个**（大概率只有 `pdf` 的一两个脚本），不把两个 skill 全填满（那又是过度治理）。

### 3.4 被搁置项重启条件总表

| 搁置项 | 重启条件（触发信号） | 先做什么 | 归属 |
|---|---|---|---|
| **Hook #2 完成门禁** | Mie 跑通 + verifier 存在 + 出现 result_class 误判 | 定义「verifier 产物存在」判据 | 跑通后 |
| **Hook #3 报告字段校验** | Mie 跑通 + 出现子 agent 漏字段 | schema 轻校验 | 跑通后 |
| **Hook #1 拦作业提交** | SEPR 真碰 Magnus/COMSOL + 出现越权提交 | 先核 §9.3-1 技术未知 | 跑通后（Mie 阶段大概率不触发） |
| **A1 capsule 产/消契约** | 准备开第一次 E-flow（自迭代）之前 | 连带修 A2 路径漂移，定义唯一 capsule 契约 + 5 字段 + 100% fire | E-flow 前必修，不卡 Mie |
| **D `pdf` 空骨架** | 开跑前核 Mie 是否需 PDF 提参/图数字化 | 只补最小可执行脚本，或标「不承诺存在」 | 跑通前（开跑前核） |
| **D `magnus` 空骨架** | SEPR 真要提交远程作业 | 标「待实现不可依赖」 | Mie 阶段不做 |

---

## 4. 问题三：V3→V4 候选改进方向（分层，每条标重启条件 + 预期收益）

**分层依据**：BORROWABLE §4.2 缺口清单 + §5.7 + §6.6 合并落地清单，对照 DESIGN-GAP-AUDIT §0.2「跑通后才值得加的治理」。**分三层**：
- **L1 自洽 bug（跑通前 / 立即，不算新治理）**：让已有设计闭环，成本低收益直接。
- **L2 跑通后按信号加的治理**：只有第一次真复现暴露对应问题才做。
- **L3 攒够 case 后才做的治理**：需要多个 case / baseline 才有意义。

> **红线注**：以下所有条目都属「经验层 / 提示词层 / 验证层 / 记忆层」，**不碰拓扑、不改蓝图结构、不改根配置**（符合「自迭代只碰经验层」铁律）。每条能回答「它堵 DESIGN-GAP-AUDIT 哪个 gap 或硬化 BORROWABLE 哪条铁律」。

### 4.1 L1：自洽 bug（跑通前修，不是新治理）

| ID | 改进 | 重启条件 | 预期收益 | 堵哪个 gap |
|---|---|---|---|---|
| D1 | **sub-leaf / sub-e-leaf 硬化**（`tools` 省略 `Agent`） | 跑 Mie 前（给第一次真 fan-out 加硬安全带，可选）；**加了必须同步改 spawn 模板改用 leaf 身份**，否则「派 sub 省略 Agent」与「派 leaf」两套并存成新漂移源（V3 §9.4-3） | 从框架层禁止第 3 层 spawn，取代 prompt 软约束 | C1（P0） |
| D2 | **skills 预加载**（4 身份各加载自己那份 + 当前领域 skill，禁全量） | 跑 Mie 前（可选）；留 `skill-print.py` 兜底 | 替脆弱 bootstrap，子 agent 启动即持有 skill 正文 | 加固 bootstrap 可靠性 |
| D3 | **A2 路径漂移收敛**（三套路径→一套 canonical） | 修 A1 时连带做（E-flow 前）；或更早 | 子 agent 不再写错/找错位置 | A2（P0） |
| D4 | **B 级口径漂移清理**（根状态过时 / 四选一残留 / result_class 旧枚举 / .human vs .claude 定位） | 已部分在 CLEANUP-A 处理；剩余随手清 | 不误导未来 agent | B1/B2/B3/B4 |
| D5 | **放弃 OpenCode 连带三文件同步红线**（CLAUDE.md/AGENTS.md 改「仅 Claude Code」） | 若真放弃 OpenCode：**必须现在就改**，否则规则自相矛盾（V3 §9.4-4）；opencode.json 等标 deprecated 不删 | 卸三文件同步负担，消 C1 双系统不对称成因 | 收尾决定 A |

> L1 里 D1/D2 是 V3 §9 认定的「真·低成本可先做」；D3/D4/D5 是让设计闭环的必要清理。**这一层不等 Mie 跑通**（除 D3 可打包到 A1 一起）。

### 4.2 L2：跑通后按信号加的治理

| ID | 改进 | 重启条件（哪个信号） | 预期收益 |
|---|---|---|---|
| D6 | **报告 8 字段改工具 schema 强约束** + capsule 100% fire + `processed` | §2.1 子 agent 漏字段信号出现 | result_class 用 enum 锁死、字段全 required；schema 强制比 hook 轻版更硬 |
| D7 | **hooks 三类**（见 §3.1） | §2.2/§2.1/§2.4 对应信号 + verifier 存在 | 红线从 prompt 下沉框架层 |
| D8 | **result_class 补机理维/诚实维** + **verifier V&V 分离 + 每层失败含义** | §2.2/§2.5 信号：答案对但机理错 / silent 算错 | replay 回放**过程**不只数值；机理不过禁升物理成功；代码自洽(verification) vs 物理有效(validation) 分开判 |
| D9 | **红线三明治 + 显式优先级** + **spawn 结束前逐条自检清单** | §2.4 信号：红线被无视 / 漏做约束 | 红线首尾各放一遍防 Lost in Middle；显式「全局>局部>主 agent，下游不得放宽红线」 |
| D10 | **verifier 加同构扰动 / held-out 参数点** | §2.5 信号：疑似过拟合论文那几个点 | 抽查论文没标注的中间点，真物理应不变、硬编码会崩 |
| D11 | **蓝图 verifier_hooks 物理契约反推** + 树状 rubric | §2.5 信号 **且** SEPR 真碰 COMSOL（Mie 纯 Python 大概率本轮不触发） | 反推实际求解方程比只比图更早抓错 |
| D12 | **记忆治理落地**（`valid_to` + trace 指针 + quarantine + 禁全库重压 + provenance.jsonl 证据层与 memento 经验层分离） | §2.3 信号：过期经验按语义捞回（**大概率第 2-3 个 case 才出现**） | 作废盖章不删、靠元数据过滤不靠向量相似、外部来源默认低置信 |

> L2 每条都必须先有对应信号才做。**没有信号 = 不做**——这是 BORROWABLE §6.1 的直接执行。D11/D12 本轮 Mie 大概率不触发（无 COMSOL、记忆库还空），列在这里是备着。

### 4.3 L3：攒够 case / baseline 后才做的治理

| ID | 改进 | 重启条件 | 预期收益 |
|---|---|---|---|
| D13 | **held-out 复现集 + 同构扰动 + anytime-valid 接受规则**（e-value/置信序列替代「分数涨就收」） | 有 ≥3-4 个 case + 准备开 E-flow 自迭代 | 防「反复偷看数据」的统计假进步 |
| D14 | **记忆 utility_score + store routing + forbidden_region + observation 存储** | 记忆库攒到有真实失败样本 | 检索分 = 0.5×语义 + 0.5×效用；缺参走 routing 防噪声 |
| D15 | **baseline A/B/C/D**（SEPR vs 裸 Claude Code vs 固定脚本 vs +自迭代） | 跑通几个 case 后 | 用数字证明「比裸 Claude Code 强」，否则核心卖点只是假设 |
| D16 | **执行真实性分级**（emulated < dry-run < real execution，与 result_class 正交） | 有真实 vs 模拟不一致的案例（如 Degiron 模拟通过但真 COMSOL 不同） | 补 result_class 缺的正交维度 |
| D17 | **declared-vs-actual / template_contract / loads_memories allowed_types / candidate_benchmark**（V1→V2 四项消风险） | 攒够 case，benchmark 开始有 drift 风险 | 防 skill 说一套做一套 / 复用带旧假设 / benchmark 污染 |

> L3 是 DESIGN-GAP-AUDIT §0.2 明确标「跑通后」+ BORROWABLE 需要多 case/baseline 才有意义的项。**这些是 V4 的『远景』，不是 V4 第一版必做**——很可能要到 V5/V6（多轮人工预训练循环之后）。

### 4.4 三层小结

```
L1 自洽 bug ──── 跑通前/立即做（不算新治理，让设计闭环）
                 sub-leaf / skills 预加载 / 路径收敛 / 口径清理 / OpenCode 收尾
L2 按信号治理 ── 跑通后、对应信号出现才做（一篇 Mie 能验证大部分）
                 报告 schema / hooks / 机理维+V&V / 三明治 / held-out / 记忆治理
L3 攒够 case ─── 多 case + baseline 后（V4 远景，可能 V5+）
                 anytime-valid / utility_score / baseline ABCD / 执行真实性 / 四项消风险
```

---

## 5. 问题四：人工预训练循环怎么转

**循环定义（来自 optics_agent CLAUDE.md）**：这是**人工**预训练，不是 E-flow 自动。SEPR 复现论文反馈的经验，由 optics_agent 的 CC **人工审查**后改进设计，不是 SEPR 自己跑 E-flow 自动改。

### 5.1 一轮循环的六步（谁做、产出什么、谁审）

| 步 | 动作 | 谁做 | 产出什么 | 谁审 |
|---|---|---|---|---|
| 1 | **在 SEPR 区跑一篇论文复现** | Claude Code 在 SEPR 以 main-agent 身份跑 10 步 W-flow（用 `.claude/skills/` 详版） | run 文件夹产物（.mph/CSV/图/benchmark 落盘）+ 结构化报告 + result_class + `WORK_LOG.md` 更新 + memento 写入 | SEPR 侧 verifier 脚本（确定性）先判，人工事后看 |
| 2 | **收集复现上下文** | SEPR 侧 CC（或人工导出） | `WORK_LOG.md`（完整交接）+ 复现报告（final_report + 三态分开：pipeline/job/physical）+ 「什么真的断了」清单（对照 §2 信号盘逐类记录） | —（这步是打包，不裁决） |
| 3 | **把上下文发回 optics_agent** | 人工（用户把 WORK_LOG + 复现报告发给 optics_agent 的 CC） | optics_agent 侧收到 SEPR 经验输入 | — |
| 4 | **人工审 + 改 V3 设计** | optics_agent 的 CC 读 SEPR 经验，**人工**改进设计（对照 §2 信号 → §3/§4 触发条目） | V4 改动提案（新 papers/SEPR/*.md 或改 SEPR 本体走 human gate）；每条标「哪个信号触发的」+「堵哪个 gap」 | **用户**（judgment call：哪些盲批、哪些逐条 review，见 V3 §9.2 D5） |
| 5 | **在 SEPR 落地改动 + 重跑论文** | 人工在 SEPR 工作区按提案逐条走 human gate 落地，重跑同一篇（或新一篇）验证改进 | 改进后的 run 产物 + 新旧对比（改动前后 result_class / verifier 通过率 / 过度声明率是否变好） | verifier + 用户 |
| 6 | **循环 2-5** | — | 这就是「人工预训练」 | — |

### 5.2 每步的诚实红线

- **第 1 步**：三态必须分开报（`workflow/pipeline completed` / `COMSOL job completed` / `physical reproduction completed`）；scalar diagnostic / surrogate / fallback / failed probe 必须直说，不得当物理复现成功（optics_agent CLAUDE.md Progress Reporting Policy）。
- **第 2 步**：「什么真的断了」清单是这一轮**最有价值的产物**——它决定第 4 步改什么。对照 §2 五类信号逐类填，没断的类别写「本轮未触发」。
- **第 4 步**：optics_agent 的 CC **不直接照搬** SEPR 复现机制到 optics_agent（optics_agent 是 Magnus+COMSOL 工作区，不是复现 agent）；只做「读经验 → 改 SEPR 设计」。改动前查 memento（本项目记忆纪律），改完更新 memento。
- **第 4 步 judgment call**：sub-leaf/skills 预加载类**可盲批**；hooks/OpenCode 撤销/改红线类**必须逐条 review**（V3 §9.2 D5）。
- **不跳步**：不允许「第 1 步还没跑通就先做第 4 步的治理」——那就退回 BORROWABLE §6.1 警告的「验证前过度投资治理」。

### 5.3 循环的输入/输出闭环图

```
[optics_agent 设计 V3/V4]
        │ (人工改进设计)
        ▼
[SEPR 跑复现] ──产出──> WORK_LOG + 复现报告 + "什么断了"清单(对照§2信号)
        │                          │
        │                          ▼ (人工发回)
        └──重跑验证◄──[optics_agent CC 人工审改]──> V4 改动提案(标信号+gap)
                              │ (用户裁决盲批/review)
                              ▼
                      [SEPR 落地 human gate]
```

---

## 6. 问题五：什么时候才考虑真开 E-flow 自迭代

**E-flow（自迭代）是后期才用的**（optics_agent CLAUDE.md：攒够 case 后人工开专门 evolution session）。**在此之前一律走 §5 人工预训练循环，不开 E-flow。**

### 6.1 真开 E-flow 的前置条件（全部满足才考虑）

| # | 前置条件 | 为什么 | 对应 |
|---|---|---|---|
| 1 | **攒够 case**（至少 3-4 篇复现，含成功 + 失败样本） | E-flow 要读多篇 capsule 做并发审查；一篇没法自迭代 | E-flow step01 输入是 `.work/.result/` 下 capsule 列表 |
| 2 | **A1 修好**（capsule 产/消契约闭环） | E-flow 首跑消费 capsule，W-flow 不产就缺输入 | §3.2 / DESIGN-GAP-AUDIT A1（P0 首跑阻断） |
| 3 | **verifier 稳定**（三层验证在多个 case 上被验证过、不误杀不放过） | 自迭代 fitness 必须锚物理 verifier；verifier 不稳 → 自迭代刷假进步 | BORROWABLE §2 主题四；Spontaneous Reward Hacking |
| 4 | **anytime-valid 接受规则就位**（D13） | 否则「分数涨就收」= 统计假进步，必然假阳性 | BORROWABLE §4.2 第 7 条 |
| 5 | **失败防护硬化**（上限/verifier/规则对 agent 只读，框架强制；禁 self-restart） | Sakana 事件：agent 会改自己的限制；E-flow 是最危险的自改场景 | BORROWABLE §2 主题六；红线 #3 |
| 6 | **baseline 有数**（D15，至少能回答「+自迭代 vs 无自迭代」） | 不然无法判断自迭代到底带来收益还是负迁移 | BORROWABLE §6.2 |

### 6.2 E-flow 的红线（开了也必须守）

- **E-flow 只碰经验层**：只更新 skill 内容 + 提示词备注，全部走 human gate；**绝不改** workflow 拓扑、蓝图结构、`AGENTS.md`、或自迭代系统自身（红线 #2/#4/#5）。
- **E-flow 不迭代自己**：自迭代 workflow 的拓扑、节点指令、专用 SKILL 人工写死，禁自我修改。
- **每轮设上限**：最大候选数 / 最大接受数 / 最大重试数；被 Absorb 的规则必须过「反例检查 + 旧能力回归」（BORROWABLE §5.4）。
- **人在环**：E-flow 不是全自动——是「人工开专门 evolution session」，六维裁决结论回 human gate。

### 6.3 时间感（诚实）

按 §5 循环，一轮 = 跑一篇 + 审改 + 重跑。攒够 3-4 篇 case + 修 A1 + 稳 verifier + 建 anytime-valid + baseline，**乐观也要好几轮人工循环**。所以：

> **E-flow 是 V5/V6 甚至更后的事，不是 V4。** V4 的任务是把第一次真复现的经验消化进设计，让人工预训练循环转起来。**现在（V4 起点）连第一篇 Mie 都没跑通——离 E-flow 还很远。**

---

## 7. 一页纸行动清单（跑通前 vs 跑通后）

```
【跑 Mie 前（可选 + 必核）】
  □ (可选) D1 sub-leaf 硬化 + 同步改 spawn 模板改用 leaf 身份    ← 第一次 fan-out 安全带
  □ (可选) D2 skills 预加载 + 留 skill-print.py 兜底
  □ (必核) 开跑前 5 分钟核 Mie 一阶段是否需 pdf/magnus 空骨架 skill（§3.3）
  □ (若放弃 OpenCode) D5 CLAUDE.md/AGENTS.md 三文件同步红线必须现在改

【跑 Mie（W-flow，A1 不挡）】
  □ 在 SEPR 跑 Akimov 2401.04146 第一阶段
  □ 全程对照 §2 信号盘记录「什么真的断了」（五类逐类填，没断写"未触发"）
  □ 三态分开报，fallback/diagnostic 直说不当物理成功

【跑通后（按信号 + 走 §5 循环）】
  □ 把 WORK_LOG + 复现报告 + "什么断了"清单发回 optics_agent
  □ optics_agent CC 人工审：信号 → §3/§4 触发条目
  □ 用户裁决盲批/review → SEPR 落地 human gate → 重跑验证
  □ 按信号选做 L2（报告 schema / hooks / 机理维+V&V / held-out / 记忆治理）

【攒够 case 后（V4 远景 / V5+）】
  □ L3（anytime-valid / utility_score / baseline ABCD / 执行真实性）
  □ 修 A1 + 满足 §6.1 六前置 → 才考虑真开 E-flow
```

---

**本文档结束。** 定位：SEPR V4 前瞻路线图（跑通后再定，非承诺）；性质为规划而非落地；下一步由用户在 SEPR 跑通 Mie 第一阶段后，按 §5 人工预训练循环 + §2 信号盘驱动 §3/§4 的改进，全程走 human gate。**核心判据：只有第一次真复现暴露的问题才值得投入治理——先跑通，再加护栏。**
