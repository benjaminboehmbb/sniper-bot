#!/usr/bin/env python3
# ASCII-only.
# Research-only trade state classifier based on STEP11A lifecycle snapshots.
# Does not affect trading logic.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--lifecycle-csv", default="live_logs/trade_lifecycle_snapshots.csv")
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="trade_state_classification")
    return p.parse_args()


def classify_trade(row: pd.Series) -> str:
    worst = float(row["worst_pnl"])
    final = float(row["final_snapshot_pnl"])
    recovery = float(row["recovery_from_worst"])
    giveback = float(row["giveback_from_best"])
    bear = int(row["bear_snapshots"])
    bull = int(row["bull_snapshots"])
    snapshots = int(row["snapshots"])

    if final > 0 and worst >= 0:
        return "STATE_HEALTHY"

    if worst < 0 and final >= 0 and recovery >= 50:
        return "STATE_RECOVERED"

    if worst <= -200 and recovery <= 25 and final < 0:
        return "STATE_COLLAPSING"

    if final < 0 and bear >= max(2, snapshots - 1) and recovery <= 25:
        return "STATE_BEAR_DEGRADING"

    if worst < 0 and recovery >= 100 and final < 0:
        return "STATE_VOLATILE_PARTIAL_RECOVERY"

    if giveback >= 100 and final > 0:
        return "STATE_PROFIT_GIVEBACK_RISK"

    if final < 0:
        return "STATE_DEGRADING"

    if bull > 0 and bear > 0:
        return "STATE_MIXED_REGIME"

    return "STATE_UNCLASSIFIED"


def main() -> int:
    args = parse_args()

    lifecycle_path = Path(args.lifecycle_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not lifecycle_path.exists():
        raise SystemExit(f"ERROR: lifecycle csv not found: {lifecycle_path}")

    df = pd.read_csv(lifecycle_path)

    required = {
        "entry_timestamp_utc",
        "side",
        "duration_sec",
        "unrealized_pnl",
        "market_regime",
        "atr_quality",
        "current_score",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df = df.copy()
    df["trade_id"] = df["entry_timestamp_utc"]

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.sort_values("duration_sec")

        first = g.iloc[0]
        last = g.iloc[-1]

        worst_pnl = float(g["unrealized_pnl"].min())
        best_pnl = float(g["unrealized_pnl"].max())
        final_pnl = float(last["unrealized_pnl"])
        first_pnl = float(first["unrealized_pnl"])

        rows.append(
            {
                "trade_id": trade_id,
                "side": str(first["side"]),
                "snapshots": int(len(g)),
                "first_timestamp_utc": first["timestamp_utc"],
                "last_timestamp_utc": last["timestamp_utc"],
                "max_duration_sec": float(g["duration_sec"].max()),
                "first_pnl": first_pnl,
                "worst_pnl": worst_pnl,
                "best_pnl": best_pnl,
                "final_snapshot_pnl": final_pnl,
                "recovery_from_worst": final_pnl - worst_pnl,
                "giveback_from_best": best_pnl - final_pnl,
                "bear_snapshots": int((g["market_regime"] == "bear").sum()),
                "bull_snapshots": int((g["market_regime"] == "bull").sum()),
                "bad_atr_snapshots": int((g["atr_quality"] == "bad_atr").sum()),
                "good_atr_snapshots": int((g["atr_quality"] == "good_atr").sum()),
                "min_score": int(g["current_score"].min()),
                "max_score": int(g["current_score"].max()),
                "final_score": int(last["current_score"]),
            }
        )

    trades = pd.DataFrame(rows)
    trades["trade_state"] = trades.apply(classify_trade, axis=1)

    state_summary = (
        trades.groupby(["side", "trade_state"], dropna=False)
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_snapshot_pnl", "mean"),
            sum_final_pnl=("final_snapshot_pnl", "sum"),
            avg_worst_pnl=("worst_pnl", "mean"),
            avg_recovery=("recovery_from_worst", "mean"),
            avg_giveback=("giveback_from_best", "mean"),
            avg_duration=("max_duration_sec", "mean"),
        )
        .reset_index()
        .sort_values(["side", "sum_final_pnl"])
    )

    out_trades = out_dir / f"trade_state_details_{args.label}.csv"
    out_summary = out_dir / f"trade_state_summary_{args.label}.csv"

    trades.to_csv(out_trades, index=False)
    state_summary.to_csv(out_summary, index=False)

    print("TRADE STATE CLASSIFICATION COMPLETE")
    print(f"input_rows: {len(df)}")
    print(f"trades_classified: {len(trades)}")
    print(f"details_csv: {out_trades}")
    print(f"summary_csv: {out_summary}")
    print()
    print(state_summary.to_string(index=False))
    print()
    print("WORST COLLAPSING TRADES")
    print(
        trades[trades["trade_state"].isin(["STATE_COLLAPSING", "STATE_BEAR_DEGRADING"])]
        .sort_values("worst_pnl")
        .head(25)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
