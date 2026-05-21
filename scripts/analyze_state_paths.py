#!/usr/bin/env python3
# ASCII-only.
# Analyze multi-step state transition paths.

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


def classify_path(avg_final_pnl, winrate):
    if avg_final_pnl >= 25 and winrate >= 0.70:
        return "ROBUST_PROFIT_PATH"

    if avg_final_pnl <= -50 and winrate <= 0.30:
        return "TOXIC_PATH"

    if avg_final_pnl > 0:
        return "MIXED_PROFIT_PATH"

    return "MIXED_PATH"


def main():
    args = parse_args()

    in_path = Path(args.edges_detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing file: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "from_state",
        "to_state",
        "final_trade_pnl",
        "final_win",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.reset_index(drop=True)

        if len(g) < 2:
            continue

        for i in range(len(g) - 1):
            a = g.iloc[i]
            b = g.iloc[i + 1]

            path = " -> ".join(
                [
                    str(a["from_state"]),
                    str(a["to_state"]),
                    str(b["to_state"]),
                ]
            )

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": str(a["side"]).lower(),
                    "path": path,
                    "state_a": str(a["from_state"]),
                    "state_b": str(a["to_state"]),
                    "state_c": str(b["to_state"]),
                    "final_trade_pnl": float(b["final_trade_pnl"]),
                    "final_win": int(b["final_win"]),
                }
            )

    path_df = pd.DataFrame(rows)

    if path_df.empty:
        raise SystemExit("ERROR: no paths generated")

    summary = (
        path_df.groupby(["side", "path"], dropna=False)
        .agg(
            count=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
        )
        .reset_index()
    )

    summary = summary[summary["count"] >= args.min_support].copy()

    summary["path_class"] = summary.apply(
        lambda r: classify_path(
            float(r["avg_final_pnl"]),
            float(r["final_winrate"]),
        ),
        axis=1,
    )

    summary = summary.sort_values(
        ["avg_final_pnl", "final_winrate", "count"],
        ascending=[False, False, False],
    )

    out_csv = out_dir / f"state_path_summary_{args.label}.csv"

    summary.to_csv(out_csv, index=False)

    print("STATE PATH ANALYSIS COMPLETE")
    print(f"paths_total: {len(path_df)}")
    print(f"paths_summary: {len(summary)}")
    print(f"csv_out: {out_csv}")
    print()

    print("BEST PATHS")
    print(
        summary.head(30).to_string(index=False)
    )
    print()

    print("WORST PATHS")
    print(
        summary.sort_values(
            ["avg_final_pnl", "final_winrate", "count"],
            ascending=[True, True, False],
        )
        .head(30)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
