# -*- coding: utf-8 -*-
"""
Generate weighted signal combinations for k-of-N.
- Reads signals.available and signals.weights from configs/base_config.yaml
- Writes CSV with column 'Combination' containing a Python dict literal
- Streams to disk (no huge RAM usage)

Usage:
  python -m scripts.generate_combinations 4
  python -m scripts.generate_combinations 4 --max 250000
  python -m scripts.generate_combinations 6 --out data/strategies_6er_custom.csv
"""

import os, sys, csv, yaml, itertools, math
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")
DATA_DIR = os.path.join(ROOT, "data")

def load_cfg():
    with open(CFG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def parse_args():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.generate_combinations <k> [--max N] [--out path]")
        sys.exit(1)
    k = int(sys.argv[1])
    maxn = None
    out = None
    argv = sys.argv[2:]
    if "--max" in argv:
        i = argv.index("--max")
        maxn = int(argv[i+1])
    if "--out" in argv:
        i = argv.index("--out")
        out = argv[i+1]
    return k, maxn, out

def est_total(n_signals, k, n_weights):
    # total = C(n_signals, k) * (n_weights ** k)
    # beware huge counts
    combs = math.comb(n_signals, k)
    return combs * (n_weights ** k)

def main():
    k, maxn, out_override = parse_args()
    cfg = load_cfg()
    signals = list(cfg["signals"]["available"])
    weights = list(cfg["signals"]["weights"])

    if k < 2 or k > len(signals):
        raise SystemExit(f"k must be between 2 and {len(signals)} (got {k})")

    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = out_override or os.path.join(DATA_DIR, f"strategies_{k}er.csv")

    total_est = est_total(len(signals), k, len(weights))
    print(f"🧮 Erzeuge {k}-von-{len(signals)} mit {len(weights)} Gewichten → geschätzt: {total_est:,} Strategien")
    if maxn:
        print(f"⚠️ Limit aktiv: max {maxn:,} Strategien")

    # stream writer
    wrote = 0
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Combination"])

        for sigs in itertools.combinations(signals, k):
            for wts in itertools.product(weights, repeat=k):
                combo = {s: float(wt) for s, wt in zip(sigs, wts)}  # ensure plain float
                w.writerow([str(combo)])
                wrote += 1
                if maxn and wrote >= maxn:
                    break
            if maxn and wrote >= maxn:
                break

    print(f"✅ Geschrieben: {os.path.relpath(out_path, ROOT)}  | Strategien: {wrote:,}")

if __name__ == "__main__":
    main()
