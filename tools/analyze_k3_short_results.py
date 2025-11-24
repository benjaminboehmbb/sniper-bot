import os
import sys
from datetime import datetime

import pandas as pd
import numpy as np


def main():
    # Pfade an dein Projekt angepasst
    input_path = "results/k3_short_regime_finetune_top300_0p01_ws/strategy_results.csv"
    output_dir = "results/k3_short_regime_finetune_top300_0p01_ws"

    if not os.path.exists(input_path):
        print("ERROR: Input file not found:", input_path)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    print("Loading:", input_path)
    df = pd.read_csv(input_path)

    required_cols = ["Combination", "roi", "num_trades", "winrate", "pnl_sum"]
    for col in required_cols:
        if col not in df.columns:
            print("ERROR: Column missing in input:", col)
            print("Columns found:", list(df.columns))
            sys.exit(1)

    # Kopie, alten Index ggf. entfernen
    df = df.copy()
    if "index" in df.columns:
        df = df.drop(columns=["index"])

    # Zusätzliche Kennzahlen
    max_trades = df["num_trades"].max()
    if max_trades and max_trades > 0:
        df["trade_density_rel"] = df["num_trades"] / float(max_trades)
    else:
        df["trade_density_rel"] = 0.0

    roi_mean = df["roi"].mean()
    roi_std = df["roi"].std()
    if roi_std and roi_std > 0:
        df["roi_zscore"] = (df["roi"] - roi_mean) / roi_std
    else:
        df["roi_zscore"] = 0.0

    # Timestamp fuer Dateinamen
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 1) ALL: alle Strategien nach ROI sortiert
    df_all = df.sort_values("roi", ascending=False).reset_index(drop=True)
    path_all = os.path.join(output_dir, f"strategy_results_short_k3_ALL_{ts}.csv")
    df_all.to_csv(path_all, index=False)
    print("Wrote ALL strategies to:", path_all, "(rows=%d)" % len(df_all))

    # 2) HITS: "gute" Strategien nach einfachen Short-Filtern
    hits_mask = (
        (df["roi"] > 0.0)
        & (df["winrate"] >= 0.55)
        & (df["num_trades"] >= 50)
    )
    df_hits = df.loc[hits_mask].sort_values("roi", ascending=False).reset_index(drop=True)
    path_hits = os.path.join(output_dir, f"strategy_results_short_k3_HITS_{ts}.csv")
    df_hits.to_csv(path_hits, index=False)
    print("Wrote HITS to:", path_hits, "(rows=%d)" % len(df_hits))

    # 3) TOP-Cluster um den oberen ROI-Bereich
    base_mask = (df["roi"] > 0.0) & (df["num_trades"] >= 50)
    df_pos = df.loc[base_mask].copy()

    if len(df_pos) > 0:
        q90 = df_pos["roi"].quantile(0.90)
        q95 = df_pos["roi"].quantile(0.95)
        q99 = df_pos["roi"].quantile(0.99)

        cluster_mask = df_pos["roi"] >= q95
        df_top_cluster = df_pos.loc[cluster_mask].sort_values("roi", ascending=False).reset_index(drop=True)

        path_cluster = os.path.join(output_dir, f"strategy_results_short_k3_TOP_CLUSTER_{ts}.csv")
        df_top_cluster.to_csv(path_cluster, index=False)
        print("Wrote TOP ROI CLUSTER to:", path_cluster, "(rows=%d)" % len(df_top_cluster))

        print("ROI quantiles on positives:")
        print(" q90 =", q90)
        print(" q95 =", q95)
        print(" q99 =", q99)
    else:
        print("No positive ROI strategies with min trades >= 50. TOP_CLUSTER file not created.")


if __name__ == "__main__":
    main()
