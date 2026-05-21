#!/usr/bin/env python3
# ASCII-only.
# Build structural stability hierarchy of market state-space.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--compatibility",
        default="reports/trade_lifecycle/regime_compatibility_matrix_STEP9A_FULL_43M.csv",
    )
    p.add_argument(
        "--mobility",
        default="reports/trade_lifecycle/regime_mobility_summary_STEP9A_FULL_43M.csv",
    )
    p.add_argument(
        "--timing",
        default="reports/trade_lifecycle/transition_timing_summary_STEP9A_FULL_43M.csv",
    )
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")
    return p.parse_args()


def classify(score):
    if score >= 80:
        return "ELITE_STRUCTURE"

    if score >= 40:
        return "STRONG_STRUCTURE"

    if score >= 0:
        return "NEUTRAL_STRUCTURE"

    if score >= -40:
        return "WEAK_STRUCTURE"

    return "COLLAPSE_STRUCTURE"


def main():
    args = parse_args()

    comp = pd.read_csv(args.compatibility)
    mob = pd.read_csv(args.mobility)
    timing = pd.read_csv(args.timing)

    rows = []

    # Compatibility contribution
    for _, r in comp.iterrows():
        score = (
            float(r["avg_final_pnl"]) * 0.5
            + float(r["final_winrate"]) * 100.0
            + float(r["avg_health_delta"]) * 0.2
        )

        rows.append(
            {
                "source": "compatibility",
                "structure": f'{r["side"]}|{r["transition_type"]}',
                "score": score,
            }
        )

    # Mobility contribution
    for _, r in mob.iterrows():
        score = (
            float(r["avg_final_pnl"]) * 0.5
            + float(r["final_winrate"]) * 100.0
            + float(r["avg_transition_ratio"]) * 20.0
        )

        rows.append(
            {
                "source": "mobility",
                "structure": (
                    f'{r["side"]}|'
                    f'{r["dominant_regime"]}|'
                    f'{r["mobility_class"]}'
                ),
                "score": score,
            }
        )

    # Timing contribution
    for _, r in timing.iterrows():
        score = (
            float(r["avg_final_pnl"]) * 0.5
            + float(r["final_winrate"]) * 100.0
            + float(r["avg_health_delta"]) * 0.2
        )

        rows.append(
            {
                "source": "timing",
                "structure": (
                    f'{r["side"]}|'
                    f'{r["transition_type"]}|'
                    f'{r["timing_bucket"]}'
                ),
                "score": score,
            }
        )

    out = pd.DataFrame(rows)

    summary = (
        out.groupby("structure", dropna=False)
        .agg(
            appearances=("source", "count"),
            avg_score=("score", "mean"),
            max_score=("score", "max"),
            min_score=("score", "min"),
        )
        .reset_index()
    )

    summary["stability_class"] = (
        summary["avg_score"]
        .apply(classify)
    )

    summary = summary.sort_values(
        ["avg_score", "appearances"],
        ascending=[False, False],
    )

    out_csv = (
        Path(args.out_dir) /
        f"structural_stability_ranking_{args.label}.csv"
    )

    summary.to_csv(out_csv, index=False)

    print("STRUCTURAL STABILITY RANKING COMPLETE")
    print(f"structures: {len(summary)}")
    print(f"csv_out: {out_csv}")
    print()

    print("TOP STRUCTURES")
    print(summary.head(30).to_string(index=False))
    print()

    print("BOTTOM STRUCTURES")
    print(
        summary.sort_values(
            ["avg_score", "appearances"],
            ascending=[True, False],
        )
        .head(30)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
