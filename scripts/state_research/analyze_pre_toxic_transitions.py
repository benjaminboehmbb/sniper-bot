from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TOXIC_CLASSES = {
    "HIGH_PERSISTENT_TOXICITY",
    "EXTREME_PERSISTENT_TOXICITY",
    "FAILED_RECOVERY",
}


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def classify_transition_pattern(group: pd.DataFrame) -> str:
    states = group["shadow_risk_name"].tolist()

    if len(states) < 3:
        return "INSUFFICIENT_DATA"

    safe_count = states.count("SAFE")
    warning_count = states.count("WARNING")
    toxic_count = states.count("TOXIC")

    if toxic_count == 0:
        return "NO_TOXICITY"

    first_toxic_idx = states.index("TOXIC")

    if first_toxic_idx <= 1:
        return "IMMEDIATE_TOXICITY"

    pre_states = states[:first_toxic_idx]

    if all(s == "WARNING" for s in pre_states):
        return "WARNING_DRIFT"

    if "SAFE" in pre_states and "WARNING" in pre_states:
        return "SAFE_WARNING_TOXIC"

    if pre_states.count("SAFE") >= len(pre_states) * 0.7:
        return "SAFE_COLLAPSE"

    return "MIXED_TRANSITION"


def analyze_trade(group: pd.DataFrame) -> dict:
    group = group.sort_values("tick_id").reset_index(drop=True)
    group["snapshot_idx"] = range(len(group))

    transition_pattern = classify_transition_pattern(group)

    toxic_ratio = (group["shadow_risk_name"] == "TOXIC").mean()
    warning_ratio = (group["shadow_risk_name"] == "WARNING").mean()
    safe_ratio = (group["shadow_risk_name"] == "SAFE").mean()

    first_toxic_idx = None

    toxic_rows = group[group["shadow_risk_name"] == "TOXIC"]

    if not toxic_rows.empty:
        first_toxic_idx = int(toxic_rows.iloc[0]["snapshot_idx"])

    return {
        "entry_timestamp_utc": group.iloc[0]["entry_timestamp_utc"],
        "side": group.iloc[0]["side"],
        "trade_class": group.iloc[0]["persistent_toxicity_class"],
        "transition_pattern": transition_pattern,
        "snapshots": len(group),
        "first_toxic_snapshot_idx": first_toxic_idx,
        "safe_ratio": safe_ratio,
        "warning_ratio": warning_ratio,
        "toxic_ratio": toxic_ratio,
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

    merged = shadow_df.merge(
        persistence_df[
            [
                "entry_timestamp_utc",
                "side",
                "persistent_toxicity_class",
                "pnl",
                "final_win",
            ]
        ],
        on=["entry_timestamp_utc", "side"],
        how="left",
    )

    merged = merged[
        merged["persistent_toxicity_class"].isin(TOXIC_CLASSES)
    ].copy()

    rows = []

    grouped = merged.groupby(["entry_timestamp_utc", "side"])

    for _, group in grouped:
        rows.append(analyze_trade(group))

    detail_df = pd.DataFrame(rows)

    summary_df = (
        detail_df.groupby(
            ["side", "trade_class", "transition_pattern"],
            dropna=False,
        )
        .agg(
            trades=("pnl", "count"),
            total_pnl=("pnl", "sum"),
            avg_pnl=("pnl", "mean"),
            median_pnl=("pnl", "median"),
            winrate=("final_win", "mean"),
            avg_first_toxic_snapshot=(
                "first_toxic_snapshot_idx",
                "mean",
            ),
        )
        .reset_index()
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = (
        out_dir
        / f"pre_toxic_transition_detail_{args.label}.csv"
    )

    summary_path = (
        out_dir
        / f"pre_toxic_transition_summary_{args.label}.csv"
    )

    detail_df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print("OK: STEP13 pre-toxic transition analysis written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")

    print()
    print("PRE-TOXIC TRANSITION SUMMARY")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()