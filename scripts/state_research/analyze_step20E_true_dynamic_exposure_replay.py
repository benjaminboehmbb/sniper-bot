import pandas as pd

START_CAPITAL = 10000.0

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
life = pd.read_csv("live_logs/trade_lifecycle_snapshots.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
trades["exit_timestamp_utc"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True)
life["timestamp_utc"] = pd.to_datetime(life["timestamp_utc"], utc=True)
life["entry_timestamp_utc"] = pd.to_datetime(life["entry_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)


def update_multiplier(risk, s030, s050, s070, current_mult):
    s030 = s030 + 1 if risk > 0.30 else 0
    s050 = s050 + 1 if risk > 0.50 else 0
    s070 = s070 + 1 if risk > 0.70 else 0

    new_mult = current_mult

    if s030 >= 3:
        new_mult = min(new_mult, 0.50)
    if s050 >= 3:
        new_mult = min(new_mult, 0.25)
    if s070 >= 3:
        new_mult = min(new_mult, 0.10)

    return s030, s050, s070, new_mult


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

    original_pnl = float(trade["pnl"])

    if len(life_trade) == 0 or len(shadow_trade) == 0:
        replay_pnl = original_pnl
        reductions = 0
        final_mult = 1.0
    else:
        merged = pd.merge_asof(
            life_trade.sort_values("timestamp_utc"),
            shadow_trade.sort_values("timestamp_utc"),
            on="timestamp_utc",
            direction="nearest",
            tolerance=pd.Timedelta("2min"),
        )

        merged["shadow_risk_score"] = merged["shadow_risk_score"].fillna(0.0)

        merged = merged.sort_values("timestamp_utc").copy()

        entry_price = float(merged.iloc[0]["entry_price"])
        prev_price = entry_price
        current_mult = 1.0
        replay_pnl = 0.0
        reductions = 0

        s030 = s050 = s070 = 0

        for _, row in merged.iterrows():
            price = float(row["current_price"])
            risk = float(row["shadow_risk_score"])

            if side == "long":
                segment_pnl = (price - prev_price) * current_mult
            else:
                segment_pnl = (prev_price - price) * current_mult

            replay_pnl += segment_pnl
            prev_price = price

            old_mult = current_mult
            s030, s050, s070, current_mult = update_multiplier(
                risk,
                s030,
                s050,
                s070,
                current_mult,
            )

            if current_mult < old_mult:
                reductions += 1

        final_exit_price = float(trade["exit_price"])

        if side == "long":
            final_segment_pnl = (final_exit_price - prev_price) * current_mult
        else:
            final_segment_pnl = (prev_price - final_exit_price) * current_mult

        replay_pnl += final_segment_pnl
        final_mult = current_mult

    rows.append({
        "trade_index": int(trade["trade_index"]),
        "side": side,
        "original_pnl": original_pnl,
        "replay_pnl": replay_pnl,
        "reductions": reductions,
        "final_multiplier": final_mult,
    })


df = pd.DataFrame(rows).sort_values("trade_index")


def stats(pnl_col):
    equity = START_CAPITAL + df[pnl_col].cumsum()
    peak = equity.cummax()
    dd_abs = peak - equity
    dd_pct = dd_abs / peak

    wins = df[df[pnl_col] > 0]
    losses = df[df[pnl_col] < 0]

    gp = wins[pnl_col].sum()
    gl = abs(losses[pnl_col].sum())
    pf = gp / gl if gl > 0 else float("inf")

    return {
        "final_equity": equity.iloc[-1],
        "total_pnl": df[pnl_col].sum(),
        "return_pct": df[pnl_col].sum() / START_CAPITAL,
        "winrate": (df[pnl_col] > 0).mean(),
        "profit_factor": pf,
        "max_drawdown_abs": dd_abs.max(),
        "max_drawdown_pct": dd_pct.max(),
    }


original = stats("original_pnl")
replay = stats("replay_pnl")

print()
print("---- STEP20E TRUE DYNAMIC EXPOSURE REPLAY ----")
print("trades:", len(df))
print()

print("ORIGINAL")
for k, v in original.items():
    print(k + ":", round(float(v), 4))

print()
print("STEP20E")
for k, v in replay.items():
    print(k + ":", round(float(v), 4))

print()
print("FINAL MULTIPLIER DISTRIBUTION")
print(df["final_multiplier"].value_counts().sort_index())

print()
print("REDUCTIONS")
print(df["reductions"].value_counts().sort_index())

out = "reports/step18/step20E_true_dynamic_exposure_replay.csv"
df.to_csv(out, index=False)

print()
print("written:", out)
