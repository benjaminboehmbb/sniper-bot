# -*- coding: utf-8 -*-
"""
Kompakte Auswertung des neuesten Runs (Long):
- zeigt Mittel/Median für num_trades, ROI, winrate und ROI-IQR
- listet die Top/Flop 5 Strategien nach ROI
"""
import glob, os, pandas as pd, numpy as np

def iqr(a):
    a = np.asarray(a, dtype=float)
    return float(np.nanpercentile(a,75) - np.nanpercentile(a,25))

def main():
    runs = sorted(glob.glob("results/*_run_*"))
    if not runs:
        print("Keine Runs in results/ gefunden."); return
    run = runs[-1]
    p = os.path.join(run, "strategy_results_long.csv")
    if not os.path.exists(p):
        print("Keine long-Ergebnisdatei gefunden:", p); return

    df = pd.read_csv(p)
    print("Run:", run, "| Strategien:", len(df))
    print("mean num_trades:", np.nanmean(df["num_trades"]))
    print("median num_trades:", np.nanmedian(df["num_trades"]))
    print("median ROI %:", np.nanmedian(df["roi"]))
    print("mean winrate %:", np.nanmean(df["winrate"]))
    print("ROI IQR:", iqr(df["roi"]))

    print("\nTop 5 nach ROI:")
    print(df.sort_values("roi", ascending=False).head(5)[["roi","num_trades","winrate","combination"]].to_string(index=False))

    print("\nFlop 5 nach ROI:")
    print(df.sort_values("roi", ascending=True).head(5)[["roi","num_trades","winrate","combination"]].to_string(index=False))

if __name__ == "__main__":
    main()
