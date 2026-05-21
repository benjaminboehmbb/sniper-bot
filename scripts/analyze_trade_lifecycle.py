#!/usr/bin/env python3
# ASCII-only.
# Analyze trade lifecycle snapshots created by STEP11A.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--lifecycle-csv",
        default="live_logs/trade_lifecycle_snapshots.csv",
    )
    p.add_argument(
        "--out-dir",
        default="reports/trade_lifecycle",
    )
    p.add_argument(
        "--label",
        default="lifecycle_analysis",
    )
    return p.parse_args()


def safe_group(df: pd.DataFrame, cols: list[str], value: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby(cols, dropna=False)[value]
        .agg(["count", "mean", "median", "sum", "min", "max"])
        .reset_index()
        .sort_values(["sum", "mean"], ascending=[True, True])
    )


def main() -> int:
    args = parse_args()

    in_path = Path(args.lifecycle_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: lifecycle csv not found: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "timestamp_utc",
        "side",
        "duration_sec",
        "entry_timestamp_utc",
        "unrealized_pnl",
        "current_score",
        "market_regime",
        "atr_quality",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df = df.copy()
    df["trade_id"] = df["entry_timestamp_utc"]
    df["duration_min"] = df["duration_sec"] / 60.0

    df["duration_band"] = pd.cut(
        df["duration_sec"],
        bins=[0, 900, 1500, 2100, 2700, 3600, 10**9],
        labels=[
            "lt_15m",
            "15m_to_25m",
            "25m_to_35m",
            "35m_to_45m",
            "45m_to_60m",
            "gt_60m",
        ],
        right=False,
    )

    # Snapshot-level summaries.
    summary_parts = []

    for side in ["long", "short"]:
        x = df[df["side"] == side].copy()
        if x.empty:
            continue

        for name, cols in [
            ("side_duration", ["side", "duration_band"]),
            ("side_regime", ["side", "market_regime"]),
            ("side_score", ["side", "current_score"]),
            ("side_atr", ["side", "atr_quality"]),
            ("side_duration_regime", ["side", "duration_band", "market_regime"]),
            ("side_duration_score", ["side", "duration_band", "current_score"]),
            ("side_duration_atr", ["side", "duration_band", "atr_quality"]),
        ]:
            tmp = safe_group(x, cols, "unrealized_pnl")
            if not tmp.empty:
                tmp.insert(0, "group_name", name)
                summary_parts.append(tmp)

    snapshot_summary = (
        pd.concat(summary_parts, ignore_index=True)
        if summary_parts
        else pd.DataFrame()
    )

    # Trade-level recovery/collapse table.
    trade_rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.sort_values("duration_sec")
        first = g.iloc[0]
        last = g.iloc[-1]

        side = str(first["side"])
        first_pnl = float(first["unrealized_pnl"])
        worst_pnl = float(g["unrealized_pnl"].min())
        best_pnl = float(g["unrealized_pnl"].max())
        final_pnl = float(last["unrealized_pnl"])
        recovery_from_worst = final_pnl - worst_pnl
        giveback_from_best = best_pnl - final_pnl

        bear_count = int((g["market_regime"] == "bear").sum())
        bull_count = int((g["market_regime"] == "bull").sum())
        bad_atr_count = int((g["atr_quality"] == "bad_atr").sum())
        good_atr_count = int((g["atr_quality"] == "good_atr").sum())

        if final_pnl > 0:
            final_class = "final_positive"
        elif final_pnl < 0:
            final_class = "final_negative"
        else:
            final_class = "final_flat"

        if worst_pnl < 0 and recovery_from_worst <= 0:
            recovery_class = "no_recovery"
        elif worst_pnl < 0 and final_pnl < 0:
            recovery_class = "partial_recovery_negative"
        elif worst_pnl < 0 and final_pnl >= 0:
            recovery_class = "recovered_to_nonnegative"
        else:
            recovery_class = "never_negative"

        if worst_pnl <= -500:
            severity = "severe_collapse"
        elif worst_pnl <= -200:
            severity = "major_collapse"
        elif worst_pnl <= -50:
            severity = "moderate_collapse"
        elif worst_pnl < 0:
            severity = "minor_adverse"
        else:
            severity = "no_adverse"

        trade_rows.append(
            {
                "trade_id": trade_id,
                "side": side,
                "snapshots": int(len(g)),
                "first_timestamp_utc": first["timestamp_utc"],
                "last_timestamp_utc": last["timestamp_utc"],
                "max_duration_sec": float(g["duration_sec"].max()),
                "first_pnl": first_pnl,
                "worst_pnl": worst_pnl,
                "best_pnl": best_pnl,
                "final_snapshot_pnl": final_pnl,
                "recovery_from_worst": recovery_from_worst,
                "giveback_from_best": giveback_from_best,
                "bear_snapshots": bear_count,
                "bull_snapshots": bull_count,
                "bad_atr_snapshots": bad_atr_count,
                "good_atr_snapshots": good_atr_count,
                "final_class": final_class,
                "recovery_class": recovery_class,
                "severity": severity,
            }
        )

    trade_summary = pd.DataFrame(trade_rows)

    recovery_summary = safe_group(
        trade_summary,
        ["side", "recovery_class", "severity"],
        "final_snapshot_pnl",
    )

    collapse_summary = safe_group(
        trade_summary,
        ["side", "severity"],
        "worst_pnl",
    )

    long_bear_risk = df[
        (df["side"] == "long")
        & (df["duration_sec"] >= 1500)
        & (df["market_regime"] == "bear")
    ].copy()

    long_bear_summary = safe_group(
        long_bear_risk,
        ["duration_band", "current_score", "atr_quality"],
        "unrealized_pnl",
    )

    out_snapshot = out_dir / f"snapshot_summary_{args.label}.csv"
    out_trades = out_dir / f"trade_recovery_{args.label}.csv"
    out_recovery = out_dir / f"recovery_summary_{args.label}.csv"
    out_collapse = out_dir / f"collapse_summary_{args.label}.csv"
    out_long_bear = out_dir / f"long_bear_risk_{args.label}.csv"

    snapshot_summary.to_csv(out_snapshot, index=False)
    trade_summary.to_csv(out_trades, index=False)
    recovery_summary.to_csv(out_recovery, index=False)
    collapse_summary.to_csv(out_collapse, index=False)
    long_bear_summary.to_csv(out_long_bear, index=False)

    print("TRADE LIFECYCLE ANALYSIS COMPLETE")
    print(f"input_rows: {len(df)}")
    print(f"trades_with_snapshots: {len(trade_summary)}")
    print()
    print(f"snapshot_summary_csv: {out_snapshot}")
    print(f"trade_recovery_csv: {out_trades}")
    print(f"recovery_summary_csv: {out_recovery}")
    print(f"collapse_summary_csv: {out_collapse}")
    print(f"long_bear_risk_csv: {out_long_bear}")
    print()

    print("TOP WORST TRADES")
    print(
        trade_summary.sort_values("worst_pnl")
        .head(20)
        .to_string(index=False)
    )
    print()

    print("TOP RECOVERIES")
    print(
        trade_summary.sort_values("recovery_from_worst", ascending=False)
        .head(20)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
