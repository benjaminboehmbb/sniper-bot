from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


TOXIC_CONFIRM_COUNT = 3
MAX_ALLOWED_RECOVERY_RATIO = 0.25


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


def detect_confirmed_toxicity(
    group: pd.DataFrame,
) -> tuple[bool, int | None]:

    group = group.sort_values("tick_id").reset_index(drop=True)

    states = group["shadow_risk_name"].tolist()

    toxic_seen = 0

    for idx, state in enumerate(states):

        if state == "TOXIC":
            toxic_seen += 1

        if toxic_seen >= TOXIC_CONFIRM_COUNT:

            sub = states[: idx + 1]

            recovery_ratio = (
                sub.count("SAFE") / len(sub)
                if len(sub) > 0
                else 0.0
            )

            if recovery_ratio <= MAX_ALLOWED_RECOVERY_RATIO:
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

    shadow_df["entry_timestamp_utc"] = (
        shadow_df["entry_timestamp_utc"].astype(str)
    )

    trades_df["entry_timestamp_utc"] = (
        trades_df["entry_timestamp_utc"].astype(str)
    )

    if "final_win" not in trades_df.columns:
        trades_df["final_win"] = (
            trades_df["pnl"].astype(float) > 0
        ).astype(int)

    trigger_map = {}

    grouped = shadow_df.groupby(
        ["entry_timestamp_utc", "side"]
    )

    for key, group in grouped:

        triggered, trigger_idx = detect_confirmed_toxicity(group)

        if triggered and trigger_idx is not None:

            group = group.sort_values("tick_id").reset_index(drop=True)

            row = group.iloc[trigger_idx]

            trigger_map[key] = {
                "trigger_tick": int(row["tick_id"]),
                "trigger_price": float(row["price"]),
                "trigger_idx": int(trigger_idx),
            }

    base_pnls = []
    sim_pnls = []

    rows = []

    for _, trade in trades_df.iterrows():

        side = str(trade["side"]).lower()

        key = (
            str(trade["entry_timestamp_utc"]),
            side,
        )

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

        else:
            sim_pnl = base_pnl
            triggered = 0

        sim_pnls.append(sim_pnl)

        rows.append(
            {
                "entry_timestamp_utc": trade["entry_timestamp_utc"],
                "side": side,
                "triggered": triggered,
                "base_pnl": base_pnl,
                "sim_pnl": sim_pnl,
                "delta_pnl": sim_pnl - base_pnl,
            }
        )

    detail_df = pd.DataFrame(rows)

    summary_df = pd.DataFrame(
        [
            {
                "gate_name": "confirmed_toxic_persistence_exit",
                "base_trades": len(base_pnls),
                "triggered_trades": int(detail_df["triggered"].sum()),
                "base_total_pnl": sum(base_pnls),
                "sim_total_pnl": sum(sim_pnls),
                "delta_total_pnl": (
                    sum(sim_pnls) - sum(base_pnls)
                ),
                "base_return_pct": (
                    sum(base_pnls) / args.start_capital
                ),
                "sim_return_pct": (
                    sum(sim_pnls) / args.start_capital
                ),
                "base_winrate": (
                    sum(1 for x in base_pnls if x > 0)
                    / len(base_pnls)
                ),
                "sim_winrate": (
                    sum(1 for x in sim_pnls if x > 0)
                    / len(sim_pnls)
                ),
                "base_profit_factor": profit_factor(base_pnls),
                "sim_profit_factor": profit_factor(sim_pnls),
                "base_max_drawdown_pct": (
                    max_drawdown_pct(
                        base_pnls,
                        args.start_capital,
                    )
                ),
                "sim_max_drawdown_pct": (
                    max_drawdown_pct(
                        sim_pnls,
                        args.start_capital,
                    )
                ),
                "base_avg_pnl": (
                    sum(base_pnls) / len(base_pnls)
                ),
                "sim_avg_pnl": (
                    sum(sim_pnls) / len(sim_pnls)
                ),
            }
        ]
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    detail_path = (
        out_dir
        / f"confirmed_toxic_exit_detail_{args.label}.csv"
    )

    summary_path = (
        out_dir
        / f"confirmed_toxic_exit_summary_{args.label}.csv"
    )

    detail_df.to_csv(detail_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print("OK: STEP13E confirmed toxic persistence simulation written")
    print(f"detail: {detail_path}")
    print(f"summary: {summary_path}")

    print()
    print("CONFIRMED TOXIC EXIT SUMMARY")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()