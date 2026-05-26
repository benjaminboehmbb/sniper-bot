from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def safe_read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise SystemExit(f"ERROR: missing file: {path}")
    return pd.read_csv(path)


def classify_trade(group: pd.DataFrame) -> dict:
    group = group.sort_values("tick_id").reset_index(drop=True)

    states = group["shadow_risk_name"].tolist()

    if len(states) < 4:
        return {
            "triggered": False,
            "trigger_idx": None,
        }

    first_toxic_idx = None

    for idx, state in enumerate(states):
        if state == "TOXIC":
            first_toxic_idx = idx
            break

    if first_toxic_idx is None:
        return {
            "triggered": False,
            "trigger_idx": None,
        }

    pre_states = states[:first_toxic_idx]

    if len(pre_states) < 3:
        return {
            "triggered": False,
            "trigger_idx": None,
        }

    safe_ratio = pre_states.count("SAFE") / len(pre_states)

    if safe_ratio < 0.8:
        return {
            "triggered": False,
            "trigger_idx": None,
        }

    return {
        "triggered": True,
        "trigger_idx": first_toxic_idx,
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("--shadow-csv", required=True)
    parser.add_argument("--trades-jsonl", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--start-capital", type=float, default=10000)

    args = parser.parse_args()

    shadow_df = safe_read_csv(Path(args.shadow_csv))

    trades_df = pd.read_json(
        Path(args.trades_jsonl),
        lines=True,
    )

    rows = []

    grouped = shadow_df.groupby(
        ["entry_timestamp_utc", "side"]
    )

    triggered_trades = set()

    for key, group in grouped:
        result = classify_trade(group)

        if result["triggered"]:
            triggered_trades.add(key)

    sim_df = trades_df.copy()

    if "final_win" not in sim_df.columns:
        sim_df["final_win"] = (sim_df["pnl"].astype(float) > 0).astype(int)

    removed = []

    for _, row in sim_df.iterrows():
        key = (
            row["entry_timestamp_utc"],
            row["side"],
        )

        if key in triggered_trades:
            removed.append(row)

    removed_df = pd.DataFrame(removed)

    kept_df = sim_df[
        ~sim_df.set_index(
            ["entry_timestamp_utc", "side"]
        ).index.isin(triggered_trades)
    ].copy()

    base_total_pnl = sim_df["pnl"].sum()
    sim_total_pnl = kept_df["pnl"].sum()

    base_winrate = sim_df["final_win"].mean()
    sim_winrate = kept_df["final_win"].mean()

    summary = pd.DataFrame(
        [
            {
                "gate_name": "safe_collapse_early_exit",
                "base_trades": len(sim_df),
                "triggered_trades": len(removed_df),
                "triggered_wins": (
                    removed_df["final_win"].sum()
                    if not removed_df.empty
                    else 0
                ),
                "triggered_losses": (
                    len(removed_df)
                    - removed_df["final_win"].sum()
                    if not removed_df.empty
                    else 0
                ),
                "base_total_pnl": base_total_pnl,
                "sim_total_pnl": sim_total_pnl,
                "delta_total_pnl": (
                    sim_total_pnl - base_total_pnl
                ),
                "base_return_pct": (
                    base_total_pnl
                    / args.start_capital
                ),
                "sim_return_pct": (
                    sim_total_pnl
                    / args.start_capital
                ),
                "base_winrate": base_winrate,
                "sim_winrate": sim_winrate,
                "base_avg_pnl": sim_df["pnl"].mean(),
                "sim_avg_pnl": kept_df["pnl"].mean(),
            }
        ]
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = (
        out_dir
        / f"safe_collapse_exit_summary_{args.label}.csv"
    )

    summary.to_csv(summary_path, index=False)

    print("OK: STEP13C safe collapse exit simulation written")
    print(f"summary: {summary_path}")

    print()
    print("SAFE COLLAPSE EXIT SUMMARY")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()