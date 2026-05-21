#!/usr/bin/env python3
# ASCII-only.
# Research-only recovery trigger detection.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument(
        "--momentum-csv",
        default="reports/trade_lifecycle/health_momentum_detail_STEP9A_FULL_43M.csv",
    )

    p.add_argument(
        "--out-dir",
        default="reports/trade_lifecycle",
    )

    p.add_argument(
        "--label",
        default="recovery_triggers",
    )

    return p.parse_args()


def main() -> int:

    args = parse_args()

    in_path = Path(args.momentum_csv)
    out_dir = Path(args.out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing momentum csv: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "trade_id",
        "side",
        "duration_sec",
        "market_regime",
        "current_score",
        "health_score",
        "health_delta",
        "momentum_bucket",
        "pnl_delta",
        "current_pnl",
        "future_best_delta",
        "future_worst_delta",
        "final_trade_pnl",
    }

    missing = sorted(required - set(df.columns))

    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    # Real recoveries.
    # Strong future upside + positive final outcome.
    x = df[
        (df["future_best_delta"] >= 100)
        & (df["final_trade_pnl"] > 0)
    ].copy()

    if x.empty:
        raise SystemExit("ERROR: no recovery candidates found")

    x = x.sort_values(["trade_id", "duration_sec"]).reset_index(drop=True)

    rows = []

    for trade_id, g in x.groupby("trade_id", dropna=False):

        g = g.sort_values("duration_sec").reset_index(drop=True)

        for i in range(len(g)):

            cur = g.iloc[i]

            prev1 = g.iloc[i - 1] if i >= 1 else None
            prev2 = g.iloc[i - 2] if i >= 2 else None

            regime_flip = 0
            score_flip = 0
            momentum_reversal = 0
            health_reversal = 0
            pnl_stabilization = 0

            if prev1 is not None:

                if prev1["market_regime"] != cur["market_regime"]:
                    regime_flip = 1

                if (
                    int(prev1["current_score"]) < 0
                    and int(cur["current_score"]) >= 0
                ) or (
                    int(prev1["current_score"]) > 0
                    and int(cur["current_score"]) <= 0
                ):
                    score_flip = 1

                if (
                    float(prev1["health_delta"]) < 0
                    and float(cur["health_delta"]) > 0
                ):
                    momentum_reversal = 1

                if (
                    float(prev1["health_score"]) < -50
                    and float(cur["health_score"]) > float(prev1["health_score"])
                ):
                    health_reversal = 1

                if (
                    float(prev1["pnl_delta"]) < 0
                    and float(cur["pnl_delta"]) > float(prev1["pnl_delta"])
                ):
                    pnl_stabilization = 1

            persistence_break = 0

            if prev1 is not None and prev2 is not None:

                if (
                    prev2["market_regime"] == prev1["market_regime"]
                    and prev1["market_regime"] != cur["market_regime"]
                ):
                    persistence_break = 1

            rows.append(
                {
                    "trade_id": trade_id,
                    "side": str(cur["side"]),
                    "duration_sec": float(cur["duration_sec"]),
                    "market_regime": str(cur["market_regime"]),
                    "current_score": int(cur["current_score"]),
                    "health_score": float(cur["health_score"]),
                    "health_delta": float(cur["health_delta"]),
                    "pnl_delta": float(cur["pnl_delta"]),
                    "current_pnl": float(cur["current_pnl"]),
                    "future_best_delta": float(cur["future_best_delta"]),
                    "future_worst_delta": float(cur["future_worst_delta"]),
                    "final_trade_pnl": float(cur["final_trade_pnl"]),
                    "regime_flip": regime_flip,
                    "score_flip": score_flip,
                    "momentum_reversal": momentum_reversal,
                    "health_reversal": health_reversal,
                    "pnl_stabilization": pnl_stabilization,
                    "persistence_break": persistence_break,
                }
            )

    out = pd.DataFrame(rows)

    trigger_cols = [
        "regime_flip",
        "score_flip",
        "momentum_reversal",
        "health_reversal",
        "pnl_stabilization",
        "persistence_break",
    ]

    summary_rows = []

    for side in sorted(out["side"].unique()):

        s = out[out["side"] == side]

        for col in trigger_cols:

            active = s[s[col] == 1]

            if len(active) == 0:
                continue

            summary_rows.append(
                {
                    "side": side,
                    "trigger": col,
                    "rows": len(active),
                    "unique_trades": active["trade_id"].nunique(),
                    "avg_health": active["health_score"].mean(),
                    "avg_health_delta": active["health_delta"].mean(),
                    "avg_pnl_delta": active["pnl_delta"].mean(),
                    "avg_future_best": active["future_best_delta"].mean(),
                    "avg_future_worst": active["future_worst_delta"].mean(),
                    "avg_final_pnl": active["final_trade_pnl"].mean(),
                }
            )

    summary = (
        pd.DataFrame(summary_rows)
        .sort_values(["side", "avg_final_pnl"], ascending=[True, False])
    )

    out_detail = out_dir / f"recovery_trigger_detail_{args.label}.csv"
    out_summary = out_dir / f"recovery_trigger_summary_{args.label}.csv"

    out.to_csv(out_detail, index=False)
    summary.to_csv(out_summary, index=False)

    print("RECOVERY TRIGGER ANALYSIS COMPLETE")
    print(f"rows: {len(out)}")
    print(f"unique_trades: {out['trade_id'].nunique()}")
    print(f"detail_csv: {out_detail}")
    print(f"summary_csv: {out_summary}")
    print()

    print("BEST RECOVERY TRIGGERS")
    print(
        summary.sort_values("avg_final_pnl", ascending=False)
        .to_string(index=False)
    )
    print()

    print("MOST COMMON RECOVERY TRIGGERS")
    print(
        summary.sort_values("rows", ascending=False)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
