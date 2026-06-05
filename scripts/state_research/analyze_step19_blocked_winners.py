import pandas as pd

THRESHOLD = 0.40

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
        "side": trade["side"],
        "pnl": float(trade["pnl"]),
        "exit_reason": trade["exit_reason"],
        "mean_shadow_risk": float(s["shadow_risk_score"].mean()),
    })

df = pd.DataFrame(rows)

blocked = df[df["mean_shadow_risk"] > THRESHOLD]
blocked_winners = blocked[blocked["pnl"] > 0]
blocked_losers = blocked[blocked["pnl"] <= 0]

print("blocked_total:", len(blocked))
print("blocked_winners:", len(blocked_winners), "sum_pnl:", round(blocked_winners["pnl"].sum(), 2))
print("blocked_losers:", len(blocked_losers), "sum_pnl:", round(blocked_losers["pnl"].sum(), 2))
print()
print("blocked winners by side")
print(blocked_winners.groupby("side")["pnl"].agg(["count","mean","sum"]))
print()
print("blocked winners by exit_reason")
print(blocked_winners.groupby("exit_reason")["pnl"].agg(["count","mean","sum"]).sort_values("sum", ascending=False))
