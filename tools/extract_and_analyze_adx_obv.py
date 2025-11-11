#!/usr/bin/env python3
# ASCII only
"""
Extract and analyze the ('adx','obv') short cluster.

Inputs:
- strategy_results.csv from the short-sweep (with column 'Combination')

Outputs (to <out_dir>):
  adx_obv_strategies.csv      rows containing exactly adx+obv
  summary.csv                 basic statistics
  weight_stats.csv            per-signal weight means/stds
  grid_counts.csv             pivot by (adx_weight, obv_weight)
  top20.csv                   top 20 rows by ROI
  best_row.json               best single row
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
        print("Usage: python tools/extract_and_analyze_adx_obv.py <strategy_results.csv> <out_dir>")
        sys.exit(2)

    in_csv = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    log("Loading {}".format(in_csv))
    df = pd.read_csv(in_csv)
    if "Combination" not in df.columns:
        raise SystemExit("Column 'Combination' missing.")

    # parse combinations
    combos = df["Combination"].map(parse_combo)
    df["_combo"] = combos

    def is_adx_obv(d):
        if not isinstance(d, dict):
            return False
        ks = set(k.lower() for k in d.keys())
        return ks == {"adx_signal", "obv_signal"}

    sub = df[df["_combo"].map(is_adx_obv)].copy()
    if len(sub) == 0:
        raise SystemExit("No rows found with ('adx_signal','obv_signal').")

    def get_w(d, key):
        for kk, vv in d.items():
            if str(kk).lower() == key:
                try:
                    return float(vv)
                except Exception:
                    return None
        return None

    sub["adx_weight"] = sub["_combo"].map(lambda d: get_w(d, "adx_signal"))
    sub["obv_weight"] = sub["_combo"].map(lambda d: get_w(d, "obv_signal"))

    keep = ["Combination","adx_weight","obv_weight","roi","winrate","num_trades"]
    sub = sub[keep].copy()
    main_out = os.path.join(out_dir, "adx_obv_strategies.csv")
    sub.to_csv(main_out, index=False)

    summary = {
        "count": int(len(sub)),
        "roi_mean": float(sub["roi"].mean()),
        "roi_median": float(sub["roi"].median()),
        "roi_std": float(sub["roi"].std(ddof=1)) if len(sub)>1 else 0.0,
        "winrate_mean": float(sub["winrate"].mean()),
        "trades_mean": float(sub["num_trades"].mean()),
        "best_roi": float(sub["roi"].max())
    }
    pd.DataFrame([summary]).to_csv(os.path.join(out_dir, "summary.csv"), index=False)

    ws = []
    for sig,col in [("adx","adx_weight"),("obv","obv_weight")]:
        arr = sub[col].astype(float).values
        ws.append({
            "signal": sig,
            "weight_mean": float(np.mean(arr)),
            "weight_std": float(np.std(arr, ddof=1)) if len(arr)>1 else 0.0,
            "weight_min": float(np.min(arr)),
            "weight_max": float(np.max(arr))
        })
    pd.DataFrame(ws).to_csv(os.path.join(out_dir, "weight_stats.csv"), index=False)

    def r01(x):
        try: return float(np.round(float(x),1))
        except: return np.nan

    sub["_adx_r"]=sub["adx_weight"].map(r01)
    sub["_obv_r"]=sub["obv_weight"].map(r01)

    grid=sub.groupby(["_adx_r","_obv_r"]).agg(
        count=("roi","size"),
        roi_mean=("roi","mean")
    ).reset_index().rename(columns={"_adx_r":"adx_weight","_obv_r":"obv_weight"})
    grid.to_csv(os.path.join(out_dir,"grid_counts.csv"),index=False)

    top20=sub.sort_values("roi",ascending=False).head(20)
    top20.to_csv(os.path.join(out_dir,"top20.csv"),index=False)

    best=top20.iloc[0].to_dict()
    with open(os.path.join(out_dir,"best_row.json"),"w",encoding="utf-8") as f:
        json.dump(best,f,ensure_ascii=True,indent=2)

    log("Wrote: {}, summary.csv, weight_stats.csv, grid_counts.csv, top20.csv, best_row.json".format(main_out))
    log("Done.")

if __name__=="__main__":
    main()
