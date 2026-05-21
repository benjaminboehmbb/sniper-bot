#!/usr/bin/env python3
# ASCII-only.
# Analyze regime transition destabilization.

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
    p.add_argument("--min-support", type=int, default=3)
    return p.parse_args()


def classify_transition(a, b):
    if a == b:
        return f"{a}_stable"

    return f"{a}_to_{b}"


def main():
    args = parse_args()

    in_path = Path(args.edges_detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    required = {
        "side",
        "from_regime",
        "to_regime",
        "pnl_delta",
        "health_delta",
        "final_trade_pnl",
        "final_win",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["transition_type"] = df.apply(
        lambda r: classify_transition(
            str(r["from_regime"]),
            str(r["to_regime"]),
        ),
        axis=1,
    )

    summary = (
        df.groupby(
            ["side", "transition_type"],
            dropna=False,
        )
        .agg(
            rows=("transition_type", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_pnl_delta=("pnl_delta", "mean"),
            median_pnl_delta=("pnl_delta", "median"),
            avg_health_delta=("health_delta", "mean"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
        )
        .reset_index()
    )

    summary = summary[summary["rows"] >= args.min_support].copy()

    summary = summary.sort_values(
        ["avg_final_pnl", "final_winrate", "rows"],
        ascending=[False, False, False],
    )

    out_csv = out_dir / f"regime_transition_summary_{args.label}.csv"

    summary.to_csv(out_csv, index=False)

    print("REGIME TRANSITION ANALYSIS COMPLETE")
    print(f"rows: {len(df)}")
    print(f"summary_rows: {len(summary)}")
    print(f"csv_out: {out_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
