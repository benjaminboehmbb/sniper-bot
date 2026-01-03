#!/usr/bin/env python3
# ASCII-only. Generate K9 LONG candidates from K8 LONG FULL results.
# Pools:
# - Top ROI pool: top 2% by ROI (Sharpe capped at 4.0 for selection stability)
# - Stable pool: winrate in [median..p90] AND num_trades in [p10..p90]
# - Optional Sharpe-elite: 2% of seeds by sharpe_capped (explorative), min-trades enforced (+10% vs K8 baseline)
# Expansion:
# - For each K8 seed (len==8), add one missing signal to reach K9 using weight grid 0.1..1.0 step 0.1
# Random:
# - 2% of seed_expansion rows, separate file; merged file = seedexp + random

from __future__ import annotations

import argparse
import ast
import json
import math
import os
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

SIGNALS_12 = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch",
]

def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

def log(msg: str) -> None:
    print(f"[{utc_ts()} UTC] {msg}", flush=True)

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def parse_combination(s: str) -> Dict[str, float]:
    s = (s or "").strip()
    if not s:
        return {}
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return {str(k): float(v) for k, v in obj.items()}
    except Exception:
        pass
    obj = ast.literal_eval(s)
    if not isinstance(obj, dict):
        raise ValueError("Combination is not a dict")
    return {str(k): float(v) for k, v in obj.items()}

def combo_to_json(d: Dict[str, float]) -> str:
    return json.dumps({k: float(d[k]) for k in sorted(d.keys())}, separators=(",", ":"), sort_keys=True)

def weight_grid(step: float, w_min: float = 0.1, w_max: float = 1.0) -> List[float]:
    vals: List[float] = []
    x = float(w_min)
    while x <= (float(w_max) + 1e-12):
        v = round(x, 10)
        if abs(step - 0.1) < 1e-12:
            v = round(v, 1)
        vals.append(float(v))
        x += float(step)
    return vals

def sharpe_capped(df: pd.DataFrame, cap: float) -> pd.Series:
    if "sharpe" not in df.columns:
        return pd.Series([0.0] * len(df))
    s = pd.to_numeric(df["sharpe"], errors="coerce").fillna(0.0)
    s = s.replace([math.inf, -math.inf], 0.0)
    return s.clip(lower=-1e9, upper=float(cap))

def canonicalize_combination_col(df: pd.DataFrame) -> pd.DataFrame:
    if "Combination" not in df.columns:
        for alt in ["strategy", "Strategy", "combination", "CombinationStr"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "Combination"})
                break
    if "Combination" not in df.columns:
        raise KeyError("Missing required column 'Combination'.")
    out = df.copy()
    out["Combination_canon"] = out["Combination"].astype(str).map(lambda s: combo_to_json(parse_combination(s)))
    return out

def build_seed_pools(
    df: pd.DataFrame,
    roi_top_frac: float,
    sharpe_cap: float,
    min_trades_k9: int,
) -> Tuple[pd.DataFrame, Dict[str, float]]:
    d = df.copy()

    for c in ["roi", "winrate", "num_trades", "sharpe"]:
        if c in d.columns:
            d[c] = pd.to_numeric(d[c], errors="coerce")

    d["sharpe_capped"] = sharpe_capped(d, sharpe_cap)

    # enforce min trades for all pools
    if "num_trades" not in d.columns:
        raise KeyError("Missing num_trades in K8 results.")
    d = d[d["num_trades"].fillna(0) >= float(min_trades_k9)].copy()

    wr = pd.to_numeric(d["winrate"], errors="coerce").dropna()
    nt = pd.to_numeric(d["num_trades"], errors="coerce").dropna()
    if len(wr) == 0 or len(nt) == 0:
        raise RuntimeError("After min_trades filter, winrate/num_trades have no valid rows.")

    wr_med = float(wr.median())
    wr_p90 = float(wr.quantile(0.90))
    nt_p10 = float(nt.quantile(0.10))
    nt_p90 = float(nt.quantile(0.90))

    # Top ROI pool
    d_roi = d.sort_values("roi", ascending=False).reset_index(drop=True)
    top_n = max(1, int(round(len(d_roi) * float(roi_top_frac))))
    top_roi = d_roi.head(top_n).copy()
    top_roi["seed_source"] = "top_roi"

    # Stable pool
    stable = d[
        (d["winrate"] >= wr_med) &
        (d["winrate"] <= wr_p90) &
        (d["num_trades"] >= nt_p10) &
        (d["num_trades"] <= nt_p90)
    ].copy()
    stable["seed_source"] = "stable_pool"

    seeds = pd.concat([top_roi, stable], ignore_index=True)
    seeds = seeds.drop_duplicates(subset=["Combination_canon"]).reset_index(drop=True)

    stats = {
        "wr_median": wr_med,
        "wr_p90": wr_p90,
        "nt_p10": nt_p10,
        "nt_p90": nt_p90,
        "min_trades_k9": float(min_trades_k9),
        "roi_top_frac": float(roi_top_frac),
        "sharpe_cap": float(sharpe_cap),
        "rows_after_min_trades": int(len(d)),
        "seed_union_rows": int(len(seeds)),
    }
    return seeds, stats

def add_sharpe_elite(seeds: pd.DataFrame, elite_frac: float) -> pd.DataFrame:
    if elite_frac <= 0 or len(seeds) == 0:
        return seeds
    n = max(1, int(round(len(seeds) * float(elite_frac))))
    elite = seeds.sort_values("sharpe_capped", ascending=False).head(n).copy()
    elite["seed_source"] = elite["seed_source"].astype(str) + "+sharpe_elite"
    out = pd.concat([seeds, elite], ignore_index=True)
    out = out.drop_duplicates(subset=["Combination_canon"]).reset_index(drop=True)
    return out

def seed_expand_k8_to_k9(seed_combos: List[str], wvals: List[float], dedup: bool = True) -> Tuple[pd.DataFrame, Set[str]]:
    rows: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    for rank, comb_str in enumerate(seed_combos, start=1):
        d0 = parse_combination(comb_str)
        if len(d0) != 8:
            continue
        present = set(d0.keys())
        missing = [s for s in SIGNALS_12 if s not in present]
        if not missing:
            continue

        for sig in missing:
            for w in wvals:
                d = dict(d0)
                d[sig] = float(w)
                cjson = combo_to_json(d)
                if dedup and cjson in seen:
                    continue
                seen.add(cjson)
                rows.append({"Combination": cjson, "source": "seed_expansion", "seed_rank": int(rank)})

    return pd.DataFrame(rows), seen

def random_k9(n: int, wvals: List[float], rng: random.Random, seen: Optional[Set[str]] = None) -> pd.DataFrame:
    out: List[Dict[str, Any]] = []
    seen_local: Set[str] = set()
    max_tries = max(2000, n * 150)
    tries = 0

    while len(out) < n and tries < max_tries:
        tries += 1
        sigs = rng.sample(SIGNALS_12, 9)
        d = {s: float(rng.choice(wvals)) for s in sigs}
        cjson = combo_to_json(d)
        if cjson in seen_local:
            continue
        if seen is not None and cjson in seen:
            continue
        seen_local.add(cjson)
        out.append({"Combination": cjson, "source": "random", "seed_rank": 0})

    return pd.DataFrame(out)

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate K9 LONG candidates from K8 LONG FULL results.")
    p.add_argument("--k8-results-csv", required=True)
    p.add_argument("--out-dir", default="data")

    p.add_argument("--roi-top-frac", type=float, default=0.02)
    p.add_argument("--sharpe-cap", type=float, default=4.0)

    p.add_argument("--min-trades-k8", type=int, default=1000)
    p.add_argument("--min-trades-mult", type=float, default=1.10)

    p.add_argument("--sharpe-elite-frac", type=float, default=0.02)

    p.add_argument("--weight-step", type=float, default=0.1)
    p.add_argument("--weights-min", type=float, default=0.1)
    p.add_argument("--weights-max", type=float, default=1.0)

    p.add_argument("--random-frac", type=float, default=0.02)  # relative to seed_expansion rows
    p.add_argument("--seed", type=int, default=1337)
    p.add_argument("--dedup", type=int, default=1)
    return p.parse_args()

def main() -> None:
    args = parse_args()
    rng = random.Random(int(args.seed))
    dedup = bool(int(args.dedup))

    in_path = Path(args.k8_results_csv)
    if not in_path.exists():
        raise FileNotFoundError(f"Not found: {in_path}")

    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    min_trades_k9 = int(math.ceil(float(args.min_trades_k8) * float(args.min_trades_mult)))

    df = pd.read_csv(in_path)
    log(f"K8 input rows: {len(df)}")
    df = canonicalize_combination_col(df)

    seeds, stats = build_seed_pools(
        df=df,
        roi_top_frac=float(args.roi_top_frac),
        sharpe_cap=float(args.sharpe_cap),
        min_trades_k9=min_trades_k9,
    )
    log(f"Seeds (top ROI + stable) rows: {len(seeds)} | min_trades_k9={min_trades_k9}")
    log(f"Stable stats: wr_med={stats['wr_median']:.6f} wr_p90={stats['wr_p90']:.6f} nt_p10={stats['nt_p10']:.1f} nt_p90={stats['nt_p90']:.1f}")

    seeds = add_sharpe_elite(seeds, elite_frac=float(args.sharpe_elite_frac))
    log(f"Seeds after sharpe-elite add: {len(seeds)}")

    seed_combos = seeds["Combination_canon"].astype(str).tolist()

    wvals = weight_grid(float(args.weight_step), float(args.weights_min), float(args.weights_max))
    log(f"Weight grid n={len(wvals)} ({args.weights_min}..{args.weights_max} step={args.weight_step})")

    seedexp, seen = seed_expand_k8_to_k9(seed_combos, wvals=wvals, dedup=dedup)
    if len(seedexp) == 0:
        raise RuntimeError("Seed expansion produced 0 rows. Are seeds really K8 (len==8)?")

    seed_rows = int(len(seedexp))
    rand_n = 0
    if float(args.random_frac) > 0:
        rand_n = max(1, int(round(seed_rows * float(args.random_frac))))
    rand = random_k9(n=rand_n, wvals=wvals, rng=rng, seen=seen if dedup else None)

    ts = utc_ts()
    out_seeds = out_dir / f"seeds_k9_long_from_k8_{ts}.csv"
    out_seedexp = out_dir / f"strategies_k9_long_seedexp_{ts}.csv"
    out_rand = out_dir / f"strategies_k9_long_random_{ts}.csv"
    out_merged = out_dir / f"strategies_k9_long_merged_{ts}.csv"

    seeds.to_csv(out_seeds, index=False)
    seedexp.to_csv(out_seedexp, index=False)
    rand.to_csv(out_rand, index=False)
    pd.concat([seedexp, rand], ignore_index=True).to_csv(out_merged, index=False)

    log("[ok] Generated K9 LONG candidates")
    log(f"Wrote: {out_seeds}")
    log(f"Wrote: {out_seedexp} (rows={seed_rows})")
    log(f"Wrote: {out_rand} (rows={len(rand)})")
    log(f"Wrote: {out_merged} (rows={seed_rows + len(rand)})")

if __name__ == "__main__":
    main()

