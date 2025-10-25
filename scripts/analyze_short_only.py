#!/usr/bin/env python3
"""
Analyze Short-Only – saubere eigenständige Version.
• Liest Strategien-CSV mit Spalte "Combination"
• Liest Kursdaten (1-Minuten-BTCUSDT)
• Berechnet alle Indikatoren (wie Long-Version)
• Handelt NUR Short (Entry combo < –0.5, Exit combo ≥ 0)
• Speichert Ergebnisse in results/<k>er/strategy_results_short.csv
"""

import os, sys, csv, ast, argparse
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES  = os.path.join(ROOT, "results")

# ---------- Hilfsfunktionen ----------
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
        for row in r:
            combo = ast.literal_eval(row["Combination"])
            if isinstance(combo, dict) and combo:
                rows.append(combo)
    return rows

def out_dir_for(path_strategies):
    base = os.path.basename(path_strategies).lower()
    kdir = "other"
    for tag in ["2er","3er","4er","5er","6er","7er","8er","9er","10er","11er","12er"]:
        if tag in base:
            kdir = tag
            break
    outdir = os.path.join(RES, kdir if kdir!="other" else "sanity")
    os.makedirs(outdir, exist_ok=True)
    return outdir

# ---------- Indikatoren ----------
def ema(s, span): return s.ewm(span=span, adjust=False).mean()
def sma(s, w): return s.rolling(w).mean()

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
    rsi14 = rsi(close, 14)
    mline, msignal, mhist = macd(close)
    ma200 = sma(close, 200)
    ema50 = ema(close, 50)
    ma, up, lo, bb_w = bollinger(close, 20, 2.0)
    st_k, st_d = stoch_osc(high, low, close)
    atr14 = atr(high, low, close)
    adx14 = adx_func(high, low, close)
    cci20 = cci_func(high, low, close)
    mfi14 = mfi_func(high, low, close, vol)
    obv = obv_func(close, vol)
    roc10 = roc_func(close)

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

# ---------- Backtest Short ----------
def backtest_short(df, sig_map, combo, thr_entry=-0.5, thr_exit=0.0, fee=0.0005, slip=0.0002):
    arr = sum(sig_map[n]*w for n,w in combo.items() if n in sig_map)
    position, entry = 0, None
    pnl = []
    for i, c in enumerate(df["close"]):
        if position == -1 and arr.iat[i] >= thr_exit:
            exit_price = c * (1 + slip)
            pnl.append((entry - exit_price) - fee*(entry + exit_price))
            position, entry = 0, None
        elif position == 0 and arr.iat[i] < thr_entry:
            entry, position = c * (1 - slip), -1
    if position == -1 and entry is not None:
        c = df["close"].iat[-1]
        exit_price = c * (1 + slip)
        pnl.append((entry - exit_price) - fee*(entry + exit_price))

    wins = sum(x > 0 for x in pnl)
    losses = len(pnl) - wins
    winrate = wins / max(1, wins + losses)
    roi = sum(pnl) / (df["close"].iat[0] + 1e-12)
    return {"num_trades": wins + losses, "wins": wins, "losses": losses,
            "winrate": round(winrate,6), "roi": round(roi,6)}

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strategies_csv")
    args = ap.parse_args()

    df, src = load_prices()
    sig_map = build_signals(df)
    combos = parse_strategies(args.strategies_csv)
    outdir = out_dir_for(args.strategies_csv)
    out_csv = os.path.join(outdir, "strategy_results_short.csv")

    print(f"[INFO] Preise: {os.path.relpath(src, ROOT)}  Zeilen: {len(df)}")
    print(f"[INFO] Strategien: {len(combos)}  → Output: {os.path.relpath(out_csv, ROOT)}")

    results = []
    for i, combo in enumerate(combos, 1):
        res = backtest_short(df, sig_map, combo)
        results.append({"id": i, "k": len(combo), "Combination": str(combo), **res})

    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"[DONE] Geschrieben: {os.path.relpath(out_csv, ROOT)}  Zeilen: {len(results)}")

if __name__ == "__main__":
    main()

