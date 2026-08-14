# COMSOL via Magnus 链路探索结论

> 只读探索完成（2026-08-03）。工作区 C:\Users\27370\Desktop\project\optics_agent。
> 未提交任何 job、未 ssh、未读 secret.json 内容。

## A. 技能链全貌（4 个 skill 各自：已实现/缺口）

### A1. optics-magnus-platform（.codex/skills/optics-magnus-platform/SKILL.md）
- 已实现/已验证：Magnus SDK 连接模式（magnus_address-gu / magnus_token-gu，读 secret.json）；COMSOL 蓝图 Optics_COMSOL_Runtime_zyz 的保存/launch 命令；job 查询与生命周期诊断；FileSecret 临时文件流；system_entry_command 挂载数组与 Apptainer 环境变量转发；资源默认 B2/cpu/8 核/32G。
- 缺口/警告：job-in-job 嵌套提交只是源码设计允许，每个部署网络不保证；service 只有一个 backing job；repo_name=optics-agent 失败（Failed to clone repo），必须用 repo_name=magnus + namespace=Rise-AGI。

### A2. optics-comsol-runtime（SKILL.md）
- 已实现/已验证：active 镜像 docker://magnus-local/comsol-runtime:latest（约 1.38G，管理员导入，禁止覆盖/重建）；license 挂载 $HOME/.comsol-container-license:/opt/comsol-license；最小 smoke 命令；输出契约 /home/magnus/data/optics_agent/comsol/runs/<run_id>/；已验证 job 表（de368ea77db7da7f smoke、deb10848cb99128a license solve、3681f26d40ccbf7b L-membrane eigenmodes、f1442f2403e37150 env_check）。
- 能力探测 campaign comsol-capability-20260613-v1 全 Success：envcheck、core-pde-eigenmode、optics-helmholtz（标量 Helmholtz core PDE）、wave-optics-probe、fluid-laminar-probe、fluid-pde-fallback。
- 缺口/边界声明：These are smoke tests, not proof that large production Wave Optics/CFD models are already validated；模块覆盖需继续用具体 case 验证。

### A3. optics-comsol-batch（SKILL.md）
- 已实现/已验证：runner 支持 env_check / batch_java / batch_mph / batch_mfile；comsol compile 先编译再 comsol batch；MPH 规范化 model_output.mph；artifact 契约与失败码（COMSOL_NOT_FOUND / LICENSE_UNAVAILABLE / BATCH_EXIT_NONZERO / OUTPUT_MPH_MISSING / POSTPROCESS_FAILED / INPUT_MISSING）；license 挂载经验（/opt/comsol-license + server_env）。
- 缺口：runner 早期版本不捕获 Java 侧 stdout marker 和 metrics（mie 报告里 metrics:{}、success_markers:[]，标注为 output-contract limitation）。

### A4. comsol-java-api（SKILL.md + references/）
- API Principles 明确声明：
  - Treat the bundled COMSOL Java API manual as API-reference material, not as proof that a physics model is correct.
  - The Java API Reference can verify API syntax and object patterns; it cannot by itself prove a Wave Optics/RF mode-analysis physics model is well posed.
  - The manual used for this skill is COMSOL 4.3; the active optics_agent runtime is COMSOL 6.3（版本敏感特征名/设置键/solver 序列必须用 6.3 GUI-exported Java 验证）。
  - Mark uncertain physics-specific setting keys as requiring GUI-exported Java validation instead of guessing.
  - Stop blind retries after an isolated dielectric waveguide smoke reaches the eigensolver but fails matrix factorization; request a COMSOL 6.3 GUI-exported .java or .mph template.
- 已验证：batch-safe Java 骨架、geometry/mesh/study/solver/results API 语法、通用 PDE eigenvalue 模板、显式 FreeTri 网格回退、COMSOL sandbox 限制（禁 getenv/getProperty/文件 IO/内部类）。

## B. 现有链路产物

### B1. comsol/automation/submit_comsol.py
- 读 secret.json（magnus_address-gu / magnus_token-gu）配置 SDK；支持 --package-only / --save-only / launch。
- 参数：run_mode、license_mode（personal_storage|server_env|file_secret|env_check_only）、license_path（默认 /opt/comsol-license/license.dat）、input_file/case_path/case_bundle_secret、container_image（默认 docker://magnus-local/comsol-runtime:latest）、cpu/memory/storage/priority、--arg key=value。
- --save-only 仅保存蓝图，不 launch。默认蓝图包 .magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml 本地存在。

### B2. comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
- 挂载：/data/public/zhangyuanzheng:/data/public/zhangyuanzheng、/home/magnus/data:/home/magnus/data、$HOME/.comsol-container-license:/opt/comsol-license。
- 设置 APPTAINERENV_LM_LICENSE_FILE / APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat、MAGNUS_HOME=/magnus。
- 启动：调用服务器侧 /data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py。蓝图精简，runner/license 在服务器私有存储。

### B3. 蓝图包
- 存在 .magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml（本地）。另有 madgraph-simulator.magnus.blueprint.yaml（无关）。

### B4. 已跑过的 COMSOL run 记录
- 本地 comsol/local-runs/local-env-check/：manifest 显示 COMSOL Multiphysics 6.3.0.290、batch help 文本；无实际 solve。
- 远端 runs 不落本地：真实 run 在 /home/magnus/data/optics_agent/comsol/runs 与 /data/public/zhangyuanzheng/comsol-runtime/runs（只能通过 Magnus 查）。本地有 Degiron V1/V2 的 raw_logs 镜像（reproduction_test/private/Degiron_2009_NJP_Fig3*/magnus/raw_logs/），含 manifest.json / stdout.txt / metrics.json。
- 证据性 run：L-membrane eigenmodes 特征值 9.64379 接近参考 9.6397238；capability campaign 6 job 全 Success；Mie 时域标量 wave smoke/medium 全 Success。

### B5. comsol/runtime Java 模板/探针清单
- probes/CorePdeEigenmode.java（通用系数型 PDE eigenvalue，成功）
- probes/OpticsHelmholtz.java（标量 Helmholtz core PDE，成功）
- probes/WaveOpticsProbe.java（候选 ElectromagneticWavesFrequencyDomain / ElectromagneticWaves，frequency-domain，成功，只证明能创建并求解最小设置）
- probes/FluidLaminarProbe.java、probes/FluidPdeFallback.java（流体）
- cases/mie_scattering/MieScatteringTimeDomain2D{Smoke,Medium}.java（2D 时域标量波 FDTD-like，CoefficientFormPDE + if(x^2+y^2<r0^2,n_cyl^2,1) 折射率表达式 + Dirichlet 边界 + Transient study，成功）
- skill 内模板（.codex/skills/comsol-java-api/assets/templates/）：BasicModel / BatchSafeModel / GeometrySequence / MeshFreeTri / StudySolverEigenvalue / ResultsEvalExport，全部是通用 PDE/geometry/mesh，没有含 Wave Optics/RF 电磁接口（StudySolverEigenvalue.java 顶部注释明示：Do not use this as a Wave Optics/RF mode-analysis model without GUI-exported Java validation）。

## C. 电磁场模拟可行性判断（⚠️ 平台通，物理建模未通）

### C1. COMSOL 6.3 镜像能做什么（Wave Optics / RF / emw / ewfd 痕迹）
- 本地 build 配置 comsol/docker/comsol-setupconfig.template.ini 明确勾选 comsol.woptics=1、comsol.rf=1、comsol.roptics=1、comsol.cfd=1、comsol.mfl=1、comsol.ht=1，即本地构建的大镜像计划包含 Wave Optics + RF 模块。
- 但 active 镜像是管理员另行导入的约 1.38G 轻量镜像，模块覆盖未知。docs/reports/comsol_runtime_sync_note_for_senior.md 明确：active image 只有 1.38G，不能默认认为所有光学和流体模块都在。
- wave-optics-probe 成功（job 1d9a03b77815f140）：能创建 emw / ElectromagneticWavesFrequencyDomain 类接口并完成 frequency-domain 求解、写出 .mph。报告解读为最小电磁专业模块探针通过，但明确标注只是 smoke，不是生产级 Wave Optics 验证。
- Degiron V2 的 wave optics mode analysis 失败：模式分析探针能创建电磁物理接口、显式网格成功、到达 eigensolver，但矩阵分解失败，0 行 neff。

### C2. 有没有已成功的电磁/光学 COMSOL 案例？
- 有（有限程度）：
  1. optics-helmholtz（标量 Helmholtz core PDE）成功，是标量近似，不是真电磁。
  2. wave-optics-probe（最小电磁 frequency-domain）成功，只证明接口创建+求解链路，不产物理量。
  3. Mie 时域标量 wave 散射 smoke/medium 成功，2D 时域标量 FDTD-like，用 CoefficientFormPDE 模拟折射率圆域，Dirichlet 边界，产出标量场，无 PML，非真电磁全矢。
  4. L-membrane eigenmodes 成功（通用 PDE 特征值）。
- 没有任何成功产出物理电磁量的全矢量 Wave Optics/RF 案例；模式分析在 Degiron 上失败。

### C3. Degiron 2009 案例（SU-8 waveguide mode analysis 失败根因）
- 记录位置：comsol-java-api/SKILL.md（API Principles）、references/09-api-patterns-for-optics.md、references/10-common-errors.md、reproduction_test/private/Degiron_2009_NJP_Fig3_v2/（final_report.md、magnus/failure_retry_record.md、raw_logs）。
- 失败链（V1 到 V2）：
  1. V1：OUTPUT_MPH_MISSING（Java 未返回/保存模型）；COMSOL sandbox 禁环境变量/系统属性/文件 IO；内部类执行错误；physics-controlled mesh 失败；full-vector mode analysis 到达 eigensolver 后矩阵分解失败（多 shift）。
  2. V2：显式 FreeTri + Size 网格修好 mesh blocker；isolated SU-8 Wave Optics/RF mode-analysis（Degiron2009Fig3V2ModeAnalysisSu8Smoke.java）编译成功、显式网格成功、能创建 emw 接口与 ModeAnalysis / BoundaryModeAnalysis study、到达 eigensolver、存出 .mph，但 neff / beta / plain 三种 shift 全部 Failed to compute the matrix factorization in the eigensolver（COMSOL 断言失败），0 物理 neff 行。
- 失败根因（skill 与 v1 audit 明确）：不是 Magnus 包装问题，是 COMSOL 6.3 mode-analysis 设置问题：physics/study/solver 特征名与设置键是猜的（4.3 manual 不足以支撑 6.3 的 Wave Optics/RF 模式分析）；shift 单位可能在 neff / beta / raw eigenvalue 之间混用；边界/PML/开放域未验证；材料用空间 if(...) 表达式覆盖重叠几何而非显式非重叠域选择；先试耦合结构而未先验证 isolated 波导。

## D. JAVA API 可靠性评估（⚠️ 语法可靠，物理建模不可靠）

### D1. 5 个模板 Java 文件是否有电磁场模板？
- 没有。BasicModel / BatchSafeModel / GeometrySequence / MeshFreeTri / StudySolverEigenvalue / ResultsEvalExport 全是通用 PDE / geometry / mesh / eigenvalue。StudySolverEigenvalue.java 显式标注 Do not use this as a Wave Optics/RF mode-analysis model without GUI-exported Java validation。唯一含 emw 的是 runtime 探针 probes/WaveOpticsProbe.java（frequency-domain，非模式分析）。

### D2. 能写对 vs 不能保证写对的分界线
- 分界线 = 是否依赖物理模块专属设置：
  - 能写对：COMSOL 通用 Java API 语法（model/param/geom/mesh/study/sol/result）、通用 PDE/eigenvalue、geometry/mesh 序列、batch-safe 骨架、结果提取表。
  - 不能保证写对：Wave Optics/RF 模式分析的 physics 接口字符串、boundary feature（Scattering/PML）、ModeAnalysis / BoundaryModeAnalysis study 设置、solver 序列、emw.neff / ewfd.neff 结果变量。skill 反复声明：这些必须来自 COMSOL 6.3 GUI-exported Java 或 Wave Optics/RF 官方文档，Java API Reference（4.3）不足以证明模型良态。
- Degiron 教训被提升为 skill 规则：停止盲目重试，改为索取 GUI-exported .java / .mph 模板。

### D3. 替代方案证据
- skill 与 v1/v2 报告一致认为 GUI-exported Java（或 .mph）是 physics/mode-analysis 设置的 source of truth（references/08-gui-exported-java.md：Treat COMSOL 6.3 GUI-exported Java as the highest-priority source；当 Java API Reference 与 GUI-exported Java 冲突时，follow the GUI-exported Java first）。
- comsol/docs/plans/comsol_headless_plan.md 提到 Python mph + mphserver 路线是参考项目做法，但已判定该参考项目只是验证工程而非成熟产品化接口，optics_agent 选 comsolbatch + Java API 为主。
- 现状：本地仓库没有现成的 COMSOL 6.3 GUI-exported Wave Optics/RF mode-analysis Java 模板（Degiron v2 todo 明确记录 not found locally）。这是当前最大缺口。

## 结论：这条链路能不能用于 Fig.3 电磁场模拟？JAVA API 是不是好方式？缺口在哪？

### 链路可行性：⚠️ 平台链路通，物理建模未通
- 平台链路已通且证据充分：active 镜像可跑 COMSOL 6.3 headless、comsol compile + comsol batch、license 挂载求解、Python 后处理依赖齐全、通用 PDE/eigenvalue 与最小电磁探针成功、Mie 时域标量波案例成功。
- Fig.3 所需的电磁场模拟（全矢量 Wave Optics/RF 模式分析或频域散射）未验证通过：唯一尝试（Degiron V2 isolated SU-8）在 eigensolver 矩阵分解失败、0 物理行；没有任何成功产出物理电磁量的先例。
- 关键不确定点：active 1.38G 管理员镜像是否包含 Wave Optics/RF 模块与对应 license（wave-optics-probe 的成功暗示接口可创建，但模块覆盖未系统确认）。

### JAVA API 是不是好方式：⚠️ 语法可靠，物理建模不可靠
- 对通用 PDE/eigenvalue、几何/网格、批量包装、结果提取：是好方式（有模板+已跑通探针）。
- 对 Wave Optics/RF 模式分析（Fig.3 需要的）：不是好方式。基于 4.3 manual 手写 Java 无法保证 6.3 的模块专属 feature/solver/变量正确；Degiron V2 已验证这一点。手写 Java 只能作为最小探针或拿到 GUI-exported 模板后打补丁的载体。

### 缺口（按优先级）
1. 没有 COMSOL 6.3 GUI-exported Wave Optics/RF 2D 模式分析模板（.java 或 .mph），唯一被所有 skill/report 认定为解锁 Fig.3 的必需 artifact。
2. active 镜像的模块/license 覆盖未系统确认，需要以带 GUI 导出的最小 waveguide mode analysis case 验证 emw / ModeAnalysis 是否真正可用，而不只是接口可创建。
3. PML/散射边界/材料域选择的方式未验证，Degiron 用空间 if 表达式覆盖材料，失败时被列为疑因之一。
4. shift 单位约定（neff vs beta vs raw eigenvalue）未确认，需要从 GUI 导出里读确切 setting 再决定。
5. 若 Fig.3 时间紧，可先考虑用 2D 标量波/频域散射（已有 Mie 时域标量波成功先例）做近似，或直接用纯 Python 的 Mie/离散偶极近似交叉验证；但全矢量 Fano 效应需要真电磁 FEM，最终仍需 GUI-exported 模板。
