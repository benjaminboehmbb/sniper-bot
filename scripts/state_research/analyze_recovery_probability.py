from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


WINDOW = 5


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


def classify_recovery_probability(
    safe_ratio: float,
    warning_ratio: float,
    toxic_ratio: float,
    toxic_accel: float,
) -> str:

    if toxic_ratio >= 0.6 and toxic_accel >= 0.25:
        return "HIGH_COLLAPSE_RISK"

    if toxic_ratio >= 0.4 and toxic_accel >= 0.15:
        return "ELEVATED_COLLAPSE_RISK"

    if safe_ratio >= 0.6 and toxic_ratio <= 0.1:
        return "HIGH_RECOVERY_PROBABILITY"

    if warning_ratio >= 0.4 and toxic_ratio <= 0.2:
        return "RECOVERABLE_INSTABILITY"

    return "UNCERTAIN_TRANSITION"


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

    toxic_acceleration = []

    for idx in range(1, len(toxic_ratios)):

        toxic_acceleration.append(
            toxic_ratios[idx]
            - toxic_ratios[idx - 1]
        )

    max_toxic_accel = (
        max(toxic_acceleration)
        if toxic_acceleration
        else 0.0
    )

    final_safe_ratio = (
        states.count("SAFE") / len(states)
        if states
        else 0.0
    )

    final_warning_ratio = (
        states.count("WARNING") / len(states)
        if states
        else 0.0
    )

    final_toxic_ratio = (
        states.count("TOXIC") / len(states)
        if states
        else 0.0
    )

    recovery_class = classify_recovery_probability(
        safe_ratio=final_safe_ratio,
        warning_ratio=final_warning_ratio,
        toxic_ratio=final_toxic_ratio,
        toxic_accel=max_toxic_accel,
    )

    return {
        "entry_timestamp_utc": group.iloc[0]["entry_timestamp_utc"],
        "side": group.iloc[0]["side"],
        "recovery_probability_class": recovery_class,
        "max_toxic_acceleration": max_toxic_accel,
        "safe_ratio": final_safe_ratio,
        "warning_ratio": final_warning_ratio,
        "toxic_ratio": final_toxic_ratio,
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

    persistence_df = safe_read_csv(
        Path(args.persistence_detail)
    )

    merge_cols = [
        "entry_timestamp_utc",
        "side",
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
            ["side", "recovery_probability_class"],
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
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = (
        out_dir
        / f"recovery_probability_detail_{args.label}.csv"
    )

    summary_path = (
        out_dir
        / f"recovery_probability_summary_{args.label}.csv"
    )

    detail_df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print("OK: STEP14 recovery probability analysis written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")

    print()
    print("RECOVERY PROBABILITY SUMMARY")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()