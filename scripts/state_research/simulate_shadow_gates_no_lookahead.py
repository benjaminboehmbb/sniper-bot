#!/usr/bin/env python3
# ASCII-only.
# STEP12B no-lookahead passive shadow gate simulation.
# Research-only. No execution changes.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--shadow-csv", required=True)
    p.add_argument("--trades-jsonl", required=True)
    p.add_argument("--out-dir", default="reports/passive_shadow_risk")
    p.add_argument("--label", default="STEP12B_no_lookahead")
    p.add_argument("--start-capital", type=float, default=10000.0)
    p.add_argument("--persistent-window", type=int, default=5)
    p.add_argument("--failed-recovery-window", type=int, default=8)
    p.add_argument("--min-toxic-ratio", type=float, default=0.50)
    p.add_argument("--min-safe-after-toxic-ratio", type=float, default=0.10)
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
    gross_win = sum(x for x in pnls if x > 0.0)
    gross_loss = abs(sum(x for x in pnls if x < 0.0))
    if gross_loss == 0.0:
        return float("inf") if gross_win > 0.0 else 0.0
    return gross_win / gross_loss


def metrics(pnls: list[float], start_capital: float) -> dict:
    trades = len(pnls)
    wins = sum(1 for x in pnls if x > 0.0)
    total = sum(float(x) for x in pnls)

    return {
        "trades": trades,
        "total_pnl": total,
        "return_pct": total / start_capital,
        "winrate": wins / trades if trades else 0.0,
        "profit_factor": profit_factor(pnls),
        "max_drawdown_pct": max_drawdown_pct(pnls, start_capital),
        "avg_pnl": total / trades if trades else 0.0,
    }


def unrealized_pnl_at_price(side: str, entry_price: float, current_price: float) -> float:
    side_l = str(side).strip().lower()
    if entry_price <= 0.0:
        return 0.0

    if side_l == "long":
        return current_price - entry_price

    if side_l == "short":
        return entry_price - current_price

    return 0.0


def find_first_persistent_toxic(g: pd.DataFrame, window: int) -> int | None:
    levels = list(g["shadow_risk_level"].astype(int))

    streak = 0

    for i, level in enumerate(levels):
        if level >= 2:
            streak += 1
            if streak >= window:
                return i
        else:
            streak = 0

    return None


def find_first_failed_recovery(
    g: pd.DataFrame,
    window: int,
    min_toxic_ratio: float,
    min_safe_after_toxic_ratio: float,
) -> int | None:
    levels = list(g["shadow_risk_level"].astype(int))

    first_toxic_idx = None

    for i, level in enumerate(levels):
        if level >= 2:
            first_toxic_idx = i
            break

    if first_toxic_idx is None:
        return None

    for i in range(first_toxic_idx + window - 1, len(levels)):
        segment = levels[first_toxic_idx : i + 1]
        total = max(1, len(segment))

        toxic_ratio = sum(1 for x in segment if x >= 2) / total
        safe_ratio = sum(1 for x in segment if x == 0) / total

        if toxic_ratio >= min_toxic_ratio and safe_ratio <= min_safe_after_toxic_ratio:
            return i

    return None


def simulate_gate(
    shadow: pd.DataFrame,
    trades: pd.DataFrame,
    gate_name: str,
    gate_indices: dict[str, int | None],
    start_capital: float,
) -> tuple[dict, pd.DataFrame]:

    rows = []
    sim_pnls = []
    base_pnls = []

    for _, trade in trades.iterrows():
        entry_ts = str(trade["entry_timestamp_utc"])
        side = str(trade["side"]).lower()
        final_pnl = float(trade["pnl"])
        entry_price = float(trade["entry_price"]) if "entry_price" in trade and pd.notna(trade["entry_price"]) else None

        base_pnls.append(final_pnl)

        g = shadow[shadow["entry_timestamp_utc"] == entry_ts].copy()
        g = g.sort_values("tick_id").reset_index(drop=True)

        idx = gate_indices.get(entry_ts)

        if idx is None or g.empty or idx >= len(g) or entry_price is None or entry_price <= 0.0:
            sim_pnl = final_pnl
            triggered = 0
            trigger_tick = None
            trigger_price = None
            avoided_pnl = 0.0
        else:
            row = g.iloc[idx]
            trigger_price = float(row["price"])
            sim_pnl = unrealized_pnl_at_price(side, entry_price, trigger_price)
            triggered = 1
            trigger_tick = int(row["tick_id"])
            avoided_pnl = final_pnl - sim_pnl

        sim_pnls.append(sim_pnl)

        rows.append(
            {
                "entry_timestamp_utc": entry_ts,
                "side": side,
                "gate_name": gate_name,
                "triggered": triggered,
                "trigger_tick": trigger_tick,
                "trigger_price": trigger_price,
                "base_pnl": final_pnl,
                "sim_pnl": sim_pnl,
                "avoided_pnl": avoided_pnl,
            }
        )

    base = metrics(base_pnls, start_capital)
    sim = metrics(sim_pnls, start_capital)

    detail = pd.DataFrame(rows)

    triggered_df = detail[detail["triggered"] == 1]

    summary = {
        "gate_name": gate_name,
        "base_trades": base["trades"],
        "triggered_trades": int(detail["triggered"].sum()),
        "triggered_wins": int((triggered_df["base_pnl"] > 0).sum()) if len(triggered_df) else 0,
        "triggered_losses": int((triggered_df["base_pnl"] < 0).sum()) if len(triggered_df) else 0,
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
        "sum_avoided_pnl": float(detail["avoided_pnl"].sum()),
    }

    return summary, detail


def main() -> int:
    args = parse_args()

    shadow_path = Path(args.shadow_csv)
    trades_path = Path(args.trades_jsonl)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not shadow_path.exists():
        raise SystemExit(f"ERROR: missing shadow csv: {shadow_path}")

    if not trades_path.exists():
        raise SystemExit(f"ERROR: missing trades jsonl: {trades_path}")

    shadow = pd.read_csv(shadow_path)
    trades = pd.read_json(trades_path, lines=True)

    required_shadow = {
        "tick_id",
        "entry_timestamp_utc",
        "side",
        "price",
        "shadow_risk_level",
        "shadow_risk_name",
    }

    required_trades = {
        "entry_timestamp_utc",
        "side",
        "entry_price",
        "pnl",
        "duration_sec",
        "exit_reason",
    }

    missing_shadow = sorted(required_shadow - set(shadow.columns))
    missing_trades = sorted(required_trades - set(trades.columns))

    if missing_shadow:
        raise SystemExit(f"ERROR: missing shadow columns: {missing_shadow}")

    if missing_trades:
        raise SystemExit(f"ERROR: missing trades columns: {missing_trades}")

    shadow["entry_timestamp_utc"] = shadow["entry_timestamp_utc"].astype(str)
    trades["entry_timestamp_utc"] = trades["entry_timestamp_utc"].astype(str)

    persistent_indices: dict[str, int | None] = {}
    failed_recovery_indices: dict[str, int | None] = {}

    for entry_ts, g in shadow.groupby("entry_timestamp_utc", dropna=False):
        entry_ts = str(entry_ts)
        g = g.sort_values("tick_id").reset_index(drop=True)

        persistent_indices[entry_ts] = find_first_persistent_toxic(
            g,
            window=args.persistent_window,
        )

        failed_recovery_indices[entry_ts] = find_first_failed_recovery(
            g,
            window=args.failed_recovery_window,
            min_toxic_ratio=args.min_toxic_ratio,
            min_safe_after_toxic_ratio=args.min_safe_after_toxic_ratio,
        )

    summaries = []
    details = []

    for gate_name, indices in [
        ("no_lookahead_persistent_toxic", persistent_indices),
        ("no_lookahead_failed_recovery", failed_recovery_indices),
    ]:
        summary, detail = simulate_gate(
            shadow=shadow,
            trades=trades,
            gate_name=gate_name,
            gate_indices=indices,
            start_capital=args.start_capital,
        )

        summaries.append(summary)
        details.append(detail)

    summary_df = pd.DataFrame(summaries)
    detail_df = pd.concat(details, ignore_index=True)

    summary_out = out_dir / f"shadow_gate_no_lookahead_summary_{args.label}.csv"
    detail_out = out_dir / f"shadow_gate_no_lookahead_detail_{args.label}.csv"

    summary_df.to_csv(summary_out, index=False)
    detail_df.to_csv(detail_out, index=False)

    print("OK: STEP12B no-lookahead shadow gate simulation written")
    print(f"summary: {summary_out}")
    print(f"detail: {detail_out}")
    print("")
    print("NO-LOOKAHEAD GATE SUMMARY")
    print(summary_df.to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
