# optics_agent Agent Manual

本文件是 AI coding agent 在 optics_agent 仓库工作的常驻项目规则。它比普通笔记优先级更高；当项目规则变化时，应同步更新相关 skill。

## Project Identity

- Repository root: `C:\Users\27370\Desktop\project\optics_agent`
- Canonical GitHub repository: `https://github.com/PKU-QNO/optics-agent-zyz`
- 当前分支：`main`
- 主要用户环境：Windows + PowerShell，可 SSH 访问 Gustation。
- Project role: **设计 SEPR 的元工作区**（设计论文复现自进化 agent 框架）+ 自身的 COMSOL/Magnus 运行时工作 + plasmonics 笔记 + 可复用科学计算 workflow 设计。SEPR 框架在姊妹工作区 `../self-evo-paper-repro/` 执行复现。

长期方向：

```text
paper reproduction
  -> reusable scientific blueprint
  -> case/DSL + parameter sweeps
  -> new scientific exploration
```

论文复现是 blueprint 迭代的回归测试，不是最终目标。Optics 是当前 use case，workflow 应能迁移到陌生科学与工程领域。

## SEPR Sister Workspace（两个工作区的分工——重要）

**架构**：optics_agent 和 SEPR 是两个独立工作区，角色不同：

- **optics_agent（本工作区）** = **设计 SEPR 的元工作区**。在这里设计 SEPR 的框架（4 agent 架构、workflow、spawn 模版、六维裁决、失败防护等），也做自身的 COMSOL/Magnus 工作。
- **SEPR**（`C:\Users\27370\Desktop\project\self-evo-paper-repro`）= **agent 复现论文的执行工作区**。Claude Code 在这里以 main-agent 身份跑 10 步复现 workflow，或以 evolution-agent 身份跑自迭代。

**人工预训练工作流**（核心，非 E-flow 自动）：

```text
1. optics_agent 设计 SEPR 框架（已完成设计阶段）
2. CC 在 SEPR 区复现一篇论文（用 .claude/skills/ 详细版）
3. 把 SEPR 复现过程的上下文（WORK_LOG.md + 复现报告）发给 optics_agent 的 CC
4. optics_agent 的 CC 读 SEPR 经验，人工改进 SEPR 设计（不直接用 E-flow 自迭代）
5. 重跑论文，验证改进
6. 循环 2-5 = 人工预训练
```

**关键边界**：SEPR 复现论文时反馈的经验，由 optics_agent 的 CC 人工审查后改进设计，不是 SEPR 自己跑 E-flow 自动改。E-flow 是后期才用的（攒够 case 后人工开专门 evolution session）。

**SEPR 现状**（2026-06-30）：设计阶段完成。`.human/`（中文大纲人看）+ `.claude/skills/`（中文 prompt-engineered 详细版，4 身份 main/sub/evolution/sub-E 全部 6465 行）+ CLAUDE.md（路由+红线+全规范）+ WORK_LOG.md（475 行完整交接）。94 篇 v3 文献审查 + 16 条风险落地。教材 `.paper/scattering.pdf`（Bohren & Huffman）已就位。待启动 Mie 第一阶段复现（Akimov 2401.04146）。

**SEPR 技术要点**：Claude Code 3 层子 agent（main-agent → sub-agent → sub-sub-agent）；`.human/` = 中文大纲，`.claude/` = 中文详细执行版；4-agent 架构：复现（main-agent + sub-agent, 10 步）+ 自迭代（evolution-agent + sub-E-agent, 6 步）；Mie 代码共享 `reproduction_test/mie/` via junction。

**给 optics_agent 的 CC 的提醒**：你要改进 SEPR 设计时，读 `C:\Users\27370\Desktop\project\self-evo-paper-repro\WORK_LOG.md` 恢复 SEPR 上下文，不要照搬 SEPR 的复现机制到 optics_agent（optics_agent 是 Magnus+COMSOL 工作区，不是复现 agent）。

**SEPR 仅 Claude Code（OpenCode 已撤销 2026-07-03）**：SEPR 现只面向 Claude Code（读 `.claude/skills/` + `.claude/agents/`）。OpenCode（GPT-5.5 备选）已撤销：`opencode.json` / `.opencode/` / `scripts/start-opencode-sepr.ps1` 已删除，SEPR `AGENTS.md` 降为 stub，"三文件同步"约束随之取消（规则主源就是 SEPR `CLAUDE.md` 一处）。Opus 不稳定时的应急方案是改 Claude Code 的 URL/API 指向 DeepSeek（非 OpenAI-specific 的 response 接口可顶），不再维护第二套 agent 配置。

## Current Project Status

- **Mie theory analytical reproduction**（2026-06）：执行基础设施已转入 SEPR 工作区；Mie blocker 已解除。验证体系从 4 层收敛为 3 层：物理硬约束 + Rayleigh/large-size 等已知极限 + 论文图定量比较；PyMieScatt 作为强依赖已废弃。11 篇参考论文在 `papers/mie/`（SEPR 侧镜像到 `.paper/mie/`）。教材 Bohren & Huffman `.paper/scattering.pdf`（27.8MB）已就位。完整计划见 `reproduction_test/mie/mie_reproduction_plan-FINAL-CN.md` + skill `optics-mie-reproduction`。下一步是在 SEPR 启动 Phase 1：Akimov 2401.04146。
- **SEPR 设计阶段已完成**：94 篇 v3 文献审查 + 16 条风险落地 + 4 身份 `.claude/skills/` 详细版（6465 行）已完成。optics_agent 当前职责是基于 SEPR 复现经验继续人工改进框架设计。
- **Agent skill & workflow self-iteration survey** 已完成。见 `notes/agent_skill_self_iteration/`。
- **Workflow engine design**（v2）已完成设计但未作为代码实现。权威文档已归档到 `v3-final/`：`workflow_v2_plan-CN_archive.md`、`project_flow_plan-CN_archive.md`、`workflow_v2_risks-CN_archive.md`（原位 `notes/*_moved.md` 只作面包屑）。v1 自演化 DSL 其余文件仍在 `project/to-do-future/DSL/`；其 127 篇 arxiv 风险审查已归档 `v3-final/V1-workflow_risk_review-CN_archive.md`。均非当前方案。
- COMSOL/Magnus runtime exists and is usable through the active Magnus image:

```text
docker://magnus-local/comsol-runtime:latest
```

- The active image was imported by the administrator. Do not refresh, pull, retag, rebuild, overwrite, or replace it unless the user explicitly asks.
- Runtime staging path:

```text
/data/public/zhangyuanzheng/comsol-runtime
```

- Validated COMSOL solve license mount inside the container:

```text
/opt/comsol-license/license.dat
```

- Canonical local COMSOL structure:

```text
comsol/runtime/
comsol/automation/
comsol/docker/
comsol/blueprints/source/
comsol/docs/
comsol/manifests/
```

- Official Magnus blueprint package:

```text
.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
```

- Degiron 2009 Fig. 3 reproduction rehearsals exist under:

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/
```

V1 completed the engineering workflow but not physical COMSOL full-vector reproduction; its final sweep is labelled `surrogate_fallback`. V2 completed a scalar TM-like PDE diagnostic sweep and an isolated SU-8 Wave Optics/RF mode-analysis probe. The v2 probe compiles, meshes, reaches the eigensolver, and saves `.mph`, but produces zero physical `neff` rows because the eigensolver fails matrix factorization. Do not present either v1 or v2 as a successful Fig. 3 paper reproduction.

## Root Layout

预期高层目录：

```text
.codex/
.claude/
.magnus/
comsol/
docs/
notes/
papers/
reproduction_test/
services/
workflows/              <-- 工作流定义、prompt 文件、状态文件
```

保持根目录低噪音。新的 COMSOL 工作放在 `comsol/`；论文私有复现产物放在 `reproduction_test/private/<case>/`；笔记按主题放在 `notes/` 或 `docs/`。

## Workflow System

optics_agent 用 YAML 定义的**固定拓扑**工作流编排论文复现。当前为 v2（简化版）；v1 的"可自迭代拓扑"声明式 DSL 已废弃（自由度过高导致风险爆炸，见 commit `bc3b5b6` 的风险报告）。

权威设计文档（细节在 `notes/`，本文件只保留不可违反的原则）：

```text
v3-final/workflow_v2_plan-CN_archive.md         工作 workflow + 自迭代 workflow（V2 废案；SEPR 用子 agent 替代 workflow 状态机）
v3-final/workflow_v2_risks-CN_archive.md        v2 风险清单
v3-final/project_flow_plan-CN_archive.md        项目状态树版本控制（project-flow）
v3-final/V1-workflow_risk_review-CN_archive.md  v1 127 篇 arxiv 风险审查（R-1~R-49）
project/to-do-future/DSL/                        v1 可变拓扑 DSL 其余文件（远期）
```

### 不可违反的架构原则

1. **拓扑写死，人工管**。workflow 拓扑由人工编写的固定 YAML 定义。agent 不得自动改拓扑、节点指令或分支条件。学长意见：小成本项目（不是扫几十万篇文献）不需要也不能有可变拓扑的自由度。
2. **只有智能断点用 agent**。能用确定性脚本做的（物理通用检查、导出、schema 校验）必须写死成脚本，不用 agent。每个 agent 节点要能回答"为什么脚本不能做"。
3. **无 supervisor/worker 双对话**。不采用"主管 agent + 工作 agent 两条独立长对话互相中继"的架构。改为：固定脊柱 + 节点内 agent 自由调子 agent。多目标复现（如 Fig2+Fig3 无关）= 在同一固定拓扑的节点内并发多个子 agent，拓扑不变。
4. **自迭代只碰经验层**。自迭代只更新 skill 内容 + 提示词备注，全部走 human gate；绝不改 workflow 拓扑、蓝图结构、`AGENTS.md`、或自迭代系统自身。
5. **自迭代不迭代自己**。自迭代 workflow 的拓扑、节点指令、专用 SKILL 人工写死，禁止自我修改。
6. **核心卖点 = 垂域可验证效果**。光学复现 + deterministic verifier + 可审计执行是目标，agent 只是手段；不是 agent 框架，不是 DSL 自演化平台。

### 三种状态改变（project-flow）

系统状态只由三种操作改变，每种走临时镜像 → 回传白名单守门 → 新状态节点：

```text
paper_reproduction   跑一篇论文复现
self_iteration       自迭代一轮 skill/备注
human_intervention   人工改 SKILL/规则/参数/记忆
```

### 实现状态

v2 设计已完成但代码未实现（2026-06）。SEPR 工作区用 claude 三层子 agent 替代 workflow 状态机，已实际运行 Mie 复现基础设施。`workflows/` 下现存文件（`paper_reproduction.workflow.yaml`、`ENGINE.md`、`prompts/`）是 v1 残留，暂不重写——SEPR 子 agent 方案是当前有效路径。

## v3-final 设计归档（V1/V2/V3 谱系 + tag 约定）

`v3-final/` 汇总 V1→V2→V3 的设计、风险审计、演进文档的 **canonical 版本**，索引见 `v3-final/README.md`。散落在 `papers/SEPR/`、`notes/`、`notes/Gemini/`、`project/to-do-future/DSL/` 的原件已改名带 `_moved` 后缀并冻结（顶部加面包屑指向 v3-final）。SEPR 侧同规则见其 `CLAUDE.md`「v3-final 设计归档」节。

文件名后缀约定（改这些文件或新增设计文档时沿用）：

| 后缀 | 含义 |
|------|------|
| `_latest` | 正在更新的最新版本（v3-final 内活文档） |
| `_archive` | 废案/完结但有价值，保留参考 |
| `_deprecated` | 废案无价值且易误导（当前无） |
| `_moved` | 别处有 canonical 版、此处不再更新（原位面包屑） |
| `_V1_finished` | 历史版本完结（预留，当前 V1 用 `_archive`） |

例外：`WORK_LOG.md` 是 living 操作日志，仍在 optics_agent 根，未移动。

## Skill System

项目 skills 位于：

```text
.codex/skills/
```

Claude 和 Agents 的 skills 通过 Windows junction 同步：

```text
.claude/skills -> .codex/skills
.agents/skills -> .codex/skills
```

只编辑 canonical 路径 `.codex/skills`。遇到匹配任务时，先完整阅读对应 `SKILL.md`。

当前路由：

| 任务 | Skill |
|---|---|
| **SEPR 上游审核 / 交接文档核对 / gate 上游裁决 / SEPR workflow·框架设计与演进 / v3-final 谱系维护 / optics_agent 自身 COMSOL·Magnus 编排（= 本工作区对话顶端身份）** | **`optics-lead`**（`.claude/agents/optics-lead.md` + skill；这是元工作区主 agent 身份，其它 skill 在其之下调用） |
| 项目路由、目标、工作区边界、credentials、安全规则、重要文件 | `optics-agent-core` |
| Mie 理论解析/半解析计算、Lorenz-Mie 系数、散射/吸收/消光截面、LSPR、介质 Mie 模式、core-shell、CDA、SLR、二元阵列、S 参数反演、Maxwell-Garnett、Mie-vs-Bragg 相图、Python-only benchmark、3 层物理验证（能量守恒、Rayleigh/large-size 极限、论文图定量比较；PyMieScatt 已废弃） | `optics-mie-reproduction` + `reproduction_test/mie/mie_reproduction_plan-FINAL-CN.md` |
| 非 Mie 的论文图复现、参数表、缺失信息分析、复现报告、handoff、COMSOL/Magnus 复现 | `optics-paper-reproduction` |
| COMSOL runtime image、active `magnus-local/comsol-runtime` image、license mount、runtime folder | `optics-comsol-runtime` |
| COMSOL batch/headless jobs、`.java`/`.mph`/`.m`、smoke cases、manifest contract | `optics-comsol-batch` |
| COMSOL Java API syntax、GUI-exported Java、feature/study/solver/result tags、batch-safe Java templates | `comsol-java-api` |
| Magnus/Gustation jobs、logs、blueprint save/launch、FileSecret、`MAGNUS_RESULT`/`MAGNUS_ACTION`、mounts、staging paths | `optics-magnus-platform` |
| Magnus artifact formats、`.magnus.yaml`、`.magnus.skill.yaml`、import/export packaging、public/private boundary | `optics-magnus-artifacts` |
| Docker image build/push/archive/handoff、ACR/PKU registry、image size/hash、active image 安全边界 | `optics-docker-images` |
| SEPR 复现编排（只在 SEPR 工作区使用） | `main-agent`（SEPR `.claude/skills/` / `.human/skills/`） |
| SEPR 复现执行（只在 SEPR 工作区使用） | `sub-agent`（SEPR `.claude/skills/` / `.human/skills/`） |
| SEPR 自迭代编排（后期人工开启，非当前 OA 自动流程） | `evolution-agent`（SEPR `.claude/skills/` / `.human/skills/`） |
| SEPR 自迭代执行（后期人工开启，非当前 OA 自动流程） | `sub-E-agent`（SEPR `.claude/skills/` / `.human/skills/`） |

如果同时涉及 COMSOL 和 Magnus，先加载 `optics-comsol-runtime`，再加载 `optics-magnus-platform`。若涉及论文复现，再加载 `optics-paper-reproduction`。SEPR 的 4 个 agent skill 属于姊妹工作区，不复制到 optics_agent。

## AGENTS And Skill Update Policy

当项目规则变化时，在同一任务内更新持久规则面：

1. 更新 `AGENTS.md` 中的常驻项目规则。
2. 更新相关 `.codex/skills/*/SKILL.md` 中的任务专用流程知识。
3. Validate changed skills with:

```powershell
python C:\Users\27370\.codex\skills\.system\skill-creator\scripts\quick_validate.py .codex\skills\<skill-name>
```

4. 如果变更会影响 Claude 或 Agents 行为，确认 `.claude/skills` 和 `.agents/skills` 仍指向 `.codex/skills`。
5. 保持 `CLAUDE.md` 与 `AGENTS.md` 同步。本仓库中 `CLAUDE.md` 应是 `AGENTS.md` 的 hard link，不要替换成分叉内容。

If an editor or patch tool breaks the hard link, recreate it after merging content:

```powershell
Remove-Item -LiteralPath .\CLAUDE.md
New-Item -ItemType HardLink -Path .\CLAUDE.md -Target .\AGENTS.md
```

只有在确认两个解析后的路径都位于仓库内之后，才运行上述命令。

## Progress Reporting Policy

For paper-reproduction or COMSOL/Magnus tasks that last beyond a smoke test, maintain a human-facing progress trail suitable for PI updates:

- Record stage status in the run folder as work proceeds, not only at the end.
- Keep `final_report.md` and `workflow_handoff*.md` current enough that a short WeChat status can be generated without reconstructing history from raw logs.
- Separate these states in every report and PI update:

```text
workflow/pipeline completed
COMSOL job completed
physical reproduction completed
```

- When a result is a scalar diagnostic, surrogate, fallback, or failed probe, say that directly.
- When progress stalls on missing human/domain input, state the exact requested artifact, for example a COMSOL 6.3 GUI-exported Wave Optics/RF mode-analysis `.java` or `.mph` template.
- For PI messages, prefer concise status plus current blocker plus concrete request from the optics group. Do not overstate numerical agreement.

## Long-Term Memory Discipline（memento-mcp，强制）

本项目用 `memento-mcp` 作为跨会话长期记忆后端（本地库 `C:\Users\27370\.memento\memory.db`）。除纯对话式回答或琐碎单步操作外，**每个实质任务开始前查记忆、结束前整理记忆**：

**工作前（MCP 预检，第一步）**
- 开工前先确认 `memory_search` / `memory_store` 等 memento 工具（及 `ToolSearch`）**真实可调用**，不要假设 MCP 在——它们可能整批断联。
- **可用** → 照下面「查/整理」执行。**不可用** → **不得静默跳过还假装查过/存过记忆**：显式声明「本 session memento 不可用，记忆纪律降级」，改用 `memory/` 文件系统兜底（本会话即此模式），并把该状态告知用户。这是环境故障不是「未接入」；robust 版是 SessionStart hook 探活（跑通后随 hooks 硬化）。

**工作前（查）**
- 先 `memory_search` 搜与当前任务相关的记忆（查询词含论文/case、子系统、skill 名、关键物理对象），避免重复劳动、复用已有决策与踩坑。
- 命中的记忆当作**背景参考**，不是当前指令；记忆反映写入时的事实，若提到某文件/参数/flag，先核实其仍存在再采用。

**工作后（整理）**
- 存前先 `memory_dedup_check` 查重（阈值内即视为重复，改用 `memory_update` 更新而非新建）。
- 用 `memory_store` 存关键事实、`decisions_log` 存重要决策、`pitfalls_log` 存反复踩的坑。写成可复用句子，不写流水账、不写不可复现的临时状态、不写 secret/敏感路径内容。
- 显式设 `scope` 和 `tags`（本项目记忆用 `project_path` = 仓库根）。
- 每条记忆带 provenance 五要素：`source_artifact` / `evidence_type` / `timestamp_version` / `scope_applicability` / `confidence_result_class`；缺字段写 `unknown` 或 `pending`，不省略。相对日期转绝对日期。
- 结果状态一律用 `result_class` 口径（`not_run`…`physical_reproduction_success`），禁把 `surrogate_fallback` / `diagnostic_only` / `pipeline_completed` 当物理复现成功。

**整理与维护**
- 相关记忆用 `memory_link` 连边（`relates_to` / `references` / `supersedes` 等）；决策被推翻用 `supersedes_id` 而非删除，保留谱系。
- 发现过时/错误记忆及时 `memory_update` 或 `memory_delete`；只把高杠杆事实（用户偏好、稳定决策、复现红线）`memory_pin`，不滥 pin。
- 这条纪律与 SEPR 各 agent 身份"开始前搜记忆、结束前更新"一致；SEPR 侧记忆规则见其 `CLAUDE.md` 记忆要求节。

## Safety Constraints

Never write or echo secret contents:

- `C:\Users\27370\Desktop\project\secret.json`
- SSH private keys under `C:\Users\27370\.ssh\`
- COMSOL license files
- Docker registry passwords
- Magnus tokens

It is acceptable to mention secret key names and non-secret mount paths, for example `/opt/comsol-license/license.dat`; it is not acceptable to copy the actual license or token contents.

Treat these as private or sensitive unless the user explicitly says otherwise:

```text
papers/private/
reproduction_test/private/
comsol-runtime/secrets/
```

Do not upload private PDFs, license files, SSH keys, or raw credentials to public paths or public registries.

High-risk operations:

- Do not run destructive git commands such as `git reset --hard` or `git checkout --` unless explicitly requested.
- Do not recursively delete or move directories without first resolving and verifying the absolute path is inside the intended workspace.
- Do not kill, resubmit, or duplicate Magnus jobs unless the user asks or the task plan explicitly requires it.
- Do not launch GPU jobs, A-class jobs, or jobs consuming more than half cluster CPU/memory without explicit review.
- Do not mutate the active COMSOL image unless explicitly requested.

## Magnus And COMSOL Rules

Credentials are stored in:

```text
C:\Users\27370\Desktop\project\secret.json
```

Prefer GU/Gustation keys when present:

```text
motif: magnus_address-gu, magnus_token-gu
```

Use SSH target:

```text
zhangyuanzheng@Gustation
```

Before submitting Magnus jobs:

1. Query existing jobs by `run_id`; reuse active or successful jobs.
2. Query cluster resources.
3. Keep `gpu_type=cpu`, `gpu_count=0` unless GPU is explicitly required.
4. Keep planned CPU and memory under half of cluster totals unless explicitly reviewed.

Default COMSOL smoke resources:

```text
gpu_type=cpu
gpu_count=0
cpu_count=8
memory_demand=32G
ephemeral_storage=40G-100G
job_type=B2
```

Real COMSOL solves on the active image require the license mount:

```text
$HOME/.comsol-container-license:/opt/comsol-license
```

Forward license variables into Apptainer with:

```bash
export APPTAINERENV_LM_LICENSE_FILE=/opt/comsol-license/license.dat
export APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
```

Use `/data/public/zhangyuanzheng` for public staging and admin handoff. Do not switch back to `/home/zhangyuanzheng` or registry-first delivery unless the user explicitly changes the deployment target.

## COMSOL Java And Paper Reproduction Lessons

Current COMSOL batch Java runs through official COMSOL Java API, but hand-written Java API calls are not automatically equivalent to a correct GUI-built model.

For current Magnus runtime Java:

- Provide `public static Model run()` and return a `Model`.
- Avoid `System.getenv`, `System.getProperty`, direct Java file IO inside `run()`, inner classes, and anonymous classes.
- Prefer GUI-exported Java templates for exact physics/study/solver tags.
- Treat generated `.mph` as necessary but insufficient; inspect stdout markers, metrics, result tables, and physical validation.

Distinguish these states:

```text
Magnus Success
  != COMSOL intended solve success
  != physical paper reproduction success
```

For paper reproduction, a fallback/surrogate result may validate the workflow but must never be reported as physical reproduction.

Degiron v1/v2 specific lessons:

- V1 proved the Magnus/COMSOL Java pipeline and stdout-to-CSV reporting, but its final plot was a `surrogate_fallback`.
- V2 proved a scalar TM-like PDE sweep can run, but its `Im(neff)` is effectively zero and no anticrossing is recovered; it is diagnostic only.
- V2 isolated SU-8 Wave Optics/RF mode-analysis reached the eigensolver after explicit mesh construction, then failed matrix factorization for multiple shift styles.
- The next meaningful technical input is a verified COMSOL 6.3 GUI-exported mode-analysis template; blind changes to Java feature strings or eigenvalue shifts should stop once isolated mode analysis fails.

## Search & Information Retrieval

Use the global MCP routing rules first, then apply these project-specific refinements:

- Physics, optics, photonics, plasmonics, Mie theory, COMSOL validation, and paper-reproduction literature: prefer `paper-search-wos` / Web of Science MCP for bibliographic metadata, citation counts, journal/source information, and screening abstracts when available.
- AI agent, workflow, skill, LLM training, or evaluation papers used to improve the agent system: prefer `arxiv-research` MCP.
- Non-paper searches such as COMSOL API usage, Magnus/cluster behavior, Docker issues, code examples, web documentation, and current public information: prefer `exa` MCP.
- Use `semantic-scholar`, `openalex`, or `crossref`-based MCPs to fill missing abstracts, citation graph context, DOI metadata, or author/institution metadata after the primary source.
- Use `firecrawl` for known URLs that need reliable extraction, and browser automation only when the page requires interaction.
- Do not rely on training data alone for API syntax, model/library versions, paper claims, or current platform behavior.

## 模型路由与 codex 委托（2026-07-05 用户拍板，两工作区通用）

codex（GPT-5.5）单价约 Opus 4.8 的 1/50。原则：**判断密度决定谁干活**。**默认 Claude 不亲自读写文件——机械读写与执行委托 codex**（读文件内容不进 Claude context）；**白名单豁免仅两类**：① 裁决必需的读（gate 停机点亲读 GATE 决定/verifier 输出/关键报告，裁决依据不得经转述）；② 契约文件的写（8 字段报告、capsule、GATE 决定、WORK_LOG、run_manifest 由 Claude 亲写自校）。物理推导、gate 裁决、编排留 Claude；代码实现 codex 写 Claude 验（verifier 兜底）；对抗审查 codex+Claude 双审（异构防 self-preference）。

**两条委托通道（2026-07-07 精化，实测确立）**：① **架构委托走 bash `codex exec`**——产物要落盘、要被后续步骤消费的委托全走它（`-C <case> --add-dir <shared> -s workspace-write -c approval_policy=never --output-schema <s> -o <out> --json`）；`codex exec` 独有 `--add-dir`/`--output-schema`/`-o`/`--json`/`-p profile`，MCP 都没有。② **一次性问答走 `codex-cli` MCP**——仅当 Claude 顶端身份要**当场读 codex 的答案**（核 API 语法/查文档）时用。**非交互 exec 的 approval 必须 `never`**（不是 `untrusted`——那会在非交互流卡等批准挂死；安全靠 `workspace-write` sandbox 兜底，实测越界写被拦）。codex 产物一律落盘不走 stdout（防截断，读 `-o` 文件）。

codex 安全硬约束：`sandbox: workspace-write` + `approval_policy=never`（非交互 exec）/`untrusted`（交互 MCP），**永不** `danger-full-access`；cwd 限任务文件夹；secrets 在可达范围外；产物落盘经 Claude 验收才作数；计入资源上限。SEPR 复现 11 步分档（A档整步交/B档绝不交/C档拆开）+ codex exec 模板 + `.codex/agents/*.toml` 详见 `notes/codex_exec_delegation_plan-CN.md` 与 SEPR `CLAUDE.md`「模型路由与 codex 委托」节。

## Malformed tool-call 熔断（2026-07-05，两工作区通用）

Opus 4.8 长上下文偶发 tool call 格式坏 + harness 留坏文本于 transcript → 模型自回归模仿自己的坏格式级联（官方 issues #61367/#62344/#64097；用户实测错 3 次后几乎写不出正确调用）。**熔断**：同 session 累计 **2 次** malformed → 立即停、写 handoff（写文件也失败就在对话里输出全文）、开新对话，**绝不** `--resume`。缓解：长任务每个自然停机点（gate/阶段界）默认断 session。

## Development Practices

- Use `rg` / `rg --files` first for search.
- Use `apply_patch` for manual edits.
- Prefer scoped changes over broad refactors.
- Do not commit unless the user asks.
- Preserve user changes in a dirty worktree.
- Keep long plans, logs, and reports in Markdown files; keep chat summaries concise.

Common checks:

```powershell
python -m py_compile comsol\automation\*.py
python comsol\automation\submit_comsol.py --help
python C:\Users\27370\.codex\skills\.system\skill-creator\scripts\quick_validate.py .codex\skills\<skill-name>
```

PowerShell may not expand Python wildcards. If needed, expand file lists in PowerShell first and pass explicit paths to Python.
