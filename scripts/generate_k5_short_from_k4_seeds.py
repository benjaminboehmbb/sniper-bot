#!/usr/bin/env python3
# ASCII only

import argparse
import csv
import json
from datetime import datetime

ALL_SIGNALS = ["adx","atr","bollinger","cci","ema50","ma200","macd","mfi","obv","roc","rsi","stoch"]

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k4-seeds", required=True, help="Input CSV with column 'Combination' (dict-string).")
    ap.add_argument("--out", required=True, help="Output CSV path.")
    ap.add_argument("--new-weight", type=float, default=0.5, help="Default weight for the added 5th signal.")
    ap.add_argument("--max-per-k4", type=int, default=8, help="How many K5 variants to create per K4 seed.")
    ap.add_argument("--limit", type=int, default=0, help="Optional limit on input rows (0 = no limit).")
    return ap.parse_args()

def main():
    args = parse_args()

    out_rows = []
    n_in = 0
    n_out = 0

    with open(args.k4_seeds, newline="") as f:
        r = csv.DictReader(f)
        if "Combination" not in r.fieldnames:
            raise SystemExit("ERROR: input missing column 'Combination'")

        for row in r:
            n_in += 1
            if args.limit and n_in > args.limit:
                break

            combo = json.loads(row["Combination"])
            if len(combo) != 4:
                # Skip anything that is not K4; we want deterministic K5-from-K4.
                continue

            present = set(combo.keys())
            missing = [s for s in ALL_SIGNALS if s not in present]

            # deterministic order; create up to max-per-k4 variants
            for s in missing[: args.max_per_k4]:
                k5 = dict(combo)
                k5[s] = float(args.new_weight)
                out_rows.append({"Combination": json.dumps(k5, separators=(",", ":"))})
                n_out += 1

    # write
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Combination"])
        w.writeheader()
        w.writerows(out_rows)

    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] Read K4 rows: {n_in}")
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] Wrote K5 rows: {n_out}")
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] Out: {args.out}")

if __name__ == "__main__":
    main()
