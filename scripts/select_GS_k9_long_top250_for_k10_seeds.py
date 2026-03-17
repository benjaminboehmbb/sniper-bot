#!/usr/bin/env python3
# scripts/select_GS_k9_long_top250_for_k10_seeds.py
#
# Gold-Standard selection:
# - Input:  K9 LONG FULL results CSV (roi_fee_* already fee-adjusted externally)
# - Robustness metric: roi_fee_p25 over offsets (25th percentile across roi_fee_off_*)
# - Gate (K9->K10): roi_fee_p25 >= -2.60  (default; calibrated from K9 FULL)
# - Rank: roi_fee_p25 desc, then roi_fee_mean desc
# - Output: K10 LONG seeds CSV (Top-N, default 250) in strategies/GS/k10_long/
#
# Properties:
# - Deterministic: stable sorting, canonical key
# - Schema-robust: if k/direction/source already exist, they are overwritten
# - ASCII-only prints

import argparse
import os
from datetime import datetime
import numpy as np
import pandas as pd


OFFSETS = ["0", "500000", "1000000", "1500000"]


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Select K10 LONG seeds from K9 LONG FULL GS results (robust roi_fee_p25 gate)."
    )
    ap.add_argument(
        "--in_results",
        default="results/GS/k9_long/strategy_results_GS_k9_long_FULL_2026-01-09_14-19-29.csv",
        help="Input K9 LONG FULL results CSV",
    )
    ap.add_argument(
        "--out_dir",
        default="strategies/GS/k10_long",
        help="Output directory for K10 LONG seeds CSV",
    )
    ap.add_argument(
        "--top_n",
        type=int,
        default=250,
        help="How many seeds to select",
    )
    ap.add_argument(
        "--gate_p25",
        type=float,
        default=-2.60,
        help="Gate: require roi_fee_p25_over_offsets >= gate_p25",
    )
    ap.add_argument(
        "--source",
        default="k9_full_select",
        help="Value to write into output column 'source'",
    )
    ap.add_argument(
        "--out_k",
        type=int,
        default=10,
        help="Write this K into output column 'k' (K10 seeds -> 10)",
    )
    ap.add_argument(
        "--direction",
        default="long",
        choices=["long", "short"],
        help="Direction to write in output (default long)",
    )
    return ap.parse_args()


def require_columns(df: pd.DataFrame, cols: list) -> None:
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


def main() -> None:
    args = parse_args()

    in_path = args.in_results
    if not os.path.exists(in_path):
        raise SystemExit(f"[fatal] Input not found: {in_path}")

    df = pd.read_csv(in_path)

    base_cols = ["roi_fee_mean", "trades_sum", "combination"]
    off_cols = [f"roi_fee_off_{o}" for o in OFFSETS]
    require_columns(df, base_cols + off_cols)

    # Compute robustness across offsets
    off_vals = df[off_cols].to_numpy(dtype=float)
    df["roi_fee_p25"] = np.quantile(off_vals, 0.25, axis=1)
    df["roi_fee_min"] = np.min(off_vals, axis=1)

    # Gate
    gated = df[df["roi_fee_p25"] >= args.gate_p25].copy()

    # Rank (stable)
    gated.sort_values(
        by=["roi_fee_p25", "roi_fee_mean"],
        ascending=[False, False],
        inplace=True,
        kind="mergesort",
    )

    # Select Top-N
    top = gated.head(args.top_n).copy()

    # GS metadata (overwrite if exists)
    top["k"] = args.out_k
    top["direction"] = args.direction
    top["source"] = args.source

    top["signals_key"] = top["combination"].astype(str).apply(make_signals_key)

    out_cols = [
        "k",
        "direction",
        "source",
        "roi_fee_mean",
        "roi_fee_p25",
        "roi_fee_min",
        "trades_sum",
        "signals_key",
        "combination",
    ]
    top_out = top[out_cols].copy()

    # Output filename with timestamp
    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_name = (
        f"strategies_GS_k10_long_seeds_top{args.top_n}"
        f"_minRoiP25{args.gate_p25:+.2f}_{ts}.csv"
    )
    out_path = os.path.join(args.out_dir, out_name)
    top_out.to_csv(out_path, index=False)

    # Summary (ASCII only)
    total = len(df)
    passed = len(gated)
    selected = len(top_out)

    print("[ok] Input:", in_path)
    print("[ok] Rows total:", total)
    print("[ok] Gate roi_fee_p25 >= %.4f" % args.gate_p25)
    print("[ok] Rows passed gate:", passed, "(%.2f%%)" % (100.0 * passed / max(total, 1)))
    print("[ok] Selected seeds:", selected)
    if selected == 0:
        print("[warn] Selected 0 rows. Gate may be too strict.")
    print("[ok] Output:", out_path)


if __name__ == "__main__":
    main()
