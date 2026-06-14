from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import magnus


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECRET_PATH = PROJECT_ROOT.parent / "secret.json"
BLUEPRINT_PATH = PROJECT_ROOT / "comsol" / "blueprints" / "source" / "Optics_COMSOL_Runtime_zyz.magnus.py"

BLUEPRINT_ID = "Optics_COMSOL_Runtime_zyz"
CODE_ROOT = "/data/public/zhangyuanzheng/comsol-runtime"
OUTPUT_ROOT = "/home/magnus/data/optics_agent/comsol/runs"
CONTAINER_IMAGE = "docker://magnus-local/comsol-runtime:latest"
LICENSE_PATH = "/opt/comsol-license/license.dat"
REMOTE_HOST = "zhangyuanzheng@Gustation"

ACTIVE_STATUSES = {"Preparing", "Pending", "Queued", "Running", "Paused"}
TERMINAL_STATUSES = {"Success", "Failed", "Terminated"}


@dataclass(frozen=True)
class MieCase:
    name: str
    run_id: str
    input_file: str
    cpu_count: int
    memory_demand: str
    ephemeral_storage: str
    max_wait_hours: float

    @property
    def output_dir(self) -> str:
        return f"{OUTPUT_ROOT}/{self.run_id}"


SMOKE = MieCase(
    name="smoke",
    run_id="comsol-mie-td-20260613-smoke-v1",
    input_file=f"{CODE_ROOT}/cases/mie_scattering/MieScatteringTimeDomain2DSmoke.java",
    cpu_count=8,
    memory_demand="32G",
    ephemeral_storage="100G",
    max_wait_hours=0.5,
)

MEDIUM = MieCase(
    name="medium",
    run_id="comsol-mie-td-20260613-medium-v1",
    input_file=f"{CODE_ROOT}/cases/mie_scattering/MieScatteringTimeDomain2DMedium.java",
    cpu_count=24,
    memory_demand="128G",
    ephemeral_storage="200G",
    max_wait_hours=12.0,
)


def load_secret(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise SystemExit(f"{path} must contain a JSON object")
    return data


def configure_magnus(secret_path: Path) -> None:
    secret = load_secret(secret_path)
    address = secret.get("magnus_address-gu") or secret.get("magnus_address")
    token = secret.get("magnus_token-gu") or secret.get("magnus_token")
    if not address or not token:
        raise SystemExit(f"Missing Magnus address/token in {secret_path}")
    magnus.configure(address=address, token=token)


def parse_memory_gb(value: str) -> float:
    match = re.fullmatch(r"([0-9.]+)\s*([kmgt]?b?)?", value.strip().lower())
    if not match:
        raise ValueError(f"cannot parse memory demand: {value}")
    number = float(match.group(1))
    unit = (match.group(2) or "g").rstrip("b")
    if unit == "t":
        return number * 1024
    if unit in {"g", ""}:
        return number
    if unit == "m":
        return number / 1024
    if unit == "k":
        return number / (1024 * 1024)
    raise ValueError(f"unknown memory unit: {value}")


def get_items(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict):
        items = response.get("items", [])
        return items if isinstance(items, list) else []
    if isinstance(response, list):
        return response
    return []


def status_of(job: dict[str, Any]) -> str:
    return str(job.get("status") or "")


def find_existing_job(run_id: str) -> dict[str, Any] | None:
    response = magnus.list_jobs(limit=100, search=run_id, timeout=20)
    for item in get_items(response):
        haystack = "\n".join([
            str(item.get("id", "")),
            str(item.get("task_name", "")),
            str(item.get("entry_command", "")),
            str(item.get("description", "")),
        ])
        if run_id in haystack:
            return item
    return None


def cluster_resource_snapshot() -> dict[str, Any]:
    stats = magnus.get_cluster_stats(timeout=20)
    resources = stats.get("resources", {}) if isinstance(stats, dict) else {}
    required = {"cpu_total", "cpu_free", "mem_total_mb", "mem_free_mb"}
    missing = sorted(required - set(resources))
    if missing:
        raise RuntimeError(f"cluster stats missing keys: {missing}")
    return stats


def check_resource_limit(case: MieCase) -> dict[str, Any]:
    stats = cluster_resource_snapshot()
    resources = stats["resources"]
    cpu_total = int(resources["cpu_total"])
    cpu_free = int(resources["cpu_free"])
    mem_total_gb = float(resources["mem_total_mb"]) / 1024.0
    mem_free_gb = float(resources["mem_free_mb"]) / 1024.0
    cpu_used = cpu_total - cpu_free
    mem_used_gb = mem_total_gb - mem_free_gb
    planned_mem_gb = parse_memory_gb(case.memory_demand)
    cpu_after = cpu_used + case.cpu_count
    mem_after = mem_used_gb + planned_mem_gb
    ok = cpu_after <= cpu_total * 0.5 and mem_after <= mem_total_gb * 0.5
    return {
        "ok": ok,
        "cpu_total": cpu_total,
        "cpu_free": cpu_free,
        "cpu_used": cpu_used,
        "cpu_after": cpu_after,
        "cpu_limit_half": cpu_total * 0.5,
        "mem_total_gb": round(mem_total_gb, 3),
        "mem_free_gb": round(mem_free_gb, 3),
        "mem_used_gb": round(mem_used_gb, 3),
        "mem_after_gb": round(mem_after, 3),
        "mem_limit_half_gb": round(mem_total_gb * 0.5, 3),
    }


def save_blueprint() -> None:
    magnus.save_blueprint(
        blueprint_id=BLUEPRINT_ID,
        title="Optics COMSOL Runtime zyz",
        description="COMSOL runtime launcher. Public blueprint, private runner and license live in server storage.",
        code=BLUEPRINT_PATH.read_text(encoding="utf-8"),
    )


def blueprint_args(case: MieCase) -> dict[str, Any]:
    return {
        "run_mode": "batch_java",
        "domain_preset": "optics",
        "code_root": CODE_ROOT,
        "license_mode": "server_env",
        "license_path": LICENSE_PATH,
        "input_file": case.input_file,
        "output_root": OUTPUT_ROOT,
        "run_id": case.run_id,
        "container_image": CONTAINER_IMAGE,
        "cpu_count": case.cpu_count,
        "memory_demand": case.memory_demand,
        "ephemeral_storage": case.ephemeral_storage,
        "priority": "B2",
        "execute_action": True,
    }


def launch_case(case: MieCase) -> str:
    job_id = magnus.launch_blueprint(BLUEPRINT_ID, args=blueprint_args(case))
    if not isinstance(job_id, str):
        raise RuntimeError(f"unexpected launch_blueprint return: {job_id!r}")
    return job_id


def submit_or_reuse(
    case: MieCase,
    *,
    dry_run: bool,
    force_rerun_failed: bool,
    force_rerun_success: bool,
) -> dict[str, Any]:
    existing = find_existing_job(case.run_id)
    if existing:
        status = status_of(existing)
        job_id = str(existing.get("id", ""))
        if status in ACTIVE_STATUSES:
            return record(case, job_id, status, "reused_active", None)
        if status == "Success" and not force_rerun_success:
            return record(case, job_id, status, "reused_success", None)
        if status in {"Failed", "Terminated"} and not force_rerun_failed:
            return record(case, job_id, status, "skipped_failed", None)

    resource_check = check_resource_limit(case)
    if not resource_check["ok"]:
        return record(case, "", "Blocked", "blocked_resource", resource_check)
    if dry_run:
        return record(case, "", "DryRun", "would_submit", resource_check)
    job_id = launch_case(case)
    return record(case, job_id, "Submitted", "submitted", resource_check)


def record(case: MieCase, job_id: str, status: str, action: str, resource_check: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "case": case.name,
        "run_id": case.run_id,
        "job_id": job_id,
        "status": status,
        "dedupe_action": action,
        "input_file": case.input_file,
        "output_dir": case.output_dir,
        "cpu_count": case.cpu_count,
        "memory_demand": case.memory_demand,
        "ephemeral_storage": case.ephemeral_storage,
        "gpu_type": "cpu",
        "gpu_count": 0,
        "resource_check": resource_check,
    }


def poll_interval(case: MieCase, elapsed: float) -> int:
    if case.name == "smoke":
        if elapsed < 60:
            return 60
        return 180
    if elapsed < 5 * 60:
        return 300
    if elapsed < 60 * 60:
        return 600
    return 1800


def wait_for_case(case: MieCase, rec: dict[str, Any]) -> dict[str, Any]:
    if not rec.get("job_id") or rec.get("dedupe_action") not in {"submitted", "reused_active", "reused_success"}:
        return rec
    if rec.get("dedupe_action") == "reused_success":
        rec["result"] = safe_get_result(rec["job_id"])
        return rec

    started = time.time()
    while True:
        job = magnus.get_job(rec["job_id"], timeout=20)
        rec["status"] = status_of(job)
        rec["task_name"] = job.get("task_name", "")
        if rec["status"] in TERMINAL_STATUSES:
            rec["result"] = safe_get_result(rec["job_id"])
            return rec
        elapsed = time.time() - started
        if elapsed >= case.max_wait_hours * 3600:
            rec["status"] = "pending_or_timeout"
            return rec
        sleep_s = poll_interval(case, elapsed)
        print(f"[{case.name}] {rec['job_id']} status={rec['status']}; waiting {sleep_s}s")
        time.sleep(sleep_s)


def safe_get_result(job_id: str) -> Any:
    try:
        return magnus.get_job_result(job_id, timeout=20)
    except Exception as exc:
        return {"result_error": repr(exc)}


def sync_runtime(dry_run: bool) -> None:
    cmd = [sys.executable, str(PROJECT_ROOT / "comsol" / "automation" / "sync_comsol_runtime_to_gustation.py")]
    if dry_run:
        cmd.append("--dry-run")
    subprocess.run(cmd, cwd=str(PROJECT_ROOT), check=True)


def write_report(records: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# COMSOL Mie-like Time-domain Scattering Run",
        "",
        f"Updated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Summary",
        "",
        "- Method: 2D time-domain scalar wave FEM, FDTD-like pulse scattering.",
        f"- Image: `{CONTAINER_IMAGE}`",
        f"- Blueprint: `{BLUEPRINT_ID}`",
        "- GPU: not used (`gpu_type=cpu`, `gpu_count=0`).",
        "",
        "## Jobs",
        "",
        "| Case | Job ID | Status | Action | Output |",
        "|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            f"| `{rec['case']}` | `{rec.get('job_id','')}` | `{rec.get('status','')}` | "
            f"`{rec.get('dedupe_action','')}` | `{rec.get('output_dir','')}` |"
        )
    lines.extend(["", "## Raw Records", "", "```json", json.dumps(records, ensure_ascii=False, indent=2), "```", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit a COMSOL Mie-like time-domain scattering smoke/medium campaign.")
    parser.add_argument("--secret-json", type=Path, default=SECRET_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Check dedupe/resources and sync commands without submitting.")
    parser.add_argument("--skip-sync", action="store_true", help="Do not upload comsol-runtime to Gustation before submission.")
    parser.add_argument("--force-rerun-failed", action="store_true", help="Resubmit Failed/Terminated matching jobs.")
    parser.add_argument("--force-rerun-success", action="store_true", help="Resubmit even if a matching job already succeeded.")
    parser.add_argument("--medium-only", action="store_true", help="Submit only the medium case; still performs dedupe/resources.")
    parser.add_argument("--smoke-only", action="store_true", help="Submit only the smoke case.")
    parser.add_argument("--no-wait", action="store_true", help="Submit/reuse jobs but do not poll.")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "comsol" / "docs" / "reports" / "comsol_mie_scattering_run_report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_magnus(args.secret_json)

    if not args.dry_run:
        save_blueprint()
    if not args.skip_sync:
        sync_runtime(dry_run=args.dry_run)

    records: list[dict[str, Any]] = []
    if not args.medium_only:
        smoke = submit_or_reuse(
            SMOKE,
            dry_run=args.dry_run,
            force_rerun_failed=args.force_rerun_failed,
            force_rerun_success=args.force_rerun_success,
        )
        records.append(smoke)
        if not args.no_wait and not args.dry_run:
            smoke = wait_for_case(SMOKE, smoke)
            records[-1] = smoke
        if not args.dry_run and smoke["status"] != "Success" and not args.smoke_only:
            write_report(records, args.report)
            print(json.dumps(records, ensure_ascii=False, indent=2))
            raise SystemExit("Smoke case did not reach Success; medium case was not submitted.")

    if not args.smoke_only:
        medium = submit_or_reuse(
            MEDIUM,
            dry_run=args.dry_run,
            force_rerun_failed=args.force_rerun_failed,
            force_rerun_success=args.force_rerun_success,
        )
        records.append(medium)
        if not args.no_wait and not args.dry_run:
            medium = wait_for_case(MEDIUM, medium)
            records[-1] = medium

    write_report(records, args.report)
    print(json.dumps(records, ensure_ascii=False, indent=2))
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
