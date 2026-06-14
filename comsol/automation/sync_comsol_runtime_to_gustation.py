from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = PROJECT_ROOT / "comsol" / "runtime"
DEFAULT_HOST = "zhangyuanzheng@Gustation"
DEFAULT_TARGET_ROOT = "/data/public/zhangyuanzheng/comsol-runtime"
SKIP_DIRS = {"__pycache__", ".git", ".pytest_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo"}


def run(cmd: list[str], *, dry_run: bool = False) -> None:
    print("+ " + " ".join(str(part) for part in cmd))
    if not dry_run:
        subprocess.run(cmd, check=True)


def sh_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Upload the private COMSOL runtime code folder to Gustation with scp.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--target-root", default=DEFAULT_TARGET_ROOT)
    parser.add_argument("--license-file", type=Path, default=None, help="Optional local license file to upload into secrets/comsol/license.dat.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def iter_files(source: Path):
    for root, dirs, files in os.walk(source):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        root_path = Path(root)
        for name in files:
            path = root_path / name
            if path.suffix in SKIP_SUFFIXES:
                continue
            yield path, path.relative_to(source)


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    if not source.is_dir():
        raise SystemExit(f"source folder not found: {source}")

    target_root = args.target_root.rstrip("/")
    run(["ssh", args.host, f"mkdir -p {sh_quote(target_root)} {sh_quote(target_root + '/secrets/comsol')}"], dry_run=args.dry_run)

    for local_file, relative in iter_files(source):
        remote_dir = f"{target_root}/{relative.parent.as_posix()}" if str(relative.parent) != "." else target_root
        run(["ssh", args.host, f"mkdir -p {sh_quote(remote_dir)}"], dry_run=args.dry_run)
        run(["scp", str(local_file), f"{args.host}:{remote_dir}/"], dry_run=args.dry_run)

    if args.license_file:
        license_file = args.license_file.resolve()
        if not license_file.is_file():
            raise SystemExit(f"license file not found: {license_file}")
        run(["scp", str(license_file), f"{args.host}:{target_root}/secrets/comsol/license.dat"], dry_run=args.dry_run)
        run(["ssh", args.host, f"chmod 700 {sh_quote(target_root + '/secrets')} {sh_quote(target_root + '/secrets/comsol')} && chmod 600 {sh_quote(target_root + '/secrets/comsol/license.dat')}"], dry_run=args.dry_run)

    print(f"Remote code root: {target_root}")
    print(f"Remote license path: {target_root}/secrets/comsol/license.dat")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
