from __future__ import annotations

import argparse
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import magnus


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECRET_PATH = PROJECT_ROOT.parent / "secret.json"
BLUEPRINT_PATH = PROJECT_ROOT / "comsol" / "blueprints" / "source" / "Optics_COMSOL_Runtime_zyz.magnus.py"
TODO_PATH = PROJECT_ROOT / "comsol" / "docs" / "plans" / "comsol_runtime_capability_probe_todolist.md"
REPORT_PATH = PROJECT_ROOT / "comsol" / "docs" / "reports" / "comsol_runtime_capability_report.md"

BLUEPRINT_ID = "Optics_COMSOL_Runtime_zyz"
CAMPAIGN_ID = "comsol-capability-20260613-v1"
CODE_ROOT = "/data/public/zhangyuanzheng/comsol-runtime"
OUTPUT_ROOT = "/home/magnus/data/optics_agent/comsol/runs"
CONTAINER_IMAGE = "docker://magnus-local/comsol-runtime:latest"
LICENSE_PATH = "/opt/comsol-license/license.dat"

ACTIVE_STATUSES = {"Preparing", "Pending", "Queued", "Running", "Paused"}
TERMINAL_STATUSES = {"Success", "Failed", "Terminated"}


@dataclass(frozen=True)
class Probe:
    case_id: str
    run_mode: str
    domain_preset: str
    input_file: str | None
    cpu_count: int = 8
    memory_demand: str = "32G"
    ephemeral_storage: str = "100G"

    @property
    def run_id(self) -> str:
        return f"{CAMPAIGN_ID}-{self.case_id}"

    @property
    def output_dir(self) -> str:
        return f"{OUTPUT_ROOT}/{self.run_id}"


PROBES = [
    Probe("envcheck", "env_check", "generic", None),
    Probe("core-pde-eigenmode", "batch_java", "generic", f"{CODE_ROOT}/probes/CorePdeEigenmode.java"),
    Probe("optics-helmholtz", "batch_java", "optics", f"{CODE_ROOT}/probes/OpticsHelmholtz.java"),
    Probe("wave-optics-probe", "batch_java", "optics", f"{CODE_ROOT}/probes/WaveOpticsProbe.java"),
    Probe("fluid-laminar-probe", "batch_java", "fluid", f"{CODE_ROOT}/probes/FluidLaminarProbe.java"),
    Probe("fluid-pde-fallback", "batch_java", "fluid", f"{CODE_ROOT}/probes/FluidPdeFallback.java"),
]


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
    text = value.strip().lower()
    match = re.fullmatch(r"([0-9.]+)\s*([kmgt]?b?)?", text)
    if not match:
        raise ValueError(f"cannot parse memory demand: {value}")
    number = float(match.group(1))
    unit = (match.group(2) or "g").rstrip("b")
    if unit == "t":
        return number * 1024
    if unit == "g" or unit == "":
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


def find_existing_job(run_id: str) -> dict[str, Any] | None:
    response = magnus.list_jobs(limit=100, search=run_id, timeout=20)
    for item in get_items(response):
        task_name = str(item.get("task_name", ""))
        entry_command = str(item.get("entry_command", ""))
        if run_id in task_name or run_id in entry_command:
            return item
    return None


def cluster_resource_snapshot() -> dict[str, Any]:
    stats = magnus.get_cluster_stats(timeout=20)
    resources = stats.get("resources", {}) if isinstance(stats, dict) else {}
    required = ["cpu_total", "cpu_free", "mem_total_mb", "mem_free_mb"]
    missing = [key for key in required if key not in resources]
    if missing:
        raise RuntimeError(f"cluster stats missing keys: {missing}")
    return stats


def check_resource_limit(probe: Probe, reserved_cpu: int, reserved_mem_gb: float) -> dict[str, Any]:
    stats = cluster_resource_snapshot()
    resources = stats["resources"]
    cpu_total = int(resources["cpu_total"])
    cpu_free = int(resources["cpu_free"])
    mem_total_gb = float(resources["mem_total_mb"]) / 1024.0
    mem_free_gb = float(resources["mem_free_mb"]) / 1024.0
    cpu_used = cpu_total - cpu_free
    mem_used_gb = mem_total_gb - mem_free_gb
    planned_mem_gb = parse_memory_gb(probe.memory_demand)
    cpu_after = cpu_used + reserved_cpu + probe.cpu_count
    mem_after = mem_used_gb + reserved_mem_gb + planned_mem_gb
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
        "reserved_cpu": reserved_cpu,
        "reserved_mem_gb": round(reserved_mem_gb, 3),
    }


def save_blueprint() -> None:
    code = BLUEPRINT_PATH.read_text(encoding="utf-8")
    magnus.save_blueprint(
        blueprint_id=BLUEPRINT_ID,
        title="Optics COMSOL Runtime zyz",
        description="COMSOL runtime launcher. Public blueprint, private runner and license live in server storage.",
        code=code,
    )


def launch_probe(probe: Probe) -> str:
    args: dict[str, Any] = {
        "run_mode": probe.run_mode,
        "domain_preset": probe.domain_preset,
        "code_root": CODE_ROOT,
        "license_mode": "server_env",
        "license_path": LICENSE_PATH,
        "output_root": OUTPUT_ROOT,
        "run_id": probe.run_id,
        "container_image": CONTAINER_IMAGE,
        "cpu_count": probe.cpu_count,
        "memory_demand": probe.memory_demand,
        "ephemeral_storage": probe.ephemeral_storage,
        "priority": "B2",
    }
    if probe.input_file:
        args["input_file"] = probe.input_file
    job_id = magnus.launch_blueprint(BLUEPRINT_ID, args=args)
    if not isinstance(job_id, str):
        raise RuntimeError(f"unexpected launch_blueprint return: {job_id!r}")
    return job_id


def status_of(job: dict[str, Any]) -> str:
    return str(job.get("status") or "")


def submit_or_reuse(force_rerun_failed: bool, dry_run: bool) -> list[dict[str, Any]]:
    if not dry_run:
        save_blueprint()
    records: list[dict[str, Any]] = []
    reserved_cpu = 0
    reserved_mem_gb = 0.0
    for probe in PROBES:
        existing = find_existing_job(probe.run_id)
        if existing:
            status = status_of(existing)
            job_id = str(existing.get("id", ""))
            if status in ACTIVE_STATUSES:
                action = "reused_active"
                reserved_cpu += probe.cpu_count
                reserved_mem_gb += parse_memory_gb(probe.memory_demand)
            elif status == "Success":
                action = "reused_success"
            elif status in {"Failed", "Terminated"} and not force_rerun_failed:
                action = "skipped_failed"
            else:
                action = "rerun_failed" if force_rerun_failed else "skipped_unknown"
            if action != "rerun_failed":
                records.append(record(probe, job_id, status, action, None))
                continue

        resource_check = check_resource_limit(probe, reserved_cpu, reserved_mem_gb)
        if not resource_check["ok"]:
            records.append(record(probe, "", "Blocked", "blocked_resource", resource_check))
            continue
        if dry_run:
            records.append(record(probe, "", "DryRun", "would_submit", resource_check))
            reserved_cpu += probe.cpu_count
            reserved_mem_gb += parse_memory_gb(probe.memory_demand)
            continue
        job_id = launch_probe(probe)
        records.append(record(probe, job_id, "Submitted", "submitted", resource_check))
        reserved_cpu += probe.cpu_count
        reserved_mem_gb += parse_memory_gb(probe.memory_demand)
    return records


def record(probe: Probe, job_id: str, status: str, action: str, resource_check: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "case_id": probe.case_id,
        "run_id": probe.run_id,
        "job_id": job_id,
        "status": status,
        "dedupe_action": action,
        "domain_preset": probe.domain_preset,
        "run_mode": probe.run_mode,
        "input_file": probe.input_file or "",
        "output_dir": probe.output_dir,
        "cpu_count": probe.cpu_count,
        "memory_demand": probe.memory_demand,
        "gpu_type": "cpu",
        "gpu_count": 0,
        "resource_check": resource_check,
    }


def poll_interval_seconds(elapsed: float, has_fast_only: bool) -> int:
    if has_fast_only:
        if elapsed < 60:
            return 60
        if elapsed < 30 * 60:
            return 180
    else:
        if elapsed < 5 * 60:
            return 300
        if elapsed < 30 * 60:
            return 600
    return 1800


def wait_for_jobs(records: list[dict[str, Any]], max_wait_hours: float) -> list[dict[str, Any]]:
    waitable = [r for r in records if r["job_id"] and r["dedupe_action"] in {"submitted", "reused_active"}]
    if not waitable:
        return records
    started = time.time()
    while True:
        all_terminal = True
        for rec in waitable:
            job = magnus.get_job(rec["job_id"], timeout=20)
            rec["status"] = status_of(job)
            rec["task_name"] = job.get("task_name", "")
            if rec["status"] not in TERMINAL_STATUSES:
                all_terminal = False
            if rec["status"] in TERMINAL_STATUSES:
                try:
                    rec["result"] = magnus.get_job_result(rec["job_id"], timeout=20)
                except Exception as exc:
                    rec["result_error"] = repr(exc)
        write_report(records, partial=not all_terminal)
        if all_terminal:
            return records
        elapsed = time.time() - started
        if elapsed >= max_wait_hours * 3600:
            for rec in waitable:
                if rec["status"] not in TERMINAL_STATUSES:
                    rec["status"] = "pending_or_timeout"
            return records
        fast = all(r["case_id"] == "envcheck" for r in waitable)
        sleep_s = poll_interval_seconds(elapsed, fast)
        print(f"Waiting {sleep_s}s before next poll; elapsed={elapsed:.0f}s")
        time.sleep(sleep_s)


def write_report(records: list[dict[str, Any]], partial: bool) -> None:
    lines = [
        "# COMSOL Runtime Capability Report",
        "",
        f"Updated: {datetime.now().isoformat(timespec='seconds')}",
        f"Campaign: `{CAMPAIGN_ID}`",
        f"Image: `{CONTAINER_IMAGE}`",
        f"Blueprint: `{BLUEPRINT_ID}`",
        f"Status: {'partial' if partial else 'complete'}",
        "",
        "## Resource Policy",
        "",
        "- CPU only: `gpu_type=cpu`, `gpu_count=0`.",
        "- Each submission is preceded by `magnus.list_jobs` dedupe and `magnus.get_cluster_stats` resource checks.",
        "- Submission is blocked if planned CPU or memory would exceed half of cluster total.",
        "",
        "## Jobs",
        "",
        "| Case | Job ID | Status | Action | Output |",
        "|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            f"| `{rec['case_id']}` | `{rec.get('job_id','')}` | `{rec.get('status','')}` | "
            f"`{rec.get('dedupe_action','')}` | `{rec.get('output_dir','')}` |"
        )
    lines.extend(["", "## Raw Records", "", "```json", json.dumps(records, ensure_ascii=False, indent=2), "```", ""])
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit/reuse COMSOL capability probes with Magnus dedupe and resource checks.")
    parser.add_argument("--secret-json", type=Path, default=SECRET_PATH)
    parser.add_argument("--dry-run", action="store_true", help="Run dedupe/resource checks but do not submit jobs.")
    parser.add_argument("--force-rerun-failed", action="store_true", help="Resubmit probes whose matching job failed or terminated.")
    parser.add_argument("--wait", action="store_true", help="Poll submitted/reused active jobs until terminal or timeout.")
    parser.add_argument("--max-wait-hours", type=float, default=12.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_magnus(args.secret_json)
    records = submit_or_reuse(force_rerun_failed=args.force_rerun_failed, dry_run=args.dry_run)
    write_report(records, partial=True)
    if args.wait and not args.dry_run:
        records = wait_for_jobs(records, max_wait_hours=args.max_wait_hours)
        write_report(records, partial=False)
    print(json.dumps(records, ensure_ascii=False, indent=2))
    print(f"Report: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
