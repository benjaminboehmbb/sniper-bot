# -*- coding: utf-8 -*-
"""
Evaluate run with per-year normalization based on 1m BTCUSDT data (2017–2025).
- Reads results/<...>/strategy_results_long.csv (or given path)
- Derives years from data/price_data_with_signals.csv timestamp span
- Prints mean/median trades per year, ROI stats, and top/flop strategies
Usage:
  python -m scripts.evaluate_run_by_years [optional_path_to_long_csv]
"""
import os, glob, sys
import pandas as pd
import numpy as np

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_CSV = os.path.join(ROOT, "data", "price_data_with_signals.csv")

def iqr(a):
    a = np.asarray(a, dtype=float)
    return float(np.nanpercentile(a,75) - np.nanpercentile(a,25))

def infer_years_from_data():
    if not os.path.exists(DATA_CSV):
        # fallback: assume 8 years if file missing
        return 8.0, None, None
    dtypes = {"timestamp":"string"}
    df = pd.read_csv(DATA_CSV, usecols=["timestamp"], dtype=dtypes)
    t0 = pd.to_datetime(df["timestamp"].iloc[0], utc=False, errors="coerce")
    t1 = pd.to_datetime(df["timestamp"].iloc[-1], utc=False, errors="coerce")
    span_days = (t1 - t0).days if (pd.notna(t0) and pd.notna(t1)) else 8*365
    years = span_days / 365.25
    return float(years), t0, t1

def pick_latest_long_csv():
    runs = sorted(glob.glob(os.path.join(ROOT, "results", "*_run_*")))
    if not runs:
        raise SystemExit("Keine Runs in results/ gefunden.")
    run = runs[-1]
    p = os.path.join(run, "strategy_results_long.csv")
    if not os.path.exists(p):
        raise SystemExit(f"Keine long-Ergebnisdatei gefunden: {p}")
    return p

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else pick_latest_long_csv()
    df = pd.read_csv(csv_path)

    years, t0, t1 = infer_years_from_data()
    if years <= 0:
        years = 8.0  # safety

    # Basis-Stats
    n = len(df)
    mean_trades = float(np.nanmean(df["num_trades"]))
    med_trades  = float(np.nanmedian(df["num_trades"]))
    mean_trades_py = mean_trades / years
    med_trades_py  = med_trades  / years

    mean_roi = float(np.nanmean(df["roi"]))
    med_roi  = float(np.nanmedian(df["roi"]))
    mean_wr  = float(np.nanmean(df["winrate"]))
    med_wr   = float(np.nanmedian(df["winrate"]))
    roi_iqr  = iqr(df["roi"])

    print("== Run-Evaluation (per-year normalized) ==")
    print("File:", os.path.relpath(csv_path, ROOT))
    if t0 is not None:
        print(f"Span: {t0} → {t1}  (~{years:.2f} Jahre)")
    else:
        print(f"Span: ~{years:.2f} Jahre (fallback)")

    print(f"Strategien: {n}")
    print(f"Trades (mean): {mean_trades:.1f}  | per-year: {mean_trades_py:.1f}")
    print(f"Trades (median): {med_trades:.1f} | per-year: {med_trades_py:.1f}")
    print(f"ROI % (mean): {mean_roi:.3f}  | ROI % (median): {med_roi:.3f} | ROI IQR: {roi_iqr:.3f}")
    print(f"Winrate % (mean): {mean_wr:.3f} | (median): {med_wr:.3f}")

    # Top / Flop
    cols = ["roi","num_trades","winrate","combination"]
    print("\nTop 5 (by ROI):")
    print(df.sort_values("roi", ascending=False).head(5)[cols].to_string(index=False))
    print("\nFlop 5 (by ROI):")
    print(df.sort_values("roi", ascending=True).head(5)[cols].to_string(index=False))

if __name__ == "__main__":
    main()
