#!/usr/bin/env python3
# ASCII-only.
# Build regime-direction compatibility matrix.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--transition-summary",
        default="reports/trade_lifecycle/regime_transition_summary_STEP9A_FULL_43M.csv",
    )
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")
    return p.parse_args()


def compatibility_class(pnl, winrate):
    if pnl >= 25 and winrate >= 0.70:
        return "HIGHLY_COMPATIBLE"

    if pnl >= 0 and winrate >= 0.55:
        return "COMPATIBLE"

    if pnl <= -50 and winrate <= 0.30:
        return "HIGHLY_TOXIC"

    if pnl < 0:
        return "TOXIC"

    return "MIXED"


def main():
    args = parse_args()

    in_path = Path(args.transition_summary)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    required = {
        "side",
        "transition_type",
        "avg_final_pnl",
        "final_winrate",
        "avg_health_delta",
        "avg_pnl_delta",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["compatibility_class"] = df.apply(
        lambda r: compatibility_class(
            float(r["avg_final_pnl"]),
            float(r["final_winrate"]),
        ),
        axis=1,
    )

    df["structural_score"] = (
        df["avg_final_pnl"] * 0.5
        + df["final_winrate"] * 100.0
        + df["avg_health_delta"] * 0.2
        + df["avg_pnl_delta"] * 0.2
    )

    df = df.sort_values(
        ["structural_score"],
        ascending=False,
    )

    out_csv = out_dir / f"regime_compatibility_matrix_{args.label}.csv"

    df.to_csv(out_csv, index=False)

    print("REGIME COMPATIBILITY MATRIX COMPLETE")
    print(f"rows: {len(df)}")
    print(f"csv_out: {out_csv}")
    print()

    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
