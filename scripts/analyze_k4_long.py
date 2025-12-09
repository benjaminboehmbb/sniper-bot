#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
Analyze K4 LONG candidate strategies (evaluate ROI, winrate, num_trades) in parallel.

Inputs:
  --input-glob   Glob for one or more shard CSVs with column 'Combination'
  --out          Output CSV path (results). A timestamped backup is created if file exists.
  --num-procs    Worker processes (default: max(cpu_count()-1, 1))
  --batch-write  Rows per buffered write to disk (default: 10000)
  --limit        Optional hard cap on number of rows to evaluate (for smoke tests)
  --progress-step  Print progress every N percent (default: 2)

Requirements:
  - engine/simtrader.py with function evaluate_strategy(combination_dict) -> dict
    Expected return keys: roi, winrate, num_trades, pnl_sum

Notes:
  - ASCII-only logging (no Unicode)
  - Robust CSV parsing for 'Combination' strings (json or python-literal)
  - If SimTrader import fails, script aborts with clear message (no fake results)
"""

import argparse
import csv
import glob
import json
import os
import sys
from datetime import datetime
from multiprocessing import Pool, cpu_count
import ast

import pandas as pd

# ----------------------------
# Helpers
# ----------------------------

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True, help="Glob for input shard CSVs")
    ap.add_argument("--out", required=True, help="Output CSV path")
    ap.add_argument("--num-procs", type=int, default=max(1, cpu_count()-1))
    ap.add_argument("--batch-write", type=int, default=10000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--progress-step", type=int, default=2)
    return ap.parse_args()


def backup_if_exists(path: str) -> None:
    d = os.path.dirname(path) or "."
    os.makedirs(d, exist_ok=True)
    if os.path.exists(path):
        ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        bak = f"{os.path.splitext(path)[0]}_backup_{ts}.csv"
        os.replace(path, bak)
        print(f"[info] Existing output moved to backup: {bak}")


def parse_comb(text: str):
    # Try JSON
    try:
        d = json.loads(text)
        if isinstance(d, dict):
            return {str(k): float(v) for k, v in d.items()}
    except Exception:
        pass
    # Try literal
    try:
        d = ast.literal_eval(text)
        if isinstance(d, dict):
            return {str(k): float(v) for k, v in d.items()}
    except Exception:
        pass
    # Fallback " to '
    try:
        d = json.loads(text.replace("'", '"'))
        if isinstance(d, dict):
            return {str(k): float(v) for k, v in d.items()}
    except Exception:
        pass
    return None


# Try to load SimTrader
try:
    from engine.simtrader import evaluate_strategy
except Exception as e:
    print("[error] Could not import engine.simtrader.evaluate_strategy")
    print(f"[error] {e}")
    sys.exit(2)


DF = pd.read_csv("data/price_data_with_signals_regime.csv")

def _eval_one(row):
    comb_s = row["Combination"]
    comb_d = parse_comb(str(comb_s))
    if not comb_d:
        return None
    try:
        res = evaluate_strategy(0, comb_d, "long", df=DF)
    except Exception as e:
        return {"Combination": comb_s, "error": str(e)}
    out = {
        "Combination": comb_s,
        "roi": res.get("roi", 0.0),
        "winrate": res.get("winrate", 0.0),
        "num_trades": res.get("num_trades", 0),
        "pnl_sum": res.get("pnl_sum", 0.0),
    }
    return out


def main():
    args = parse_args()

    files = sorted(glob.glob(args.input_glob))
    if not files:
        print("[error] No input files match glob")
        sys.exit(1)

    print(f"[info] Input files: {len(files)}")
    for f in files:
        print(f"[info] + {f}")

    backup_if_exists(args.out)

    total_rows = 0
    for f in files:
        try:
            c = sum(1 for _ in open(f, "r", encoding="utf-8", errors="ignore")) - 1
        except Exception:
            c = 0
        if c > 0:
            total_rows += c

    if args.limit and args.limit > 0:
        total_rows = min(total_rows, args.limit)

    print(f"[info] Estimated rows to evaluate: {total_rows}")

    # Writer
    out_f = open(args.out, "w", newline="", encoding="utf-8")
    writer = csv.writer(out_f)
    writer.writerow(["Combination", "roi", "winrate", "num_trades", "pnl_sum"]) 

    # Pool
    procs = max(1, int(args.num_procs))
    print(f"[info] Using processes: {procs}")

    evaluated = 0
    pct_next = args.progress_step

    with Pool(processes=procs) as pool:
        def gen_rows():
            sent = 0
            for f in files:
                for chunk in pd.read_csv(f, usecols=["Combination"], chunksize=100000):
                    for _, r in chunk.iterrows():
                        yield r
                        sent += 1
                        if args.limit and sent >= args.limit:
                            return
        for res in pool.imap_unordered(_eval_one, gen_rows(), chunksize=512):
            if res is None:
                continue
            writer.writerow([res["Combination"], res.get("roi",0.0), res.get("winrate",0.0), res.get("num_trades",0), res.get("pnl_sum",0.0)])
            evaluated += 1
            # progress
            if total_rows > 0:
                pct = (evaluated * 100) // (total_rows if total_rows else 1)
                if pct >= pct_next:
                    print(f"[info] Progress {pct}% ({evaluated}/{total_rows})")
                    pct_next += args.progress_step

    out_f.flush(); out_f.close()
    print("[info] Done.")
    print(f"[info] Wrote results to: {args.out}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("[warn] Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"[error] {e}")
        sys.exit(1)
