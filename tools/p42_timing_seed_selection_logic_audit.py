#!/usr/bin/env python3
# P42 Timing Seed Selection Logic Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGET = Path("live_l1/core/timing_5m.py")
DOC = Path("docs/review/P42_TIMING_SEED_SELECTION_LOGIC_AUDIT_2026-06-06.md")

KEYWORDS = [
    "def _seed_score",
    "def _pick_best_seed",
    "def compute_5m_timing_vote",
    "seed.direction",
    "return -abs",
    "return abs",
    "best_score",
    "score",
    "strength",
]


def collect_context(lines: list[str], hit_idx: int, before: int = 5, after: int = 12) -> list[tuple[int, str]]:
    start = max(0, hit_idx - before)
    end = min(len(lines), hit_idx + after + 1)
    return [(i + 1, lines[i]) for i in range(start, end)]


def main() -> int:
    if not TARGET.exists():
        print("ERROR: missing target:", TARGET)
        return 1

    lines = TARGET.read_text(encoding="utf-8", errors="replace").splitlines()

    blocks = []
    seen = set()

    for i, line in enumerate(lines):
        if any(k in line for k in KEYWORDS):
            ctx = collect_context(lines, i)
            key = tuple(n for n, _ in ctx)
            if key not in seen:
                seen.add(key)
                blocks.append(ctx)

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P42 TIMING SEED SELECTION LOGIC AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Audit the 5m timing seed scoring and selection logic after P41 showed that short seeds do not win in isolated tests.\n\n")

        out.write("## Target File\n\n")
        out.write(f"{TARGET}\n\n")

        out.write("## Relevant Source Context\n\n")
        for idx, block in enumerate(blocks, start=1):
            out.write(f"### Context {idx}\n\n")
            out.write("```text\n")
            for line_no, text in block:
                out.write(f"{line_no}: {text}\n")
            out.write("```\n\n")

        out.write("## Preliminary Findings\n\n")
        out.write("- P41 showed that negative input signals still selected the long seed.\n")
        out.write("- This indicates that seed selection is not currently direction-aware with respect to signal polarity.\n")
        out.write("- The audit must confirm whether _seed_score() uses only seed weights and direction, but not current signal values.\n")
        out.write("- If true, short seeds cannot win based on negative market signals alone.\n\n")

        out.write("## Required Next Step\n\n")
        out.write("Review this audit output and design a polarity-aware seed scoring model before patching.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P42 TIMING SEED SELECTION LOGIC AUDIT")
    print("doc_out:", DOC)
    print("contexts:", len(blocks))
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
