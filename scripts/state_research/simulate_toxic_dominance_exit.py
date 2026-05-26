from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


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


def trade_pnl_at_exit(side: str, entry_price: float, exit_price: float) -> float:
    if side == "long":
        return exit_price - entry_price

    if side == "short":
        return entry_price - exit_price

    return 0.0


def detect_toxic_dominance(group: pd.DataFrame) -> tuple[bool, int | None]:
    group = group.sort_values("tick_id").reset_index(drop=True)

    states = group["shadow_risk_name"].tolist()

    if len(states) < 5:
        return False, None

    for idx in range(2, len(states)):
        window = states[idx - 2 : idx + 1]
        toxic_ratio = window.count("TOXIC") / len(window)

        pre_window = states[: max(0, idx - 2)]
        pre_toxic_ratio = (
            pre_window.count("TOXIC") / len(pre_window)
            if pre_window
            else 0.0
        )

        if toxic_ratio >= 0.66 and pre_toxic_ratio <= 0.25:
            return True, idx

    return False, None


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--shadow-csv", required=True)
    parser.add_argument("--trades-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--start-capital", type=float, default=10000)

    args = parser.parse_args()

    shadow_df = safe_read_csv(Path(args.shadow_csv))
    trades_df = pd.read_json(Path(args.trades_jsonl), lines=True)

    required_shadow = {
        "entry_timestamp_utc",
        "side",
        "tick_id",
        "price",
        "shadow_risk_name",
    }

    required_trades = {
        "entry_timestamp_utc",
        "side",
        "entry_price",
        "pnl",
    }

    missing_shadow = sorted(required_shadow - set(shadow_df.columns))
    missing_trades = sorted(required_trades - set(trades_df.columns))

    if missing_shadow:
        raise SystemExit(f"ERROR: missing shadow columns: {missing_shadow}")

    if missing_trades:
        raise SystemExit(f"ERROR: missing trade columns: {missing_trades}")

    shadow_df["entry_timestamp_utc"] = shadow_df["entry_timestamp_utc"].astype(str)
    trades_df["entry_timestamp_utc"] = trades_df["entry_timestamp_utc"].astype(str)

    trigger_map = {}

    for key, group in shadow_df.groupby(["entry_timestamp_utc", "side"]):
        triggered, trigger_idx = detect_toxic_dominance(group)

        if triggered and trigger_idx is not None:
            group = group.sort_values("tick_id").reset_index(drop=True)
            trigger_row = group.iloc[trigger_idx]

            trigger_map[key] = {
                "trigger_tick": int(trigger_row["tick_id"]),
                "trigger_price": float(trigger_row["price"]),
                "trigger_idx": int(trigger_idx),
            }

    rows = []
    base_pnls = []
    sim_pnls = []

    for _, trade in trades_df.iterrows():
        entry_ts = str(trade["entry_timestamp_utc"])
        side = str(trade["side"]).lower()
        key = (entry_ts, side)

        base_pnl = float(trade["pnl"])
        entry_price = float(trade["entry_price"])

        base_pnls.append(base_pnl)

        if key in trigger_map:
            trigger_price = trigger_map[key]["trigger_price"]
            sim_pnl = trade_pnl_at_exit(
                side=side,
                entry_price=entry_price,
                exit_price=trigger_price,
            )

            triggered = 1
            trigger_tick = trigger_map[key]["trigger_tick"]
            trigger_idx = trigger_map[key]["trigger_idx"]
        else:
            sim_pnl = base_pnl
            triggered = 0
            trigger_tick = None
            trigger_idx = None
            trigger_price = None

        sim_pnls.append(sim_pnl)

        rows.append(
            {
                "entry_timestamp_utc": entry_ts,
                "side": side,
                "triggered": triggered,
                "trigger_tick": trigger_tick,
                "trigger_idx": trigger_idx,
                "trigger_price": trigger_price,
                "entry_price": entry_price,
                "base_pnl": base_pnl,
                "sim_pnl": sim_pnl,
                "delta_pnl": sim_pnl - base_pnl,
            }
        )

    detail_df = pd.DataFrame(rows)

    base_total = sum(base_pnls)
    sim_total = sum(sim_pnls)

    summary_df = pd.DataFrame(
        [
            {
                "gate_name": "toxic_dominance_partial_exit",
                "base_trades": len(base_pnls),
                "triggered_trades": int(detail_df["triggered"].sum()),
                "triggered_base_wins": int(
                    (detail_df[detail_df["triggered"] == 1]["base_pnl"] > 0).sum()
                ),
                "triggered_base_losses": int(
                    (detail_df[detail_df["triggered"] == 1]["base_pnl"] < 0).sum()
                ),
                "base_total_pnl": base_total,
                "sim_total_pnl": sim_total,
                "delta_total_pnl": sim_total - base_total,
                "base_return_pct": base_total / args.start_capital,
                "sim_return_pct": sim_total / args.start_capital,
                "base_winrate": sum(1 for x in base_pnls if x > 0) / len(base_pnls),
                "sim_winrate": sum(1 for x in sim_pnls if x > 0) / len(sim_pnls),
                "base_profit_factor": profit_factor(base_pnls),
                "sim_profit_factor": profit_factor(sim_pnls),
                "base_max_drawdown_pct": max_drawdown_pct(base_pnls, args.start_capital),
                "sim_max_drawdown_pct": max_drawdown_pct(sim_pnls, args.start_capital),
                "base_avg_pnl": base_total / len(base_pnls),
                "sim_avg_pnl": sim_total / len(sim_pnls),
            }
        ]
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = out_dir / f"toxic_dominance_partial_exit_detail_{args.label}.csv"
    summary_path = out_dir / f"toxic_dominance_partial_exit_summary_{args.label}.csv"

    detail_df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print("OK: STEP13G toxic dominance partial-exit simulation written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")
    print()
    print("TOXIC DOMINANCE PARTIAL EXIT SUMMARY")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
