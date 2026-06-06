#!/usr/bin/env python3
# P46 Runtime Timing Signal Wiring Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path

TARGET = Path("live_l1/core/loop.py")
DOC = Path("docs/review/P46_RUNTIME_TIMING_SIGNAL_WIRING_AUDIT_2026-06-06.md")

KEYWORDS = [
    "compute_5m_timing_vote",
    "vote_v1",
    "rsi_signal",
    "stoch_signal",
    "features.signal",
    "build_feature_snapshot",
    "intent_fused",
    "vote_5m_direction",
    "vote_5m_seed_id",
    "vote_5m_strength",
]


def collect_context(lines: list[str], hit_idx: int, before: int = 12, after: int = 18) -> list[tuple[int, str]]:
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
        out.write("# P46 RUNTIME TIMING SIGNAL WIRING AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Audit how live_l1/core/loop.py wires runtime signals into compute_5m_timing_vote after P45 produced only none votes.\n\n")

        out.write("## Background\n\n")
        out.write("P44 isolated tests confirmed polarity-aware timing works when rsi_signal and stoch_signal are passed explicitly.\n\n")
        out.write("P45 runtime validation produced 100 none votes, suggesting runtime signal kwargs may not be passed into compute_5m_timing_vote.\n\n")

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
        out.write("- If compute_5m_timing_vote is called without rsi_signal/stoch_signal kwargs, polarity-aware timing will correctly return none.\n")
        out.write("- The audit output should identify the exact call site and available feature signal access pattern.\n")
        out.write("- No code changes are introduced in P46.\n\n")

        out.write("## Required Next Step\n\n")
        out.write("Review call-site output and design the wiring fix before patching.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P46 RUNTIME TIMING SIGNAL WIRING AUDIT")
    print("contexts:", len(blocks))
    print("doc_out:", DOC)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
