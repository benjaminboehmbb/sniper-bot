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

    risk = float(s["shadow_risk_score"].mean())
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
        "mean_shadow_risk": risk,
        "multiplier": multiplier,
        "scaled_pnl": scaled_pnl,
    })

df = pd.DataFrame(rows).sort_values("trade_index")

def stats(pnl_col):
    equity = START_CAPITAL + df[pnl_col].cumsum()
    peak = equity.cummax()
    dd = peak - equity
    dd_pct = dd / peak

    wins = df[df[pnl_col] > 0]
    losses = df[df[pnl_col] < 0]

    gp = wins[pnl_col].sum()
    gl = abs(losses[pnl_col].sum())
    pf = gp / gl if gl > 0 else float("inf")

    return {
        "final_equity": float(equity.iloc[-1]),
        "total_pnl": float(df[pnl_col].sum()),
        "return_pct": float(df[pnl_col].sum() / START_CAPITAL),
        "winrate": float((df[pnl_col] > 0).mean()),
        "profit_factor": float(pf),
        "max_drawdown_abs": float(dd.max()),
        "max_drawdown_pct": float(dd_pct.max()),
    }

original = stats("original_pnl")
scaled = stats("scaled_pnl")

print()
print("---- STEP20A POSITION SIZING REPLAY ----")
print("trades:", len(df))
print()

print("ORIGINAL")
for k, v in original.items():
    print(k + ":", round(v, 4))

print()
print("SCALED")
for k, v in scaled.items():
    print(k + ":", round(v, 4))

print()
print("MULTIPLIER DISTRIBUTION")
print(df["multiplier"].value_counts().sort_index())

out = "reports/step18/step20_position_sizing_replay.csv"
df.to_csv(out, index=False)

print()
print("written:", out)
