#!/usr/bin/env python3
# ASCII-only.
# Research-only transition analysis for STEP11A lifecycle snapshots.
# Does not affect trading logic.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--lifecycle-csv", default="live_logs/trade_lifecycle_snapshots.csv")
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="state_transitions")
    return p.parse_args()


def snapshot_state(row: pd.Series) -> str:
    pnl = float(row["unrealized_pnl"])
    score = int(row["current_score"])
    regime = str(row["market_regime"]).strip().lower()
    atr = str(row["atr_quality"]).strip().lower()

    if pnl >= 100:
        return "SNAP_STRONG_PROFIT"

    if pnl > 0:
        return "SNAP_PROFIT"

    if pnl <= -300:
        return "SNAP_SEVERE_LOSS"

    if pnl <= -100:
        return "SNAP_MAJOR_LOSS"

    if pnl < 0 and regime == "bear":
        return "SNAP_BEAR_LOSS"

    if pnl < 0:
        return "SNAP_SMALL_LOSS"

    if regime == "bear" and score <= 0:
        return "SNAP_WEAK_BEAR"

    if regime == "bull" and score >= 0:
        return "SNAP_STABLE_BULL"

    if atr == "bad_atr":
        return "SNAP_BAD_ATR"

    return "SNAP_NEUTRAL"


def main() -> int:
    args = parse_args()

    in_path = Path(args.lifecycle_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: lifecycle csv not found: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "entry_timestamp_utc",
        "timestamp_utc",
        "side",
        "duration_sec",
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
    df["snap_state"] = df.apply(snapshot_state, axis=1)

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.sort_values("duration_sec").reset_index(drop=True)

        for i in range(1, len(g)):
            prev = g.iloc[i - 1]
            cur = g.iloc[i]

            pnl_delta = float(cur["unrealized_pnl"]) - float(prev["unrealized_pnl"])
            score_delta = int(cur["current_score"]) - int(prev["current_score"])

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": str(cur["side"]),
                    "from_duration_sec": float(prev["duration_sec"]),
                    "to_duration_sec": float(cur["duration_sec"]),
                    "from_state": str(prev["snap_state"]),
                    "to_state": str(cur["snap_state"]),
                    "transition": str(prev["snap_state"]) + " -> " + str(cur["snap_state"]),
                    "from_pnl": float(prev["unrealized_pnl"]),
                    "to_pnl": float(cur["unrealized_pnl"]),
                    "pnl_delta": pnl_delta,
                    "from_score": int(prev["current_score"]),
                    "to_score": int(cur["current_score"]),
                    "score_delta": score_delta,
                    "from_regime": str(prev["market_regime"]),
                    "to_regime": str(cur["market_regime"]),
                    "from_atr": str(prev["atr_quality"]),
                    "to_atr": str(cur["atr_quality"]),
                }
            )

    trans = pd.DataFrame(rows)

    if trans.empty:
        raise SystemExit("ERROR: no transitions found. Need trades with at least 2 snapshots.")

    trans["transition_quality"] = trans["pnl_delta"].apply(
        lambda x: "improving" if x > 0 else ("worsening" if x < 0 else "flat")
    )

    summary = (
        trans.groupby(["side", "transition"], dropna=False)
        .agg(
            count=("trade_id", "count"),
            avg_pnl_delta=("pnl_delta", "mean"),
            sum_pnl_delta=("pnl_delta", "sum"),
            min_pnl_delta=("pnl_delta", "min"),
            max_pnl_delta=("pnl_delta", "max"),
            avg_to_pnl=("to_pnl", "mean"),
        )
        .reset_index()
        .sort_values(["side", "sum_pnl_delta"])
    )

    regime_summary = (
        trans.groupby(["side", "from_regime", "to_regime"], dropna=False)
        .agg(
            count=("trade_id", "count"),
            avg_pnl_delta=("pnl_delta", "mean"),
            sum_pnl_delta=("pnl_delta", "sum"),
            avg_to_pnl=("to_pnl", "mean"),
        )
        .reset_index()
        .sort_values(["side", "sum_pnl_delta"])
    )

    duration_summary = (
        trans.groupby(["side", "from_duration_sec", "to_duration_sec"], dropna=False)
        .agg(
            count=("trade_id", "count"),
            avg_pnl_delta=("pnl_delta", "mean"),
            sum_pnl_delta=("pnl_delta", "sum"),
            avg_to_pnl=("to_pnl", "mean"),
        )
        .reset_index()
        .sort_values(["side", "to_duration_sec"])
    )

    out_trans = out_dir / f"state_transitions_detail_{args.label}.csv"
    out_summary = out_dir / f"state_transitions_summary_{args.label}.csv"
    out_regime = out_dir / f"state_transitions_regime_{args.label}.csv"
    out_duration = out_dir / f"state_transitions_duration_{args.label}.csv"

    trans.to_csv(out_trans, index=False)
    summary.to_csv(out_summary, index=False)
    regime_summary.to_csv(out_regime, index=False)
    duration_summary.to_csv(out_duration, index=False)

    print("STATE TRANSITION ANALYSIS COMPLETE")
    print(f"input_rows: {len(df)}")
    print(f"transitions: {len(trans)}")
    print(f"detail_csv: {out_trans}")
    print(f"summary_csv: {out_summary}")
    print(f"regime_csv: {out_regime}")
    print(f"duration_csv: {out_duration}")
    print()

    print("WORST TRANSITIONS")
    print(summary.head(25).to_string(index=False))
    print()

    print("BEST TRANSITIONS")
    print(summary.sort_values("sum_pnl_delta", ascending=False).head(25).to_string(index=False))
    print()

    print("REGIME TRANSITIONS")
    print(regime_summary.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
