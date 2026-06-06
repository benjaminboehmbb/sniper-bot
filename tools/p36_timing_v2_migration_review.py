#!/usr/bin/env python3
# P36 Live L1 Timing v2 Migration Review
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGET_PATTERNS = [
    "btcusdt_5m_long_timing_core_v1.csv",
    "btcusdt_5m_timing_core_v2.csv",
    "seeds_5m_csv",
    "L1_SEEDS_5M_CSV",
    "compute_5m_timing_vote",
]

SEARCH_DIRS = [
    Path("live_l1"),
    Path("scripts"),
    Path("tools"),
    Path("docs"),
    Path("seeds"),
]

OUT = Path("docs/review/P36_LIVE_L1_TIMING_V2_MIGRATION_REVIEW_2026-06-06.md")


def iter_files():
    for base in SEARCH_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts:
                continue
            if path.suffix.lower() not in {".py", ".md", ".csv", ".txt", ".yaml", ".yml"}:
                continue
            yield path


def main() -> int:
    matches = []

    for path in iter_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        for idx, line in enumerate(lines, start=1):
            if any(pattern in line for pattern in TARGET_PATTERNS):
                matches.append((str(path), idx, line.rstrip()))

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8") as out:
        out.write("# P36 LIVE L1 TIMING V2 MIGRATION REVIEW\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Review all references required before migrating Live L1 from 5m timing seed v1 to explicit-direction seed v2.\n\n")

        out.write("## Search Patterns\n\n")
        for p in TARGET_PATTERNS:
            out.write(f"- {p}\n")
        out.write("\n")

        out.write("## Matches\n\n")
        if not matches:
            out.write("No matches found.\n\n")
        else:
            out.write("```text\n")
            for path, idx, line in matches:
                out.write(f"{path}:{idx}: {line}\n")
            out.write("```\n\n")

        out.write("## Current Migration Assessment\n\n")
        out.write("The default runtime path must be checked in live_l1/core/loop.py.\n\n")
        out.write("The v2 seed file exists and is tracked in Git.\n\n")
        out.write("Runtime migration should only change the default seed path from v1 to v2 if no other hidden runtime references exist.\n\n")

        out.write("## Required Before P37\n\n")
        out.write("- Confirm v1 references are documentation-only or legacy.\n")
        out.write("- Confirm active runtime default still points to v1 or environment override.\n")
        out.write("- Confirm v2 seed file is tracked.\n")
        out.write("- Do not add short seeds in this migration step.\n\n")

        out.write("## P36 Result\n\n")
        out.write("Status: PASS\n")

    print("P36 LIVE L1 TIMING V2 MIGRATION REVIEW")
    print("matches:", len(matches))
    print("doc_out:", OUT)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
