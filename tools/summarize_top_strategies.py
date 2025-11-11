#!/usr/bin/env python3
# ASCII only
import sys, os, json
import pandas as pd
import numpy as np
from datetime import datetime

def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print("[{} UTC] {}".format(ts, msg), flush=True)

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/summarize_top_strategies.py <input_csv> <output_dir>")
        sys.exit(2)

    in_csv = sys.argv[1]
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)

    log("Loading {}".format(in_csv))
    df = pd.read_csv(in_csv)

    # basic sanity
    required = {"Combination","roi","num_trades","winrate"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit("Missing columns: {}".format(", ".join(missing)))

    # remove zero-trade rows
    df = df[df["num_trades"] > 0].copy()

    # overall summary
    summary = {
        "count": int(len(df)),
        "roi_mean": float(df["roi"].mean()) if len(df) else 0.0,
        "roi_median": float(df["roi"].median()) if len(df) else 0.0,
        "roi_std": float(df["roi"].std(ddof=1)) if len(df) > 1 else 0.0,
        "winrate_mean": float(df["winrate"].mean()) if len(df) else 0.0,
        "num_trades_mean": float(df["num_trades"].mean()) if len(df) else 0.0,
        "num_trades_median": float(df["num_trades"].median()) if len(df) else 0.0,
        "best_roi": float(df["roi"].max()) if len(df) else 0.0,
    }
    pd.DataFrame([summary]).to_csv(os.path.join(out_dir, "summary_overall.csv"), index=False)

    # rank by ROI desc
    ranked = df.sort_values(by=["roi"], ascending=False).reset_index(drop=True)
    ranked.to_csv(os.path.join(out_dir, "top500_ranked_by_roi.csv"), index=False)

    # robust slice: filter by at least 100 trades and winrate >= 0.5
    robust = ranked[(ranked["num_trades"] >= 100) & (ranked["winrate"] >= 0.50)].copy()
    robust.to_csv(os.path.join(out_dir, "top_robust_roi_winrate.csv"), index=False)

    # quick top20
    top20 = ranked.head(20).copy()
    top20.to_csv(os.path.join(out_dir, "top20.csv"), index=False)

    log("Saved: summary_overall.csv, top500_ranked_by_roi.csv, top_robust_roi_winrate.csv, top20.csv")

if __name__ == "__main__":
    main()
