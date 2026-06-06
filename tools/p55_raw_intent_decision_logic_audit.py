#!/usr/bin/env python3
# P55 Raw Intent Decision Logic Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGET = Path("live_l1/core/intent.py")
DOC = Path("docs/review/P55_RAW_INTENT_DECISION_LOGIC_AUDIT_2026-06-06.md")

KEYWORDS = [
    "def compute_1m_intent_raw",
    "BUY",
    "SELL",
    "HOLD",
    "current_position",
    "score",
    "entry_score",
    "ma200_signal",
    "mfi_signal",
    "rsi_signal",
    "stoch_signal",
    "threshold",
    "return",
]


def collect_context(lines: list[str], hit_idx: int, before: int = 12, after: int = 22):
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
        out.write("# P55 RAW INTENT DECISION LOGIC AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Audit why strong post-fix entry scores in P54 still produced HOLD raw intents.\n\n")

        out.write("## Background\n\n")
        out.write("P54 showed entry_score distribution in the P49 segment:\n\n")
        out.write("- +4: 6\n")
        out.write("- +3: 10\n")
        out.write("- -4: 1\n")
        out.write("- -3: 3\n\n")
        out.write("Despite this, raw intent distribution was:\n\n")
        out.write("- HOLD: 100\n")
        out.write("- BUY: 0\n")
        out.write("- SELL: 0\n\n")

        out.write("## Target File\n\n")
        out.write(f"{TARGET}\n\n")

        out.write("## Relevant Source Context\n\n")
        for idx, block in enumerate(blocks, start=1):
            out.write(f"### Context {idx}\n\n")
            out.write("```text\n")
            for line_no, text in block:
                out.write(f"{line_no}: {text}\n")
            out.write("```\n\n")

        out.write("## Preliminary Assessment\n\n")
        out.write("- This audit captures the raw 1m intent decision logic.\n")
        out.write("- The next step should compare the exact decision formula against the score fields observed in P54.\n")
        out.write("- No code changes are introduced in P55.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P55 RAW INTENT DECISION LOGIC AUDIT")
    print("contexts:", len(blocks))
    print("doc_out:", DOC)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
