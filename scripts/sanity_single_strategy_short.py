#!/usr/bin/env python3
"""
Sanity-Backtest (Short-only) auf OHLCV-CSV.
- Erwartet Spalten: open_time, open, high, low, close, volume
- Indikatoren: RSI(14), MACD(12,26,9), Bollinger(20,2)
- Signal: gewichtete Summe; Entry wenn < -0.5, Exit wenn >= 0
- Fees/Slippage berücksichtigt (konstant klein)
- Outputs:
  results/sanity_short_result.json
  results/sanity_short_trades.csv
"""
import os, sys, json, argparse
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEF_SRC = os.path.join(ROOT, "data", "btcusdt_5m_spot.csv")
RES_DIR = os.path.join(ROOT, "results")
os.makedirs(RES_DIR, exist_ok=True)

def rsi(series, period=14):
    delta = series.diff()
    up = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    down = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = up / (down + 1e-12)
    return 100 - (100 / (1 + rs))

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - macd_signal
    return macd_line, macd_signal, hist

def bollinger(series, window=20, k=2.0):
    ma = series.rolling(window).mean()
    sd = series.rolling(window).std(ddof=0)
    upper = ma + k*sd
    lower = ma - k*sd
    width = (upper - lower) / (ma + 1e-12)
    return ma, upper, lower, width

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEF_SRC, help="Pfad zur OHLCV-CSV")
    ap.add_argument("--fee", type=float, default=0.0005, help="Gebühr pro Trade (0.05%)")
    ap.add_argument("--slip", type=float, default=0.0002, help="Slippage pro Trade (0.02%)")
    ap.add_argument("--risk_unit", type=float, default=1.0, help="Einsatz-Einheit pro Trade (vereinfacht)")
    args = ap.parse_args()

    if not os.path.isfile(args.src):
        print(f"❌ Quelle nicht gefunden: {args.src}")
        sys.exit(1)

    df = pd.read_csv(args.src)
    need = ["open_time","open","high","low","close","volume"]
    miss = [c for c in need if c not in df.columns]
    if miss:
        print(f"❌ Fehlende Spalten: {miss}")
        sys.exit(2)

    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.sort_values("open_time").reset_index(drop=True)

    # Indikatoren
    df["rsi"] = rsi(df["close"], 14)
    macd_line, macd_signal, macd_hist = macd(df["close"], 12, 26, 9)
    df["macd"] = macd_line
    df["macd_sig"] = macd_signal
    ma, up, lo, width = bollinger(df["close"], 20, 2.0)
    df["bb_width"] = width

    # Einfache Signale (wie in Long-Version, aber gleich genutzt)
    df["sig_rsi"]   = ((df["rsi"] - 50.0) / 50.0).clip(-1, 1)              # [-1..+1]
    df["sig_macd"]  = np.sign(df["macd"] - df["macd_sig"])                 # {-1,0,+1}
    w_med           = df["bb_width"].rolling(200).median()
    df["sig_bb"]    = np.sign((df["bb_width"] - w_med).fillna(0))          # {-1,0,+1}

    # Gewichte
    w_rsi, w_macd, w_bb = 0.5, 0.4, 0.1
    df["combo"] = w_rsi*df["sig_rsi"] + w_macd*df["sig_macd"] + w_bb*df["sig_bb"]

    # Regeln (short-only):
    # Entry, wenn combo < -0.5 und keine Position; Exit, wenn combo >= 0
    position = 0   # 0 flat, -1 short
    entry_price = None
    trades = []
    fee = args.fee
    slip = args.slip
    qty = args.risk_unit

    for i in range(len(df)):
        c = float(df.at[i, "close"])
        t = df.at[i, "open_time"]

        # Exit (short schließen)
        if position == -1 and df.at[i, "combo"] >= 0:
            exit_price = c * (1 + slip)  # zurückkaufen (slip +)
            pnl = (entry_price - exit_price) * qty  # short-PL: entry - exit
            # Gebühren: 2x (Entry+Exit)
            pnl -= (entry_price * qty * fee)
            pnl -= (exit_price * qty * fee)
            trades.append({"timestamp": t, "side": "EXIT", "price": exit_price, "pnl": pnl})
            position = 0
            entry_price = None
            continue

        # Entry (short eröffnen)
        if position == 0 and df.at[i, "combo"] < -0.5:
            entry_price = c * (1 - slip)  # zuerst verkaufen (slip -)
            trades.append({"timestamp": t, "side": "ENTRY", "price": entry_price, "pnl": 0.0})
            position = -1

    # Falls am Ende offen: schließen zum letzten Kurs
    if position == -1 and entry_price is not None:
        c = float(df.iloc[-1]["close"])
        t = df.iloc[-1]["open_time"]
        exit_price = c * (1 + slip)
        pnl = (entry_price - exit_price) * qty
        pnl -= (entry_price * qty * fee)
        pnl -= (exit_price * qty * fee)
        trades.append({"timestamp": t, "side": "EXIT_EOD", "price": exit_price, "pnl": pnl})

    # Kennzahlen
    pnl_list = [x["pnl"] for x in trades if x["side"].startswith("EXIT")]
    wins = sum(1 for x in pnl_list if x > 0)
    losses = sum(1 for x in pnl_list if x <= 0)
    roi = (sum(pnl_list) / (qty * (df["close"].iloc[0] + 1e-12)))
    winrate = (wins / max(1, (wins + losses)))

    # speichern
    trades_df = pd.DataFrame(trades)
    trades_path = os.path.join(RES_DIR, "sanity_short_trades.csv")
    trades_df.to_csv(trades_path, index=False)

    res = {
        "src": os.path.relpath(args.src, ROOT),
        "n_trades": int(wins + losses),
        "wins": int(wins),
        "losses": int(losses),
        "winrate": round(float(winrate), 4),
        "roi_vs_startprice": round(float(roi), 6),
        "fee": args.fee,
        "slippage": args.slip,
        "weights": {"rsi": w_rsi, "macd": w_macd, "bb": w_bb},
        "entry_rule": "combo<-0.5; exit combo>=0; short-only",
        "outputs": {"trades_csv": os.path.relpath(trades_path, ROOT)}
    }
    with open(os.path.join(RES_DIR, "sanity_short_result.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    print("✅ Sanity-Backtest (short-only) fertig.")
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
