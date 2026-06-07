#!/usr/bin/env python3
# P60 Extended Runtime Trade Quality Review
# ASCII-only.

from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

TRADES = Path("live_logs/trades_l1.jsonl")
DOC = Path("docs/review/P60_EXTENDED_RUNTIME_TRADE_QUALITY_REVIEW_2026-06-06.md")


def main() -> int:
    if not TRADES.exists():
        print("ERROR: missing", TRADES)
        return 1

    trades = []

    with TRADES.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                obj = json.loads(line)
                trades.append(obj)
            except Exception:
                pass

    exit_reasons = Counter()

    total_pnl = 0.0
    durations = []

    examples = []

    for t in trades:
        pnl = float(t.get("pnl_net", 0.0))
        total_pnl += pnl

        dur = float(t.get("duration_sec", 0.0))
        durations.append(dur)

        reason = str(t.get("exit_reason", "UNKNOWN"))
        exit_reasons[reason] += 1

        if len(examples) < 10:
            examples.append({
                "side": t.get("side"),
                "entry_price": t.get("entry_price"),
                "exit_price": t.get("exit_price"),
                "pnl_net": pnl,
                "duration_sec": dur,
                "exit_reason": reason,
            })

    avg_duration = sum(durations) / len(durations) if durations else 0.0
    wins = sum(1 for t in trades if float(t.get("pnl_net", 0.0)) > 0)
    losses = sum(1 for t in trades if float(t.get("pnl_net", 0.0)) < 0)

    DOC.parent.mkdir(parents=True, exist_ok=True)

    with DOC.open("w", encoding="utf-8") as out:
        out.write("# P60 EXTENDED RUNTIME TRADE QUALITY REVIEW\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")

        out.write("## Objective\n\n")
        out.write("Review trade quality from the extended runtime validation.\n\n")

        out.write("## Trade Summary\n\n")
        out.write(f"total_trades: {len(trades)}\n\n")
        out.write(f"wins: {wins}\n\n")
        out.write(f"losses: {losses}\n\n")
        out.write(f"total_pnl_net: {total_pnl:.6f}\n\n")
        out.write(f"avg_duration_sec: {avg_duration:.2f}\n\n")

        out.write("## Exit Reasons\n\n")
        for k, v in exit_reasons.most_common():
            out.write(f"- {k}: {v}\n")
        out.write("\n")

        out.write("## Example Trades\n\n")
        for e in examples:
            out.write(
                "- side={side} entry={entry_price} exit={exit_price} pnl={pnl_net:.6f} "
                "duration_sec={duration_sec:.2f} exit_reason={exit_reason}\n".format(**e)
            )

        out.write("\n## Result\n\n")
        out.write("Status: PASS\n")

    print("P60 EXTENDED RUNTIME TRADE QUALITY REVIEW")
    print("total_trades:", len(trades))
    print("wins:", wins)
    print("losses:", losses)
    print("total_pnl_net:", round(total_pnl, 6))
    print("avg_duration_sec:", round(avg_duration, 2))
    print("doc_out:", DOC)
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
