from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


META_STATE_SCORES = {
    "HIGH_RECOVERY_PROBABILITY": 2,
    "RECOVERABLE_INSTABILITY": 1,
    "UNCERTAIN_TRANSITION": 0,
    "ELEVATED_COLLAPSE_RISK": -1,
    "HIGH_COLLAPSE_RISK": -2,
}


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument("--recovery-detail", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)

    args = parser.parse_args()

    df = safe_read_csv(Path(args.recovery_detail))

    df["meta_state_score"] = (
        df["recovery_probability_class"]
        .map(META_STATE_SCORES)
        .astype(int)
    )

    summary_df = (
        df.groupby(
            ["side", "meta_state_score"],
            dropna=False,
        )
        .agg(
            trades=("pnl", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_safe_ratio=("safe_ratio", "mean"),
            avg_warning_ratio=("warning_ratio", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_max_toxic_acceleration=(
                "max_toxic_acceleration",
                "mean",
            ),
        )
        .reset_index()
        .sort_values(
            ["side", "meta_state_score"]
        )
    )

    correlation_df = pd.DataFrame(
        [
            {
                "metric": "meta_state_score_vs_pnl",
                "correlation": (
                    df["meta_state_score"]
                    .corr(df["pnl"])
                ),
            },
            {
                "metric": "meta_state_score_vs_win",
                "correlation": (
                    df["meta_state_score"]
                    .corr(df["final_win"])
                ),
            },
        ]
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = (
        out_dir
        / f"meta_state_scoring_detail_{args.label}.csv"
    )

    summary_path = (
        out_dir
        / f"meta_state_scoring_summary_{args.label}.csv"
    )

    corr_path = (
        out_dir
        / f"meta_state_scoring_correlations_{args.label}.csv"
    )

    df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    correlation_df.to_csv(corr_path, index=False)

    print("OK: STEP14B meta-state scoring analysis written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")
    print(f"correlations: {corr_path}")

    print()
    print("META STATE SCORE SUMMARY")
    print(summary_df.to_string(index=False))

    print()
    print("META STATE CORRELATIONS")
    print(correlation_df.to_string(index=False))


if __name__ == "__main__":
    main()