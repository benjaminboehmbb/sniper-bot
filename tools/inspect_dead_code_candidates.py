#!/usr/bin/env python3
# tools/inspect_dead_code_candidates.py
# P25B Candidate Content Inspection.
# ASCII-only.

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(".").resolve()

CANDIDATES = [
    "live_l1/io/validate.py",
    "live_l1/core/gate_builder.py",
    "live_l1/core/regime_builder.py",
    "live_l1/core/regime_v2_builder.py",
    "live_l1/core/signal_builder.py",
    "live_l1/guards/cost_guards.py",
    "live_l1/core/timing_5m_v2.py",
    "tools/test_timing_5m_v2_minimal.py",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def parse_ast(text: str):
    try:
        return ast.parse(text)
    except Exception:
        return None


def extract_defs(tree) -> tuple[list[str], list[str]]:
    functions = []
    classes = []

    if tree is None:
        return functions, classes

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    return sorted(functions), sorted(classes)


def extract_imports(tree) -> list[str]:
    imports = []

    if tree is None:
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                imports.append(item.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return sorted(set(imports))


def classify(path_s: str, functions: list[str], classes: list[str], text: str) -> str:
    lower = text.lower()

    if path_s == "live_l1/io/validate.py":
        return "ARCHIVE_CANDIDATE_STRONG"

    if path_s == "live_l1/core/timing_5m_v2.py":
        return "KEEP_FUTURE_OR_EXPERIMENTAL_REVIEW"

    if path_s == "tools/test_timing_5m_v2_minimal.py":
        return "KEEP_WITH_TIMING_5M_V2_OR_ARCHIVE_TOGETHER"

    if "todo" in lower or "experimental" in lower or "shadow" in lower:
        return "KEEP_FUTURE_REVIEW"

    if functions or classes:
        return "CONTENT_PRESENT_REVIEW_REQUIRED"

    return "ARCHIVE_CANDIDATE_REVIEW"


def main() -> int:
    rows = []

    for rel in CANDIDATES:
        path = ROOT / rel
        text = read_text(path)
        tree = parse_ast(text)
        functions, classes = extract_defs(tree)
        imports = extract_imports(tree)

        preview_lines = []
        for line in text.splitlines()[:25]:
            preview_lines.append(line.rstrip())

        rows.append(
            {
                "path": rel,
                "exists": path.is_file(),
                "line_count": len(text.splitlines()) if text else 0,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "classification": classify(rel, functions, classes, text),
                "preview": preview_lines,
            }
        )

    out_dir = ROOT / "docs" / "inventory"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "P25B_CANDIDATE_CONTENT_INSPECTION_2026-06-06.json"
    md_path = out_dir / "P25B_CANDIDATE_CONTENT_INSPECTION_2026-06-06.md"

    json_path.write_text(
        json.dumps(rows, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    with md_path.open("w", encoding="utf-8") as fh:
        fh.write("# P25B CANDIDATE CONTENT INSPECTION\n\n")
        fh.write("Date: 2026-06-06\n")
        fh.write("Device: G15 / AR15\n")
        fh.write("Environment: WSL\n\n")

        for row in rows:
            fh.write(f"## {row['path']}\n\n")
            fh.write(f"exists: {row['exists']}\n\n")
            fh.write(f"line_count: {row['line_count']}\n\n")
            fh.write(f"classification: {row['classification']}\n\n")

            fh.write("functions:\n\n")
            if row["functions"]:
                for item in row["functions"]:
                    fh.write(f"- {item}\n")
            else:
                fh.write("- none\n")
            fh.write("\n")

            fh.write("classes:\n\n")
            if row["classes"]:
                for item in row["classes"]:
                    fh.write(f"- {item}\n")
            else:
                fh.write("- none\n")
            fh.write("\n")

            fh.write("imports:\n\n")
            if row["imports"]:
                for item in row["imports"]:
                    fh.write(f"- {item}\n")
            else:
                fh.write("- none\n")
            fh.write("\n")

            fh.write("preview:\n\n")
            fh.write("```text\n")
            for line in row["preview"]:
                fh.write(line + "\n")
            fh.write("```\n\n")

    print("P25B CANDIDATE CONTENT INSPECTION")
    print("candidates:", len(rows))
    print("json_out:", json_path)
    print("md_out:", md_path)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
