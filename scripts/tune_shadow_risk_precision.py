#!/usr/bin/env python3
# ASCII-only.
# Precision tuning for Shadow Risk Engine.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--detail",
        default="reports/trade_lifecycle/shadow_risk_detail_STEP9A_FULL_43M.csv",
    )

    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")

    return p.parse_args()


def tuned_risk(row):
    side = str(row["side"]).lower()

    toxic_ratio = float(row["toxic_ratio_so_far"])
    elite_ratio = float(row["elite_ratio_so_far"])
    compatible_ratio = float(row["compatible_ratio_so_far"])

    # LONGS:
    # much stricter because long+bear is structurally catastrophic

    if side == "long":
        if toxic_ratio >= 0.70:
            return "COLLAPSE_RISK"

        if toxic_ratio >= 0.40:
            return "TOXIC"

        if toxic_ratio > 0:
            return "WARNING"

        return "SAFE"

    # SHORTS:
    # allow temporary toxicity if elite/compatible structure exists

    if toxic_ratio >= 0.95 and elite_ratio < 0.20:
        return "COLLAPSE_RISK"

    if toxic_ratio >= 0.80 and compatible_ratio < 0.25:
        return "TOXIC"

    if toxic_ratio >= 0.40:
        return "WARNING"

    return "SAFE"


def main():
    args = parse_args()

    in_path = Path(args.detail)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "toxic_ratio_so_far",
        "elite_ratio_so_far",
        "compatible_ratio_so_far",
        "final_trade_pnl",
        "final_win",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["tuned_shadow_risk"] = (
        df.apply(tuned_risk, axis=1)
    )

    trade_rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.reset_index(drop=True)

        max_risk = g["tuned_shadow_risk"].value_counts().index[0]

        risk_rank = {
            "SAFE": 0,
            "WARNING": 1,
            "TOXIC": 2,
            "COLLAPSE_RISK": 3,
        }

        max_risk = max(
            g["tuned_shadow_risk"],
            key=lambda x: risk_rank[x],
        )

        trade_rows.append(
            {
                "trade_id": trade_id,
                "side": str(g.iloc[-1]["side"]).lower(),
                "max_risk": max_risk,
                "final_trade_pnl": float(g.iloc[-1]["final_trade_pnl"]),
                "final_win": int(g.iloc[-1]["final_win"]),
            }
        )

    trades = pd.DataFrame(trade_rows)

    summary = (
        trades.groupby(
            ["side", "max_risk"],
            dropna=False,
        )
        .agg(
            trades=("trade_id", "count"),
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

    out_csv = (
        out_dir /
        f"shadow_risk_precision_tuning_{args.label}.csv"
    )

    summary.to_csv(out_csv, index=False)

    print("SHADOW RISK PRECISION TUNING COMPLETE")
    print(f"csv_out: {out_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
