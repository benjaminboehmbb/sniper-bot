# scripts/generate_combinations_universal.py
# Erzeugt universelle Kombinationsdateien für k=2..12 Signale (Shards)
# Unterstützt beliebige Signalanzahl (z. B. 12) und Gewichtsraster
# Kompatibel mit analyze_template.py

import os, csv, argparse, yaml
from itertools import combinations, product
from math import comb

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")
OUT_DIR = os.path.join(ROOT, "data")

def load_signals_weights():
    """Lädt Signale und Gewichtsraster aus base_config.yaml"""
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    signals = cfg.get("signals", {}).get("available", [])
    weights = cfg.get("signals", {}).get("weights", [])
    if not signals or not weights:
        raise ValueError("Fehlende signals.available oder signals.weights in base_config.yaml")
    return signals, [float(w) for w in weights]

def ensure_out():
    os.makedirs(OUT_DIR, exist_ok=True)

def estimate_total(signals, weights, kmin, kmax):
    total = 0
    for k in range(kmin, kmax + 1):
        total += comb(len(signals), k) * (len(weights) ** k)
    return total

def stream_k(signals, weights, k, shard_size):
    """Erzeugt Shards mit Kombis der Ordnung k"""
    ensure_out()
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
        filename = os.path.join(OUT_DIR, f"strategies_universal_k{k}_part{part}.csv")
        f = open(filename, "w", newline="", encoding="utf-8")
        writer = csv.writer(f)
        writer.writerow(["Combination"])
        rows_in_part = 0
        part += 1
        return f, writer, filename

    f, writer, filename = open_new_part()

    for sig_subset in combinations(signals, k):
        for ws in product(weights, repeat=k):
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
    ap = argparse.ArgumentParser(description="Universeller Kombinationsgenerator (2–12er Shards)")
    ap.add_argument("--kmin", type=int, default=2)
    ap.add_argument("--kmax", type=int, default=12)
    ap.add_argument("--shard_size", type=int, default=200_000, help="max Zeilen pro Shard")
    args = ap.parse_args()

    signals, weights = load_signals_weights()
    kmin, kmax = args.kmin, args.kmax

    print(f"➡️ Signale ({len(signals)}): {signals}")
    print(f"➡️ Gewichtsraster: {weights}")
    print(f"➡️ Kombinationsbereich: {kmin}–{kmax}")

    total_est = estimate_total(signals, weights, kmin, kmax)
    print(f"🧮 Geschätzte Gesamtanzahl Strategien: {total_est:,}")
    ensure_out()

    grand_total = 0
    for k in range(kmin, kmax + 1):
        print(f"[k={k}] → Erzeuge Shards …")
        written_k = stream_k(signals, weights, k, args.shard_size)
        grand_total += written_k
        print(f"[k={k}] Geschrieben: {written_k:,}")

    print(f"✅ Fertig. Gesamt: {grand_total:,} Strategien über k={kmin}–{kmax}")

if __name__ == "__main__":
    main()
