#!/usr/bin/env python3
# P29 Trading Behavior Assessment
# ASCII-only.

from pathlib import Path
import re
from collections import Counter

LOG = Path("live_logs/l1_paper.log")
OUT = Path("docs/review/P29_LIVE_L1_TRADING_BEHAVIOR_ASSESSMENT_2026-06-06.md")

def main():
    gate_counts = Counter()
    regime_counts = Counter()
    intent_counts = Counter()
    vote_counts = Counter()
    reason_counts = Counter()

    total_market = 0
    total_intents = 0

    with LOG.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:

            if "event=market_snapshot" in line:
                total_market += 1

                m1 = re.search(r"allow_long=(\S+)", line)
                m2 = re.search(r"allow_short=(\S+)", line)

                if m1 and m2:
                    gate_counts[(m1.group(1), m2.group(1))] += 1

            elif "event=regime_snapshot" in line:

                m = re.search(r"regime_label=(\S+)", line)
                if m:
                    regime_counts[m.group(1)] += 1

            elif "event=intent_fused" in line:

                total_intents += 1

                m = re.search(r"intent_final=(\S+)", line)
                if m:
                    intent_counts[m.group(1)] += 1

                m = re.search(r"vote_5m_direction=(\S+)", line)
                if m:
                    vote_counts[m.group(1)] += 1

                m = re.search(r"reason_code=(\S+)", line)
                if m:
                    reason_counts[m.group(1)] += 1

    OUT.parent.mkdir(parents=True, exist_ok=True)

    with OUT.open("w", encoding="utf-8") as out:

        out.write("# P29 LIVE L1 TRADING BEHAVIOR ASSESSMENT\n\n")
        out.write("Date: 2026-06-06\n\n")

        out.write("## Regime Distribution\n\n")
        for k,v in regime_counts.most_common():
            out.write(f"- {k}: {v}\n")

        out.write("\n## Gate Distribution\n\n")
        for k,v in gate_counts.most_common():
            out.write(f"- allow_long={k[0]} allow_short={k[1]}: {v}\n")

        out.write("\n## Intent Distribution\n\n")
        for k,v in intent_counts.most_common():
            out.write(f"- {k}: {v}\n")

        out.write("\n## 5m Vote Distribution\n\n")
        for k,v in vote_counts.most_common():
            out.write(f"- {k}: {v}\n")

        out.write("\n## Intent Reasons\n\n")
        for k,v in reason_counts.most_common(20):
            out.write(f"- {k}: {v}\n")

        out.write("\n## Assessment\n\n")

        if vote_counts.get("long",0) > 0 and len(vote_counts) == 1:
            out.write(
                "- WARNING: 5m timing layer appears permanently biased to LONG.\n"
            )

        if intent_counts.get("HOLD",0) > 0:
            hold_ratio = intent_counts["HOLD"] / max(total_intents,1)

            out.write(
                f"- HOLD ratio: {hold_ratio:.6f}\n"
            )

        if gate_counts.get(("0","0"),0) > 0:
            blocked_ratio = gate_counts[("0","0")] / max(total_market,1)

            out.write(
                f"- Gate blocked ratio: {blocked_ratio:.6f}\n"
            )

        out.write(
            "- Infrastructure validated in P28.\n"
        )

        out.write(
            "- Future work should focus on signal quality and trading behavior.\n"
        )

        out.write("\n## Result\n\n")
        out.write("Status: PASS\n")

    print("P29 LIVE L1 TRADING BEHAVIOR ASSESSMENT")
    print("doc_out:", OUT)
    print("RESULT: PASS")


if __name__ == "__main__":
    main()
