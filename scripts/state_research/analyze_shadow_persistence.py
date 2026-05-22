#!/usr/bin/env python3
# ASCII-only.
# STEP11B persistence-aware shadow risk analysis.
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
        default="STEP11B_persistence",
    )

    return p.parse_args()


def persistence_class(
    toxic_ratio: float,
    longest_toxic_streak: int,
    recovery_ratio: float,
) -> str:

    if toxic_ratio >= 0.70 and longest_toxic_streak >= 10:
        return "EXTREME_PERSISTENT_TOXICITY"

    if toxic_ratio >= 0.50 and longest_toxic_streak >= 5:
        return "HIGH_PERSISTENT_TOXICITY"

    if toxic_ratio >= 0.25:
        return "MODERATE_TOXICITY"

    if recovery_ratio >= 0.50:
        return "RECOVERING_STRUCTURE"

    return "TEMPORARY_INSTABILITY"


def longest_streak(values: list[int]) -> int:
    best = 0
    current = 0

    for v in values:
        if v:
            current += 1
            best = max(best, current)
        else:
            current = 0

    return best


def recovery_metrics(risk_levels: list[int]) -> tuple[int, int]:
    toxic_to_safe = 0
    toxic_periods = 0

    for i in range(1, len(risk_levels)):
        prev = risk_levels[i - 1]
        cur = risk_levels[i]

        if prev >= 2:
            toxic_periods += 1

            if cur <= 1:
                toxic_to_safe += 1

    return toxic_to_safe, toxic_periods


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
        "atr_quality",
        "shadow_risk_level",
        "shadow_risk_name",
    }

    required_trades = {
        "entry_timestamp_utc",
        "side",
        "pnl",
        "pnl_pct",
        "duration_sec",
        "exit_reason",
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

        risk_levels = list(g["shadow_risk_level"].astype(int))

        total = max(1, len(risk_levels))

        toxic_flags = [1 if v >= 2 else 0 for v in risk_levels]
        warning_flags = [1 if v == 1 else 0 for v in risk_levels]
        safe_flags = [1 if v == 0 else 0 for v in risk_levels]

        toxic_ratio = sum(toxic_flags) / total
        warning_ratio = sum(warning_flags) / total
        safe_ratio = sum(safe_flags) / total

        longest_toxic = longest_streak(toxic_flags)
        longest_warning = longest_streak(warning_flags)

        toxic_to_safe, toxic_periods = recovery_metrics(risk_levels)

        recovery_ratio = (
            toxic_to_safe / toxic_periods
            if toxic_periods > 0 else 1.0
        )

        rows.append(
            {
                "entry_timestamp_utc": entry_ts,
                "side": str(g.iloc[-1]["side"]),
                "dominant_regime": str(g["market_regime"].mode().iloc[0]),
                "dominant_atr_quality": str(g["atr_quality"].mode().iloc[0]),
                "snapshots": total,
                "safe_ratio": safe_ratio,
                "warning_ratio": warning_ratio,
                "toxic_ratio": toxic_ratio,
                "longest_toxic_streak": longest_toxic,
                "longest_warning_streak": longest_warning,
                "recovery_ratio": recovery_ratio,
                "persistent_toxicity_class": persistence_class(
                    toxic_ratio=toxic_ratio,
                    longest_toxic_streak=longest_toxic,
                    recovery_ratio=recovery_ratio,
                ),
            }
        )

    out = pd.DataFrame(rows)

    merge_cols = [
        "entry_timestamp_utc",
        "side",
        "exit_reason",
        "pnl",
        "pnl_pct",
        "duration_sec",
    ]

    trades_merge = trades[merge_cols]

    out = out.merge(
        trades_merge,
        on="entry_timestamp_utc",
        how="left",
        suffixes=("", "_trade"),
    )

    out["final_win"] = (out["pnl"] > 0).astype(int)

    summary = (
        out.groupby(
            ["side", "persistent_toxicity_class"],
            dropna=False,
        )
        .agg(
            trades=("entry_timestamp_utc", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_recovery_ratio=("recovery_ratio", "mean"),
            avg_longest_toxic_streak=("longest_toxic_streak", "mean"),
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
        f"shadow_persistence_detail_{args.label}.csv"
    )

    summary_out = (
        out_dir /
        f"shadow_persistence_summary_{args.label}.csv"
    )

    out.to_csv(detail_out, index=False)
    summary.to_csv(summary_out, index=False)

    print("OK: persistence-aware shadow analysis written")
    print(f"detail: {detail_out}")
    print(f"summary: {summary_out}")
    print("")
    print("PERSISTENCE SUMMARY")
    print(summary.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
