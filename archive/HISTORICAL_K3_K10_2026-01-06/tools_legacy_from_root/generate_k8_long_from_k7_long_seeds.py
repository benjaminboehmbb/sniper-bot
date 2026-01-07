#!/usr/bin/env python3
# Generate K8-LONG candidate strategies from a seed list (K7-LONG-derived).
# Output:
#  - SEEDS expansion (dominant)
#  - RANDOM (2%) strictly separate
#  - POOL = concat(SEEDS, RANDOM) with source column, dedup by Combination
#
# Assumptions:
# - Input seed CSV has "Combination" (JSON/dict string) and metrics columns (roi, winrate, num_trades).
# - Signal universe is fixed to the 12 signals.
# - Weight step is 0.1, weights in [0.1..1.0].
#
# NOTE: This script does NOT do gate-merge by ROI/winrate (that happens after we analyze RANDOM).
# It only generates candidates for the next analyze step.

import argparse
import json
import os
import random
import sys
from datetime import datetime, timezone
from itertools import combinations
from typing import Dict, List, Tuple

import pandas as pd


SIGNALS_12 = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch"
]


def die(msg: str, code: int = 1) -> None:
    print(f"[error] {msg}")
    sys.exit(code)


def safe_mkdir(path: str) -> None:
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def parse_combo(s: str) -> Dict[str, float]:
    # Accept JSON-like or Python-dict-like strings.
    s = s.strip()
    try:
        # First try JSON
        if s.startswith("{") and '"' in s:
            d = json.loads(s)
            return {str(k): float(v) for k, v in d.items()}
    except Exception:
        pass
    try:
        # Fallback: python literal dict
        import ast
        d = ast.literal_eval(s)
        if not isinstance(d, dict):
            raise ValueError("Combination is not a dict")
        return {str(k): float(v) for k, v in d.items()}
    except Exception as e:
        raise ValueError(f"Cannot parse Combination: {e}")


def combo_to_str(d: Dict[str, float]) -> str:
    # Canonical JSON with sorted keys, stable floats.
    # Ensure one decimal for weights (0.1 steps).
    out = {k: round(float(v), 1) for k, v in d.items()}
    return json.dumps(out, sort_keys=True, separators=(",", ":"))


def round1(x: float) -> float:
    return round(float(x) + 1e-12, 1)


def generate_expansions_for_seed(seed: Dict[str, float], weights: List[float]) -> List[Dict[str, float]]:
    # K8 from K7: add one new signal not in seed, choose its weight.
    # Keep existing weights unchanged.
    existing = set(seed.keys())
    missing = [s for s in SIGNALS_12 if s not in existing]
    out = []
    for add_sig in missing:
        for w in weights:
            d = dict(seed)
            d[add_sig] = w
            out.append(d)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed-csv", required=True, help="Union+Dedup seed CSV from build_k8_long_seed_pools.py")
    ap.add_argument("--outdir", required=True, help="Output dir, e.g. results/k8_long")
    ap.add_argument("--weight-step", type=float, default=0.1, help="Weight step (default 0.1)")
    ap.add_argument("--min-w", type=float, default=0.1, help="Min weight (default 0.1)")
    ap.add_argument("--max-w", type=float, default=1.0, help="Max weight (default 1.0)")
    ap.add_argument("--random-frac", type=float, default=0.02, help="Random fraction vs SEED expansion count (default 0.02)")
    ap.add_argument("--random-seed", type=int, default=42, help="PRNG seed for reproducibility")
    args = ap.parse_args()

    seed_csv = args.seed_csv
    outdir = args.outdir
    safe_mkdir(outdir)

    if not os.path.exists(seed_csv):
        die(f"Seed CSV not found: {seed_csv}")

    df = pd.read_csv(seed_csv)
    if "Combination" not in df.columns:
        die(f"Missing column 'Combination' in seed CSV. Columns: {list(df.columns)}")

    # Parse seed combinations
    seeds: List[Dict[str, float]] = []
    bad = 0
    for s in df["Combination"].astype(str).tolist():
        try:
            d = parse_combo(s)
            # Keep only valid signals, ignore extras (but warn)
            d2 = {k: round1(v) for k, v in d.items() if k in SIGNALS_12}
            if len(d2) < 1:
                raise ValueError("empty after filtering to SIGNALS_12")
            seeds.append(d2)
        except Exception:
            bad += 1

    if not seeds:
        die("No valid seeds parsed from seed CSV.")
    if bad > 0:
        print(f"[warn] Failed to parse {bad} seed rows (skipped).")

    # Weight grid
    step = args.weight_step
    w = args.min_w
    weights = []
    while w <= args.max_w + 1e-9:
        weights.append(round1(w))
        w += step
    if not weights:
        die("Weight grid empty. Check --min-w/--max-w/--weight-step.")

    # Generate SEED expansions
    print(f"[ok] Seeds parsed: {len(seeds)}")
    print(f"[ok] Weight grid: {weights[0]}..{weights[-1]} step={step} (n={len(weights)})")

    exp_rows: List[Tuple[str, str]] = []  # (Combination, source)
    for d in seeds:
        # K7 -> K8 expansions (add one new signal)
        exps = generate_expansions_for_seed(d, weights)
        for e in exps:
            exp_rows.append((combo_to_str(e), "seed_expansion"))

    df_seeds = pd.DataFrame(exp_rows, columns=["Combination", "source"])
    df_seeds = df_seeds.drop_duplicates(subset=["Combination"]).copy()

    seed_count = len(df_seeds)
    if seed_count < 1:
        die("Seed expansion produced 0 rows (unexpected).")

    # RANDOM: sample from full K8 universe at a small fraction of seed_count.
    # K8 universe size: choose 8 signals out of 12 and assign weights.
    # We do uniform sampling over (signal-set, weights) by simple random construction:
    # - pick 8 distinct signals uniformly
    # - pick 8 weights uniformly from grid (with replacement allowed)
    # This is not perfectly uniform over all combinations, but sufficient for blindspot detection.
    rand_n = max(1, int(round(seed_count * args.random_frac)))
    random.seed(args.random_seed)

    rand_rows = []
    for _ in range(rand_n):
        sigs = random.sample(SIGNALS_12, 8)
        d = {s: random.choice(weights) for s in sigs}
        rand_rows.append((combo_to_str(d), "random"))

    df_rand = pd.DataFrame(rand_rows, columns=["Combination", "source"])
    df_rand = df_rand.drop_duplicates(subset=["Combination"]).copy()

    # POOL
    df_pool = pd.concat([df_seeds, df_rand], ignore_index=True)
    df_pool = df_pool.drop_duplicates(subset=["Combination"], keep="first").copy()

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    seeds_path = os.path.join(outdir, f"strategies_k8_long_SEEDS_{ts}.csv")
    rand_path = os.path.join(outdir, f"strategies_k8_long_RANDOM_{ts}.csv")
    pool_path = os.path.join(outdir, f"strategies_k8_long_POOL_{ts}.csv")
    summary_path = os.path.join(outdir, f"strategies_k8_long_GENERATE_SUMMARY_{ts}.txt")

    df_seeds.to_csv(seeds_path, index=False)
    df_rand.to_csv(rand_path, index=False)
    df_pool.to_csv(pool_path, index=False)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("K8-LONG generation summary\n")
        f.write(f"seed_input_csv: {seed_csv}\n")
        f.write(f"seed_input_rows: {len(df)}\n")
        f.write(f"seed_parsed_ok: {len(seeds)}\n")
        f.write(f"seed_parsed_bad: {bad}\n")
        f.write(f"weight_grid_n: {len(weights)}\n")
        f.write(f"weight_grid_min: {weights[0]}\n")
        f.write(f"weight_grid_max: {weights[-1]}\n")
        f.write(f"seed_expansion_rows: {len(df_seeds)}\n")
        f.write(f"random_target_frac: {args.random_frac}\n")
        f.write(f"random_rows: {len(df_rand)}\n")
        f.write(f"pool_rows: {len(df_pool)}\n")
        f.write("\nOutputs:\n")
        f.write(f"seeds_csv: {seeds_path}\n")
        f.write(f"random_csv: {rand_path}\n")
        f.write(f"pool_csv: {pool_path}\n")

    print("[ok] Wrote K8-LONG candidate sets:")
    print(f"  SEEDS:  {seeds_path} (rows={len(df_seeds)})")
    print(f"  RANDOM: {rand_path} (rows={len(df_rand)})")
    print(f"  POOL:   {pool_path} (rows={len(df_pool)})")
    print(f"[ok] Summary: {summary_path}")
    print("[note] Next step: analyze RANDOM first (smoke), then gate-merge RANDOMPASS into SEEDS for final pool.")


if __name__ == "__main__":
    main()
