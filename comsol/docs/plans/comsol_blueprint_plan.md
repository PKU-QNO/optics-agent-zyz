# COMSOL `comsolbatch` 蓝图化深化计划

## 0. 结论

针对 optics-agent 的核心任务——**让 agent 复刻前沿光学论文，并把复杂数值计算流程转成 Magnus 蓝图执行**——COMSOL 封装应采用：

> **Agent 生成/整理 COMSOL 主脚本与输入文件 → Magnus Blueprint 调用 `comsol batch` 执行 → 输出 `.mph`、日志、导出数据和 manifest → Agent 读取 artifact 做分析/迭代。**

因此，当前阶段不应主推交互式 `mphserver`。最终目标结构分成 3 个长期稳定组件：

1. **GU `/data/` 长期存储上的 COMSOL 主文件夹**：保存论文级 case、COMSOL Java/M-file/.mph 模板、运行记录和 artifact。
2. **Magnus `.magnus` 蓝图**：只负责任务参数、资源、镜像、挂载、调用 `comsolbatch` 和结果回收。
3. **LobeHub/Claude `SKILL.md` 技能包**：告诉 agent 如何生成 COMSOL 脚本、如何调用蓝图、如何检查结果、如何迭代失败。

---

## 1. 为什么选择 `comsolbatch`

### 1.1 方案对比

| 方案 | 适配论文复刻 | 适配 Magnus Job | 复杂计算稳定性 | 开发复杂度 | 结论 |
|---|---:|---:|---:|---:|---|
| `comsol batch` / `comsolbatch` | 高 | 最高 | 高 | 中 | **主方案** |
| Java API 直接程序化建模 | 高 | 中 | 中-高 | 高 | 作为 agent 生成 `.java` 的模型表达方式，不单独作为执行后端 |
| Python `mph` + `mphserver` | 中 | 低 | 中 | 高 | 只作为本地调试/多 case service 复用备选 |
| COMSOL Server App | 低-中 | 中 | 高 | 高且 license 要求高 | 不适合当前 agent 蓝图化主线 |

### 1.2 对我们的实际工作流

我们的工作流不是人工在 GUI 里反复调参，而是：

```text
论文 → agent 理解模型 → agent 写 COMSOL Java/M-file/参数 JSON
  → Magnus 蓝图提交大资源 batch job
  → GU 站 headless 求解
  → 返回 .mph/log/csv/png/manifest
  → agent 检查结果并决定是否修正脚本或进入下一阶段
```

这与 `comsol batch -inputfile ... -outputfile ... -batchlog ...` 完全匹配。

### 1.3 `comsolbatch` 的关键优点

- **无交互**：不需要 GUI、不需要 socket、不需要长驻 server。
- **适合复杂长任务**：Magnus/SLURM 管理进程生命周期、超时、资源和日志。
- **artifact 清晰**：`.mph`、`comsol.log`、CSV/PNG/export、`manifest.json` 可标准回收。
- **失败可结构化**：退出码 + batchlog + 缺失文件检查足够构建 failure manifest。
- **蓝图简单**：蓝图只需组合命令，不承载模型逻辑。

---

## 2. 最终目标结构一：GU `/data/` 上的 COMSOL 主文件夹

### 2.1 设计原则

COMSOL 论文复刻的核心资产不应散落在临时 job 目录，而应沉淀到 GU 站 `/data/` 持久存储。

建议路径：

```text
/data/zhangyuanzheng/optics_agent/comsol/
```

或更通用：

```text
/data/$USER/optics_agent/comsol/
```

### 2.2 目录结构

```text
/data/$USER/optics_agent/comsol/
├── README.md
├── env/
│   ├── comsol_env_report.json             # validate_comsol_env 生成，不含 license 秘密值
│   └── available_modules.json             # 记录可用 COMSOL modules，如 Wave Optics/RF 等
├── templates/
│   ├── smoke_2d_waveguide/
│   │   ├── model.java                     # 最小 waveguide smoke 模板
│   │   ├── case.default.json
│   │   └── README.md
│   └── paper_template_base/
│       ├── model.java
│       ├── model.mph                      # 如 license/内部策略允许保存
│       └── README.md
├── papers/
│   └── <paper_slug>/
│       ├── paper_context.md               # agent 提炼的论文数值复现实验说明
│       ├── cases/
│       │   ├── case_001.json
│       │   ├── case_002.json
│       │   └── sweep_001.json
│       ├── scripts/
│       │   ├── model_case_001.java
│       │   ├── model_case_002.java
│       │   └── postprocess.py
│       ├── runs/
│       │   └── <run_id>/
│       │       ├── manifest.json
│       │       ├── input_case.json
│       │       ├── command.json
│       │       ├── raw/
│       │       │   ├── model_input.java
│       │       │   ├── model_output.mph
│       │       │   └── comsol.log
│       │       ├── results/
│       │       │   ├── metrics.json
│       │       │   ├── tables/*.csv
│       │       │   └── figures/*.png
│       │       └── errors/failure.json
│       └── reports/
│           ├── reproduction_status.md
│           └── numerical_findings.md
└── shared/
    ├── runners/
    │   ├── comsol_batch_runner.py
    │   ├── collect_outputs.py
    │   └── validate_comsol_env.py
    └── schemas/
        ├── optical_case.schema.json
        └── run_manifest.schema.json
```

### 2.3 主文件夹职责

| 子目录 | 职责 |
|---|---|
| `templates/` | 保存可复用 COMSOL 模板，尤其是 smoke 和常见光学几何模板 |
| `papers/<paper_slug>/cases/` | 保存论文复刻的参数化输入，不含 token/license |
| `papers/<paper_slug>/scripts/` | 保存 agent 生成或从模板渲染出的 COMSOL Java/M-file |
| `papers/<paper_slug>/runs/` | 每次 Magnus Job 的标准 artifact 输出 |
| `shared/runners/` | 可被多个论文复用的 runner 脚本 |
| `shared/schemas/` | 输入/输出契约 |

### 2.4 路径策略

- **本地 repo**：负责开发 runner、schema、skill、blueprint。
- **GU `/data/`**：负责长期保存大文件、`.mph` 输出、论文运行历史。
- **Magnus Job 临时目录**：只做执行工作区，结束后同步/拷贝到 `/data/`。

---

## 3. 最终目标结构二：Magnus `.magnus` 蓝图

### 3.1 蓝图定位

蓝图不写 COMSOL 物理逻辑，只做以下事情：

1. 接收论文 case 参数或 case 文件路径。
2. 准备工作目录。
3. 检查 COMSOL 可执行文件与 license 环境。
4. 调用 `comsol batch`。
5. 调用 `collect_outputs.py` 生成 manifest。
6. 将 manifest 摘要写入 `$MAGNUS_RESULT`。
7. 将重要 artifact 打包并写入 `$MAGNUS_ACTION` 下载命令。

### 3.2 建议蓝图文件位置

本地：

```text
C:\Users\27370\Desktop\project\optics_agent\comsol\blueprints\source\Optics_COMSOL_Batch_zyz.magnus.py
```

蓝图 ID 约定：

```text
Optics_COMSOL_Batch_zyz
```

### 3.3 `.magnus` 参数设计

参考 `OpenFundus_SFT_zyz.magnus` 风格，使用 `typing.Annotated` 定义参数 schema。

核心参数：

```python
from typing import Annotated, Optional, Literal

PaperSlug = Annotated[str, {
    "label": "论文 slug",
    "description": "用于 /data/$USER/optics_agent/comsol/papers/<paper_slug>/ 下组织运行结果",
    "placeholder": "mzi_topology_2026",
    "allow_empty": False,
}]

CasePath = Annotated[str, {
    "label": "case JSON 路径",
    "description": "GU /data 上的 case JSON，或仓库内相对路径",
    "placeholder": "/data/$USER/optics_agent/comsol/papers/<paper_slug>/cases/case_001.json",
    "allow_empty": False,
}]

InputFile = Annotated[str, {
    "label": "COMSOL 输入文件",
    "description": "COMSOL Java/M-file/.mph 输入文件路径；一般由 agent 生成到 /data 主文件夹",
    "placeholder": "/data/$USER/optics_agent/comsol/papers/<paper_slug>/scripts/model_case_001.java",
    "allow_empty": False,
}]

OutputRoot = Annotated[str, {
    "label": "输出根目录",
    "description": "持久输出目录，默认 /data/$USER/optics_agent/comsol/papers/<paper_slug>/runs",
    "placeholder": "/data/$USER/optics_agent/comsol/papers/<paper_slug>/runs",
}]

ComsolCommand = Annotated[str, {
    "label": "COMSOL 命令",
    "description": "comsol 可执行命令；可为 comsol、comsolbatch 或绝对路径",
    "default": "comsol",
}]

InputMode = Annotated[Literal["java", "mph", "mfile"], {
    "label": "输入类型",
    "options": {
        "java": "COMSOL Java API 文件",
        "mph": "已有 MPH 模型模板",
        "mfile": "COMSOL MATLAB/M-file",
    },
    "default": "java",
}]

Cores = Annotated[int, {
    "label": "CPU 核心数",
    "min": 1,
    "max": 64,
    "default": 8,
}]

MemoryDemand = Annotated[str, {
    "label": "内存需求",
    "description": "带单位，例如 16G、64G、128G、256G",
    "default": "64G",
}]

EphemeralStorage = Annotated[str, {
    "label": "临时存储",
    "description": "用于 COMSOL 临时文件和中间导出",
    "default": "100G",
}]

Priority = Annotated[Literal["A1", "A2", "B1", "B2"], {
    "label": "优先级",
    "default": "B2",
}]

ContainerImage = Annotated[Optional[str], {
    "label": "容器镜像",
    "description": "包含 COMSOL runtime 或能挂载 COMSOL 的镜像；留空用默认",
    "placeholder": "docker://registry/comsol-optics-runtime:6.4",
}]

ExecuteAction = Annotated[bool, {
    "label": "自动下载 artifact",
    "default": True,
}]
```

### 3.4 蓝图主函数骨架

```python
def blueprint(
    paper_slug: PaperSlug,
    case_path: CasePath,
    input_file: InputFile,
    output_root: OutputRoot = "",
    comsol_command: ComsolCommand = "comsol",
    input_mode: InputMode = "java",
    cores: Cores = 8,
    memory_demand: MemoryDemand = "64G",
    ephemeral_storage: EphemeralStorage = "100G",
    priority: Priority = "B2",
    container_image: ContainerImage = None,
    execute_action: ExecuteAction = True,
):
    if not output_root:
        output_root = f"/data/$USER/optics_agent/comsol/papers/{paper_slug}/runs"

    task_name = f"optics-comsol-{paper_slug}"

    entry_command = f'''
set -e
_log() {{ echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }}

export PYTHONUNBUFFERED=1
export OMP_NUM_THREADS={cores}
export COMSOL_NUM_THREADS={cores}

RUN_ID="$(date +%Y%m%d-%H%M%S)-$MAGNUS_JOB_ID"
OUTPUT_ROOT="{output_root}"
RUN_DIR="$OUTPUT_ROOT/$RUN_ID"
mkdir -p "$RUN_DIR" "$RUN_DIR/raw" "$RUN_DIR/results" "$RUN_DIR/errors" "$RUN_DIR/progress"

_log "[1/5] 环境检查"
which {comsol_command} || true
{comsol_command} -version || true

_log "[2/5] 复制输入"
cp "{case_path}" "$RUN_DIR/input_case.json"
cp "{input_file}" "$RUN_DIR/raw/model_input.{input_mode}"

_log "[3/5] 执行 COMSOL batch"
set +e
{comsol_command} batch \
  -inputfile "$RUN_DIR/raw/model_input.{input_mode}" \
  -outputfile "$RUN_DIR/raw/model_output.mph" \
  -batchlog "$RUN_DIR/raw/comsol.log" \
  -np {cores}
EXIT_CODE=$?
set -e

_log "[4/5] 生成 manifest"
python3 /workspace/optics_agent/comsol/runners/collect_outputs.py \
  --run-dir "$RUN_DIR" \
  --case-id "{paper_slug}" \
  --backend "comsolbatch_{input_mode}" \
  --exit-code "$EXIT_CODE"

_log "[5/5] 回写 Magnus 结果"
python3 - <<'PY'
import json, os
run_dir = os.environ['RUN_DIR']
manifest_path = os.path.join(run_dir, 'manifest.json')
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)
with open(os.environ['MAGNUS_RESULT'], 'w', encoding='utf-8') as f:
    json.dump({
        'status': manifest.get('status'),
        'run_dir': run_dir,
        'manifest': manifest_path,
        'output_mph': manifest.get('artifacts', {}).get('output_mph'),
        'batch_log': manifest.get('artifacts', {}).get('batch_log'),
        'failure': manifest.get('failure'),
    }, f, ensure_ascii=False)
PY

# 打包重要 artifact，供本地可选下载
cd "$RUN_DIR"
tar -czf "$RUN_DIR/artifacts.tgz" manifest.json input_case.json command.json raw/comsol.log results errors 2>/dev/null || true
SECRET=$(magnus custody "$RUN_DIR/artifacts.tgz" --expire-minutes 1440 2>/dev/null || true)
if [ -n "$SECRET" ]; then
  echo "magnus receive $SECRET -o ./comsol_artifacts_$RUN_ID.tgz" > "$MAGNUS_ACTION"
fi

exit "$EXIT_CODE"
'''

    submit_job(
        task_name=task_name,
        entry_command=entry_command,
        repo_name="optics-agent",          # 后续按真实仓库名修改
        namespace="Rise-AGI",             # 后续按真实 namespace 修改
        branch="main",                    # 后续由提交脚本注入
        commit_sha="",                    # 推荐由提交脚本注入当前 commit
        gpu_type="cpu",
        gpu_count=0,
        cpu_count=cores,
        memory_demand=memory_demand,
        ephemeral_storage=ephemeral_storage,
        job_type=priority,
        container_image=container_image,
        system_entry_command="",           # 如需挂载 /data，按 magnus-platform 规范填入
        description=f"COMSOL batch reproduction for {paper_slug}",
    )
```

> 注：实际 `.magnus` 受沙箱限制，不能在蓝图函数中 `import os/subprocess/open`；但可以拼接 `entry_command` 字符串，并调用 `submit_job(...)`。上面骨架保持这个原则。

### 3.5 蓝图不应做的事

- 不在蓝图里写具体 COMSOL 几何、材料、边界条件。
- 不在蓝图里硬编码 license server/token。
- 不在蓝图里读论文或推理物理模型。
- 不把复杂后处理逻辑写进 shell 字符串；复杂逻辑放 `collect_outputs.py` 或论文目录 `postprocess.py`。

---

## 4. 最终目标结构三：COMSOL Skill 技能包

### 4.1 技能包位置

参考 `magnus-platform` 的标准结构：

```text
C:\Users\27370\Desktop\project\.claude\skills\optics-comsol-batch/
├── SKILL.md
├── references/
│   ├── comsol_batch.md
│   ├── artifact_contract.md
│   ├── optical_case_schema.md
│   ├── magnus_blueprint_usage.md
│   └── failure_modes.md
└── scripts/
    ├── validate_comsol_env.py
    ├── render_case_template.py
    └── inspect_manifest.py
```

### 4.2 `SKILL.md` 内容框架

```markdown
---
name: optics-comsol-batch
description: 使用 COMSOL batch/headless 复刻光学论文数值计算，并通过 Magnus 蓝图提交复杂仿真任务。用户提及 COMSOL、光学仿真、论文复刻、Magnus 蓝图、headless simulation 时使用。
---

# Optics COMSOL Batch Skill

## 使用边界
- 主后端：`comsol batch`
- 不使用 GUI
- 不默认使用 `mphserver`
- license/token 不写入代码或文档

## 标准流程
1. 阅读论文数值计算部分
2. 提取物理模型、几何、材料、边界、网格、solver、输出指标
3. 生成 `case.json`
4. 生成或修改 COMSOL `model.java` / `.mph` 模板
5. 保存到 `/data/$USER/optics_agent/comsol/papers/<paper_slug>/`
6. 调用 `Optics_COMSOL_Batch_zyz` 蓝图
7. 读取 manifest/log/result
8. 如果失败，按 failure_modes 分类修正
9. 如果成功，输出复现报告和下一轮参数扫描计划

## Artifact Contract
- 每次运行必须有 `manifest.json`
- 成功必须有 `.mph` 或明确说明无需保存 `.mph`
- 失败必须有 `errors/failure.json`
- 所有路径写入 manifest

## 失败处理
- `COMSOL_NOT_FOUND`
- `LICENSE_UNAVAILABLE`
- `BATCH_EXIT_NONZERO`
- `OUTPUT_MPH_MISSING`
- `EXPORT_MISSING`
- `OOM_OR_RESOURCE_LIMIT`
- `TIMEOUT`
- `PHYSICS_SANITY_FAILED`
```

### 4.3 references 文件职责

| 文件 | 内容 |
|---|---|
| `comsol_batch.md` | `comsol batch` 命令格式、Java/M-file/.mph 输入差异、常用参数 |
| `artifact_contract.md` | `manifest.json`、`failure.json`、目录结构、结果表/图规范 |
| `optical_case_schema.md` | 论文 case JSON 字段：几何、材料、物理场、solver、export |
| `magnus_blueprint_usage.md` | 如何调用 `Optics_COMSOL_Batch_zyz`、参数说明、资源建议 |
| `failure_modes.md` | 失败类型、日志关键词、修复建议 |

### 4.4 scripts 文件职责

这些脚本是本地/远程都可复用的小工具，不是大型业务逻辑：

| 脚本 | 职责 |
|---|---|
| `validate_comsol_env.py` | 检查 `comsol` 命令、版本、license 变量、可用模块 |
| `render_case_template.py` | 从 `case.json` 渲染 Java 模板，避免 agent 手写重复路径 |
| `inspect_manifest.py` | 读取 manifest/failure，给 agent 返回结构化摘要 |

---

## 5. 三组件之间的数据流

```text
[Agent / Skill]
  读取论文 → 生成 case.json + model.java
          ↓ 写入
[/data/$USER/optics_agent/comsol/papers/<paper_slug>/]
          ↓ 参数传给
[Magnus Blueprint: Optics_COMSOL_Batch_zyz]
          ↓ submit_job
[GU 容器 Job]
  comsol batch -inputfile model.java -outputfile model_output.mph -batchlog comsol.log
          ↓ 写入
[/data/.../runs/<run_id>/manifest.json + artifacts]
          ↓ 返回
[Agent]
  inspect_manifest → 分析结果/修正模型/生成报告/下一轮 sweep
```

---

## 6. 分阶段实施计划

### Stage 0：确认环境与 license

目标：先确认 GU 站 COMSOL 能否 batch 跑。

产出：

```text
optics_agent/comsol/scripts/validate_comsol_env.py
/data/$USER/optics_agent/comsol/env/comsol_env_report.json
```

检查项：

- `which comsol`
- `comsol -version`
- license 环境变量是否存在：`LM_LICENSE_FILE` / `COMSOL_LICENSE_FILE`
- 是否能运行极小 `comsol batch` smoke。

### Stage 1：本地/远程通用 runner

产出：

```text
optics_agent/comsol/runners/comsol_batch_runner.py
optics_agent/comsol/runners/collect_outputs.py
optics_agent/comsol/schemas/run_manifest.schema.json
optics_agent/comsol/cases/smoke_waveguide_case.json
```

目标：即使没有 COMSOL，也能结构化失败；有 COMSOL 时生成标准 artifact。

### Stage 2：Magnus 蓝图

产出：

```text
optics_agent/comsol/blueprints/source/Optics_COMSOL_Batch_zyz.magnus.py
```

目标：使用 Magnus 提交 COMSOL batch job。

资源默认建议：

| 任务类型 | CPU | 内存 | 临时盘 | 优先级 |
|---|---:|---:|---:|---|
| smoke | 4 | 16G | 20G | B2 |
| 小型 2D 光学 | 8-16 | 32-64G | 50-100G | B2/B1 |
| 大型 3D / 参数扫描 | 32 | 128-256G | 200-500G | B1，超过红线需确认 |

注意：按当前群组规则，使用 **>32 核或 >250G RAM 或 GPU** 前需要用户审批。

### Stage 3：Skill 化

产出：

```text
.claude/skills/optics-comsol-batch/SKILL.md
.claude/skills/optics-comsol-batch/references/*.md
.claude/skills/optics-comsol-batch/scripts/*.py
```

目标：任何 agent 接到 COMSOL 论文复刻任务时，都按同一流程生成脚本、调用蓝图、检查结果。

### Stage 4：论文级自迭代

目标：使 agent 能根据 manifest/log 自动判断下一步。

典型循环：

```text
运行失败 → inspect_manifest → 归类 failure → 修改 model.java/case.json → 再提交
运行成功但 sanity 失败 → 修改参数/网格/边界 → 再提交
运行成功 → 生成复现报告 → 设计参数 sweep 蓝图
```

---

## 7. 首个可执行目标

建议第一个最小可执行目标不是复杂论文，而是：

```text
2D waveguide / slab waveguide smoke
```

要求：

1. Agent 生成一个最小 `model.java`。
2. 蓝图调用 `comsol batch` 求解。
3. 输出 `.mph`、`comsol.log`、一个 CSV 表、一个 PNG 图。
4. `manifest.json` 标记 completed。
5. 若 COMSOL/license 不可用，`manifest.json` 标记 failed 且 `failure.code` 清楚。

---

## 8. 当前应创建的文件清单

第一轮建议创建：

```text
optics_agent/comsol/README.md
optics_agent/comsol/runners/comsol_batch_runner.py
optics_agent/comsol/runners/collect_outputs.py
optics_agent/comsol/scripts/validate_comsol_env.py
optics_agent/comsol/cases/smoke_waveguide_case.json
optics_agent/comsol/schemas/run_manifest.schema.json
optics_agent/comsol/blueprints/source/Optics_COMSOL_Batch_zyz.magnus.py
.claude/skills/optics-comsol-batch/SKILL.md
.claude/skills/optics-comsol-batch/references/comsol_batch.md
.claude/skills/optics-comsol-batch/references/artifact_contract.md
.claude/skills/optics-comsol-batch/references/magnus_blueprint_usage.md
.claude/skills/optics-comsol-batch/references/failure_modes.md
```

如果要进一步压缩，最小 MVP 是：

```text
optics_agent/comsol/runners/comsol_batch_runner.py
optics_agent/comsol/runners/collect_outputs.py
optics_agent/comsol/cases/smoke_waveguide_case.json
optics_agent/comsol/blueprints/source/Optics_COMSOL_Batch_zyz.magnus.py
.claude/skills/optics-comsol-batch/SKILL.md
```

---

## 9. 关键设计约束

- COMSOL license/server/token 不写入 repo、蓝图、skill。
- 蓝图不直接写复杂物理逻辑，只调用脚本。
- `.mph` 大文件留在 `/data/`，本地只下载摘要 artifact 或按需 custody。
- 所有失败都进入 `manifest.json` 和 `errors/failure.json`。
- 真实论文复刻前必须先 smoke。
- 对大资源 job，必须先查重，避免重复 Pending/Running job。
- 严格串行 agent 调用，避免向量数据库崩溃。
