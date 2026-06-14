from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SECRET_PATH = PROJECT_ROOT.parent / "secret.json"
CONTAINERS_DIR = Path(__file__).resolve().parent

DEFAULT_COMSOL_SETUP = Path(r"D:\docker-base\COMSOL Multiphysics 6.3.0.290\Setup")
DEFAULT_TAG = "6.3-zyz-v1"
DEFAULT_REPO = "comsol-runtime"
DEFAULT_ACR_REGISTRY = "crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com"
DEFAULT_ACR_NAMESPACE = "zyz25"
DEFAULT_PKU_REGISTRY = "git.pku.edu.cn"
DEFAULT_PKU_NAMESPACE = "rise-agi"

FORBIDDEN_NAMES = {
    "crack",
    "ssq",
    "keygen",
    "patch",
    "license.dat",
    "license.trial",
    "licenseinfo.ini",
}
SETUP_COPY_IGNORE = {
    "setup.exe",
    "autorun.inf",
    "comsol.ico",
    "comsol.icns",
    "COMSOL_MultiphysicsInstallationGuide.pdf",
    "COMSOL_ReleaseNotes.pdf",
    "COMSOL_ServerManual.pdf",
}
PY_IMPORTS = "import numpy, scipy, pandas, matplotlib, h5py, meshio, mph, jpype; print('python deps ok')"


class ToolError(RuntimeError):
    pass


def load_secret() -> dict:
    if not SECRET_PATH.exists():
        return {}
    try:
        with SECRET_PATH.open("r", encoding="utf-8-sig") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ToolError(f"Invalid JSON in {SECRET_PATH}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def pick(mapping: dict, *names: str, default: str | None = None) -> str | None:
    for name in names:
        value = mapping.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    input_text: str | None = None,
    capture: bool = False,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    printable = " ".join(cmd)
    print(f"+ {printable}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            input=input_text,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=capture,
            check=False,
            env=env,
        )
    except FileNotFoundError as exc:
        raise ToolError(f"Command not found: {cmd[0]}") from exc
    if result.returncode != 0:
        details = ""
        if capture:
            if result.stdout:
                details += f"\n[stdout]\n{result.stdout.strip()}"
            if result.stderr:
                details += f"\n[stderr]\n{result.stderr.strip()}"
        raise ToolError(f"Command failed with exit={result.returncode}: {printable}{details}")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and optionally push the COMSOL 6.3 headless runtime image.")
    parser.add_argument("--registry", choices=("acr", "gitpku"), default="acr")
    parser.add_argument("--tag", default=DEFAULT_TAG)
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--comsol-setup", type=Path, default=DEFAULT_COMSOL_SETUP)
    parser.add_argument("--secret-json", type=Path, default=SECRET_PATH)
    parser.add_argument("--license-file", type=Path, default=None, help="Build-time COMSOL license file, if required by installer.")
    parser.add_argument("--license-server", default=None, help="Build-time COMSOL license server, for example 1718@host.")
    parser.add_argument("--install-license", default=None, help="Explicit installer license value. Prefer --license-file or --license-server.")
    parser.add_argument("--no-push", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-smoke", action="store_true")
    parser.add_argument("--keep-context", action="store_true")
    parser.add_argument("--context-dir", type=Path, default=None)
    return parser.parse_args()


def registry_config(secret: dict, target: str, repo: str) -> dict:
    if target == "acr":
        acr = secret.get("acr", {})
        if not isinstance(acr, dict):
            acr = {}
        registry = pick(acr, "registry", "registry_public", default=DEFAULT_ACR_REGISTRY)
        namespace = pick(acr, "namespace", default=DEFAULT_ACR_NAMESPACE)
        username = pick(acr, "username", "user")
        password = pick(acr, "password", "token")
    else:
        pku = secret.get("docker_registry_git_pku", {})
        if not isinstance(pku, dict):
            pku = {}
        registry = pick(pku, "registry", "registry_url", default=DEFAULT_PKU_REGISTRY)
        namespace = pick(pku, "namespace", "organization", default=DEFAULT_PKU_NAMESPACE).lower()
        username = pick(pku, "username", "user")
        password = pick(pku, "token", "password")
    return {
        "registry": registry,
        "namespace": namespace,
        "username": username,
        "password": password,
        "image": f"{registry}/{namespace}/{repo}",
    }


def validate_setup_dir(setup_dir: Path) -> Path:
    setup_dir = setup_dir.expanduser().resolve()
    required = ["setup", "setupconfig.ini", "archives", "bin"]
    missing = [name for name in required if not (setup_dir / name).exists()]
    if missing:
        raise ToolError(f"COMSOL setup directory is missing {missing}: {setup_dir}")
    if "Crack" in {p.name for p in setup_dir.iterdir()}:
        raise ToolError(f"Refusing setup directory that directly contains Crack/: {setup_dir}")
    return setup_dir


def scan_path_forbidden(root: Path, *, allow_setup_license_text: bool = False) -> list[Path]:
    hits: list[Path] = []
    for path in root.rglob("*"):
        name = path.name.lower()
        if name in FORBIDDEN_NAMES:
            if allow_setup_license_text and name == "license_en_us.txt":
                continue
            hits.append(path)
    return hits


def ignore_setup_items(_dir: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        lower = name.lower()
        if lower in {item.lower() for item in SETUP_COPY_IGNORE}:
            ignored.add(name)
        if lower in FORBIDDEN_NAMES:
            ignored.add(name)
    return ignored


def resolve_build_license(args: argparse.Namespace, secret: dict) -> str:
    if args.install_license:
        return args.install_license
    if args.license_server:
        return args.license_server
    if args.license_file:
        return "/run/secrets/comsol_license"
    env_license = os.getenv("COMSOL_INSTALL_LICENSE")
    if env_license:
        return env_license
    comsol_secret = secret.get("comsol", {})
    if not isinstance(comsol_secret, dict):
        comsol_secret = {}
    if pick(comsol_secret, "install_license", "build_license"):
        return pick(comsol_secret, "install_license", "build_license")
    if pick(comsol_secret, "license_server", "build_license_server"):
        args.license_server = pick(comsol_secret, "license_server", "build_license_server")
        return args.license_server
    license_file = pick(comsol_secret, "license_file", "build_license_file", "install_license_file")
    if license_file:
        args.license_file = Path(license_file)
        return "/run/secrets/comsol_license"
    raise ToolError(
        "COMSOL installer requires a build-time license value. "
        "Pass --license-file <path>, --license-server <port@host>, set COMSOL_INSTALL_LICENSE, "
        "or add a comsol build license entry to secret.json."
    )


def prepare_context(args: argparse.Namespace, install_license: str) -> Path:
    setup_dir = validate_setup_dir(args.comsol_setup)
    context_dir = args.context_dir.expanduser().resolve() if args.context_dir else Path(tempfile.mkdtemp(prefix="comsol-runtime-build-"))
    if context_dir.exists() and any(context_dir.iterdir()):
        raise ToolError(f"Context directory must be empty: {context_dir}")
    context_dir.mkdir(parents=True, exist_ok=True)

    print(f"Preparing clean Docker context: {context_dir}")
    shutil.copytree(setup_dir, context_dir / "Setup", ignore=ignore_setup_items)

    template = (CONTAINERS_DIR / "comsol-setupconfig.template.ini").read_text(encoding="utf-8")
    config = template.replace("${COMSOL_INSTALL_LICENSE}", install_license)
    (context_dir / "setupconfig-docker.ini").write_text(config, encoding="utf-8", newline="\n")

    forbidden = scan_path_forbidden(context_dir)
    if forbidden:
        formatted = "\n".join(str(p) for p in forbidden[:20])
        raise ToolError(f"Forbidden files found in build context:\n{formatted}")
    return context_dir


def docker_preflight() -> None:
    run(["docker", "version", "--format", "{{.Server.Version}}"], capture=True)


def build_image(context_dir: Path, image_ref: str, args: argparse.Namespace) -> None:
    env = os.environ.copy()
    env["DOCKER_BUILDKIT"] = "1"
    cmd = [
        "docker",
        "build",
        "--pull=false",
        "-f",
        str(CONTAINERS_DIR / "comsol-runtime.Containerfile"),
        "-t",
        image_ref,
    ]
    if args.license_file:
        license_path = args.license_file.expanduser().resolve()
        if not license_path.exists():
            raise ToolError(f"Build-time license file does not exist: {license_path}")
        cmd.extend(["--secret", f"id=comsol_license,src={license_path}"])
    cmd.append(str(context_dir))
    run(cmd, env=env)


def smoke_image(image_ref: str) -> None:
    run(["docker", "run", "--rm", image_ref, "comsol", "-version"])
    run(["docker", "run", "--rm", image_ref, "comsol", "batch", "-help"])
    run(["docker", "run", "--rm", image_ref, "python", "-c", PY_IMPORTS])


def scan_image(image_ref: str) -> None:
    script = (
        "set -eu; "
        "hits=$(find / -iname license.dat -o -iname license.trial -o -iname licenseinfo.ini "
        "-o -iname Crack -o -iname SSQ -o -iname keygen -o -iname patch 2>/dev/null | head -50); "
        "if [ -n \"$hits\" ]; then echo \"$hits\"; exit 23; fi; "
        "echo 'secret scan ok'"
    )
    run(["docker", "run", "--rm", image_ref, "bash", "-lc", script])


def docker_login(registry: str, username: str | None, password: str | None) -> None:
    if not username or not password:
        raise ToolError(f"Missing registry credentials for {registry}; update {SECRET_PATH}")
    run(["docker", "login", registry, "--username", username, "--password-stdin"], input_text=password, capture=True)


def push_image(image_ref: str) -> None:
    run(["docker", "push", image_ref])


def main() -> int:
    args = parse_args()
    global SECRET_PATH
    SECRET_PATH = args.secret_json.expanduser().resolve()
    secret = load_secret()
    reg = registry_config(secret, args.registry, args.repo)
    image_ref = f"{reg['image']}:{args.tag}"

    context_dir: Path | None = None
    try:
        print(f"Target image: {image_ref}")
        docker_preflight()
        if not args.skip_build:
            install_license = resolve_build_license(args, secret)
            context_dir = prepare_context(args, install_license)
            build_image(context_dir, image_ref, args)
        if not args.skip_smoke:
            smoke_image(image_ref)
            scan_image(image_ref)
        if not args.no_push:
            docker_login(reg["registry"], reg["username"], reg["password"])
            push_image(image_ref)
        print(f"COMSOL runtime image ready: {image_ref}")
        return 0
    except ToolError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    finally:
        if context_dir and context_dir.exists() and not args.keep_context:
            shutil.rmtree(context_dir, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
