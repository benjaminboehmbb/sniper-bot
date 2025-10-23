# scripts/generate_combinations_short_refined.py
# Erzeugt eine gezielte Short-Feinmenge an Strategien:
# - nur Top-Signale: rsi, macd, stoch, ma200, bollinger
# - Gewichte aus feinem Raster (0.0 .. 1.0 in 0.1)
# - zufällige Stichprobe bis MAX_N
import os, argparse, random, yaml, pandas as pd
from itertools import combinations

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")
OUT_CSV = os.path.join(ROOT, "data", "strategies_short_refined.csv")

DEFAULT_SIGNALS = ["rsi","macd","stoch","ma200","bollinger"]
DEFAULT_WEIGHTS = [round(x/10,1) for x in range(0,11)]  # 0.0 .. 1.0

def load_seed():
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return int(cfg.get("general", {}).get("seed", 42))
    except Exception:
        return 42

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=5000, help="maximale Anzahl Strategien")
    ap.add_argument("--kmin", type=int, default=3, help="minimale Anzahl Signale pro Kombination")
    ap.add_argument("--kmax", type=int, default=5, help="maximale Anzahl Signale pro Kombination")
    ap.add_argument("--signals", type=str, default=",".join(DEFAULT_SIGNALS),
                    help="Kommagetrennte Signale (Standard: rsi,macd,stoch,ma200,bollinger)")
    ap.add_argument("--weights", type=str, default=",".join(map(str, DEFAULT_WEIGHTS)),
                    help="Kommagetrennte Gewichte (Standard: 0.0..1.0 in 0.1)")
    args = ap.parse_args()

    signals = [s.strip() for s in args.signals.split(",") if s.strip()]
    weights = [float(x) for x in args.weights.split(",") if x.strip()]

    seed = load_seed()
    random.seed(seed)

    # Alle Signal-Subsets vorbereiten (k in [kmin..kmax])
    subsets = []
    for k in range(max(1,args.kmin), min(len(signals),args.kmax)+1):
        subsets.extend(list(combinations(signals, k)))

    # Zufällig permutieren, damit Sampling fair ist
    random.shuffle(subsets)

    # Zufällige Gewichtszuteilungen samplen, bis Limit erreicht
    seen = set()
    combos = []
    target = args.max

    def sample_weights(sig_tuple):
        return {s: random.choice(weights) for s in sig_tuple}

    while len(combos) < target and subsets:
        sigs = random.choice(subsets)
        d = sample_weights(sigs)
        # Entferne harte Null-Kombinationen (alles 0) – bringt nichts
        if all(v == 0.0 for v in d.values()):
            continue
        key = tuple(sorted(d.items()))
        if key in seen:
            continue
        seen.add(key)
        combos.append(d)

    # In DataFrame schreiben (Spalte heißt "Combination", index = Reihenindex)
    df = pd.DataFrame({"Combination": [str(c) for c in combos]})
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    df.to_csv(OUT_CSV, index=True)  # index ist wichtig (wird später als 'index' gemerged)
    print(f"✅ Geschrieben: {os.path.relpath(OUT_CSV, ROOT)}  | Strategien: {len(df)}")

if __name__ == "__main__":
    main()
