#!/usr/bin/env python3
"""
compare_runs.py
Simple tool to compare two strategy result CSVs (normalizes combination keys).
Usage:
  python tools/compare_runs.py --a path/to/runA.csv --b path/to/runB.csv --out results/compare/diffs_YYYYMMDD.csv
"""
import argparse
import ast
import csv
import json
import os
import pandas as pd
from datetime import datetime

KEY_MAP = {
    "rsi": "rsi_signal", "macd": "macd_signal", "bollinger": "bollinger_signal",
    "ma200": "ma200_signal", "stoch": "stoch_signal", "atr": "atr_signal", "ema50": "ema50_signal"
}

def parse_combo_string(s):
    """
    Parse a combination string into a dict of normalized signal keys.
    Accepts formats like "{'rsi': 0.1, 'macd': 0.2}" or "{'rsi_signal': 0.1, ...}".
    Returns normalized dict with keys like 'rsi_signal'.
    """
    if pd.isna(s):
        return {}
    try:
        d = ast.literal_eval(s)
        nd = {}
        for k,v in d.items():
            nk = KEY_MAP.get(k, k)
            # ensure numeric
            try:
                nv = float(v)
            except Exception:
                nv = float(str(v).replace(',', '.'))
            nd[nk] = nv
        return dict(sorted(nd.items()))
    except Exception:
        # fallback: try to interpret as JSON-ish
        try:
            js = json.loads(s.replace("'", '"'))
            nd = {}
            for k,v in js.items():
                nk = KEY_MAP.get(k, k)
                nd[nk] = float(v)
            return dict(sorted(nd.items()))
        except Exception:
            return {}

def combo_to_stable_string(d):
    """Convert normalized dict to stable string ordering keys alphabetically."""
    if not d:
        return "{}"
    items = ", ".join([f"'{k}': {d[k]:.3f}" for k in sorted(d.keys())])
    return "{" + items + "}"

def load_and_normalize(path):
    df = pd.read_csv(path)
    # ensure 'Combination' or 'combination' column handled
    combo_col = None
    for c in ["Combination", "combination", "Combination "]:
        if c in df.columns:
            combo_col = c
            break
    if combo_col is None:
        raise RuntimeError(f"No combination column found in {path}. Expected 'Combination' or 'combination'.")

    df = df.copy()
    df["__norm_combo_dict"] = df[combo_col].apply(parse_combo_string)
    df["__norm_combo"] = df["__norm_combo_dict"].apply(combo_to_stable_string)
    return df

def compare_runs(path_a, path_b, out_path, tolerance_trades_pct=0.10, tolerance_winrate=0.02):
    a = load_and_normalize(path_a)
    b = load_and_normalize(path_b)

    # Merge on normalized combo
    cols_to_keep = ["num_trades", "winrate", "total_pnl", "avg_pnl"]
    a_sel = a[["__norm_combo"] + [c for c in cols_to_keep if c in a.columns]].drop_duplicates("__norm_combo")
    b_sel = b[["__norm_combo"] + [c for c in cols_to_keep if c in b.columns]].drop_duplicates("__norm_combo")

    merged = pd.merge(a_sel, b_sel, on="__norm_combo", how="inner", suffixes=("_a", "_b"))

    if merged.empty:
        print("No overlapping normalized combinations found.")
    else:
        # compute diffs
        merged["num_trades_diff"] = None
        if "num_trades_a" in merged.columns and "num_trades_b" in merged.columns:
            merged["num_trades_diff"] = merged["num_trades_a"] - merged["num_trades_b"]
            merged["num_trades_diff_pct"] = merged["num_trades_diff"].abs() / (merged[["num_trades_a","num_trades_b"]].max(axis=1).replace(0,1))

        if "winrate_a" in merged.columns and "winrate_b" in merged.columns:
            merged["winrate_diff"] = merged["winrate_a"] - merged["winrate_b"]

        if "total_pnl_a" in merged.columns and "total_pnl_b" in merged.columns:
            merged["total_pnl_diff"] = merged["total_pnl_a"] - merged["total_pnl_b"]

        # summary counts
        total_common = len(merged)
        trades_signif = 0
        winrate_signif = 0
        if "num_trades_diff_pct" in merged.columns:
            trades_signif = int((merged["num_trades_diff_pct"] > tolerance_trades_pct).sum())
        if "winrate_diff" in merged.columns:
            winrate_signif = int((merged["winrate_diff"].abs() > tolerance_winrate).sum())

        summary = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "file_a": os.path.basename(path_a),
            "file_b": os.path.basename(path_b),
            "total_common_combinations": int(total_common),
            "num_trades_diff_gt_pct": trades_signif,
            "winrate_diff_gt_abs": winrate_signif
        }

        # write merged diffs csv (keep main columns)
        out_dir = os.path.dirname(out_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        merged.to_csv(out_path, index=False)
        # write also a small summary json
        summary_path = out_path.replace(".csv", ".summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        print("Compare finished.")
        print("Common combinations:", total_common)
        print("num_trades differing by >", int(tolerance_trades_pct*100), "% :", trades_signif)
        print("winrate differing by >", tolerance_winrate, ":", winrate_signif)
        print("Output CSV:", out_path)
        print("Summary JSON:", summary_path)

def main():
    p = argparse.ArgumentParser(description="Compare two strategy result CSVs.")
    p.add_argument("--a", required=True, help="Path to run A CSV")
    p.add_argument("--b", required=True, help="Path to run B CSV")
    p.add_argument("--out", required=True, help="Output CSV path for diffs")
    p.add_argument("--trades-tol", type=float, default=0.10, help="Tolerance for num_trades relative difference (e.g. 0.10)")
    p.add_argument("--winrate-tol", type=float, default=0.02, help="Tolerance for winrate absolute difference")
    args = p.parse_args()

    compare_runs(args.a, args.b, args.out, tolerance_trades_pct=args.trades_tol, tolerance_winrate=args.winrate_tol)

if __name__ == "__main__":
    main()
