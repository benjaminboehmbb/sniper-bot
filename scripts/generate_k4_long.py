#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
Generate K4 LONG candidate strategies from a K3 base pool.

Inputs:
  - --base-csv         Path to k4_base_long_*.csv (must contain column 'Combination')
  - --signal-space     Path to k4_signal_space_*.json (12 signals + selection_probabilities)

Output:
  - CSV with new 4-signal combinations and provenance columns.

Design goals:
  - Robust parsing of Combination dicts (json or python-literal)
  - Flexible generation modes: exhaustive vs probabilistic per-base selection
  - Weight grid configurable; default 0.1..1.0 step 0.1 (10 values)
  - Dedupe by canonicalized Combination (sorted keys, fixed float formatting)
  - Streamed writing to avoid high memory usage
  - Safe backups with timestamp before overwriting
  - ASCII-only logging

Example usage:
  python scripts/generate_k4_long.py \
    --base-csv data/k4_base_long_2025-12-01_13-28-35.csv \
    --signal-space data/k4_signal_space_pruned_2025-12-01_13-59-12.json \
    --mode probabilistic --per-base 6 \
    --weights 0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0 \
    --out data/strategies_k4_from_k3_long_2025-12-01.csv

Notes:
  - If you choose --mode exhaustive, every missing signal will be added per base
    and combined with all weights; this may generate a very large file.
  - Prefer probabilistic mode with --per-base N for a balanced, broad set.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, Iterable, List, Tuple

import ast
import math
import random

# ----------------------------
# Helpers
# ----------------------------

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-csv", required=True, help="Path to k4_base_long_*.csv")
    ap.add_argument("--signal-space", required=True, help="Path to k4_signal_space_*.json")
    ap.add_argument("--mode", choices=["exhaustive", "probabilistic"], default="probabilistic",
                    help="Generation mode for selecting the 4th signal")
    ap.add_argument("--per-base", type=int, default=6,
                    help="Only for probabilistic mode: number of new signals per base to extend with")
    ap.add_argument("--weights", default="0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0",
                    help="Comma-separated weight grid for the added signal")
    ap.add_argument("--dedupe", type=int, default=1, help="1 to dedupe by canonical Combination, else 0")
    ap.add_argument("--shard-size", type=int, default=500_000,
                    help="Rows per output shard (use 0 for single file)")
    ap.add_argument("--out", default=None,
                    help="Output CSV path. If omitted, a dated name is created under data/")
    return ap.parse_args()


def read_signal_space(path: str) -> Tuple[List[str], Dict[str, float]]:
    with open(path, "r", encoding="utf-8") as f:
        js = json.load(f)
    signals = js.get("signals")
    if not signals or not isinstance(signals, list):
        sys.exit("Error: signal-space JSON missing 'signals' list")
    probs = js.get("selection_probabilities", {})
    # Normalize probabilities over provided signals; fallback to uniform
    p = []
    total = 0.0
    for s in signals:
        w = float(probs.get(s, 1.0))
        if w < 0.0:
            w = 0.0
        p.append(w)
        total += w
    if total <= 0.0:
        p = [1.0 for _ in signals]
        total = float(len(signals))
    p = [x / total for x in p]
    prob_map = {s: w for s, w in zip(signals, p)}
    return signals, prob_map


def parse_comb_dict(text: str) -> Dict[str, float]:
    # Try JSON first
    try:
        d = json.loads(text)
        if isinstance(d, dict):
            return {str(k): float(v) for k, v in d.items()}
    except Exception:
        pass
    # Try python literal
    try:
        d = ast.literal_eval(text)
        if isinstance(d, dict):
            return {str(k): float(v) for k, v in d.items()}
    except Exception:
        pass
    # Try replacing single quotes
    try:
        d = json.loads(text.replace("'", '"'))
        if isinstance(d, dict):
            return {str(k): float(v) for k, v in d.items()}
    except Exception:
        pass
    raise ValueError("Could not parse Combination into dict")


def canonical_comb_str(d: Dict[str, float]) -> str:
    # Sort keys; format floats with one decimal if possible, else default
    items = []
    for k in sorted(d.keys()):
        v = float(d[k])
        # format weights to 1 decimal; avoid trailing .0 if it was an int weight
        if abs(v - round(v, 1)) < 1e-9:
            s = ("%.1f" % v).rstrip("0").rstrip(".")
        else:
            s = str(v)
        items.append(f'"{k}": {s}')
    return "{" + ", ".join(items) + "}"


def ensure_out_path(path: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # backup if exists
    if os.path.exists(path):
        ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        bak = f"{os.path.splitext(path)[0]}_backup_{ts}.csv"
        os.replace(path, bak)
        print(f"[info] Existing output moved to backup: {bak}")
    return path


def choose_new_signals(candidates: List[str], prob_map: Dict[str, float], k: int) -> List[str]:
    # Weighted sample without replacement; if k>=len(candidates) return candidates sorted by prob desc
    if k >= len(candidates):
        return sorted(candidates, key=lambda s: prob_map.get(s, 0.0), reverse=True)
    # Build weights list
    weights = [max(0.0, prob_map.get(s, 0.0)) for s in candidates]
    total = sum(weights)
    if total <= 0.0:
        # uniform fallback
        return random.sample(candidates, k)
    # sampling without replacement by iterative draw
    chosen = []
    pool = list(candidates)
    w = list(weights)
    for _ in range(k):
        total = sum(w)
        if total <= 0.0:
            # rest uniform
            remain = [x for x in pool if x not in chosen]
            if not remain:
                break
            pick = random.choice(remain)
        else:
            r = random.random() * total
            acc = 0.0
            pick = pool[-1]
            for s, ww in zip(pool, w):
                acc += ww
                if r <= acc:
                    pick = s
                    break
        chosen.append(pick)
        idx = pool.index(pick)
        del pool[idx]
        del w[idx]
    return chosen


# ----------------------------
# Main generation logic
# ----------------------------

def main():
    args = parse_args()

    # Prepare outputs
    if args.out is None:
        ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        out_path = f"data/strategies_k4_from_k3_long_{ts}.csv"
    else:
        out_path = args.out
    out_path = ensure_out_path(out_path)

    # Load signal space
    signals, prob_map = read_signal_space(args.signal_space)
    signal_set = set(signals)

    # Weight grid
    try:
        weight_grid = [float(x.strip()) for x in args.weights.split(",") if x.strip()]
        if not weight_grid:
            raise ValueError
    except Exception:
        sys.exit("Error: invalid --weights. Provide comma-separated floats, e.g., 0.1,0.2,...,1.0")

    # Open base csv and stream
    import pandas as pd

    # Output writer
    shard_size = max(0, int(args.shard_size))
    shard_idx = 0
    row_count = 0
    dedupe = bool(args.dedupe)
    seen = set() if dedupe else None

    def open_writer(path: str):
        f = open(path, "w", newline="", encoding="utf-8")
        w = csv.writer(f)
        w.writerow(["Combination", "base_index", "base_roi", "base_winrate", "base_num_trades"])  # header
        return f, w

    current_path = out_path if shard_size == 0 else out_path.replace(".csv", f".part{shard_idx+1}.csv")
    fh, writer = open_writer(current_path)

    print("[info] Start generation")
    print(f"[info] Mode: {args.mode}")
    print(f"[info] Per-base: {args.per_base}")
    print(f"[info] Weight grid: {weight_grid}")

    # Read in chunks to reduce memory
    use_cols = ["Combination", "index", "roi", "winrate", "num_trades"]
    for chunk in pd.read_csv(args.base_csv, usecols=use_cols, chunksize=50_000):
        for _, r in chunk.iterrows():
            try:
                comb = parse_comb_dict(str(r["Combination"]))
            except Exception:
                continue
            keys = list(sorted(comb.keys()))
            if len(keys) != 3:
                # Only extend proper K3 combos
                continue
            # Candidate signals = all minus existing
            missing = list(sorted(signal_set.difference(keys)))
            if not missing:
                continue

            if args.mode == "exhaustive":
                chosen = missing
            else:
                chosen = choose_new_signals(missing, prob_map, max(1, int(args.per_base)))

            for s in chosen:
                for wv in weight_grid:
                    new = dict(comb)
                    new[s] = float(wv)
                    canon = canonical_comb_str(new)
                    if dedupe:
                        if canon in seen:
                            continue
                        seen.add(canon)
                    writer.writerow([canon, r.get("index", ""), r.get("roi", ""), r.get("winrate", ""), r.get("num_trades", "")])
                    row_count += 1
                    # Handle sharding
                    if shard_size and (row_count % shard_size == 0):
                        fh.flush(); fh.close()
                        shard_idx += 1
                        current_path = out_path.replace(".csv", f".part{shard_idx+1}.csv")
                        fh, writer = open_writer(current_path)

    fh.flush(); fh.close()

    print("[info] Done.")
    if shard_size:
        print(f"[info] Wrote {shard_idx+1} shards starting with: {out_path}")
    else:
        print(f"[info] Wrote: {out_path}")
    print(f"[info] Rows generated: {row_count}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[warn] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"[error] {e}")
        sys.exit(1)
