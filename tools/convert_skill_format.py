from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only on missing dependency.
    raise SystemExit("PyYAML is required. Install it with: python -m pip install pyyaml") from exc


DEFAULT_VERSION = "1.0"
DEFAULT_EXCLUDES = {
    ".DS_Store",
    "Thumbs.db",
}
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
}


class LiteralDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        return super().increase_indent(flow, False)


def str_presenter(dumper: yaml.SafeDumper, value: str) -> yaml.nodes.ScalarNode:
    if "\n" in value:
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", value)


LiteralDumper.add_representer(str, str_presenter)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a YAML mapping")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    text = yaml.dump(
        data,
        Dumper=LiteralDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=120,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def parse_skill_frontmatter(skill_md: Path) -> dict[str, Any]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    frontmatter = text[4:end]
    data = yaml.safe_load(frontmatter) or {}
    if not isinstance(data, dict):
        return {}
    return data


def first_markdown_heading(skill_md: Path) -> str | None:
    for line in skill_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def normalize_package_path(path: str) -> str:
    candidate = path.replace("\\", "/")
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"Unsafe package path: {path!r}")
    return pure.as_posix()


def destination_for_package_path(root: Path, package_path: str) -> Path:
    normalized = normalize_package_path(package_path)
    destination = (root / Path(*PurePosixPath(normalized).parts)).resolve()
    root_resolved = root.resolve()
    if destination != root_resolved and root_resolved not in destination.parents:
        raise ValueError(f"Package path escapes output directory: {package_path!r}")
    return destination


def iter_skill_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(source_dir).parts
        if any(part in DEFAULT_EXCLUDED_DIRS for part in rel_parts):
            continue
        if path.name in DEFAULT_EXCLUDES:
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(source_dir).as_posix().lower())


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Skill package files must be UTF-8 text, but {path} is not decodable") from exc


def codex_to_magnus(args: argparse.Namespace) -> int:
    source_dir = args.source.resolve()
    output = args.output.resolve()
    if not source_dir.is_dir():
        raise FileNotFoundError(f"Codex skill directory does not exist: {source_dir}")

    skill_md = source_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Codex skill directory must contain SKILL.md: {source_dir}")

    frontmatter = parse_skill_frontmatter(skill_md)
    skill_id = args.skill_id or frontmatter.get("name") or source_dir.name
    description = args.description or frontmatter.get("description") or ""
    title = args.title or first_markdown_heading(skill_md) or skill_id

    payload_files = []
    for path in iter_skill_files(source_dir):
        relative = path.relative_to(source_dir).as_posix()
        payload_files.append(
            {
                "path": relative,
                "content": read_text_file(path),
            }
        )

    package = {
        "kind": "magnus/skill",
        "version": DEFAULT_VERSION,
        "payload": {
            "id": str(skill_id),
            "title": str(title),
            "description": str(description),
            "files": payload_files,
        },
        "exported_at": args.exported_at or utc_timestamp(),
    }
    write_yaml(output, package)
    print(f"Wrote Magnus skill package: {output}")
    print(f"Packaged {len(payload_files)} files from: {source_dir}")
    return 0


def magnus_to_codex(args: argparse.Namespace) -> int:
    source = args.source.resolve()
    output_dir = args.output.resolve()
    data = load_yaml(source)

    if data.get("kind") != "magnus/skill":
        raise ValueError(f"Expected kind: magnus/skill, got {data.get('kind')!r}")
    payload = data.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Magnus skill package is missing payload mapping")
    files = payload.get("files")
    if not isinstance(files, list):
        raise ValueError("Magnus skill package is missing payload.files list")

    if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
        raise FileExistsError(f"Output directory is not empty; pass --force to overwrite files: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    for item in files:
        if not isinstance(item, dict):
            raise ValueError("Each payload.files entry must be a mapping")
        package_path = item.get("path")
        content = item.get("content")
        if not isinstance(package_path, str):
            raise ValueError("Each payload.files entry requires a string path")
        if not isinstance(content, str):
            raise ValueError(f"payload.files entry {package_path!r} requires string content")

        destination = destination_for_package_path(output_dir, package_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="\n")
        written += 1

    if not (output_dir / "SKILL.md").is_file():
        raise ValueError(f"Magnus skill package did not contain SKILL.md: {source}")

    print(f"Wrote Codex skill directory: {output_dir}")
    print(f"Restored {written} files from: {source}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert skills between directory-style Codex skills and magnus/skill YAML packages."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    to_magnus = subparsers.add_parser("codex-to-magnus", help="Package a Codex skill directory as magnus/skill YAML.")
    to_magnus.add_argument("source", type=Path, help="Codex skill directory containing SKILL.md.")
    to_magnus.add_argument("output", type=Path, help="Output .magnus.skill.yaml path.")
    to_magnus.add_argument("--id", dest="skill_id", help="Override payload.id; defaults to SKILL.md frontmatter name.")
    to_magnus.add_argument("--title", help="Override payload.title; defaults to the first H1 in SKILL.md.")
    to_magnus.add_argument(
        "--description",
        help="Override payload.description; defaults to SKILL.md frontmatter description.",
    )
    to_magnus.add_argument("--exported-at", help="Override exported_at timestamp.")
    to_magnus.set_defaults(func=codex_to_magnus)

    to_codex = subparsers.add_parser("magnus-to-codex", help="Restore a magnus/skill YAML package to a Codex skill dir.")
    to_codex.add_argument("source", type=Path, help="Input magnus/skill YAML package.")
    to_codex.add_argument("output", type=Path, help="Output Codex skill directory.")
    to_codex.add_argument("--force", action="store_true", help="Allow overwriting files in a non-empty output dir.")
    to_codex.set_defaults(func=magnus_to_codex)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
