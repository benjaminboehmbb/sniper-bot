#!/usr/bin/env python3
# ASCII-only.
# Analyze passive structure overlay warning power.
# No trading logic. No execution changes.

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


def main():
    args = parse_args()

    in_path = Path(args.labeled)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

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

        final_pnl = float(g.iloc[-1]["final_trade_pnl"])
        final_win = int(g.iloc[-1]["final_win"])
        side = str(g.iloc[-1]["side"]).lower()

        toxic = g[g["structure_label"] == "HIGHLY_TOXIC"]
        elite = g[g["structure_label"] == "ELITE_STRUCTURE"]
        compatible = g[g["structure_label"] == "COMPATIBLE"]

        rows.append(
            {
                "trade_id": trade_id,
                "side": side,
                "final_trade_pnl": final_pnl,
                "final_win": final_win,
                "had_highly_toxic": int(len(toxic) > 0),
                "had_elite": int(len(elite) > 0),
                "had_compatible": int(len(compatible) > 0),
                "first_toxic_sec": float(toxic.iloc[0]["from_duration_sec"]) if len(toxic) else None,
                "toxic_count": int(len(toxic)),
                "elite_count": int(len(elite)),
                "compatible_count": int(len(compatible)),
                "total_edges": int(len(g)),
                "toxic_ratio": float(len(toxic) / max(1, len(g))),
                "elite_ratio": float(len(elite) / max(1, len(g))),
                "compatible_ratio": float(len(compatible) / max(1, len(g))),
            }
        )

    out = pd.DataFrame(rows)

    summary = (
        out.groupby(["side", "had_highly_toxic", "had_elite", "had_compatible"], dropna=False)
        .agg(
            trades=("trade_id", "count"),
            avg_final_pnl=("final_trade_pnl", "mean"),
            median_final_pnl=("final_trade_pnl", "median"),
            final_winrate=("final_win", "mean"),
            avg_first_toxic_sec=("first_toxic_sec", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_elite_ratio=("elite_ratio", "mean"),
            avg_compatible_ratio=("compatible_ratio", "mean"),
        )
        .reset_index()
        .sort_values(["avg_final_pnl", "final_winrate"], ascending=[False, False])
    )

    detail_csv = out_dir / f"structure_overlay_warning_detail_{args.label}.csv"
    summary_csv = out_dir / f"structure_overlay_warning_summary_{args.label}.csv"

    out.to_csv(detail_csv, index=False)
    summary.to_csv(summary_csv, index=False)

    print("STRUCTURE OVERLAY WARNING POWER COMPLETE")
    print(f"trades: {len(out)}")
    print(f"detail_csv: {detail_csv}")
    print(f"summary_csv: {summary_csv}")
    print()

    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
