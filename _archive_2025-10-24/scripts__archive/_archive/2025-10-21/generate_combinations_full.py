# scripts/generate_combinations_full.py
# Exhaustive Combinations Generator (streams to multiple CSV shards)
# - Signals: frei wählbar
# - k-range: z.B. 2..7
# - Weights: z.B. 0.0..1.0 in 0.1
# - Output: data/strategies_full_k{K}_part{P}.csv (Shards, um RAM/Dateigröße zu kontrollieren)

import os, csv, argparse, yaml, math
from itertools import combinations, product

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")
OUT_DIR = os.path.join(ROOT, "data")

def load_seed():
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return int(cfg.get("general", {}).get("seed", 42))
    except Exception:
        return 42

def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)

def count_total(signals, weights, kmin, kmax):
    # Sum_{k=kmin..kmax} C(n,k) * (len(weights))^k
    n = len(signals)
    from math import comb
    W = len(weights)
    total = 0
    for k in range(kmin, kmax+1):
        total += comb(n, k) * (W ** k)
    return total

def stream_k(signals, weights, k, shard_size):
    """Erzeugt (filename, count_written) für jede Shard-Datei von genauem k."""
    from math import comb
    ensure_out()
    n = len(signals)
    combos_written_total = 0
    part = 1
    rows_in_part = 0
    writer = None
    f = None
    filename = None

    def open_new_part():
        nonlocal writer, f, filename, rows_in_part, part
        if f:
            f.close()
        filename = os.path.join(OUT_DIR, f"strategies_full_k{k}_part{part}.csv")
        f = open(filename, "w", newline="", encoding="utf-8")
        writer = csv.writer(f)
        writer.writerow(["Combination"])  # einspaltig, index = Zeilennummer beim Analyzer-Merge
        rows_in_part = 0
        part += 1
        return f, writer, filename

    f, writer, filename = open_new_part()

    for sig_subset in combinations(signals, k):
        # Für dieses Subset alle Gewichtskuples (W^k) durchgehen
        for ws in product(weights, repeat=k):
            # skip all-zero
            if all(w == 0.0 for w in ws):
                continue
            combo = "{" + ", ".join(f"'{s}': {w}" for s, w in zip(sig_subset, ws)) + "}"
            writer.writerow([combo])
            rows_in_part += 1
            combos_written_total += 1
            if rows_in_part >= shard_size:
                f, writer, filename = open_new_part()

    if f:
        f.close()
    return combos_written_total

def main():
    ap = argparse.ArgumentParser(description="Exhaustive strategy combinations (streamed to shards).")
    ap.add_argument("--signals", type=str, default="rsi,macd,stoch,ma200,bollinger,atr,ema50",
                    help="Kommagetrennte Signale aus der CSV")
    ap.add_argument("--weights", type=str, default="0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0",
                    help="Kommagetrennte Gewichte")
    ap.add_argument("--kmin", type=int, default=2)
    ap.add_argument("--kmax", type=int, default=7)
    ap.add_argument("--shard_size", type=int, default=200_000,
                    help="max Zeilen pro CSV (Shard)")
    args = ap.parse_args()

    signals = [s.strip() for s in args.signals.split(",") if s.strip()]
    weights = [float(x) for x in args.weights.split(",") if x.strip()]
    kmin = max(1, args.kmin)
    kmax = min(len(signals), args.kmax)

    total_est = count_total(signals, weights, kmin, kmax)
    print(f"🧮 Geschätzte Gesamtanzahl Kombinationen: {total_est:,}")
    print(f"➡️  Signale: {signals}")
    print(f"➡️  k-Bereich: {kmin}..{kmax}")
    print(f"➡️  Gewichte: {weights}")
    print(f"➡️  Shard-Größe: {args.shard_size:,} Zeilen pro Datei")
    ensure_out()

    grand_total = 0
    for k in range(kmin, kmax+1):
        print(f"[k={k}] Starte Generierung …")
        written_k = stream_k(signals, weights, k, args.shard_size)
        grand_total += written_k
        print(f"[k={k}] Geschrieben: {written_k:,} Kombinationen (über mehrere Shards)")

    print(f"✅ Fertig. Insgesamt geschrieben: {grand_total:,} Kombinationen.")

if __name__ == "__main__":
    main()
