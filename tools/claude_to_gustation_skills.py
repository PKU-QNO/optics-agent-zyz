from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

import magnus

from export_claude_skills_to_magnus import export_workspace, utc_timestamp as export_timestamp
from sync_magnus_skills import (
    configure_magnus,
    list_remote_skill_ids,
    load_candidates,
    utc_timestamp,
    write_report,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OPTICS_ROOT = PROJECT_ROOT
DEFAULT_SEPR_ROOT = PROJECT_ROOT.parent / "self-evo-paper-repro"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / ".magnus"
DEFAULT_SECRET = PROJECT_ROOT.parent / "secret.json"
DEFAULT_ADDRESS = "https://gustation.phybench.cn"
DEFAULT_REPORT = PROJECT_ROOT / ".magnus" / "claude_to_gustation_report.json"


def export_claude_tree(optics_root: Path, sepr_root: Path, output_root: Path) -> dict[str, dict[str, int]]:
    exported_at = export_timestamp()
    summary: dict[str, dict[str, int]] = {}
    for workspace_label, workspace_root in [
        ("optics-agent", optics_root.resolve()),
        ("sepr", sepr_root.resolve()),
    ]:
        skill_count, agent_count = export_workspace(
            workspace_label=workspace_label,
            workspace_root=workspace_root,
            output_root=output_root.resolve(),
            exported_at=exported_at,
        )
        summary[workspace_label] = {"skills": skill_count, "agents": agent_count}
        print(f"exported {workspace_label}: {skill_count} skills, {agent_count} agents")
    return summary


def sync_to_gustation(
    *,
    packages_root: Path,
    secret: Path,
    address: str,
    report_path: Path,
    submit: bool,
) -> dict[str, object]:
    configure_magnus(secret.resolve(), address)

    selected, duplicates = load_candidates(packages_root.resolve())
    remote_ids_before, remote_items_before = list_remote_skill_ids()
    missing_ids = sorted(upload_id for upload_id in selected if upload_id not in remote_ids_before)

    submitted: list[str] = []
    failed: list[dict[str, str]] = []
    if submit:
        for upload_id in missing_ids:
            candidate, files = selected[upload_id]
            try:
                magnus.save_skill(
                    skill_id=upload_id,
                    title=candidate.title,
                    description=candidate.description,
                    files=files,
                    timeout=60,
                )
                submitted.append(upload_id)
                print(f"submitted {upload_id} <- {candidate.package_path}")
            except Exception as exc:  # keep going and report all failures.
                failed.append({"id": upload_id, "package_path": candidate.package_path, "error": str(exc)})
                print(f"FAILED {upload_id} <- {candidate.package_path}: {exc}")

    remote_count_after: int | None = None
    missing_submitted_after: list[str] = []
    if submit:
        remote_items_after = list_remote_skill_ids()[1]
        remote_count_after = len(remote_items_after)
        missing_submitted_after = verify_submitted_ids(submitted)

    report: dict[str, object] = {
        "timestamp": utc_timestamp(),
        "address": address,
        "mode": "submit" if submit else "dry-run",
        "remote_count_before": len(remote_items_before),
        "remote_count_after": remote_count_after,
        "local_package_count": sum(1 for _ in packages_root.glob("**/*.magnusskill.yaml")),
        "unique_upload_id_count": len(selected),
        "duplicate_group_count": len(duplicates),
        "remote_existing_ids_before": sorted(remote_ids_before),
        "missing_ids_before_submit": missing_ids,
        "submitted_ids": submitted,
        "missing_submitted_after": missing_submitted_after,
        "failed": failed,
        "selected": {upload_id: asdict(candidate) for upload_id, (candidate, _) in sorted(selected.items())},
        "duplicates": {
            upload_id: [asdict(candidate) for candidate in values] for upload_id, values in sorted(duplicates.items())
        },
    }
    write_report(report_path.resolve(), report)
    return report


def verify_submitted_ids(skill_ids: list[str], *, attempts: int = 3, delay_seconds: float = 2.0) -> list[str]:
    remaining = sorted(set(skill_ids))
    for attempt in range(attempts):
        missing: list[str] = []
        for skill_id in remaining:
            try:
                magnus.get_skill(skill_id, timeout=30)
            except Exception:
                missing.append(skill_id)
        if not missing:
            return []
        remaining = missing
        if attempt < attempts - 1:
            time.sleep(delay_seconds)
    return remaining


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "End-to-end pipeline: export optics_agent/SEPR .claude skills and agents to .magnus packages, "
            "deduplicate them, then optionally submit missing packages to Gustation."
        )
    )
    parser.add_argument("--optics-root", type=Path, default=DEFAULT_OPTICS_ROOT)
    parser.add_argument("--sepr-root", type=Path, default=DEFAULT_SEPR_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--secret", type=Path, default=DEFAULT_SECRET)
    parser.add_argument("--address", default=DEFAULT_ADDRESS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--submit", action="store_true", help="Submit missing skills to Gustation. Default is dry-run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()

    export_summary = export_claude_tree(
        optics_root=args.optics_root,
        sepr_root=args.sepr_root,
        output_root=output_root,
    )
    sync_report = sync_to_gustation(
        packages_root=output_root,
        secret=args.secret,
        address=args.address,
        report_path=args.report,
        submit=args.submit,
    )
    sync_report["export_summary"] = export_summary
    args.report.resolve().write_text(json.dumps(sync_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"address: {args.address}")
    print(f"mode: {'submit' if args.submit else 'dry-run'}")
    print(f"local_package_count: {sync_report['local_package_count']}")
    print(f"unique_upload_id_count: {sync_report['unique_upload_id_count']}")
    print(f"duplicate_group_count: {sync_report['duplicate_group_count']}")
    print(f"missing_count_before_submit: {len(sync_report['missing_ids_before_submit'])}")
    print(f"submitted_count: {len(sync_report['submitted_ids'])}")
    print(f"failed_count: {len(sync_report['failed'])}")
    print(f"missing_submitted_after: {len(sync_report['missing_submitted_after'])}")
    print(f"report: {args.report.resolve()}")
    return 1 if sync_report["failed"] or sync_report["missing_submitted_after"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
