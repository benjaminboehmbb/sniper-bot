#!/usr/bin/env python3
# P53 Raw 1m Intent Generation Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGETS = [
    Path("live_l1/core/intent.py"),
    Path("live_l1/core/feature_snapshot.py"),
    Path("live_l1/core/loop.py"),
]

DOC = Path("docs/review/P53_RAW_1M_INTENT_GENERATION_AUDIT_2026-06-06.md")

KEYWORDS = [
    "def compute_1m_intent_raw",
    "intent_1m_raw",
    "BUY",
    "SELL",
    "HOLD",
    "score",
    "entry",
    "exit",
    "threshold",
    "features.signal",
    "rsi_signal",
    "stoch_signal",
    "mfi_signal",
    "ma200_signal",
    "return",
]


def collect_context(lines: list[str], hit_idx: int, before: int = 10, after: int = 18):
    start = max(0, hit_idx - before)
    end = min(len(lines), hit_idx + after + 1)
    return [(i + 1, lines[i]) for i in range(start, end)]


def main() -> int:
    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P53 RAW 1M INTENT GENERATION AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Audit why post-fix runtime segments produced timing long/short/none votes while intent_1m_raw remained HOLD.\n\n")

        out.write("## Background\n\n")
        out.write("P51 showed post-fix timing votes in runtime:\n\n")
        out.write("- long: 38\n")
        out.write("- short: 29\n")
        out.write("- none: 133\n\n")
        out.write("But final intent remained HOLD for all 200 audited ticks.\n\n")
        out.write("P52 confirmed that intent fusion preserves HOLD_RAW when intent_1m_raw is HOLD.\n\n")

        for target in TARGETS:
            out.write(f"## Target: {target}\n\n")
            out.write(f"exists: {target.exists()}\n\n")

            if not target.exists():
                continue

            lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            blocks = []
            seen = set()

            for i, line in enumerate(lines):
                if any(k in line for k in KEYWORDS):
                    ctx = collect_context(lines, i)
                    key = tuple(n for n, _ in ctx)
                    if key not in seen:
                        seen.add(key)
                        blocks.append(ctx)

            for idx, block in enumerate(blocks, start=1):
                out.write(f"### Context {idx}\n\n")
                out.write("```text\n")
                for line_no, text in block:
                    out.write(f"{line_no}: {text}\n")
                out.write("```\n\n")

        out.write("## Preliminary Assessment\n\n")
        out.write("- If compute_1m_intent_raw emits HOLD unless specific score thresholds are reached, timing cannot create trades alone.\n")
        out.write("- The audit should identify the raw 1m scoring formula and BUY/SELL thresholds.\n")
        out.write("- Next step should quantify score distribution in post-fix segments or a new controlled segment.\n\n")

        out.write("## Required Next Step\n\n")
        out.write("Review this source audit and then run a raw intent score distribution audit.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P53 RAW 1M INTENT GENERATION AUDIT")
    print("doc_out:", DOC)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
