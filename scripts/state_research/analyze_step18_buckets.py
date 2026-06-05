import pandas as pd

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)
trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)

rows = []

for _, trade in trades.iterrows():
    entry_ts = trade["entry_timestamp_utc"]

    snap = shadow[
        shadow["timestamp_utc"] <= entry_ts
    ].tail(1)

    if len(snap) == 0:
        continue

    snap = snap.iloc[0]

    rows.append({
        "pnl": float(trade["pnl"]),
        "win": int(float(trade["pnl"]) > 0.0),
        "shadow_risk_score": float(snap["shadow_risk_score"]),
    })

df = pd.DataFrame(rows)

df["bucket"] = pd.cut(
    df["shadow_risk_score"],
    bins=[0,0.2,0.4,0.6,0.8,1.0],
    include_lowest=True
)

summary = (
    df.groupby("bucket")
    .agg(
        trades=("pnl","count"),
        avg_pnl=("pnl","mean"),
        winrate=("win","mean"),
    )
    .reset_index()
)

print()
print(summary)
print()
