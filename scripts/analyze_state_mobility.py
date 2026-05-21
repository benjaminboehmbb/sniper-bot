#!/usr/bin/env python3
# ASCII-only.
# Analyze state mobility vs profitability.

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


def mobility_class(v):
    if v >= 0.80:
        return "EXTREME_MOBILITY"
    if v >= 0.60:
        return "HIGH_MOBILITY"
    if v >= 0.40:
        return "MEDIUM_MOBILITY"
    return "LOW_MOBILITY"


def main():
    args = parse_args()

    in_path = Path(args.edges_detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.reset_index(drop=True)

        states = []

        for _, r in g.iterrows():
            states.append(str(r["from_state"]))

        states.append(str(g.iloc[-1]["to_state"]))

        unique_states = len(set(states))
        total_states = len(states)

        mobility_ratio = unique_states / total_states

        transitions = 0

        for i in range(1, len(states)):
            if states[i] != states[i - 1]:
                transitions += 1

        transition_ratio = transitions / max(1, total_states - 1)

        rows.append(
            {
                "trade_id": trade_id,
                "side": str(g.iloc[-1]["side"]).lower(),
                "unique_states": unique_states,
                "total_states": total_states,
                "mobility_ratio": mobility_ratio,
                "transition_ratio": transition_ratio,
                "final_trade_pnl": float(g.iloc[-1]["final_trade_pnl"]),
                "final_win": int(g.iloc[-1]["final_win"]),
            }
        )

    mobility = pd.DataFrame(rows)

    mobility["mobility_class"] = mobility["mobility_ratio"].apply(mobility_class)

    summary = (
        mobility.groupby(["side", "mobility_class"], dropna=False)
        .agg(
            trades=("trade_id", "count"),
            avg_unique_states=("unique_states", "mean"),
            avg_mobility_ratio=("mobility_ratio", "mean"),
            avg_transition_ratio=("transition_ratio", "mean"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
        )
        .reset_index()
    )

    out_csv = out_dir / f"state_mobility_summary_{args.label}.csv"

    mobility.to_csv(
        out_dir / f"state_mobility_detail_{args.label}.csv",
        index=False,
    )

    summary.to_csv(out_csv, index=False)

    print("STATE MOBILITY ANALYSIS COMPLETE")
    print(f"trades: {len(mobility)}")
    print(f"csv_out: {out_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
