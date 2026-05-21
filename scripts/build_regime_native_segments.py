#!/usr/bin/env python3
# ASCII-only.
# Build regime-native market phase segmentation.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--edges-detail",
        default="reports/trade_lifecycle/state_transition_graph_edges_detail_STEP9A_FULL_43M.csv",
    )
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")
    return p.parse_args()


def detect_native_regime(state: str) -> str:
    s = state.lower()

    is_bull = "|bull|" in s
    is_bear = "|bear|" in s
    bad_atr = "bad_atr" in s

    if is_bull and bad_atr:
        return "HIGH_VOL_BULL"

    if is_bear and bad_atr:
        return "HIGH_VOL_BEAR"

    if is_bull:
        return "LOW_VOL_BULL"

    if is_bear:
        return "LOW_VOL_BEAR"

    return "UNKNOWN"


def main():
    args = parse_args()

    in_path = Path(args.edges_detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "from_state",
        "final_trade_pnl",
        "final_win",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["native_regime"] = (
        df["from_state"]
        .astype(str)
        .apply(detect_native_regime)
    )

    out_csv = (
        out_dir /
        f"regime_native_segmented_edges_{args.label}.csv"
    )

    df.to_csv(out_csv, index=False)

    summary = (
        df.groupby(
            ["native_regime", "side"],
            dropna=False,
        )
        .agg(
            rows=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
        )
        .reset_index()
    )

    summary = summary.sort_values(
        ["avg_final_pnl", "final_winrate"],
        ascending=[False, False],
    )

    print("REGIME NATIVE SEGMENTATION COMPLETE")
    print(f"rows: {len(df)}")
    print(f"csv_out: {out_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
