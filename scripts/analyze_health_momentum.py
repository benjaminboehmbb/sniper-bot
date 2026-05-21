#!/usr/bin/env python3
# ASCII-only.
# Research-only health momentum analysis.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--health-csv",
        default="reports/trade_lifecycle/trade_health_detail_STEP9A_FULL_43M.csv",
    )

    p.add_argument(
        "--out-dir",
        default="reports/trade_lifecycle",
    )

    p.add_argument(
        "--label",
        default="health_momentum",
    )

    return p.parse_args()


def momentum_bucket(v: float) -> str:

    if v <= -50:
        return "MOMENTUM_COLLAPSE"

    if v <= -20:
        return "MOMENTUM_DEGRADING"

    if v < 20:
        return "MOMENTUM_FLAT"

    if v < 50:
        return "MOMENTUM_RECOVERING"

    return "MOMENTUM_SURGING"


def main() -> int:

    args = parse_args()

    health_path = Path(args.health_csv)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not health_path.exists():
        raise SystemExit(f"ERROR: missing health csv: {health_path}")

    df = pd.read_csv(health_path)

    required = {
        "trade_id",
        "side",
        "duration_sec",
        "trade_health_score",
        "trade_health_state",
        "unrealized_pnl",
        "market_regime",
        "current_score",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):

        g = g.sort_values("duration_sec").reset_index(drop=True)

        if len(g) < 2:
            continue

        final_row = g.iloc[-1]

        final_pnl = float(final_row["unrealized_pnl"])

        for i in range(1, len(g)):

            prev = g.iloc[i - 1]
            cur = g.iloc[i]

            health_delta = (
                float(cur["trade_health_score"])
                - float(prev["trade_health_score"])
            )

            pnl_delta = (
                float(cur["unrealized_pnl"])
                - float(prev["unrealized_pnl"])
            )

            future = g.iloc[i + 1 :]

            if len(future) > 0:
                future_best_pnl = float(future["unrealized_pnl"].max())
                future_worst_pnl = float(future["unrealized_pnl"].min())
            else:
                future_best_pnl = float(cur["unrealized_pnl"])
                future_worst_pnl = float(cur["unrealized_pnl"])

            future_best_delta = (
                future_best_pnl - float(cur["unrealized_pnl"])
            )

            future_worst_delta = (
                future_worst_pnl - float(cur["unrealized_pnl"])
            )

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": str(cur["side"]),
                    "duration_sec": float(cur["duration_sec"]),
                    "market_regime": str(cur["market_regime"]),
                    "current_score": int(cur["current_score"]),
                    "health_score": float(cur["trade_health_score"]),
                    "health_state": str(cur["trade_health_state"]),
                    "health_delta": health_delta,
                    "momentum_bucket": momentum_bucket(health_delta),
                    "pnl_delta": pnl_delta,
                    "current_pnl": float(cur["unrealized_pnl"]),
                    "future_best_delta": future_best_delta,
                    "future_worst_delta": future_worst_delta,
                    "final_trade_pnl": final_pnl,
                    "future_recovery": int(future_best_delta >= 50),
                    "future_collapse": int(future_worst_delta <= -50),
                }
            )

    out = pd.DataFrame(rows)

    if out.empty:
        raise SystemExit("ERROR: no momentum rows")

    summary = (
        out.groupby(["side", "momentum_bucket"], dropna=False)
        .agg(
            rows=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_health_delta=("health_delta", "mean"),
            avg_pnl_delta=("pnl_delta", "mean"),
            recovery_rate=("future_recovery", "mean"),
            collapse_rate=("future_collapse", "mean"),
            avg_future_best=("future_best_delta", "mean"),
            avg_future_worst=("future_worst_delta", "mean"),
            avg_final_trade_pnl=("final_trade_pnl", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_final_trade_pnl"])
    )

    correlation = out[
        [
            "health_delta",
            "pnl_delta",
            "future_best_delta",
            "future_worst_delta",
            "final_trade_pnl",
        ]
    ].corr()

    detail_path = out_dir / f"health_momentum_detail_{args.label}.csv"
    summary_path = out_dir / f"health_momentum_summary_{args.label}.csv"
    corr_path = out_dir / f"health_momentum_correlation_{args.label}.csv"

    out.to_csv(detail_path, index=False)
    summary.to_csv(summary_path, index=False)
    correlation.to_csv(corr_path)

    print("HEALTH MOMENTUM ANALYSIS COMPLETE")
    print(f"rows: {len(out)}")
    print(f"detail_csv: {detail_path}")
    print(f"summary_csv: {summary_path}")
    print(f"correlation_csv: {corr_path}")
    print()

    print("SUMMARY")
    print(summary.to_string(index=False))
    print()

    print("CORRELATION MATRIX")
    print(correlation.to_string())
    print()

    print("STRONGEST NEGATIVE MOMENTUM")
    print(
        out.sort_values("health_delta")
        .head(30)
        .to_string(index=False)
    )
    print()

    print("STRONGEST POSITIVE MOMENTUM")
    print(
        out.sort_values("health_delta", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
