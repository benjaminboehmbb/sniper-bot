# generate_k5_random_long.py
# Generate random K5 LONG combinations (separate from seed-based generation).
# Output: CSV shard(s) with column "Combination" containing JSON dict strings.
# ASCII-only logs.

import argparse
import csv
import json
import os
import random
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple


DEFAULT_SIGNALS = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch"
]


def utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def utc_ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def parse_signals(s: str) -> List[str]:
    if not s.strip():
        return list(DEFAULT_SIGNALS)
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return parts


def weight_values(wmin: float, wmax: float, step: float) -> List[float]:
    vals = []
    x = wmin
    # avoid float drift via integer steps
    imin = int(round(wmin / step))
    imax = int(round(wmax / step))
    for i in range(imin, imax + 1):
        vals.append(round(i * step, 10))
    return vals


def combo_key(d: Dict[str, float]) -> Tuple[Tuple[str, float], ...]:
    return tuple(sorted((k, float(v)) for k, v in d.items()))


def dict_to_json_sorted(d: Dict[str, float]) -> str:
    return json.dumps({k: float(v) for k, v in sorted(d.items())}, separators=(",", ":"))


def generate_unique_random_k(
    signals: List[str],
    k: int,
    weights: List[float],
    n: int,
    rng: random.Random,
    max_attempts: int = 2_000_000
) -> List[Dict[str, float]]:
    if k > len(signals):
        raise ValueError(f"k={k} is larger than number of signals={len(signals)}")

    out: List[Dict[str, float]] = []
    seen: Set[Tuple[Tuple[str, float], ...]] = set()

    attempts = 0
    while len(out) < n and attempts < max_attempts:
        attempts += 1
        picked = rng.sample(signals, k)
        d = {name: float(rng.choice(weights)) for name in picked}
        key = combo_key(d)
        if key in seen:
            continue
        seen.add(key)
        out.append(d)

    if len(out) < n:
        raise RuntimeError(
            f"Could not generate enough unique combos: requested={n}, got={len(out)} "
            f"after attempts={attempts}. Increase max_attempts or reduce n."
        )
    return out


def write_sharded_csv(out_dir: str, prefix: str, rows: List[Dict[str, float]], shard_size: int) -> List[str]:
    ensure_dir(out_dir)
    paths = []
    total = len(rows)
    part = 1
    for start in range(0, total, shard_size):
        chunk = rows[start:start + shard_size]
        out_path = os.path.join(out_dir, f"{prefix}.part{part}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["Combination"])
            w.writeheader()
            for d in chunk:
                w.writerow({"Combination": dict_to_json_sorted(d)})
        paths.append(out_path)
        part += 1
    return paths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True, help="Output directory, e.g. data/k5_long_regime_random")
    ap.add_argument("--n", type=int, default=40, help="Number of random K5 combos to generate. Default: 40 (~0.5% of 7952)")
    ap.add_argument("--k", type=int, default=5, help="K in K5. Default: 5")
    ap.add_argument("--signals", default=",".join(DEFAULT_SIGNALS), help="Comma-separated signal names")
    ap.add_argument("--weight-min", type=float, default=0.1, help="Min weight. Default: 0.1")
    ap.add_argument("--weight-max", type=float, default=1.0, help="Max weight. Default: 1.0")
    ap.add_argument("--weight-step", type=float, default=0.1, help="Weight step. Default: 0.1")
    ap.add_argument("--seed", type=int, default=42, help="RNG seed for reproducibility. Default: 42")
    ap.add_argument("--shard-size", type=int, default=50000, help="Rows per output shard. Default: 50000")
    args = ap.parse_args()

    signals = parse_signals(args.signals)
    weights = weight_values(args.weight_min, args.weight_max, args.weight_step)
    rng = random.Random(args.seed)

    print(f"[{utc_now_str()}] Generating random K{args.k} combos for LONG")
    print(f"[{utc_now_str()}] signals={len(signals)} k={args.k} n={args.n} weights={len(weights)} seed={args.seed}")

    combos = generate_unique_random_k(signals, args.k, weights, args.n, rng)

    prefix = f"strategies_k5_long_random_{utc_ts_compact()}"
    paths = write_sharded_csv(args.out_dir, prefix, combos, args.shard_size)

    print(f"[{utc_now_str()}] Done")
    print(f"Rows written: {len(combos)}")
    print(f"Output prefix: {os.path.join(args.out_dir, prefix)} (files: {paths[0]} ..)")


if __name__ == "__main__":
    main()
