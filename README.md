# optics_agent

> 注意：这个仓库目前是 zyz 的个人工作目录，不是课题组统一维护的最终版项目仓库。  
> 这里保留了大量探索性脚本、复现实验记录、失败日志和本地工作流约定。后续如果整理成正式小组仓库，需要再做目录清理、权限检查和文档收敛。

## 项目目标与当前状态

`optics_agent` 的目标是探索一个面向光学论文复现的 agent 工作流：

```text
论文读取 -> 参数提取 -> 数值建模 -> COMSOL/Magnus 运行 -> 结果验证 -> 失败修正 -> 技术报告
```

短期用例是 SPP / LR-SPP 等光学论文图像复现；长期目标不是只复刻一张图，而是把论文复现过程沉淀为可复用的 scientific-computing blueprint、参数 sweep、case/DSL 和自迭代验证流程。

当前状态概括：

- COMSOL/Magnus headless 运行链路基本打通：Java 模型可以编译、batch 运行、保存 `.mph`，并通过 stdout/postprocess 生成 CSV 和图。
- Degiron 2009 NJP Fig. 3 已完成 v1/v2 两轮复现 rehearsal，但物理复现还没有成功。
- 当前主要 blocker 不是 Magnus 封装，也不是 COMSOL license/image，而是缺少 COMSOL 6.3 Wave Optics/RF mode-analysis 的准确 GUI 导出模板。
- 后续最需要的输入是：光学组同学在 COMSOL GUI 中搭一个最小可运行的 mode-analysis 模型，并导出 `.java` 或提供 `.mph`，用于固定 physics/study/solver/result 设置。

## 公开仓库注意事项

这个目录里有一些本地私有工作流路径。整理公开 GitHub 仓库时请注意：

- 不要上传 COMSOL license、Magnus token、SSH key、Docker registry 密码等凭据。
- `papers/private/` 和 `reproduction_test/private/` 可能包含私有论文、截图、原始日志或本地实验记录，公开前必须人工检查。
- `README.md` 可以说明这些目录的用途，但不要依赖私有文件作为公开仓库的必要输入。

## 顶层目录说明

| 路径 | 说明 |
|---|---|
| `AGENTS.md` | AI 编码智能体的项目规则手册。记录项目状态、安全约束、COMSOL/Magnus 约定和长期协作规则。 |
| `CLAUDE.md` | 与 `AGENTS.md` 同步的硬链接，供 Claude 类工具读取同一套项目规则。 |
| `.codex/skills/` | Codex 项目 skills。记录 COMSOL、Magnus、论文复现等可复用工作流知识。 |
| `.claude/skills/` | Claude 侧 skills，同步到 `.codex/skills/`。 |
| `.magnus/` | Magnus 平台相关导出文件，包括 blueprint/skill YAML。 |
| `comsol/` | COMSOL runtime、automation、blueprint、Docker、probe、报告和运行计划。 |
| `docs/` | 项目文档、Magnus 部署说明、运行报告和规划文档。 |
| `notes/` | 光学/plasmonics 课程、论文和理论笔记。 |
| `papers/` | 本地论文存放区。`papers/private/` 不应直接公开。 |
| `reproduction_test/` | 论文复现实验记录，包含 v1/v2 的完整过程、脚本、日志、结果和报告。 |
| `services/` | 服务化或后续平台接口相关实验目录。 |
| `tools/` | 辅助工具脚本目录。 |

## 关键工作流：Degiron 2009 NJP Fig. 3

目前最完整的一条复现实验是 Degiron 2009 NJP Fig. 3：

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/      # v1
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/   # v2
```

目标图是论文 Fig. 3：扫描 BCB 总厚度 `t`，计算两个耦合 eigenmodes 的 `Re(neff)` 和 `Im(neff)`，并检查 `t ≈ 5.6 µm` 附近的 anticrossing / mode hybridization。

重要结论：

- v1 跑通了论文复现的工程流程，但最终图是 `surrogate_fallback`，不是物理 COMSOL 复现。
- v2 用更严格的 isolated-validation 方式重跑。标量 TM-like PDE sweep 能跑完，但 `Re(neff)` 偏低、`Im(neff)` 基本为 0，没有恢复 Fig. 3 的关键趋势。
- v2 的 isolated SU-8 Wave Optics/RF mode-analysis probe 能编译、显式网格能通过、能进入 eigensolver 并保存 `.mph`，但 eigensolver matrix factorization failed，仍无物理 `neff` 输出。
- 因此，当前不是“封装完全坏了”，而是缺少 COMSOL 6.3 GUI 导出的 mode-analysis 模板来固定模块专用设置。

## V1 文件说明

路径：

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
```

| 文件/目录 | 作用 | 是否重点技术报告 |
|---|---|---|
| `paper_notes.md` | 论文 Fig. 3 相关内容笔记：物理目标、图像上下文、关键参数来源。 | 是，论文理解报告 |
| `parameter_table.md` | 几何、材料、计算类型、输出量等参数表。 | 是，参数提取报告 |
| `assumptions_and_missing_info.md` | 论文缺失信息和复现假设：边界、mesh、solver、mode sorting 等。 | 是，缺失信息/假设报告 |
| `final_report.md` | v1 最终报告：做了什么、跑了哪些 job、哪些成功、哪里失败、为什么不是物理复现。 | 是，核心技术报告 |
| `workflow_handoff_A.md` | 面向 optics_agent 框架和光学组交接的通用方案。说明标准答案需要包含哪些技术细节。 | 是，核心交接报告 |
| `comsol/Degiron2009Fig3ModeSweep.java` | v1 COMSOL Java 模型。尝试 full-vector mode analysis，失败后输出 fallback。 | 代码 |
| `comsol/postprocess_degiron_fig3.py` | 从 COMSOL/Magnus stdout 中解析数据，生成 CSV 和图。 | 代码 |
| `comsol/run_config_smoke.json` | smoke job 的运行配置记录。 | 配置 |
| `comsol/run_config_sweep.json` | sweep job 的运行配置记录。 | 配置 |
| `magnus/submit_degiron_fig3.py` | v1 Magnus 提交脚本。 | 代码 |
| `magnus/submit_log.md` | v1 job 提交、复用、下载和 postprocess 记录。 | 是，运行记录报告 |
| `magnus/job_ids.md` | v1 job id 列表，便于追踪平台任务。 | 运行索引 |
| `magnus/failure_retry_record.md` | v1 失败重试记录：Java wrapper、sandbox、mesh、eigensolver 等问题。 | 是，失败诊断报告 |
| `magnus/raw_logs/` | 下载的原始 Magnus/COMSOL 日志。公开前需检查。 | 原始日志 |
| `results/neff_sweep.csv` | v1 输出数据。注意最终为 `surrogate_fallback`，不能作为物理结果。 | 数据 |
| `results/fig3_reproduction.png` | v1 输出图。注意不是物理 COMSOL 复现图。 | 图 |
| `results/postprocess_summary.json` | postprocess 的摘要指标。 | 数据摘要 |
| `results/mode_profiles/` | mode profile 预留目录，目前不是核心结果。 | 结果目录 |

`magnus/raw_logs/` 下面按 job id 分目录保存平台返回的原始产物。常见文件含义如下：

| raw log 文件类型 | 作用 |
|---|---|
| `command.json` | COMSOL batch 命令、输入输出路径和运行参数记录。 |
| `compile.json` | Java 编译阶段状态。 |
| `env_report.json` | 容器内环境、license 路径和运行上下文摘要。 |
| `case_path.txt` | 平台侧 case 工作目录路径。 |
| `manifest.json` | Magnus/COMSOL runner 生成的任务产物清单。 |
| `errors/failure.json` | 失败任务的结构化错误信息。 |
| `raw/stdout.txt` / `raw/stderr.txt` | COMSOL batch 标准输出和错误输出。 |
| `raw/comsol.log` | COMSOL 自身日志。 |
| `raw/compile.stdout.txt` / `raw/compile.stderr.txt` | Java 编译 stdout/stderr。 |
| `raw/*_raw_from_stdout.csv` | 从 stdout 中解析出的原始数值表。 |
| `raw/model_output*.mph` / `raw/model_output.mph.status` | COMSOL 保存的模型文件和保存状态。生成 `.mph` 只说明模型文件保存成功，不等于物理复现成功。 |
| `raw/*.java` / `raw/*.class` | 提交到平台的 Java 源文件和编译产物快照。 |

### V1 优先阅读顺序

```text
final_report.md
workflow_handoff_A.md
failure_retry_record.md
parameter_table.md
assumptions_and_missing_info.md
```

## V2 文件说明

路径：

```text
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/
```

| 文件/目录 | 作用 | 是否重点技术报告 |
|---|---|---|
| `README.md` | v2 目录内说明：当前状态、文件布局、job id。 | 是，v2 快速入口 |
| `v1_experience_audit.md` | v2 开始前对 v1 的经验审计：哪些是 workflow success，哪些不是 physical success。 | 是，v1 复盘报告 |
| `v2_reproduction_plan.md` | v2 执行计划：validation ladder、COMSOL 模型、Magnus 提交、停止条件。 | 是，v2 技术计划 |
| `todo.md` | v2 持久化执行清单，记录每一步状态、job id、输出和备注。 | 是，进度报告 |
| `paper_notes.md` | v2 重新阅读论文和 Fig. 3 后的笔记。 | 是，论文理解报告 |
| `parameter_table.md` | v2 使用的几何、材料、计算和验证目标表。 | 是，参数提取报告 |
| `assumptions_and_missing_info.md` | v2 假设、缺失信息和已验证 blocker。 | 是，缺失信息/假设报告 |
| `final_report.md` | v2 最终报告：scalar PDE、Wave Optics probe、job 状态、结果差异、下一步。 | 是，核心技术报告 |
| `workflow_handoff_A_v2.md` | v2 交接报告：光学组标准答案、agent 模块、GUI 模板需求。 | 是，核心交接报告 |
| `pi_wechat_update.md` | 面向 PI 的微信进度同步草稿。 | 沟通材料 |
| `pdf_pages/` | 从 PDF 渲染出的关键页面截图，用于图像/版面核对。公开前需检查。 | 论文辅助材料 |
| `comsol/Degiron2009Fig3V2ScalarPdeLadderSmoke.java` | v2 标量 TM-like PDE ladder smoke。 | 代码 |
| `comsol/Degiron2009Fig3V2ScalarPdeCoupledSweep.java` | v2 标量 TM-like PDE coupled sweep。能跑完，但不是物理复现。 | 代码 |
| `comsol/Degiron2009Fig3V2ModeAnalysisSu8Smoke.java` | v2 isolated SU-8 Wave Optics/RF mode-analysis probe。定位到 eigensolver blocker。 | 代码 |
| `comsol/postprocess_degiron_fig3_v2.py` | v2 stdout CSV 解析、结果 CSV/图/metrics 生成脚本。 | 代码 |
| `comsol/run_config_ladder_smoke.json` | ladder smoke 配置。 | 配置 |
| `comsol/run_config_coupled_sweep.json` | coupled scalar sweep 配置。 | 配置 |
| `comsol/run_config_mode_su8_smoke.json` | isolated SU-8 mode-analysis probe 配置。 | 配置 |
| `magnus/submit_degiron_fig3_v2.py` | v2 Magnus 提交脚本，包含 dedupe、资源检查、下载和 postprocess。 | 代码 |
| `magnus/submit_log.md` | v2 提交日志：staging、job id、状态、下载、postprocess 摘要。 | 是，运行记录报告 |
| `magnus/job_ids.md` | v2 job id 索引。 | 运行索引 |
| `magnus/failure_retry_record.md` | v2 失败重试记录：mesh tag、rtol、anonymous class、单位转换、mode-analysis mesh/eigensolver 等。 | 是，失败诊断报告 |
| `magnus/raw_logs/` | v2 原始 Magnus/COMSOL 日志。公开前需检查。 | 原始日志 |
| `results/ladder_smoke_neff.csv` | scalar ladder smoke 输出数据。 | 数据 |
| `results/ladder_smoke_neff.png` | scalar ladder smoke 输出图。 | 图 |
| `results/coupled_neff_sweep.csv` | scalar coupled sweep 输出数据。注意不是物理复现结果。 | 数据 |
| `results/fig3_reproduction_v2.png` | scalar coupled sweep 输出图。注意不是论文物理复现成功图。 | 图 |
| `results/degiron-2009-fig3-v2-mode-su8-smoke-v1_neff.csv` | mode-analysis smoke v1 输出，0 行，记录 mesh 阶段失败。 | 失败数据 |
| `results/degiron-2009-fig3-v2-mode-su8-smoke-v2_neff.csv` | mode-analysis smoke v2 输出，0 行，记录 eigensolver 失败。 | 失败数据 |
| `results/postprocess_summary.json` | v2 postprocess 摘要。 | 数据摘要 |
| `results/mode_profiles/` | mode profile 预留目录，目前不是核心结果。 | 结果目录 |

`magnus/raw_logs/` 下面按 v2 job id 分目录保存原始产物。除 v1 已说明的 `command.json`、`compile.json`、`env_report.json`、`manifest.json`、`stdout.txt`、`stderr.txt`、`comsol.log`、`.java`、`.class`、`.mph` 等文件外，v2 还常见：

| raw log 文件类型 | 作用 |
|---|---|
| `results/metrics.json` | job 后处理得到的结构化指标，例如数据行数、是否出现有效 `neff`。 |
| `results/*.csv` / `results/*.png` | 从该 job 下载的局部结果副本。 |
| `raw/postprocess.stdout.txt` / `raw/postprocess.stderr.txt` | 后处理脚本 stdout/stderr。 |
| `raw/neff_v2_raw_from_stdout.csv` | v2 从 COMSOL stdout 解析出的原始 `neff` 表。mode-analysis probe 中 0 行是失败证据，不是空白成功。 |

### V2 优先阅读顺序

```text
README.md
final_report.md
workflow_handoff_A_v2.md
v1_experience_audit.md
v2_reproduction_plan.md
failure_retry_record.md
todo.md
```

## 技术报告索引

如果只想快速理解项目现状，优先读这些报告：

| 报告 | 内容 |
|---|---|
| `AGENTS.md` | 项目全局规则、当前状态、安全约束和 AI 行为标准。 |
| `reproduction_test/private/Degiron_2009_NJP_Fig3/final_report.md` | v1 复现总结。 |
| `reproduction_test/private/Degiron_2009_NJP_Fig3/workflow_handoff_A.md` | v1 对 agent 框架和光学组标准答案的交接。 |
| `reproduction_test/private/Degiron_2009_NJP_Fig3_v2/final_report.md` | v2 复现总结和当前 blocker。 |
| `reproduction_test/private/Degiron_2009_NJP_Fig3_v2/workflow_handoff_A_v2.md` | v2 对后续框架和光学组需求的交接。 |
| `reproduction_test/private/Degiron_2009_NJP_Fig3_v2/pi_wechat_update.md` | 给 PI 的阶段性微信汇报草稿。 |

## 当前最重要的下一步

请光学组提供一个最小 COMSOL 6.3 GUI 导出的 mode-analysis 模板：

```text
2D rectangular dielectric waveguide
wavelength = 1.55 um
output = at least one correct neff
format = .java exported from COMSOL GUI, or .mph
```

这个模板的意义是固定 Wave Optics/RF 的 physics、boundary/PML、study、solver sequence 和 result expression。之后 agent 才能可靠地修改几何、材料和 sweep，而不是继续猜 COMSOL 内部 API 设置。
