#!/usr/bin/env python3
# Gate RANDOM strategies for K8-LONG using thresholds computed from SEED BASIS (UNION_DEDUP CSV)
# Criteria:
#   ROI > seed_roi_p90
#   Winrate > seed_winrate_median
#
# Inputs:
#   - Seed CSV (Union+Dedup) containing at least: roi, winrate, Combination
#   - RANDOM results CSV containing at least: roi, winrate, Combination
# Output:
#   - RANDOMPASS CSV (only passing strategies)

import argparse
import sys
from pathlib import Path

import pandas as pd


def die(msg: str):
    print(f"[error] {msg}")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Gate RANDOM K8-LONG strategies")
    ap.add_argument("--seed-csv", required=True, help="Union+Dedup seed CSV (has roi, winrate)")
    ap.add_argument("--random-results", required=True, help="RANDOM smoke results CSV")
    ap.add_argument("--out", required=True, help="Output RANDOMPASS CSV")
    args = ap.parse_args()

    seed_csv = Path(args.seed_csv)
    random_results = Path(args.random_results)
    out_path = Path(args.out)

    if not seed_csv.exists():
        die(f"Seed CSV not found: {seed_csv}")
    if not random_results.exists():
        die(f"Random results not found: {random_results}")

    seed = pd.read_csv(seed_csv)
    need_seed = {"roi", "winrate", "Combination"}
    if not need_seed.issubset(seed.columns):
        die(f"Seed CSV missing columns: {need_seed - set(seed.columns)}")

    seed["roi"] = pd.to_numeric(seed["roi"], errors="coerce")
    seed["winrate"] = pd.to_numeric(seed["winrate"], errors="coerce")
    seed = seed.dropna(subset=["roi", "winrate", "Combination"]).copy()

    if len(seed) < 10:
        die(f"Seed CSV too small after cleaning: {len(seed)} rows")

    seed_roi_p90 = float(seed["roi"].quantile(0.90))
    seed_wr_med = float(seed["winrate"].median())

    rnd = pd.read_csv(random_results)
    need_rnd = {"roi", "winrate", "Combination"}
    if not need_rnd.issubset(rnd.columns):
        die(f"Random results missing columns: {need_rnd - set(rnd.columns)}")

    rnd["roi"] = pd.to_numeric(rnd["roi"], errors="coerce")
    rnd["winrate"] = pd.to_numeric(rnd["winrate"], errors="coerce")
    rnd = rnd.dropna(subset=["roi", "winrate", "Combination"]).copy()

    passed = rnd[(rnd["roi"] > seed_roi_p90) & (rnd["winrate"] > seed_wr_med)].copy()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    passed.to_csv(out_path, index=False)

    print("[ok] RANDOM gate applied")
    print(f"[ok] Seed ROI p90      : {seed_roi_p90}")
    print(f"[ok] Seed Winrate med : {seed_wr_med}")
    print(f"[ok] RANDOM rows in   : {len(rnd)}")
    print(f"[ok] RANDOM rows pass : {len(passed)}")
    print(f"[ok] Wrote            : {out_path}")


if __name__ == "__main__":
    main()

