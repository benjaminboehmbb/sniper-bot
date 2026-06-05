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

    pnl = float(trade["pnl"])

    rows.append({
        "pnl": pnl,
        "win": int(pnl > 0.0),
        "mean_shadow_risk": float(s["shadow_risk_score"].mean()),
    })

df = pd.DataFrame(rows)

df["group"] = df["mean_shadow_risk"].apply(
    lambda x: "HIGH_RISK" if x > 0.50 else "LOW_RISK"
)

for group_name, g in df.groupby("group"):

    wins = g[g["pnl"] > 0]
    losses = g[g["pnl"] <= 0]

    gross_profit = wins["pnl"].sum()
    gross_loss = abs(losses["pnl"].sum())

    pf = (
        gross_profit / gross_loss
        if gross_loss > 0
        else float("inf")
    )

    print()
    print("GROUP:", group_name)
    print("trades:", len(g))
    print("winrate:", round(g["win"].mean(), 4))
    print("avg_pnl:", round(g["pnl"].mean(), 2))
    print("gross_profit:", round(gross_profit, 2))
    print("gross_loss:", round(gross_loss, 2))
    print("profit_factor:", round(pf, 4))
    print()

