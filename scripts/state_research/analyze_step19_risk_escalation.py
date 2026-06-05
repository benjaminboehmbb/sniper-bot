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
    ].copy()

    if len(s) < 3:
        continue

    pnl = float(trade["pnl"])

    rows.append({
        "win": int(pnl > 0),
        "pnl": pnl,
        "entry_risk": float(s.iloc[0]["shadow_risk_score"]),
        "max_risk": float(s["shadow_risk_score"].max()),
        "mean_risk": float(s["shadow_risk_score"].mean()),
        "high_risk_count": int((s["shadow_risk_score"] > 0.5).sum()),
        "high_risk_pct": float((s["shadow_risk_score"] > 0.5).mean()),
    })

df = pd.DataFrame(rows)

print()
print("WINNERS")
print(df[df["win"] == 1][[
    "entry_risk",
    "max_risk",
    "mean_risk",
    "high_risk_count",
    "high_risk_pct"
]].mean())

print()
print("LOSERS")
print(df[df["win"] == 0][[
    "entry_risk",
    "max_risk",
    "mean_risk",
    "high_risk_count",
    "high_risk_pct"
]].mean())

print()
print("CORRELATIONS")
print("mean_risk vs pnl:", df["mean_risk"].corr(df["pnl"]))
print("max_risk vs pnl :", df["max_risk"].corr(df["pnl"]))
print("high_risk_pct vs pnl :", df["high_risk_pct"].corr(df["pnl"]))
