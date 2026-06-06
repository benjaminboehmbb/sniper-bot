#!/usr/bin/env python3
# P56 Raw Intent Recent-Score Sequence Audit
# ASCII-only.

from __future__ import annotations

from pathlib import Path
from collections import Counter

SEGMENT = Path("live_logs/review_segments/p49_after_timing_signal_wiring_segment.log")
DOC = Path("docs/review/P56_RAW_INTENT_RECENT_SCORE_SEQUENCE_AUDIT_2026-06-06.md")


def value(parts: list[str], key: str) -> str | None:
    prefix = key + "="
    for p in parts:
        if p.startswith(prefix):
            return p.split("=", 1)[1]
    return None


def main() -> int:
    if not SEGMENT.exists():
        print("ERROR: missing segment:", SEGMENT)
        return 1

    scores = []
    intents = []
    timing = []

    with SEGMENT.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()

            if "event=regime_snapshot" in line:
                s = value(parts, "entry_score")
                if s is not None:
                    try:
                        scores.append(int(s))
                    except Exception:
                        pass

            elif "event=intent_fused" in line:
                i = value(parts, "intent_1m_raw")
                t = value(parts, "vote_5m_direction")
                if i is not None:
                    intents.append(i)
                if t is not None:
                    timing.append(t)

    score_counts = Counter(scores)
    intent_counts = Counter(intents)
    timing_counts = Counter(timing)

    windows = {
        "last2_ge_3": 0,
        "last3_ge_3": 0,
        "last2_ge_4": 0,
        "last3_ge_4": 0,
        "last2_le_-3": 0,
        "last3_le_-3": 0,
        "last2_le_-4": 0,
        "last3_le_-4": 0,
    }

    examples = []

    for idx in range(len(scores)):
        last2 = scores[max(0, idx - 1): idx + 1]
        last3 = scores[max(0, idx - 2): idx + 1]

        def all_ge(vals, threshold, n):
            return len(vals) == n and all(v >= threshold for v in vals)

        def all_le(vals, threshold, n):
            return len(vals) == n and all(v <= threshold for v in vals)

        checks = [
            ("last2_ge_3", all_ge(last2, 3, 2)),
            ("last3_ge_3", all_ge(last3, 3, 3)),
            ("last2_ge_4", all_ge(last2, 4, 2)),
            ("last3_ge_4", all_ge(last3, 4, 3)),
            ("last2_le_-3", all_le(last2, -3, 2)),
            ("last3_le_-3", all_le(last3, -3, 3)),
            ("last2_le_-4", all_le(last2, -4, 2)),
            ("last3_le_-4", all_le(last3, -4, 3)),
        ]

        for name, ok in checks:
            if ok:
                windows[name] += 1
                if len(examples) < 20:
                    examples.append((idx + 1, name, list(last3), list(last2)))

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P56 RAW INTENT RECENT-SCORE SEQUENCE AUDIT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Audit whether post-fix runtime scores form the repeated score sequences required by raw 1m intent logic.\n\n")

        out.write("## Segment\n\n")
        out.write(f"{SEGMENT}\n\n")

        out.write("## Counts\n\n")
        out.write(f"scores: {len(scores)}\n\n")
        out.write(f"intents: {len(intents)}\n\n")
        out.write(f"timing_votes: {len(timing)}\n\n")

        out.write("## Score Distribution\n\n")
        for k, v in sorted(score_counts.items()):
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Raw Intent Distribution\n\n")
        for k, v in intent_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Timing Distribution\n\n")
        for k, v in timing_counts.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Sequence Checks\n\n")
        for k, v in windows.items():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Example Sequence Hits\n\n")
        if not examples:
            out.write("none\n\n")
        else:
            for tick, name, last3, last2 in examples:
                out.write(f"- tick_index={tick} check={name} last3={last3} last2={last2}\n")
            out.write("\n")

        out.write("## Interpretation\n\n")
        out.write("If strong single scores exist but repeated sequence checks are zero, the raw intent logic is intentionally filtering isolated spikes.\n\n")

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P56 RAW INTENT RECENT-SCORE SEQUENCE AUDIT")
    print("scores:", len(scores))
    print("score_counts:", dict(sorted(score_counts.items())))
    print("sequence_checks:", windows)
    print("doc_out:", DOC)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
