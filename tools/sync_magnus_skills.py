from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import magnus
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGES_ROOT = PROJECT_ROOT / ".magnus"
DEFAULT_SECRET = PROJECT_ROOT.parent / "secret.json"
DEFAULT_ADDRESS = "https://gustation.phybench.cn"
DEFAULT_REPORT = PROJECT_ROOT / ".magnus" / "skill_sync_report.json"


@dataclass(frozen=True)
class Candidate:
    upload_id: str
    source_kind: str
    source_name: str
    title: str
    description: str
    package_path: str
    file_count: int
    content_bytes: int
    fingerprint: str


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def normalize_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")
    return cleaned.lower() or "unnamed-skill"


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data = yaml.safe_load(text[4:end]) or {}
    return data if isinstance(data, dict) else {}


def load_secret(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def configure_magnus(secret_path: Path, address: str) -> None:
    secret = load_secret(secret_path)
    token = secret.get("magnus_token-gu") or secret.get("magnus_token")
    if not token:
        raise ValueError(f"No Magnus token found in {secret_path}")
    magnus.configure(address=address, token=token)


def package_files_content(files: list[dict[str, Any]]) -> str:
    parts = []
    for item in files:
        parts.append(
            "\0".join(
                [
                    str(item.get("path", "")),
                    str(item.get("encoding", "")),
                    str(item.get("content", "")),
                ]
            )
        )
    return "\n".join(parts)


def load_candidate(package_path: Path, packages_root: Path) -> tuple[Candidate, list[dict[str, str]]]:
    data = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("kind") != "magnus/skill":
        raise ValueError(f"Not a magnus/skill package: {package_path}")
    payload = data.get("payload")
    if not isinstance(payload, dict):
        raise ValueError(f"Missing payload: {package_path}")
    files = payload.get("files")
    if not isinstance(files, list):
        raise ValueError(f"Missing payload.files: {package_path}")

    rel = package_path.relative_to(packages_root).as_posix()
    source_kind = "agent" if "/claude-agents/" in rel else "skill"
    skill_md = next((item.get("content", "") for item in files if item.get("path") == "SKILL.md"), "")
    frontmatter = parse_frontmatter(skill_md)
    source_name = str(frontmatter.get("name") or Path(rel).name.removesuffix(".magnusskill.yaml"))
    upload_id = normalize_id(("agent-" if source_kind == "agent" else "") + source_name)

    title = str(payload.get("title") or source_name)
    if source_kind == "agent" and not title.lower().startswith("agent:"):
        title = f"Agent: {title}"
    description = str(payload.get("description") or "")
    content = package_files_content(files)
    candidate = Candidate(
        upload_id=upload_id,
        source_kind=source_kind,
        source_name=source_name,
        title=title,
        description=description,
        package_path=rel,
        file_count=len(files),
        content_bytes=sum(len(str(item.get("content", "")).encode("utf-8")) for item in files),
        fingerprint=hashlib.sha256(content.encode("utf-8")).hexdigest(),
    )
    return candidate, files


def load_candidates(packages_root: Path) -> tuple[dict[str, tuple[Candidate, list[dict[str, str]]]], dict[str, list[Candidate]]]:
    groups: dict[str, list[tuple[Candidate, list[dict[str, str]]]]] = {}
    for package_path in sorted(packages_root.glob("**/*.magnusskill.yaml")):
        candidate, files = load_candidate(package_path, packages_root)
        groups.setdefault(candidate.upload_id, []).append((candidate, files))

    selected: dict[str, tuple[Candidate, list[dict[str, str]]]] = {}
    duplicates: dict[str, list[Candidate]] = {}
    for upload_id, values in groups.items():
        values_sorted = sorted(values, key=lambda item: (-item[0].content_bytes, item[0].package_path))
        selected[upload_id] = values_sorted[0]
        if len(values_sorted) > 1:
            duplicates[upload_id] = [candidate for candidate, _ in values_sorted]
    return selected, duplicates


def list_remote_skill_ids(limit: int = 100, timeout: float = 30.0) -> tuple[set[str], list[dict[str, Any]]]:
    all_items: list[dict[str, Any]] = []
    skip = 0
    while True:
        page = magnus.list_skills(limit=limit, skip=skip, timeout=timeout)
        if isinstance(page, dict):
            items = page.get("items") or page.get("skills") or page.get("data") or page.get("results") or []
            total = page.get("total") or page.get("count") or page.get("total_count")
        else:
            items = page
            total = None
        if not items:
            break
        all_items.extend(items)
        if total is not None and len(all_items) >= int(total):
            break
        if len(items) < limit:
            break
        skip += limit

    ids: set[str] = set()
    for item in all_items:
        if isinstance(item, dict):
            item_id = item.get("id") or item.get("_id") or item.get("name")
            if item_id:
                ids.add(str(item_id))
    return ids, all_items


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


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deduplicate and sync local .magnusskill.yaml packages to Gustation.")
    parser.add_argument("--packages-root", type=Path, default=DEFAULT_PACKAGES_ROOT)
    parser.add_argument("--secret", type=Path, default=DEFAULT_SECRET)
    parser.add_argument("--address", default=DEFAULT_ADDRESS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--submit", action="store_true", help="Actually submit missing skills. Default is dry-run.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packages_root = args.packages_root.resolve()
    configure_magnus(args.secret.resolve(), args.address)

    selected, duplicates = load_candidates(packages_root)
    remote_ids, remote_items = list_remote_skill_ids()
    missing_ids = sorted(upload_id for upload_id in selected if upload_id not in remote_ids)

    submitted: list[str] = []
    failed: list[dict[str, str]] = []
    missing_submitted_after: list[str] = []
    if args.submit:
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
            except Exception as exc:  # keep going so one bad package does not hide the rest.
                failed.append({"id": upload_id, "package_path": candidate.package_path, "error": str(exc)})
                print(f"FAILED {upload_id} <- {candidate.package_path}: {exc}")
        missing_submitted_after = verify_submitted_ids(submitted)

    report = {
        "timestamp": utc_timestamp(),
        "address": args.address,
        "mode": "submit" if args.submit else "dry-run",
        "remote_count_before": len(remote_items),
        "local_package_count": sum(1 for _ in packages_root.glob("**/*.magnusskill.yaml")),
        "unique_upload_id_count": len(selected),
        "duplicate_group_count": len(duplicates),
        "remote_existing_ids": sorted(remote_ids),
        "missing_ids": missing_ids,
        "submitted_ids": submitted,
        "missing_submitted_after": missing_submitted_after,
        "failed": failed,
        "selected": {upload_id: asdict(candidate) for upload_id, (candidate, _) in sorted(selected.items())},
        "duplicates": {upload_id: [asdict(candidate) for candidate in values] for upload_id, values in sorted(duplicates.items())},
    }
    write_report(args.report.resolve(), report)

    print(f"address: {args.address}")
    print(f"remote_count_before: {len(remote_items)}")
    print(f"local_package_count: {report['local_package_count']}")
    print(f"unique_upload_id_count: {len(selected)}")
    print(f"duplicate_group_count: {len(duplicates)}")
    print(f"missing_count: {len(missing_ids)}")
    print(f"submitted_count: {len(submitted)}")
    print(f"missing_submitted_after: {len(missing_submitted_after)}")
    print(f"failed_count: {len(failed)}")
    print(f"report: {args.report.resolve()}")
    return 1 if failed or missing_submitted_after else 0


if __name__ == "__main__":
    raise SystemExit(main())
