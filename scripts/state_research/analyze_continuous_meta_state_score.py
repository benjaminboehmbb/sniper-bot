from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def calc_score(row: pd.Series) -> float:
    safe = float(row["safe_ratio"])
    warning = float(row["warning_ratio"])
    toxic = float(row["toxic_ratio"])
    toxic_accel = float(row["max_toxic_acceleration"])

    score = (
        1.25 * safe
        + 0.60 * warning
        - 1.75 * toxic
        - 1.25 * toxic_accel
    )

    return clamp(score, -1.0, 1.0)


def score_bucket(score: float) -> str:
    if score >= 0.60:
        return "STRONG_POSITIVE"
    if score >= 0.20:
        return "POSITIVE"
    if score > -0.20:
        return "NEUTRAL"
    if score > -0.60:
        return "NEGATIVE"
    return "STRONG_NEGATIVE"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--recovery-detail", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)

    args = parser.parse_args()

    df = safe_read_csv(Path(args.recovery_detail))

    required = {
        "entry_timestamp_utc",
        "side",
        "pnl",
        "final_win",
        "safe_ratio",
        "warning_ratio",
        "toxic_ratio",
        "max_toxic_acceleration",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["continuous_meta_state_score"] = df.apply(calc_score, axis=1)
    df["continuous_meta_state_bucket"] = df["continuous_meta_state_score"].apply(score_bucket)

    summary_df = (
        df.groupby(["side", "continuous_meta_state_bucket"], dropna=False)
        .agg(
            trades=("pnl", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_score=("continuous_meta_state_score", "mean"),
            avg_safe_ratio=("safe_ratio", "mean"),
            avg_warning_ratio=("warning_ratio", "mean"),
            avg_toxic_ratio=("toxic_ratio", "mean"),
            avg_max_toxic_acceleration=("max_toxic_acceleration", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_score"])
    )

    corr_df = pd.DataFrame(
        [
            {
                "metric": "continuous_meta_state_score_vs_pnl",
                "correlation": df["continuous_meta_state_score"].corr(df["pnl"]),
            },
            {
                "metric": "continuous_meta_state_score_vs_win",
                "correlation": df["continuous_meta_state_score"].corr(df["final_win"]),
            },
        ]
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = out_dir / f"continuous_meta_state_score_detail_{args.label}.csv"
    summary_path = out_dir / f"continuous_meta_state_score_summary_{args.label}.csv"
    corr_path = out_dir / f"continuous_meta_state_score_correlations_{args.label}.csv"

    df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    corr_df.to_csv(corr_path, index=False)

    print("OK: STEP14C continuous meta-state score analysis written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")
    print(f"correlations: {corr_path}")

    print()
    print("CONTINUOUS META STATE SCORE SUMMARY")
    print(summary_df.to_string(index=False))

    print()
    print("CONTINUOUS META STATE CORRELATIONS")
    print(corr_df.to_string(index=False))


if __name__ == "__main__":
    main()
