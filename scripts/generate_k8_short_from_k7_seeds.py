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
    if s is None:
        return {}
    s = str(s).strip()
    if not s:
        return {}
    try:
        d = json.loads(s)
        if not isinstance(d, dict):
            return {}
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
    keys = sorted(d.keys())
    out = {k: float(d[k]) for k in keys}
    return json.dumps(out, separators=(",", ":"), sort_keys=True)


def weights_grid(step: float):
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
    ap.add_argument("--k7-seeds-csv", required=True,
                    help="K7 seed pool CSV (must have Combination; may have roi).")
    ap.add_argument("--strategy-col", default="Combination",
                    help="Column holding the strategy JSON string (default: Combination).")
    ap.add_argument("--top-n", type=int, default=0,
                    help="If >0, take only top N seeds by ROI desc (if roi exists), else first N rows.")
    ap.add_argument("--random-frac", type=float, default=0.0,
                    help="Random exploration size as fraction of seed_expansion rows (default 0.0 for SHORT).")
    ap.add_argument("--weight-step", type=float, default=0.1,
                    help="Weight step for new 8th signal (default 0.1).")
    ap.add_argument("--seed", type=int, default=1337,
                    help="RNG seed for reproducibility.")
    ap.add_argument("--out-dir", default="data",
                    help="Output directory for strategy CSVs (default: data).")
    args = ap.parse_args()

    random.seed(args.seed)

    k7_path = args.k7_seeds_csv
    if not os.path.isfile(k7_path):
        print(f"[error] K7 seeds file not found: {k7_path}")
        sys.exit(1)

    df = pd.read_csv(k7_path)
    if args.strategy_col not in df.columns:
        print(f"[error] strategy_col '{args.strategy_col}' not found in K7 seeds file.")
        print("[info] columns:", list(df.columns))
        sys.exit(1)

    # Optional top-n selection
    if args.top_n and args.top_n > 0:
        if "roi" in df.columns:
            df = df.sort_values("roi", ascending=False).reset_index(drop=True)
        df = df.head(int(args.top_n)).copy().reset_index(drop=True)

    df["seed_rank"] = df.index + 1

    step = float(args.weight_step)
    grid = weights_grid(step)

    # Seed expansion: add one missing signal (8th) with weight in grid.
    out_rows = []
    seen = set()

    for _, row in df.iterrows():
        combo = parse_combo(row[args.strategy_col])
        if not combo:
            continue

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

    # Optional Random exploration (default 0.0 for SHORT)
    rand_target = 0
    if float(args.random_frac) > 0.0:
        rand_target = max(1, int(round(seed_rows * float(args.random_frac))))

    rand_rows = []
    attempts = 0
    max_attempts = max(1000, rand_target * 200)

    while len(rand_rows) < rand_target and attempts < max_attempts:
        attempts += 1
        sigs = random.sample(ALL_SIGNALS_12, 8)
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

    out_seed = os.path.join(args.out_dir, f"strategies_k8_short_from_k7_seeds_{ts}.csv")
    out_rand = os.path.join(args.out_dir, f"strategies_k8_short_random_{ts}.csv")
    out_merged = os.path.join(args.out_dir, f"strategies_k8_short_merged_{ts}.csv")

    seed_exp_df.to_csv(out_seed, index=False)
    rand_df.to_csv(out_rand, index=False)

    merged = pd.concat([seed_exp_df, rand_df], ignore_index=True)
    merged.to_csv(out_merged, index=False)

    print("[ok] Generated K8 short strategies")
    print("Seed source (K7 seeds):", k7_path)
    print("Seed expansion rows:", seed_rows)
    print("Random rows:", len(rand_df))
    print("Wrote:", out_seed)
    print("Wrote:", out_rand)
    print("Wrote:", out_merged)


if __name__ == "__main__":
    main()

