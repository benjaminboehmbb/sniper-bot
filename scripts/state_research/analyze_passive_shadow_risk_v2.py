#!/usr/bin/env python3
# ASCII-only.
# STEP11B V2 compatibility-aware passive shadow risk analysis.
# Research-only. No trading decisions. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--shadow-csv", default="live_logs/passive_shadow_risk_snapshots.csv")
    p.add_argument("--trades-jsonl", default="live_logs/trades_l1.jsonl")
    p.add_argument("--out-dir", default="reports/passive_shadow_risk")
    p.add_argument("--label", default="STEP11B_v2")
    return p.parse_args()


def require_columns(df: pd.DataFrame, cols: set[str], name: str) -> None:
    missing = sorted(cols - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: {name} missing columns: {missing}")


def compatibility(side: str, regime: str) -> str:
    s = str(side).lower()
    r = str(regime).lower()

    if s == "short" and r == "bear":
        return "HIGHLY_COMPATIBLE"
    if s == "long" and r == "bull":
        return "COMPATIBLE"
    if s == "long" and r == "bear":
        return "HIGHLY_TOXIC"
    if s == "short" and r == "bull":
        return "TOXIC"

    return "MIXED"


def trade_level(shadow: pd.DataFrame, trades: pd.DataFrame) -> pd.DataFrame:
    rows = []

    shadow = shadow.copy()
    trades = trades.copy()

    shadow["entry_timestamp_utc"] = shadow["entry_timestamp_utc"].astype(str)
    trades["entry_timestamp_utc"] = trades["entry_timestamp_utc"].astype(str)

    shadow["compatibility_class"] = shadow.apply(
        lambda r: compatibility(r["side"], r["market_regime"]),
        axis=1,
    )

    for entry_ts, g in shadow.groupby("entry_timestamp_utc", dropna=False):
        g = g.sort_values("tick_id").reset_index(drop=True)
        n = max(1, len(g))

        compat_counts = g["compatibility_class"].value_counts().to_dict()
        risk_counts = g["shadow_risk_name"].value_counts().to_dict()

        rows.append(
            {
                "entry_timestamp_utc": entry_ts,
                "side": str(g.iloc[-1]["side"]),
                "snapshots": len(g),
                "dominant_regime": str(g["market_regime"].mode().iloc[0]),
                "dominant_atr_quality": str(g["atr_quality"].mode().iloc[0]),
                "max_shadow_risk_level": int(g["shadow_risk_level"].max()),
                "max_shadow_risk_name": str(g.loc[g["shadow_risk_level"].idxmax(), "shadow_risk_name"]),
                "safe_ratio": risk_counts.get("SAFE", 0) / n,
                "warning_ratio": risk_counts.get("WARNING", 0) / n,
                "toxic_ratio": risk_counts.get("TOXIC", 0) / n,
                "collapse_ratio": risk_counts.get("COLLAPSE_RISK", 0) / n,
                "highly_compatible_ratio": compat_counts.get("HIGHLY_COMPATIBLE", 0) / n,
                "compatible_ratio": compat_counts.get("COMPATIBLE", 0) / n,
                "mixed_ratio": compat_counts.get("MIXED", 0) / n,
                "toxic_structure_ratio": compat_counts.get("TOXIC", 0) / n,
                "highly_toxic_structure_ratio": compat_counts.get("HIGHLY_TOXIC", 0) / n,
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
    available = [c for c in merge_cols if c in trades.columns]

    out = out.merge(
        trades[available],
        on="entry_timestamp_utc",
        how="left",
        suffixes=("", "_trade"),
    )

    out["final_win"] = (out["pnl"] > 0).astype(int)

    out["risk_false_positive_flag"] = (
        (out["max_shadow_risk_name"].isin(["TOXIC", "COLLAPSE_RISK"]))
        & (out["pnl"] > 0)
    ).astype(int)

    out["compatibility_adjusted_risk"] = out.apply(classify_adjusted_risk, axis=1)

    return out


def classify_adjusted_risk(r: pd.Series) -> str:
    side = str(r["side"]).lower()

    if float(r["highly_toxic_structure_ratio"]) >= 0.50:
        return "STRUCTURAL_TOXIC"

    if float(r["toxic_structure_ratio"]) >= 0.50:
        return "STRUCTURAL_WARNING"

    if side == "short" and float(r["highly_compatible_ratio"]) >= 0.50:
        if float(r["toxic_ratio"]) >= 0.70:
            return "COMPATIBLE_BUT_LOCALLY_TOXIC"
        return "COMPATIBLE"

    if side == "long" and float(r["compatible_ratio"]) >= 0.50:
        if float(r["warning_ratio"]) >= 0.50:
            return "COMPATIBLE_WITH_ATR_WARNING"
        return "COMPATIBLE"

    if float(r["toxic_ratio"]) >= 0.70:
        return "LOCAL_TOXIC"

    if float(r["warning_ratio"]) >= 0.50:
        return "LOCAL_WARNING"

    return "NEUTRAL"


def summaries(trade_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    by_adjusted = (
        trade_df.groupby(["side", "compatibility_adjusted_risk"], dropna=False)
        .agg(
            trades=("entry_timestamp_utc", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            false_positive_rate=("risk_false_positive_flag", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_highly_compatible_ratio=("highly_compatible_ratio", "mean"),
            avg_highly_toxic_structure_ratio=("highly_toxic_structure_ratio", "mean"),
            avg_duration_sec=("duration_sec", "mean"),
        )
        .reset_index()
        .sort_values(["side", "total_pnl"], ascending=[True, False])
    )

    false_pos = (
        trade_df[trade_df["risk_false_positive_flag"] == 1]
        .sort_values(["side", "pnl"], ascending=[True, False])
    )

    return by_adjusted, false_pos


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

    require_columns(
        shadow,
        {
            "tick_id",
            "entry_timestamp_utc",
            "side",
            "current_score",
            "market_regime",
            "atr_quality",
            "shadow_risk_level",
            "shadow_risk_name",
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

    trade_df = trade_level(shadow, trades)
    by_adjusted, false_pos = summaries(trade_df)

    trade_out = out_dir / f"passive_shadow_v2_trade_detail_{args.label}.csv"
    summary_out = out_dir / f"passive_shadow_v2_adjusted_summary_{args.label}.csv"
    false_pos_out = out_dir / f"passive_shadow_v2_false_positives_{args.label}.csv"

    trade_df.to_csv(trade_out, index=False)
    by_adjusted.to_csv(summary_out, index=False)
    false_pos.to_csv(false_pos_out, index=False)

    print("OK: STEP11B V2 compatibility-aware analysis written")
    print(f"trade_detail: {trade_out}")
    print(f"adjusted_summary: {summary_out}")
    print(f"false_positives: {false_pos_out}")
    print("")
    print("ADJUSTED SUMMARY")
    print(by_adjusted.to_string(index=False))
    print("")
    print("FALSE POSITIVES")
    if false_pos.empty:
        print("EMPTY")
    else:
        print(false_pos.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
