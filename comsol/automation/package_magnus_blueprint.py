from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BLUEPRINT_ID = "Optics_COMSOL_Runtime_zyz"
DEFAULT_SOURCE = PROJECT_ROOT / "comsol" / "blueprints" / "source" / "Optics_COMSOL_Runtime_zyz.magnus.py"
DEFAULT_OUTPUT = PROJECT_ROOT / ".magnus" / ".blueprints" / "Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml"
DEFAULT_TITLE = "Optics COMSOL Runtime zyz"
DEFAULT_DESCRIPTION = "COMSOL runtime launcher. Public blueprint, private runner and license live in server storage."


def yaml_double_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", "\\n")
    return f'"{escaped}"'


def indent_block(value: str, spaces: int = 4) -> str:
    prefix = " " * spaces
    lines = value.splitlines()
    if value.endswith("\n"):
        lines.append("")
    return "\n".join(prefix + line for line in lines)


def write_blueprint_package(
    *,
    source: Path,
    output: Path,
    blueprint_id: str = DEFAULT_BLUEPRINT_ID,
    title: str = DEFAULT_TITLE,
    description: str = DEFAULT_DESCRIPTION,
) -> None:
    code = source.read_text(encoding="utf-8")
    exported_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    description_block = indent_block(description, 4)
    code_block = indent_block(code, 4)
    text = (
        "kind: magnus/blueprint\n"
        'version: "1.0"\n'
        "payload:\n"
        f"  id: {yaml_double_quote(blueprint_id)}\n"
        f"  title: {yaml_double_quote(title)}\n"
        "  description: |-\n"
        f"{description_block}\n"
        "  code: |\n"
        f"{code_block}\n"
        f"exported_at: {yaml_double_quote(exported_at)}\n"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a raw Magnus Python blueprint into .magnus.blueprint.yaml.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--blueprint-id", default=DEFAULT_BLUEPRINT_ID)
    parser.add_argument("--title", default=DEFAULT_TITLE)
    parser.add_argument("--description", default=DEFAULT_DESCRIPTION)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_blueprint_package(
        source=args.source,
        output=args.output,
        blueprint_id=args.blueprint_id,
        title=args.title,
        description=args.description,
    )
    print(f"Wrote blueprint package: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
