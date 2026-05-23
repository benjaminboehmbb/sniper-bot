#!/usr/bin/env python3
# ASCII-only.
# STEP11 factor strength analysis.
# Research-only. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--v2-detail", required=True)
    p.add_argument("--persistence-detail", required=True)
    p.add_argument("--recovery-detail", required=True)
    p.add_argument("--out-dir", default="reports/passive_shadow_risk")
    p.add_argument("--label", default="STEP11_factor_strength")
    return p.parse_args()


def factor_summary(df: pd.DataFrame, factor: str) -> pd.DataFrame:
    return (
        df.groupby(["side", factor], dropna=False)
        .agg(
            trades=("entry_timestamp_utc", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_duration_sec=("duration_sec", "mean"),
        )
        .reset_index()
        .rename(columns={factor: "factor_value"})
        .assign(factor_name=factor)
        .sort_values(["side", "total_pnl"], ascending=[True, False])
    )


def main() -> int:
    args = parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    v2 = pd.read_csv(args.v2_detail)
    persistence = pd.read_csv(args.persistence_detail)
    recovery = pd.read_csv(args.recovery_detail)

    key = ["entry_timestamp_utc"]

    keep_v2 = [
        "entry_timestamp_utc",
        "side",
        "pnl",
        "duration_sec",
        "final_win",
        "compatibility_adjusted_risk",
        "toxic_ratio",
        "safe_ratio",
        "warning_ratio",
        "highly_compatible_ratio",
        "highly_toxic_structure_ratio",
    ]

    keep_persistence = [
        "entry_timestamp_utc",
        "persistent_toxicity_class",
        "longest_toxic_streak",
        "recovery_ratio",
    ]

    keep_recovery = [
        "entry_timestamp_utc",
        "recovery_transition_class",
        "recovery_events",
        "deterioration_events",
        "recovery_balance",
        "safe_ratio_after_first_toxic",
    ]

    df = (
        v2[keep_v2]
        .merge(persistence[keep_persistence], on=key, how="left")
        .merge(recovery[keep_recovery], on=key, how="left")
    )

    df["failed_recovery_flag"] = (
        df["recovery_transition_class"].astype(str).eq("FAILED_RECOVERY")
    ).astype(int)

    df["persistent_toxic_flag"] = (
        df["persistent_toxicity_class"]
        .astype(str)
        .isin(["HIGH_PERSISTENT_TOXICITY", "EXTREME_PERSISTENT_TOXICITY"])
    ).astype(int)

    df["structural_toxic_flag"] = (
        df["compatibility_adjusted_risk"].astype(str).eq("STRUCTURAL_TOXIC")
    ).astype(int)

    df["structural_warning_flag"] = (
        df["compatibility_adjusted_risk"].astype(str).eq("STRUCTURAL_WARNING")
    ).astype(int)

    df["compatible_flag"] = (
        df["compatibility_adjusted_risk"].astype(str).eq("COMPATIBLE")
    ).astype(int)

    factors = [
        "compatibility_adjusted_risk",
        "persistent_toxicity_class",
        "recovery_transition_class",
        "failed_recovery_flag",
        "persistent_toxic_flag",
        "structural_toxic_flag",
        "structural_warning_flag",
        "compatible_flag",
    ]

    summaries = [factor_summary(df, f) for f in factors]
    all_summary = pd.concat(summaries, ignore_index=True)

    numeric_cols = [
        "pnl",
        "toxic_ratio",
        "safe_ratio",
        "warning_ratio",
        "highly_compatible_ratio",
        "highly_toxic_structure_ratio",
        "longest_toxic_streak",
        "recovery_ratio",
        "recovery_events",
        "deterioration_events",
        "recovery_balance",
        "safe_ratio_after_first_toxic",
    ]

    corr = (
        df[numeric_cols]
        .corr(numeric_only=True)["pnl"]
        .reset_index()
        .rename(columns={"index": "factor", "pnl": "corr_with_pnl"})
        .sort_values("corr_with_pnl", ascending=False)
    )

    detail_out = out_dir / f"state_factor_strength_detail_{args.label}.csv"
    summary_out = out_dir / f"state_factor_strength_summary_{args.label}.csv"
    corr_out = out_dir / f"state_factor_strength_correlations_{args.label}.csv"

    df.to_csv(detail_out, index=False)
    all_summary.to_csv(summary_out, index=False)
    corr.to_csv(corr_out, index=False)

    print("OK: state factor strength analysis written")
    print(f"detail: {detail_out}")
    print(f"summary: {summary_out}")
    print(f"correlations: {corr_out}")
    print("")
    print("FACTOR SUMMARY")
    print(all_summary.to_string(index=False))
    print("")
    print("CORRELATIONS WITH PNL")
    print(corr.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
