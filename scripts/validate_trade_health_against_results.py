#!/usr/bin/env python3
# ASCII-only.
# Validate whether trade health scores are predictive of final outcomes.

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
        "--trades-jsonl",
        default="live_logs/trades_l1.jsonl",
    )

    p.add_argument(
        "--out-dir",
        default="reports/trade_lifecycle",
    )

    p.add_argument(
        "--label",
        default="health_validation",
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
    trades_path = Path(args.trades_jsonl)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not health_path.exists():
        raise SystemExit(f"ERROR: missing health csv: {health_path}")

    if not trades_path.exists():
        raise SystemExit(f"ERROR: missing trades jsonl: {trades_path}")

    health = pd.read_csv(health_path)

    trades = pd.read_json(trades_path, lines=True)

    required_health = {
        "trade_id",
        "trade_health_score",
        "trade_health_state",
        "side",
    }

    missing_health = sorted(required_health - set(health.columns))

    if missing_health:
        raise SystemExit(f"ERROR: missing health cols: {missing_health}")

    trade_rows = []

    for trade_id, g in health.groupby("trade_id", dropna=False):

        g = g.sort_values("duration_sec")

        trade_rows.append(
            {
                "trade_id": trade_id,
                "side": str(g.iloc[0]["side"]),
                "health_min": float(g["trade_health_score"].min()),
                "health_max": float(g["trade_health_score"].max()),
                "health_mean": float(g["trade_health_score"].mean()),
                "health_last": float(g.iloc[-1]["trade_health_score"]),
                "health_bucket": bucket(float(g["trade_health_score"].min())),
                "health_state_last": str(g.iloc[-1]["trade_health_state"]),
            }
        )

    trade_health = pd.DataFrame(trade_rows)

    trade_map = {}

    for _, row in trades.iterrows():

        entry_ts = str(row.get("entry_timestamp_utc", ""))

        if not entry_ts:
            continue

        trade_map[entry_ts] = {
            "realized_pnl": float(row.get("pnl", 0.0)),
            "exit_reason": str(row.get("exit_reason", "")),
            "side": str(row.get("side", "")),
        }

    merged_rows = []

    for _, row in trade_health.iterrows():

        trade_id = str(row["trade_id"])

        if trade_id not in trade_map:
            continue

        real = trade_map[trade_id]

        pnl = float(real["realized_pnl"])

        merged_rows.append(
            {
                "trade_id": trade_id,
                "side": row["side"],
                "health_min": row["health_min"],
                "health_max": row["health_max"],
                "health_mean": row["health_mean"],
                "health_last": row["health_last"],
                "health_bucket": row["health_bucket"],
                "health_state_last": row["health_state_last"],
                "realized_pnl": pnl,
                "profitable": int(pnl > 0),
                "exit_reason": real["exit_reason"],
            }
        )

    merged = pd.DataFrame(merged_rows)

    if merged.empty:
        raise SystemExit("ERROR: no matching trades found")

    summary = (
        merged.groupby(["side", "health_bucket"], dropna=False)
        .agg(
            trades=("trade_id", "count"),
            profitable_trades=("profitable", "sum"),
            winrate=("profitable", "mean"),
            avg_realized_pnl=("realized_pnl", "mean"),
            sum_realized_pnl=("realized_pnl", "sum"),
            avg_health_min=("health_min", "mean"),
            avg_health_last=("health_last", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_health_min"])
    )

    correlation = merged[[
        "health_min",
        "health_mean",
        "health_last",
        "realized_pnl",
    ]].corr()

    out_merged = out_dir / f"health_validation_detail_{args.label}.csv"
    out_summary = out_dir / f"health_validation_summary_{args.label}.csv"
    out_corr = out_dir / f"health_validation_correlation_{args.label}.csv"

    merged.to_csv(out_merged, index=False)
    summary.to_csv(out_summary, index=False)
    correlation.to_csv(out_corr)

    print("HEALTH VALIDATION COMPLETE")
    print(f"health_rows: {len(health)}")
    print(f"validated_trades: {len(merged)}")
    print(f"detail_csv: {out_merged}")
    print(f"summary_csv: {out_summary}")
    print(f"correlation_csv: {out_corr}")
    print()

    print("SUMMARY")
    print(summary.to_string(index=False))
    print()

    print("CORRELATION MATRIX")
    print(correlation.to_string())
    print()

    print("WORST HEALTH / BEST REALIZED")
    print(
        merged.sort_values(["health_min", "realized_pnl"], ascending=[True, False])
        .head(25)
        .to_string(index=False)
    )
    print()

    print("BEST HEALTH / WORST REALIZED")
    print(
        merged.sort_values(["health_min", "realized_pnl"], ascending=[False, True])
        .head(25)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
