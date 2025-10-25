#!/usr/bin/env python3
"""
Erzeugt Strategiekombinationen für k=Kmin..Kmax aus einer Signalliste mit Gewichtungsraster.
Schreibt CSV-Shards mit Spalte 'Combination' (Dictionary-String), kompatibel mit deiner Pipeline.

Beispiele:
  python -m scripts.generate_combinations_universal --kmin 2 --kmax 12 --shard_size 200000
  python -m scripts.generate_combinations_universal --kmin 2 --kmax 4 --weights 0.1,0.3,0.6,0.9 --shard_size 150000

Wichtig:
- Spaltenname exakt: Combination (kein 'strategy')
- Keine tqdm, klare Prints
- Sharding, damit riesige Kandidatenmengen speicherarm erzeugt werden
- Deterministische Reihenfolge
"""

import os
import sys
import csv
import math
import argparse
import itertools
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_SIGNALS = [
    "rsi", "macd", "bollinger", "ma200", "stoch", "atr",
    "ema50", "adx", "cci", "mfi", "obv", "roc"
]

def parse_weights(s: str):
    if not s:
        # Standardraster 0.1..1.0 (exhaustive)
        return [round(x/10, 1) for x in range(1, 11)]
    ws = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            v = float(part)
        except ValueError:
            raise ValueError(f"Ungültiges Gewicht: {part}")
        if v <= 0.0 or v > 1.0:
            raise ValueError(f"Gewicht außerhalb (0,1]: {v}")
        ws.append(round(v, 10))
    return ws

def combinations_count(n, k):
    # nCk
    if k < 0 or k > n:
        return 0
    k = min(k, n-k)
    if k == 0:
        return 1
    numer = 1
    denom = 1
    for i in range(1, k+1):
        numer *= (n - (k - i))
        denom *= i
    return numer // denom

def estimate_total(signals, kmin, kmax, weight_grid):
    n = len(signals)
    total = 0
    for k in range(kmin, kmax+1):
        total += combinations_count(n, k) * (len(weight_grid) ** k)
    return total

def shard_writer(basepath_prefix, k, shard_idx):
    # data/strategies_k{K}_shard{N}.csv
    fn = f"{basepath_prefix}_k{k}_shard{shard_idx}.csv"
    fpath = os.path.join(DATA_DIR, fn)
    f = open(fpath, "w", newline="", encoding="utf-8")
    w = csv.writer(f)
    w.writerow(["Combination"])  # exakt so
    return f, w, fpath

def format_combination_dict(sig_names, weights):
    # Dictionary-String im gewünschten Format: "{'rsi': 0.5, 'macd': 0.3, ...}"
    items = []
    for s, w in zip(sig_names, weights):
        # floats kompakt, max 10 Nachkommastellen
        items.append(f"'{s}': {w:.10g}")
    return "{"+", ".join(items)+"}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signals", type=str, default=",".join(DEFAULT_SIGNALS),
                    help="Kommagetrennte Liste der Signalnamen")
    ap.add_argument("--kmin", type=int, default=2)
    ap.add_argument("--kmax", type=int, default=12)
    ap.add_argument("--weights", type=str, default="", help="Gewichte, z.B. '0.1,0.3,0.6,0.9' (leer = 0.1..1.0)")
    ap.add_argument("--shard_size", type=int, default=200000, help="Zeilen pro CSV-Shard")
    ap.add_argument("--prefix", type=str, default="strategies",
                    help="Dateipräfix der Ausgabedateien (Standard: strategies)")
    args = ap.parse_args()

    signals = [s.strip() for s in args.signals.split(",") if s.strip()]
    if len(signals) < 2:
        print("❌ Mindestens 2 Signale erforderlich.")
        sys.exit(1)
    if args.kmin < 2 or args.kmin > args.kmax:
        print("❌ Ungültiger Bereich: kmin..kmax")
        sys.exit(1)
    weight_grid = parse_weights(args.weights)
    if len(weight_grid) == 0:
        print("❌ Keine Gewichte definiert.")
        sys.exit(1)

    print(f"➡️ Signale ({len(signals)}): {signals}")
    print(f"➡️ Gewichtsraster: {weight_grid}")
    print(f"➡️ Kombinationsbereich: {args.kmin}–{args.kmax}")

    total_est = estimate_total(signals, args.kmin, args.kmax, weight_grid)
    print(f"🧮 Geschätzte Gesamtanzahl Strategien: {total_est:,}")

    baseprefix = args.prefix.strip()
    if not baseprefix:
        baseprefix = "strategies"
    baseprefix = baseprefix.replace(" ", "_")

    start_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏱ Start: {start_ts}")
    written_total = 0

    # Für jede K-Kombination: alle Signalkombis und alle Gewichtskreuze
    for k in range(args.kmin, args.kmax+1):
        comb_count = combinations_count(len(signals), k)
        print(f"[k={k}] → {comb_count} Signal-Kombinationen")

        # Shard-Writer vorbereiten
        shard_idx = 1
        rows_in_shard = 0
        f, w, current_path = shard_writer(baseprefix, k, shard_idx)
        print(f"[k={k}] Schreibe in: {os.path.basename(current_path)} (shard_size={args.shard_size})")

        # alle Signal-Kombinationen
        for sig_tuple in itertools.combinations(signals, k):
            # alle Gewichtskartesierprodukte
            for weights in itertools.product(weight_grid, repeat=k):
                row_str = format_combination_dict(sig_tuple, weights)
                w.writerow([row_str])
                rows_in_shard += 1
                written_total += 1

                if rows_in_shard >= args.shard_size:
                    f.close()
                    print(f"[k={k}] Shard abgeschlossen: {os.path.basename(current_path)}  (+{rows_in_shard} Zeilen)")
                    shard_idx += 1
                    rows_in_shard = 0
                    f, w, current_path = shard_writer(baseprefix, k, shard_idx)

        # Rest schließen
        if rows_in_shard > 0:
            f.close()
            print(f"[k={k}] Shard abgeschlossen: {os.path.basename(current_path)}  (+{rows_in_shard} Zeilen)")
        else:
            # Leere Datei nicht liegen lassen
            try:
                f.close()
                os.remove(current_path)
            except Exception:
                pass

        print(f"[k={k}] ✅ Fertig.")

    end_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"✅ Gesamt fertig. Geschrieben: {written_total:,} Zeilen")
    print(f"⏱ Ende: {end_ts}")

if __name__ == "__main__":
    main()

