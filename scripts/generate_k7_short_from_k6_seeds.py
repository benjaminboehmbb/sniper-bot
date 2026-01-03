#!/usr/bin/env python3
# ASCII-only script. No emojis, no unicode symbols.

import argparse
import json
import os
import random
import sys
from datetime import datetime

import pandas as pd


ALL_SIGNALS_12 = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch"
]


def utc_ts():
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")


def parse_combo(s: str) -> dict:
    # Input is like: {"adx":0.2,"ema50":0.7,...}
    if s is None:
        return {}
    s = str(s).strip()
    if not s:
        return {}
    try:
        d = json.loads(s)
        if not isinstance(d, dict):
            return {}
        # ensure python floats
        out = {}
        for k, v in d.items():
            try:
                out[str(k)] = float(v)
            except Exception:
                pass
        return out
    except Exception:
        return {}


def combo_to_json(d: dict) -> str:
    # stable key order for reproducibility
    keys = sorted(d.keys())
    out = {k: float(d[k]) for k in keys}
    return json.dumps(out, separators=(",", ":"), sort_keys=True)


def weights_grid(step: float):
    # e.g. 0.1 -> 0.1..1.0
    n = int(round(1.0 / step))
    vals = []
    for i in range(1, n + 1):
        vals.append(round(i * step, 10))
    return vals


def ensure_dir(p):
    if p and not os.path.isdir(p):
        os.makedirs(p, exist_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k6-merged-results", required=True,
                    help="K6 short merged results CSV (seed source).")
    ap.add_argument("--strategy-col", default="Combination",
                    help="Column holding the strategy JSON string (default: Combination).")
    ap.add_argument("--top-n", type=int, default=2000,
                    help="How many top K6 seeds to expand (by ROI desc).")
    ap.add_argument("--random-frac", type=float, default=0.02,
                    help="Random exploration size as fraction of seed_expansion rows (default 0.02 = 2%%).")
    ap.add_argument("--weight-step", type=float, default=0.1,
                    help="Weight step for new 7th signal (default 0.1).")
    ap.add_argument("--seed", type=int, default=1337,
                    help="RNG seed for reproducibility.")
    ap.add_argument("--out-dir", default="data",
                    help="Output directory for strategy CSVs (default: data).")
    args = ap.parse_args()

    random.seed(args.seed)

    k6_path = args.k6_merged_results
    if not os.path.isfile(k6_path):
        print(f"[error] K6 merged results not found: {k6_path}")
        sys.exit(1)

    df = pd.read_csv(k6_path)
    if args.strategy_col not in df.columns:
        print(f"[error] strategy_col '{args.strategy_col}' not found in K6 file.")
        print("[info] columns:", list(df.columns))
        sys.exit(1)

    if "roi" not in df.columns:
        print("[error] K6 file has no 'roi' column. This must be an analyze results CSV.")
        sys.exit(1)

    # sort by ROI desc
    df = df.sort_values("roi", ascending=False).reset_index(drop=True)
    seeds = df.head(args.top_n).copy()
    seeds["seed_rank"] = seeds.index + 1

    step = float(args.weight_step)
    grid = weights_grid(step)

    # Seed expansion: add one missing signal (7th) with weight in grid.
    # Keep existing weights as-is (no jitter here; pure expansion like earlier K-runs).
    out_rows = []
    seen = set()

    for i, row in seeds.iterrows():
        combo = parse_combo(row[args.strategy_col])
        if len(combo) != 6:
            # If K6 is not exactly 6 signals, still expand by adding one new signal not present.
            pass

        present = set(combo.keys())
        missing = [s for s in ALL_SIGNALS_12 if s not in present]
        if not missing:
            continue

        for sig in missing:
            for w in grid:
                new_combo = dict(combo)
                new_combo[sig] = float(w)
                cjson = combo_to_json(new_combo)
                if cjson in seen:
                    continue
                seen.add(cjson)
                out_rows.append({
                    "Combination": cjson,
                    "source": "seed_expansion",
                    "seed_rank": int(row["seed_rank"]),
                })

    seed_exp_df = pd.DataFrame(out_rows)
    seed_rows = len(seed_exp_df)
    if seed_rows == 0:
        print("[error] seed_expansion produced 0 rows. Check input seeds and signals.")
        sys.exit(1)

    # Random exploration: generate random 7-signal combos with random weights in grid.
    rand_target = max(1, int(round(seed_rows * float(args.random_frac))))
    rand_rows = []
    attempts = 0
    max_attempts = rand_target * 200  # enough to avoid duplicates in practice

    while len(rand_rows) < rand_target and attempts < max_attempts:
        attempts += 1
        sigs = random.sample(ALL_SIGNALS_12, 7)
        d = {}
        for s in sigs:
            d[s] = float(random.choice(grid))
        cjson = combo_to_json(d)
        if cjson in seen:
            continue
        seen.add(cjson)
        rand_rows.append({"Combination": cjson, "source": "random", "seed_rank": 0})

    rand_df = pd.DataFrame(rand_rows)

    ts = utc_ts()
    ensure_dir(args.out_dir)

    out_seed = os.path.join(args.out_dir, f"strategies_k7_short_from_k6_seeds_{ts}.csv")
    out_rand = os.path.join(args.out_dir, f"strategies_k7_short_random_{ts}.csv")
    out_merged = os.path.join(args.out_dir, f"strategies_k7_short_merged_{ts}.csv")

    seed_exp_df.to_csv(out_seed, index=False)
    rand_df.to_csv(out_rand, index=False)

    merged = pd.concat([seed_exp_df, rand_df], ignore_index=True)
    merged.to_csv(out_merged, index=False)

    print("[ok] Generated K7 short strategies")
    print("Seed source (K6 merged):", k6_path)
    print("Seed expansion rows:", seed_rows)
    print("Random rows:", len(rand_df))
    print("Wrote:", out_seed)
    print("Wrote:", out_rand)
    print("Wrote:", out_merged)


if __name__ == "__main__":
    main()
