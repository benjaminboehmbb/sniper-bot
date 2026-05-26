from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


WINDOW = 3


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def rolling_ratio(values: list[str], target: str, end_idx: int) -> float:
    start = max(0, end_idx - WINDOW + 1)

    sub = values[start : end_idx + 1]

    if not sub:
        return 0.0

    return sub.count(target) / len(sub)


def analyze_trade(group: pd.DataFrame) -> dict:

    group = group.sort_values("tick_id").reset_index(drop=True)

    states = group["shadow_risk_name"].tolist()

    safe_ratios = []
    warning_ratios = []
    toxic_ratios = []

    for idx in range(len(states)):

        safe_ratios.append(
            rolling_ratio(states, "SAFE", idx)
        )

        warning_ratios.append(
            rolling_ratio(states, "WARNING", idx)
        )

        toxic_ratios.append(
            rolling_ratio(states, "TOXIC", idx)
        )

    safe_acceleration = []
    warning_acceleration = []
    toxic_acceleration = []

    for idx in range(1, len(states)):

        safe_acceleration.append(
            safe_ratios[idx] - safe_ratios[idx - 1]
        )

        warning_acceleration.append(
            warning_ratios[idx] - warning_ratios[idx - 1]
        )

        toxic_acceleration.append(
            toxic_ratios[idx] - toxic_ratios[idx - 1]
        )

    max_warning_accel = (
        max(warning_acceleration)
        if warning_acceleration
        else 0.0
    )

    max_toxic_accel = (
        max(toxic_acceleration)
        if toxic_acceleration
        else 0.0
    )

    min_safe_accel = (
        min(safe_acceleration)
        if safe_acceleration
        else 0.0
    )

    final_toxic_ratio = (
        states.count("TOXIC") / len(states)
        if states
        else 0.0
    )

    return {
        "entry_timestamp_utc": group.iloc[0]["entry_timestamp_utc"],
        "side": group.iloc[0]["side"],
        "trade_class": (
            group.iloc[0]["persistent_toxicity_class"]
            if "persistent_toxicity_class" in group.columns
            else ""
        ),
        "snapshots": len(states),
        "max_warning_acceleration": max_warning_accel,
        "max_toxic_acceleration": max_toxic_accel,
        "min_safe_acceleration": min_safe_accel,
        "final_toxic_ratio": final_toxic_ratio,
        "pnl": (
            group.iloc[0]["pnl"]
            if "pnl" in group.columns
            else 0.0
        ),
        "final_win": (
            group.iloc[0]["final_win"]
            if "final_win" in group.columns
            else int(group.iloc[0]["pnl"] > 0)
        ),
    }


def main() -> None:

    parser = argparse.ArgumentParser()

    parser.add_argument("--shadow-csv", required=True)
    parser.add_argument("--persistence-detail", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)

    args = parser.parse_args()

    shadow_df = safe_read_csv(Path(args.shadow_csv))

    persistence_df = safe_read_csv(
        Path(args.persistence_detail)
    )

    merge_cols = [
        "entry_timestamp_utc",
        "side",
        "persistent_toxicity_class",
        "pnl",
        "final_win",
    ]

    merged = shadow_df.merge(
        persistence_df[merge_cols],
        on=["entry_timestamp_utc", "side"],
        how="left",
    )

    rows = []

    grouped = merged.groupby(
        ["entry_timestamp_utc", "side"]
    )

    for _, group in grouped:
        rows.append(analyze_trade(group))

    detail_df = pd.DataFrame(rows)

    summary_df = (
        detail_df.groupby(
            ["side", "trade_class"],
            dropna=False,
        )
        .agg(
            trades=("pnl", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_max_warning_acceleration=(
                "max_warning_acceleration",
                "mean",
            ),
            avg_max_toxic_acceleration=(
                "max_toxic_acceleration",
                "mean",
            ),
            avg_min_safe_acceleration=(
                "min_safe_acceleration",
                "mean",
            ),
            avg_final_toxic_ratio=(
                "final_toxic_ratio",
                "mean",
            ),
        )
        .reset_index()
    )

    corr_cols = [
        "max_warning_acceleration",
        "max_toxic_acceleration",
        "min_safe_acceleration",
        "final_toxic_ratio",
    ]

    corr_rows = []

    for col in corr_cols:

        corr = detail_df[col].corr(detail_df["pnl"])

        corr_rows.append(
            {
                "factor": col,
                "corr_with_pnl": corr,
            }
        )

    corr_df = pd.DataFrame(corr_rows)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = (
        out_dir
        / f"degradation_acceleration_detail_{args.label}.csv"
    )

    summary_path = (
        out_dir
        / f"degradation_acceleration_summary_{args.label}.csv"
    )

    corr_path = (
        out_dir
        / f"degradation_acceleration_correlations_{args.label}.csv"
    )

    detail_df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)
    corr_df.to_csv(corr_path, index=False)

    print("OK: STEP13F degradation acceleration analysis written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")
    print(f"correlations: {corr_path}")

    print()
    print("DEGRADATION ACCELERATION SUMMARY")
    print(summary_df.to_string(index=False))

    print()
    print("CORRELATIONS WITH PNL")
    print(corr_df.to_string(index=False))


if __name__ == "__main__":
    main()