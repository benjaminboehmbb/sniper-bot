#!/usr/bin/env python3
# ASCII-only. Fast single-process 3er benchmark (vectorized, Numba-ready).
# ADD: scripts/analyze_3er_fast_bench.py

import os
import sys
import argparse
from datetime import datetime
import ast
import numpy as np
import pandas as pd

def now_ts():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def robust_minmax(arr):
    a = arr.astype(float)
    if a.size == 0:
        return a
    med = np.nanmedian(a)
    a = np.where(np.isnan(a), med, a)
    q1, q99 = np.percentile(a, 1), np.percentile(a, 99)
    if not (np.isfinite(q1) and np.isfinite(q99) and q99 > q1):
        lo, hi = np.nanmin(a), np.nanmax(a)
    else:
        lo, hi = q1, q99
    if not (np.isfinite(lo) and np.isfinite(hi) and hi > lo):
        return np.zeros_like(a)
    a = np.clip(a, lo, hi)
    return (a - lo) / (hi - lo)

def build_norm_map(df, cols):
    norm = {}
    for c in cols:
        if c in df.columns:
            norm[c] = robust_minmax(df[c].to_numpy())
        else:
            norm[c] = None
    return norm

def simulate_long(score, timestamps, close, threshold, cooldown, max_hold, gate):
    in_pos = False
    entry_idx = None
    last_exit = None
    trades = []

    n = len(score)
    for i in range(n - 1):
        if in_pos:
            hold = (timestamps[i] - timestamps[entry_idx]).total_seconds() / 60.0
            if score[i] < threshold or hold >= max_hold:
                eidx = entry_idx
                xidx = i + 1 if i + 1 < n else i
                if close is not None:
                    entry_px = close[eidx + 1] if eidx + 1 < n else close[eidx]
                    exit_px  = close[xidx]
                    pnl = (exit_px / entry_px) - 1.0
                else:
                    pnl = 0.0
                trades.append((eidx, xidx, pnl))
                in_pos = False
                entry_idx = None
                last_exit = timestamps[xidx]
            else:
                continue

        if not in_pos:
            if last_exit is not None:
                mins_since = (timestamps[i] - last_exit).total_seconds() / 60.0
                if mins_since < cooldown:
                    continue
            if score[i] > threshold and (gate[i] == 1):
                entry_idx = i
                in_pos = True
                if i + 1 >= n:
                    in_pos = False
                    entry_idx = None
                    break

    if in_pos and entry_idx is not None:
        eidx = entry_idx
        xidx = n - 1
        if close is not None:
            entry_px = close[eidx + 1] if eidx + 1 < n else close[eidx]
            exit_px  = close[xidx]
            pnl = (exit_px / entry_px) - 1.0
        else:
            pnl = 0.0
        trades.append((eidx, xidx, pnl))

    num_trades = len(trades)
    if num_trades > 0:
        pnls = [t[2] for t in trades]
        total = float(np.sum(pnls))
        avg = float(total / num_trades)
        win = float(np.sum(np.array(pnls) > 0) / num_trades)
    else:
        total = 0.0
        avg = 0.0
        win = 0.0
    return num_trades, total, avg, win

def parse_args():
    p = argparse.ArgumentParser(description="Fast single-process 3er benchmark (vectorized, Numba-ready).")
    p.add_argument("--data", required=True, help="CSV with signals and close; index is timestamp column")
    p.add_argument("--strategies", required=True, help="CSV with column 'Combination' (dict string, *_signal keys recommended)")
    p.add_argument("--n", type=int, default=2000, help="Number of strategies to evaluate (from top of file)")
    p.add_argument("--threshold", type=float, default=0.60)
    p.add_argument("--cooldown", type=int, default=0)
    p.add_argument("--max-hold", type=int, default=240)
    p.add_argument("--require-ma200", type=int, default=1)
    p.add_argument("--min-trades", type=int, default=50)
    p.add_argument("--max-trades", type=int, default=50000)
    p.add_argument("--output-dir", default="results/3er")
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    print("[INFO] fast_bench starting", now_ts())
    print("[INFO] loading data:", args.data)

    df = pd.read_csv(args.data, index_col=0)
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[df.index.notna()]
    nrows = len(df)
    if nrows == 0:
        print("[ERROR] empty data after datetime parsing"); sys.exit(1)

    close = df["close"].to_numpy(dtype=float) if "close" in df.columns else None
    timestamps = df.index.to_numpy()

    # Gate
    if args.require_ma200 and "ma200_signal" in df.columns:
        gate = df["ma200_signal"].astype(int).to_numpy()
    elif args.require_ma200 and ("close" in df.columns and "ma200" in df.columns):
        gate = (df["close"].to_numpy(dtype=float) > df["ma200"].to_numpy(dtype=float)).astype(int)
    else:
        gate = np.ones(nrows, dtype=int)

    # Prepare normalized maps for signal columns only once
    sig_cols = [c for c in df.columns if c.endswith("_signal")]
    norm_map = build_norm_map(df, sig_cols)

    print("[INFO] loading strategies:", args.strategies)
    s_df = pd.read_csv(args.strategies)
    if "Combination" not in s_df.columns and "combination" not in s_df.columns:
        print("[ERROR] 'Combination' column not found"); sys.exit(1)

    s_col = "Combination" if "Combination" in s_df.columns else "combination"
    total_strats = len(s_df)
    take = min(args.n, total_strats)
    print("[INFO] strategies total:", total_strats, "evaluating:", take)

    out_rows = []
    checked = 0
    for idx in range(take):
        combo_str = s_df.iloc[idx][s_col]
        try:
            combo = ast.literal_eval(combo_str)
            if not isinstance(combo, dict):
                continue
        except Exception:
            continue

        # keep available signals only
        avail = [k for k in combo.keys() if k in norm_map and norm_map[k] is not None]
        if not avail:
            continue

        # renormalize weights
        sw = sum(abs(float(combo[k])) for k in avail) or 1.0
        weights = {k: float(combo[k]) / sw for k in avail}

        # build score
        score = np.zeros(nrows, dtype=float)
        for k, w in weights.items():
            score += w * norm_map[k]

        # simulate
        num_trades, total_pnl, avg_pnl, winrate = simulate_long(
            score=score,
            timestamps=timestamps,
            close=close,
            threshold=args.threshold,
            cooldown=args.cooldown,
            max_hold=args.max_hold,
            gate=gate
        )

        # filter
        if num_trades < args.min_trades or num_trades > args.max_trades:
            checked += 1
            if checked % 200 == 0:
                print("[PROGRESS]", checked, "/", take)
            continue

        out_rows.append({
            "Combination": combo_str,
            "num_trades": int(num_trades),
            "total_pnl": float(total_pnl),
            "avg_pnl": float(avg_pnl),
            "winrate": float(winrate)
        })
        checked += 1
        if checked % 200 == 0:
            print("[PROGRESS]", checked, "/", take)

    ts = now_ts()
    out_path = os.path.join(args.output_dir, f"strategy_results_long_fast_{ts}.csv")
    if out_rows:
        pd.DataFrame(out_rows).to_csv(out_path, index=False)
        print("[INFO] saved:", out_path, "rows:", len(out_rows))
    else:
        print("[INFO] no strategies in band; no file written")

    print("[INFO] fast_bench finished", now_ts())

if __name__ == "__main__":
    main()
