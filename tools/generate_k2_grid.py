#!/usr/bin/env python3
# ASCII only
"""
Generate all k=2 signal pairs with full 0.1 weight grid (0.1..1.0) for each pair.
Usage:
  python tools/generate_k2_grid.py out.csv mfi rsi roc adx cci obv
Creates column: Combination  (JSON dict with two signals and weights)
"""
import sys, json
import pandas as pd
from itertools import combinations

def grid(step=0.1):
    vals = []
    v = 0.1
    while v <= 1.000001:
        vals.append(round(v, 1))
        v += step
    return vals

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/generate_k2_grid.py <out_csv> <signal1> <signal2> [more_signals...]")
        sys.exit(2)
    out_csv = sys.argv[1]
    sigs = sys.argv[2:]
    pairs = list(combinations(sigs, 2))
    vals = grid(0.1)
    rows = []
    for a,b in pairs:
        for wa in vals:
            for wb in vals:
                combo = {f"{a}_signal": wa, f"{b}_signal": wb}
                rows.append({"Combination": json.dumps(combo, sort_keys=True)})
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    print("pairs:", len(pairs), "rows:", len(rows), "->", out_csv)

if __name__ == "__main__":
    main()
