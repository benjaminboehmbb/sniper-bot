import pandas as pd

START_CAPITAL = 10000.0

configs = [
    (0.5, 3),
    (0.5, 5),
    (0.6, 3),
    (0.6, 5),
    (0.7, 3),
]

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
life = pd.read_csv("live_logs/trade_lifecycle_snapshots.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
trades["exit_timestamp_utc"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True)
life["timestamp_utc"] = pd.to_datetime(life["timestamp_utc"], utc=True)
life["entry_timestamp_utc"] = pd.to_datetime(life["entry_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

print("threshold,consecutive,dynamic_exits,total_pnl,pf,max_dd_pct")

for THRESHOLD, CONSECUTIVE in configs:

    rows = []

    for _, trade in trades.iterrows():

        entry_ts = trade["entry_timestamp_utc"]
        exit_ts = trade["exit_timestamp_utc"]
        side = str(trade["side"]).lower()

        life_trade = life[
            (life["entry_timestamp_utc"] == entry_ts)
            & (life["side"].astype(str).str.lower() == side)
        ].copy()

        shadow_trade = shadow[
            (shadow["timestamp_utc"] >= entry_ts)
            & (shadow["timestamp_utc"] <= exit_ts)
        ][["timestamp_utc", "shadow_risk_score"]].copy()

        replay_pnl = float(trade["pnl"])
        triggered = 0

        if len(life_trade) > 0 and len(shadow_trade) > 0:

            merged = pd.merge_asof(
                life_trade.sort_values("timestamp_utc"),
                shadow_trade.sort_values("timestamp_utc"),
                on="timestamp_utc",
                direction="nearest",
                tolerance=pd.Timedelta("2min"),
            )

            merged["shadow_risk_score"] = merged["shadow_risk_score"].fillna(0.0)

            merged["high"] = merged["shadow_risk_score"] > THRESHOLD

            merged["streak"] = (
                merged["high"]
                .astype(int)
                .groupby((merged["high"] != merged["high"].shift()).cumsum())
                .cumsum()
            )

            trigger = merged[merged["streak"] >= CONSECUTIVE]

            if len(trigger) > 0:

                row = trigger.iloc[0]

                entry_price = float(row["entry_price"])
                exit_price = float(row["current_price"])
                size = float(row["position_size"])

                if side == "long":
                    replay_pnl = (exit_price - entry_price) * size
                else:
                    replay_pnl = (entry_price - exit_price) * size

                triggered = 1

        rows.append(
            {
                "pnl": replay_pnl,
                "triggered": triggered,
            }
        )

    df = pd.DataFrame(rows)

    df["equity"] = START_CAPITAL + df["pnl"].cumsum()
    df["peak"] = df["equity"].cummax()
    df["dd_pct"] = (df["peak"] - df["equity"]) / df["peak"]

    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] < 0]

    gp = wins["pnl"].sum()
    gl = abs(losses["pnl"].sum())

    pf = gp / gl if gl > 0 else float("inf")

    print(
        f"{THRESHOLD},"
        f"{CONSECUTIVE},"
        f"{df['triggered'].sum()},"
        f"{df['pnl'].sum():.2f},"
        f"{pf:.4f},"
        f"{df['dd_pct'].max():.4f}"
    )
