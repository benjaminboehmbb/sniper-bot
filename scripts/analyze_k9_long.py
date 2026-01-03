#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K9 LONG Analyzer (WSL) – built on the proven K8 analyzer pattern.

Goals:
- Smoke / Intermediate / Full runs must start quickly (no slow worker init).
- No dependency on "engine" package (fallback to repo-root simtrader.py).
- Minimal terminal output like previous runs (no worker prints; no spam).
- Writes results + random-pass merge gate output.

Usage example:
python3 scripts/analyze_k9_long.py \
  --strategies-csv data/strategies_k9_long_merged_2026-01-02_07-57-54.csv \
  --price-csv data/price_data_with_signals.csv \
  --mode smoke \
  --smoke-n 200 \
  --num-procs 4
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from multiprocessing import Pool

# ------------------------------
# Hard path fix (critical for workers)
# scripts/... -> repo root is parent of "scripts"
# ------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ------------------------------
# Globals for multiprocessing workers
# ------------------------------
_PRICE_DF: Optional[pd.DataFrame] = None
_EVAL_FN = None  # evaluate_strategy(df, comb, direction)


# ------------------------------
# Logging
# ------------------------------
def utc_ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def log(msg: str) -> None:
    print(f"[{utc_ts()} UTC] {msg}", flush=True)


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def backup_if_exists(path: Path) -> None:
    if path.exists():
        b = path.with_name(path.stem + f"_backup_{utc_ts()}" + path.suffix)
        path.replace(b)
        log(f"[backup] Existing file moved to: {b}")


def safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
        if not math.isfinite(v):
            return default
        return v
    except Exception:
        return default


def safe_int(x: Any, default: int = 0) -> int:
    try:
        return int(float(x))
    except Exception:
        return default


def sharpe_cap_value(x: Any, cap: float) -> float:
    v = safe_float(x, 0.0)
    if v > cap:
        return float(cap)
    if v < -1e9:
        return -1e9
    return v


def fmt_eta(seconds: float) -> str:
    if seconds <= 0:
        return "0s"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


# ------------------------------
# Parsing / evaluator glue (K8 pattern)
# ------------------------------
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


def coerce_strategy_obj_to_dict(obj: Any) -> Dict[str, Any]:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return obj
    out: Dict[str, Any] = {}
    # common attribute names seen in earlier runs
    for k in [
        "roi", "winrate", "num_trades", "num_wins", "num_losses",
        "avg_hold", "sharpe", "max_dd"
    ]:
        if hasattr(obj, k):
            out[k] = getattr(obj, k)
    # fallback: __dict__
    if hasattr(obj, "__dict__"):
        out.update(obj.__dict__)
    return out


def import_evaluator() -> None:
    global _EVAL_FN
    if _EVAL_FN is not None:
        return

    # Prefer repo-root simtrader.py (your environment)
    try:
        from simtrader import evaluate_strategy  # type: ignore
        _EVAL_FN = evaluate_strategy
        log("Using simtrader.evaluate_strategy.")
        return
    except Exception as e:
        log(f"[warn] Could not import simtrader.evaluate_strategy: {type(e).__name__}: {e}")

    # Optional fallback if you ever have engine package on some machine
    try:
        from engine.simtrader import evaluate_strategy  # type: ignore
        _EVAL_FN = evaluate_strategy
        log("Using engine.simtrader.evaluate_strategy.")
        return
    except Exception as e:
        log(f"[warn] Could not import engine.simtrader.evaluate_strategy: {type(e).__name__}: {e}")

    raise RuntimeError("No evaluate_strategy found (simtrader.py missing or broken).")


def load_price_data(price_csv: str) -> pd.DataFrame:
    path = Path(price_csv)
    if not path.exists():
        raise FileNotFoundError(f"Price CSV not found: {price_csv}")
    return pd.read_csv(path)


def init_context(price_csv: str) -> None:
    global _PRICE_DF
    import_evaluator()
    _PRICE_DF = load_price_data(price_csv)


# ------------------------------
# Multiprocessing hooks (pickleable)
# ------------------------------
def mp_init(price_csv: str) -> None:
    # Ensure repo root is always in sys.path inside worker
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    init_context(price_csv)


def mp_worker(args: Tuple[int, str, str, float]) -> Tuple[int, Dict[str, Any], Optional[str]]:
    idx, comb_str, direction, sharpe_cap = args
    try:
        if _PRICE_DF is None:
            raise RuntimeError("PRICE_DF not initialized in worker.")
        if _EVAL_FN is None:
            raise RuntimeError("EVAL_FN not initialized in worker.")

        comb = parse_combination(comb_str)
        out = _EVAL_FN(_PRICE_DF, comb, direction)  # type: ignore
        d = coerce_strategy_obj_to_dict(out)

        res: Dict[str, Any] = {
            "i": idx,
            "direction": direction,
            "Combination": comb_str,
            "source": "",  # filled by main from strategies csv if present
        }

        # Keep exactly the known KPI set (K8-style)
        res["roi"] = safe_float(d.get("roi", 0.0), 0.0)
        res["winrate"] = safe_float(d.get("winrate", 0.0), 0.0)
        res["num_trades"] = safe_int(d.get("num_trades", 0), 0)
        if "num_wins" in d:
            res["num_wins"] = safe_int(d.get("num_wins", 0), 0)
        if "num_losses" in d:
            res["num_losses"] = safe_int(d.get("num_losses", 0), 0)
        if "avg_hold" in d:
            res["avg_hold"] = safe_float(d.get("avg_hold", 0.0), 0.0)

        res["sharpe"] = safe_float(d.get("sharpe", 0.0), 0.0)
        res["sharpe_capped"] = sharpe_cap_value(res["sharpe"], float(sharpe_cap))

        if "max_dd" in d:
            res["max_dd"] = safe_float(d.get("max_dd", 0.0), 0.0)

        return idx, res, None

    except Exception as e:
        return idx, {"i": idx, "direction": direction, "Combination": comb_str}, f"{type(e).__name__}: {e}"


# ------------------------------
# Strategies IO
# ------------------------------
def load_strategies(path: str, limit: Optional[int]) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Strategies CSV not found: {path}")
    df = pd.read_csv(p)

    if "Combination" not in df.columns:
        for alt in ["strategy", "Strategy", "combination"]:
            if alt in df.columns:
                df = df.rename(columns={alt: "Combination"})
                break
    if "Combination" not in df.columns:
        raise KeyError("Strategies CSV must contain 'Combination' column.")

    if "source" not in df.columns:
        df["source"] = "seed_expansion"

    if limit is not None:
        df = df.head(int(limit)).copy()

    df["Combination"] = df["Combination"].astype(str)
    df["source"] = df["source"].astype(str)
    return df[["Combination", "source"]].copy()


# ------------------------------
# Gate: Seeds + RandomPass
# ------------------------------
def gate_random_pass(results_csv: Path, out_merge_csv: Path) -> Dict[str, Any]:
    df = pd.read_csv(results_csv)

    if "source" in df.columns:
        seeds = df[df["source"].astype(str) != "random"].copy()
        rands = df[df["source"].astype(str) == "random"].copy()
    else:
        seeds = df.copy()
        rands = df.iloc[0:0].copy()

    roi_p90 = float(pd.to_numeric(seeds["roi"], errors="coerce").quantile(0.90)) if len(seeds) else 0.0
    wr_med = float(pd.to_numeric(seeds["winrate"], errors="coerce").median()) if len(seeds) else 0.0

    rand_pass = rands[
        (pd.to_numeric(rands["roi"], errors="coerce") > roi_p90) &
        (pd.to_numeric(rands["winrate"], errors="coerce") > wr_med)
    ].copy()

    merged = pd.concat([seeds, rand_pass], ignore_index=True)

    backup_if_exists(out_merge_csv)
    merged.to_csv(out_merge_csv, index=False)

    return {
        "seed_rows": int(len(seeds)),
        "rand_rows": int(len(rands)),
        "rand_pass_rows": int(len(rand_pass)),
        "roi_p90_seed": roi_p90,
        "winrate_median_seed": wr_med,
        "merged_rows": int(len(merged)),
    }


# ------------------------------
# Main
# ------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--strategies-csv", required=True)
    p.add_argument("--price-csv", default="data/price_data_with_signals.csv")
    p.add_argument("--out-dir", default="results/k9_long")

    p.add_argument("--mode", choices=["smoke", "intermediate", "full"], default="smoke")
    p.add_argument("--smoke-n", type=int, default=200)
    p.add_argument("--intermediate-n", type=int, default=50000)

    p.add_argument("--num-procs", type=int, default=4)
    p.add_argument("--batch-write", type=int, default=50)      # < smoke-n => file appears early
    p.add_argument("--progress-step", type=int, default=10)    # prints only at 10%,20%,... like stable runs
    p.add_argument("--sharpe-cap", type=float, default=4.0)

    return p.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dir(Path(args.out_dir))

    # limit by mode
    limit = None
    if args.mode == "smoke":
        limit = int(args.smoke_n)
    elif args.mode == "intermediate":
        limit = int(args.intermediate_n)

    strat_df = load_strategies(args.strategies_csv, limit=limit)
    total = int(len(strat_df))
    if total == 0:
        raise RuntimeError("0 strategies loaded.")

    # Output paths
    ts = utc_ts()
    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    out_path = out_dir / f"strategy_results_k9_long_{args.mode.upper()}_{ts}.csv"
    merge_path = out_dir / f"strategy_results_k9_long_{args.mode.upper()}_{ts}_MERGE_SEEDS_PLUS_RANDOMPASS.csv"
    backup_if_exists(out_path)

    # write header now (so you see file immediately)
    cols = [
        "i", "direction", "Combination", "source",
        "roi", "winrate", "num_trades", "num_wins", "num_losses",
        "avg_hold", "sharpe", "sharpe_capped", "max_dd"
    ]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()

    log(f"Mode: {args.mode} | rows={total} | procs={args.num_procs} | batch_write={args.batch_write}")
    log(f"Writing: {out_path}")

    # Prepare work
    direction = "long"
    combos = strat_df["Combination"].tolist()
    sources = strat_df["source"].tolist()
    work: List[Tuple[int, str, str, float]] = [
        (i, combos[i], direction, float(args.sharpe_cap)) for i in range(total)
    ]

    # Map idx->source back in main (no worker touching stdout)
    idx_to_source = {i: sources[i] for i in range(total)}

    done = 0
    errors: List[Tuple[int, str]] = []
    buffer_rows: List[Dict[str, Any]] = []
    written = 0

    def flush(rows: List[Dict[str, Any]]) -> int:
        if not rows:
            return 0
        with out_path.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            for r in rows:
                w.writerow(r)
        return len(rows)

    t0 = time.time()
    last_pct = -1
    step = max(1, int(args.progress_step))

    with Pool(processes=int(args.num_procs), initializer=mp_init, initargs=(args.price_csv,)) as pool:
        for idx, res, err in pool.imap_unordered(mp_worker, work, chunksize=50):
            done += 1
            if err is not None:
                errors.append((idx, err))
                continue

            # add source in main process only
            res["source"] = idx_to_source.get(idx, "")

            buffer_rows.append(res)

            if len(buffer_rows) >= int(args.batch_write):
                written += flush(buffer_rows)
                buffer_rows = []

            pct = int((done / total) * 100)
            if pct != last_pct and (pct % step == 0 or pct == 100):
                elapsed = time.time() - t0
                rate = done / elapsed if elapsed > 0 else 0.0
                eta = (total - done) / rate if rate > 0 else 0.0
                log(f"[progress] {pct:3d}% ({done}/{total}) rate={rate:.2f}/s elapsed={elapsed/60:.1f}m eta={fmt_eta(eta)}")
                last_pct = pct

    if buffer_rows:
        written += flush(buffer_rows)
        buffer_rows = []

    log(f"[ok] Wrote analyze results: {out_path} (rows_written={written})")

    # Gate merge
    gate_stats = gate_random_pass(out_path, merge_path)
    log(f"[gate] SEED rows: {gate_stats['seed_rows']} p90 roi: {gate_stats['roi_p90_seed']} median winrate: {gate_stats['winrate_median_seed']}")
    log(f"[gate] RAND rows: {gate_stats['rand_rows']} pass: {gate_stats['rand_pass_rows']}")
    log(f"[ok] Wrote gated merged output: {merge_path}")

    if errors:
        # summarize only (avoid spam)
        log(f"[warn] Errors: {len(errors)} (first 5 shown)")
        for i, e in errors[:5]:
            log(f"  - idx={i}: {e}")


if __name__ == "__main__":
    main()




