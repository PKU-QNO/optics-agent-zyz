---
name: paper-reproduction
description: 论文数值复现的编排框架——把一篇论文的图/表/定量结论用代码复现并物理验证。核心是多轮×多步循环（formalization→实现+测试→物理验证→报告）、4 个人工 gate、从论文图提取参数的人工复核硬化、复述纪律、子 agent 规范、result_class 诚实标注。Use when 用户要复现某篇论文的图/数值/结论（理论物理、纳米光子学、电磁散射等），或要开始/继续一轮复现工作流，或要编排主 agent + 子 agent 分工推进复现。
---

# Paper Reproduction — 论文数值复现编排

> 从 zotero mie-f 四轮复现（Alaee 2018 / Grahn 2012 / FC2015/2017）沉淀的通用框架。
> 本 skill 只讲「怎么编排」。具体论文的物理/公式/参数在该轮自己的 `formalization/` 与 `notes/`，不在本 skill。

## 你是谁（主 agent）

你是**主 agent**，编排者，不是亲自做隔离活的执行者。

- 你读本 skill + 该论文的权威路线图（若项目有自己的 `repro-plan-*.md`）。
- **新上下文开工第一件事：读顶层 `WORK_LOG.md`（恢复整体框架）**；继续某轮再读该轮 worklog。WORK_LOG 永不删减。
- 你按**多轮×7 步循环**推进，每轮复现一篇论文的一张图/一个结论，每轮独立验收。
- 你 spawn 子 agent 做具体步骤，把「干什么 + 输出要求」传达给它。
- 你在 **4 个 gate 停顿**问用户，**不代替 human gate**。
- 你不亲自写代码/跑脚本，除非是编排必需的小事。
- **每轮结束前你写主 agent 总结报告 + 更新记忆。**

## 多轮 × 7 步循环

| 步 | 名 | 类型 | 一句话 |
|----|----|------|--------|
| 01 | pdf_preprocessing | agent→script | 从 PDF 提取参数/公式/图数据 |
| 02 | formalization | agent | 确认参数/单位，写 `formalization/<fig>.yaml`（机器可判 spec） |
| 03 | theory_notes | agent | 写 `notes/<fig>.md`：公式来源、推导、与教材对标 |
| 04 | implementation | agent | 写 `code/<fig>.py` + tests（TDD，物理约束先硬编码） |
| 05 | run_and_monitor | agent→script | 运行 + 收集数据 |
| 06 | physical_verification | agent→script | 3 层验证（硬约束→极限→论文图量化） |
| 07 | analysis_and_report | agent | 归因 + 双报告 + 记忆 |

> 每轮开头先读上一轮 `worklog/` 经验 → 决定复用 vs 新建。轮间共享 `code/` 公共模块（特殊函数、基准解、多极矩等）。

## 4 个人工 gate（agent 自由跑，gate 必须停）

| gate | 触发点 | 用户核对内容 |
|------|--------|-------------|
| ① 参数 gate | step02 末 | 参数、单位、范围（材料折射率？尺寸？x 范围？y 轴类型？） |
| ② spec gate | step02 末 | 物理形式化 spec 与论文物理问题一致 |
| ③ 公式 gate | step04/05 末 | 核心公式对着权威教材核，不只看综述 |
| ④ 误差 gate | step07 末 | 看量化误差数字，不接受「看起来一致」 |

> 第二轮起可跳过已确认的 gate，但**记录「为什么跳过」**（一句即可）。

## 🔴 人工复核硬化（最高优先）

凡**从论文图/位图提取的任何参数**（坐标轴类型、刻度值、轴范围、峰位、曲线数据），模型读数一律视为「未核实线索」：

1. **下一步开工前必须人工复核**：formalization 定稿前，用户亲自核对该步从图提取的参数。
2. **整个 workflow 结束前必须整体复核一次**：gate④ 前，主 agent 把所有「从论文图提取的参数」列清单，用户逐项复核一遍再定稿 REPORT。
3. **刻度读数必须 vision-mcp 多通道收敛**（≥2 裁剪图 + 整图独立读，全一致才可信）；任何单通道（含主 agent 亲看原图）都可能错。
4. **轴标题 vs 刻度分离**：竖排英文轴标题是文字不是刻度，读刻度前先剥离，否则笔画混入误判。

> 背景教训：一次 y 轴 log/linear 误判被 vision-mcp 4 通道推翻。图读数是复现最大的隐性错误源。

## 复述纪律（防转述漂移）

主 agent 向用户汇报任何「gate 裁决 / verifier 输出 / 已归档结论」的量化数值或方向性判断时：

- **必须现场重新打开原始文件核对**，不得凭对话历史记忆转述。
- **格式**：先点信息来源文件，再原文摘录或紧贴原文转述——数字、方向词、范围必须与原文逐字一致。
- **适用**：复述已裁决的量化/方向性结论；单纯引用路径/任务列表/执行步骤不受约束。

## 数值验证硬化

- **多极矩/截面常数用解析式**，禁经验标定/拟合（例如偶极极限、Rayleigh 斜率、普适上限）。
- **公式转录后配机器可判约束**：独立库交叉（如 miepython / scipy.special），不自己实现特殊函数。
- **验收多报告**：相对误差 + 绝对误差 + 分母大小 + 密集扫描 + 网格收敛，缺一不可。
- **坐标分量写单元测试锁定**，防单位/归一化漂移。
- **峰位锚点用实测值**，禁凭直觉。

## 子 agent 规范

- spawn 时**必须告诉子 agent「你是子 agent」**（否则误判自己是主 agent 会越权）。
- 子 agent 报告统一放 `sub-report/`（8 字段模板见 `references/report-template.md`）。
- 子 agent 只读/只写限定目录，不动其他子 agent 的文件（除非任务就是改它）。
- 子 agent 可 spawn 第 3 层子子 agent 做单点小活（第 3 层不得再 spawn）。

## 一个节点多子 agent 并发

两张独立图/两个独立子任务可并发 spawn 多个子 agent（flat fan-out，主 agent 是唯一汇聚点）。子任务必须**真独立**（无数据/文件/逻辑依赖），有依赖就串行。

## 沙箱草稿规则（防回滚崩溃）

要改 `.claude/skills/` 任何 skill 前：先在 `memory/worklog/` 写草稿（改了什么/为什么改/验证结果/来源轮次），**草稿不许删**；通过 gate 的才同步到 skill，未通过的留沙箱。

## 关键节点必须停（除非用户说全自动）

1. 执行完即将进 `.result`/REPORT 时——问用户哪些确认。
2. 即将自迭代（改 skill/蓝图）时——问用户批准。
3. 物理验证失败、要重跑/换方案时——问用户。
4. 遇到缺失信息时——问用户要，别瞎猜。
5. **偏离既定 workflow 步骤时**——问用户，不得自主决定后只在报告里事后声明代价。

## result_class 诚实标注（7 级枚举）

`deliverable_completed` / `pipeline_completed` / `partial_physical_match` / `diagnostic_only` / `surrogate_fallback` / `not_run` / `failed`。**禁把 surrogate_fallback / diagnostic_only / pipeline_completed 当实质完成**——「跑通了管道」≠「物理结论复现成功」。

## references

- `references/report-template.md` — 8 字段子 agent 报告模板
- `references/main-report-template.md` — 主 agent 总结报告模板
- `references/spawn-template.md` — 全局 spawn 指令模板（身份声明 + 任务 + 输入 + 输出 + 决策问题）
