#!/usr/bin/env python3
# ASCII-only.
# Build market phase segments from 4.3M state-space dataset.

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


def phase_from_progress(v):
    if v <= 0.3333:
        return "EARLY"

    if v <= 0.6666:
        return "MID"

    return "LATE"


def main():
    args = parse_args()

    in_path = Path(args.edges_detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "final_trade_pnl",
        "final_win",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    unique_trades = (
        df[["trade_id"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    unique_trades["trade_index"] = range(len(unique_trades))

    total = len(unique_trades)

    unique_trades["progress_ratio"] = (
        unique_trades["trade_index"] / max(1, total - 1)
    )

    unique_trades["market_phase"] = (
        unique_trades["progress_ratio"]
        .apply(phase_from_progress)
    )

    df = df.merge(
        unique_trades[["trade_id", "market_phase"]],
        on="trade_id",
        how="left",
    )

    out_csv = (
        out_dir /
        f"market_phase_segmented_edges_{args.label}.csv"
    )

    df.to_csv(out_csv, index=False)

    summary = (
        df.groupby(
            ["market_phase", "side"],
            dropna=False,
        )
        .agg(
            rows=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            final_winrate=("final_win", "mean"),
        )
        .reset_index()
    )

    print("MARKET PHASE SEGMENTATION COMPLETE")
    print(f"rows: {len(df)}")
    print(f"csv_out: {out_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
