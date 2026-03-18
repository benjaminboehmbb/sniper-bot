#!/usr/bin/env python3
# tools/validate_trades.py
# ASCII-only

import json
import sys
from datetime import datetime

def parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tools/validate_trades.py <trades.jsonl>")
        return

    path = sys.argv[1]

    trades = []
    with open(path, "r") as f:
        for line in f:
            trades.append(json.loads(line))

    if not trades:
        print("No trades")
        return

    errors = 0

    prev_exit = None

    for i, t in enumerate(trades):
        entry = parse_ts(t["entry_timestamp_utc"])
        exit_ = parse_ts(t["exit_timestamp_utc"])

        if exit_ <= entry:
            print(f"ERROR: trade {i} exit <= entry")
            errors += 1

        if prev_exit and entry < prev_exit:
            print(f"ERROR: overlap at trade {i}")
            errors += 1

        prev_exit = exit_

    print("---- VALIDATION ----")
    print(f"trades_checked: {len(trades)}")
    print(f"errors: {errors}")

    if errors == 0:
        print("STATUS: OK")
    else:
        print("STATUS: FAIL")

if __name__ == "__main__":
    main()