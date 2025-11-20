#!/usr/bin/env python3
# tools/add_regime.py
# Erzeugt data/price_data_with_signals_regime.csv mit Regime-Spalten.
# Regime-Kriterien (anpassbar):
#   bull: close>ma200, ema50>ma200, roc>0, adx>=ADX_MIN
#   bear: close<ma200, ema50<ma200, roc<0, adx>=ADX_MIN

import argparse
import pandas as pd
from pathlib import Path

IN  = Path("data/price_data_with_signals.csv")
OUT = Path("data/price_data_with_signals_regime.csv")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--adx-min", type=float, default=15.0)  # vorher 20.0
    args = ap.parse_args()
    adx_min = args.adx_min

    if not IN.exists():
        raise FileNotFoundError(f"Missing: {IN}")

    df = pd.read_csv(IN)

    need = ["close", "ma200", "ema50", "roc", "adx"]
    for col in need:
        if col not in df.columns:
            raise KeyError(f"Required column missing: {col}")

    bull = (df["close"] > df["ma200"]) & (df["ema50"] > df["ma200"]) & (df["roc"] > 0) & (df["adx"] >= adx_min)
    bear = (df["close"] < df["ma200"]) & (df["ema50"] < df["ma200"]) & (df["roc"] < 0) & (df["adx"] >= adx_min)

    regime = pd.Series("side", index=df.index)
    regime = regime.mask(bull, "bull")
    regime = regime.mask(bear, "bear")

    regime_signal = pd.Series(0, index=df.index)
    regime_signal = regime_signal.mask(bull, 1)
    regime_signal = regime_signal.mask(bear, -1)

    df["market_regime"] = regime
    df["regime_signal"] = regime_signal.astype(int)
    df["regime_bull"]   = (regime == "bull").astype(int)
    df["regime_bear"]   = (regime == "bear").astype(int)

    df.to_csv(OUT, index=False)
    print(f"[INFO] Wrote: {OUT}  rows={len(df)}  adx_min={adx_min}")

if __name__ == "__main__":
    main()

