#!/usr/bin/env python3
# ASCII only: analyze_k3_long_short_4sigs.py

import pandas as pd
from pathlib import Path


def load_results(path_str, side_label):
    path = Path(path_str)
    if not path.exists():
        raise SystemExit("Results CSV not found for %s: %s" % (side_label, path))

    print("[INFO] Loading %s results from %s" % (side_label, path))
    df = pd.read_csv(path)

    # Spalten vereinheitlichen
    cols_lower = {c.lower(): c for c in df.columns}
    required = ["combination", "roi", "num_trades", "winrate"]
    for col in required:
        if col not in cols_lower:
            raise SystemExit("Column '%s' not found in %s" % (col, path))

    comb_col = cols_lower["combination"]
    roi_col = cols_lower["roi"]
    trades_col = cols_lower["num_trades"]
    win_col = cols_lower["winrate"]

    out = pd.DataFrame({
        "Combination": df[comb_col],
        "roi": df[roi_col],
        "num_trades": df[trades_col],
        "winrate": df[win_col],
    })
    out["side"] = side_label
    return out


def main():
    # Pfade zu den fertigen Feintuning-Runs
    long_csv = "results/hold_sweep/k3_long_mid_4sigs_0p01_top300_CHUNKED/strategy_results.csv"
    short_csv = "results/hold_sweep/k3_short_mid_4sigs_0p01_top300_CHUNKED/strategy_results.csv"

    df_long = load_results(long_csv, "long")
    df_short = load_results(short_csv, "short")

    print("[INFO] Long rows:", len(df_long))
    print("[INFO] Short rows:", len(df_short))

    # Grundlegende Statistiken pro Seite
    for side, df_side in [("long", df_long), ("short", df_short)]:
        print("\n[STATS] Side:", side)
        print(df_side[["roi", "num_trades", "winrate"]].describe())

    # Top-N pro Seite nach ROI
    top_n = 100

    long_top = (
        df_long.dropna(subset=["roi"])
        .sort_values("roi", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    short_top = (
        df_short.dropna(subset=["roi"])
        .sort_values("roi", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )

    long_out = Path(long_csv).with_name("strategy_results_top100_long.csv")
    short_out = Path(short_csv).with_name("strategy_results_top100_short.csv")

    long_top.to_csv(long_out, index=False)
    short_top.to_csv(short_out, index=False)

    print("\n[INFO] Saved top %d long strategies to %s" % (len(long_top), long_out))
    print("[INFO] Saved top %d short strategies to %s" % (len(short_top), short_out))

    # Optional: kombinierte Datei der Top-Kombos mit Side-Flag
    combined_top = pd.concat([long_top, short_top], ignore_index=True)
    combo_out = Path("results/hold_sweep/k3_long_short_4sigs_top100_combined.csv")
    combo_out.parent.mkdir(parents=True, exist_ok=True)
    combined_top.to_csv(combo_out, index=False)
    print("[INFO] Saved combined top long+short to %s" % combo_out)


if __name__ == "__main__":
    main()
