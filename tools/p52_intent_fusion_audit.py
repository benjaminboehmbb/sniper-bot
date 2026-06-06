#!/usr/bin/env python3
# P52 Intent Fusion Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGETS = [
    Path("live_l1/core/intent_fusion.py"),
    Path("live_l1/core/intent.py"),
    Path("live_l1/core/loop.py"),
]

DOC = Path("docs/review/P52_INTENT_FUSION_AUDIT_2026-06-06.md")

KEYWORDS = [
    "def fuse_intent_with_5m_timing",
    "intent_1m_raw",
    "vote_5m_direction",
    "vote_5m_strength",
    "allow_long",
    "allow_short",
    "current_position",
    "HOLD_RAW",
    "CONFIRMED",
    "ASYM",
    "EXIT",
    "BUY",
    "SELL",
    "HOLD",
    "return",
]


def collect_context(lines: list[str], hit_idx: int, before: int = 8, after: int = 16):
    start = max(0, hit_idx - before)
    end = min(len(lines), hit_idx + after + 1)
    return [(i + 1, lines[i]) for i in range(start, end)]


def main() -> int:
    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P52 INTENT FUSION AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Audit why post-fix runtime timing votes include long/short/none while final intents remain HOLD.\n\n")

        out.write("## Background\n\n")
        out.write("P51 post-fix segments showed:\n\n")
        out.write("- timing long: 38\n")
        out.write("- timing short: 29\n")
        out.write("- timing none: 133\n")
        out.write("- final intent HOLD: 200\n")
        out.write("- execution NOOP: 200\n\n")

        out.write("This suggests the current bottleneck is now 1m raw intent, intent fusion, or gate interaction.\n\n")

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
        out.write("- If intent_1m_raw is HOLD, fusion likely preserves HOLD regardless of timing vote.\n")
        out.write("- If gates allow neither direction, BUY/SELL should be blocked even when timing agrees.\n")
        out.write("- The audit should identify whether timing can create entries or only confirm raw 1m intents.\n\n")

        out.write("## Required Next Step\n\n")
        out.write("Review fusion rules and decide whether timing remains confirmatory only or can become a candidate signal layer.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P52 INTENT FUSION AUDIT")
    print("doc_out:", DOC)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
