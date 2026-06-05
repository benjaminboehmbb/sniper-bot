import pandas as pd

START_CAPITAL = 10000.0

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

df = pd.DataFrame(rows)

print("threshold,trades,blocked,total_pnl,winrate,pf,max_dd_pct")

for threshold in [0.35,0.375,0.40,0.425,0.45,0.475,0.50]:
    kept = df[df["mean_shadow_risk"] <= threshold].copy()

    kept["equity"] = START_CAPITAL + kept["pnl"].cumsum()
    kept["peak"] = kept["equity"].cummax()
    kept["dd_pct"] = (kept["peak"] - kept["equity"]) / kept["peak"]

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
        f"{pf:.4f},"
        f"{kept['dd_pct'].max():.4f}"
    )
