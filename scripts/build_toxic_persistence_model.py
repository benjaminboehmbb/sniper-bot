#!/usr/bin/env python3
# ASCII-only.
# Analyze persistence dominance of toxic structures.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--overlay-detail",
        default="reports/trade_lifecycle/structure_overlay_warning_detail_STEP9A_FULL_43M.csv",
    )

    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")

    return p.parse_args()


def persistence_class(v: float):
    if v >= 0.90:
        return "EXTREME_TOXIC"

    if v >= 0.70:
        return "HIGH_TOXIC"

    if v >= 0.40:
        return "MODERATE_TOXIC"

    if v > 0:
        return "TEMPORARY_TOXIC"

    return "NO_TOXICITY"


def pnl_class(v: float):
    if v >= 100:
        return "BIG_WIN"

    if v >= 25:
        return "WIN"

    if v <= -100:
        return "BIG_LOSS"

    if v < 0:
        return "LOSS"

    return "NEUTRAL"


def main():
    args = parse_args()

    in_path = Path(args.overlay_detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "final_trade_pnl",
        "final_win",
        "toxic_ratio",
        "first_toxic_sec",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["toxic_persistence_class"] = (
        df["toxic_ratio"]
        .apply(persistence_class)
    )

    df["trade_class"] = (
        df["final_trade_pnl"]
        .apply(pnl_class)
    )

    summary = (
        df.groupby(
            ["side", "toxic_persistence_class"],
            dropna=False,
        )
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_first_toxic_sec=("first_toxic_sec", "mean"),
        )
        .reset_index()
    )

    trade_class_summary = (
        df.groupby(
            ["side", "toxic_persistence_class", "trade_class"],
            dropna=False,
        )
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_trade_pnl", "mean"),
        )
        .reset_index()
    )

    summary = summary.sort_values(
        ["avg_final_pnl", "final_winrate"],
        ascending=[False, False],
    )

    summary_csv = (
        out_dir /
        f"toxic_persistence_summary_{args.label}.csv"
    )

    trade_class_csv = (
        out_dir /
        f"toxic_persistence_trade_classes_{args.label}.csv"
    )

    summary.to_csv(summary_csv, index=False)
    trade_class_summary.to_csv(trade_class_csv, index=False)

    print("TOXIC PERSISTENCE MODEL COMPLETE")
    print(f"summary_csv: {summary_csv}")
    print(f"trade_class_csv: {trade_class_csv}")
    print()

    print("PERSISTENCE SUMMARY")
    print(summary.to_string(index=False))
    print()

    print("TRADE CLASS BREAKDOWN")
    print(trade_class_summary.to_string(index=False))


if __name__ == "__main__":
    main()
