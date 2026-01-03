# scripts/generate_k6_long_from_k5_merge.py
# Purpose: K6 LONG candidate generation per strategy:
# - Exploitation: Seed-expansion from K5 "merge" pool (assumed to contain K5 combos with metrics)
# - Exploration: Random sampling ~2% of seed count (strictly separate file)
# - Pool-merge criterion for randoms: ROI > seed-P90 AND Winrate > seed-median (computed from K5 merge)
#
# Outputs (date-stamped):
# 1) seeds_k6_candidates_*.csv
# 2) random_k6_candidates_*.csv
# 3) merged_k6_pool_*.csv  (seeds + passing randoms only)

import argparse
import csv
import json
import math
import os
import random
from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd


SIGNALS_12 = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch"
]


def utc_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")


def parse_combination(val: str) -> Dict[str, float]:
    """
    Accepts:
      - JSON object string: {"rsi":0.2,...}
      - Python dict-like string: {'rsi': 0.2, ...}
    Returns a dict[str,float] with pure floats.
    """
    if not isinstance(val, str) or not val.strip():
        raise ValueError("Empty Combination")
    s = val.strip()
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return {str(k): float(v) for k, v in obj.items()}
    except Exception:
        pass

    # Fallback: python-literal-ish dict (single quotes)
    s2 = s.replace("'", '"')
    obj = json.loads(s2)
    if not isinstance(obj, dict):
        raise ValueError("Combination is not a dict")
    return {str(k): float(v) for k, v in obj.items()}


def dict_to_json(d: Dict[str, float]) -> str:
    # stable output (sorted keys), ensure normal Python floats
    return json.dumps({k: float(d[k]) for k in sorted(d.keys())}, separators=(",", ":"))


def ensure_k5_seed_row(row: pd.Series) -> Dict[str, float]:
    comb = parse_combination(row["Combination"])
    if len(comb) != 5:
        raise ValueError(f"Expected K5 combination, got K={len(comb)}")
    # sanity: signals known
    for k in comb.keys():
        if k not in SIGNALS_12:
            raise ValueError(f"Unknown signal in seed: {k}")
    return comb


def compute_seed_thresholds(k5_df: pd.DataFrame) -> Tuple[float, float]:
    # Requires columns roi, winrate
    if "roi" not in k5_df.columns or "winrate" not in k5_df.columns:
        raise ValueError("K5 merge CSV must contain columns: roi, winrate, Combination")
    roi_p90 = float(k5_df["roi"].quantile(0.90))
    winrate_median = float(k5_df["winrate"].median())
    return roi_p90, winrate_median


def build_k6_from_seed(seed_comb: Dict[str, float], add_signal: str, add_weight: float) -> Dict[str, float]:
    if add_signal in seed_comb:
        raise ValueError("add_signal already in seed")
    out = dict(seed_comb)
    out[add_signal] = float(add_weight)
    if len(out) != 6:
        raise ValueError("K6 build failed")
    return out


def generate_seed_expansion(
    k5_df: pd.DataFrame,
    max_seeds: int,
    weights: List[float],
    per_seed_max: int,
    rng: random.Random,
) -> pd.DataFrame:
    """
    For each top seed row, expand to K6 by adding one new signal (not present) with each weight.
    To control explosion, cap per seed by `per_seed_max` (randomly sample expansions if needed).
    """
    seeds = k5_df.head(max_seeds).copy()
    rows = []

    for i, row in seeds.iterrows():
        seed_comb = ensure_k5_seed_row(row)
        missing = [s for s in SIGNALS_12 if s not in seed_comb]

        expansions = []
        for sig in missing:
            for w in weights:
                expansions.append((sig, w))

        if per_seed_max > 0 and len(expansions) > per_seed_max:
            expansions = rng.sample(expansions, per_seed_max)

        for sig, w in expansions:
            k6 = build_k6_from_seed(seed_comb, sig, w)
            rows.append({
                "source": "seed_expansion",
                "seed_rank": int(seeds.index.get_loc(i)) + 1,  # 1-based within chosen seed slice
                "Combination": dict_to_json(k6),
            })

    return pd.DataFrame(rows)


def generate_random_k6(
    n: int,
    weights: List[float],
    rng: random.Random
) -> pd.DataFrame:
    """
    Random K6 candidates: choose 6 distinct signals, each with random weight from grid.
    """
    rows = []
    for _ in range(n):
        sigs = rng.sample(SIGNALS_12, 6)
        comb = {s: float(rng.choice(weights)) for s in sigs}
        rows.append({
            "source": "random",
            "seed_rank": "",
            "Combination": dict_to_json(comb),
        })
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k5-merge-csv", required=True, help="K5 LONG merged pool CSV with columns roi, winrate, Combination")
    ap.add_argument("--out-dir", default="data/k6_long", help="Output directory (will be created)")
    ap.add_argument("--seed-count", type=int, default=16000, help="How many top K5 seeds to expand")
    ap.add_argument("--random-frac", type=float, default=0.02, help="Random size as fraction of seed-count (~2%)")
    ap.add_argument("--per-seed-max", type=int, default=0,
                    help="Cap expansions per seed (0 = no cap). Use to control size if needed.")
    ap.add_argument("--weights-step", type=float, default=0.1, help="Weight grid step (default 0.1)")
    ap.add_argument("--weights-min", type=float, default=0.1, help="Min weight")
    ap.add_argument("--weights-max", type=float, default=1.0, help="Max weight")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility")
    ap.add_argument("--dedup", type=int, default=1, help="Deduplicate by Combination (1/0)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    stamp = utc_ts()
    rng = random.Random(args.seed)

    k5 = pd.read_csv(args.k5_merge_csv)
    for col in ["Combination", "roi", "winrate"]:
        if col not in k5.columns:
            raise ValueError(f"Missing column '{col}' in {args.k5_merge_csv}")

    # thresholds from the K5 merge distribution (seed distribution per your definition)
    roi_p90, winrate_median = compute_seed_thresholds(k5)

    # build weight grid
    step = float(args.weights_step)
    wmin = float(args.weights_min)
    wmax = float(args.weights_max)
    if step <= 0:
        raise ValueError("weights-step must be > 0")
    weights = []
    x = wmin
    # robust float stepping
    while x <= wmax + 1e-9:
        weights.append(round(x, 10))
        x += step

    seed_count = min(int(args.seed_count), len(k5))
    rand_n = int(math.ceil(seed_count * float(args.random_frac)))

    print(f"[{stamp} UTC] K5 merge rows: {len(k5)}")
    print(f"[{stamp} UTC] Using seed_count={seed_count}, random_n≈{rand_n} ({args.random_frac*100:.2f}%)")
    print(f"[{stamp} UTC] Merge thresholds (from K5 merge): roi_p90={roi_p90:.6f}, winrate_median={winrate_median:.6f}")
    print(f"[{stamp} UTC] Weight grid: {weights[0]}..{weights[-1]} step={step} (n={len(weights)})")

    seeds_k6 = generate_seed_expansion(
        k5_df=k5.sort_values(["roi", "winrate"], ascending=[False, False]),
        max_seeds=seed_count,
        weights=weights,
        per_seed_max=int(args.per_seed_max),
        rng=rng,
    )

    random_k6 = generate_random_k6(
        n=rand_n,
        weights=weights,
        rng=rng
    )

    if int(args.dedup) == 1:
        seeds_k6 = seeds_k6.drop_duplicates(subset=["Combination"]).reset_index(drop=True)
        random_k6 = random_k6.drop_duplicates(subset=["Combination"]).reset_index(drop=True)

    # NOTE: randoms are filtered only after they are evaluated in K6 analyzer.
    # Here we only generate candidate pools; merge criterion is for *selecting* randoms after evaluation.
    # To keep "sauberes Merge-Kriterium", we write the thresholds into a small metadata row-file too.
    meta_path = os.path.join(args.out_dir, f"meta_k6_long_generation_{stamp}.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "created_utc": stamp,
            "k5_merge_csv": args.k5_merge_csv,
            "seed_count": seed_count,
            "random_frac": float(args.random_frac),
            "random_n": len(random_k6),
            "roi_p90_from_k5_merge": roi_p90,
            "winrate_median_from_k5_merge": winrate_median,
            "weights": weights,
            "per_seed_max": int(args.per_seed_max),
            "rng_seed": int(args.seed),
            "signals": SIGNALS_12,
            "merge_rule_for_randoms_after_k6_eval": "roi > roi_p90_from_k5_merge AND winrate > winrate_median_from_k5_merge"
        }, f, indent=2)

    seeds_path = os.path.join(args.out_dir, f"seeds_k6_candidates_long_{stamp}.csv")
    rand_path = os.path.join(args.out_dir, f"random_k6_candidates_long_{stamp}.csv")

    seeds_k6.to_csv(seeds_path, index=False, quoting=csv.QUOTE_MINIMAL)
    random_k6.to_csv(rand_path, index=False, quoting=csv.QUOTE_MINIMAL)

    # merged candidate list for evaluation = seeds + all random candidates (randoms still tagged)
    merged = pd.concat([seeds_k6, random_k6], ignore_index=True)
    if int(args.dedup) == 1:
        merged = merged.drop_duplicates(subset=["Combination"]).reset_index(drop=True)

    merged_path = os.path.join(args.out_dir, f"candidates_k6_long_SEEDS_PLUS_RANDOM_{stamp}.csv")
    merged.to_csv(merged_path, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"[{stamp} UTC] Wrote:")
    print(f"  {seeds_path}  (rows={len(seeds_k6)})")
    print(f"  {rand_path}   (rows={len(random_k6)})")
    print(f"  {merged_path} (rows={len(merged)})")
    print(f"  {meta_path}")


if __name__ == "__main__":
    main()
