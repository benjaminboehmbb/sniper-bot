from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


WINDOW = 5


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def rolling_ratio(values: list[str], target: str, end_idx: int) -> float:
    start = max(0, end_idx - WINDOW + 1)
    sub = values[start : end_idx + 1]
    if not sub:
        return 0.0
    return sub.count(target) / len(sub)


def calc_snapshot_score(
    safe_ratio: float,
    warning_ratio: float,
    toxic_ratio: float,
    toxic_accel: float,
) -> float:
    score = (
        1.25 * safe_ratio
        + 0.60 * warning_ratio
        - 1.75 * toxic_ratio
        - 1.25 * toxic_accel
    )
    return clamp(score, -1.0, 1.0)


def analyze_trade(group: pd.DataFrame) -> dict:
    group = group.sort_values("tick_id").reset_index(drop=True)
    states = group["shadow_risk_name"].astype(str).tolist()

    scores = []
    toxic_ratios = []

    prev_toxic_ratio = 0.0

    for idx in range(len(states)):
        safe_ratio = rolling_ratio(states, "SAFE", idx)
        warning_ratio = rolling_ratio(states, "WARNING", idx)
        toxic_ratio = rolling_ratio(states, "TOXIC", idx)
        toxic_accel = toxic_ratio - prev_toxic_ratio if idx > 0 else 0.0

        score = calc_snapshot_score(
            safe_ratio=safe_ratio,
            warning_ratio=warning_ratio,
            toxic_ratio=toxic_ratio,
            toxic_accel=toxic_accel,
        )

        scores.append(score)
        toxic_ratios.append(toxic_ratio)
        prev_toxic_ratio = toxic_ratio

    n = len(scores)

    first_third_end = max(1, n // 3)
    first_half_end = max(1, n // 2)

    early_scores = scores[:first_third_end]
    half_scores = scores[:first_half_end]

    return {
        "entry_timestamp_utc": group.iloc[0]["entry_timestamp_utc"],
        "side": group.iloc[0]["side"],
        "snapshots": n,
        "avg_snapshot_score": sum(scores) / n if n else 0.0,
        "min_snapshot_score": min(scores) if scores else 0.0,
        "max_snapshot_score": max(scores) if scores else 0.0,
        "early_avg_score": sum(early_scores) / len(early_scores) if early_scores else 0.0,
        "early_min_score": min(early_scores) if early_scores else 0.0,
        "half_avg_score": sum(half_scores) / len(half_scores) if half_scores else 0.0,
        "half_min_score": min(half_scores) if half_scores else 0.0,
        "final_score": scores[-1] if scores else 0.0,
        "max_toxic_ratio_seen": max(toxic_ratios) if toxic_ratios else 0.0,
        "pnl": group.iloc[0]["pnl"],
        "final_win": group.iloc[0]["final_win"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--shadow-csv", required=True)
    parser.add_argument("--persistence-detail", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)

    args = parser.parse_args()

    shadow_df = safe_read_csv(Path(args.shadow_csv))
    persistence_df = safe_read_csv(Path(args.persistence_detail))

    required_shadow = {
        "entry_timestamp_utc",
        "side",
        "tick_id",
        "shadow_risk_name",
    }

    required_persistence = {
        "entry_timestamp_utc",
        "side",
        "pnl",
        "final_win",
    }

    missing_shadow = sorted(required_shadow - set(shadow_df.columns))
    missing_persistence = sorted(required_persistence - set(persistence_df.columns))

    if missing_shadow:
        raise SystemExit(f"ERROR: missing shadow columns: {missing_shadow}")

    if missing_persistence:
        raise SystemExit(f"ERROR: missing persistence columns: {missing_persistence}")

    shadow_df["entry_timestamp_utc"] = shadow_df["entry_timestamp_utc"].astype(str)
    persistence_df["entry_timestamp_utc"] = persistence_df["entry_timestamp_utc"].astype(str)

    merged = shadow_df.merge(
        persistence_df[
            [
                "entry_timestamp_utc",
                "side",
                "pnl",
                "final_win",
            ]
        ],
        on=["entry_timestamp_utc", "side"],
        how="left",
    )

    rows = []

    for _, group in merged.groupby(["entry_timestamp_utc", "side"]):
        rows.append(analyze_trade(group))

    detail_df = pd.DataFrame(rows)

    score_cols = [
        "avg_snapshot_score",
        "min_snapshot_score",
        "early_avg_score",
        "early_min_score",
        "half_avg_score",
        "half_min_score",
        "final_score",
        "max_toxic_ratio_seen",
    ]

    corr_rows = []

    for col in score_cols:
        corr_rows.append(
            {
                "factor": col,
                "corr_with_pnl": detail_df[col].corr(detail_df["pnl"]),
                "corr_with_win": detail_df[col].corr(detail_df["final_win"]),
            }
        )

    corr_df = pd.DataFrame(corr_rows)

    def bucket_score(v: float) -> str:
        if v >= 0.60:
            return "STRONG_POSITIVE"
        if v >= 0.20:
            return "POSITIVE"
        if v > -0.20:
            return "NEUTRAL"
        if v > -0.60:
            return "NEGATIVE"
        return "STRONG_NEGATIVE"

    detail_df["early_score_bucket"] = detail_df["early_avg_score"].apply(bucket_score)

    summary_df = (
        detail_df.groupby(["side", "early_score_bucket"], dropna=False)
        .agg(
            trades=("pnl", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_early_score=("early_avg_score", "mean"),
            avg_half_score=("half_avg_score", "mean"),
            avg_full_score=("avg_snapshot_score", "mean"),
            avg_min_score=("min_snapshot_score", "mean"),
            avg_max_toxic_ratio_seen=("max_toxic_ratio_seen", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_early_score"])
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = out_dir / f"snapshot_meta_state_score_detail_{args.label}.csv"
    summary_path = out_dir / f"snapshot_meta_state_score_summary_{args.label}.csv"
    corr_path = out_dir / f"snapshot_meta_state_score_correlations_{args.label}.csv"

    detail_df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    corr_df.to_csv(corr_path, index=False)

    print("OK: STEP14D snapshot meta-state score analysis written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")
    print(f"correlations: {corr_path}")

    print()
    print("SNAPSHOT META STATE SCORE SUMMARY")
    print(summary_df.to_string(index=False))

    print()
    print("SNAPSHOT META STATE SCORE CORRELATIONS")
    print(corr_df.to_string(index=False))


if __name__ == "__main__":
    main()
