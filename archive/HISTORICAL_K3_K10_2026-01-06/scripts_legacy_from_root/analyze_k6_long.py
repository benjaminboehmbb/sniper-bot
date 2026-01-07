# scripts/analyze_k6_long.py
# K6 LONG Analyzer (multiprocessing, robust imports, date-stamped outputs, batch flush)
#
# Input:
#   --candidates-csv : CSV with at least column "Combination" (and optional "source", "seed_rank")
#   --price-csv      : price_data_with_signals_regime.csv (or equivalent; must include OHLC + time column)
#
# Output:
#   results/k6_long/strategy_results_k6_long_<UTCSTAMP>.csv
#
# Notes:
# - Fixes the common WSL/mp import issue by injecting repo-root into sys.path inside workers.
# - Actively guards against timestamp/open_time column mismatch.
# - Never crashes per-strategy due to missing result attributes; errors are captured in "error" column.

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count
from typing import Any, Dict, Optional, Tuple

import pandas as pd


# ------------------------
# Helpers
# ------------------------
def utc_stamp() -> str:
    # Keep as-is; warning is harmless. (We can modernize later.)
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")


def log(msg: str) -> None:
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC] {msg}", flush=True)


def backup_if_exists(path: str) -> Optional[str]:
    """
    If output file exists, rename it with a timestamp backup suffix.
    """
    if os.path.exists(path):
        base, ext = os.path.splitext(path)
        bkp = f"{base}_backup_{utc_stamp()}{ext}"
        os.replace(path, bkp)
        return bkp
    return None


def load_price_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Active prevention: open_time vs timestamp mismatch
    if "timestamp" not in df.columns and "open_time" in df.columns:
        df["timestamp"] = df["open_time"]
    if "open_time" not in df.columns and "timestamp" in df.columns:
        df["open_time"] = df["timestamp"]

    required = ["open_time", "open", "high", "low", "close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"price csv missing columns {missing}. Found: {list(df.columns)}"
        )
    return df


# ------------------------
# Import / Engine hook
# ------------------------
def _ensure_repo_root_on_syspath() -> str:
    """
    Ensure repo root (sniper-bot/) is importable in this process.
    Critical for multiprocessing workers.
    Returns repo_root path.
    """
    this_file = os.path.abspath(__file__)
    repo_root = os.path.dirname(os.path.dirname(this_file))  # .../sniper-bot
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    return repo_root


def resolve_evaluator():
    """
    Prefer engine.simtrader.evaluate_strategy if present.
    Falls back to simtrader.evaluate_strategy at repo root.
    Ensures repo root on sys.path (important for mp workers).
    """
    _ensure_repo_root_on_syspath()

    try:
        from engine.simtrader import evaluate_strategy  # type: ignore
        return evaluate_strategy
    except Exception:
        pass

    try:
        from simtrader import evaluate_strategy  # type: ignore
        return evaluate_strategy
    except Exception as e:
        raise ImportError(
            f"Could not import evaluate_strategy. sys.path[0:5]={sys.path[0:5]}"
        ) from e


# ------------------------
# Result normalization
# ------------------------
def safe_result_dict(res: Any, combination: str, extra: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize output into a dict with stable columns.
    res can be dict-like or object-like.
    """
    out: Dict[str, Any] = {"Combination": combination}
    out.update(extra)

    def get(k: str) -> Any:
        if isinstance(res, dict):
            return res.get(k, None)
        return getattr(res, k, None)

    # common metrics
    out["roi"] = get("roi")
    out["winrate"] = get("winrate") or get("accuracy")
    out["num_trades"] = get("num_trades") or get("trades") or get("n_trades")
    out["avg_trade"] = get("avg_trade")
    out["profit_factor"] = get("profit_factor")
    out["sharpe"] = get("sharpe") or get("sharpe_ratio")
    out["max_dd"] = get("max_dd") or get("max_drawdown")

    # error channel (if res indicates)
    out["error"] = get("error")
    return out


# ------------------------
# Worker
# ------------------------
def worker_eval(args: Tuple[int, str, Dict[str, Any], str]) -> Dict[str, Any]:
    idx, combination, extra, price_csv_path = args

    # Lazy-load per process (workers)
    if not hasattr(worker_eval, "_eval"):
        worker_eval._eval = resolve_evaluator()  # type: ignore
        worker_eval._price = load_price_csv(price_csv_path)  # type: ignore

    evaluate_strategy = worker_eval._eval  # type: ignore
    price_df = worker_eval._price  # type: ignore

    try:
        # IMPORTANT: call signature may differ in your engine.
        # This matches the intended interface: evaluate_strategy(df, combination, side="long")
        res = evaluate_strategy(price_df, combination, side="long")
        return safe_result_dict(res, combination, extra)
    except Exception as e:
        d: Dict[str, Any] = {"Combination": combination}
        d.update(extra)
        d.update(
            {
                "roi": None,
                "winrate": None,
                "num_trades": None,
                "avg_trade": None,
                "profit_factor": None,
                "sharpe": None,
                "max_dd": None,
                "error": f"{type(e).__name__}: {e}",
            }
        )
        return d


# ------------------------
# Main
# ------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidates-csv", required=True, help="Candidate CSV with column Combination")
    ap.add_argument("--price-csv", required=True, help="Price CSV with signals already present")
    ap.add_argument("--out-dir", default="results/k6_long", help="Output directory")
    ap.add_argument(
        "--num-procs",
        type=int,
        default=max(2, min(16, cpu_count())),
        help="Worker processes",
    )
    ap.add_argument("--batch-write", type=int, default=5000, help="Write/flush every N rows")
    ap.add_argument("--progress-step", type=int, default=2, help="Progress print step in percent")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of candidates (0=all)")
    ap.add_argument("--chunksize", type=int, default=200, help="imap_unordered chunksize")
    args = ap.parse_args()

    # Ensure repo root on sys.path in main too (useful for non-mp)
    _ensure_repo_root_on_syspath()

    os.makedirs(args.out_dir, exist_ok=True)
    stamp = utc_stamp()

    out_path = os.path.join(args.out_dir, f"strategy_results_k6_long_{stamp}.csv")
    bkp = backup_if_exists(out_path)
    if bkp:
        log(f"Backed up existing output to: {bkp}")

    cand = pd.read_csv(args.candidates_csv)
    if "Combination" not in cand.columns:
        raise ValueError(
            f"Missing column 'Combination' in {args.candidates_csv}. Found: {list(cand.columns)}"
        )

    if args.limit and int(args.limit) > 0:
        cand = cand.head(int(args.limit)).copy()

    total = len(cand)
    log(f"Loaded candidates: {total} rows from {args.candidates_csv}")
    log(f"Using price csv: {args.price_csv}")
    log(f"num_procs={args.num_procs} batch_write={args.batch_write} progress_step={args.progress_step}% chunksize={args.chunksize}")

    # Preflight: verify we can import evaluator in main process
    try:
        _ = resolve_evaluator()
        log("Evaluator import OK (engine.simtrader preferred).")
    except Exception as e:
        raise RuntimeError(f"Evaluator import failed in main process: {e}") from e

    # Prepare tasks
    tasks = []
    has_source = "source" in cand.columns
    has_seed_rank = "seed_rank" in cand.columns

    for i, row in cand.iterrows():
        extra: Dict[str, Any] = {}
        if has_source:
            extra["source"] = row.get("source", "")
        if has_seed_rank:
            extra["seed_rank"] = row.get("seed_rank", "")
        tasks.append((int(i), str(row["Combination"]), extra, args.price_csv))

    # Stable output columns
    fieldnames = [
        "Combination",
        "source",
        "seed_rank",
        "roi",
        "winrate",
        "num_trades",
        "avg_trade",
        "profit_factor",
        "sharpe",
        "max_dd",
        "error",
    ]

    done = 0
    next_progress = 0
    t0 = time.time()

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()

        with Pool(processes=int(args.num_procs)) as pool:
            for res in pool.imap_unordered(worker_eval, tasks, chunksize=int(args.chunksize)):
                w.writerow(res)
                done += 1

                # periodic flush (durability)
                if done % int(args.batch_write) == 0:
                    f.flush()
                    os.fsync(f.fileno())

                # progress
                pct = int((done / total) * 100) if total else 100
                if pct >= next_progress:
                    elapsed = time.time() - t0
                    rate = done / elapsed if elapsed > 0 else 0.0
                    eta = (total - done) / rate if rate > 0 else 0.0
                    log(f"Progress: {pct}% ({done}/{total}) | rate={rate:.2f} rows/s | ETA={eta/60:.1f} min")
                    next_progress += int(args.progress_step)

    log(f"Done. Wrote: {out_path}")
    log("Next step (separate): apply merge rule for RANDOM using meta JSON thresholds (roi > seed_p90 AND winrate > seed_median).")


if __name__ == "__main__":
    main()

