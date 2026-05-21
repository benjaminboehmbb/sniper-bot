#!/usr/bin/env python3
# ASCII-only.
# Time-weighted toxic persistence model.
# Research/passive only. No trading decisions.

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


def classify_weighted_risk(toxic_time_ratio: float, longest_toxic_streak: int):
    if toxic_time_ratio >= 0.85 and longest_toxic_streak >= 3:
        return "TIME_WEIGHTED_COLLAPSE_RISK"
    if toxic_time_ratio >= 0.65 and longest_toxic_streak >= 2:
        return "TIME_WEIGHTED_TOXIC"
    if toxic_time_ratio >= 0.35:
        return "TIME_WEIGHTED_WARNING"
    if toxic_time_ratio > 0:
        return "TEMPORARY_TOXICITY"
    return "NO_TOXICITY"


def main():
    args = parse_args()

    in_path = Path(args.detail)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing detail file: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "from_duration_sec",
        "to_duration_sec",
        "structure_label",
        "final_trade_pnl",
        "final_win",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.sort_values("from_duration_sec").reset_index(drop=True)

        toxic_time = 0.0
        total_time = 0.0

        current_streak = 0
        longest_streak = 0
        toxic_segments = 0

        first_toxic_sec = None

        for _, r in g.iterrows():
            start = float(r["from_duration_sec"])
            end = float(r["to_duration_sec"])
            duration = max(0.0, end - start)

            is_toxic = str(r["structure_label"]) == "HIGHLY_TOXIC"

            total_time += duration

            if is_toxic:
                toxic_time += duration
                toxic_segments += 1
                current_streak += 1
                longest_streak = max(longest_streak, current_streak)

                if first_toxic_sec is None:
                    first_toxic_sec = start
            else:
                current_streak = 0

        toxic_time_ratio = toxic_time / total_time if total_time > 0 else 0.0

        rows.append(
            {
                "trade_id": trade_id,
                "side": str(g.iloc[-1]["side"]).lower(),
                "total_time_sec": total_time,
                "toxic_time_sec": toxic_time,
                "toxic_time_ratio": toxic_time_ratio,
                "toxic_segments": toxic_segments,
                "longest_toxic_streak": longest_streak,
                "first_toxic_sec": first_toxic_sec,
                "weighted_risk_class": classify_weighted_risk(
                    toxic_time_ratio,
                    longest_streak,
                ),
                "final_trade_pnl": float(g.iloc[-1]["final_trade_pnl"]),
                "final_win": int(g.iloc[-1]["final_win"]),
            }
        )

    out = pd.DataFrame(rows)

    summary = (
        out.groupby(["side", "weighted_risk_class"], dropna=False)
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
            avg_toxic_time_ratio=("toxic_time_ratio", "mean"),
            avg_toxic_time_sec=("toxic_time_sec", "mean"),
            avg_longest_toxic_streak=("longest_toxic_streak", "mean"),
            avg_first_toxic_sec=("first_toxic_sec", "mean"),
        )
        .reset_index()
        .sort_values(["avg_final_pnl", "final_winrate"], ascending=[False, False])
    )

    detail_csv = out_dir / f"time_weighted_toxic_detail_{args.label}.csv"
    summary_csv = out_dir / f"time_weighted_toxic_summary_{args.label}.csv"

    out.to_csv(detail_csv, index=False)
    summary.to_csv(summary_csv, index=False)

    print("TIME-WEIGHTED TOXIC PERSISTENCE COMPLETE")
    print(f"trades: {len(out)}")
    print(f"detail_csv: {detail_csv}")
    print(f"summary_csv: {summary_csv}")
    print()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
