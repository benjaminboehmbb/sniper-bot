#!/usr/bin/env python3
# ASCII only
"""
Analyze robust strategy cluster:
- Input CSV must contain columns: Combination, roi, winrate, num_trades
- Combination is a Python-dict-like string, e.g. "{'rsi': 0.4, 'macd': 0.6}"

Outputs:
1) cluster_summary_by_keyset.csv
   Per unique signal key-set (e.g., ('rsi','macd')):
     count, share, roi_mean, roi_median, roi_std, roi_best,
     winrate_mean, trades_mean

2) weights_stats_by_signal.csv
   For each individual signal across all rows:
     weight_mean, weight_std, weight_min, weight_max, rows_with_signal, share

3) cluster_top20_keysets.csv
   Top 20 key-sets ranked by roi_mean (desc)

4) cluster_rows_top_keysets.csv
   All original rows for the best key-set (rank 1) with columns:
     Combination, roi, winrate, num_trades
"""

import sys, os, ast, json
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
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

def norm_keyset(d):
    # sorted tuple of signal names
    return tuple(sorted(d.keys()))

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/analyze_robust_cluster.py <input_csv> <output_dir>")
        sys.exit(2)

    in_csv = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    log("Loading {}".format(in_csv))
    df = pd.read_csv(in_csv)

    # sanity checks
    need = {"Combination","roi","winrate","num_trades"}
    miss = [c for c in need if c not in df.columns]
    if miss:
        raise SystemExit("Missing columns: {}".format(", ".join(miss)))

    # drop rows without trades
    df = df[df["num_trades"] > 0].copy()
    if len(df) == 0:
        raise SystemExit("No rows with num_trades > 0")

    # parse Combination to dict
    combos = df["Combination"].map(parse_combo)
    df["_combo"] = combos
    df["_keyset"] = combos.map(norm_keyset)

    # --- 1) Summary per key-set ---
    records = []
    total = len(df)
    for kset, g in df.groupby("_keyset"):
        rec = {
            "keyset": str(kset),
            "count": int(len(g)),
            "share": float(len(g)) / float(total),
            "roi_mean": float(g["roi"].mean()),
            "roi_median": float(g["roi"].median()),
            "roi_std": float(g["roi"].std(ddof=1)) if len(g) > 1 else 0.0,
            "roi_best": float(g["roi"].max()),
            "winrate_mean": float(g["winrate"].mean()),
            "trades_mean": float(g["num_trades"].mean()),
        }
        records.append(rec)
    keyset_df = pd.DataFrame(records).sort_values(["roi_mean","roi_best"], ascending=[False, False])
    keyset_out = os.path.join(out_dir, "cluster_summary_by_keyset.csv")
    keyset_df.to_csv(keyset_out, index=False)
    log("Wrote {}".format(keyset_out))

    # --- 2) Weight stats per signal ---
    # flatten weights per signal
    weight_map = defaultdict(list)  # signal -> list of weights
    rows_with_signal = Counter()
    for row in df["_combo"]:
        if not isinstance(row, dict):
            continue
        for k, w in row.items():
            try:
                weight_map[k].append(float(w))
                rows_with_signal[k] += 1
            except Exception:
                continue

    sig_rows = []
    for sig, ws in weight_map.items():
        arr = np.array(ws, dtype=float)
        sig_rows.append({
            "signal": sig,
            "weight_mean": float(np.mean(arr)),
            "weight_std": float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0,
            "weight_min": float(np.min(arr)),
            "weight_max": float(np.max(arr)),
            "rows_with_signal": int(rows_with_signal[sig]),
            "share": float(rows_with_signal[sig]) / float(total),
        })
    weights_df = pd.DataFrame(sig_rows).sort_values(["share","weight_mean"], ascending=[False, False])
    weights_out = os.path.join(out_dir, "weights_stats_by_signal.csv")
    weights_df.to_csv(weights_out, index=False)
    log("Wrote {}".format(weights_out))

    # --- 3) Top 20 key-sets by roi_mean ---
    top20 = keyset_df.head(20).copy()
    top20_out = os.path.join(out_dir, "cluster_top20_keysets.csv")
    top20.to_csv(top20_out, index=False)
    log("Wrote {}".format(top20_out))

    # --- 4) Dump rows for the best key-set (rank 1) ---
    if len(keyset_df) > 0:
        best_keyset_str = keyset_df.iloc[0]["keyset"]
        try:
            # safe parse of tuple-string like "('macd','rsi')"
            kset = eval(best_keyset_str, {"__builtins__": None}, {})
            if not isinstance(kset, tuple):
                kset = tuple()
        except Exception:
            kset = tuple()
        mask = df["_keyset"].map(lambda ks: tuple(ks) == tuple(kset))
        rows_best = df.loc[mask, ["Combination","roi","winrate","num_trades"]].copy()
        best_rows_out = os.path.join(out_dir, "cluster_rows_top_keysets.csv")
        rows_best.to_csv(best_rows_out, index=False)
        log("Wrote {} (best key-set rows)".format(best_rows_out))

    # quick print
    log("Keyset top5 by roi_mean:")
    print(keyset_df.head(5).to_string(index=False))

if __name__ == "__main__":
    main()
