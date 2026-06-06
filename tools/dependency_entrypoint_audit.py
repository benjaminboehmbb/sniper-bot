#!/usr/bin/env python3
# tools/dependency_entrypoint_audit.py
# P24 Dependency and Entry-Point Audit.
# ASCII-only.

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(".").resolve()

EXCLUDE_PARTS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "backups",
    "archive",
}

TARGETS = [
    "live_l1.core.timing_5m",
    "live_l1.core.timing_5m_v2",
    "live_l1.io.valid",
    "live_l1.io.validate",
    "live_l1.core.loop",
    "live_l1.tools.safe_launch",
    "live_l1.tools.monitor_runtime",
    "live_l1.tools.runtime_control_loop",
    "scripts.run_live_l1_paper",
]


def is_excluded(path: Path) -> bool:
    return bool(set(path.parts).intersection(EXCLUDE_PARTS))


def iter_py_files() -> list[Path]:
    files = []
    for base in ["live_l1", "scripts", "tools", "engine"]:
        p = ROOT / base
        if not p.exists():
            continue
        for file_path in p.rglob("*.py"):
            rel = file_path.relative_to(ROOT)
            if not is_excluded(rel):
                files.append(rel)
    return sorted(files)


def module_from_path(path: Path) -> str:
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


def has_main_guard(path: Path) -> bool:
    full = ROOT / path
    try:
        text = full.read_text(encoding="utf-8")
    except Exception:
        return False

    return 'if __name__ == "__main__"' in text or "if __name__ == '__main__'" in text


def contains_argparse(path: Path) -> bool:
    full = ROOT / path
    try:
        text = full.read_text(encoding="utf-8")
    except Exception:
        return False

    return "argparse" in text


def main() -> int:
    files = iter_py_files()

    module_to_path = {
        module_from_path(path): path
        for path in files
    }

    imports_by_file = {
        str(path): parse_imports(path)
        for path in files
    }

    target_usage = {}

    for target in TARGETS:
        users = []
        for path_s, imports in imports_by_file.items():
            for imp in imports:
                if imp == target or imp.startswith(target + "."):
                    users.append(path_s)
                    break

        target_usage[target] = {
            "path": str(module_to_path.get(target, "")),
            "imported_by": sorted(users),
            "imported_by_count": len(users),
        }

    entrypoints = []

    for path in files:
        path_s = str(path)
        if has_main_guard(path) or contains_argparse(path):
            entrypoints.append(
                {
                    "path": path_s,
                    "module": module_from_path(path),
                    "has_main_guard": has_main_guard(path),
                    "uses_argparse": contains_argparse(path),
                }
            )

    live_entrypoints = [
        item for item in entrypoints
        if item["path"].startswith("live_l1/tools/")
        or item["path"] == "scripts/run_live_l1_paper.py"
    ]

    suspicious_zero_import_live = []

    for path in files:
        module = module_from_path(path)
        if not str(path).startswith("live_l1/"):
            continue

        users = []
        for path_s, imports in imports_by_file.items():
            for imp in imports:
                if imp == module or imp.startswith(module + "."):
                    users.append(path_s)
                    break

        if len(users) == 0 and not str(path).endswith("__init__.py"):
            suspicious_zero_import_live.append(str(path))

    payload = {
        "targets": target_usage,
        "live_entrypoints": live_entrypoints,
        "suspicious_zero_import_live": sorted(suspicious_zero_import_live),
    }

    out_dir = ROOT / "docs" / "inventory"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "DEPENDENCY_ENTRYPOINT_AUDIT_2026-06-06.json"
    md_path = out_dir / "DEPENDENCY_ENTRYPOINT_AUDIT_2026-06-06.md"

    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    with md_path.open("w", encoding="utf-8") as fh:
        fh.write("# DEPENDENCY AND ENTRY-POINT AUDIT\n\n")
        fh.write("Date: 2026-06-06\n")
        fh.write("Device: G15 / AR15\n")
        fh.write("Environment: WSL\n\n")

        fh.write("## Target Dependency Usage\n\n")
        for target in TARGETS:
            item = target_usage[target]
            fh.write(f"### {target}\n\n")
            fh.write(f"path: {item['path']}\n\n")
            fh.write(f"imported_by_count: {item['imported_by_count']}\n\n")
            if item["imported_by"]:
                for user in item["imported_by"]:
                    fh.write(f"- {user}\n")
            else:
                fh.write("- none\n")
            fh.write("\n")

        fh.write("## Live Entry-Point Candidates\n\n")
        for item in live_entrypoints:
            fh.write(
                f"- {item['path']} | main_guard={item['has_main_guard']} | argparse={item['uses_argparse']}\n"
            )

        fh.write("\n## Suspicious Zero-Import Live L1 Files\n\n")
        for path_s in sorted(suspicious_zero_import_live):
            fh.write(f"- {path_s}\n")

        fh.write("\n## Notes\n\n")
        fh.write("Zero-import files may still be valid CLI entry-points.\n")
        fh.write("Archive decisions require manual review.\n")

    print("P24 DEPENDENCY AND ENTRY-POINT AUDIT")
    print("python_files_scanned:", len(files))
    print("json_out:", json_path)
    print("md_out:", md_path)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
