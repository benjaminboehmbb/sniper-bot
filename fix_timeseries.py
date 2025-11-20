#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fix_timeseries.py
Bereinigt duplizierte Zeitstempel in OHLCV+Signals CSVs.
Standard: Aggregation je Zeitstempel (open=first, high=max, low=min, close=last, volume=sum, andere Spalten=first).

Nutzung (Beispiel):
  python fix_timeseries.py --in price_data_with_signals.csv --out price_data_with_signals_fixed.csv
Optionen:
  --mode aggregate  (Standard, empfehlenswert)
  --mode drop       (behält die erste Zeile je Zeitstempel, verwirft den Rest)

Hinweise:
- Erwartet Spalten: open_time, open, high, low, close, volume (weitere Spalten werden beibehalten).
- Sortiert nach open_time und prüft Basis-Qualität.
"""

import argparse
import pandas as pd
import numpy as np
import sys

REQ = ["open_time", "open", "high", "low", "close", "volume"]

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--in",  dest="inp",  required=True, help="Eingabe-CSV")
    p.add_argument("--out", dest="outp", required=True, help="Output-CSV")
    p.add_argument("--mode", choices=["aggregate","drop"], default="aggregate")
    p.add_argument("--sep", default=",")
    return p.parse_args()

def ensure_cols(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        sys.exit(f"❌ Fehlende Pflichtspalten: {missing}")

def main():
    args = parse_args()
    print(f"📥 Lade: {args.inp}")
    df = pd.read_csv(args.inp, sep=args.sep)
    ensure_cols(df, REQ)

    # Zeitspalte parsen und sortieren
    df["open_time"] = pd.to_datetime(df["open_time"], utc=True, errors="coerce")
    before = len(df)
    bad_time = df["open_time"].isna().sum()
    if bad_time > 0:
        print(f"⚠ Ungültige Zeitwerte: {bad_time} → werden verworfen")
        df = df.dropna(subset=["open_time"])

    df = df.sort_values("open_time")
    dup = df["open_time"].duplicated().sum()
    print(f"🔎 Duplizierte Zeitstempel: {dup}")

    if dup == 0 and bad_time == 0:
        print("✅ Keine Duplikate. Speichere 1:1 Kopie.")
        df.to_csv(args.outp, index=False)
        print(f"💾 Gespeichert: {args.outp} | Zeilen: {len(df):,}")
        return

    if args.mode == "drop":
        # simple Variante: erste pro Timestamp behalten
        df_fixed = df.drop_duplicates(subset=["open_time"], keep="first")
    else:
        # robuste Aggregation je Zeitstempel
        agg = {
            "open":  "first",
            "high":  "max",
            "low":   "min",
            "close": "last",
            "volume":"sum",
        }
        # alle übrigen Spalten als 'first' übernehmen
        for c in df.columns:
            if c in agg or c == "open_time":
                continue
            # numerisch oder nicht: first ist stabil/neutral
            agg[c] = "first"

        df_fixed = df.groupby("open_time", sort=True).agg(agg).reset_index()

    after = len(df_fixed)
    removed = before - after
    # Basis-Prüfungen
    ohlc_bad = ((df_fixed["high"] < df_fixed["low"]) |
                (df_fixed["high"] < df_fixed["open"]) |
                (df_fixed["high"] < df_fixed["close"])|
                (df_fixed["low"]  > df_fixed["open"]) |
                (df_fixed["low"]  > df_fixed["close"])).sum()

    print(f"✅ Bereinigung fertig: {before:,} → {after:,} Zeilen (−{removed:,}) | Mode: {args.mode}")
    if ohlc_bad > 0:
        print(f"⚠ Unplausible OHLC-Zeilen nach Aggregation: {ohlc_bad} (bitte prüfen)")
    else:
        print("✅ OHLC plausibel.")

    df_fixed.to_csv(args.outp, index=False)
    print(f"💾 Gespeichert: {args.outp}")

if __name__ == "__main__":
    main()
