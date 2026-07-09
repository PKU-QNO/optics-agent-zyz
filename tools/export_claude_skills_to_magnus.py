from __future__ import annotations

import argparse
import base64
import re
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised only on missing dependency.
    raise SystemExit("PyYAML is required. Install it with: python -m pip install pyyaml") from exc


DEFAULT_VERSION = "1.0"
DEFAULT_EXCLUDES = {".DS_Store", "Thumbs.db"}
DEFAULT_EXCLUDED_DIRS = {".git", "__pycache__"}


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


def parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data = yaml.safe_load(text[4:end]) or {}
    return data if isinstance(data, dict) else {}


def first_markdown_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or None
    return None


def normalize_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value).strip("-")
    return cleaned.lower() or "unnamed-skill"


def normalize_package_path(path: str) -> str:
    candidate = path.replace("\\", "/")
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"Unsafe package path: {path!r}")
    return pure.as_posix()


def iter_source_files(source_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(source_dir).parts
        if any(part in DEFAULT_EXCLUDED_DIRS for part in rel_parts):
            continue
        if path.name in DEFAULT_EXCLUDES or path.suffix == ".pyc":
            continue
        files.append(path)
    return sorted(files, key=lambda p: p.relative_to(source_dir).as_posix().lower())


def package_file_entry(path: Path, source_dir: Path) -> dict[str, str]:
    relative = normalize_package_path(path.relative_to(source_dir).as_posix())
    data = path.read_bytes()
    try:
        content = data.decode("utf-8")
    except UnicodeDecodeError:
        return {
            "path": relative,
            "encoding": "base64",
            "content": base64.b64encode(data).decode("ascii"),
        }
    return {"path": relative, "content": content}


def build_skill_package(
    *,
    source_dir: Path,
    source_rel: PurePosixPath,
    workspace_label: str,
    exported_at: str,
) -> dict[str, Any]:
    skill_md = source_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    source_id = normalize_id(f"{workspace_label}-claude-skills-{source_rel.as_posix()}")
    title = first_markdown_heading(text) or str(frontmatter.get("name") or source_rel.name)
    description = str(frontmatter.get("description") or "")
    files = [package_file_entry(path, source_dir) for path in iter_source_files(source_dir)]
    return {
        "kind": "magnus/skill",
        "version": DEFAULT_VERSION,
        "payload": {
            "id": source_id,
            "title": title,
            "description": description,
            "files": files,
        },
        "exported_at": exported_at,
    }


def build_agent_package(
    *,
    agent_md: Path,
    workspace_label: str,
    exported_at: str,
) -> dict[str, Any]:
    text = agent_md.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    source_id = normalize_id(f"{workspace_label}-claude-agents-{agent_md.stem}")
    title = first_markdown_heading(text) or str(frontmatter.get("name") or agent_md.stem)
    description = str(frontmatter.get("description") or "")
    return {
        "kind": "magnus/skill",
        "version": DEFAULT_VERSION,
        "payload": {
            "id": source_id,
            "title": title,
            "description": description,
            "files": [
                {
                    "path": "SKILL.md",
                    "content": text,
                }
            ],
        },
        "exported_at": exported_at,
    }


def export_workspace(
    *,
    workspace_label: str,
    workspace_root: Path,
    output_root: Path,
    exported_at: str,
) -> tuple[int, int]:
    skill_count = 0
    agent_count = 0

    skill_root = workspace_root / ".claude" / "skills"
    if skill_root.is_dir():
        skill_dirs = sorted(
            [path.parent for path in skill_root.rglob("SKILL.md")],
            key=lambda p: p.relative_to(skill_root).as_posix().lower(),
        )
        for source_dir in skill_dirs:
            source_rel = PurePosixPath(source_dir.relative_to(skill_root).as_posix())
            package = build_skill_package(
                source_dir=source_dir,
                source_rel=source_rel,
                workspace_label=workspace_label,
                exported_at=exported_at,
            )
            destination_dir = output_root / workspace_label / "claude-skills" / Path(*source_rel.parent.parts)
            destination = destination_dir / f"{source_rel.name}.magnusskill.yaml"
            write_yaml(destination, package)
            skill_count += 1

    agent_root = workspace_root / ".claude" / "agents"
    if agent_root.is_dir():
        for agent_md in sorted(agent_root.glob("*.md"), key=lambda p: p.name.lower()):
            package = build_agent_package(agent_md=agent_md, workspace_label=workspace_label, exported_at=exported_at)
            destination = output_root / workspace_label / "claude-agents" / f"{agent_md.stem}.magnusskill.yaml"
            write_yaml(destination, package)
            agent_count += 1

    return skill_count, agent_count


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Export optics_agent and SEPR .claude skills/agents as classified magnus/skill YAML packages."
    )
    parser.add_argument("--optics-root", type=Path, default=repo_root, help="optics_agent workspace root.")
    parser.add_argument(
        "--sepr-root",
        type=Path,
        default=repo_root.parent / "self-evo-paper-repro",
        help="SEPR sister workspace root.",
    )
    parser.add_argument("--output-root", type=Path, default=repo_root / ".magnus", help="Output .magnus root.")
    parser.add_argument("--exported-at", default=utc_timestamp(), help="Override exported_at timestamp.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    total_skills = 0
    total_agents = 0

    for workspace_label, workspace_root in [
        ("optics-agent", args.optics_root.resolve()),
        ("sepr", args.sepr_root.resolve()),
    ]:
        skill_count, agent_count = export_workspace(
            workspace_label=workspace_label,
            workspace_root=workspace_root,
            output_root=output_root,
            exported_at=args.exported_at,
        )
        total_skills += skill_count
        total_agents += agent_count
        print(f"{workspace_label}: exported {skill_count} skills and {agent_count} agents")

    print(f"Total: exported {total_skills} skills and {total_agents} agents to {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
