#!/usr/bin/env python3
# scripts/select_GS_k8_long_top250_for_k9_seeds.py
#
# Gold-Standard selection:
# - Input:  K8 LONG FULL results CSV
# - Robustness metric: roi_fee_p25 over offsets
# - Gate: roi_fee_p25 >= -0.75 (default)
# - Ranking: roi_fee_p25 desc, then roi_fee_mean desc
# - Output: K9 LONG seeds (Top-N)
#
# GS guarantees:
# - Deterministic
# - Schema-robust (handles existing columns)
# - ASCII-only output
# - No engine dependency

import argparse
import os
from datetime import datetime
import numpy as np
import pandas as pd


OFFSETS = ["0", "500000", "1000000", "1500000"]


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in_results",
        default="results/GS/k8_long/strategy_results_GS_k8_long_FULL_2026-01-09_13-19-31.csv",
    )
    ap.add_argument(
        "--out_dir",
        default="strategies/GS/k9_long",
    )
    ap.add_argument("--top_n", type=int, default=250)
    ap.add_argument("--gate_p25", type=float, default=-0.75)
    ap.add_argument("--source", default="k8_full_select")
    ap.add_argument("--out_k", type=int, default=9)
    ap.add_argument("--direction", default="long")
    return ap.parse_args()


def require_columns(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}")


def make_signals_key(comb_str):
    try:
        d = eval(comb_str, {"__builtins__": {}}, {})
        if not isinstance(d, dict):
            return "UNKNOWN"
        return "+".join(sorted(map(str, d.keys())))
    except Exception:
        return "UNKNOWN"


def upsert_constant_column(df, name, value):
    df[name] = value
    return df


def main():
    args = parse_args()

    if not os.path.exists(args.in_results):
        raise FileNotFoundError(args.in_results)

    df = pd.read_csv(args.in_results)

    base_cols = ["roi_fee_mean", "trades_sum", "combination"]
    off_cols = [f"roi_fee_off_{o}" for o in OFFSETS]
    require_columns(df, base_cols + off_cols)

    # --- Robustness metrics ---
    offs = df[off_cols].to_numpy(dtype=float)
    df["roi_fee_p25"] = np.quantile(offs, 0.25, axis=1)
    df["roi_fee_min"] = np.min(offs, axis=1)

    # --- Gate ---
    gated = df[df["roi_fee_p25"] >= args.gate_p25].copy()

    # --- Ranking ---
    gated.sort_values(
        by=["roi_fee_p25", "roi_fee_mean"],
        ascending=[False, False],
        kind="mergesort",
        inplace=True,
    )

    top = gated.head(args.top_n).copy()

    # --- GS metadata (UPSERT, not insert) ---
    top = upsert_constant_column(top, "k", args.out_k)
    top = upsert_constant_column(top, "direction", args.direction)
    top = upsert_constant_column(top, "source", args.source)

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

    # --- Write ---
    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_name = (
        f"strategies_GS_k9_long_seeds_top{args.top_n}"
        f"_minRoiP25{args.gate_p25:+.2f}_{ts}.csv"
    )
    out_path = os.path.join(args.out_dir, out_name)
    top_out.to_csv(out_path, index=False)

    # --- Summary ---
    print("[ok] Input:", args.in_results)
    print("[ok] Total rows:", len(df))
    print("[ok] Gate roi_fee_p25 >=", args.gate_p25)
    print("[ok] Passed gate:", len(gated))
    print("[ok] Selected seeds:", len(top_out))
    print("[ok] Output:", out_path)


if __name__ == "__main__":
    main()

