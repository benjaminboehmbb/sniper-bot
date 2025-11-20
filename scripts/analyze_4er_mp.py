#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyze 4er combinations with multiprocessing (Windows-safe).
ASCII output; top-level worker; percent progress.

Example:
  PYTHONIOENCODING=UTF-8 python -u scripts/analyze_4er_mp.py \
    --data data/price_data_with_signals.csv \
    --strategies data/strategies_k4_shard1.csv \
    --n 200000 --num-procs 20 --chunksize 512 --progress_step 2 --sim long
"""

import argparse, ast, csv, datetime, json, math, os, time
from pathlib import Path
import numpy as np
import pandas as pd
from multiprocessing import Pool

DF_DATA = None
RET_NEXT = None
SIGNAL_COLS = None

def init_worker(data_path: str):
    global DF_DATA, RET_NEXT, SIGNAL_COLS
    t0 = time.time()
    df = pd.read_csv(data_path, low_memory=False)
    close = df["close"].astype(float)
    RET_NEXT = close.pct_change().shift(-1).fillna(0.0).to_numpy(dtype=np.float64)
    SIGNAL_COLS = [c for c in df.columns if c.endswith("_signal")]
    DF_DATA = df[["open_time"] + SIGNAL_COLS]
    print(f"[INIT] Data loaded in {time.time()-t0:.2f}s. rows={len(df)} signals={len(SIGNAL_COLS)}", flush=True)

def simulate_long(weights_map: dict) -> tuple:
    global DF_DATA, RET_NEXT, SIGNAL_COLS
    wsum = None
    for k, w in weights_map.items():
        col = f"{k}_signal"
        if col in SIGNAL_COLS and w != 0:
            sig = DF_DATA[col].to_numpy(dtype=np.float64)
            wsum = sig * float(w) if wsum is None else wsum + sig * float(w)
    if wsum is None:
        return (0.0, 0, 0.0, 0.0, 0.0, 0.0, 0, 0)

    pos = (wsum > 0.0).astype(np.int8)
    trades = int(pos.sum())
    if trades == 0:
        return (0.0, 0, 0.0, float((pos==1).mean()), 0.0, 0.0, 0, 0)

    pnl = float((RET_NEXT * pos).sum())
    ret_pos = RET_NEXT[pos == 1]
    winrate = float((ret_pos > 0).mean()) if len(ret_pos) else 0.0
    accuracy = float((pos == 1).mean())
    return (pnl*100.0, trades, winrate, accuracy, pnl*100.0, 0.0, trades, 0)

def parse_combo(cell: str) -> dict:
    try:
        m = ast.literal_eval(cell)
        return {str(k): float(v) for k, v in m.items() if float(v) != 0.0}
    except Exception:
        return {}

def worker_task(batch_rows):
    out_rows = []
    trades_rows = []
    for idx, combo_str in batch_rows:
        wmap = parse_combo(combo_str)
        roi, num_tr, winr, acc, roi_l, roi_s, n_l, n_s = simulate_long(wmap)
        out_rows.append((idx, combo_str, roi, num_tr, winr, acc, roi_l, roi_s, n_l, n_s))
    return out_rows, trades_rows

def main():
    ap = argparse.ArgumentParser(description="Analyze 4er combinations with multiprocessing (long only).")
    ap.add_argument("--data", required=True, help="CSV with price_data_with_signals")
    ap.add_argument("--strategies", required=True, help="CSV file with Combination column")
    ap.add_argument("--n", type=int, default=200000, help="max strategies to read from file")
    ap.add_argument("--num-procs", type=int, default=20, help="worker processes")
    ap.add_argument("--chunksize", type=int, default=512, help="strategies per worker task")
    ap.add_argument("--progress_step", type=int, default=2, help="progress percent step")
    ap.add_argument("--sim", choices=["long"], default="long", help="simulation mode")
    ap.add_argument("--save-trades", type=int, default=0, help="0/1 save trade rows (disabled)")
    args = ap.parse_args()

    df_s = pd.read_csv(args.strategies, usecols=["Combination"], nrows=args.n)
    combolist = list(df_s["Combination"].astype(str).values)
    total = len(combolist)

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outdir = Path(f"analysis_output_4er/{ts}")
    outdir.mkdir(parents=True, exist_ok=True)
    out_csv = outdir / f"strategy_results_4er_{ts}.csv"
    trades_csv = outdir / f"trades_4er_{ts}.csv"
    meta_dir = outdir

    run_meta = {
        "run_id": ts,
        "k": 4,
        "data": str(Path(args.data).resolve()),
        "strategies": str(Path(args.strategies).resolve()),
        "params": {
            "num_procs": args.num_procs,
            "chunksize": args.chunksize,
            "progress_step": args.progress_step,
            "sim": args.sim,
            "save_trades": args.save_trades,
        },
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    (meta_dir / "run_meta.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    chunk = args.chunksize
    tasks = []
    for i in range(0, total, chunk):
        batch = [(j, combolist[j]) for j in range(i, min(i+chunk, total))]
        tasks.append(batch)

    print(f"[RUN] Start: {total} strategies | Procs={args.num_procs} Chunk={args.chunksize}", flush=True)

    header = ["id","Combination","roi","num_trades","winrate","accuracy",
              "roi_long","roi_short","num_trades_long","num_trades_short"]
    with out_csv.open("w", newline="") as f_res:
        csv.writer(f_res).writerow(header)

    if args.save_trades:
        with trades_csv.open("w", newline="") as f_tr:
            csv.writer(f_tr).writerow(["id","timestamp","side","price","qty"])

    t0 = time.time()
    next_pct = args.progress_step
    done_rows = 0
    with Pool(processes=args.num_procs, initializer=init_worker, initargs=(args.data,)) as pool:
        for batch_res, _ in pool.imap_unordered(worker_task, tasks, chunksize=1):
            with out_csv.open("a", newline="") as f_res:
                csv.writer(f_res).writerows(batch_res)
            done_rows += sum(1 for _ in batch_res)

            pct = int(done_rows * 100 / total)
            if pct >= next_pct:
                print(f"[PROGRESS] {done_rows}/{total} = {pct:.1f}%  elapsed={time.time()-t0:.1f}s", flush=True)
                while next_pct <= pct:
                    next_pct += args.progress_step

    (meta_dir / "DONE").write_text(datetime.datetime.now(datetime.timezone.utc).isoformat(), encoding="utf-8")
    print(f"[DONE] results: {out_csv}")
    print(f"[TIME] elapsed {time.time()-t0:.1f}s")

if __name__ == "__main__":
    main()
