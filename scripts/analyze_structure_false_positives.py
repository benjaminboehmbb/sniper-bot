#!/usr/bin/env python3
# ASCII-only.
# Analyze false positives of HIGHLY_TOXIC overlay.

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


def classify_trade(pnl: float):
    if pnl >= 100:
        return "BIG_WIN"

    if pnl >= 25:
        return "WIN"

    if pnl <= -100:
        return "BIG_LOSS"

    if pnl < 0:
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
        "had_highly_toxic",
        "toxic_ratio",
        "first_toxic_sec",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["trade_class"] = (
        df["final_trade_pnl"]
        .apply(classify_trade)
    )

    false_positive = df[
        (df["had_highly_toxic"] == 1)
        & (df["final_trade_pnl"] > 0)
    ].copy()

    true_positive = df[
        (df["had_highly_toxic"] == 1)
        & (df["final_trade_pnl"] < 0)
    ].copy()

    fp_summary = (
        false_positive.groupby(
            ["side", "trade_class"],
            dropna=False,
        )
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_first_toxic_sec=("first_toxic_sec", "mean"),
        )
        .reset_index()
    )

    tp_summary = (
        true_positive.groupby(
            ["side", "trade_class"],
            dropna=False,
        )
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_first_toxic_sec=("first_toxic_sec", "mean"),
        )
        .reset_index()
    )

    fp_csv = (
        out_dir /
        f"false_positive_summary_{args.label}.csv"
    )

    tp_csv = (
        out_dir /
        f"true_positive_summary_{args.label}.csv"
    )

    fp_summary.to_csv(fp_csv, index=False)
    tp_summary.to_csv(tp_csv, index=False)

    print("FALSE POSITIVE ANALYSIS COMPLETE")
    print(f"false_positive_csv: {fp_csv}")
    print(f"true_positive_csv: {tp_csv}")
    print()

    print("FALSE POSITIVES")
    print(fp_summary.to_string(index=False))
    print()

    print("TRUE POSITIVES")
    print(tp_summary.to_string(index=False))


if __name__ == "__main__":
    main()
