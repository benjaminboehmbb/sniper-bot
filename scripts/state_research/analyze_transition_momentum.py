#!/usr/bin/env python3
# ASCII-only.
# STEP11C transition momentum research.
# Research-only. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()

    p.add_argument(
        "--shadow-csv",
        default="live_logs/passive_shadow_risk_snapshots.csv",
    )

    p.add_argument(
        "--trades-jsonl",
        default="live_logs/trades_l1.jsonl",
    )

    p.add_argument(
        "--out-dir",
        default="reports/passive_shadow_risk",
    )

    p.add_argument(
        "--label",
        default="STEP11C_transition_momentum",
    )

    return p.parse_args()


def classify_transition(avg_delta: float, flip_rate: float) -> str:

    if avg_delta <= -0.50:
        return "ACCELERATING_DEGRADATION"

    if avg_delta < 0:
        return "SLOW_DEGRADATION"

    if avg_delta >= 0.50:
        return "STRONG_RECOVERY"

    if avg_delta > 0:
        return "WEAK_RECOVERY"

    if flip_rate >= 0.50:
        return "HIGHLY_VOLATILE"

    return "NEUTRAL"


def main() -> int:
    args = parse_args()

    shadow_path = Path(args.shadow_csv)
    trades_path = Path(args.trades_jsonl)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not shadow_path.exists():
        raise SystemExit(f"ERROR: missing shadow csv: {shadow_path}")

    if not trades_path.exists():
        raise SystemExit(f"ERROR: missing trades jsonl: {trades_path}")

    shadow = pd.read_csv(shadow_path)
    trades = pd.read_json(trades_path, lines=True)

    required_shadow = {
        "entry_timestamp_utc",
        "side",
        "market_regime",
        "shadow_risk_level",
    }

    required_trades = {
        "entry_timestamp_utc",
        "side",
        "pnl",
        "duration_sec",
    }

    missing_shadow = sorted(required_shadow - set(shadow.columns))
    missing_trades = sorted(required_trades - set(trades.columns))

    if missing_shadow:
        raise SystemExit(f"ERROR: missing shadow columns: {missing_shadow}")

    if missing_trades:
        raise SystemExit(f"ERROR: missing trades columns: {missing_trades}")

    shadow["entry_timestamp_utc"] = shadow["entry_timestamp_utc"].astype(str)
    trades["entry_timestamp_utc"] = trades["entry_timestamp_utc"].astype(str)

    rows = []

    for entry_ts, g in shadow.groupby("entry_timestamp_utc", dropna=False):

        g = g.sort_values("tick_id").reset_index(drop=True)

        levels = list(g["shadow_risk_level"].astype(int))

        deltas = []
        flips = 0

        for i in range(1, len(levels)):
            prev = levels[i - 1]
            cur = levels[i]

            delta = prev - cur
            deltas.append(delta)

            if (prev <= 1 and cur >= 2) or (prev >= 2 and cur <= 1):
                flips += 1

        avg_delta = (
            sum(deltas) / len(deltas)
            if deltas else 0.0
        )

        flip_rate = (
            flips / len(deltas)
            if deltas else 0.0
        )

        degradation_acceleration = sum(
            1 for d in deltas if d <= -1
        )

        recovery_acceleration = sum(
            1 for d in deltas if d >= 1
        )

        stabilization_score = (
            recovery_acceleration
            - degradation_acceleration
        )

        rows.append(
            {
                "entry_timestamp_utc": entry_ts,
                "side": str(g.iloc[-1]["side"]),
                "dominant_regime": str(g["market_regime"].mode().iloc[0]),
                "snapshots": len(levels),
                "avg_transition_delta": avg_delta,
                "flip_rate": flip_rate,
                "degradation_acceleration": degradation_acceleration,
                "recovery_acceleration": recovery_acceleration,
                "stabilization_score": stabilization_score,
                "transition_momentum_class": classify_transition(
                    avg_delta,
                    flip_rate,
                ),
            }
        )

    out = pd.DataFrame(rows)

    merge_cols = [
        "entry_timestamp_utc",
        "side",
        "pnl",
        "duration_sec",
        "exit_reason",
    ]

    available = [c for c in merge_cols if c in trades.columns]

    out = out.merge(
        trades[available],
        on="entry_timestamp_utc",
        how="left",
        suffixes=("", "_trade"),
    )

    out["final_win"] = (out["pnl"] > 0).astype(int)

    summary = (
        out.groupby(
            ["side", "transition_momentum_class"],
            dropna=False,
        )
        .agg(
            trades=("entry_timestamp_utc", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_transition_delta=("avg_transition_delta", "mean"),
            avg_flip_rate=("flip_rate", "mean"),
            avg_stabilization_score=("stabilization_score", "mean"),
            avg_duration_sec=("duration_sec", "mean"),
        )
        .reset_index()
        .sort_values(
            ["side", "total_pnl"],
            ascending=[True, False],
        )
    )

    detail_out = (
        out_dir /
        f"transition_momentum_detail_{args.label}.csv"
    )

    summary_out = (
        out_dir /
        f"transition_momentum_summary_{args.label}.csv"
    )

    out.to_csv(detail_out, index=False)
    summary.to_csv(summary_out, index=False)

    print("OK: transition momentum analysis written")
    print(f"detail: {detail_out}")
    print(f"summary: {summary_out}")
    print("")
    print("TRANSITION MOMENTUM SUMMARY")
    print(summary.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
