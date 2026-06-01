import pandas as pd

START_CAPITAL = 10000.0
THRESHOLD = 0.50
CONSECUTIVE = 3

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
life = pd.read_csv("live_logs/trade_lifecycle_snapshots.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
trades["exit_timestamp_utc"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True)
life["timestamp_utc"] = pd.to_datetime(life["timestamp_utc"], utc=True)
life["entry_timestamp_utc"] = pd.to_datetime(life["entry_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

rows = []

for _, trade in trades.iterrows():
    entry_ts = trade["entry_timestamp_utc"]
    exit_ts = trade["exit_timestamp_utc"]
    side = str(trade["side"]).lower()

    life_trade = life[
        (life["entry_timestamp_utc"] == entry_ts) &
        (life["side"].astype(str).str.lower() == side)
    ].copy()

    shadow_trade = shadow[
        (shadow["timestamp_utc"] >= entry_ts) &
        (shadow["timestamp_utc"] <= exit_ts)
    ][["timestamp_utc", "shadow_risk_score"]].copy()

    if len(life_trade) == 0 or len(shadow_trade) == 0:
        replay_pnl = float(trade["pnl"])
        exit_type = "ORIGINAL_NO_LIFECYCLE"
    else:
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

            exit_type = "STEP19B_DYNAMIC_EXIT"
        else:
            replay_pnl = float(trade["pnl"])
            exit_type = "ORIGINAL_EXIT"

    rows.append({
        "trade_index": int(trade["trade_index"]),
        "side": side,
        "original_pnl": float(trade["pnl"]),
        "replay_pnl": replay_pnl,
        "exit_type": exit_type,
    })

df = pd.DataFrame(rows).sort_values("trade_index")

df["win"] = (df["replay_pnl"] > 0).astype(int)
df["equity"] = START_CAPITAL + df["replay_pnl"].cumsum()
df["peak"] = df["equity"].cummax()
df["dd_abs"] = df["peak"] - df["equity"]
df["dd_pct"] = df["dd_abs"] / df["peak"]

wins = df[df["replay_pnl"] > 0]
losses = df[df["replay_pnl"] < 0]

gross_profit = wins["replay_pnl"].sum()
gross_loss = abs(losses["replay_pnl"].sum())
pf = gross_profit / gross_loss if gross_loss > 0 else float("inf")

print()
print("---- STEP19B REAL EXIT REPLAY ----")
print("threshold:", THRESHOLD)
print("consecutive:", CONSECUTIVE)
print("trades:", len(df))
print("dynamic_exits:", int((df["exit_type"] == "STEP19B_DYNAMIC_EXIT").sum()))
print("final_equity:", round(df["equity"].iloc[-1], 2))
print("total_pnl:", round(df["replay_pnl"].sum(), 2))
print("return_pct:", round(df["replay_pnl"].sum() / START_CAPITAL, 4))
print("winrate:", round(df["win"].mean(), 4))
print("profit_factor:", round(pf, 4))
print("max_drawdown_abs:", round(df["dd_abs"].max(), 2))
print("max_drawdown_pct:", round(df["dd_pct"].max(), 4))
print()
print(df.groupby("exit_type")["replay_pnl"].agg(["count", "mean", "sum"]))

out = "reports/step18/step19B_real_exit_replay.csv"
df.to_csv(out, index=False)
print()
print("written:", out)
