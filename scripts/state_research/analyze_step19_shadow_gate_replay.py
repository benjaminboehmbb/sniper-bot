import pandas as pd

START_CAPITAL = 10000.0
THRESHOLDS = [0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
trades["exit_timestamp_utc"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

rows = []

for _, trade in trades.iterrows():
    s = shadow[
        (shadow["timestamp_utc"] >= trade["entry_timestamp_utc"]) &
        (shadow["timestamp_utc"] <= trade["exit_timestamp_utc"])
    ]

    if len(s) == 0:
        continue

    rows.append({
        "trade_index": int(trade["trade_index"]),
        "pnl": float(trade["pnl"]),
        "win": int(float(trade["pnl"]) > 0),
        "mean_shadow_risk": float(s["shadow_risk_score"].mean()),
    })

df = pd.DataFrame(rows).sort_values("trade_index")

df["kept"] = df["mean_shadow_risk"] <= THRESHOLD

kept = df[df["kept"]].copy()

kept["equity"] = START_CAPITAL + kept["pnl"].cumsum()
kept["equity_peak"] = kept["equity"].cummax()
kept["drawdown_abs"] = kept["equity_peak"] - kept["equity"]
kept["drawdown_pct"] = kept["drawdown_abs"] / kept["equity_peak"]

wins = kept[kept["pnl"] > 0]
losses = kept[kept["pnl"] <= 0]

gross_profit = wins["pnl"].sum()
gross_loss = abs(losses["pnl"].sum())
pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")

print()
print("---- STEP19A SHADOW GATE REPLAY ----")
print("threshold:", THRESHOLD)
print("start_capital:", START_CAPITAL)
print("original_trades:", len(df))
print("kept_trades:", len(kept))
print("blocked_trades:", len(df) - len(kept))
print("final_equity:", round(kept["equity"].iloc[-1], 2))
print("total_pnl:", round(kept["pnl"].sum(), 2))
print("return_pct:", round(kept["pnl"].sum() / START_CAPITAL, 4))
print("winrate:", round(kept["win"].mean(), 4))
print("profit_factor:", round(pf, 4))
print("max_drawdown_abs:", round(kept["drawdown_abs"].max(), 2))
print("max_drawdown_pct:", round(kept["drawdown_pct"].max(), 4))
print()

df.to_csv("reports/step18/step19_shadow_gate_replay_trades.csv", index=False)
kept.to_csv("reports/step18/step19_shadow_gate_replay_kept_trades.csv", index=False)

print("written:")
print("reports/step18/step19_shadow_gate_replay_trades.csv")
print("reports/step18/step19_shadow_gate_replay_kept_trades.csv")
