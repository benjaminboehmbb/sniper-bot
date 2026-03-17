#!/usr/bin/env python3
# scripts/select_GS_k11_long_top250_for_k12_seeds.py
#
# Gold-Standard selection:
# - Input:  K11 LONG FULL results CSV (roi_fee_* already fee-adjusted externally)
# - Robustness metric: roi_fee_p25 over offsets (25th percentile across roi_fee_off_*)
# - Gate (K11->K12): roi_fee_p25 >= -2.8203  (default; calibrated to yield >=250)
# - Rank: roi_fee_p25 desc, then roi_fee_mean desc
# - Output: K12 LONG seeds CSV (Top-N, default 250) in strategies/GS/k12_long/
#
# Deterministic, ASCII-only.

import argparse
import os
from datetime import datetime
import numpy as np
import pandas as pd

OFFSETS = ["0", "500000", "1000000", "1500000"]

def parse_args():
    ap = argparse.ArgumentParser(
        description="Select K12 LONG seeds from K11 LONG FULL GS results (robust roi_fee_p25 gate)."
    )
    ap.add_argument(
        "--in_results",
        default="results/GS/k11_long/strategy_results_GS_k11_long_FULL_2026-01-09_15-27-11.csv",
        help="Input K11 LONG FULL results CSV",
    )
    ap.add_argument(
        "--out_dir",
        default="strategies/GS/k12_long",
        help="Output directory for K12 LONG seeds CSV",
    )
    ap.add_argument("--top_n", type=int, default=250)
    ap.add_argument(
        "--gate_p25",
        type=float,
        default=-2.8203,
        help="Gate: require roi_fee_p25_over_offsets >= gate_p25 (more negative = weaker gate).",
    )
    ap.add_argument("--source", default="k11_full_select")
    ap.add_argument("--out_k", type=int, default=12)
    ap.add_argument("--direction", default="long", choices=["long", "short"])
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

    top["k"] = args.out_k
    top["direction"] = args.direction
    top["source"] = args.source
    top["signals_key"] = top["combination"].astype(str).apply(make_signals_key)

    out_cols = [
        "k", "direction", "source",
        "roi_fee_mean", "roi_fee_p25", "roi_fee_min",
        "trades_sum", "signals_key", "combination"
    ]
    top_out = top[out_cols].copy()

    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_name = f"strategies_GS_k12_long_seeds_top{args.top_n}_minRoiP25{args.gate_p25:+.2f}_{ts}.csv"
    out_path = os.path.join(args.out_dir, out_name)
    top_out.to_csv(out_path, index=False)

    total = len(df)
    passed = len(gated)
    selected = len(top_out)

    print("[ok] Input:", args.in_results)
    print("[ok] Rows total:", total)
    print("[ok] Gate roi_fee_p25 >= %.4f" % args.gate_p25)
    print("[ok] Rows passed gate:", passed, "(%.2f%%)" % (100.0 * passed / max(total, 1)))
    print("[ok] Selected seeds:", selected)
    print("[ok] Output:", out_path)

if __name__ == "__main__":
    main()
