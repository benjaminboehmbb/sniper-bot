#!/usr/bin/env python3
"""
Analyze Long-Only — eigenständig, ersetzt nichts.
Liest:
  - Preise: data/btcusdt_1m_spot.csv (Fallback: *_filled.csv)
  - Strategien: CSV mit Spalte 'Combination' (Dictionary-String, z.B. "{'rsi':0.5,'macd':0.3}")
Berechnet 12 Indikatoren, normalisiert je ein Signal [-1..+1], bildet gewichtete Summe,
handelt Long-only (Entry combo>+0.5, Exit combo<=0), speichert Kennzahlen je Strategie.

Outputs:
  results/2er|3er|.../strategy_results_long.csv  (wird aus Dateiname der Strategien abgeleitet)
  results/2er|3er|.../trades_long_<idx>.csv      (optional pro Strategie, hier AUS für Speed)
"""
import os, sys, csv, ast, argparse, math
import numpy as np
import pandas as pd
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES  = os.path.join(ROOT, "results")

# ---------- Utils ----------
def load_prices():
    p1 = os.path.join(DATA, "btcusdt_1m_spot.csv")
    p2 = os.path.join(DATA, "btcusdt_1m_spot_filled.csv")
    src = p1 if os.path.isfile(p1) else p2
    if not os.path.isfile(src):
        raise FileNotFoundError(f"Preis-CSV nicht gefunden: {p1} oder {p2}")
    df = pd.read_csv(src)
    need = ["open_time","open","high","low","close","volume"]
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise ValueError(f"Fehlende Spalten in {src}: {miss}")
    df["open_time"] = pd.to_datetime(df["open_time"])
    df = df.sort_values("open_time").reset_index(drop=True)
    return df, src

def parse_strategies(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Strategie-CSV fehlt: {path}")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if "Combination" not in r.fieldnames:
            raise ValueError(f"'Combination' Spalte fehlt in {path}")
        for i, row in enumerate(r, start=1):
            combo = ast.literal_eval(row["Combination"])
            if not isinstance(combo, dict) or not combo:
                continue
            rows.append(combo)
    return rows

def out_dir_for(path_strategies):
    base = os.path.basename(path_strategies).lower()
    # heuristik: "strategies_2er.csv" → "2er"
    kdir = "other"
    for tag in ["2er","3er","4er","5er","6er","7er","8er","9er","10er","11er","12er"]:
        if tag in base:
            kdir = tag
            break
    outdir = os.path.join(RES, kdir if kdir!="other" else "sanity")
    os.makedirs(outdir, exist_ok=True)
    return outdir

# ---------- Indicators ----------
def ema(s, span): return s.ewm(span=span, adjust=False).mean()
def sma(s, w):    return s.rolling(w).mean()
def rsi(close, period=14):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = up / (dn + 1e-12)
    return 100 - (100/(1+rs))
def macd(close, fast=12, slow=26, sig=9):
    ef, es = ema(close, fast), ema(close, slow)
    m = ef - es
    ms = ema(m, sig)
    return m, ms, m - ms
def bollinger(close, w=20, k=2.0):
    ma = sma(close, w)
    sd = close.rolling(w).std(ddof=0)
    up, lo = ma + k*sd, ma - k*sd
    width = (up - lo) / (ma + 1e-12)
    return ma, up, lo, width
def stoch_osc(high, low, close, k=14, d=3):
    ll = low.rolling(k).min()
    hh = high.rolling(k).max()
    kline = 100 * (close - ll) / (hh - ll + 1e-12)
    dline = kline.rolling(d).mean()
    return kline, dline
def atr(high, low, close, w=14):
    prev = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev).abs(),
        (low - prev).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(w).mean()
def adx_func(high, low, close, w=14):
    # Simplified ADX
    up = high.diff()
    dn = -low.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = atr(high, low, close, w=1)
    plus_di = 100 * pd.Series(plus_dm).rolling(w).sum() / (tr.rolling(w).sum() + 1e-12)
    minus_di = 100 * pd.Series(minus_dm).rolling(w).sum() / (tr.rolling(w).sum() + 1e-12)
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di + 1e-12))
    return pd.Series(dx).rolling(w).mean()
def cci_func(high, low, close, w=20):
    tp = (high + low + close) / 3.0
    ma = tp.rolling(w).mean()
    md = (tp - ma).abs().rolling(w).mean()
    return (tp - ma) / (0.015 * (md + 1e-12))
def mfi_func(high, low, close, volume, w=14):
    tp = (high + low + close) / 3.0
    pm = tp * volume
    pos = pm.where(tp > tp.shift(1), 0.0)
    neg = pm.where(tp < tp.shift(1), 0.0)
    mr = pos.rolling(w).sum() / (neg.rolling(w).sum() + 1e-12)
    return 100 - (100/(1+mr))
def obv_func(close, volume):
    direction = np.sign(close.diff().fillna(0.0))
    return (volume * direction).cumsum()
def roc_func(close, w=10):
    return 100.0 * (close / (close.shift(w) + 1e-12) - 1.0)

def build_signals(df):
    close, high, low, vol = df["close"], df["high"], df["low"], df["volume"]
    # compute
    rsi14 = rsi(close, 14)
    mline, msignal, mhist = macd(close, 12, 26, 9)
    ma200 = sma(close, 200)
    ema50 = ema(close, 50)
    ma, up, lo, bb_w = bollinger(close, 20, 2.0)
    st_k, st_d = stoch_osc(high, low, close, 14, 3)
    atr14 = atr(high, low, close, 14)
    adx14 = adx_func(high, low, close, 14)
    cci20 = cci_func(high, low, close, 20)
    mfi14 = mfi_func(high, low, close, vol, 14)
    obv = obv_func(close, vol)
    roc10 = roc_func(close, 10)

    # normalized signals in [-1..+1]
    sig = {}
    sig["rsi"]       = ((rsi14 - 50.0) / 50.0).clip(-1, 1)
    sig["macd"]      = np.sign(mline - msignal)
    sig["bollinger"] = np.sign((bb_w - bb_w.rolling(200).median()).fillna(0))
    sig["ma200"]     = np.sign(close - ma200)
    sig["stoch"]     = ((st_k - 50.0) / 50.0).clip(-1, 1)
    sig["atr"]       = np.sign((atr14 - atr14.rolling(200).median()).fillna(0))
    sig["ema50"]     = np.sign(close - ema50)
    sig["adx"]       = np.sign(adx14 - 25.0)
    sig["cci"]       = np.sign(cci20)
    sig["mfi"]       = ((mfi14 - 50.0) / 50.0).clip(-1, 1)
    sig["obv"]       = np.sign(obv.diff().rolling(10).sum().fillna(0))
    sig["roc"]       = np.sign(roc10)
    return sig

def backtest_long(df, sig_map, combo_dict, thr_entry=0.5, thr_exit=0.0, fee=0.0005, slip=0.0002):
    # gewichtete Summe
    arr = None
    for name, w in combo_dict.items():
        s = sig_map.get(name)
        if s is None:  # unbekanntes Signal
            continue
        v = w * s
        arr = v if arr is None else (arr + v)
    if arr is None:
        arr = pd.Series(0.0, index=df.index)

    position = 0
    entry = None
    pnl_list = []
    for i in range(len(df)):
        c = float(df.at[i, "close"])
        # Exit
        if position == 1 and arr.iat[i] <= thr_exit:
            exit_price = c * (1 - slip)
            pnl = (exit_price - entry) - fee*(entry + exit_price)
            pnl_list.append(pnl)
            position = 0
            entry = None
            continue
        # Entry
        if position == 0 and arr.iat[i] > thr_entry:
            entry = c * (1 + slip)
            position = 1
    if position == 1 and entry is not None:
        c = float(df.iloc[-1]["close"])
        exit_price = c * (1 - slip)
        pnl = (exit_price - entry) - fee*(entry + exit_price)
        pnl_list.append(pnl)

    wins = sum(1 for x in pnl_list if x > 0)
    losses = sum(1 for x in pnl_list if x <= 0)
    roi = (sum(pnl_list) / (df["close"].iloc[0] + 1e-12))
    winrate = wins / max(1, (wins + losses))
    return {
        "num_trades": wins + losses,
        "wins": wins,
        "losses": losses,
        "winrate": round(float(winrate), 6),
        "roi": round(float(roi), 6)
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strategies_csv", help="CSV mit Spalte 'Combination'")
    ap.add_argument("--save_trades", type=int, default=0, help="0/1 (Trades pro Strategie als CSV ausgeben)")
    args = ap.parse_args()

    df, src = load_prices()
    sig_map = build_signals(df)

    combos = parse_strategies(args.strategies_csv)
    outdir = out_dir_for(args.strategies_csv)
    out_csv = os.path.join(outdir, "strategy_results_long.csv")

    print(f"[INFO] Preise: {os.path.relpath(src, ROOT)}  Zeilen: {len(df)}")
    print(f"[INFO] Strategien: {len(combos)}  → Output: {os.path.relpath(out_csv, ROOT)}")

    rows = []
    for idx, combo in enumerate(combos, start=1):
        res = backtest_long(df, sig_map, combo)
        rows.append({
            "id": idx,
            "k": len(combo),
            "Combination": str(combo),
            "num_trades": res["num_trades"],
            "wins": res["wins"],
            "losses": res["losses"],
            "winrate": res["winrate"],
            "roi": res["roi"]
        })

    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print(f"[DONE] Geschrieben: {os.path.relpath(out_csv, ROOT)}  Zeilen: {len(rows)}")

if __name__ == "__main__":
    main()
