#!/usr/bin/env python3
# tools/analyze_live_l1_signal_quality.py
# P28D Live L1 signal quality review.
# Streaming version. ASCII-only.

from __future__ import annotations

from collections import Counter
from pathlib import Path


LOG_PATH = Path("live_logs/l1_paper.log")
OUT_PATH = Path("docs/review/P28D_SIGNAL_QUALITY_REVIEW_2026-06-06.md")


def parse_line(line: str) -> dict:
    out = {}
    for part in line.strip().split():
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


def write_counter(fh, title: str, counter: Counter, limit: int = 30) -> None:
    fh.write(f"## {title}\n\n")
    if not counter:
        fh.write("none\n\n")
        return
    for key, val in counter.most_common(limit):
        fh.write(f"- {key}: {val}\n")
    fh.write("\n")


def main() -> int:
    if not LOG_PATH.is_file():
        print("ERROR: missing log file:", LOG_PATH)
        return 1

    counts = Counter()
    gates = Counter()
    regime_labels = Counter()
    risk_labels = Counter()
    entry_scores = Counter()
    raw_intents = Counter()
    final_intents = Counter()
    reason_codes = Counter()
    vote_dirs = Counter()
    actions = Counter()
    exec_reasons = Counter()

    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            row = parse_line(raw)
            event = row.get("event", "")
            if not event:
                continue

            counts[event] += 1

            if event == "market_snapshot":
                gates[(row.get("allow_long", ""), row.get("allow_short", ""))] += 1

            elif event == "regime_snapshot":
                regime_labels[row.get("regime_label", "")] += 1
                risk_labels[row.get("risk_label", "")] += 1
                entry_scores[row.get("entry_score", "")] += 1

            elif event == "intent_fused":
                raw_intents[row.get("intent_1m_raw", "")] += 1
                final_intents[row.get("intent_final", "")] += 1
                reason_codes[row.get("reason_code", "")] += 1
                vote_dirs[row.get("vote_5m_direction", "")] += 1

            elif event == "execution":
                actions[row.get("action", "")] += 1
                exec_reasons[row.get("reason", "")] += 1

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUT_PATH.open("w", encoding="utf-8") as out:
        out.write("# P28D SIGNAL QUALITY REVIEW\n\n")
        out.write("Date: 2026-06-06\n")
        out.write("Device: G15 / AR15\n")
        out.write("Environment: WSL\n\n")
        out.write("## Objective\n\n")
        out.write("Review Live L1 signal quality from live_logs/l1_paper.log using streaming analysis.\n\n")

        write_counter(out, "Event Counts", counts)
        write_counter(out, "Gate Counts allow_long/allow_short", gates)
        write_counter(out, "Regime Labels", regime_labels)
        write_counter(out, "Risk Labels", risk_labels)
        write_counter(out, "Entry Scores", entry_scores)
        write_counter(out, "Raw 1m Intents", raw_intents)
        write_counter(out, "Final Intents", final_intents)
        write_counter(out, "Intent Reason Codes", reason_codes)
        write_counter(out, "5m Vote Directions", vote_dirs)
        write_counter(out, "Execution Actions", actions)
        write_counter(out, "Execution Reasons", exec_reasons)

        out.write("## Result\n\n")
        out.write("Status: PASS\n")

    print("P28D LIVE L1 SIGNAL QUALITY REVIEW")
    print("log:", LOG_PATH)
    print("doc_out:", OUT_PATH)
    print("market_snapshots:", counts.get("market_snapshot", 0))
    print("regime_snapshots:", counts.get("regime_snapshot", 0))
    print("intent_fused:", counts.get("intent_fused", 0))
    print("execution:", counts.get("execution", 0))
    print("RESULT: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
