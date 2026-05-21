#!/usr/bin/env python3
# ASCII-only.
# Build meta-structure importance model.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--ranking",
        default="reports/trade_lifecycle/structural_stability_ranking_STEP9A_FULL_43M.csv",
    )
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="STEP9A_FULL_43M")
    return p.parse_args()


def extract_features(structure: str):
    s = structure.lower()

    return {
        "has_short": int("short" in s),
        "has_long": int("long" in s),
        "has_bear": int("bear" in s),
        "has_bull": int("bull" in s),
        "has_high_mobility": int("high_mobility" in s),
        "has_extreme_mobility": int("extreme_mobility" in s),
        "has_mid": int("|mid" in s),
        "has_late": int("|late" in s),
        "has_early": int("|early" in s),
        "has_stable": int("stable" in s),
        "has_transition": int("_to_" in s),
    }


def main():
    args = parse_args()

    in_path = Path(args.ranking)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(in_path)

    rows = []

    for _, r in df.iterrows():
        structure = str(r["structure"])

        features = extract_features(structure)

        row = {
            "structure": structure,
            "avg_score": float(r["avg_score"]),
            "stability_class": str(r["stability_class"]),
        }

        row.update(features)

        rows.append(row)

    meta = pd.DataFrame(rows)

    feature_scores = []

    feature_cols = [
        c for c in meta.columns
        if c.startswith("has_")
    ]

    for col in feature_cols:
        subset = meta[meta[col] == 1]

        if len(subset) == 0:
            continue

        feature_scores.append(
            {
                "feature": col,
                "structures": len(subset),
                "avg_structure_score": subset["avg_score"].mean(),
                "max_structure_score": subset["avg_score"].max(),
                "min_structure_score": subset["avg_score"].min(),
            }
        )

    feature_df = pd.DataFrame(feature_scores)

    feature_df = feature_df.sort_values(
        ["avg_structure_score"],
        ascending=False,
    )

    out_csv = (
        out_dir /
        f"meta_structure_feature_importance_{args.label}.csv"
    )

    feature_df.to_csv(out_csv, index=False)

    print("META STRUCTURE MODEL COMPLETE")
    print(f"features: {len(feature_df)}")
    print(f"csv_out: {out_csv}")
    print()

    print(feature_df.to_string(index=False))


if __name__ == "__main__":
    main()
