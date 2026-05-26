from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def analyze_trade(group: pd.DataFrame) -> dict:
    group = group.sort_values("tick_id").reset_index(drop=True)

    first_toxic_idx = None

    toxic_rows = group[group["shadow_risk_name"] == "TOXIC"]

    if not toxic_rows.empty:
        first_toxic_idx = int(toxic_rows.index[0])

    pre_toxic = (
        group.iloc[:first_toxic_idx]
        if first_toxic_idx is not None
        else group
    )

    return {
        "entry_timestamp_utc": group.iloc[0]["entry_timestamp_utc"],
        "side": group.iloc[0]["side"],
        "trade_class": group.iloc[0]["trade_class"],
        "snapshots": len(group),
        "first_toxic_snapshot_idx": first_toxic_idx,
        "safe_ratio_before_toxic": (
            (pre_toxic["shadow_risk_name"] == "SAFE").mean()
            if len(pre_toxic) > 0
            else 0.0
        ),
        "warning_ratio_before_toxic": (
            (pre_toxic["shadow_risk_name"] == "WARNING").mean()
            if len(pre_toxic) > 0
            else 0.0
        ),
        "toxic_ratio_total": (
            (group["shadow_risk_name"] == "TOXIC").mean()
        ),
        "avg_score_before_toxic": (
            pre_toxic["score"].mean()
            if "score" in pre_toxic.columns and len(pre_toxic) > 0
            else None
        ),
        "avg_score_total": (
            group["score"].mean()
            if "score" in group.columns
            else None
        ),
        "market_regime_before_toxic": (
            pre_toxic["market_regime"].mode().iloc[0]
            if len(pre_toxic) > 0
            and not pre_toxic["market_regime"].mode().empty
            else ""
        ),
        "atr_before_toxic": (
            pre_toxic["atr_quality"].mode().iloc[0]
            if len(pre_toxic) > 0
            and not pre_toxic["atr_quality"].mode().empty
            else ""
        ),
        "pnl": group.iloc[0]["pnl"],
        "final_win": group.iloc[0]["final_win"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--shadow-csv", required=True)
    parser.add_argument("--transition-detail", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)

    args = parser.parse_args()

    shadow_df = safe_read_csv(Path(args.shadow_csv))

    transition_df = safe_read_csv(Path(args.transition_detail))

    collapse_df = transition_df[
        transition_df["transition_pattern"] == "SAFE_COLLAPSE"
    ].copy()

    merged = shadow_df.merge(
        collapse_df[
            [
                "entry_timestamp_utc",
                "side",
                "trade_class",
                "pnl",
                "final_win",
            ]
        ],
        on=["entry_timestamp_utc", "side"],
        how="inner",
    )

    rows = []

    grouped = merged.groupby(["entry_timestamp_utc", "side"])

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
            avg_first_toxic_snapshot=(
                "first_toxic_snapshot_idx",
                "mean",
            ),
            avg_safe_ratio_before_toxic=(
                "safe_ratio_before_toxic",
                "mean",
            ),
            avg_warning_ratio_before_toxic=(
                "warning_ratio_before_toxic",
                "mean",
            ),
            avg_toxic_ratio_total=(
                "toxic_ratio_total",
                "mean",
            ),
        )
        .reset_index()
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = (
        out_dir
        / f"safe_collapse_detail_{args.label}.csv"
    )

    summary_path = (
        out_dir
        / f"safe_collapse_summary_{args.label}.csv"
    )

    detail_df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print("OK: STEP13B safe collapse analysis written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")

    print()
    print("SAFE COLLAPSE SUMMARY")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()