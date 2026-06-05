import pandas as pd

START_CAPITAL = 10000.0

configs = [
    ("D1", 0.50, 0.25, 0.10),
    ("D2", 0.75, 0.50, 0.25),
    ("D3", 1.00, 0.50, 0.25),
]

trades = pd.read_csv("live_logs/trades_l1_auto_analysis.csv")
life = pd.read_csv("live_logs/trade_lifecycle_snapshots.csv")
shadow = pd.read_csv("live_logs/passive_shadow_risk_snapshots.csv")

trades["entry_timestamp_utc"] = pd.to_datetime(trades["entry_timestamp_utc"], utc=True)
trades["exit_timestamp_utc"] = pd.to_datetime(trades["exit_timestamp_utc"], utc=True)
life["timestamp_utc"] = pd.to_datetime(life["timestamp_utc"], utc=True)
life["entry_timestamp_utc"] = pd.to_datetime(life["entry_timestamp_utc"], utc=True)
shadow["timestamp_utc"] = pd.to_datetime(shadow["timestamp_utc"], utc=True)

def get_multiplier(risks, m030, m050, m070):
    s030 = s050 = s070 = 0
    m = 1.0
    for r in risks:
        s030 = s030 + 1 if r > 0.30 else 0
        s050 = s050 + 1 if r > 0.50 else 0
        s070 = s070 + 1 if r > 0.70 else 0
        if s030 >= 3:
            m = min(m, m030)
        if s050 >= 3:
            m = min(m, m050)
        if s070 >= 3:
            m = min(m, m070)
    return m

print("config,total_pnl,pf,max_dd_pct,m_010,m_025,m_050,m_075,m_100")

for name, m030, m050, m070 in configs:
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
            mult = 1.0
        else:
            merged = pd.merge_asof(
                life_trade.sort_values("timestamp_utc"),
                shadow_trade.sort_values("timestamp_utc"),
                on="timestamp_utc",
                direction="nearest",
                tolerance=pd.Timedelta("2min"),
            )
            merged["shadow_risk_score"] = merged["shadow_risk_score"].fillna(0.0)
            mult = get_multiplier(merged["shadow_risk_score"].tolist(), m030, m050, m070)

        rows.append({
            "pnl": float(trade["pnl"]) * mult,
            "mult": mult,
        })

    df = pd.DataFrame(rows)
    equity = START_CAPITAL + df["pnl"].cumsum()
    peak = equity.cummax()
    dd_pct = ((peak - equity) / peak).max()

    wins = df[df["pnl"] > 0]
    losses = df[df["pnl"] < 0]
    gp = wins["pnl"].sum()
    gl = abs(losses["pnl"].sum())
    pf = gp / gl if gl > 0 else float("inf")

    vc = df["mult"].value_counts()

    print(
        f"{name},"
        f"{df['pnl'].sum():.2f},"
        f"{pf:.4f},"
        f"{dd_pct:.4f},"
        f"{int(vc.get(0.10,0))},"
        f"{int(vc.get(0.25,0))},"
        f"{int(vc.get(0.50,0))},"
        f"{int(vc.get(0.75,0))},"
        f"{int(vc.get(1.00,0))}"
    )
