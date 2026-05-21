#!/usr/bin/env python3
# ASCII-only.
# Research-only trade health scoring model for STEP11A lifecycle data.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--lifecycle-csv", default="live_logs/trade_lifecycle_snapshots.csv")
    p.add_argument("--out-dir", default="reports/trade_lifecycle")
    p.add_argument("--label", default="trade_health")
    return p.parse_args()


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def health_score(
    *,
    side: str,
    pnl: float,
    score: int,
    regime: str,
    atr: str,
    prev_regime: str | None,
    persistence_count: int,
    pnl_delta: float,
) -> float:

    h = 0.0

    # Base pnl contribution.
    h += pnl * 0.25

    # Signal score contribution.
    h += score * 8.0

    # ATR.
    if atr == "bad_atr":
        h -= 10.0
    elif atr == "good_atr":
        h += 5.0

    # Directional regime asymmetry.
    if side == "long":
        if regime == "bull":
            h += 12.0
        elif regime == "bear":
            h -= 18.0

    elif side == "short":
        if regime == "bear":
            h += 12.0
        elif regime == "bull":
            h -= 18.0

    # Persistence escalation.
    if persistence_count >= 2:
        if side == "long" and regime == "bear":
            h -= persistence_count * 15.0

        if side == "short" and regime == "bull":
            h -= persistence_count * 15.0

    # Recovery dynamics.
    h += pnl_delta * 0.40

    # Regime recovery bonus.
    if prev_regime is not None:
        if side == "long":
            if prev_regime == "bear" and regime == "bull":
                h += 25.0
            elif prev_regime == "bull" and regime == "bear":
                h -= 25.0

        elif side == "short":
            if prev_regime == "bull" and regime == "bear":
                h += 25.0
            elif prev_regime == "bear" and regime == "bull":
                h -= 25.0

    return clamp(h, -100.0, 100.0)


def health_state(v: float) -> str:
    if v >= 70:
        return "HEALTHY_STRONG"

    if v >= 35:
        return "HEALTHY"

    if v >= 5:
        return "RECOVERING"

    if v > -25:
        return "NEUTRAL"

    if v > -55:
        return "DEGRADING"

    if v > -80:
        return "COLLAPSING"

    return "TERMINAL"


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
        "timestamp_utc",
        "side",
        "duration_sec",
        "unrealized_pnl",
        "market_regime",
        "atr_quality",
        "current_score",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df = df.copy()

    df["trade_id"] = df["entry_timestamp_utc"]

    rows = []

    for trade_id, g in df.groupby("trade_id", dropna=False):

        g = g.sort_values("duration_sec").reset_index(drop=True)

        prev_regime = None
        persistence_count = 0
        prev_pnl = None

        for _, row in g.iterrows():

            side = str(row["side"])
            regime = str(row["market_regime"]).strip().lower()
            atr = str(row["atr_quality"]).strip().lower()

            pnl = float(row["unrealized_pnl"])
            score = int(row["current_score"])

            if prev_regime == regime:
                persistence_count += 1
            else:
                persistence_count = 1

            if prev_pnl is None:
                pnl_delta = 0.0
            else:
                pnl_delta = pnl - prev_pnl

            h = health_score(
                side=side,
                pnl=pnl,
                score=score,
                regime=regime,
                atr=atr,
                prev_regime=prev_regime,
                persistence_count=persistence_count,
                pnl_delta=pnl_delta,
            )

            rows.append(
                {
                    "trade_id": trade_id,
                    "timestamp_utc": row["timestamp_utc"],
                    "side": side,
                    "duration_sec": float(row["duration_sec"]),
                    "market_regime": regime,
                    "atr_quality": atr,
                    "current_score": score,
                    "unrealized_pnl": pnl,
                    "pnl_delta": pnl_delta,
                    "persistence_count": persistence_count,
                    "trade_health_score": h,
                    "trade_health_state": health_state(h),
                }
            )

            prev_regime = regime
            prev_pnl = pnl

    out = pd.DataFrame(rows)

    summary = (
        out.groupby(["side", "trade_health_state"], dropna=False)
        .agg(
            snapshots=("trade_id", "count"),
            unique_trades=("trade_id", "nunique"),
            avg_health=("trade_health_score", "mean"),
            min_health=("trade_health_score", "min"),
            max_health=("trade_health_score", "max"),
            avg_pnl=("unrealized_pnl", "mean"),
            avg_persistence=("persistence_count", "mean"),
        )
        .reset_index()
        .sort_values(["side", "avg_health"])
    )

    out_detail = out_dir / f"trade_health_detail_{args.label}.csv"
    out_summary = out_dir / f"trade_health_summary_{args.label}.csv"

    out.to_csv(out_detail, index=False)
    summary.to_csv(out_summary, index=False)

    print("TRADE HEALTH MODEL COMPLETE")
    print(f"input_rows: {len(df)}")
    print(f"health_rows: {len(out)}")
    print(f"detail_csv: {out_detail}")
    print(f"summary_csv: {out_summary}")
    print()

    print(summary.to_string(index=False))
    print()

    print("MOST TERMINAL SNAPSHOTS")
    print(
        out.sort_values("trade_health_score")
        .head(30)
        .to_string(index=False)
    )
    print()

    print("MOST HEALTHY SNAPSHOTS")
    print(
        out.sort_values("trade_health_score", ascending=False)
        .head(30)
        .to_string(index=False)
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
