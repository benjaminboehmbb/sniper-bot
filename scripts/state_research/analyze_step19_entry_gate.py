import pandas as pd

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

rows = []

for _, trade in trades.iterrows():

    entry_ts = trade["entry_timestamp_utc"]

    snap = shadow[
        shadow["timestamp_utc"] <= entry_ts
    ].tail(1)

    if len(snap) == 0:
        continue

    snap = snap.iloc[0]

    pnl = float(trade["pnl"])

    rows.append({
        "pnl": pnl,
        "win": int(pnl > 0.0),
        "entry_shadow_risk": float(snap["shadow_risk_score"]),
    })

df = pd.DataFrame(rows)

print()
print("ENTRY_RISK vs PNL")
print(df["entry_shadow_risk"].corr(df["pnl"]))
print()

print("ENTRY_RISK vs WIN")
print(df["entry_shadow_risk"].corr(df["win"]))
print()

print("threshold,trades,blocked,total_pnl,winrate,pf")

for threshold in [0.35,0.40,0.45,0.50,0.55,0.60]:

    kept = df[df["entry_shadow_risk"] <= threshold]

    wins = kept[kept["pnl"] > 0]
    losses = kept[kept["pnl"] <= 0]

    gross_profit = wins["pnl"].sum()
    gross_loss = abs(losses["pnl"].sum())

    pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    print(
        f"{threshold},"
        f"{len(kept)},"
        f"{len(df)-len(kept)},"
        f"{kept['pnl'].sum():.2f},"
        f"{kept['win'].mean():.4f},"
        f"{pf:.4f}"
    )
