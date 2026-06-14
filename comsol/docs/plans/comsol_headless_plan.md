# COMSOL 非 GUI（Headless）接口与 Magnus 蓝图集成计划

## 0. 任务结论

参考项目 `permafrost-paper2016-agent-repo-main` 已经做出一个可运行的 COMSOL 非 GUI 原型，但它本质上是一个“COMSOL Python mph / mphserver 服务化 + Magnus Blueprint 包装”的验证工程，而不是成熟的工程级 COMSOL 产品化接口。对 optics-agent 更务实的路线是：

- **Phase A** 先做标准化 headless runner：优先封装 `comsolbatch`，保留 Java API / Python `mph` 作为模型生成与调试后端；统一输入 JSON、输出 manifest、日志、结果文件和失败分类。
- **Phase B** 再将 runner 包装成 Magnus 蓝图：由蓝图负责提交、容器/挂载、环境变量、资源规格和 artifact 回收；COMSOL 许可证、安装目录和 token 均只由运行环境提供。
- 对 optics-agent，不建议直接照搬参考项目的“论文复现 + 降阶物理模型 + 经验文件写入”结构；应抽取其中的接口契约、服务复用、artifact 组织和 Blueprint 注册方式，重写为光学仿真专用的最小、干净、可测试框架。

---

## 1. 参考项目架构分析

### 1.1 顶层结构

参考项目主要目录含义如下：

```text
permafrost-paper2016-agent-repo-main/
├── src/blind_permafrost_agent/          # 降阶/快速扫参后端，不依赖 COMSOL
├── scripts/                             # COMSOL service、COMSOL study、workflow runner、报告生成、蓝图注册
├── blueprints/                          # 本地 Blueprint shim / 接口契约
├── comsol/blueprints/source/                   # Magnus YAML 蓝图 artifact
├── comsol/docker/                          # COMSOL 应用镜像 / Python mph fallback 镜像定义
├── skills/                              # agent skill 与环境 runbook
├── docs/                                # 架构说明、环境手册、审计报告
├── cases/                               # study 输入 JSON
├── evaluation/                          # 后置 evaluator，避免运行期读论文 target
└── permafrost-agent/experience/          # 经验记录文件
```

它采用的分层思想是：

```text
自然语言/Agent 层
  ↓ 解析工况、选择流程、解释结果
Skill / Runbook 层
  ↓ 保存可迁移的运行规程、边界、失败分类
Blueprint / Runner 层
  ↓ 扩展 case、调用 COMSOL、写 manifest/progress/metrics
COMSOL 后端层
  ↓ mphserver + Python mph/Java API 非 GUI 建模求解
Artifact / Evaluation 层
  ↓ manifest、csv、.mph、log、报告；后置对照评估
```

### 1.2 COMSOL 非 GUI 实现方式

参考项目实际使用了两条 COMSOL 非 GUI 路线：

#### 路线 1：Python `mph` + COMSOL `mphserver`

核心文件：

- `scripts/comsol_mph_service.py`
- `scripts/run_comsol_python_heat_smoke.py`
- `scripts/run_comsol_paper2016_study.py`

实现要点：

1. 通过 `comsol mphserver -silent -login force -user ... -passwd nostore -port ... -multi on` 启动 COMSOL server。
2. Python 用 `mph.Client` 连接本地 `127.0.0.1:<port>`。
3. 通过 `model.java` 调用 COMSOL Java API 创建模型、几何、材料、物理场、mesh、study。
4. 调用 `java.study(...).run()` 求解。
5. 保存 `.mph`，抽样 `model.evaluate("T", "K")`，写出 `manifest.json`、`simulation_metrics.csv`、server log。
6. `comsol_mph_service.py` 支持常驻复用 service，避免每个 case 反复冷启动 COMSOL。

优点：

- 适合动态建模、自动生成 geometry/physics/study。
- 可以在 Python 中统一做参数扫描、结果抽样、物理性检查和 artifact 写出。
- 常驻 `mphserver` 能显著减少冷启动成本。

问题：

- 依赖 `mph`、`JPype1` 与 COMSOL 版本发现，环境脆弱。
- `mphserver` 需要本地 socket，受限 sandbox 或 runner 网络策略可能失败。
- 密码状态存在临时 state file，虽然不入仓库，但需要处理权限、清理和异常终止。
- 代码里直接写 Java API 调用，选择边界时用硬编码 selection 编号，模型稍复杂就容易错。
- 当前 demo 是二维 stationary heat transfer，很多论文物理被等效边界替代，不是完整工程级仿真。

#### 路线 2：预留 `comsolbatch` batch contract

核心文件：

- `blueprints/comsol_adapter_contract.md`

它建议的 batch 执行形态是：

```bash
"$COMSOL_BIN" batch -inputfile model.java -outputfile run.mph -batchlog comsol.log
```

但参考项目没有真正实现完整 `comsolbatch` runner。对 optics-agent 来说，`comsolbatch` 反而应作为 Phase A 的首选，因为它更适合 headless 标准作业：输入文件、输出文件、日志和退出码天然明确，也更贴近 Magnus Job 模式。

### 1.3 Magnus 蓝图集成方式

核心文件：

- `comsol/blueprints/source/permafrost-comsol-python-heat-smoke.yaml`
- `comsol/blueprints/source/permafrost-comsol-python-paper2016-study.yaml`
- `comsol/blueprints/source/permafrost-airflow-thermal-study.yaml`
- `scripts/register_magnus_blueprints.py`
- `scripts/run_permafrost_agent_once.py`

参考项目有两类蓝图写法：

#### 简单 metadata YAML

例如 `permafrost-comsol-python-heat-smoke.yaml`：

```yaml
id: permafrost-comsol-python-heat-smoke-safe
entrypoint: scripts/run_comsol_python_heat_smoke.py
default_args:
  run_dir: /tmp/cmph_run/comsol_python_heat_smoke
runtime_env:
  required:
    - COMSOL_ROOT
outputs:
  - manifest.json
  - raw/.../*.mph
  - raw/.../mphserver.log
```

这类 YAML 更像蓝图描述/注册 artifact，便于文档化和离线检查。

#### Magnus DSL YAML

例如 `permafrost-comsol-python-paper2016-study.yaml` 的 `code: |` 中定义 `blueprint(...)`，内部拼接 `entry_command` 并调用：

```python
submit_job(
  task_name="permafrost-comsol-python-paper2016-study",
  entry_command=entry,
  repo_name="landscape-dynamics",
  branch="halluscope",
  commit_sha="...",
  job_type="B2",
  container_image="docker://permafrost/comsol-app-runtime:6.4-py312",
  memory_demand="8G",
)
```

运行后用 `$MAGNUS_RESULT` 写回 JSON。这个思路值得复用：Magnus 蓝图不要承载复杂仿真逻辑，只固定调用项目内 runner，并把结果 manifest 写入 Magnus result。

### 1.4 容器与运行环境策略

核心文件：

- `comsol/docker/comsol-app-runtime.Containerfile`
- `comsol/docker/comsol-python-mph.Containerfile`
- `skills/permafrost-comsol-environment/SKILL.md`
- `docs/environment_setup_and_magnus_handoff.md`

参考项目推荐：

- 受控应用镜像包含 COMSOL 6.4 + Python + `mph` + `JPype1` + 绘图/报告依赖。
- 仓库代码不打入镜像，由 Magnus runner 挂载到 `/workspace/...`。
- license、trial code、Magnus token 不进镜像、不进 Git，只由运行时 mount/env/license server 提供。
- 若不能把 COMSOL 放进镜像，则用 Python-only 镜像，运行时额外挂载 COMSOL。

这是可复用的关键边界：**镜像提供应用运行时，仓库提供业务脚本，许可证由环境提供。**

### 1.5 Skill / Runbook 方式

参考项目将可复用规程写入：

- `skills/permafrost-comsol-agent/SKILL.md`
- `skills/permafrost-comsol-environment/SKILL.md`

其中 environment skill 是手册，不自动安装 COMSOL；agent skill 描述从自然语言工况到 Blueprint、COMSOL solve、QC、报告的流程。

对 optics-agent 可复用的不是冻土内容，而是这套文档边界：

- 环境准备 skill / runbook：说明 COMSOL_ROOT、license、Python、Magnus、镜像 smoke test。
- 仿真 agent skill：说明输入 schema、runner、蓝图、输出契约、失败分类。

---

## 2. 可复用思路与坑

### 2.1 值得复用的思路

1. **统一 artifact contract**

   每次运行都生成：

   ```text
   manifest.json
   progress/*.md
   simulation_metrics.csv 或 results.json
   raw/*.mph
   raw/comsol.log 或 mphserver.log
   errors/*.txt 或 failure.json
   ```

   这比只看 stdout 稳定得多，也便于 Magnus 回收结果。

2. **COMSOL service 复用**

   对需要多 case 扫参的任务，常驻 `mphserver` 能减少冷启动成本。即使 Phase A 首选 `comsolbatch`，Phase A+ 仍可保留 `mphserver` 作为动态建模/调试后端。

3. **Blueprint 只做编排，不写复杂模型逻辑**

   Magnus YAML 负责资源、镜像、挂载、命令和 `$MAGNUS_RESULT`；真正模型逻辑放在项目脚本中，方便本地测试和版本控制。

4. **环境与许可证边界清晰**

   COMSOL 本体、license、Magnus token 不进 Git、不进公开镜像、不进 skill。只通过运行时环境变量、挂载或机构 license server 提供。

5. **先 smoke，再复杂模型**

   参考项目先用最小 heat-transfer smoke 验证 COMSOL 非 GUI链路，然后再跑 study。optics-agent 也应先有最小 optical smoke，例如二维波导/散射/模式分析的最小模型。

6. **后端选择可降级**

   `run_permafrost_agent_once.py --backend auto/local/magnus` 的思想可复用：优先 Magnus，失败时可本地 runner；但对生产应避免悄悄 fallback 导致结果位置混乱，fallback 必须写入 manifest。

### 2.2 需要避免的坑

1. **不要把物理模型和 agent 叙事混在一起**

   参考项目中冻土论文复现、快速降阶模型、COMSOL demo、报告、经验记录交织较多。optics-agent 应将 COMSOL headless runner 做成通用底座，光学模型模板另放。

2. **不要依赖硬编码 COMSOL selection 编号**

   Java API 中 `selection().set([2])`、`selection().set([3])` 对简单矩形可行，对复杂几何不稳。应使用命名 selection、几何标签、显式边界选择策略，或在模板 `.mph` 中预定义 selections。

3. **不要把 `mphserver` 当作唯一 headless 方案**

   `mphserver` 适合交互式 API，但在 Magnus job 中本地 socket、端口、进程清理、并发隔离都会带来复杂性。Phase A 应优先实现 `comsolbatch`，它天然适合 batch job。

4. **不要在蓝图中写个人路径、固定 commit 或私有仓库约定**

   参考项目蓝图里有固定 repo/branch/commit/image。optics-agent 应参数化 repo、branch、commit、image，或由项目配置生成蓝图。

5. **不要把运行失败静默改成成功**

   参考项目有 fallback 和 broad physicality check。optics-agent 必须将 COMSOL 退出码、日志关键错误、缺失 artifact 作为结构化失败写入 manifest，而不是只靠 Python 异常或 stdout。

6. **不要把 license/server/token 写进代码或文档**

   文档只能写变量名，如 `COMSOL_LICENSE_FILE`、`LM_LICENSE_FILE`、`MAGNUS_TOKEN`；具体值只读 `secret.json` 或运行时环境。

7. **不要一开始就做复杂光学全模型**

   先建立最小 `comsolbatch` smoke，验证非 GUI、license、Magnus、artifact、日志，再接入真实光学模板。

---

## 3. optics-agent 的目标架构

### 3.1 建议目录结构

在 `C:\Users\27370\Desktop\project\optics_agent` 下新增：

```text
optics_agent/
├── comsol/
│   ├── README.md
│   ├── schemas/
│   │   ├── optical_case.schema.json
│   │   └── run_manifest.schema.json
│   ├── templates/
│   │   ├── smoke_2d_waveguide.java
│   │   ├── smoke_2d_waveguide.mph          # 可选；若 license/模板允许内部保存
│   │   └── README.md
│   ├── runners/
│   │   ├── comsol_batch_runner.py          # Phase A 主入口：comsolbatch 封装
│   │   ├── comsol_java_builder.py          # 生成/改写 Java 模型输入，可选
│   │   ├── comsol_mph_service.py           # 可从参考项目简化迁移，作为 API 后端
│   │   └── collect_outputs.py
│   ├── cases/
│   │   ├── smoke_waveguide_case.json
│   │   └── example_param_sweep.json
│   ├── scripts/
│   │   ├── run_comsol_smoke.py
│   │   ├── run_optical_case.py
│   │   └── validate_comsol_env.py
│   └── tests/
│       ├── test_schema.py
│       └── test_manifest_contract.py
├── comsol/blueprints/source/
│   ├── optics-comsol-headless-smoke.yaml
│   └── optics-comsol-case-run.yaml
├── comsol/docker/
│   ├── comsol-optics-runtime.Containerfile
│   └── comsol-python-fallback.Containerfile
└── skills/
    ├── optics-comsol-agent/
    │   └── SKILL.md
    └── optics-comsol-environment/
        └── SKILL.md
```

若暂时不想大改项目结构，可先只建：

```text
optics_agent/comsol/runners/comsol_batch_runner.py
optics_agent/comsol/cases/smoke_waveguide_case.json
optics_agent/comsol/blueprints/source/optics-comsol-headless-smoke.yaml
```

### 3.2 输入/输出契约

#### 输入 JSON：`optical_case.json`

建议最小 schema：

```json
{
  "case_id": "smoke_waveguide_001",
  "model": {
    "template": "templates/smoke_2d_waveguide.java",
    "mode": "batch_java"
  },
  "parameters": {
    "wavelength_nm": 1550,
    "core_index": 3.48,
    "cladding_index": 1.44,
    "waveguide_width_um": 0.5
  },
  "solver": {
    "study": "frequency_domain",
    "timeout_s": 1800,
    "cores": 4
  },
  "outputs": {
    "export_tables": ["s_parameters", "field_energy"],
    "export_images": ["ez_field"]
  }
}
```

原则：

- 输入只描述物理参数、模板、solver 控制和输出需求。
- 不包含 license、token、个人路径。
- 参数单位写清楚，避免 COMSOL Java 里乱拼单位。

#### 输出目录

每个 case 输出：

```text
runs/comsol/<run_id>/
├── manifest.json
├── input_case.json
├── command.json
├── progress/
│   ├── 01_validate_input.md
│   ├── 02_prepare_model.md
│   ├── 03_run_comsolbatch.md
│   └── 04_collect_outputs.md
├── raw/
│   ├── model_input.java 或 model_input.mph
│   ├── model_output.mph
│   ├── comsol.log
│   └── exports/
├── results/
│   ├── metrics.json
│   ├── tables/*.csv
│   └── figures/*.png
└── errors/
    └── failure.json      # 失败时存在
```

#### `manifest.json` 建议字段

```json
{
  "status": "completed | failed | partial",
  "backend": "comsolbatch_java | comsolbatch_mph | mphserver_python",
  "case_id": "...",
  "run_dir": "...",
  "started_at": "...",
  "ended_at": "...",
  "elapsed_seconds": 0,
  "comsol": {
    "root": "env:COMSOL_ROOT",
    "command": "comsol batch ...",
    "version": "6.x if detected"
  },
  "resources": {
    "cores": 4,
    "memory": "8G"
  },
  "artifacts": {
    "input_case": "input_case.json",
    "output_mph": "raw/model_output.mph",
    "batch_log": "raw/comsol.log",
    "metrics": "results/metrics.json"
  },
  "checks": {
    "output_mph_exists": true,
    "batch_log_exists": true,
    "exports_exist": true,
    "physics_sanity_ok": true
  },
  "failure": null
}
```

---

## 4. Phase A：COMSOL 非 GUI 命令接口设计

### 4.1 Phase A 的目标

Phase A 只解决一件事：在本地或容器中，通过命令行稳定调用 COMSOL，不打开 GUI，并形成标准输出契约。

完成标准：

1. `python comsol/runners/comsol_batch_runner.py --case comsol/cases/smoke_waveguide_case.json --run-dir runs/comsol/smoke` 可运行。
2. runner 能生成/准备 COMSOL 输入文件。
3. runner 能调用 `comsol batch` 或 `comsolbatch`。
4. runner 能捕获退出码、日志、`.mph`、导出 CSV/图片。
5. 成功/失败都写 `manifest.json`。
6. 无 COMSOL 环境时能输出清晰失败分类，而不是 Python stacktrace 结束。

### 4.2 推荐后端优先级

#### 后端 A：`comsolbatch` / `comsol batch`（首选）

命令形态：

```bash
comsol batch \
  -inputfile raw/model_input.java \
  -outputfile raw/model_output.mph \
  -batchlog raw/comsol.log \
  -np 4
```

或对已有 `.mph` 模板：

```bash
comsol batch \
  -inputfile templates/model_template.mph \
  -outputfile raw/model_output.mph \
  -batchlog raw/comsol.log \
  -pname wavelength_nm core_index \
  -plist 1550 3.48
```

具体参数需按当前 COMSOL 版本验证，但 runner 应先抽象成统一 `ComsolBatchCommand`，避免业务代码直接拼命令。

优点：

- 最适合 Magnus job。
- 不需要本地 socket。
- 日志和退出码清晰。
- 容易限制超时和资源。

适用场景：

- 已有 `.mph` 模板，只改参数求解。
- Java/M-file 可生成模型并求解。
- CI/Magnus 批量作业。

#### 后端 B：Java API 生成模型 + batch 求解

对于光学模型，建议先用 COMSOL GUI 做一个模板，再导出 Java。Phase A runner 做两件事：

1. 根据 JSON 参数渲染 Java 文件，替换参数和输出路径。
2. 调用 `comsol batch -inputfile rendered.java -outputfile output.mph`。

这样比在 Python 里用 `model.java.component...` 动态写全部模型更容易审计，也方便由 COMSOL GUI 重新导出更新模板。

#### 后端 C：Python `mph` + `mphserver`（保留但不首选）

迁移参考项目的 `comsol_mph_service.py`，但只作为：

- 动态建模原型；
- 需要 Python 直接读取结果数组时；
- 多 case 同一 service 复用；
- 本地 debug。

不建议第一版 Magnus 蓝图依赖它。

### 4.3 `comsol_batch_runner.py` 设计

建议模块职责：

```python
# comsol/runners/comsol_batch_runner.py

@dataclass
class ComsolRunConfig:
    case_file: Path
    run_dir: Path
    comsol_root: Path | None
    backend: Literal["batch_java", "batch_mph"]
    timeout_s: int
    cores: int

class ComsolBatchRunner:
    def validate_environment(self) -> EnvReport: ...
    def load_case(self) -> dict: ...
    def prepare_run_dir(self) -> None: ...
    def render_or_copy_model(self) -> Path: ...
    def build_command(self) -> list[str]: ...
    def run_command(self) -> CompletedProcess: ...
    def collect_outputs(self) -> dict: ...
    def write_manifest(self, status, failure=None) -> dict: ...
```

CLI：

```bash
python comsol/runners/comsol_batch_runner.py \
  --case comsol/cases/smoke_waveguide_case.json \
  --run-dir runs/comsol/smoke_waveguide_001 \
  --backend batch_java \
  --cores 4 \
  --timeout-s 1800
```

环境变量：

```text
COMSOL_ROOT             # 可选；若设置，用 $COMSOL_ROOT/bin/comsol
COMSOL_BIN              # 可选；优先级高于 COMSOL_ROOT
COMSOL_LICENSE_FILE     # 可选；由机构 license 决定
LM_LICENSE_FILE         # 可选；部分 license server 习惯
```

失败分类建议：

```text
env.comsol_bin_missing
env.license_unavailable
env.python_dependency_missing
input.schema_invalid
input.template_missing
model.render_failed
solver.timeout
solver.nonzero_exit
solver.log_error_detected
artifact.output_mph_missing
artifact.export_missing
postprocess.failed
```

### 4.4 光学 smoke case 建议

第一版不要直接做复杂器件。建议 smoke 选择：

- 2D dielectric waveguide mode / frequency-domain smoke；或
- 简化散射结构，输出一个 S 参数或场强积分；或
- 若 RF/Wave Optics 模块许可不稳定，先用最小 Poisson/Helmholtz 类模板验证 batch 链路，再升级到 Wave Optics。

验收指标：

```text
- COMSOL batch exit code = 0
- output.mph 存在且大于阈值
- comsol.log 无明显 license/solver fatal error
- 至少一个 CSV 或数值 metrics 导出成功
- manifest.status = completed
```

---

## 5. Phase B：Magnus 蓝图集成设计

### 5.1 Phase B 的目标

将 Phase A runner 包装为标准 Magnus 蓝图，使用户/agent 可以提交：

```bash
magnus run optics-comsol-headless-smoke
magnus run optics-comsol-case-run --case_file ... --run_dir ... --cores 4
```

或通过 Python/Magnus API 提交。

完成标准：

1. 蓝图能在 GU/Magnus runner 中找到仓库代码。
2. 蓝图能使用受控 COMSOL runtime 镜像或挂载的 COMSOL 安装目录。
3. 蓝图能把 `manifest.json` 写入 `$MAGNUS_RESULT`。
4. 蓝图输出明确 artifact 路径。
5. 本地失败和 Magnus 失败能区分：挂载失败、镜像失败、license 失败、COMSOL 求解失败。

### 5.2 蓝图文件建议

`comsol/blueprints/source/optics-comsol-headless-smoke.yaml`：

```yaml
id: optics-comsol-headless-smoke
name: Optics COMSOL headless smoke
entrypoint: comsol/scripts/run_comsol_smoke.py
description: Run the minimal optics COMSOL batch smoke without GUI.
default_args:
  case_file: comsol/cases/smoke_waveguide_case.json
  run_dir: /tmp/optics_comsol_run/smoke
runtime_env:
  required:
    - COMSOL_ROOT
  optional:
    - COMSOL_BIN
    - COMSOL_LICENSE_FILE
    - LM_LICENSE_FILE
outputs:
  - manifest.json
  - raw/model_output.mph
  - raw/comsol.log
  - results/metrics.json
security_policy:
  do_not_commit:
    - COMSOL license files
    - license server secrets
    - Magnus tokens
    - COMSOL server passwords
```

如果使用 Magnus DSL `code: |`，建议：

```python
def blueprint(case_file: CaseFile = "comsol/cases/smoke_waveguide_case.json",
              run_dir: RunDir = "/tmp/optics_comsol_run/smoke",
              cores: Cores = "4"):
    entry = (
      "set -euo pipefail\n"
      "export OPTICS_AGENT_REPO=${OPTICS_AGENT_REPO:-/workspace/optics_agent}\n"
      "export COMSOL_ROOT=${COMSOL_ROOT:-/opt/comsol/COMSOL64/Multiphysics}\n"
      "cd \"$OPTICS_AGENT_REPO\"\n"
      "python comsol/runners/comsol_batch_runner.py "
      "--case " + str(case_file) + " "
      "--run-dir " + str(run_dir) + " "
      "--cores " + str(cores) + "\n"
      "python - <<'PY'\n"
      "import json, os, pathlib\n"
      "m = pathlib.Path('" + str(run_dir) + "') / 'manifest.json'\n"
      "result = json.loads(m.read_text()) if m.exists() else {'status':'missing_manifest'}\n"
      "open(os.environ['MAGNUS_RESULT'], 'w').write(json.dumps(result, ensure_ascii=False, indent=2))\n"
      "print(json.dumps(result, ensure_ascii=False, indent=2))\n"
      "PY\n"
    )
    job_id = submit_job(
      task_name="optics-comsol-headless-smoke",
      entry_command=entry,
      job_type="B2",
      container_image="docker://<registry>/optics-comsol-runtime:6.x-py312",
      memory_demand="8G",
    )
    return {"status": "submitted", "job_id": job_id, "run_dir": str(run_dir)}
```

### 5.3 容器镜像建议

`comsol/docker/comsol-optics-runtime.Containerfile`：

```dockerfile
FROM python:3.12-bookworm

ARG COMSOL_ROOT=/opt/comsol/COMSOL64/Multiphysics
ENV COMSOL_ROOT=${COMSOL_ROOT}
ENV PATH=${COMSOL_ROOT}/bin/glnxa64:${COMSOL_ROOT}/bin:${PATH}
ENV PYTHONUNBUFFERED=1

RUN python -m pip install --no-cache-dir numpy pandas matplotlib pydantic

# 受控内部构建才允许 copy COMSOL，本文件不应包含 license
RUN mkdir -p /opt/comsol/COMSOL64
COPY --from=comsol / ${COMSOL_ROOT}/

RUN rm -f \
  ${COMSOL_ROOT}/license/license.dat \
  ${COMSOL_ROOT}/license/license.trial \
  ${COMSOL_ROOT}/licenseinfo.ini \
  || true

WORKDIR /workspace/optics_agent
CMD ["python", "--version"]
```

注意：

- 镜像标签应优先推到 GU 站可快速拉取的 registry。
- 若 COMSOL 不能入镜像，则做 Python-only fallback 并通过 runner 挂载 COMSOL。
- 不在镜像里放 optics_agent 源码；源码通过 Git 或挂载提供。

### 5.4 Magnus 注册与运行脚本

参考 `scripts/register_magnus_blueprints.py`，在 optics-agent 增加：

```text
comsol/scripts/register_magnus_blueprints.py
```

功能：

```bash
python comsol/scripts/register_magnus_blueprints.py --dry-run
python comsol/scripts/register_magnus_blueprints.py --address <MAGNUS_ADDRESS>
```

要求：

- 默认读 `comsol/blueprints/source/*.yaml`。
- 只从环境变量读取 `MAGNUS_TOKEN`。
- 支持 `/api/blueprints` 注册。
- 输出 verify 命令。

---

## 6. Skill 系统集成建议

### 6.1 `optics-comsol-environment` skill

用途：给人/agent 看的一份环境 runbook，不自动安装软件。

应包含：

- COMSOL 安装/挂载位置约定：`COMSOL_ROOT`。
- license 提供方式：`COMSOL_LICENSE_FILE` / `LM_LICENSE_FILE` / 机构 license server。
- 如何验证：
  - `comsol -version`
  - `comsol batch -help`
  - 跑 smoke case
- Magnus runner 要求：
  - 仓库挂载到 `/workspace/optics_agent`
  - COMSOL runtime image 可拉取
  - `/tmp/optics_comsol_run` 可写
- 常见错误分类：license、挂载、镜像、COMSOL 模块缺失、solver 失败。

### 6.2 `optics-comsol-agent` skill

用途：描述 agent 如何从光学仿真需求调用 COMSOL runner。

应包含：

1. 将用户需求解析为 `optical_case.json`。
2. 选择模板：waveguide / grating / metasurface / cavity 等。
3. 本地先做 schema validation。
4. Phase A 可本地 runner；Phase B 优先 Magnus 蓝图。
5. 读取 manifest 和 metrics，不凭 stdout 猜测成功。
6. 对失败做最小调整并记录 rerun manifest。
7. 输出短摘要 + artifact 路径。

不要在 skill 中写当前日期/时间等实时变量，避免破坏缓存命中。

---

## 7. 分阶段实施计划

### Stage 0：参考项目裁剪与需求冻结（0.5 天）

交付物：

- 本文档。
- 确认 optics-agent 第一版 COMSOL smoke 模型类型。
- 确认 GU/Magnus 上是否已有 COMSOL、license、runtime image 或挂载方式。

决策点：

- 如果 GU 站无 COMSOL license，Phase B 只能做到蓝图和环境检查，不能完成求解验收。
- 如果 COMSOL 可入受控镜像，则优先 image；否则走挂载 COMSOL_ROOT。

### Stage 1：Phase A 最小 batch runner（1-2 天）

新增文件：

```text
optics_agent/comsol/runners/comsol_batch_runner.py
optics_agent/comsol/cases/smoke_waveguide_case.json
optics_agent/comsol/templates/smoke_2d_waveguide.java
optics_agent/comsol/scripts/run_comsol_smoke.py
```

任务：

1. 写 case schema 和 smoke case。
2. 准备 Java 模板或 `.mph` 模板。
3. 实现 batch runner：环境检查、命令构造、超时、日志、manifest。
4. 在本地有 COMSOL 的环境跑通；若本地没有，至少跑通 `--dry-run` 和环境失败分类。

验收：

```bash
python comsol/scripts/run_comsol_smoke.py --dry-run
python comsol/scripts/run_comsol_smoke.py --run-dir runs/comsol/smoke
```

成功后 manifest 中：

```json
{"status":"completed", "checks":{"output_mph_exists":true}}
```

### Stage 2：结果导出与光学 sanity check（1-2 天）

新增/完善：

```text
optics_agent/comsol/runners/collect_outputs.py
optics_agent/comsol/results schema
```

任务：

1. 从 COMSOL 导出 CSV/数值指标。
2. 定义最小 optical sanity：例如 S 参数范围、有效折射率范围、能量非负、场图存在。
3. 将 sanity 写入 manifest 的 `checks.physics_sanity_ok`。
4. 出错时写 `errors/failure.json`。

验收：

- 结果 CSV/metrics 存在。
- 非物理或导出缺失能被结构化分类。

### Stage 3：Phase B Magnus smoke 蓝图（1 天）

新增文件：

```text
optics_agent/comsol/blueprints/source/optics-comsol-headless-smoke.yaml
optics_agent/comsol/scripts/register_magnus_blueprints.py
```

任务：

1. 写 smoke 蓝图。
2. 注册 dry-run。
3. 在 Magnus 提交 smoke job。
4. `$MAGNUS_RESULT` 回写 manifest。

验收：

```bash
python comsol/scripts/register_magnus_blueprints.py --dry-run
magnus run optics-comsol-headless-smoke
magnus job result <job-id>
```

### Stage 4：容器/runtime 固化（1-2 天）

新增文件：

```text
optics_agent/comsol/docker/comsol-runtime.Containerfile
optics_agent/comsol/docs/plans/comsol_environment_runbook.md
```

任务：

1. 构建受控 COMSOL runtime image 或 Python-only fallback。
2. 推送到 GU 可拉取 registry。
3. 写清 license runtime mount 方式。
4. 跑容器 smoke。

验收：

- runner 能拉镜像。
- 容器中 `comsol batch` 可执行。
- 不含 license 文件和 token。

### Stage 5：正式 case-run 蓝图与 skill（2-3 天）

新增文件：

```text
optics_agent/comsol/blueprints/source/optics-comsol-case-run.yaml
optics_agent/skills/optics-comsol-agent/SKILL.md
optics_agent/skills/optics-comsol-environment/SKILL.md
```

任务：

1. 支持任意 `case_file`。
2. 支持参数扫：多个 case 或 sweep JSON。
3. skill 描述 agent 如何调用、如何判断失败、如何读取 artifacts。
4. 形成标准用户入口。

验收：

- 用户只给 case JSON 或自然语言工况，agent 能生成 case 并提交蓝图。
- manifest、metrics、log、mph 都可定位。

---

## 8. 推荐第一批代码组织细节

### 8.1 runner 命令行接口

```bash
python comsol/runners/comsol_batch_runner.py \
  --case comsol/cases/smoke_waveguide_case.json \
  --run-dir runs/comsol/smoke_waveguide_001 \
  --backend batch_java \
  --cores 4 \
  --timeout-s 1800
```

可选：

```bash
--dry-run              # 只检查环境和打印命令，不执行 COMSOL
--strict-artifacts     # 缺任何声明 artifact 即失败
--allow-missing-comsol # 仅用于 CI schema 测试
```

### 8.2 Python 包结构

```text
comsol/runners/
├── __init__.py
├── env.py              # find_comsol_bin, version, license hints
├── schema.py           # load/validate case
├── command.py          # build batch command
├── manifest.py         # write/update manifest
├── runner.py           # ComsolBatchRunner
└── cli.py              # argparse
```

第一版也可以单文件实现，但尽量保持函数边界清楚，后续再拆分。

### 8.3 日志处理

runner 应记录：

- 完整命令写入 `command.json`。
- stdout/stderr 分别写 `raw/stdout.txt`、`raw/stderr.txt`。
- COMSOL batch log 写 `raw/comsol.log`。
- 日志扫描关键词：
  - `License error`
  - `Could not obtain license`
  - `Out of memory`
  - `Failed to solve`
  - `Undefined variable`
  - `Segmentation fault`

不要把完整超长日志直接发到聊天；长日志只保存在文件中。

---

## 9. 与当前 optics-agent / GU-Magnus 规范的对齐

当前项目已有本地 ↔ Gustation 规范：PC 写代码/构建镜像，GU 站跑 Magnus job。COMSOL headless 应遵守同样拓扑：

```text
本地 PC
  - 写 runner / templates / blueprints / skills
  - 构建或准备 COMSOL runtime image
  - 注册蓝图、提交 job

Gustation / Magnus
  - 拉取镜像
  - 挂载仓库或从 GitHub 获取代码
  - 提供 COMSOL_ROOT/license
  - 执行 comsolbatch
  - 返回 manifest / artifacts
```

注意：

- 不在 GU 站临时安装开发环境。
- 代码修改后先 commit/push，再提交依赖新代码的 Magnus job。
- Magnus API 使用 `/api/jobs`、`/api/blueprints` 等当前站点约定。
- token 从 `project/secret.json` 或环境变量读，不写入代码和文档。

---

## 10. 最小验收清单

Phase A 完成需要：

- [ ] `comsol_batch_runner.py --dry-run` 能输出命令和环境报告。
- [ ] 无 COMSOL 时失败分类为 `env.comsol_bin_missing`，不是裸异常。
- [ ] 有 COMSOL 时 smoke case 生成 `.mph`、`comsol.log`、`manifest.json`。
- [ ] manifest 能描述成功/失败、artifact、检查项和耗时。
- [ ] 长日志不进入聊天，只保存文件。

Phase B 完成需要：

- [ ] `optics-comsol-headless-smoke.yaml` 可注册。
- [ ] Magnus job 能执行 Phase A runner。
- [ ] `$MAGNUS_RESULT` 返回 manifest 内容。
- [ ] runner 挂载/镜像/license/求解失败可区分。
- [ ] 许可证、token、个人路径不进入 Git、镜像、skill。

---

## 11. 建议立即执行的下一步

1. 确认第一版 optical smoke 模型：建议选一个最小 2D waveguide / frequency-domain 模型。
2. 从 COMSOL GUI 导出 Java 模板，放入 `optics_agent/comsol/templates/`。
3. 编写 `comsol_batch_runner.py`，优先支持 `batch_java`。
4. 写 smoke case JSON 与 manifest schema。
5. 本地或 GU 环境跑 `--dry-run`，确认路径、命令和失败分类。
6. 再写 Magnus smoke 蓝图，不要先上复杂扫参。

总体原则：先把“非 GUI 可控调用 + artifact 契约 + Magnus 回传”做稳，再谈复杂光学模型和自动调参。
