#folgende gitbash befehle:

#PYTHONIOENCODING=UTF-8 \
#python -u scripts/analyze_3er_mp.py \
# --data data/price_data_with_signals.csv \
  #--strategies data/strategies_k3_shard1.csv \
  #--threshold 0.60 \
  #--cooldown 0 \
  #--require-ma200 1 \
  #--min-trades 50 \
  #--max-trades 50000 \
  #--num-procs 12 \
  #--chunksize 512 \
  #--save-trades 0

 



#!/usr/bin/env python3
# analyze_3er_mp.py
# Normalized-score version. ASCII-only. Multiprocessing-ready.
# This file REPLACES the previous version.

import os
import sys
import time
import argparse
import ast
import hashlib
from datetime import datetime
from multiprocessing import Pool, cpu_count
import pandas as pd
import numpy as np

# ---------------- Basic utils ----------------
def now_ts():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def safe_makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def combo_hash(combo):
    s = str(sorted(combo.items()))
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:12]

# ---------------- Normalization ----------------
# Robust per-column min-max normalization to [0,1] with percentile clipping.
# Falls back to column min/max if percentiles are degenerate.

def robust_minmax(col_values):
    arr = col_values.astype(float)
    if np.all(np.isnan(arr)):
        return np.zeros_like(arr)
    # Replace NaN by column median temporarily
    med = np.nanmedian(arr)
    arr = np.where(np.isnan(arr), med, arr)
    q1 = np.percentile(arr, 1.0)
    q99 = np.percentile(arr, 99.0)
    lo = q1
    hi = q99
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        lo = np.nanmin(arr)
        hi = np.nanmax(arr)
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return np.zeros_like(arr)
    clipped = np.clip(arr, lo, hi)
    norm = (clipped - lo) / (hi - lo)
    return norm

def build_normalized_matrix(df, needed_cols):
    norm = {}
    for c in needed_cols:
        if c in df.columns:
            norm[c] = robust_minmax(df[c].to_numpy())
        else:
            norm[c] = np.zeros(len(df), dtype=float)
    return norm

# ---------------- Simulation ----------------

def simulate_strategy_long(
    df,
    combo,
    threshold=0.65,
    cooldown=60,
    max_hold=240,
    require_ma200=False,
    normalize_signals=True
):
    """
    Event-driven long-only simulation.
    Signals are normalized to [0,1] before weighting if normalize_signals is True.
    Only signals that EXIST in df are used; weights are renormalized over available signals.
    Entry when score > threshold and optional MA200 gate passes.
    Exit when score < threshold or max_hold exceeded.
    """
    # keep only signals that exist in df
    available = [k for k in combo.keys() if k in df.columns]
    if len(available) == 0:
        return {"num_trades": 0, "total_pnl": 0.0, "avg_pnl": 0.0, "winrate": 0.0}, []

    # renormalize weights over available-only
    sum_w = sum(abs(float(combo[k])) for k in available) or 1.0
    weights = {k: float(combo[k]) / sum_w for k in available}

    timestamps = df.index
    n = len(df)

    if normalize_signals:
        norm_map = build_normalized_matrix(df, available)
    else:
        norm_map = {c: (df[c].to_numpy(dtype=float) if c in df.columns else np.zeros(n, dtype=float)) for c in available}

    # Build score array in [0,1] due to normalization and weight renorm
    score_arr = np.zeros(n, dtype=float)
    for sig, w in weights.items():
        score_arr += w * norm_map[sig]

    trades = []
    in_pos = False
    entry_idx = None
    last_exit_time = None

    # MA200 gate preparation
    use_ma200_gate = False
    if require_ma200:
        if "ma200_signal" in df.columns:
            gate_series = df["ma200_signal"].astype(int).to_numpy()
            use_ma200_gate = True
        elif "close" in df.columns and "ma200" in df.columns:
            gate_series = (df["close"].to_numpy(dtype=float) > df["ma200"].to_numpy(dtype=float)).astype(int)
            use_ma200_gate = True
        else:
            use_ma200_gate = False

    for i in range(n - 1):
        score = score_arr[i]
        ma200_ok = True
        if require_ma200 and use_ma200_gate:
            ma200_ok = bool(gate_series[i])

        if in_pos:
            hold_minutes = (timestamps[i] - timestamps[entry_idx]).total_seconds() / 60.0
            if score < threshold or hold_minutes >= max_hold:
                entry_price = df["close"].iat[entry_idx + 1] if entry_idx + 1 < n else df["close"].iat[entry_idx]
                exit_price = df["close"].iat[i + 1] if i + 1 < n else df["close"].iat[i]
                ret = (exit_price / entry_price) - 1.0
                trades.append({
                    "entry_time": timestamps[entry_idx],
                    "exit_time": timestamps[i + 1] if i + 1 < n else timestamps[i],
                    "entry_price": float(entry_price),
                    "exit_price": float(exit_price),
                    "pnl": float(ret),
                })
                in_pos = False
                entry_idx = None
                last_exit_time = timestamps[i + 1] if i + 1 < n else timestamps[i]
            else:
                continue

        if not in_pos:
            if last_exit_time is not None:
                minutes_since_exit = (timestamps[i] - last_exit_time).total_seconds() / 60.0
                if minutes_since_exit < cooldown:
                    continue
            if score > threshold and ma200_ok:
                entry_idx = i
                in_pos = True
                if i + 1 >= n:
                    in_pos = False
                    entry_idx = None
                    break

    if in_pos and entry_idx is not None:
        entry_price = df["close"].iat[entry_idx + 1] if entry_idx + 1 < n else df["close"].iat[entry_idx]
        exit_price = df["close"].iat[-1]
        ret = (exit_price / entry_price) - 1.0
        trades.append({
            "entry_time": timestamps[entry_idx],
            "exit_time": timestamps[-1],
            "entry_price": float(entry_price),
            "exit_price": float(exit_price),
            "pnl": float(ret),
        })

    num_trades = len(trades)
    total_pnl = sum(t["pnl"] for t in trades) if trades else 0.0
    avg_pnl = (total_pnl / num_trades) if num_trades > 0 else 0.0
    winrate = (sum(1 for t in trades if t["pnl"] > 0) / num_trades) if num_trades > 0 else 0.0

    metrics = {
        "num_trades": int(num_trades),
        "total_pnl": float(total_pnl),
        "avg_pnl": float(avg_pnl),
        "winrate": float(winrate),
    }
    return metrics, trades

# ---------------- Worker ----------------

def worker_process(args):
    (strategy_row, df_sample, sim_params) = args
    combo_str = strategy_row.get("Combination") or strategy_row.get("combination") or ""
    try:
        combo = ast.literal_eval(combo_str)
        if not isinstance(combo, dict):
            raise ValueError("Combination not a dict")
    except Exception as e:
        return {"error": "bad_combo", "combo_str": combo_str, "msg": str(e)}

    try:
        metrics, trades = simulate_strategy_long(
            df_sample,
            combo,
            threshold=sim_params["threshold"],
            cooldown=sim_params["cooldown"],
            max_hold=sim_params["max_hold"],
            require_ma200=sim_params["require_ma200"],
            normalize_signals=sim_params["normalize_signals"],
        )
    except Exception as e:
        return {"error": "sim_error", "msg": str(e), "combo": combo_str}

    num_trades = metrics["num_trades"]
    if num_trades < sim_params["min_trades"] or num_trades > sim_params["max_trades"]:
        return {
            "combo": combo_str,
            "hash": combo_hash(combo),
            "num_trades": num_trades,
            "total_pnl": metrics["total_pnl"],
            "avg_pnl": metrics["avg_pnl"],
            "winrate": metrics["winrate"],
            "plausible": False,
            "reason": "trade_count_out_of_bounds",
        }

    return {
        "combo": combo_str,
        "hash": combo_hash(combo),
        "num_trades": num_trades,
        "total_pnl": metrics["total_pnl"],
        "avg_pnl": metrics["avg_pnl"],
        "winrate": metrics["winrate"],
        "plausible": True,
        "trades": trades if sim_params.get("save_trades", 0) else None,
    }

# ---------------- Main ----------------

def main():
    parser = argparse.ArgumentParser(description="Analyze 3er strategies (MP, normalized). ASCII-only logs.")
    parser.add_argument("--data", required=True, help="Price + signals CSV (index timestamp or column 'timestamp')")
    parser.add_argument("--strategies", required=True, help="CSV with column 'Combination' (dict string)")
    parser.add_argument("--sim", choices=["long"], default="long")
    parser.add_argument("--threshold", type=float, default=0.65)
    parser.add_argument("--cooldown", type=int, default=60)
    parser.add_argument("--max-hold", type=int, default=240)
    parser.add_argument("--require-ma200", type=int, default=0)
    parser.add_argument("--min-trades", type=int, default=50)
    parser.add_argument("--max-trades", type=int, default=50000)
    parser.add_argument("--num-procs", type=int, default=max(2, min(cpu_count(), 28)))
    parser.add_argument("--chunksize", type=int, default=512)
    parser.add_argument("--progress-step", type=int, default=2)
    parser.add_argument("--save-trades", type=int, default=0)
    parser.add_argument("--output-dir", default="results/3er")
    parser.add_argument("--normalize", type=int, default=1, help="1=normalize signals to 0..1 (recommended)")

    args = parser.parse_args()

    start = time.time()
    print("[INFO] analyze_3er_mp starting at", now_ts())
    print("[INFO] Loading price data:", args.data)

    df = pd.read_csv(args.data, index_col=0)
    # force datetime index to avoid numpy.timedelta64 issues in MP workers
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[df.index.notna()]
    if "close" not in df.columns:
        if "Close" in df.columns:
            df = df.rename(columns={"Close": "close"})
        else:
            print("[ERROR] 'close' column not found in data. Aborting.")
            sys.exit(1)

    print("[INFO] Loading strategies:", args.strategies)
    s_df = pd.read_csv(args.strategies)
    if "Combination" not in s_df.columns and "combination" not in s_df.columns:
        print("[ERROR] Strategy CSV missing 'Combination' column. Aborting.")
        sys.exit(1)

    safe_makedirs(args.output_dir)
    trades_dir = os.path.join(args.output_dir, "trades")
    safe_makedirs(trades_dir)

    out_name = "strategy_results_long_{}.csv".format(now_ts())
    out_path = os.path.join(args.output_dir, out_name)

    sim_params = {
        "threshold": args.threshold,
        "cooldown": args.cooldown,
        "max_hold": args.max_hold,
        "require_ma200": bool(args.require_ma200),
        "min_trades": args.min_trades,
        "max_trades": args.max_trades,
        "save_trades": args.save_trades,
        "normalize_signals": bool(args.normalize),
    }

    total = len(s_df)
    print("[INFO] Total strategies:", total)
    num_procs = max(1, args.num_procs)
    pool = Pool(processes=num_procs)

    tasks = []
    for _, row in s_df.iterrows():
        tasks.append((row.to_dict(), df, sim_params))

    results = []
    batch_size = args.chunksize
    processed = 0
    t0 = time.time()

    try:
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            res_batch = pool.map(worker_process, batch)
            results.extend(res_batch)
            processed += len(batch)
            elapsed = time.time() - t0
            pct = processed / total * 100.0
            print("[PROGRESS] {:3.1f}%  processed {}/{}  elapsed {:.1f}s".format(pct, processed, total, elapsed))
    except KeyboardInterrupt:
        print("[WARN] KeyboardInterrupt received. Terminating pool.")
        pool.terminate()
        pool.join()
        sys.exit(1)
    finally:
        pool.close()
        pool.join()

    good_rows = []
    for r in results:
        if isinstance(r, dict) and r.get("plausible"):
            good_rows.append({
                "Combination": r["combo"],
                "hash": r["hash"],
                "num_trades": r["num_trades"],
                "total_pnl": r["total_pnl"],
                "avg_pnl": r["avg_pnl"],
                "winrate": r["winrate"],
            })
            if args.save_trades and r.get("trades"):
                trades_file = os.path.join(trades_dir, "{}_trades.csv".format(r["hash"]))
                pd.DataFrame(r["trades"]).to_csv(trades_file, index=False)

    if good_rows:
        out_df = pd.DataFrame(good_rows)
        out_df.to_csv(out_path, index=False)
        print("[INFO] Saved plausible strategies:", out_path)
    else:
        print("[INFO] No plausible strategies found with the current filters. No result file created.")

    elapsed_total = time.time() - start
    print("[INFO] analyze_3er_mp finished. elapsed {:.1f}s".format(elapsed_total))

if __name__ == "__main__":
    main()







