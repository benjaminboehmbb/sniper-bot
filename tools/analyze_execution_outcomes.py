#!/usr/bin/env python3
# P28E Execution Outcome Review
# ASCII-only.

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

TRADES = Path("live_logs/trades_l1.jsonl")


def main() -> int:
    if not TRADES.exists():
        print("ERROR: trades file missing")
        return 1

    trades = []

    with TRADES.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            trades.append(json.loads(line))

    total = len(trades)

    long_trades = [t for t in trades if t.get("side") == "long"]
    short_trades = [t for t in trades if t.get("side") == "short"]

    exit_reasons = Counter(t.get("exit_reason", "UNKNOWN") for t in trades)

    pnl_total = sum(float(t.get("pnl_net", 0.0)) for t in trades)

    wins = [t for t in trades if float(t.get("pnl_net", 0.0)) > 0]
    losses = [t for t in trades if float(t.get("pnl_net", 0.0)) < 0]

    durations = [float(t.get("duration_sec", 0.0)) for t in trades]

    avg_duration = sum(durations) / len(durations) if durations else 0.0

    print("P28E EXECUTION OUTCOME REVIEW")
    print("")
    print("total_trades:", total)
    print("long_trades:", len(long_trades))
    print("short_trades:", len(short_trades))
    print("")
    print("total_pnl_net:", round(pnl_total, 6))
    print("wins:", len(wins))
    print("losses:", len(losses))
    print("")
    print("avg_duration_sec:", round(avg_duration, 2))
    print("")
    print("EXIT REASONS")
    for k, v in exit_reasons.most_common():
        print(k, v)

    out = Path("docs/review/P28E_EXECUTION_OUTCOME_REVIEW_2026-06-06.md")
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as fh:
        fh.write("# P28E EXECUTION OUTCOME REVIEW\n\n")
        fh.write("Date: 2026-06-06\n\n")
        fh.write(f"total_trades: {total}\n\n")
        fh.write(f"long_trades: {len(long_trades)}\n\n")
        fh.write(f"short_trades: {len(short_trades)}\n\n")
        fh.write(f"total_pnl_net: {round(pnl_total,6)}\n\n")
        fh.write(f"wins: {len(wins)}\n\n")
        fh.write(f"losses: {len(losses)}\n\n")
        fh.write(f"avg_duration_sec: {round(avg_duration,2)}\n\n")
        fh.write("## Exit Reasons\n\n")
        for k, v in exit_reasons.most_common():
            fh.write(f"- {k}: {v}\n")
        fh.write("\n## Result\n\nStatus: PASS\n")

    print("")
    print("doc_out:", out)
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
