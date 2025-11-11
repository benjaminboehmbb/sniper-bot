#!/usr/bin/env python3
# ASCII only
"""
Extract and analyze the ('mfi','rsi') cluster.

Inputs:
- cluster_rows_top_keysets.csv  (from cluster_analysis)
  Columns required: Combination, roi, winrate, num_trades
  Combination is a python-dict-like string, e.g. "{'mfi': 0.6, 'rsi': 0.4}"

Outputs (to given out_dir):
- mfi_rsi_strategies.csv          (clean rows with mfi,rsi weights as columns)
- summary.csv                     (count, roi_mean/median/std, winrate_mean, trades_mean, best_roi)
- weight_stats.csv                (per-signal weight mean/std/min/max)
- grid_counts.csv                 (pivot by (mfi_weight, rsi_weight): count and roi_mean)
- top20.csv                       (top 20 rows by roi desc)
- best_row.json                   (best single row by roi)
"""

import sys, os, ast, json
import pandas as pd
import numpy as np
from datetime import datetime

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print("[{} UTC] {}".format(ts, msg), flush=True)

def parse_combo(cell):
    if isinstance(cell, dict):
        return cell
    try:
        return ast.literal_eval(str(cell))
    except Exception:
        return {}

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/extract_and_analyze_mfi_rsi.py <cluster_rows_top_keysets.csv> <out_dir>")
        sys.exit(2)

    in_csv = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    log("Loading {}".format(in_csv))
    df = pd.read_csv(in_csv)

    need = {"Combination", "roi", "winrate", "num_trades"}
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise SystemExit("Missing columns: {}".format(", ".join(miss)))

    # parse Combination
    combos = df["Combination"].map(parse_combo)
    df["_combo"] = combos

    # keep rows that have exactly mfi and rsi
    def is_mfi_rsi(d):
        if not isinstance(d, dict):
            return False
        ks = set(k.lower() for k in d.keys())
        return ks == {"mfi", "rsi"}

    m = df["_combo"].map(is_mfi_rsi)
    sub = df.loc[m].copy()
    if len(sub) == 0:
        raise SystemExit("No rows with exactly ('mfi','rsi') found.")

    # extract weights
    def get_w(d, k):
        for kk, vv in d.items():
            if str(kk).lower() == k:
                try:
                    return float(vv)
                except Exception:
                    return None
        return None

    sub["mfi_weight"] = sub["_combo"].map(lambda d: get_w(d, "mfi"))
    sub["rsi_weight"] = sub["_combo"].map(lambda d: get_w(d, "rsi"))

    # clean columns
    keep_cols = ["Combination", "mfi_weight", "rsi_weight", "roi", "winrate", "num_trades"]
    sub = sub[keep_cols].copy()
    out_main = os.path.join(out_dir, "mfi_rsi_strategies.csv")
    sub.to_csv(out_main, index=False)

    # summary
    summary = {
        "count": int(len(sub)),
        "roi_mean": float(sub["roi"].mean()),
        "roi_median": float(sub["roi"].median()),
        "roi_std": float(sub["roi"].std(ddof=1)) if len(sub) > 1 else 0.0,
        "winrate_mean": float(sub["winrate"].mean()),
        "num_trades_mean": float(sub["num_trades"].mean()),
        "best_roi": float(sub["roi"].max()),
    }
    pd.DataFrame([summary]).to_csv(os.path.join(out_dir, "summary.csv"), index=False)

    # weight stats
    ws = []
    for sig, col in [("mfi", "mfi_weight"), ("rsi", "rsi_weight")]:
        arr = sub[col].astype(float).values
        ws.append({
            "signal": sig,
            "weight_mean": float(np.mean(arr)),
            "weight_std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
            "weight_min": float(np.min(arr)),
            "weight_max": float(np.max(arr)),
        })
    pd.DataFrame(ws).to_csv(os.path.join(out_dir, "weight_stats.csv"), index=False)

    # grid counts and mean ROI (rounded to one decimal)
    def r01(x):
        try:
            return float(np.round(float(x), 1))
        except Exception:
            return np.nan

    sub["_mfi_r"] = sub["mfi_weight"].map(r01)
    sub["_rsi_r"] = sub["rsi_weight"].map(r01)

    grid = sub.groupby(["_mfi_r", "_rsi_r"]).agg(
        count=("roi", "size"),
        roi_mean=("roi", "mean")
    ).reset_index().rename(columns={"_mfi_r": "mfi_weight", "_rsi_r": "rsi_weight"})
    grid.to_csv(os.path.join(out_dir, "grid_counts.csv"), index=False)

    # top20
    top20 = sub.sort_values("roi", ascending=False).head(20)
    top20.to_csv(os.path.join(out_dir, "top20.csv"), index=False)

    # best single row as json
    best_row = sub.sort_values("roi", ascending=False).head(1).iloc[0].to_dict()
    with open(os.path.join(out_dir, "best_row.json"), "w", encoding="utf-8") as f:
        json.dump(best_row, f, ensure_ascii=True, indent=2)

    log("Wrote: {}, summary.csv, weight_stats.csv, grid_counts.csv, top20.csv, best_row.json".format(out_main))
    log("Done.")

if __name__ == "__main__":
    main()
