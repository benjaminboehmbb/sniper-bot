#!/usr/bin/env python3
# scripts/generate_GS_k7_short_from_k6_seeds.py
#
# Generate K7 SHORT candidates from K6 SHORT seeds by structural expansion (unweighted).
# - Input seeds: strategies/GS/k6_short/strategies_GS_k6_short_TOP300_for_k7_seeds_<ts>.csv
# - Expansion: add 1 additional signal from the remaining pool
# - Dedup: canonical key of sorted signal names => unique K7 sets
# - Output: strategies/GS/k7_short/strategies_GS_k7_short_from_k6_TOP300_unweighted_<ts>.csv
#
# Note: Unique count <= C(12,7)=792 (upper bound)

import argparse
import os
import csv
from datetime import datetime

SIGNALS = [
    "rsi", "macd", "bollinger",
    "ma200", "stoch", "atr", "ema50",
    "adx", "cci", "mfi", "obv", "roc",
]

def safe_eval_dict(s: str) -> dict:
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict")
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out

def canonical_key(keys):
    return "+".join(sorted(keys))

def parse_args():
    ap = argparse.ArgumentParser(description="Generate GS K7 SHORT candidates from K6 SHORT seeds (unweighted, dedup).")
    ap.add_argument(
        "--seeds_csv",
        default="strategies/GS/k6_short/strategies_GS_k6_short_TOP300_for_k7_seeds_2026-01-09_17-22-21.csv",
        help="K6 SHORT seed file"
    )
    ap.add_argument("--out_dir", default="strategies/GS/k7_short")
    return ap.parse_args()

def main():
    args = parse_args()
    if not os.path.exists(args.seeds_csv):
        raise FileNotFoundError(args.seeds_csv)

    os.makedirs(args.out_dir, exist_ok=True)

    seeds = []
    with open(args.seeds_csv, "r", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        if "combination" not in rdr.fieldnames:
            raise RuntimeError(f"Missing 'combination' column. Have: {rdr.fieldnames}")
        for row in rdr:
            comb = safe_eval_dict(row["combination"])
            keys = list(comb.keys())
            if len(keys) != 6:
                raise RuntimeError(f"Seed is not K6: {row['combination']}")
            seeds.append(keys)

    uniq = {}
    for k6_keys in seeds:
        remaining = [s for s in SIGNALS if s not in k6_keys]
        for add in remaining:
            k7 = list(k6_keys) + [add]
            key = canonical_key(k7)
            if key not in uniq:
                uniq[key] = {k: 1.0 for k in sorted(k7)}

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(args.out_dir, f"strategies_GS_k7_short_from_k6_TOP{len(seeds)}_unweighted_{ts}.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["combination"])
        for key in sorted(uniq.keys()):
            w.writerow([str(uniq[key])])

    print("[ok] Seeds:", len(seeds), "from:", args.seeds_csv)
    print("[ok] Unique K7:", len(uniq), "(upper bound 792)")
    print("[ok] OUT:", out_path)

if __name__ == "__main__":
    main()
