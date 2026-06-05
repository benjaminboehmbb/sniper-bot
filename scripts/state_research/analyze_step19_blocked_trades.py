import pandas as pd

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
        "side": trade["side"],
        "pnl": trade["pnl"],
        "exit_reason": trade["exit_reason"],
        "mean_shadow_risk": s["shadow_risk_score"].mean(),
    })

df = pd.DataFrame(rows)

blocked = df[df["mean_shadow_risk"] > 0.5]

print(blocked.groupby("side")["pnl"].agg(["count","mean","sum"]))
print()
print(blocked.groupby("exit_reason")["pnl"].agg(["count","mean","sum"]).sort_values("sum"))
