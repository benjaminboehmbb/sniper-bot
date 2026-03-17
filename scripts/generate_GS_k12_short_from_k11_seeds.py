#!/usr/bin/env python3
# scripts/generate_GS_k12_short_from_k11_seeds.py
#
# Generate K12 SHORT candidate from K11 SHORT seeds (structural expansion, unweighted).
# - Input seeds: any K11 seed file with "combination" column
# - Output: strategies/GS/k12_short/strategies_GS_k12_short_from_k11_unweighted_<ts>.csv
#
# K12 is the final point: all 12 signals, unique count must be 1.

import argparse
import os
import csv
from datetime import datetime

SIGNALS = [
    "rsi", "macd", "bollinger",
    "ma200", "stoch", "atr", "ema50",
    "adx", "cci", "mfi", "obv", "roc",
]

def safe_eval_dict(s: str) -> dict:
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict")
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out

def parse_args():
    ap = argparse.ArgumentParser(description="Generate GS K12 SHORT (final) from K11 SHORT seeds (unweighted).")
    ap.add_argument(
        "--seeds_csv",
        default="strategies/GS/k11_short/strategies_GS_k11_short_from_k10_TOP66_unweighted_2026-01-09_18-20-33.csv",
        help="K11 SHORT seed file"
    )
    ap.add_argument("--out_dir", default="strategies/GS/k12_short")
    return ap.parse_args()

def main():
    args = parse_args()
    if not os.path.exists(args.seeds_csv):
        raise FileNotFoundError(args.seeds_csv)

    os.makedirs(args.out_dir, exist_ok=True)

    # Any K11 seed contains 11 signals; K12 is deterministic: add the missing one => full set.
    # We validate seeds and then emit exactly one K12 combination.
    seeds_n = 0
    with open(args.seeds_csv, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if "combination" not in rdr.fieldnames:
            raise RuntimeError(f"Missing 'combination' column. Have: {rdr.fieldnames}")
        for row in rdr:
            comb = safe_eval_dict(row["combination"])
            keys = list(comb.keys())
            if len(keys) != 11:
                raise RuntimeError(f"Seed is not K11: {row['combination']}")
            seeds_n += 1

    k12 = {k: 1.0 for k in sorted(SIGNALS)}

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(args.out_dir, f"strategies_GS_k12_short_from_k11_unweighted_{ts}.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["combination"])
        w.writerow([str(k12)])

    print("[ok] Seeds:", seeds_n, "from:", args.seeds_csv)
    print("[ok] Unique K12:", 1, "(upper bound 1)")
    print("[ok] OUT:", out_path)

if __name__ == "__main__":
    main()
