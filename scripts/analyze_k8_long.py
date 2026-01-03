#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyze K8 strategies (LONG/SHORT) - Windows spawn safe.

Based on scripts/analyze_k7_long.py (same engine/evaluator contract).
Evaluator signature required:
  evaluate_strategy(price_df, comb, direction)

Usage (WSL, repo root):
  python3 scripts/analyze_k8_long.py \
    --input-glob "results/k8_long/strategies_k8_long_RANDOM_....csv" \
    --price-csv "data/price_data_with_signals.csv" \
    --direction long \
    --num-procs 28 \
    --batch-write 2000 \
    --limit 1000
"""

from __future__ import annotations

import argparse
import ast
import csv
import glob
import json
import os
import sys
import time
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


# -----------------------------
# Hard path fix (critical for Windows spawn)
# -----------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# -----------------------------
# Globals for worker processes
# -----------------------------
_EVAL_FN = None
_PRICE_DF: Optional[pd.DataFrame] = None


# -----------------------------
# Logging / time
# -----------------------------
def utc_ts_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts} UTC] {msg}", flush=True)


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def backup_if_exists(out_path: Path) -> Optional[Path]:
    if out_path.exists():
        stamp = utc_ts_compact()
        backup = out_path.with_name(out_path.stem + f"_backup_{stamp}" + out_path.suffix)
        out_path.replace(backup)
        return backup
    return None


# -----------------------------
# Parse Combination
# -----------------------------
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


# -----------------------------
# Evaluator loading
# -----------------------------
def import_evaluator() -> None:
    global _EVAL_FN
    if _EVAL_FN is not None:
        return

    try:
        from engine.simtrader import evaluate_strategy  # type: ignore
        _EVAL_FN = evaluate_strategy
        log("Using engine.simtrader.evaluate_strategy.")
        return
    except Exception as e:
        log(f"[warn] Could not import engine.simtrader.evaluate_strategy: {e}")

    try:
        from simtrader import evaluate_strategy  # type: ignore
        _EVAL_FN = evaluate_strategy
        log("Using simtrader.evaluate_strategy.")
        return
    except Exception as e:
        log(f"[error] Could not import simtrader.evaluate_strategy: {e}")

    raise ImportError("No evaluate_strategy found. Ensure engine/simtrader.py provides evaluate_strategy().")


def coerce_strategy_obj_to_dict(obj: Any) -> Dict[str, Any]:
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj):
        return asdict(obj)

    d: Dict[str, Any] = {}
    for k in ["roi", "winrate", "num_trades", "num_wins", "num_losses", "avg_hold", "sharpe", "max_dd"]:
        if hasattr(obj, k):
            try:
                d[k] = getattr(obj, k)
            except Exception:
                pass
    return d


# -----------------------------
# Price data
# -----------------------------
def load_price_data(price_csv: str) -> pd.DataFrame:
    path = Path(price_csv)
    if not path.exists():
        raise FileNotFoundError(f"Price CSV not found: {price_csv}")
    return pd.read_csv(path)


def init_context(price_csv: str) -> None:
    global _PRICE_DF
    import_evaluator()
    _PRICE_DF = load_price_data(price_csv)


# -----------------------------
# TOP-LEVEL multiprocessing hooks (pickleable)
# -----------------------------
def mp_init(price_csv: str) -> None:
    # Ensure repo root is always in sys.path inside worker
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    init_context(price_csv)


def mp_worker(args: Tuple[int, str, str]) -> Tuple[int, Dict[str, Any], Optional[str]]:
    idx, comb_str, direction = args
    try:
        if _PRICE_DF is None:
            raise RuntimeError("PRICE_DF not initialized in worker.")
        comb = parse_combination(comb_str)
        out = _EVAL_FN(_PRICE_DF, comb, direction)  # type: ignore
        d = coerce_strategy_obj_to_dict(out)

        res: Dict[str, Any] = {"i": idx, "direction": direction, "Combination": comb_str}
        for k in ["roi", "winrate", "num_trades", "num_wins", "num_losses", "avg_hold", "sharpe", "max_dd"]:
            if k in d:
                res[k] = d[k]
        return idx, res, None
    except Exception as e:
        return idx, {"i": idx, "direction": direction, "Combination": comb_str}, f"{type(e).__name__}: {e}"


# -----------------------------
# Strategies IO
# -----------------------------
def load_strategies(input_glob: str, limit: Optional[int] = None) -> pd.DataFrame:
    files = sorted(glob.glob(input_glob))
    if not files:
        raise FileNotFoundError(f"No files matched --input-glob: {input_glob}")

    log(f"Loading strategies from {len(files)} file(s).")
    dfs: List[pd.DataFrame] = [pd.read_csv(fp) for fp in files]
    df_all = pd.concat(dfs, ignore_index=True)

    if "Combination" not in df_all.columns:
        for alt in ["strategy", "Strategy", "combination", "CombinationStr"]:
            if alt in df_all.columns:
                df_all = df_all.rename(columns={alt: "Combination"})
                break
    if "Combination" not in df_all.columns:
        raise KeyError("Missing required column 'Combination' in input strategies CSV(s).")

    if limit is not None and limit > 0:
        df_all = df_all.iloc[:limit].copy()

    log(f"Strategies loaded: {len(df_all)} rows.")
    return df_all


# -----------------------------
# Runner
# -----------------------------
def run_sequential(
    combos: List[str],
    direction: str,
    out_path: Path,
    batch_write: int,
    progress_step: int,
) -> Tuple[int, List[Tuple[int, str]]]:
    cols = ["i", "direction", "roi", "winrate", "num_trades", "num_wins", "num_losses", "avg_hold", "sharpe", "max_dd", "Combination"]

    total = len(combos)
    started = time.time()

    buffer_rows: List[Dict[str, Any]] = []
    errors: List[Tuple[int, str]] = []
    written = 0
    done = 0
    last_progress = -1

    def flush(rows: List[Dict[str, Any]]) -> int:
        if not rows:
            return 0
        with out_path.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            for r in rows:
                w.writerow(r)
        return len(rows)

    for i, comb_str in enumerate(combos):
        _, res, err = mp_worker((i, comb_str, direction))
        done += 1
        if err is not None:
            errors.append((i, err))
        else:
            buffer_rows.append(res)

        if len(buffer_rows) >= batch_write:
            written += flush(buffer_rows)
            buffer_rows = []

        if progress_step > 0:
            pct = int((done / total) * 100)
            if pct >= last_progress + progress_step:
                last_progress = pct
                elapsed = time.time() - started
                rate = done / elapsed if elapsed > 0 else 0.0
                eta = (total - done) / rate if rate > 0 else 0.0
                log(f"Progress: {pct}% (done={done}/{total}) rate={rate:.2f}/s eta={eta/60:.1f}m")

    if buffer_rows:
        written += flush(buffer_rows)

    elapsed = time.time() - started
    log(f"Done. Written rows: {written}. Elapsed: {elapsed/60:.1f} minutes.")
    return written, errors


def run(
    df: pd.DataFrame,
    direction: str,
    num_procs: int,
    out_path: Path,
    batch_write: int,
    progress_step: int,
    price_csv: str,
) -> None:
    ensure_parent_dir(out_path)
    backup = backup_if_exists(out_path)
    if backup is not None:
        log(f"Backed up existing output to: {backup}")

    cols = ["i", "direction", "roi", "winrate", "num_trades", "num_wins", "num_losses", "avg_hold", "sharpe", "max_dd", "Combination"]
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()

    log(f"Output: {out_path}")
    log(f"Price CSV: {price_csv}")
    log(f"Starting evaluation: total={len(df)}, num_procs={num_procs}, batch_write={batch_write}")

    combos = df["Combination"].astype(str).tolist()

    # Init context in main process (needed for sequential path)
    init_context(price_csv)

    if num_procs <= 1:
        written, errors = run_sequential(combos, direction, out_path, batch_write, progress_step)
        _ = written
    else:
        from multiprocessing import Pool

        total = len(combos)
        started = time.time()
        done = 0
        last_progress = -1

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

        work = [(i, combos[i], direction) for i in range(total)]

        with Pool(processes=num_procs, initializer=mp_init, initargs=(price_csv,)) as pool:
            for idx, res, err in pool.imap_unordered(mp_worker, work, chunksize=50):
                done += 1
                if err is not None:
                    errors.append((idx, err))
                else:
                    buffer_rows.append(res)

                if len(buffer_rows) >= batch_write:
                    written += flush(buffer_rows)
                    buffer_rows = []

                if progress_step > 0:
                    pct = int((done / total) * 100)
                    if pct >= last_progress + progress_step:
                        last_progress = pct
                        elapsed = time.time() - started
                        rate = done / elapsed if elapsed > 0 else 0.0
                        eta = (total - done) / rate if rate > 0 else 0.0
                        log(f"Progress: {pct}% (done={done}/{total}) rate={rate:.2f}/s eta={eta/60:.1f}m")

        if buffer_rows:
            written += flush(buffer_rows)

        elapsed = time.time() - started
        log(f"Done. Written rows: {written}. Elapsed: {elapsed/60:.1f} minutes.")

    if errors:
        err_path = out_path.with_suffix(".errors.txt")
        with err_path.open("w", encoding="utf-8") as f:
            for i, msg in errors[:20000]:
                f.write(f"{i}\t{msg}\n")
        log(f"Errors: {len(errors)} (first 20000 saved to {err_path})")
    else:
        log("Errors: 0")


# -----------------------------
# CLI
# -----------------------------
def ksep() -> str:
    return "\\" if os.name == "nt" else "/"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze K8 strategies.")
    p.add_argument("--input-glob", required=True, help="Input strategies CSV path or glob (must contain Combination).")
    p.add_argument("--price-csv", default="data/price_data_with_signals.csv", help="Price data CSV used by evaluator.")
    p.add_argument("--out", default=f"results{ksep()}k8_long{ksep()}strategy_results_k8_long_{utc_ts_compact()}.csv", help="Output CSV path")
    p.add_argument("--direction", default="long", choices=["long", "short"], help="Direction")
    p.add_argument("--num-procs", type=int, default=1, help="Processes")
    p.add_argument("--batch-write", type=int, default=5000, help="Flush every N successful rows")
    p.add_argument("--progress-step", type=int, default=2, help="Progress print step in percent")
    p.add_argument("--limit", type=int, default=0, help="Optional row limit (0=no limit)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    limit = args.limit if args.limit and args.limit > 0 else None
    df = load_strategies(args.input_glob, limit=limit)
    out_path = Path(args.out)

    run(
        df=df,
        direction=args.direction,
        num_procs=int(args.num_procs),
        out_path=out_path,
        batch_write=int(args.batch_write),
        progress_step=int(args.progress_step),
        price_csv=str(args.price_csv),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
