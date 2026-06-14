from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import magnus

from package_magnus_blueprint import DEFAULT_DESCRIPTION, DEFAULT_TITLE, write_blueprint_package

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECRET_PATH = PROJECT_ROOT.parent / "secret.json"
DEFAULT_BLUEPRINT = PROJECT_ROOT / "comsol" / "blueprints" / "source" / "Optics_COMSOL_Runtime_zyz.magnus.py"
DEFAULT_BLUEPRINT_PACKAGE = PROJECT_ROOT / ".magnus" / ".blueprints" / "Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml"
DEFAULT_BLUEPRINT_ID = "Optics_COMSOL_Runtime_zyz"


def load_secret(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def pick(data: dict, *keys: str, default: str | None = None) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def parse_kv(values: list[str]) -> dict:
    result: dict[str, object] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"--arg requires key=value, got: {item}")
        key, value = item.split("=", 1)
        value = value.strip()
        if value.lower() in {"true", "false"}:
            parsed: object = value.lower() == "true"
        elif value.lower() in {"none", "null"}:
            parsed = None
        else:
            parsed = value
        result[key.strip()] = parsed
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save and launch the COMSOL Magnus blueprint.")
    parser.add_argument("--blueprint", type=Path, default=DEFAULT_BLUEPRINT)
    parser.add_argument("--blueprint-package", type=Path, default=DEFAULT_BLUEPRINT_PACKAGE)
    parser.add_argument("--blueprint-id", default=DEFAULT_BLUEPRINT_ID)
    parser.add_argument("--title", default=DEFAULT_TITLE)
    parser.add_argument("--description", default=DEFAULT_DESCRIPTION)
    parser.add_argument("--secret-json", type=Path, default=SECRET_PATH)
    parser.add_argument("--address", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--site", choices=("gu", "default"), default="gu")
    parser.add_argument("--package-only", action="store_true")
    parser.add_argument("--save-only", action="store_true")
    parser.add_argument("--run-mode", choices=("env_check", "batch_java", "batch_mph", "batch_mfile"), default=None)
    parser.add_argument("--domain-preset", choices=("optics", "fluid", "generic"), default=None)
    parser.add_argument("--code-root", default=None)
    parser.add_argument("--license-mode", choices=("personal_storage", "server_env", "file_secret", "env_check_only"), default=None)
    parser.add_argument("--license-path", default=None)
    parser.add_argument("--input-file", default=None)
    parser.add_argument("--case-path", default=None)
    parser.add_argument("--case-bundle-secret", default=None)
    parser.add_argument("--license-file-secret", default=None)
    parser.add_argument("--postprocess-file", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--container-image", default=None)
    parser.add_argument("--cpu-count", type=int, default=None)
    parser.add_argument("--memory-demand", default=None)
    parser.add_argument("--ephemeral-storage", default=None)
    parser.add_argument("--priority", choices=("A1", "A2", "B1", "B2"), default=None)
    parser.add_argument("--arg", action="append", default=[], help="Blueprint argument as key=value. Repeatable.")
    parser.add_argument("--config", type=Path, default=None, help="Optional JSON object with blueprint args.")
    parser.add_argument("--wait-after-save", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_blueprint_package(
        source=args.blueprint,
        output=args.blueprint_package,
        blueprint_id=args.blueprint_id,
        title=args.title,
        description=args.description,
    )
    print(f"Packaged blueprint: {args.blueprint_package}")
    if args.package_only:
        return 0

    secret = load_secret(args.secret_json)
    if args.site == "gu":
        address = args.address or pick(secret, "magnus_address-gu", "magnus_address")
        token = args.token or pick(secret, "magnus_token-gu", "magnus_token")
    else:
        address = args.address or pick(secret, "magnus_address")
        token = args.token or pick(secret, "magnus_token")
    if not address or not token:
        raise SystemExit(f"Missing Magnus address/token in {args.secret_json}")

    code = args.blueprint.read_text(encoding="utf-8")
    magnus.configure(address=address, token=token)
    magnus.save_blueprint(
        blueprint_id=args.blueprint_id,
        title=args.title,
        description=args.description,
        code=code,
    )
    print(f"Saved blueprint: {args.blueprint_id}")
    if args.save_only:
        return 0

    bp_args: dict[str, object] = {}
    if args.config:
        with args.config.open("r", encoding="utf-8-sig") as fh:
            loaded = json.load(fh)
        if not isinstance(loaded, dict):
            raise SystemExit("--config must contain a JSON object")
        bp_args.update(loaded)
    direct_args = {
        "run_mode": args.run_mode,
        "domain_preset": args.domain_preset,
        "code_root": args.code_root,
        "license_mode": args.license_mode,
        "license_path": args.license_path,
        "input_file": args.input_file,
        "case_path": args.case_path,
        "case_bundle_secret": args.case_bundle_secret,
        "license_file_secret": args.license_file_secret,
        "postprocess_file": args.postprocess_file,
        "output_root": args.output_root,
        "run_id": args.run_id,
        "container_image": args.container_image,
        "cpu_count": args.cpu_count,
        "memory_demand": args.memory_demand,
        "ephemeral_storage": args.ephemeral_storage,
        "priority": args.priority,
    }
    bp_args.update({key: value for key, value in direct_args.items() if value is not None})
    bp_args.update(parse_kv(args.arg))

    if args.wait_after_save > 0:
        time.sleep(args.wait_after_save)
    job_id = magnus.launch_blueprint(args.blueprint_id, args=bp_args)
    print(f"Launched job: {job_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
