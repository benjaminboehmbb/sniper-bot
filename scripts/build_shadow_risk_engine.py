#!/usr/bin/env python3
# ASCII-only.
# Shadow Risk Engine.
# Research/passive only. No trading decisions. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--labeled",
        default="reports/trade_lifecycle/structure_labeled_lifecycle_STEP9A_FULL_43M.csv",
    )
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")
    return p.parse_args()


def risk_level(label: str, toxic_ratio_so_far: float, elite_ratio_so_far: float) -> int:
    label = str(label)

    if toxic_ratio_so_far >= 0.90:
        return 3

    if toxic_ratio_so_far >= 0.70:
        return 2

    if toxic_ratio_so_far >= 0.40:
        return 1

    if label == "HIGHLY_TOXIC":
        return 1

    if label in {"ELITE_STRUCTURE", "COMPATIBLE"} and elite_ratio_so_far >= 0.50:
        return 0

    return 0


def risk_name(v: int) -> str:
    if v == 3:
        return "COLLAPSE_RISK"
    if v == 2:
        return "TOXIC"
    if v == 1:
        return "WARNING"
    return "SAFE"


def main():
    args = parse_args()

    in_path = Path(args.labeled)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing labeled lifecycle: {in_path}")

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

        toxic_count = 0
        elite_count = 0
        compatible_count = 0

        total = 0

        final_pnl = float(g.iloc[-1]["final_trade_pnl"])
        final_win = int(g.iloc[-1]["final_win"])
        side = str(g.iloc[-1]["side"]).lower()

        for _, r in g.iterrows():
            total += 1

            label = str(r["structure_label"])

            if label == "HIGHLY_TOXIC":
                toxic_count += 1

            if label == "ELITE_STRUCTURE":
                elite_count += 1

            if label == "COMPATIBLE":
                compatible_count += 1

            toxic_ratio_so_far = toxic_count / total
            elite_ratio_so_far = elite_count / total
            compatible_ratio_so_far = compatible_count / total

            lvl = risk_level(
                label=label,
                toxic_ratio_so_far=toxic_ratio_so_far,
                elite_ratio_so_far=elite_ratio_so_far,
            )

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": side,
                    "from_duration_sec": float(r["from_duration_sec"]),
                    "to_duration_sec": float(r["to_duration_sec"]),
                    "structure_label": label,
                    "toxic_ratio_so_far": toxic_ratio_so_far,
                    "elite_ratio_so_far": elite_ratio_so_far,
                    "compatible_ratio_so_far": compatible_ratio_so_far,
                    "shadow_risk_level": lvl,
                    "shadow_risk_name": risk_name(lvl),
                    "final_trade_pnl": final_pnl,
                    "final_win": final_win,
                }
            )

    out = pd.DataFrame(rows)

    trade_rows = []

    for trade_id, g in out.groupby("trade_id", dropna=False):
        g = g.sort_values("from_duration_sec").reset_index(drop=True)

        max_risk = int(g["shadow_risk_level"].max())
        first_warning = g[g["shadow_risk_level"] >= 1]
        first_toxic = g[g["shadow_risk_level"] >= 2]
        first_collapse = g[g["shadow_risk_level"] >= 3]

        trade_rows.append(
            {
                "trade_id": trade_id,
                "side": str(g.iloc[-1]["side"]),
                "max_shadow_risk_level": max_risk,
                "max_shadow_risk_name": risk_name(max_risk),
                "first_warning_sec": float(first_warning.iloc[0]["from_duration_sec"]) if len(first_warning) else None,
                "first_toxic_sec": float(first_toxic.iloc[0]["from_duration_sec"]) if len(first_toxic) else None,
                "first_collapse_sec": float(first_collapse.iloc[0]["from_duration_sec"]) if len(first_collapse) else None,
                "final_trade_pnl": float(g.iloc[-1]["final_trade_pnl"]),
                "final_win": int(g.iloc[-1]["final_win"]),
            }
        )

    trade_summary = pd.DataFrame(trade_rows)

    summary = (
        trade_summary.groupby(["side", "max_shadow_risk_name"], dropna=False)
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
            avg_first_warning_sec=("first_warning_sec", "mean"),
            avg_first_toxic_sec=("first_toxic_sec", "mean"),
            avg_first_collapse_sec=("first_collapse_sec", "mean"),
        )
        .reset_index()
        .sort_values(["avg_final_pnl", "final_winrate"], ascending=[False, False])
    )

    detail_csv = out_dir / f"shadow_risk_detail_{args.label}.csv"
    trade_csv = out_dir / f"shadow_risk_trade_summary_{args.label}.csv"
    summary_csv = out_dir / f"shadow_risk_summary_{args.label}.csv"

    out.to_csv(detail_csv, index=False)
    trade_summary.to_csv(trade_csv, index=False)
    summary.to_csv(summary_csv, index=False)

    print("SHADOW RISK ENGINE COMPLETE")
    print(f"detail_csv: {detail_csv}")
    print(f"trade_csv: {trade_csv}")
    print(f"summary_csv: {summary_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
