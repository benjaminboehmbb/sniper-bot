from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SIZING_MAP = {
    "STRONG_POSITIVE": 1.00,
    "POSITIVE": 0.75,
    "NEUTRAL": 0.50,
    "NEGATIVE": 0.25,
    "STRONG_NEGATIVE": 0.00,
}


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def max_drawdown_pct(pnls: list[float], start_capital: float) -> float:
    equity = start_capital
    peak = start_capital
    max_dd = 0.0

    for pnl in pnls:
        equity += float(pnl)
        peak = max(peak, equity)

        dd = (peak - equity) / peak if peak > 0 else 0.0
        max_dd = max(max_dd, dd)

    return max_dd


def profit_factor(pnls: list[float]) -> float:
    wins = sum(x for x in pnls if x > 0)
    losses = abs(sum(x for x in pnls if x < 0))

    if losses == 0:
        return float("inf") if wins > 0 else 0.0

    return wins / losses


def classify_bucket(score: float) -> str:
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

    parser.add_argument("--snapshot-detail", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--start-capital", type=float, default=10000)

    args = parser.parse_args()

    df = safe_read_csv(Path(args.snapshot_detail))

    required = {
        "entry_timestamp_utc",
        "side",
        "pnl",
        "early_avg_score",
        "final_win",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df["bucket"] = df["early_avg_score"].apply(classify_bucket)

    df["position_multiplier"] = (
        df["bucket"]
        .map(SIZING_MAP)
        .astype(float)
    )

    df["scaled_pnl"] = (
        df["pnl"]
        * df["position_multiplier"]
    )

    base_pnls = df["pnl"].tolist()
    scaled_pnls = df["scaled_pnl"].tolist()

    summary_df = pd.DataFrame(
        [
            {
                "simulation": "adaptive_position_sizing",

                "base_total_pnl": sum(base_pnls),
                "scaled_total_pnl": sum(scaled_pnls),

                "delta_total_pnl": (
                    sum(scaled_pnls)
                    - sum(base_pnls)
                ),

                "base_return_pct": (
                    sum(base_pnls)
                    / args.start_capital
                ),

                "scaled_return_pct": (
                    sum(scaled_pnls)
                    / args.start_capital
                ),

                "base_winrate": (
                    (df["pnl"] > 0).mean()
                ),

                "scaled_winrate": (
                    (df["scaled_pnl"] > 0).mean()
                ),

                "base_profit_factor": (
                    profit_factor(base_pnls)
                ),

                "scaled_profit_factor": (
                    profit_factor(scaled_pnls)
                ),

                "base_max_drawdown_pct": (
                    max_drawdown_pct(
                        base_pnls,
                        args.start_capital,
                    )
                ),

                "scaled_max_drawdown_pct": (
                    max_drawdown_pct(
                        scaled_pnls,
                        args.start_capital,
                    )
                ),

                "base_avg_pnl": (
                    sum(base_pnls)
                    / len(base_pnls)
                ),

                "scaled_avg_pnl": (
                    sum(scaled_pnls)
                    / len(scaled_pnls)
                ),
            }
        ]
    )

    bucket_df = (
        df.groupby(
            ["side", "bucket"],
            dropna=False,
        )
        .agg(
            trades=("pnl", "count"),
            base_total_pnl=("pnl", "sum"),
            scaled_total_pnl=("scaled_pnl", "sum"),
            avg_multiplier=("position_multiplier", "mean"),
            avg_pnl=("pnl", "mean"),
            scaled_avg_pnl=("scaled_pnl", "mean"),
            winrate=("final_win", "mean"),
        )
        .reset_index()
        .sort_values(
            ["side", "avg_multiplier"]
        )
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = (
        out_dir
        / f"adaptive_position_sizing_summary_{args.label}.csv"
    )

    bucket_path = (
        out_dir
        / f"adaptive_position_sizing_buckets_{args.label}.csv"
    )

    summary_df.to_csv(summary_path, index=False)
    bucket_df.to_csv(bucket_path, index=False)

    print("OK: STEP15 adaptive sizing simulation written")
    print(f"summary: {summary_path}")
    print(f"buckets: {bucket_path}")

    print()
    print("ADAPTIVE POSITION SIZING SUMMARY")
    print(summary_df.to_string(index=False))

    print()
    print("ADAPTIVE POSITION SIZING BUCKETS")
    print(bucket_df.to_string(index=False))


if __name__ == "__main__":
    main()
