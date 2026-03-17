#!/usr/bin/env python3
# scripts/select_GS_k12_long_top250_FINAL.py
#
# Final GS selection from K12 LONG FULL:
# - Robustness: roi_fee_p25 across offsets (q25 of roi_fee_off_*)
# - Gate calibrated to yield >=250 pass: roi_fee_p25 >= -3.1788
# - Rank: roi_fee_p25 desc, then roi_fee_mean desc
# - Output: strategies/GS/k12_long/strategies_GS_k12_long_TOP250_FINAL_*.csv
#
# ASCII-only prints, deterministic mergesort.

import argparse
import os
from datetime import datetime
import numpy as np
import pandas as pd

OFFSETS = ["0", "500000", "1000000", "1500000"]

def parse_args():
    ap = argparse.ArgumentParser(description="Select final TOP250 from K12 LONG FULL (GS).")
    ap.add_argument(
        "--in_results",
        default="results/GS/k12_long/strategy_results_GS_k12_long_FULL_2026-01-09_15-46-13.csv",
        help="Input K12 LONG FULL results CSV",
    )
    ap.add_argument(
        "--out_dir",
        default="strategies/GS/k12_long",
        help="Output directory",
    )
    ap.add_argument("--top_n", type=int, default=250)
    ap.add_argument("--gate_p25", type=float, default=-3.1788)
    ap.add_argument("--direction", choices=["long", "short"], default="long")
    ap.add_argument("--source", default="k12_full_final_select")
    return ap.parse_args()

def require_columns(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise SystemExit(f"[fatal] Missing required columns: {missing}")

def make_signals_key(comb_str: str) -> str:
    try:
        d = eval(comb_str, {"__builtins__": {}}, {})
        if not isinstance(d, dict):
            return "UNKNOWN"
        keys = sorted([str(k) for k in d.keys()])
        return "+".join(keys) if keys else "EMPTY"
    except Exception:
        return "UNKNOWN"

def main():
    args = parse_args()
    if not os.path.exists(args.in_results):
        raise SystemExit(f"[fatal] Input not found: {args.in_results}")

    df = pd.read_csv(args.in_results)

    base_cols = ["roi_fee_mean", "trades_sum", "combination"]
    off_cols = [f"roi_fee_off_{o}" for o in OFFSETS]
    require_columns(df, base_cols + off_cols)

    off_vals = df[off_cols].to_numpy(dtype=float)
    df["roi_fee_p25"] = np.quantile(off_vals, 0.25, axis=1)
    df["roi_fee_min"] = np.min(off_vals, axis=1)

    gated = df[df["roi_fee_p25"] >= args.gate_p25].copy()

    gated.sort_values(
        by=["roi_fee_p25", "roi_fee_mean"],
        ascending=[False, False],
        inplace=True,
        kind="mergesort",
    )

    top = gated.head(args.top_n).copy()
    top["k"] = 12
    top["direction"] = args.direction
    top["source"] = args.source
    top["signals_key"] = top["combination"].astype(str).apply(make_signals_key)

    out_cols = [
        "k", "direction", "source",
        "roi_fee_mean", "roi_fee_p25", "roi_fee_min",
        "trades_sum", "signals_key", "combination"
    ]
    out = top[out_cols].copy()

    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(args.out_dir, f"strategies_GS_k12_long_TOP250_FINAL_{ts}.csv")
    out.to_csv(out_path, index=False)

    print("[ok] Input:", args.in_results)
    print("[ok] Rows total:", len(df))
    print("[ok] Gate roi_fee_p25 >= %.4f" % args.gate_p25)
    print("[ok] Rows passed gate:", len(gated), "(%.2f%%)" % (100.0 * len(gated) / max(len(df), 1)))
    print("[ok] Selected:", len(out))
    print("[ok] Output:", out_path)

if __name__ == "__main__":
    main()
