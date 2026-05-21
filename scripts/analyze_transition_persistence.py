#!/usr/bin/env python3
# ASCII-only.
# Research-only persistence-chain analysis for lifecycle snapshots.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--lifecycle-csv", default="live_logs/trade_lifecycle_snapshots.csv")
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="transition_persistence")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    in_path = Path(args.lifecycle_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: lifecycle csv not found: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "entry_timestamp_utc",
        "side",
        "duration_sec",
        "unrealized_pnl",
        "market_regime",
        "current_score",
        "atr_quality",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df = df.copy()
    df["trade_id"] = df["entry_timestamp_utc"]

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):
        g = g.sort_values("duration_sec").reset_index(drop=True)

        if len(g) < 2:
            continue

        side = str(g.iloc[0]["side"])

        regimes = list(g["market_regime"].astype(str))
        pnls = list(g["unrealized_pnl"].astype(float))
        scores = list(g["current_score"].astype(int))
        durations = list(g["duration_sec"].astype(float))

        for i in range(len(g)):
            for chain_len in [2, 3, 4]:
                j = i + chain_len
                if j > len(g):
                    continue

                chain = regimes[i:j]
                chain_name = "->".join(chain)

                start_pnl = pnls[i]
                end_pnl = pnls[j - 1]
                min_pnl = min(pnls[i:j])
                max_pnl = max(pnls[i:j])

                rows.append(
                    {
                        "trade_id": trade_id,
                        "side": side,
                        "chain_len": chain_len,
                        "chain": chain_name,
                        "start_duration_sec": durations[i],
                        "end_duration_sec": durations[j - 1],
                        "start_pnl": start_pnl,
                        "end_pnl": end_pnl,
                        "pnl_delta": end_pnl - start_pnl,
                        "min_pnl_in_chain": min_pnl,
                        "max_pnl_in_chain": max_pnl,
                        "start_score": scores[i],
                        "end_score": scores[j - 1],
                        "score_delta": scores[j - 1] - scores[i],
                    }
                )

    out = pd.DataFrame(rows)

    if out.empty:
        raise SystemExit("ERROR: no persistence chains found")

    summary = (
        out.groupby(["side", "chain_len", "chain"], dropna=False)
        .agg(
            count=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_pnl_delta=("pnl_delta", "mean"),
            sum_pnl_delta=("pnl_delta", "sum"),
            avg_end_pnl=("end_pnl", "mean"),
            avg_min_pnl=("min_pnl_in_chain", "mean"),
            min_pnl=("min_pnl_in_chain", "min"),
            max_pnl=("max_pnl_in_chain", "max"),
            avg_score_delta=("score_delta", "mean"),
        )
        .reset_index()
        .sort_values(["side", "chain_len", "sum_pnl_delta"])
    )

    detail_path = out_dir / f"transition_persistence_detail_{args.label}.csv"
    summary_path = out_dir / f"transition_persistence_summary_{args.label}.csv"

    out.to_csv(detail_path, index=False)
    summary.to_csv(summary_path, index=False)

    print("TRANSITION PERSISTENCE ANALYSIS COMPLETE")
    print(f"input_rows: {len(df)}")
    print(f"chains: {len(out)}")
    print(f"detail_csv: {detail_path}")
    print(f"summary_csv: {summary_path}")
    print()

    print("WORST CHAINS")
    print(summary.head(30).to_string(index=False))
    print()

    print("BEST CHAINS")
    print(summary.sort_values("sum_pnl_delta", ascending=False).head(30).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
