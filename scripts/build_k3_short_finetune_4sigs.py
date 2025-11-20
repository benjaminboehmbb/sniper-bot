#!/usr/bin/env python3
# ASCII only: build_k3_short_finetune_4sigs.py

import json
import itertools
from pathlib import Path

import pandas as pd


def clip_two_dec(x: float) -> float:
    x = max(0.01, min(1.00, x))
    return round(x, 2)


def main():
    # Pfade
    results_csv = Path("results/hold_sweep/k3_short_mid_4sigs_0p1/strategy_results.csv")
    out_csv = Path("data/strategies_k3_short_finetune_top300_0p01.csv")

    if not results_csv.exists():
        raise SystemExit("Results CSV not found: %s" % results_csv)

    print("[INFO] Loading results:", results_csv)
    df = pd.read_csv(results_csv)

    # Spaltennamen vereinheitlichen
    cols_lower = {c.lower(): c for c in df.columns}
    if "roi" not in cols_lower or "combination" not in cols_lower:
        raise SystemExit("Expected columns 'roi' and 'Combination' not found in results CSV.")

    roi_col = cols_lower["roi"]
    comb_col = cols_lower["combination"]

    # Sortierung nach ROI absteigend
    df = df.dropna(subset=[roi_col, comb_col]).sort_values(roi_col, ascending=False)

    top_n = 300
    top = df.head(top_n).copy()
    print("[INFO] Selected top %d rows by %s." % (len(top), roi_col))

    # Feintuning-Gitter: +/- 0.02 in 0.01-Schritten
    deltas = [-0.02, -0.01, 0.00, 0.01, 0.02]

    rows = []
    for idx, row in top.iterrows():
        comb_json = row[comb_col]
        try:
            comb = json.loads(comb_json)
        except Exception as e:
            print("[WARN] Could not parse Combination at index %s: %s" % (idx, e))
            continue

        keys = list(comb.keys())
        if len(keys) != 3:
            # Sicherstellen, dass es wirklich 3er-Kombinationen sind
            print("[WARN] Skipping row %s: expected 3 keys, got %d" % (idx, len(keys)))
            continue

        base = [float(comb[k]) for k in keys]

        grids = []
        for w in base:
            grid = sorted({clip_two_dec(w + d) for d in deltas})
            grids.append(grid)

        for w0, w1, w2 in itertools.product(*grids):
            new_comb = {
                keys[0]: w0,
                keys[1]: w1,
                keys[2]: w2,
            }
            rows.append({"Combination": json.dumps(new_comb, sort_keys=True)})

    if not rows:
        raise SystemExit("No rows generated for finetune strategies.")

    out_df = pd.DataFrame(rows).drop_duplicates(subset=["Combination"])
    out_df.to_csv(out_csv, index=False)
    print("[INFO] Wrote %d unique combinations to %s" % (len(out_df), out_csv))


if __name__ == "__main__":
    main()
