import pandas as pd

START_CAPITAL = 10000.0

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
trades["exit_timestamp_utc"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

configs = [
    {"threshold": 0.50, "consecutive": 3},
    {"threshold": 0.50, "consecutive": 5},
    {"threshold": 0.60, "consecutive": 3},
    {"threshold": 0.60, "consecutive": 5},
]

print("threshold,consecutive,trades,early_exits,total_pnl,winrate,pf,max_dd_pct")

for cfg in configs:
    threshold = cfg["threshold"]
    consecutive = cfg["consecutive"]

    rows = []

    for _, trade in trades.iterrows():
        s = shadow[
            (shadow["timestamp_utc"] >= trade["entry_timestamp_utc"]) &
            (shadow["timestamp_utc"] <= trade["exit_timestamp_utc"])
        ].copy()

        if len(s) == 0:
            continue

        s["high"] = s["shadow_risk_score"] > threshold
        s["streak"] = s["high"].astype(int).groupby((s["high"] != s["high"].shift()).cumsum()).cumsum()

        triggered = (s["streak"] >= consecutive).any()

        pnl = float(trade["pnl"])

        # Conservative offline assumption:
        # If dynamic exit triggers, use 0 pnl instead of final pnl.
        # This avoids pretending we know exact intratrade exit price from shadow snapshots.
        replay_pnl = 0.0 if triggered else pnl

        rows.append({
            "pnl": replay_pnl,
            "win": int(replay_pnl > 0),
            "triggered": int(triggered),
        })

    df = pd.DataFrame(rows)

    df["equity"] = START_CAPITAL + df["pnl"].cumsum()
    df["peak"] = df["equity"].cummax()
    df["dd_pct"] = (df["peak"] - df["equity"]) / df["peak"]

    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] < 0]

    gross_profit = wins["pnl"].sum()
    gross_loss = abs(losses["pnl"].sum())
    pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")

    print(
        f"{threshold},"
        f"{consecutive},"
        f"{len(df)},"
        f"{df['triggered'].sum()},"
        f"{df['pnl'].sum():.2f},"
        f"{df['win'].mean():.4f},"
        f"{pf:.4f},"
        f"{df['dd_pct'].max():.4f}"
    )
