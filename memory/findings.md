# findings — optics_agent 已验证结论

> 两档分级：## 已验证重要（高杠杆设计决策 / 架构红线） / ## 已验证一般（工程实践 / 已验证可用机制）。
> 每条引 memento id 或 worklog 锚定位。L1.5 首次整理，2026-07-26。

## 已验证重要

- finding-verified-important-1: **result_class 7 级枚举防 overclaim** — not_run→physical_reproduction_success 七级，禁把 surrogate_fallback/diagnostic_only/pipeline_completed 当物理复现成功。Akimov Fig3 Gate1-4 全程锁定 partial_physical_match，CLAUDE.md 红线封顶验证有效。
  - see memento:19467fda（首跑六条信号修复）
  - 见 WORK_LOG.md#5.10

- finding-verified-important-2: **spawn 模版拼接机制** — 全局模版（身份+记忆+纪律）+ 局部模版（步级任务/输入/输出）+ 主 agent 理解三层拼接，已在 SEPR 4 身份 .claude/skills/ 详细版（6465 行）落地。
  - 见 WORK_LOG.md#5.4

- finding-verified-important-3: **三级治理 + 六维裁决** — Save/Improve/Absorb/Fork/Archive/Drop 六维，case count × 决策级别二维定 Tier-1/2/3。已在 evolution-agent skill 落地。
  - 见 WORK_LOG.md#5.6

- finding-verified-important-4: **失败防护五重** — 节点级 5 轮 + 新证据 + retry fingerprint + case 级 4h/20spawn/30search + evolution 级 15capsule/8skill，失败不是终止。
  - 见 WORK_LOG.md#5.9

- finding-verified-important-5: **3 层物理 verifier** — Layer 1 物理硬约束 / Layer 2 极限退化 / Layer 3 论文图定量，Akimov Fig3 Gate2-4 验证。Layer 1 每条带适用条件/容差/失败解释/不适用。
  - 见 WORK_LOG.md#5.16

- finding-verified-important-6: **codex 委托双通道** — 架构委托走 bash codex exec（never + workspace-write 兜底），一次性问答走 codex-cli MCP（untrusted）。SEPR 11 步分 A/B/C 三档。实测 6 项全绿（见记忆 c9ebdf3d）。
  - see memento:74c52808
  - 见 notes/codex_exec_delegation_plan-CN.md

- finding-verified-important-7: **启动机制洞** — agent frontmatter model 只在 --agent 启动时生效，/skill 斜杠命令不切 model。已写入 4 处：SEPR CLAUDE.md、optics-lead agent.md、SKILL.md、OA README.md。
  - see pitfalls_log:5dacf95a
  - 见 WORK_LOG.md#阶段十三

- finding-verified-important-8: **MCP 预检第 0 步** — 开工先验 memento 可调用，不可用显式声明降级+文件兜底，禁静默假装。2026-07-04 修复批次写入 SEPR + OA CLAUDE.md。
  - see memento:19467fda
  - 见 WORK_LOG.md#阶段十二

## 已验证一般

- finding-verified-general-1: **subsubagent 叶子不 spawn** — 第 3 层叶子省略 Agent 工具，框架层硬约束不递归。Claude Code leaf/sub-leaf + OpenCode leaf 均已落地。
  - 见 WORK_LOG.md#5.5

- finding-verified-general-2: **E-flow 不调 W-flow** — selective replay 层 A/B/C，层 C 人工重跑，evolution 不修改复现 workflow。
  - 见 WORK_LOG.md#5.7

- finding-verified-general-3: **hardlink 维护** — 编辑工具在 Windows 会破坏 hardlink。每次改 AGENTS.md 后验 hash，断裂用 Remove-Item CLAUDE.md; New-Item -ItemType HardLink -Path CLAUDE.md -Target AGENTS.md 重建。
  - 见 WORK_LOG.md#10（教训）

- finding-verified-general-4: **main-agent 偏离流程须先问 human gate** — 跳过校验层必须停下请示，不得自主决定。human_intervention 写入 main-agent SKILL.md + .human 双写。
  - see memento:4a094a7a
  - 见 WORK_LOG.md#阶段十四

- finding-verified-general-5: **人工预训练循环** — OA 设计 SEPR → SEPR 执行复现 → 经验反馈给 OA → OA 改进设计 → 重跑验证，核心工作流非 E-flow 自动。
  - 见 WORK_LOG.md#0

- finding-verified-general-6: **2 条 user-preference 行为修正已验证生效** — optics-lead 身份修正（运营优先于设计 + 授权边界），实证表明已无自发扎 V4/自作主张开工问题。
  - 见 WORK_LOG.md#阶段十三

- finding-verified-general-7: **两工作区分工** — OA=设计 SEPR 的元工作区 + 自身 COMSOL/Magnus；SEPR=agent 复现论文执行工作区。AGENTS.md/CLAUDE.md 均有定义。
  - 见 WORK_LOG.md#0 + AGENTS.md#SEPR-Sister-Workspace
