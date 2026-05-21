#!/usr/bin/env python3
# ASCII-only.
# Research-only collapse recovery pattern analysis.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--momentum-csv",
        default="reports/trade_lifecycle/health_momentum_detail_STEP9A_FULL_43M.csv",
    )
    p.add_argument(
        "--out-dir",
        default="reports/trade_lifecycle",
    )
    p.add_argument(
        "--label",
        default="collapse_recovery_patterns",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    in_path = Path(args.momentum_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing momentum csv: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "duration_sec",
        "market_regime",
        "current_score",
        "health_score",
        "health_delta",
        "momentum_bucket",
        "pnl_delta",
        "current_pnl",
        "future_best_delta",
        "future_worst_delta",
        "final_trade_pnl",
        "future_recovery",
        "future_collapse",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    # Collapse candidates: strong deterioration or bad current health.
    x = df[
        (df["momentum_bucket"].isin(["MOMENTUM_COLLAPSE", "MOMENTUM_DEGRADING"]))
        | (df["health_score"] <= -55)
        | (df["pnl_delta"] <= -50)
    ].copy()

    if x.empty:
        raise SystemExit("ERROR: no collapse candidates found")

    x["recovery_class"] = x.apply(
        lambda r: "RECOVERED"
        if (float(r["future_best_delta"]) >= 50 and float(r["final_trade_pnl"]) > 0)
        else (
            "PARTIAL_RECOVERY"
            if float(r["future_best_delta"]) >= 50
            else "NO_RECOVERY"
        ),
        axis=1,
    )

    x["terminal_outcome"] = x["final_trade_pnl"].apply(
        lambda v: "FINAL_WIN" if float(v) > 0 else "FINAL_LOSS"
    )

    x["duration_band"] = pd.cut(
        x["duration_sec"],
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

    summary = (
        x.groupby(
            [
                "side",
                "recovery_class",
                "terminal_outcome",
                "market_regime",
                "duration_band",
            ],
            dropna=False,
            observed=False,
        )
        .agg(
            rows=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_health=("health_score", "mean"),
            avg_health_delta=("health_delta", "mean"),
            avg_pnl_delta=("pnl_delta", "mean"),
            avg_current_pnl=("current_pnl", "mean"),
            avg_future_best=("future_best_delta", "mean"),
            avg_future_worst=("future_worst_delta", "mean"),
            avg_final_pnl=("final_trade_pnl", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_final_pnl"])
    )

    score_summary = (
        x.groupby(
            ["side", "recovery_class", "current_score", "market_regime"],
            dropna=False,
            observed=False,
        )
        .agg(
            rows=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_health=("health_score", "mean"),
            avg_health_delta=("health_delta", "mean"),
            avg_pnl_delta=("pnl_delta", "mean"),
            avg_current_pnl=("current_pnl", "mean"),
            avg_future_best=("future_best_delta", "mean"),
            avg_future_worst=("future_worst_delta", "mean"),
            avg_final_pnl=("final_trade_pnl", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_final_pnl"])
    )

    out_detail = out_dir / f"collapse_recovery_detail_{args.label}.csv"
    out_summary = out_dir / f"collapse_recovery_summary_{args.label}.csv"
    out_score = out_dir / f"collapse_recovery_score_summary_{args.label}.csv"

    x.to_csv(out_detail, index=False)
    summary.to_csv(out_summary, index=False)
    score_summary.to_csv(out_score, index=False)

    print("COLLAPSE RECOVERY PATTERN ANALYSIS COMPLETE")
    print(f"collapse_candidate_rows: {len(x)}")
    print(f"unique_trades: {x['trade_id'].nunique()}")
    print(f"detail_csv: {out_detail}")
    print(f"summary_csv: {out_summary}")
    print(f"score_summary_csv: {out_score}")
    print()

    print("SUMMARY WORST GROUPS")
    print(summary.head(30).to_string(index=False))
    print()

    print("SUMMARY BEST RECOVERY GROUPS")
    print(summary.sort_values("avg_final_pnl", ascending=False).head(30).to_string(index=False))
    print()

    print("SCORE SUMMARY WORST GROUPS")
    print(score_summary.head(30).to_string(index=False))
    print()

    print("SCORE SUMMARY BEST GROUPS")
    print(score_summary.sort_values("avg_final_pnl", ascending=False).head(30).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
