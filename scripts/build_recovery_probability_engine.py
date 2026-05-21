#!/usr/bin/env python3
# ASCII-only.
# Research-only recovery probability engine.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--momentum-csv",
        default="reports/trade_lifecycle/health_momentum_detail_STEP9A_FULL_43M.csv",
    )

    p.add_argument(
        "--out-dir",
        default="reports/trade_lifecycle",
    )

    p.add_argument(
        "--label",
        default="recovery_probability_engine",
    )

    return p.parse_args()


def bucket_health(v: float) -> str:

    if v <= -80:
        return "H_NEG_EXTREME"

    if v <= -55:
        return "H_NEG_STRONG"

    if v <= -25:
        return "H_NEG"

    if v < 5:
        return "H_NEUTRAL"

    if v < 35:
        return "H_POS"

    return "H_POS_STRONG"


def bucket_delta(v: float) -> str:

    if v <= -80:
        return "D_COLLAPSE_EXTREME"

    if v <= -30:
        return "D_COLLAPSE"

    if v < 10:
        return "D_FLAT"

    if v < 50:
        return "D_RECOVER"

    return "D_SURGE"


def main() -> int:

    args = parse_args()

    in_path = Path(args.momentum_csv)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing momentum csv: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "market_regime",
        "current_score",
        "health_score",
        "health_delta",
        "pnl_delta",
        "current_pnl",
        "future_best_delta",
        "future_worst_delta",
        "final_trade_pnl",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    x = df.copy()

    # Recovery definition.
    x["recovered"] = (
        (x["future_best_delta"] >= 100)
        & (x["final_trade_pnl"] > 0)
    ).astype(int)

    x["health_bucket"] = x["health_score"].apply(bucket_health)
    x["delta_bucket"] = x["health_delta"].apply(bucket_delta)

    x["score_sign"] = x["current_score"].apply(
        lambda v: "POS" if int(v) > 0 else (
            "NEG" if int(v) < 0 else "ZERO"
        )
    )

    summary = (
        x.groupby(
            [
                "side",
                "market_regime",
                "health_bucket",
                "delta_bucket",
                "score_sign",
            ],
            dropna=False,
            observed=False,
        )
        .agg(
            rows=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            recovery_probability=("recovered", "mean"),
            avg_health=("health_score", "mean"),
            avg_health_delta=("health_delta", "mean"),
            avg_pnl_delta=("pnl_delta", "mean"),
            avg_current_pnl=("current_pnl", "mean"),
            avg_future_best=("future_best_delta", "mean"),
            avg_future_worst=("future_worst_delta", "mean"),
            avg_final_pnl=("final_trade_pnl", "mean"),
        )
        .reset_index()
    )

    summary = summary[summary["rows"] >= 3].copy()

    summary = summary.sort_values(
        [
            "recovery_probability",
            "avg_final_pnl",
            "rows",
        ],
        ascending=[False, False, False],
    )

    # Probability classes.
    summary["recovery_class"] = summary["recovery_probability"].apply(
        lambda v:
            "VERY_HIGH"
            if v >= 0.80 else (
                "HIGH"
                if v >= 0.60 else (
                    "MEDIUM"
                    if v >= 0.40 else (
                        "LOW"
                        if v >= 0.20 else "VERY_LOW"
                    )
                )
            )
    )

    out_summary = (
        out_dir
        / f"recovery_probability_summary_{args.label}.csv"
    )

    summary.to_csv(out_summary, index=False)

    print("RECOVERY PROBABILITY ENGINE COMPLETE")
    print(f"rows: {len(summary)}")
    print(f"summary_csv: {out_summary}")
    print()

    print("HIGHEST RECOVERY PROBABILITIES")
    print(
        summary.head(40).to_string(index=False)
    )
    print()

    print("LOWEST RECOVERY PROBABILITIES")
    print(
        summary.sort_values(
            "recovery_probability",
            ascending=True,
        ).head(40).to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
