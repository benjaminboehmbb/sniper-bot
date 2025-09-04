#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
add_volume_and_regime.py
Fügt Volumen-Features (OBV, MFI14, Volume-Spikes) und Marktphasen-Features (EMA200, EMA200-Slope10,
ret1, ret1-ZScore63, regime) zu einer OHLCV+Signals-CSV hinzu.

Nutzung (Beispiele):
  python add_volume_and_regime.py --in price_data_with_signals_fixed.csv --out price_data_with_features.csv
  python add_volume_and_regime.py --in price_data_with_signals.csv       --out price_data_with_features.csv

Erwartete Pflichtspalten:
  open_time, open, high, low, close, volume

Neue Spalten:
  obv, mfi14, vol_spike_ratio, vol_spike_flag, ema200, ema200_slope10, ret1, ret1_zscore63, regime
"""
import argparse
import sys
import numpy as np
import pandas as pd

REQ = ["open_time", "open", "high", "low", "close", "volume"]

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Eingabe-CSV")
    ap.add_argument("--out", dest="outp", required=True, help="Ausgabe-CSV")
    ap.add_argument("--sep", default=",")
    return ap.parse_args()

def ensure_cols(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        sys.exit(f"❌ Fehlende Pflichtspalten: {missing}")

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    # Vorzeichen der Preisänderung (0 bei NaN)
    sign = np.sign(close.diff().fillna(0.0))
    return (sign * volume).fillna(0.0).cumsum()

def mfi14(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    period = 14
    tp = (high + low + close) / 3.0
    mf = tp * volume
    pos = pd.Series(np.where(tp > tp.shift(1), mf, 0.0), index=tp.index)
    neg = pd.Series(np.where(tp < tp.shift(1), mf, 0.0), index=tp.index)
    pos_sum = pos.rolling(period, min_periods=period).sum()
    neg_sum = neg.rolling(period, min_periods=period).sum()
    with np.errstate(divide='ignore', invalid='ignore'):
        mfr = pos_sum / neg_sum
    mfi = 100 - (100 / (1 + mfr))
    return mfi.fillna(50.0)

def zscore(s: pd.Series, window: int) -> pd.Series:
    rolling = s.rolling(window, min_periods=window)
    mu = rolling.mean()
    sigma = rolling.std(ddof=0)
    z = (s - mu) / sigma
    return z

def add_features(df: pd.DataFrame) -> pd.DataFrame:
    # Sicherstellen, dass Zeit parsebar ist (optional, hilfreich)
    if "open_time" in df.columns:
        df["open_time"] = pd.to_datetime(df["open_time"], utc=True, errors="coerce")

    # 1) Volumen-Features
    df["obv"] = obv(df["close"], df["volume"])
    df["mfi14"] = mfi14(df["high"], df["low"], df["close"], df["volume"])

    # Volume-Spike: robust via Median-Fenster
    vol_med50 = df["volume"].rolling(50, min_periods=25).median()
    # Division durch 0 vermeiden: NaN -> 1.0 (neutral)
    df["vol_spike_ratio"] = (df["volume"] / vol_med50.replace(0, np.nan)).fillna(1.0)
    df["vol_spike_flag"] = (df["vol_spike_ratio"] >= 2.0).astype(int)

    # 2) Marktphasen-Features
    df["ema200"] = ema(df["close"], 200)
    df["ema200_slope10"] = df["ema200"] - df["ema200"].shift(10)

    df["ret1"] = df["close"].pct_change()
    df["ret1_zscore63"] = zscore(df["ret1"], 63).fillna(0.0)

    # Regime-Regeln:
    # - side: niedrige Volatilität (|z|<0.5) und flache EMA200 (|slope|<=0.0)
    # - bull: close>ema200 und ema200_slope10 > 0
    # - sonst: bear
    side_mask = (df["ret1_zscore63"].abs() < 0.5) & (df["ema200_slope10"].abs() <= 0.0)
    bull_mask = (~side_mask) & (df["close"] > df["ema200"]) & (df["ema200_slope10"] > 0)
    # Rest ist bear
    df["regime"] = np.where(side_mask, "side", np.where(bull_mask, "bull", "bear"))

    return df

def main():
    args = parse_args()
    print(f"📥 Lade: {args.inp}")
    df = pd.read_csv(args.inp, sep=args.sep)
    ensure_cols(df, REQ)

    print(f"Zeilen: {len(df):,} | Spalten: {len(df.columns)}")
    df = add_features(df)

    outp = args.outp
    df.to_csv(outp, index=False)
    print(f"✅ Features hinzugefügt und gespeichert: {outp} | Zeilen: {len(df):,} | Spalten: {len(df.columns)}")

if __name__ == "__main__":
    main()
