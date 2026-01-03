#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate K7 LONG strategies from K6 LONG merge pool (seed expansion + optional random sampling).

INPUT:
  - A CSV (merge pool) that contains at least a column "Combination"
    Optionally also "roi" and "winrate" for ranking/thresholds.

OUTPUT:
  - One CSV in --out-dir with column "Combination" (dict/JSON string) for K7 candidates.

Design goals:
  - Robust to missing roi/winrate columns (no NaN threshold crash)
  - Enforces seed K=6 and produces K7 dicts (size 7)
  - ASCII-only logs
"""

from __future__ import annotations

import argparse
import ast
import json
import math
import os
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

import pandas as pd


# 12-signal universe (per project convention)
SIGNALS = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch",
]


def utc_ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    print(f"[{ts} UTC] {msg}", flush=True)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def parse_combination(s: str) -> Dict[str, float]:
    s = (s or "").strip()
    if not s:
        return {}
    # Try JSON first
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return {str(k): float(v) for k, v in obj.items()}
    except Exception:
        pass
    # Fallback: python literal dict
    obj = ast.literal_eval(s)
    if not isinstance(obj, dict):
        raise ValueError("Combination is not a dict")
    return {str(k): float(v) for k, v in obj.items()}


def combo_to_str(d: Dict[str, float]) -> str:
    # stable ordering for dedup
    return json.dumps({k: float(d[k]) for k in sorted(d.keys())}, separators=(",", ":"))


def safe_numeric_series(df: pd.DataFrame, col: str) -> Optional[pd.Series]:
    if col not in df.columns:
        return None
    s = pd.to_numeric(df[col], errors="coerce")
    s = s.replace([math.inf, -math.inf], pd.NA).dropna()
    if len(s) == 0:
        return None
    return s


def compute_thresholds(df: pd.DataFrame) -> Tuple[Optional[float], Optional[float]]:
    """
    Returns (roi_p90, winrate_median) if possible, else (None, None).
    """
    roi_s = safe_numeric_series(df, "roi")
    wr_s = safe_numeric_series(df, "winrate")
    roi_p90 = float(roi_s.quantile(0.90)) if roi_s is not None else None
    wr_med = float(wr_s.median()) if wr_s is not None else None
    return roi_p90, wr_med


def ensure_k6_seed_row(comb_str: str) -> Dict[str, float]:
    comb = parse_combination(comb_str)
    if len(comb) != 6:
        raise ValueError(f"Expected K6 combination, got K={len(comb)}")
    # sanity: keys subset of SIGNALS
    for k in comb.keys():
        if k not in SIGNALS:
            # allow unknown keys but warn via exception? keep robust: allow, but it will reduce expansion options
            pass
    return comb


def weight_grid(w_min: float, w_max: float, step: float) -> List[float]:
    # inclusive grid, with rounding to avoid float drift
    vals: List[float] = []
    x = w_min
    while x <= (w_max + 1e-12):
        vals.append(round(float(x), 10))
        x += step
    # convert to one-decimal typical grid if step is 0.1
    if abs(step - 0.1) < 1e-12:
        vals = [round(v, 1) for v in vals]
    return vals


def rank_seeds(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prefer to rank by roi desc if available; else keep file order.
    """
    if "roi" in df.columns:
        tmp = df.copy()
        tmp["roi_num"] = pd.to_numeric(tmp["roi"], errors="coerce")
        tmp = tmp.sort_values(["roi_num"], ascending=[False], na_position="last")
        tmp = tmp.drop(columns=["roi_num"])
        return tmp
    return df


def generate_seed_expansion(
    seed_rows: List[str],
    per_seed_max: int,
    wvals: List[float],
    rng: random.Random,
    dedup: bool,
) -> List[str]:
    """
    For each K6 seed, add exactly one missing signal with each weight value
    (or sampled subset limited by per_seed_max).
    Produces K7 combos.
    """
    out: List[str] = []
    seen: Set[str] = set()

    for comb_str in seed_rows:
        seed = ensure_k6_seed_row(comb_str)
        present = set(seed.keys())
        missing = [s for s in SIGNALS if s not in present]
        if not missing:
            continue

        # build all candidate additions for this seed
        candidates: List[Dict[str, float]] = []
        for add_sig in missing:
            for w in wvals:
                d = dict(seed)
                d[add_sig] = float(w)
                candidates.append(d)

        # sample/limit per seed
        if per_seed_max and per_seed_max > 0 and len(candidates) > per_seed_max:
            candidates = rng.sample(candidates, per_seed_max)

        for d in candidates:
            s = combo_to_str(d)
            if dedup:
                if s in seen:
                    continue
                seen.add(s)
            out.append(s)

    return out


def generate_random_k7(
    n: int,
    wvals: List[float],
    rng: random.Random,
    dedup_against: Optional[Set[str]] = None,
) -> List[str]:
    """
    Random K7 sampling (exploration) independent of seeds.
    """
    out: List[str] = []
    seen_local: Set[str] = set()
    max_tries = max(1000, n * 50)
    tries = 0

    while len(out) < n and tries < max_tries:
        tries += 1
        sigs = rng.sample(SIGNALS, 7)
        d = {s: float(rng.choice(wvals)) for s in sigs}
        s = combo_to_str(d)
        if s in seen_local:
            continue
        if dedup_against is not None and s in dedup_against:
            continue
        seen_local.add(s)
        out.append(s)

    return out


def write_out(combos: List[str], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    df = pd.DataFrame({"Combination": combos})
    df.to_csv(out_path, index=False)
    log(f"Wrote: {out_path} (rows={len(df)})")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate K7 LONG from K6 LONG merge pool.")
    p.add_argument("--k6-merge-csv", required=True, help="Path to K6 merge pool CSV (must contain Combination).")
    p.add_argument("--out-dir", default="data", help="Output directory for K7 CSV(s).")

    # sizing
    p.add_argument("--seed-count", type=int, default=16000, help="How many top seeds (rows) to use from merge pool.")
    p.add_argument("--random-frac", type=float, default=0.02, help="Random exploration fraction relative to seed-count.")
    p.add_argument("--per-seed-max", type=int, default=50, help="Max expansions per seed (0 = no limit).")

    # weights
    p.add_argument("--weights-step", type=float, default=0.1, help="Weight grid step (default 0.1).")
    p.add_argument("--weights-min", type=float, default=0.1, help="Min weight.")
    p.add_argument("--weights-max", type=float, default=1.0, help="Max weight.")

    p.add_argument("--seed", type=int, default=1337, help="RNG seed.")
    p.add_argument("--dedup", type=int, default=1, help="Deduplicate output (1/0).")

    return p.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(int(args.seed))
    dedup = bool(int(args.dedup))

    merge_csv = Path(args.k6_merge_csv)
    if not merge_csv.exists():
        raise FileNotFoundError(f"Not found: {merge_csv}")

    df = pd.read_csv(merge_csv)
    if "Combination" not in df.columns:
        # common alias fallback
        for alt in ["strategy", "Strategy", "combination"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "Combination"})
                break
    if "Combination" not in df.columns:
        raise KeyError("Missing required column 'Combination' in merge CSV.")

    log(f"K6 merge rows: {len(df)}")

    # thresholds (informational; generator does not rely on them)
    roi_p90, wr_med = compute_thresholds(df)
    log(f"Merge thresholds (informational): roi_p90={roi_p90 if roi_p90 is not None else 'NA'}, winrate_median={wr_med if wr_med is not None else 'NA'}")

    df_ranked = rank_seeds(df)

    seed_count = int(args.seed_count)
    seed_count = max(1, min(seed_count, len(df_ranked)))
    seed_rows = df_ranked["Combination"].astype(str).head(seed_count).tolist()

    random_n = int(round(seed_count * float(args.random_frac)))
    log(f"Using seed_count={seed_count}, random_n≈{random_n} ({float(args.random_frac)*100:.2f}%)")

    wvals = weight_grid(float(args.weights_min), float(args.weights_max), float(args.weights_step))
    log(f"Weight grid: {args.weights_min}..{args.weights_max} step={args.weights_step} (n={len(wvals)})")

    # Seed expansion K6 -> K7
    seeds_k7 = generate_seed_expansion(
        seed_rows=seed_rows,
        per_seed_max=int(args.per_seed_max),
        wvals=wvals,
        rng=rng,
        dedup=dedup,
    )
    log(f"Seed expansion generated: {len(seeds_k7)} candidates")

    # Optional random exploration
    all_seen: Set[str] = set(seeds_k7) if dedup else set()
    rand_k7: List[str] = []
    if random_n > 0:
        rand_k7 = generate_random_k7(
            n=random_n,
            wvals=wvals,
            rng=rng,
            dedup_against=all_seen if dedup else None,
        )
        log(f"Random generated: {len(rand_k7)} candidates")

    combos = seeds_k7 + rand_k7
    if dedup:
        # final dedup pass (stable)
        uniq: List[str] = []
        seen: Set[str] = set()
        for s in combos:
            if s in seen:
                continue
            seen.add(s)
            uniq.append(s)
        combos = uniq
        log(f"Final deduped rows: {len(combos)}")

    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)
    out_path = out_dir / f"strategies_k7_from_k6_long_{utc_ts_compact()}.csv"
    write_out(combos, out_path)


if __name__ == "__main__":
    main()

