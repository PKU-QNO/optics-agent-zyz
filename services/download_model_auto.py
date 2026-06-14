#!/usr/bin/env python3
"""
Submit a Magnus GU CPU job that downloads DeepSeek-R1-Distill-Qwen-7B
from ModelScope into persistent storage under /data/.

This file is intentionally self-contained and does NOT import anything from
project/train/. It was adapted conceptually from the PHY-LLM helper script.

Usage:
    python download_model_auto.py

Credentials:
- GU address/token are read from C:\\Users\\27370\\Desktop\\project\\secret.json.
- The script intentionally fails fast if secret.json or required keys are missing.

IMPORTANT:
- This script only defines the submitter. Do not run it until you are ready
  to create a real Magnus job.
- The actual model download happens inside Magnus GU, not on the local machine.
- The download path defaults to /data/$USER/models/DeepSeek-R1-Distill-Qwen-7B.
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
from datetime import datetime

# ========== 用户配置 ==========
MODEL_ID = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
MODELSCOPE_MODEL_PATH = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"  # ModelScope 路径
SAVE_DIR = "/data/$USER/models/DeepSeek-R1-Distill-Qwen-7B"       # GU 站保存路径
# 从 secret.json 读取 GU 站凭据
_SECRET_PATH = r"C:\Users\27370\Desktop\project\secret.json"
with open(_SECRET_PATH, "r", encoding="utf-8") as _f:
    _secret = json.load(_f)
MAGNUS_ADDRESS = _secret["magnus_address-gu"]
MAGNUS_TOKEN = _secret["magnus_token-gu"]

# 任务硬件参数
JOB_TYPE = "B2"       # B2=CPU only
GPU_COUNT = 0
CPU_COUNT = 4
MEMORY_DEMAND = "16G"

# 仓库信息（用于 Magnus job）
NAMESPACE = "Rise-AGI"
REPO_NAME = "OpenFundus"
BRANCH = "main"
COMMIT_SHA = "HEAD"

# 下载重试
MAX_RETRIES = 3
RETRY_DELAY = 30  # 秒
# ========== 配置结束 ==========

# 进阶配置：一般无需修改
MODEL_REVISION = None
MAX_WORKERS = 8
EPHEMERAL_STORAGE = "200G"


def _mask_token(token: str) -> str:
    """Return a safe token preview for logs."""
    if not token:
        return "<empty>"
    if len(token) <= 12:
        return token[:2] + "***" + token[-2:]
    return token[:8] + "..." + token[-4:]


def _job_save_dir_expr(save_dir: str) -> str:
    """
    Convert SAVE_DIR into a shell expression evaluated inside the Magnus job.

    The configured SAVE_DIR intentionally supports /data/$USER/... so the
    remote GU job can resolve $USER for the account running the job.
    """
    return save_dir.replace("$USER", '"$USERNAME"')


def build_entry_command(
    *,
    modelscope_model_path: str,
    save_dir: str,
    max_retries: int,
    retry_delay: int,
    max_workers: int,
    revision: str | None,
) -> str:
    """
    Build the shell command executed inside the Magnus job.

    ModelScope snapshot_download supports local_dir-based resumable downloads:
    incomplete files and cache metadata are kept under the target/cache
    directories, so retries can continue instead of starting from scratch.
    """
    revision_arg = repr(revision) if revision else "None"
    save_dir_expr = _job_save_dir_expr(save_dir)

    return textwrap.dedent(
        fr"""
        set -euo pipefail

        echo "=== Magnus GU ModelScope download job ==="
        echo "time: $(date -Is)"
        echo "user: $(whoami)"

        # Keep all caches and final files under /data to avoid ephemeral storage limits.
        USERNAME="$(whoami)"
        SAVE_DIR={save_dir_expr}
        CACHE_DIR="/data/$USERNAME/.cache/modelscope"

        echo "model_id : {modelscope_model_path}"
        echo "save_dir : $SAVE_DIR"
        echo "cache_dir: $CACHE_DIR"

        mkdir -p "$SAVE_DIR" "$CACHE_DIR"
        export MODELSCOPE_CACHE="$CACHE_DIR"
        export HF_HOME="/data/$USERNAME/.cache/huggingface"
        export TRANSFORMERS_CACHE="$HF_HOME/transformers"
        export MODEL_SAVE_DIR="$SAVE_DIR"
        export PYTHONUNBUFFERED=1

        # If the model already appears complete, skip the expensive network step.
        if [ -f "$SAVE_DIR/config.json" ] && find "$SAVE_DIR" -maxdepth 1 -type f \( -name '*.safetensors' -o -name '*.bin' \) | grep -q .; then
            echo "[skip] model already exists and has weights: $SAVE_DIR"
            ls -lah "$SAVE_DIR"
            exit 0
        fi

        python3 -m pip install --no-cache-dir -q --upgrade pip
        python3 -m pip install --no-cache-dir -q modelscope

        echo "=== downloading with retry + resume semantics ==="
        python3 - <<'PY'
import os
import sys
import time
import traceback

from modelscope import snapshot_download

model_id = {modelscope_model_path!r}
local_dir = os.environ["MODEL_SAVE_DIR"]
revision = {revision_arg}
max_retries = {max_retries}
retry_delay = {retry_delay}
max_workers = {max_workers}

print(f"snapshot_download model_id={{model_id}}")
print(f"snapshot_download local_dir={{local_dir}}")
print(f"snapshot_download revision={{revision}}")

last_error = None
for attempt in range(1, max_retries + 1):
    try:
        kwargs = dict(
            model_id=model_id,
            local_dir=local_dir,
            max_workers=max_workers,
        )
        if revision:
            kwargs["revision"] = revision

        # Different ModelScope versions expose slightly different kwargs.
        # Try the more explicit resumable form first; fall back if unsupported.
        try:
            path = snapshot_download(**kwargs, resume_download=True)
        except TypeError:
            path = snapshot_download(**kwargs)

        print("download completed:", path)
        break
    except Exception as exc:  # noqa: BLE001 - keep retry diagnostics in job logs.
        last_error = exc
        print(f"[attempt {{attempt}}/{{max_retries}}] failed: {{exc}}", file=sys.stderr)
        traceback.print_exc()
        if attempt < max_retries:
            time.sleep(retry_delay * attempt)
else:
    print("download failed after retries", file=sys.stderr)
    raise last_error
PY

        echo "=== verifying downloaded files ==="
        if [ ! -f "$SAVE_DIR/config.json" ]; then
            echo "[error] missing config.json under $SAVE_DIR" >&2
            exit 2
        fi
        if ! find "$SAVE_DIR" -maxdepth 1 -type f \( -name '*.safetensors' -o -name '*.bin' \) | grep -q .; then
            echo "[error] missing model weight files under $SAVE_DIR" >&2
            exit 3
        fi

        echo "=== download done ==="
        du -sh "$SAVE_DIR" || true
        ls -lah "$SAVE_DIR" | sed -n '1,80p'
        """
    ).strip()


def submit_download_job() -> str:
    """
    Configure Magnus SDK and submit the download job.

    The Magnus SDK must be installed in the environment where this submitter is
    run. This function is deliberately not called by importers.
    """
    import magnus  # Imported lazily so static inspection does not require SDK.

    entry_command = build_entry_command(
        modelscope_model_path=MODELSCOPE_MODEL_PATH,
        save_dir=SAVE_DIR,
        max_retries=MAX_RETRIES,
        retry_delay=RETRY_DELAY,
        max_workers=MAX_WORKERS,
        revision=MODEL_REVISION,
    )

    print("[1/3] configuring Magnus connection")
    print(f"      address: {MAGNUS_ADDRESS}")
    print(f"      token  : {_mask_token(MAGNUS_TOKEN)}")
    magnus.configure(address=MAGNUS_ADDRESS, token=MAGNUS_TOKEN)

    print("[2/3] submitting model download job")
    print(f"      model : {MODEL_ID}")
    print(f"      source: {MODELSCOPE_MODEL_PATH}")
    print(f"      target: {SAVE_DIR}")

    job_id = magnus.submit_job(
        task_name=f"DownloadModel-{MODEL_ID.rstrip('/').split('/')[-1]}",
        description=f"Download {MODELSCOPE_MODEL_PATH} from ModelScope to GU persistent storage",
        namespace=NAMESPACE,
        repo_name=REPO_NAME,
        branch=BRANCH,
        commit_sha=COMMIT_SHA,
        entry_command=entry_command,
        gpu_count=GPU_COUNT,
        gpu_type="cpu" if GPU_COUNT == 0 else None,
        cpu_count=CPU_COUNT,
        memory_demand=MEMORY_DEMAND,
        ephemeral_storage=EPHEMERAL_STORAGE,
        job_type=JOB_TYPE,
    )

    print("[3/3] submitted")
    print(f"      job_id: {job_id}")
    print(f"      time  : {datetime.now().isoformat()}")
    return str(job_id)


def main() -> None:
    submit_download_job()


if __name__ == "__main__":
    main()  # 不再传 args
