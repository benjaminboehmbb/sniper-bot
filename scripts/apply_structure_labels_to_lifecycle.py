#!/usr/bin/env python3
# ASCII-only.
# Apply structural compatibility labels to lifecycle state-space.

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

    p.add_argument(
        "--ranking",
        default="reports/trade_lifecycle/structural_stability_ranking_STEP9A_FULL_43M.csv",
    )

    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")

    return p.parse_args()


def classify_structure(row):
    side = str(row["side"]).lower()

    from_state = str(row["from_state"]).lower()

    is_bear = "|bear|" in from_state
    is_bull = "|bull|" in from_state

    high_vol = "bad_atr" in from_state

    if side == "short" and is_bear and high_vol:
        return "ELITE_STRUCTURE"

    if side == "short" and is_bear:
        return "COMPATIBLE"

    if side == "short" and is_bull:
        return "HIGHLY_TOXIC"

    if side == "long" and is_bear:
        return "HIGHLY_TOXIC"

    if side == "long" and is_bull:
        return "NEUTRAL"

    return "UNKNOWN"


def main():
    args = parse_args()

    edges_path = Path(args.edges_detail)
    ranking_path = Path(args.ranking)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not edges_path.exists():
        raise SystemExit(f"ERROR: missing edges file: {edges_path}")

    if not ranking_path.exists():
        raise SystemExit(f"ERROR: missing ranking file: {ranking_path}")

    df = pd.read_csv(edges_path)

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

    df["structure_label"] = (
        df.apply(classify_structure, axis=1)
    )

    summary = (
        df.groupby(
            ["structure_label", "side"],
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

    out_detail = (
        out_dir /
        f"structure_labeled_lifecycle_{args.label}.csv"
    )

    out_summary = (
        out_dir /
        f"structure_label_summary_{args.label}.csv"
    )

    df.to_csv(out_detail, index=False)
    summary.to_csv(out_summary, index=False)

    print("STRUCTURE LABEL APPLICATION COMPLETE")
    print(f"rows: {len(df)}")
    print(f"detail_csv: {out_detail}")
    print(f"summary_csv: {out_summary}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
