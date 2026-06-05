import pandas as pd

START_CAPITAL = 10000.0

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

rows = []

for _, trade in trades.iterrows():
    entry_ts = trade["entry_timestamp_utc"]

    snap = shadow[shadow["timestamp_utc"] <= entry_ts].tail(1)

    if len(snap) == 0:
        continue

    snap = snap.iloc[0]

    risk = float(snap["shadow_risk_score"])
    original_pnl = float(trade["pnl"])

    if risk <= 0.30:
        multiplier = 1.00
    elif risk <= 0.50:
        multiplier = 0.50
    else:
        multiplier = 0.25

    scaled_pnl = original_pnl * multiplier

    rows.append({
        "trade_index": int(trade["trade_index"]),
        "side": trade["side"],
        "original_pnl": original_pnl,
        "entry_shadow_risk": risk,
        "multiplier": multiplier,
        "scaled_pnl": scaled_pnl,
    })

df = pd.DataFrame(rows).sort_values("trade_index")

def calc_stats(pnl_col):
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

original = calc_stats("original_pnl")
scaled = calc_stats("scaled_pnl")

print()
print("---- STEP20C LIVE-COMPATIBLE REPLAY ----")
print("trades:", len(df))
print()

print("ORIGINAL")
for k, v in original.items():
    print(k + ":", round(float(v), 4))

print()
print("STEP20C")
for k, v in scaled.items():
    print(k + ":", round(float(v), 4))

print()
print("MULTIPLIER DISTRIBUTION")
print(df["multiplier"].value_counts().sort_index())

out = "reports/step18/step20C_live_replay.csv"
df.to_csv(out, index=False)

print()
print("written:", out)
