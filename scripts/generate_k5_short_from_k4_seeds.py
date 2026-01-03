# generate_k5_short_from_k4_seeds.py
# Generate K5 SHORT combinations from K4 seed combos.
# Expansion rule (deterministic, matches prior K5-long behavior):
#   For each K4 seed (4 signals), add exactly 1 new signal (from remaining set)
#   and sweep its weight over [wmin..wmax] in steps, producing (12-4)*nweights combos per seed.
#
# Input: one or more CSV files (glob) containing a column "Combination" (JSON or dict-string).
# Output: sharded CSV(s) with a single column "Combination" (JSON dict string, sorted keys).
#
# ASCII-only logs. UTC timestamps.

import argparse
import ast
import csv
import glob
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Set


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


def expand_globs(glob_expr: str) -> List[str]:
    patterns = [p.strip() for p in glob_expr.split(";") if p.strip()]
    out: List[str] = []
    for pat in patterns:
        matches = sorted(glob.glob(pat))
        if matches:
            out.extend(matches)
        elif os.path.isfile(pat):
            out.append(pat)
    # dedupe preserve order
    seen = set()
    dedup = []
    for p in out:
        if p not in seen:
            dedup.append(p)
            seen.add(p)
    return dedup


def parse_signals(s: str) -> List[str]:
    if not s.strip():
        return list(DEFAULT_SIGNALS)
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return parts


def weight_values(wmin: float, wmax: float, step: float) -> List[float]:
    imin = int(round(wmin / step))
    imax = int(round(wmax / step))
    vals: List[float] = []
    for i in range(imin, imax + 1):
        vals.append(round(i * step, 10))
    return vals


def dict_to_json_sorted(d: Dict[str, float]) -> str:
    return json.dumps({k: float(v) for k, v in sorted(d.items())}, separators=(",", ":"))


def combo_key(d: Dict[str, float]) -> Tuple[Tuple[str, float], ...]:
    return tuple(sorted((k, float(v)) for k, v in d.items()))


def read_seed_rows(paths: List[str], comb_col: str, score_col: str) -> List[Tuple[float, Dict[str, float]]]:
    seeds: List[Tuple[float, Dict[str, float]]] = []
    for p in paths:
        with open(p, "r", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            if comb_col not in (r.fieldnames or []):
                raise ValueError(f"Seed file '{p}' missing column '{comb_col}'. Found: {r.fieldnames}")
            # score_col is optional; if absent, score = 0.0
            for row in r:
                raw = (row.get(comb_col) or "").strip()
                if not raw:
                    continue
                try:
                    d = json.loads(raw)
                except Exception:
                    d = ast.literal_eval(raw)
                if not isinstance(d, dict):
                    continue
                comb: Dict[str, float] = {}
                for k, v in d.items():
                    comb[str(k)] = float(v)
                score = 0.0
                if score_col and (r.fieldnames and score_col in r.fieldnames):
                    try:
                        score = float(row.get(score_col))
                    except Exception:
                        score = 0.0
                seeds.append((score, comb))
    return seeds


def dedupe_keep_best(seeds: List[Tuple[float, Dict[str, float]]]) -> List[Tuple[float, Dict[str, float]]]:
    best: Dict[Tuple[Tuple[str, float], ...], Tuple[float, Dict[str, float]]] = {}
    for score, comb in seeds:
        k = combo_key(comb)
        prev = best.get(k)
        if prev is None or score > prev[0]:
            best[k] = (score, comb)
    return list(best.values())


def write_shards(out_dir: str, prefix: str, combos_json: List[str], shard_size: int) -> List[str]:
    ensure_dir(out_dir)
    paths: List[str] = []
    part = 1
    for start in range(0, len(combos_json), shard_size):
        chunk = combos_json[start:start + shard_size]
        out_path = os.path.join(out_dir, f"{prefix}.part{part}.csv")
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["Combination"])
            w.writeheader()
            for s in chunk:
                w.writerow({"Combination": s})
        paths.append(out_path)
        part += 1
    return paths


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True, help='Seed CSV glob(s), e.g. "results/k4_short_regime/top_seeds*.csv" or "results/k4_short/*.csv"')
    ap.add_argument("--out-dir", required=True, help='Output dir, e.g. "data/k5_short_regime"')
    ap.add_argument("--limit-seeds", type=int, default=0, help="Use only top-N seeds by score column (after dedupe). 0 = all.")
    ap.add_argument("--comb-col", default="Combination", help="Column containing combination dict/JSON. Default: Combination")
    ap.add_argument("--score-col", default="roi", help="Column used to rank seeds. Default: roi")
    ap.add_argument("--signals", default=",".join(DEFAULT_SIGNALS), help="Comma-separated signals universe")
    ap.add_argument("--weight-min", type=float, default=0.1)
    ap.add_argument("--weight-max", type=float, default=1.0)
    ap.add_argument("--weight-step", type=float, default=0.1)
    ap.add_argument("--shard-size", type=int, default=50000)
    args = ap.parse_args()

    seed_files = expand_globs(args.seeds)
    if not seed_files:
        raise SystemExit(f"No seed files found for --seeds: {args.seeds}")

    signals = parse_signals(args.signals)
    weights = weight_values(args.weight_min, args.weight_max, args.weight_step)

    print(f"[{utc_now_str()}] Loading seeds from {len(seed_files)} file(s)")
    raw = read_seed_rows(seed_files, args.comb_col, args.score_col)
    if not raw:
        raise SystemExit("No seeds loaded (empty input).")

    seeds = dedupe_keep_best(raw)
    # sort descending by score
    seeds.sort(key=lambda x: x[0], reverse=True)

    if args.limit_seeds and args.limit_seeds > 0:
        seeds = seeds[: args.limit_seeds]

    print(f"[{utc_now_str()}] Seeds processed: {len(seeds)}")
    print(f"[{utc_now_str()}] Expansion: add 1 signal x {len(weights)} weight steps per remaining signal")

    # expand
    out_json: List[str] = []
    seen: Set[Tuple[Tuple[str, float], ...]] = set()

    for _, base in seeds:
        base_keys = set(base.keys())
        remaining = [s for s in signals if s not in base_keys]
        for add_sig in remaining:
            for w in weights:
                d = dict(base)
                d[add_sig] = float(w)
                key = combo_key(d)
                if key in seen:
                    continue
                seen.add(key)
                out_json.append(dict_to_json_sorted(d))

    ensure_dir(args.out_dir)
    prefix = f"strategies_k5_short_from_k4_seeds_{utc_ts_compact()}"
    paths = write_shards(args.out_dir, prefix, out_json, args.shard_size)

    print(f"[{utc_now_str()}] Done")
    print(f"Rows written: {len(out_json)}")
    print(f"Output prefix: {os.path.join(args.out_dir, prefix)} (files: {paths[0]} ..)")


if __name__ == "__main__":
    main()
