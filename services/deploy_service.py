#!/usr/bin/env python3
"""
Create or update the DeepSeek-R1-Distill-Qwen-7B Magnus Service on GU.

This script uses raw Magnus HTTP APIs with requests and verify=False, matching
current GU service endpoint behavior:
- GET    /api/services
- POST   /api/services       (create/update/upsert)
- DELETE /api/services/{id}

IMPORTANT:
- Do not run this script until the model has already been downloaded to /data/.
- New Magnus Services are forced inactive on first creation by the backend, so
  this script POSTs the same payload twice to ensure is_active=true after create.
- Token is read from C:\\Users\\27370\\Desktop\\project\\secret.json. Never hard-code credentials here.
- Address defaults to secret.json and can be overridden with --address.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

import requests
import urllib3


SECRET_PATH = Path(r"C:\Users\27370\Desktop\project\secret.json")
DEFAULT_CONFIG = Path(__file__).with_name("service_config.json")

# GU currently may require verify=False; suppress the expected warning so logs
# stay readable. Remove this if GU obtains a trusted certificate chain.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


COMPARABLE_FIELDS = [
    "id",
    "name",
    "description",
    "is_active",
    "request_timeout",
    "idle_timeout",
    "max_concurrency",
    "job_task_name",
    "job_description",
    "namespace",
    "repo_name",
    "branch",
    "commit_sha",
    "entry_command",
    "gpu_count",
    "gpu_type",
    "job_type",
    "cpu_count",
    "memory_demand",
    "ephemeral_storage",
    "runner",
    "container_image",
    "system_entry_command",
]


def load_secret(path: Path = SECRET_PATH) -> dict[str, str]:
    """Load GU Magnus address/token from project secret.json."""
    with path.open("r", encoding="utf-8") as f:
        secret = json.load(f)
    return {
        "address": secret["magnus_address-gu"],
        "token": secret["magnus_token-gu"],
    }


def load_config(path: Path) -> dict[str, Any]:
    """Load and minimally validate the ServiceCreate JSON payload."""
    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)

    required = [
        "id",
        "name",
        "job_task_name",
        "job_description",
        "namespace",
        "repo_name",
        "branch",
        "commit_sha",
        "entry_command",
        "gpu_count",
        "gpu_type",
    ]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"missing required service_config fields: {missing}")
    if "$MAGNUS_PORT" not in config["entry_command"]:
        raise ValueError("entry_command must listen on $MAGNUS_PORT")
    return config


def normalize_for_compare(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Keep only user-controlled ServiceCreate fields for stable comparison.

    Magnus responses include runtime fields such as owner_id, current_job_id,
    assigned_port, updated_at, etc. Those must not trigger rebuilds.
    """
    normalized: dict[str, Any] = {}
    for key in COMPARABLE_FIELDS:
        if key in payload and payload[key] is not None:
            normalized[key] = payload[key]
    return normalized


def configs_equal(existing: dict[str, Any], desired: dict[str, Any]) -> bool:
    """Return True when existing service config matches desired config."""
    return normalize_for_compare(existing) == normalize_for_compare(desired)


def make_session(address: str, token: str) -> tuple[requests.Session, str]:
    """Create an authenticated requests session and normalized base URL."""
    if not token:
        raise RuntimeError("magnus_token-gu is required in secret.json")

    base_url = address.rstrip("/")
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    )
    return session, base_url


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> Any:
    """Send a Magnus API request and return JSON when available."""
    resp = session.request(method, url, json=payload, timeout=timeout, verify=False)
    if resp.status_code >= 400:
        raise RuntimeError(
            f"{method} {url} failed: HTTP {resp.status_code}\n{resp.text[:4000]}"
        )
    if resp.text.strip():
        try:
            return resp.json()
        except ValueError:
            return resp.text
    return None


def list_services(session: requests.Session, base_url: str, service_id: str) -> dict[str, Any] | None:
    """Return the matching service from GET /api/services, or None."""
    # Search narrows the list; limit is still kept high enough for safety.
    url = f"{base_url}/api/services?skip=0&limit=100&search={service_id}&active_only=false&sort_by=updated"
    data = request_json(session, "GET", url)

    items: list[dict[str, Any]]
    if isinstance(data, dict) and "items" in data:
        items = data["items"]
    elif isinstance(data, list):
        items = data
    else:
        items = []

    for item in items:
        if item.get("id") == service_id:
            return item
    return None


def delete_service(session: requests.Session, base_url: str, service_id: str) -> None:
    """Delete a service; Magnus will terminate its current service job if any."""
    request_json(session, "DELETE", f"{base_url}/api/services/{service_id}")


def create_or_update_service(session: requests.Session, base_url: str, config: dict[str, Any]) -> dict[str, Any]:
    """
    POST ServiceCreate payload to Magnus.

    The backend has upsert semantics, but for materially different existing
    configs we delete first to guarantee stale runtime state is removed.
    """
    return request_json(session, "POST", f"{base_url}/api/services", payload=config)


def deploy(config_path: Path, address: str, token: str, dry_run: bool = False) -> None:
    """Check existing service and create/update/delete according to config."""
    desired = load_config(config_path)
    service_id = desired["id"]
    session, base_url = make_session(address, token)

    existing = list_services(session, base_url, service_id)
    if existing and configs_equal(existing, desired):
        print(f"[skip] service '{service_id}' already exists with identical config")
        return

    if dry_run:
        print("[dry-run] desired config:")
        print(json.dumps(normalize_for_compare(desired), ensure_ascii=False, indent=2))
        if existing:
            print("[dry-run] existing config differs and would be deleted/recreated")
        else:
            print("[dry-run] service does not exist and would be created")
        return

    if existing:
        print(f"[delete] existing service '{service_id}' config differs; deleting first")
        delete_service(session, base_url, service_id)

    print(f"[create] posting service '{service_id}'")
    create_or_update_service(session, base_url, desired)

    # New service creation is forced inactive by Magnus backend. POST again with
    # the same ID and is_active=true so the upsert path activates it.
    if desired.get("is_active", True):
        print(f"[activate] posting service '{service_id}' again to enable is_active=true")
        second_payload = copy.deepcopy(desired)
        second_payload["is_active"] = True
        create_or_update_service(session, base_url, second_payload)

    final = list_services(session, base_url, service_id)
    print("[done] final service summary:")
    print(json.dumps(normalize_for_compare(final or desired), ensure_ascii=False, indent=2))


def parse_args() -> argparse.Namespace:
    secret = load_secret()
    parser = argparse.ArgumentParser(description="Deploy a Magnus GU Service from service_config.json")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--address", default=secret["address"], help="Override GU Magnus address from secret.json")
    parser.add_argument("--dry-run", action="store_true", help="Print intended changes without API writes")
    args = parser.parse_args()
    args.token = secret["token"]
    return args


def main() -> None:
    args = parse_args()
    try:
        deploy(args.config, args.address, args.token, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001 - CLI should surface actionable errors.
        print(f"[error] {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
