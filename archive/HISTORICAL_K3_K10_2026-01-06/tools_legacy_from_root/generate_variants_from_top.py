#!/usr/bin/env python3
# ASCII only
import sys, os, ast, json, math, argparse
import pandas as pd
import numpy as np
from itertools import product

def parse_combo(s):
    if isinstance(s, dict): return s
    try: return ast.literal_eval(str(s))
    except Exception: return {}

def clamp_round(x, step):
    # clamp to [0.1, 1.0] and round to step grid
    x = max(0.1, min(1.0, float(x)))
    q = round(x / step) * step
    # fix binary rounding artifacts
    q = float(np.round(q, 10))
    return q

def neighbor_grid(center, step, radius):
    # values: center +- n*step for n in [0..radius], clamped and rounded
    vals = set()
    for n in range(-radius, radius + 1):
        vals.add(clamp_round(center + n * step, step))
    return sorted(vals)

def full_grid(step):
    # full mesh from 0.1..1.0 with given step
    n = int(round((1.0 - 0.1) / step)) + 1
    return [clamp_round(0.1 + i * step, step) for i in range(n)]

def combo_key(combo):
    return json.dumps(combo, sort_keys=True)

def main():
    ap = argparse.ArgumentParser(description="Generate weight variants from top strategies.")
    ap.add_argument("input_csv", help="CSV with column 'Combination'")
    ap.add_argument("output_csv", help="Output CSV with column 'Combination'")
    ap.add_argument("--limit", type=int, default=200, help="How many top rows to use")
    ap.add_argument("--step", type=float, default=0.1, help="Weight step size (e.g., 0.1)")
    ap.add_argument("--radius", type=int, default=1, help="Neighborhood radius in steps (1 -> +-0.1, 2 -> +-0.2, ...)")
    ap.add_argument("--full-grid", type=int, default=0, help="If 1, generate full mesh per signal set")
    args = ap.parse_args()

    df = pd.read_csv(args.input_csv)
    if "Combination" not in df.columns:
        print("ERROR: Column 'Combination' missing")
        sys.exit(3)

    base = df["Combination"].head(args.limit).tolist()

    seen = set()
    out_rows = []

    # group by signal key-set to optionally build full meshes
    by_keys = {}
    for s in base:
        c = parse_combo(s)
        if not c: 
            continue
        kset = tuple(sorted(c.keys()))
        by_keys.setdefault(kset, []).append(c)

    for kset, combos in by_keys.items():
        if args.full_grid == 1:
            # Build full mesh for this signal set at given step
            axes = [full_grid(args.step) for _ in kset]
            for weights in product(*axes):
                combo = {k: clamp_round(w, args.step) for k, w in zip(kset, weights)}
                key = combo_key(combo)
                if key in seen: 
                    continue
                seen.add(key)
                out_rows.append({"Combination": key})
        else:
            # Local neighborhoods around each base combo
            for c in combos:
                grids = [neighbor_grid(float(c[k]), args.step, args.radius) for k in kset]
                for weights in product(*grids):
                    combo = {k: clamp_round(w, args.step) for k, w in zip(kset, weights)}
                    key = combo_key(combo)
                    if key in seen:
                        continue
                    seen.add(key)
                    out_rows.append({"Combination": key})

    out_df = pd.DataFrame(out_rows)
    out_df.to_csv(args.output_csv, index=False)
    print("Wrote", len(out_df), "variants to", args.output_csv)

if __name__ == "__main__":
    main()

