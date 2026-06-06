#!/usr/bin/env python3
# tools/repository_usage_audit.py
# P23 Repository Usage Audit.
# ASCII-only.

from __future__ import annotations

import ast
import json
import os
from pathlib import Path


ROOT = Path(".").resolve()

EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "backups",
    "archive",
}

SCAN_DIRS = [
    "live_l1",
    "scripts",
    "tools",
    "engine",
]


def is_excluded(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts.intersection(EXCLUDE_DIRS))


def iter_python_files() -> list[Path]:
    out = []
    for base in SCAN_DIRS:
        p = ROOT / base
        if not p.exists():
            continue
        for file_path in p.rglob("*.py"):
            rel = file_path.relative_to(ROOT)
            if is_excluded(rel):
                continue
            out.append(rel)
    return sorted(out)


def module_name_from_path(path: Path) -> str:
    if path.name == "__init__.py":
        return ".".join(path.with_suffix("").parts[:-1])
    return ".".join(path.with_suffix("").parts)


def parse_imports(path: Path) -> list[str]:
    full = ROOT / path
    try:
        tree = ast.parse(full.read_text(encoding="utf-8"))
    except Exception:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                imports.append(item.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return sorted(set(imports))


def classify_file(path: Path, imported_by_count: int) -> str:
    s = str(path)

    if s.startswith("live_l1/"):
        if "/tools/test_" in s or Path(s).name.startswith("test_"):
            return "TEST_TOOL"
        if s.startswith("live_l1/tools/"):
            return "ACTIVE_TOOL_OR_ENTRYPOINT"
        return "ACTIVE_CORE"

    if s.startswith("engine/"):
        return "ACTIVE_OR_ANALYSIS_ENGINE"

    if s.startswith("tools/"):
        if imported_by_count > 0:
            return "ACTIVE_SUPPORT_TOOL"
        return "STANDALONE_TOOL_REVIEW"

    if s.startswith("scripts/state_research/"):
        return "RESEARCH_ARCHIVE_CANDIDATE"

    if s.startswith("scripts/"):
        if s == "scripts/run_live_l1_paper.py":
            return "LIVE_ENTRYPOINT_REVIEW"
        return "RESEARCH_OR_BATCH_SCRIPT_REVIEW"

    return "UNKNOWN"


def main() -> int:
    files = iter_python_files()

    modules = {
        module_name_from_path(path): str(path)
        for path in files
    }

    imports_by_file = {}
    imported_by = {str(path): [] for path in files}

    for path in files:
        imports = parse_imports(path)
        imports_by_file[str(path)] = imports

        for imp in imports:
            for mod, mod_path in modules.items():
                if imp == mod or imp.startswith(mod + "."):
                    imported_by[mod_path].append(str(path))

    rows = []

    for path in files:
        path_s = str(path)
        users = sorted(set(imported_by.get(path_s, [])))
        classification = classify_file(path, len(users))

        rows.append(
            {
                "path": path_s,
                "module": module_name_from_path(path),
                "classification": classification,
                "imported_by_count": len(users),
                "imported_by": users,
                "imports": imports_by_file.get(path_s, []),
            }
        )

    out_dir = ROOT / "docs" / "inventory"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "REPOSITORY_USAGE_AUDIT_2026-06-06.json"
    md_path = out_dir / "REPOSITORY_USAGE_AUDIT_2026-06-06.md"

    json_path.write_text(
        json.dumps(rows, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    groups = {}
    for row in rows:
        groups.setdefault(row["classification"], []).append(row)

    with md_path.open("w", encoding="utf-8") as fh:
        fh.write("# REPOSITORY USAGE AUDIT\n\n")
        fh.write("Date: 2026-06-06\n")
        fh.write("Device: G15 / AR15\n")
        fh.write("Environment: WSL\n\n")
        fh.write("## Summary\n\n")
        fh.write(f"Python files scanned: {len(rows)}\n\n")

        for name in sorted(groups.keys()):
            fh.write(f"- {name}: {len(groups[name])}\n")

        fh.write("\n## Classification Details\n\n")

        for name in sorted(groups.keys()):
            fh.write(f"### {name}\n\n")
            for row in sorted(groups[name], key=lambda x: x["path"]):
                fh.write(f"- {row['path']} | imported_by={row['imported_by_count']}\n")
            fh.write("\n")

        fh.write("## Notes\n\n")
        fh.write("This audit is a static import and path classification scan.\n")
        fh.write("It does not prove that a standalone script is unused.\n")
        fh.write("Archive decisions require an additional manual review.\n")

    print("P23 REPOSITORY USAGE AUDIT")
    print("python_files_scanned:", len(rows))
    print("json_out:", json_path)
    print("md_out:", md_path)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
