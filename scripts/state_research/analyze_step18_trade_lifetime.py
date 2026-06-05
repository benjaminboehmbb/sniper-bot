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
        "max_shadow_risk": float(trade_shadow["shadow_risk_score"].max()),
        "mean_meta_state": float(trade_shadow["meta_state_score"].mean()),
    })

df = pd.DataFrame(rows)

print()
print("matched trades:", len(df))
print()

print("mean_shadow_risk vs pnl")
print(df["mean_shadow_risk"].corr(df["pnl"]))
print()

print("mean_shadow_risk vs win")
print(df["mean_shadow_risk"].corr(df["win"]))
print()

print("max_shadow_risk vs pnl")
print(df["max_shadow_risk"].corr(df["pnl"]))
print()

print("max_shadow_risk vs win")
print(df["max_shadow_risk"].corr(df["win"]))
print()

print("mean_meta_state vs pnl")
print(df["mean_meta_state"].corr(df["pnl"]))
print()

print("mean_meta_state vs win")
print(df["mean_meta_state"].corr(df["win"]))
print()
