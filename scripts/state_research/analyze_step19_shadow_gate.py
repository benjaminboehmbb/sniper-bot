import pandas as pd

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
trades["exit_timestamp_utc"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

rows = []

for _, trade in trades.iterrows():

    trade_shadow = shadow[
        (shadow["timestamp_utc"] >= trade["entry_timestamp_utc"]) &
        (shadow["timestamp_utc"] <= trade["exit_timestamp_utc"])
    ]

    if len(trade_shadow) == 0:
        continue

    rows.append({
        "pnl": float(trade["pnl"]),
        "win": int(float(trade["pnl"]) > 0),
        "mean_shadow_risk": float(trade_shadow["shadow_risk_score"].mean()),
    })

df = pd.DataFrame(rows)

print()
print("TOTAL TRADES:", len(df))
print()

for threshold in [0.50, 0.60, 0.70, 0.80]:

    kept = df[df["mean_shadow_risk"] <= threshold]
    blocked = df[df["mean_shadow_risk"] > threshold]

    print("THRESHOLD", threshold)
    print(" kept_trades :", len(kept))
    print(" blocked     :", len(blocked))
    print(" kept_pnl    :", round(kept["pnl"].sum(), 2))
    print(" kept_winrate:", round(kept["win"].mean(), 4))
    print()
