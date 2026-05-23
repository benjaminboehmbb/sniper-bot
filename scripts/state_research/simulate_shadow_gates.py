#!/usr/bin/env python3
# ASCII-only.
# STEP12 passive shadow gate simulation.
# Research-only. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--factor-detail", required=True)
    p.add_argument("--out-dir", default="reports/passive_shadow_risk")
    p.add_argument("--label", default="STEP12_shadow_gate_sim")
    p.add_argument("--start-capital", type=float, default=10000.0)
    return p.parse_args()


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
    gross_win = sum(x for x in pnls if x > 0)
    gross_loss = abs(sum(x for x in pnls if x < 0))
    if gross_loss == 0:
        return float("inf") if gross_win > 0 else 0.0
    return gross_win / gross_loss


def metrics(df: pd.DataFrame, start_capital: float) -> dict:
    pnls = list(df["pnl"].astype(float))

    total_pnl = sum(pnls)
    trades = len(pnls)
    wins = sum(1 for x in pnls if x > 0)

    return {
        "trades": trades,
        "total_pnl": total_pnl,
        "return_pct": total_pnl / start_capital,
        "winrate": wins / trades if trades else 0.0,
        "profit_factor": profit_factor(pnls),
        "max_drawdown_pct": max_drawdown_pct(pnls, start_capital),
        "avg_pnl": total_pnl / trades if trades else 0.0,
    }


def simulate_gate(df: pd.DataFrame, name: str, mask: pd.Series, start_capital: float) -> dict:
    removed = df[mask].copy()
    kept = df[~mask].copy()

    base = metrics(df, start_capital)
    sim = metrics(kept, start_capital)

    removed_pnl = float(removed["pnl"].sum()) if len(removed) else 0.0
    removed_losses = int((removed["pnl"] < 0).sum()) if len(removed) else 0
    removed_wins = int((removed["pnl"] > 0).sum()) if len(removed) else 0

    return {
        "gate_name": name,
        "base_trades": base["trades"],
        "kept_trades": sim["trades"],
        "removed_trades": len(removed),
        "removed_wins": removed_wins,
        "removed_losses": removed_losses,
        "removed_total_pnl": removed_pnl,
        "base_total_pnl": base["total_pnl"],
        "sim_total_pnl": sim["total_pnl"],
        "delta_total_pnl": sim["total_pnl"] - base["total_pnl"],
        "base_return_pct": base["return_pct"],
        "sim_return_pct": sim["return_pct"],
        "base_winrate": base["winrate"],
        "sim_winrate": sim["winrate"],
        "base_profit_factor": base["profit_factor"],
        "sim_profit_factor": sim["profit_factor"],
        "base_max_drawdown_pct": base["max_drawdown_pct"],
        "sim_max_drawdown_pct": sim["max_drawdown_pct"],
        "base_avg_pnl": base["avg_pnl"],
        "sim_avg_pnl": sim["avg_pnl"],
    }


def main() -> int:
    args = parse_args()

    in_path = Path(args.factor_detail)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise SystemExit(f"ERROR: missing factor detail: {in_path}")

    df = pd.read_csv(in_path)

    required = {
        "entry_timestamp_utc",
        "side",
        "pnl",
        "compatibility_adjusted_risk",
        "persistent_toxicity_class",
        "recovery_transition_class",
        "failed_recovery_flag",
        "persistent_toxic_flag",
        "structural_toxic_flag",
        "structural_warning_flag",
        "compatible_flag",
    }

    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"ERROR: missing columns: {missing}")

    df = df.copy()
    df["pnl"] = df["pnl"].astype(float)

    gate_defs = [
        (
            "block_failed_recovery",
            df["failed_recovery_flag"].astype(int) == 1,
        ),
        (
            "block_persistent_toxic",
            df["persistent_toxic_flag"].astype(int) == 1,
        ),
        (
            "block_structural_toxic_or_warning",
            (df["structural_toxic_flag"].astype(int) == 1)
            | (df["structural_warning_flag"].astype(int) == 1),
        ),
        (
            "block_extreme_persistent_toxicity",
            df["persistent_toxicity_class"].astype(str).eq("EXTREME_PERSISTENT_TOXICITY"),
        ),
        (
            "block_high_or_extreme_persistent_toxicity",
            df["persistent_toxicity_class"]
            .astype(str)
            .isin(["HIGH_PERSISTENT_TOXICITY", "EXTREME_PERSISTENT_TOXICITY"]),
        ),
        (
            "keep_only_compatible",
            df["compatible_flag"].astype(int) == 0,
        ),
        (
            "block_failed_recovery_or_persistent_toxic",
            (df["failed_recovery_flag"].astype(int) == 1)
            | (df["persistent_toxic_flag"].astype(int) == 1),
        ),
    ]

    rows = []

    for name, mask in gate_defs:
        rows.append(
            simulate_gate(
                df=df,
                name=name,
                mask=mask,
                start_capital=args.start_capital,
            )
        )

    summary = pd.DataFrame(rows)

    out_csv = out_dir / f"shadow_gate_simulation_{args.label}.csv"
    summary.to_csv(out_csv, index=False)

    print("OK: STEP12 passive shadow gate simulation written")
    print(f"summary: {out_csv}")
    print("")
    print("GATE SIMULATION SUMMARY")
    print(summary.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
