# PI WeChat Update

老师好，我系统同步一下 optics_agent 论文复现这条线的进展。之前从 v1 到 v2 的细节没有及时跟您汇报清楚，所以我把现在的状态、已经验证的能力、以及需要光学组配合的地方整理一下。

这轮主要选了 Degiron 2009 NJP 论文里的 Fig. 3 做试跑。目标不是只复刻一张图，而是亲自走一遍完整流程：读论文、提取几何和材料参数、写 COMSOL 模型、通过 Magnus 提交、读日志、修失败、生成 CSV/图和最终报告。这个过程是为了明确后续论文复现 agent 和自迭代工作流到底需要哪些模块。

目前已经确认的是：COMSOL/Magnus 运行链路基本打通了。COMSOL Java 模型可以编译、batch 运行、保存 `.mph`，也可以通过 stdout/postprocess 自动生成 CSV 和图。v1 已经完成了参数表、缺失信息表、提交脚本、失败记录、最终报告和交接报告；v2 又单独开了新目录重跑，补了更严格的验证和失败定位。

但物理复现还没有成功。v1 最后能出类似曲线的图，但那是 `surrogate_fallback`，只能证明流程，不是 COMSOL 物理复现。v2 的标量 TM-like PDE 诊断也能跑完整 sweep，但结果显示 `Re(neff)` 偏低、`Im(neff)` 基本为 0，也没有恢复 Fig. 3 在 `t≈5.6 µm` 附近的反交叉趋势，所以也不能算论文复现成功。

现在定位到的核心问题不是 Magnus 封装，也不是 COMSOL license/image，而是 Wave Optics/RF 的 full-vector mode analysis 还缺 COMSOL 6.3 里准确的物理接口、边界/PML、solver sequence、mode search 和 `neff/beta` 导出设置。我已经把问题缩小到孤立 SU-8 波导：模型能编译，显式网格能通过，能进入 eigensolver 并保存 `.mph`，但 eigensolver 仍然 matrix factorization failed。这说明继续靠我手写猜 Java API 意义不大。

这里有一个关键点：COMSOL GUI 里建好的模型可以直接导出 Java 文件。也就是说，我们不一定需要光学组同学手写 COMSOL Java；更现实的方式是请他们在 COMSOL 图形界面里搭一个最小可运行的 mode-analysis 模型，然后导出 `.java` 或直接给 `.mph`。这个模板会告诉 agent 正确的 physics/study/solver/result 设置，后续 agent 再基于模板自动改几何、材料和 sweep。

所以下一步最需要光学组支持的是一个最小 COMSOL 6.3 GUI 导出的 mode-analysis 模板，`.java` 或 `.mph` 都可以。最小例子可以是 2D 矩形 dielectric waveguide，在 1.55 µm 下能输出一个正确的 `neff`。同时希望他们给每个复现任务提供“标准答案”式信息：geometry、materials、physics、boundary/PML、mesh、solver、sweep、validation range、common failure notes。这样 agent 才能稳定生成和自迭代，而不是靠猜 COMSOL 内部设置。

我这边已经把这次经验写进 AGENTS 和项目 skills，后续会强制区分三种状态：流程跑通、COMSOL job 成功、物理复现成功，避免把 fallback 或诊断结果误报成论文复现。
