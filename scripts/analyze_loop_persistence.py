#!/usr/bin/env python3
# ASCII-only.
# Analyze recursive loop persistence in state topology.

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


def classify_loop(loop_rate, final_pnl, winrate):
    if loop_rate >= 0.60 and final_pnl > 0 and winrate >= 0.70:
        return "STABLE_PROFIT_ATTRACTOR"

    if loop_rate >= 0.60 and final_pnl < 0 and winrate <= 0.30:
        return "TOXIC_COLLAPSE_ATTRACTOR"

    if loop_rate >= 0.40:
        return "PERSISTENT_REGION"

    return "TRANSIENT_REGION"


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

        states = []

        for _, r in g.iterrows():
            states.append(str(r["from_state"]))

        states.append(str(g.iloc[-1]["to_state"]))

        final_pnl = float(g.iloc[-1]["final_trade_pnl"])
        final_win = int(g.iloc[-1]["final_win"])
        side = str(g.iloc[-1]["side"]).lower()

        unique_states = set(states)

        for state in unique_states:
            count = states.count(state)

            loop_rate = count / len(states)

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": side,
                    "state": state,
                    "visits": count,
                    "trajectory_len": len(states),
                    "loop_rate": loop_rate,
                    "final_trade_pnl": final_pnl,
                    "final_win": final_win,
                }
            )

    loops = pd.DataFrame(rows)

    summary = (
        loops.groupby(["side", "state"], dropna=False)
        .agg(
            trades=("trade_id", "nunique"),
            avg_visits=("visits", "mean"),
            avg_loop_rate=("loop_rate", "mean"),
            max_loop_rate=("loop_rate", "max"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
        )
        .reset_index()
    )

    summary = summary[summary["trades"] >= args.min_support].copy()

    summary["loop_class"] = summary.apply(
        lambda r: classify_loop(
            float(r["avg_loop_rate"]),
            float(r["avg_final_pnl"]),
            float(r["final_winrate"]),
        ),
        axis=1,
    )

    summary = summary.sort_values(
        ["avg_final_pnl", "final_winrate", "avg_loop_rate"],
        ascending=[False, False, False],
    )

    out_csv = out_dir / f"loop_persistence_summary_{args.label}.csv"

    summary.to_csv(out_csv, index=False)

    print("LOOP PERSISTENCE ANALYSIS COMPLETE")
    print(f"rows: {len(loops)}")
    print(f"summary_rows: {len(summary)}")
    print(f"csv_out: {out_csv}")
    print()

    print("BEST ATTRACTORS")
    print(
        summary.head(30).to_string(index=False)
    )
    print()

    print("WORST ATTRACTORS")
    print(
        summary.sort_values(
            ["avg_final_pnl", "final_winrate", "avg_loop_rate"],
            ascending=[True, True, False],
        )
        .head(30)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
