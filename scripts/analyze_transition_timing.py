#!/usr/bin/env python3
# ASCII-only.
# Analyze timing of regime transitions inside trade lifecycle.

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


def timing_bucket(ratio):
    if ratio <= 0.33:
        return "EARLY"

    if ratio <= 0.66:
        return "MID"

    return "LATE"


def main():
    args = parse_args()

    in_path = Path(args.edges_detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.reset_index(drop=True)

        total_steps = len(g)

        if total_steps == 0:
            continue

        for idx, r in g.iterrows():
            transition_type = classify_transition(
                str(r["from_regime"]),
                str(r["to_regime"]),
            )

            progress_ratio = (idx + 1) / total_steps

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": str(r["side"]).lower(),
                    "transition_type": transition_type,
                    "timing_bucket": timing_bucket(progress_ratio),
                    "progress_ratio": progress_ratio,
                    "pnl_delta": float(r["pnl_delta"]),
                    "health_delta": float(r["health_delta"]),
                    "final_trade_pnl": float(r["final_trade_pnl"]),
                    "final_win": int(r["final_win"]),
                }
            )

    out = pd.DataFrame(rows)

    summary = (
        out.groupby(
            ["side", "transition_type", "timing_bucket"],
            dropna=False,
        )
        .agg(
            rows=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_progress_ratio=("progress_ratio", "mean"),
            avg_pnl_delta=("pnl_delta", "mean"),
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

    out_csv = out_dir / f"transition_timing_summary_{args.label}.csv"

    summary.to_csv(out_csv, index=False)

    print("TRANSITION TIMING ANALYSIS COMPLETE")
    print(f"rows: {len(out)}")
    print(f"summary_rows: {len(summary)}")
    print(f"csv_out: {out_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
