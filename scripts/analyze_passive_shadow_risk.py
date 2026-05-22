#!/usr/bin/env python3
# ASCII-only.
# Analyze passive STEP11B shadow risk snapshots.
# Research-only. No trading decisions. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--shadow-csv", default="live_logs/passive_shadow_risk_snapshots.csv")
    p.add_argument("--trades-csv", default="live_logs/trades_l1_auto_analysis.csv")
    p.add_argument("--trades-jsonl", default="live_logs/trades_l1.jsonl")
    p.add_argument("--out-dir", default="reports/passive_shadow_risk")
    p.add_argument("--label", default="STEP11B_shadow_risk")
    return p.parse_args()


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def load_trades_jsonl(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_json(path, lines=True)


def require_columns(df: pd.DataFrame, cols: set[str], name: str) -> None:
    missing = sorted(cols - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: {name} missing columns: {missing}")


def risk_summary(shadow: pd.DataFrame) -> pd.DataFrame:
    return (
        shadow.groupby(["side", "market_regime", "atr_quality", "shadow_risk_name"], dropna=False)
        .agg(
            snapshots=("snapshot_id", "count"),
            avg_score=("current_score", "mean"),
            median_score=("current_score", "median"),
            min_score=("current_score", "min"),
            max_score=("current_score", "max"),
        )
        .reset_index()
        .sort_values(["side", "market_regime", "atr_quality", "shadow_risk_name"])
    )


def trade_level_shadow(shadow: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    shadow = shadow.copy()
    trades = trades.copy()

    shadow["entry_timestamp_utc"] = shadow["entry_timestamp_utc"].astype(str)
    trades["entry_timestamp_utc"] = trades["entry_timestamp_utc"].astype(str)

    rows = []

    for entry_ts, g in shadow.groupby("entry_timestamp_utc", dropna=False):
        g = g.sort_values("tick_id").reset_index(drop=True)

        risk_counts = g["shadow_risk_name"].value_counts().to_dict()
        max_level = int(g["shadow_risk_level"].max())

        first_warning = g[g["shadow_risk_level"] >= 1]
        first_toxic = g[g["shadow_risk_level"] >= 2]
        first_collapse = g[g["shadow_risk_level"] >= 3]

        total = len(g)

        rows.append(
            {
                "entry_timestamp_utc": entry_ts,
                "side": str(g.iloc[-1]["side"]),
                "snapshots": total,
                "max_shadow_risk_level": max_level,
                "max_shadow_risk_name": str(g.loc[g["shadow_risk_level"].idxmax(), "shadow_risk_name"]),
                "safe_ratio": risk_counts.get("SAFE", 0) / total,
                "warning_ratio": risk_counts.get("WARNING", 0) / total,
                "toxic_ratio": risk_counts.get("TOXIC", 0) / total,
                "collapse_ratio": risk_counts.get("COLLAPSE_RISK", 0) / total,
                "first_warning_tick": int(first_warning.iloc[0]["tick_id"]) if len(first_warning) else None,
                "first_toxic_tick": int(first_toxic.iloc[0]["tick_id"]) if len(first_toxic) else None,
                "first_collapse_tick": int(first_collapse.iloc[0]["tick_id"]) if len(first_collapse) else None,
                "dominant_regime": str(g["market_regime"].mode().iloc[0]) if len(g["market_regime"].mode()) else "",
                "dominant_atr_quality": str(g["atr_quality"].mode().iloc[0]) if len(g["atr_quality"].mode()) else "",
            }
        )

    trade_shadow = pd.DataFrame(rows)

    merge_cols = [
        "entry_timestamp_utc",
        "side",
        "exit_reason",
        "pnl",
        "pnl_pct",
        "duration_sec",
    ]

    available = [c for c in merge_cols if c in trades.columns]

    merged = trade_shadow.merge(
        trades[available],
        on="entry_timestamp_utc",
        how="left",
        suffixes=("", "_trade"),
    )

    if "pnl" in merged.columns:
        merged["final_win"] = (merged["pnl"] > 0).astype(int)

    return merged


def trade_outcome_summary(trade_shadow: pd.DataFrame) -> pd.DataFrame:
    required = {"side", "max_shadow_risk_name", "pnl", "final_win"}
    if not required.issubset(set(trade_shadow.columns)):
        return pd.DataFrame()

    return (
        trade_shadow.groupby(["side", "max_shadow_risk_name"], dropna=False)
        .agg(
            trades=("entry_timestamp_utc", "count"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            total_pnl=("pnl", "sum"),
            winrate=("final_win", "mean"),
            avg_safe_ratio=("safe_ratio", "mean"),
            avg_warning_ratio=("warning_ratio", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_duration_sec=("duration_sec", "mean"),
        )
        .reset_index()
        .sort_values(["side", "total_pnl"], ascending=[True, False])
    )


def main() -> int:
    args = parse_args()

    shadow_path = Path(args.shadow_csv)
    trades_path = Path(args.trades_jsonl)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    shadow = safe_read_csv(shadow_path)
    trades = load_trades_jsonl(trades_path)

    require_columns(
        shadow,
        {
            "tick_id",
            "timestamp_utc",
            "snapshot_id",
            "entry_timestamp_utc",
            "side",
            "position",
            "price",
            "current_score",
            "market_regime",
            "atr_quality",
            "shadow_risk_level",
            "shadow_risk_name",
            "shadow_risk_reason",
        },
        "shadow",
    )

    require_columns(
        trades,
        {
            "entry_timestamp_utc",
            "side",
            "pnl",
            "pnl_pct",
            "duration_sec",
            "exit_reason",
        },
        "trades",
    )

    snapshot_summary = risk_summary(shadow)
    trade_shadow = trade_level_shadow(shadow, trades)
    outcome_summary = trade_outcome_summary(trade_shadow)

    snapshot_out = out_dir / f"passive_shadow_snapshot_summary_{args.label}.csv"
    trade_out = out_dir / f"passive_shadow_trade_detail_{args.label}.csv"
    outcome_out = out_dir / f"passive_shadow_trade_outcome_summary_{args.label}.csv"

    snapshot_summary.to_csv(snapshot_out, index=False)
    trade_shadow.to_csv(trade_out, index=False)
    outcome_summary.to_csv(outcome_out, index=False)

    print("OK: passive shadow risk analysis written")
    print(f"snapshot_summary: {snapshot_out}")
    print(f"trade_detail: {trade_out}")
    print(f"outcome_summary: {outcome_out}")
    print("")
    print("SNAPSHOT SUMMARY")
    print(snapshot_summary.to_string(index=False))
    print("")
    print("OUTCOME SUMMARY")
    if outcome_summary.empty:
        print("EMPTY")
    else:
        print(outcome_summary.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
