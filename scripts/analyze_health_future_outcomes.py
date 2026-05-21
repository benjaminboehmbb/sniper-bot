#!/usr/bin/env python3
# ASCII-only.
# Research-only future outcome analysis for trade health states.

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
        default="health_future_outcomes",
    )

    return p.parse_args()


def bucket(v: float) -> str:

    if v <= -80:
        return "TERMINAL"

    if v <= -55:
        return "COLLAPSING"

    if v <= -25:
        return "DEGRADING"

    if v < 5:
        return "NEUTRAL"

    if v < 35:
        return "RECOVERING"

    if v < 70:
        return "HEALTHY"

    return "HEALTHY_STRONG"


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

        final_row = g.iloc[-1]

        final_pnl = float(final_row["unrealized_pnl"])
        final_health = float(final_row["trade_health_score"])

        for i in range(len(g) - 1):

            cur = g.iloc[i]

            future = g.iloc[i + 1 :]

            current_pnl = float(cur["unrealized_pnl"])

            best_future_pnl = float(future["unrealized_pnl"].max())
            worst_future_pnl = float(future["unrealized_pnl"].min())
            final_future_pnl = final_pnl

            best_future_delta = best_future_pnl - current_pnl
            worst_future_delta = worst_future_pnl - current_pnl
            final_future_delta = final_future_pnl - current_pnl

            recovery_happened = int(best_future_delta >= 50)
            collapse_happened = int(worst_future_delta <= -50)

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": str(cur["side"]),
                    "duration_sec": float(cur["duration_sec"]),
                    "health_score": float(cur["trade_health_score"]),
                    "health_bucket": bucket(float(cur["trade_health_score"])),
                    "health_state": str(cur["trade_health_state"]),
                    "market_regime": str(cur["market_regime"]),
                    "current_score": int(cur["current_score"]),
                    "current_pnl": current_pnl,
                    "future_best_pnl": best_future_pnl,
                    "future_worst_pnl": worst_future_pnl,
                    "future_final_pnl": final_future_pnl,
                    "future_best_delta": best_future_delta,
                    "future_worst_delta": worst_future_delta,
                    "future_final_delta": final_future_delta,
                    "recovery_happened": recovery_happened,
                    "collapse_happened": collapse_happened,
                    "final_health_score": final_health,
                }
            )

    out = pd.DataFrame(rows)

    if out.empty:
        raise SystemExit("ERROR: no future outcome rows")

    summary = (
        out.groupby(["side", "health_bucket"], dropna=False)
        .agg(
            snapshots=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            recovery_rate=("recovery_happened", "mean"),
            collapse_rate=("collapse_happened", "mean"),
            avg_future_best_delta=("future_best_delta", "mean"),
            avg_future_worst_delta=("future_worst_delta", "mean"),
            avg_future_final_delta=("future_final_delta", "mean"),
            avg_final_health=("final_health_score", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_future_final_delta"])
    )

    correlation = out[
        [
            "health_score",
            "future_best_delta",
            "future_worst_delta",
            "future_final_delta",
            "final_health_score",
        ]
    ].corr()

    out_detail = out_dir / f"health_future_outcomes_detail_{args.label}.csv"
    out_summary = out_dir / f"health_future_outcomes_summary_{args.label}.csv"
    out_corr = out_dir / f"health_future_outcomes_correlation_{args.label}.csv"

    out.to_csv(out_detail, index=False)
    summary.to_csv(out_summary, index=False)
    correlation.to_csv(out_corr)

    print("HEALTH FUTURE OUTCOME ANALYSIS COMPLETE")
    print(f"future_rows: {len(out)}")
    print(f"detail_csv: {out_detail}")
    print(f"summary_csv: {out_summary}")
    print(f"correlation_csv: {out_corr}")
    print()

    print("SUMMARY")
    print(summary.to_string(index=False))
    print()

    print("CORRELATION MATRIX")
    print(correlation.to_string())
    print()

    print("MOST DANGEROUS CURRENT STATES")
    print(
        out.sort_values("future_final_delta")
        .head(30)
        .to_string(index=False)
    )
    print()

    print("BEST RECOVERY STATES")
    print(
        out.sort_values("future_best_delta", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
