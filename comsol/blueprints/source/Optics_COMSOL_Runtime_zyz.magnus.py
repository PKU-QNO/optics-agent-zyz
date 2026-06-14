# Magnus 蓝图: Optics_COMSOL_Runtime_zyz
# 公开蓝图故意保持精简。实际运行逻辑放在服务器侧目录:
# /data/public/zhangyuanzheng/comsol-runtime.

from typing import Annotated, Optional, Literal


RunMode = Annotated[Literal["env_check", "batch_java", "batch_mph", "batch_mfile"], {
    "label": "运行模式",
    "description": "env_check 只检查镜像和环境；batch_* 模式会通过服务器侧 runner 调用 comsol batch。",
    "default": "env_check",
}]

DomainPreset = Annotated[Literal["optics", "fluid", "generic"], {
    "label": "领域预设",
    "description": "给后续 agent 使用的任务领域提示：光学、流体或通用。",
    "default": "generic",
}]

CodeRoot = Annotated[str, {
    "label": "服务器代码目录",
    "description": "管理员已放置的 COMSOL runtime 代码目录，包含 comsol_runner.py。",
    "placeholder": "/data/public/zhangyuanzheng/comsol-runtime",
}]

LicenseMode = Annotated[Literal["personal_storage", "server_env", "file_secret", "env_check_only"], {
    "label": "许可证模式",
    "description": "server_env 使用已验证的 /opt/comsol-license 挂载；personal_storage 读取 license_path；env_check_only 不做正式求解。",
    "default": "server_env",
}]

LicensePath = Annotated[str, {
    "label": "许可证路径",
    "description": "容器内的 COMSOL license 路径。默认使用管理员提供的挂载许可证。",
    "placeholder": "/opt/comsol-license/license.dat",
}]

InputFile = Annotated[Optional[str], {
    "label": "输入文件",
    "description": "持久存储中的 COMSOL 输入文件，用于 batch_java、batch_mph 或 batch_mfile。",
    "placeholder": "/home/magnus/data/optics_agent/comsol/papers/demo/model.java",
}]

CasePath = Annotated[Optional[str], {
    "label": "案例目录",
    "description": "可选的持久案例目录，适合放模型、参数、网格和后处理脚本。",
    "placeholder": "/home/magnus/data/optics_agent/comsol/papers/demo",
}]

CaseBundleSecret = Annotated[Optional[str], {
    "label": "临时案例包密钥",
    "description": "可选的 Magnus FileSecret，用于上传 tar/tgz/zip 等临时案例包。",
    "placeholder": "magnus-secret:...",
}]

LicenseFileSecret = Annotated[Optional[str], {
    "label": "许可证文件密钥",
    "description": "仅在 license_mode=file_secret 时作为备用输入；常规运行优先使用服务器挂载许可证。",
    "placeholder": "magnus-secret:...",
}]

PostprocessFile = Annotated[Optional[str], {
    "label": "后处理脚本",
    "description": "可选的 Python 后处理脚本路径，脚本应位于已挂载的持久存储中。",
    "placeholder": "/home/magnus/data/optics_agent/comsol/papers/demo/postprocess.py",
}]

OutputRoot = Annotated[str, {
    "label": "输出根目录",
    "description": "持久化运行输出根目录；每次任务会在其下创建独立 run_id 子目录。",
    "placeholder": "/home/magnus/data/optics_agent/comsol/runs",
}]

RunId = Annotated[Optional[str], {
    "label": "运行 ID",
    "description": "留空时使用 $MAGNUS_JOB_ID 或时间戳自动生成。",
    "placeholder": "waveguide-smoke-001",
}]

ContainerImage = Annotated[str, {
    "label": "容器镜像",
    "description": "管理员已导入的 Magnus 本地镜像。不要在蓝图中刷新、拉取或替换该镜像。",
    "placeholder": "docker://magnus-local/comsol-runtime:latest",
}]

CpuCount = Annotated[int, {"label": "CPU 核心数", "min": 1, "max": 64, "default": 8}]
MemoryDemand = Annotated[str, {"label": "内存需求", "placeholder": "32G", "default": "32G"}]
EphemeralStorage = Annotated[str, {"label": "临时存储", "placeholder": "100G", "default": "100G"}]
Priority = Annotated[Literal["A1", "A2", "B1", "B2"], {"label": "任务优先级", "default": "B2"}]
ExecuteAction = Annotated[bool, {"label": "自动执行下载动作", "default": True}]
Runner = Annotated[Optional[str], {"label": "运行器", "placeholder": "留空则使用默认运行器"}]


def blueprint(
    run_mode: RunMode = "env_check",
    domain_preset: DomainPreset = "generic",
    code_root: CodeRoot = "/data/public/zhangyuanzheng/comsol-runtime",
    license_mode: LicenseMode = "server_env",
    license_path: LicensePath = "/opt/comsol-license/license.dat",
    input_file: InputFile = None,
    case_path: CasePath = None,
    case_bundle_secret: CaseBundleSecret = None,
    license_file_secret: LicenseFileSecret = None,
    postprocess_file: PostprocessFile = None,
    output_root: OutputRoot = "/home/magnus/data/optics_agent/comsol/runs",
    run_id: RunId = None,
    container_image: ContainerImage = "docker://magnus-local/comsol-runtime:latest",
    cpu_count: CpuCount = 8,
    memory_demand: MemoryDemand = "32G",
    ephemeral_storage: EphemeralStorage = "100G",
    priority: Priority = "B2",
    execute_action: ExecuteAction = True,
    runner: Runner = None,
):
    def q(value):
        if value is None:
            value = ""
        return "'" + str(value).replace("'", "'\"'\"'") + "'"

    entry_command = """#!/usr/bin/env bash
set -euo pipefail

RUN_MODE=__RUN_MODE__
DOMAIN_PRESET=__DOMAIN_PRESET__
CODE_ROOT_TEMPLATE=__CODE_ROOT__
LICENSE_MODE=__LICENSE_MODE__
LICENSE_PATH_TEMPLATE=__LICENSE_PATH__
INPUT_FILE=__INPUT_FILE__
CASE_PATH=__CASE_PATH__
CASE_BUNDLE_SECRET=__CASE_BUNDLE_SECRET__
LICENSE_FILE_SECRET=__LICENSE_FILE_SECRET__
POSTPROCESS_FILE=__POSTPROCESS_FILE__
OUTPUT_ROOT_TEMPLATE=__OUTPUT_ROOT__
RUN_ID=__RUN_ID__

USER_NAME="${USER:-magnus}"
CODE_ROOT="${CODE_ROOT_TEMPLATE//\\$USER/$USER_NAME}"
LICENSE_PATH="${LICENSE_PATH_TEMPLATE//\\$USER/$USER_NAME}"
OUTPUT_ROOT="${OUTPUT_ROOT_TEMPLATE//\\$USER/$USER_NAME}"
RUNTIME="$CODE_ROOT/comsol_runner.py"

if [ ! -f "$RUNTIME" ]; then
  msg="{\\"status\\":\\"failed\\",\\"failure\\":{\\"code\\":\\"RUNTIME_NOT_FOUND\\",\\"message\\":\\"Missing $RUNTIME. Stage comsol-runtime under /data/public/zhangyuanzheng first.\\"}}"
  echo "$msg"
  if [ -n "${MAGNUS_RESULT:-}" ]; then echo "$msg" > "$MAGNUS_RESULT"; fi
  exit 1
fi

args=(
  --run-mode "$RUN_MODE"
  --domain-preset "$DOMAIN_PRESET"
  --code-root "$CODE_ROOT"
  --license-mode "$LICENSE_MODE"
  --license-path "$LICENSE_PATH"
  --output-root "$OUTPUT_ROOT"
)

[ -n "$RUN_ID" ] && args+=(--run-id "$RUN_ID")
[ -n "$INPUT_FILE" ] && args+=(--input-file "$INPUT_FILE")
[ -n "$CASE_PATH" ] && args+=(--case-path "$CASE_PATH")
[ -n "$CASE_BUNDLE_SECRET" ] && args+=(--case-bundle-secret "$CASE_BUNDLE_SECRET")
[ -n "$LICENSE_FILE_SECRET" ] && args+=(--license-file-secret "$LICENSE_FILE_SECRET")
[ -n "$POSTPROCESS_FILE" ] && args+=(--postprocess-file "$POSTPROCESS_FILE")

python "$RUNTIME" "${args[@]}"
""".replace("__RUN_MODE__", q(run_mode)) \
        .replace("__DOMAIN_PRESET__", q(domain_preset)) \
        .replace("__CODE_ROOT__", q(code_root)) \
        .replace("__LICENSE_MODE__", q(license_mode)) \
        .replace("__LICENSE_PATH__", q(license_path)) \
        .replace("__INPUT_FILE__", q(input_file)) \
        .replace("__CASE_PATH__", q(case_path)) \
        .replace("__CASE_BUNDLE_SECRET__", q(case_bundle_secret)) \
        .replace("__LICENSE_FILE_SECRET__", q(license_file_secret)) \
        .replace("__POSTPROCESS_FILE__", q(postprocess_file)) \
        .replace("__OUTPUT_ROOT__", q(output_root)) \
        .replace("__RUN_ID__", q(run_id)) \
        .replace("\r\n", "\n")

    submit_job(
        task_name="COMSOL-" + (run_id if run_id else run_mode),
        description="精简 COMSOL runtime 启动器。实际逻辑和许可证保存在服务器私有/挂载存储中。",
        entry_command=entry_command,
        system_entry_command="""mounts=(
    "/data/public/zhangyuanzheng:/data/public/zhangyuanzheng"
    "/home/magnus/data:/home/magnus/data"
    "$HOME/.comsol-container-license:/opt/comsol-license"
)
export APPTAINER_BIND="${APPTAINER_BIND:+$APPTAINER_BIND,}$(IFS=,; echo "${mounts[*]}")"
export APPTAINERENV_LM_LICENSE_FILE=/opt/comsol-license/license.dat
export APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
export MAGNUS_HOME=/magnus
mkdir -p /home/magnus/data 2>/dev/null || true
unset VIRTUAL_ENV SSL_CERT_FILE
        """,
        namespace="Rise-AGI",
        repo_name="magnus",
        gpu_type="cpu",
        gpu_count=0,
        cpu_count=cpu_count,
        memory_demand=memory_demand,
        ephemeral_storage=ephemeral_storage,
        job_type=priority,
        execute_action=execute_action,
        runner=runner,
        container_image=container_image,
    )
