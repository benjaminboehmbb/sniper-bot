#!/usr/bin/env python3
# scripts/select_GS_k10_short_top66_for_k11_seeds.py
#
# Select K10 SHORT strategies as seeds for K11 SHORT.
# K10 universe is complete (66), so we keep ALL (Top-66) to avoid information loss.
# Sort:
#   1) roi_fee_p25 desc
#   2) roi_fee_mean desc
#
# Input:
#   results/GS/k10_short/strategy_results_GS_k10_short_FULL_<ts>.csv
# Output:
#   strategies/GS/k10_short/strategies_GS_k10_short_TOP66_for_k11_seeds_<ts>.csv

import argparse
import os
from datetime import datetime
import pandas as pd

def parse_args():
    ap = argparse.ArgumentParser(description="Select Top-66 (all) K10 SHORT seeds for K11 SHORT.")
    ap.add_argument(
        "--in_csv",
        default="results/GS/k10_short/strategy_results_GS_k10_short_FULL_2026-01-09_18-15-55.csv",
        help="K10 SHORT FULL results CSV",
    )
    ap.add_argument("--top", type=int, default=66)
    ap.add_argument("--out_dir", default="strategies/GS/k10_short")
    return ap.parse_args()

def main():
    args = parse_args()
    if not os.path.exists(args.in_csv):
        raise FileNotFoundError(args.in_csv)

    df = pd.read_csv(args.in_csv)

    required = ["combination", "roi_fee_p25", "roi_fee_mean", "trades_sum"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}. Have: {list(df.columns)}")

    df = df.sort_values(["roi_fee_p25", "roi_fee_mean"], ascending=[False, False]).reset_index(drop=True)

    top_n = int(args.top)
    if top_n <= 0:
        raise RuntimeError("--top must be > 0")
    top_n = min(top_n, len(df))

    out = df.loc[: top_n - 1, required].copy()

    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(args.out_dir, f"strategies_GS_k10_short_TOP{top_n}_for_k11_seeds_{ts}.csv")

    out.to_csv(out_path, index=False)

    print("[ok] IN:", args.in_csv)
    print("[ok] OUT:", out_path)
    print("[ok] Rows:", len(out))

if __name__ == "__main__":
    main()
