#!/usr/bin/env python3
# tools/l1e_log_summary.py
#
# Summarize live_logs/l1_paper.log for L1-E monitoring.
# ASCII only.

from __future__ import annotations
import argparse
from pathlib import Path
from collections import Counter


def parse_kv(line: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for token in line.strip().split():
        if "=" not in token:
            continue
        k, v = token.split("=", 1)
        out[k] = v
    return out


def run_summary(log_path: Path) -> None:

    if not log_path.exists():
        print(f"ERROR log file not found: {log_path}")
        return

    event_counts = Counter()
    reason_counts = Counter()
    raw_counts = Counter()
    final_counts = Counter()
    vote_counts = Counter()

    first_ts = None
    last_ts = None

    with open(log_path, "r", encoding="utf-8") as f:

        for line in f:

            if not line.strip():
                continue

            kv = parse_kv(line)

            ts = kv.get("timestamp_utc")

            if ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts

            event = kv.get("event")

            if event:
                event_counts[event] += 1

            if event == "intent_fused":

                raw = kv.get("intent_1m_raw")
                final = kv.get("intent_final")
                reason = kv.get("reason_code")
                vote = kv.get("vote_5m_direction")

                if raw:
                    raw_counts[raw] += 1

                if final:
                    final_counts[final] += 1

                if reason:
                    reason_counts[reason] += 1

                if vote:
                    vote_counts[vote] += 1

    print("L1E LOG SUMMARY")
    print("----------------")
    print(f"log_path={log_path}")
    print(f"first_timestamp={first_ts}")
    print(f"last_timestamp={last_ts}")
    print()

    print("EVENT COUNTS")
    for k in sorted(event_counts):
        print(f"{k}: {event_counts[k]}")
    print()

    print("RAW INTENTS")
    for k in sorted(raw_counts):
        print(f"{k}: {raw_counts[k]}")
    print()

    print("FINAL INTENTS")
    for k in sorted(final_counts):
        print(f"{k}: {final_counts[k]}")
    print()

    print("REASON CODES")
    for k in sorted(reason_counts):
        print(f"{k}: {reason_counts[k]}")
    print()

    print("5M VOTES")
    for k in sorted(vote_counts):
        print(f"{k}: {vote_counts[k]}")
    print()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log",
        default="live_logs/l1_paper.log",
        help="log file path"
    )

    args = parser.parse_args()

    run_summary(Path(args.log))


if __name__ == "__main__":
    main()