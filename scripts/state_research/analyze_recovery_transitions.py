#!/usr/bin/env python3
# ASCII-only.
# STEP11C recovery transition research.
# Research-only. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--shadow-csv", default="live_logs/passive_shadow_risk_snapshots.csv")
    p.add_argument("--trades-jsonl", default="live_logs/trades_l1.jsonl")
    p.add_argument("--out-dir", default="reports/passive_shadow_risk")
    p.add_argument("--label", default="STEP11C_recovery_transitions")
    return p.parse_args()


def recovery_class(
    toxic_to_warning: int,
    toxic_to_safe: int,
    warning_to_safe: int,
    toxic_periods: int,
    safe_ratio_after_first_toxic: float,
) -> str:
    recovery_events = toxic_to_warning + toxic_to_safe + warning_to_safe

    if toxic_periods <= 0:
        return "NO_TOXICITY"

    if toxic_to_safe >= 1 and safe_ratio_after_first_toxic >= 0.50:
        return "STRONG_RECOVERY_AFTER_TOXICITY"

    if recovery_events >= 2 and safe_ratio_after_first_toxic >= 0.25:
        return "PARTIAL_RECOVERY_AFTER_TOXICITY"

    if recovery_events >= 1:
        return "WEAK_RECOVERY_AFTER_TOXICITY"

    return "FAILED_RECOVERY"


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
        "tick_id",
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

        levels = list(g["shadow_risk_level"].astype(int))
        total = max(1, len(levels))

        toxic_periods = sum(1 for x in levels if x >= 2)
        warning_periods = sum(1 for x in levels if x == 1)
        safe_periods = sum(1 for x in levels if x == 0)

        toxic_to_warning = 0
        toxic_to_safe = 0
        warning_to_safe = 0
        safe_to_warning = 0
        warning_to_toxic = 0
        safe_to_toxic = 0

        for i in range(1, len(levels)):
            prev = levels[i - 1]
            cur = levels[i]

            if prev >= 2 and cur == 1:
                toxic_to_warning += 1
            elif prev >= 2 and cur == 0:
                toxic_to_safe += 1
            elif prev == 1 and cur == 0:
                warning_to_safe += 1
            elif prev == 0 and cur == 1:
                safe_to_warning += 1
            elif prev == 1 and cur >= 2:
                warning_to_toxic += 1
            elif prev == 0 and cur >= 2:
                safe_to_toxic += 1

        toxic_indices = [i for i, x in enumerate(levels) if x >= 2]

        if toxic_indices:
            first_toxic_idx = toxic_indices[0]
            after_first_toxic = levels[first_toxic_idx:]
            safe_after_first_toxic = sum(1 for x in after_first_toxic if x == 0)
            safe_ratio_after_first_toxic = safe_after_first_toxic / max(1, len(after_first_toxic))
            first_toxic_tick = int(g.iloc[first_toxic_idx]["tick_id"])
        else:
            safe_ratio_after_first_toxic = 1.0
            first_toxic_tick = None

        recovery_events = toxic_to_warning + toxic_to_safe + warning_to_safe
        deterioration_events = safe_to_warning + warning_to_toxic + safe_to_toxic

        rows.append(
            {
                "entry_timestamp_utc": entry_ts,
                "side": str(g.iloc[-1]["side"]),
                "dominant_regime": str(g["market_regime"].mode().iloc[0]),
                "dominant_atr_quality": str(g["atr_quality"].mode().iloc[0]),
                "snapshots": total,
                "safe_ratio": safe_periods / total,
                "warning_ratio": warning_periods / total,
                "toxic_ratio": toxic_periods / total,
                "toxic_periods": toxic_periods,
                "first_toxic_tick": first_toxic_tick,
                "toxic_to_warning": toxic_to_warning,
                "toxic_to_safe": toxic_to_safe,
                "warning_to_safe": warning_to_safe,
                "safe_to_warning": safe_to_warning,
                "warning_to_toxic": warning_to_toxic,
                "safe_to_toxic": safe_to_toxic,
                "recovery_events": recovery_events,
                "deterioration_events": deterioration_events,
                "recovery_balance": recovery_events - deterioration_events,
                "safe_ratio_after_first_toxic": safe_ratio_after_first_toxic,
                "recovery_transition_class": recovery_class(
                    toxic_to_warning=toxic_to_warning,
                    toxic_to_safe=toxic_to_safe,
                    warning_to_safe=warning_to_safe,
                    toxic_periods=toxic_periods,
                    safe_ratio_after_first_toxic=safe_ratio_after_first_toxic,
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

    out = out.merge(
        trades[merge_cols],
        on="entry_timestamp_utc",
        how="left",
        suffixes=("", "_trade"),
    )

    out["final_win"] = (out["pnl"] > 0).astype(int)

    summary = (
        out.groupby(["side", "recovery_transition_class"], dropna=False)
        .agg(
            trades=("entry_timestamp_utc", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_recovery_events=("recovery_events", "mean"),
            avg_deterioration_events=("deterioration_events", "mean"),
            avg_recovery_balance=("recovery_balance", "mean"),
            avg_safe_ratio_after_first_toxic=("safe_ratio_after_first_toxic", "mean"),
            avg_duration_sec=("duration_sec", "mean"),
        )
        .reset_index()
        .sort_values(["side", "total_pnl"], ascending=[True, False])
    )

    detail_out = out_dir / f"recovery_transition_detail_{args.label}.csv"
    summary_out = out_dir / f"recovery_transition_summary_{args.label}.csv"

    out.to_csv(detail_out, index=False)
    summary.to_csv(summary_out, index=False)

    print("OK: recovery transition analysis written")
    print(f"detail: {detail_out}")
    print(f"summary: {summary_out}")
    print("")
    print("RECOVERY TRANSITION SUMMARY")
    print(summary.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
