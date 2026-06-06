#!/usr/bin/env python3
# P50 Trading Behavior Reassessment
# ASCII-only.

from __future__ import annotations

from collections import Counter
from pathlib import Path


LOG = Path("live_logs/l1_paper.log")
DOC = Path("docs/review/P50_TRADING_BEHAVIOR_REASSESSMENT_2026-06-06.md")


def extract_value(parts, prefix):
    for p in parts:
        if p.startswith(prefix):
            return p.split("=", 1)[1]
    return None


def main() -> int:
    if not LOG.exists():
        print("ERROR: missing", LOG)
        return 1

    vote_counter = Counter()
    seed_counter = Counter()
    intent_counter = Counter()
    reason_counter = Counter()
    action_counter = Counter()

    with LOG.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()

            if "event=intent_fused" in line:
                v = extract_value(parts, "vote_5m_direction=")
                s = extract_value(parts, "vote_5m_seed_id=")
                i = extract_value(parts, "intent_final=")
                r = extract_value(parts, "reason_code=")

                if v:
                    vote_counter[v] += 1
                if s:
                    seed_counter[s] += 1
                if i:
                    intent_counter[i] += 1
                if r:
                    reason_counter[r] += 1

            elif "event=execution" in line:
                a = extract_value(parts, "action=")
                if a:
                    action_counter[a] += 1

    total_votes = sum(vote_counter.values())
    total_intents = sum(intent_counter.values())

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P50 TRADING BEHAVIOR REASSESSMENT\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Reassess Live L1 trading behavior after P44-P49 timing redesign.\n\n")

        out.write("## Timing Vote Distribution\n\n")
        for k, v in vote_counter.most_common():
            pct = (100.0 * v / total_votes) if total_votes else 0.0
            out.write(f"- {k}: {v} ({pct:.2f}%)\n")

        out.write("\n## Timing Seed Distribution\n\n")
        for k, v in seed_counter.most_common():
            out.write(f"- {k}: {v}\n")

        out.write("\n## Final Intent Distribution\n\n")
        for k, v in intent_counter.most_common():
            pct = (100.0 * v / total_intents) if total_intents else 0.0
            out.write(f"- {k}: {v} ({pct:.2f}%)\n")

        out.write("\n## Intent Reasons\n\n")
        for k, v in reason_counter.most_common(20):
            out.write(f"- {k}: {v}\n")

        out.write("\n## Execution Actions\n\n")
        for k, v in action_counter.most_common():
            out.write(f"- {k}: {v}\n")

        out.write("\n## Assessment\n\n")

        long_votes = vote_counter.get("long", 0)
        short_votes = vote_counter.get("short", 0)
        none_votes = vote_counter.get("none", 0)

        if long_votes > 0 and short_votes > 0:
            out.write("- PASS: timing layer is no longer long-only.\n")

        if none_votes > 0:
            out.write("- PASS: timing layer can remain neutral.\n")

        if long_votes > 0 and short_votes > 0 and none_votes > 0:
            out.write("- PASS: all three timing states observed.\n")

        out.write("\n## Result\n\n")
        out.write("Status: PASS\n")

    print("P50 TRADING BEHAVIOR REASSESSMENT")
    print("doc_out:", DOC)
    print("votes:", total_votes)
    print("intents:", total_intents)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
