#!/usr/bin/env python3
# ASCII-only output (avoid cp1252 issues).
# Build K8-LONG seed pools from K7-LONG FULL results:
#  - Top-ROI pool: top 2% by ROI
#  - Stable pool: top 1000 by ROI with winrate in [median..p90] and trades in [p10..p90]
#  - Union + dedup by Combination

import argparse
import os
import sys
from datetime import datetime

import pandas as pd


REQUIRED_COLS = ["Combination", "roi", "winrate", "num_trades"]


def die(msg: str, code: int = 1) -> None:
    print(f"[error] {msg}")
    sys.exit(code)


def ensure_cols(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        die(f"Missing required columns: {missing}. Found columns: {list(df.columns)}")


def safe_mkdir(path: str) -> None:
    if path and not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True, help="Path to K7-LONG FULL strategy_results CSV")
    ap.add_argument("--outdir", required=True, help="Output directory, e.g. results/k8_long_seedprep")
    ap.add_argument("--top-roi-pct", type=float, default=2.0, help="Top ROI pool percent (default: 2.0)")
    ap.add_argument("--stable-n", type=int, default=1000, help="Stable pool size target (default: 1000)")
    ap.add_argument("--min-rows", type=int, default=1000, help="Sanity: minimum rows expected (default: 1000)")
    args = ap.parse_args()

    in_csv = args.in_csv
    outdir = args.outdir
    top_pct = args.top_roi_pct
    stable_n = args.stable_n

    if not os.path.exists(in_csv):
        die(f"Input file not found: {in_csv}")

    safe_mkdir(outdir)

    print(f"[ok] Reading: {in_csv}")
    df = pd.read_csv(in_csv)
    ensure_cols(df)

    # Basic sanitation
    df = df.dropna(subset=["Combination", "roi", "winrate", "num_trades"]).copy()
    df["roi"] = pd.to_numeric(df["roi"], errors="coerce")
    df["winrate"] = pd.to_numeric(df["winrate"], errors="coerce")
    df["num_trades"] = pd.to_numeric(df["num_trades"], errors="coerce")
    df = df.dropna(subset=["roi", "winrate", "num_trades"]).copy()

    if len(df) < args.min_rows:
        die(f"Too few rows after cleaning: {len(df)} < min-rows {args.min_rows}. Check input file.")

    # Compute thresholds
    wr_med = float(df["winrate"].median())
    wr_p90 = float(df["winrate"].quantile(0.90))
    tr_p10 = float(df["num_trades"].quantile(0.10))
    tr_p90 = float(df["num_trades"].quantile(0.90))

    # Top ROI pool: top X%
    df_sorted = df.sort_values("roi", ascending=False).copy()
    top_n = max(1, int(round(len(df_sorted) * (top_pct / 100.0))))
    top_roi = df_sorted.head(top_n).copy()

    # Stable pool candidate filter
    stable_candidates = df_sorted[
        (df_sorted["winrate"] >= wr_med) &
        (df_sorted["winrate"] <= wr_p90) &
        (df_sorted["num_trades"] >= tr_p10) &
        (df_sorted["num_trades"] <= tr_p90)
    ].copy()

    stable_pool = stable_candidates.head(stable_n).copy()

    # Union + dedup by Combination
    union = pd.concat([top_roi, stable_pool], ignore_index=True)
    union_dedup = union.drop_duplicates(subset=["Combination"], keep="first").copy()

    # Timestamped outputs
    ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    base = os.path.join(outdir, f"k8_long_seedpools_from_k7_long_FULL_{ts}")

    top_path = f"{base}_TOP_ROI_{top_pct:.1f}pct.csv"
    stable_path = f"{base}_STABLE_TOP{stable_n}.csv"
    union_path = f"{base}_UNION_DEDUP.csv"
    summary_path = f"{base}_SUMMARY.txt"

    # Write
    top_roi.to_csv(top_path, index=False)
    stable_pool.to_csv(stable_path, index=False)
    union_dedup.to_csv(union_path, index=False)

    # Summary
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("K8-LONG seed pool build summary (from K7-LONG FULL)\n")
        f.write(f"input_rows_clean: {len(df)}\n")
        f.write(f"top_roi_pct: {top_pct}\n")
        f.write(f"top_roi_rows: {len(top_roi)}\n")
        f.write(f"stable_target_n: {stable_n}\n")
        f.write(f"stable_candidate_rows: {len(stable_candidates)}\n")
        f.write(f"stable_rows: {len(stable_pool)}\n")
        f.write(f"union_rows_before_dedup: {len(union)}\n")
        f.write(f"union_rows_after_dedup: {len(union_dedup)}\n")
        f.write("\nThresholds computed on FULL cleaned set:\n")
        f.write(f"winrate_median: {wr_med}\n")
        f.write(f"winrate_p90: {wr_p90}\n")
        f.write(f"num_trades_p10: {tr_p10}\n")
        f.write(f"num_trades_p90: {tr_p90}\n")
        f.write("\nOutputs:\n")
        f.write(f"top_roi_csv: {top_path}\n")
        f.write(f"stable_csv: {stable_path}\n")
        f.write(f"union_dedup_csv: {union_path}\n")

    print("[ok] Wrote seed pools:")
    print(f"  TOP-ROI:      {top_path} (rows={len(top_roi)})")
    print(f"  STABLE:       {stable_path} (rows={len(stable_pool)})")
    print(f"  UNION+DEDUP:  {union_path} (rows={len(union_dedup)})")
    print(f"[ok] Summary: {summary_path}")
    print("[note] Next step: we will use UNION+DEDUP as the seed basis for K8-LONG generation.")


if __name__ == "__main__":
    main()
