#!/usr/bin/env python3
# tools/analyze_trades.py
# Chunk-basierte Auswertung einer Trades-CSV (auch .csv.gz).
# Outputs: summary.json, combo_stats.csv, top_trades.csv, worst_trades.csv, holdtime_quantiles.csv

import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np

# ---- Konfiguration (konservative Defaults) ----
DEFAULT_CHUNKSIZE = 500_000  # fuer 6.5 GB gz solide
TRADE_COLS = [
    "Combination", "side",
    "entry_idx", "entry_time", "entry_price",
    "exit_idx", "exit_time", "exit_price",
    "pnl"
]

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", required=True, help="Pfad zur Trades-CSV oder -CSV.GZ")
    ap.add_argument("--out-dir", required=True, help="Zielordner fuer Ausgaben")
    ap.add_argument("--chunksize", type=int, default=DEFAULT_CHUNKSIZE, help="CSV chunksize")
    ap.add_argument("--top", type=int, default=100, help="Anzahl Top-Trades nach PnL")
    ap.add_argument("--worst", type=int, default=100, help="Anzahl Flop-Trades nach PnL")
    return ap.parse_args()

def safe_to_datetime(s):
    # robust: errors="coerce" -> unparseable -> NaT
    return pd.to_datetime(s, errors="coerce", utc=True)

def agg_chunk(df):
    # Grundchecks
    need = set(TRADE_COLS)
    missing = list(need - set(df.columns))
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    # PnL als float
    df["pnl"] = pd.to_numeric(df["pnl"], errors="coerce")

    # Haltezeit in Minuten (falls Zeiten vorhanden)
    et = safe_to_datetime(df["entry_time"])
    xt = safe_to_datetime(df["exit_time"])
    hold_minutes = (xt - et).dt.total_seconds() / 60.0
    df["hold_minutes"] = hold_minutes

    # globale Summen
    total_trades = len(df)
    pnl_sum = np.nansum(df["pnl"].to_numpy())
    pnl_mean = float(np.nanmean(df["pnl"].to_numpy())) if total_trades else 0.0
    pnl_median = float(np.nanmedian(df["pnl"].to_numpy())) if total_trades else 0.0
    pnl_std = float(np.nanstd(df["pnl"].to_numpy())) if total_trades else 0.0
    winrate = float(np.nanmean((df["pnl"] > 0).to_numpy())) if total_trades else 0.0

    # Holdtime-Quantile
    hold_clean = df["hold_minutes"].to_numpy()
    hold_q = np.nanpercentile(hold_clean, [5, 25, 50, 75, 95]) if np.isfinite(hold_clean).any() else [np.nan]*5

    # combo-aggregation
    grp = df.groupby("Combination", observed=True)
    combo_stats = grp.agg(
        num_trades=("pnl", "size"),
        total_pnl=("pnl", "sum"),
        avg_pnl=("pnl", "mean"),
        winrate=("pnl", lambda x: np.nanmean((x > 0).to_numpy())),
        median_hold_min=("hold_minutes", "median"),
        mean_hold_min=("hold_minutes", "mean"),
    ).reset_index()

    # Top/Worst Trades extrahieren (im Chunk)
    # Nur noetige Spalten kopieren
    keep_cols = ["Combination", "side", "entry_time", "entry_price", "exit_time", "exit_price", "pnl", "hold_minutes"]
    top_trades = df[keep_cols].nlargest(1000, "pnl")  # lokal gross halten, spaeter global auf --top kuerzen
    worst_trades = df[keep_cols].nsmallest(1000, "pnl")

    summary = {
        "total_trades": int(total_trades),
        "pnl_sum": float(pnl_sum),
        "pnl_mean": float(pnl_mean),
        "pnl_median": float(pnl_median),
        "pnl_std": float(pnl_std),
        "winrate": float(winrate),
        "hold_q05": float(hold_q[0]),
        "hold_q25": float(hold_q[1]),
        "hold_q50": float(hold_q[2]),
        "hold_q75": float(hold_q[3]),
        "hold_q95": float(hold_q[4]),
    }

    return summary, combo_stats, top_trades, worst_trades

def merge_summaries(a, b):
    # Summaries additiv mergen (gewichtete Mittelwerte)
    out = {}
    tot_a, tot_b = a["total_trades"], b["total_trades"]
    tot = tot_a + tot_b
    out["total_trades"] = tot
    out["pnl_sum"] = a["pnl_sum"] + b["pnl_sum"]

    def wmean(key):
        va, vb = a[key], b[key]
        if tot == 0:
            return 0.0
        return (va * tot_a + vb * tot_b) / tot

    out["pnl_mean"] = wmean("pnl_mean")
    out["pnl_median"] = wmean("pnl_median")  # Approximation (nicht exakt, aber ausreichend fuer Uebersicht)
    out["pnl_std"] = wmean("pnl_std")        # Approximation
    out["winrate"] = wmean("winrate")

    # Quantile approximieren mit gewichteten Mitteln (naeherungsweise)
    for k in ["hold_q05", "hold_q25", "hold_q50", "hold_q75", "hold_q95"]:
        out[k] = wmean(k)

    return out

def main():
    args = parse_args()
    trades_path = Path(args.trades)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Loading trades: {trades_path}")
    usecols = TRADE_COLS  # gezielt, spart RAM/IO
    reader = pd.read_csv(trades_path, usecols=usecols, chunksize=args.chunksize)

    global_summary = None
    combo_list = []
    top_list = []
    worst_list = []

    total_chunks = 0
    for chunk in reader:
        total_chunks += 1
        s, cstats, topc, worstc = agg_chunk(chunk)

        # global summary
        if global_summary is None:
            global_summary = s
        else:
            global_summary = merge_summaries(global_summary, s)

        combo_list.append(cstats)
        top_list.append(topc)
        worst_list.append(worstc)

        if total_chunks % 5 == 0:
            print(f"[INFO] processed {total_chunks} chunks")

    # combo stats zusammenfassen
    if combo_list:
        combos = pd.concat(combo_list, ignore_index=True)
        # gleiche Combination mergen
        agg = combos.groupby("Combination", as_index=False).agg(
            num_trades=("num_trades", "sum"),
            total_pnl=("total_pnl", "sum"),
            avg_pnl=("avg_pnl", "mean"),  # Mittel der Mittel (nahezu ok); alternativ gewichtetes Mittel
            winrate=("winrate", "mean"),
            median_hold_min=("median_hold_min", "median"),
            mean_hold_min=("mean_hold_min", "mean"),
        )
        # ROI = total_pnl / num_trades
        agg["roi"] = agg["total_pnl"] / agg["num_trades"].clip(lower=1)
        agg = agg.sort_values(["roi", "winrate", "total_pnl"], ascending=[False, False, False])
    else:
        agg = pd.DataFrame(columns=["Combination","num_trades","total_pnl","avg_pnl","winrate","median_hold_min","mean_hold_min","roi"])

    # top/worst global
    if top_list:
        top_all = pd.concat(top_list, ignore_index=True).nlargest(args.top, "pnl")
    else:
        top_all = pd.DataFrame(columns=["Combination","side","entry_time","entry_price","exit_time","exit_price","pnl","hold_minutes"])

    if worst_list:
        worst_all = pd.concat(worst_list, ignore_index=True).nsmallest(args.worst, "pnl")
    else:
        worst_all = pd.DataFrame(columns=["Combination","side","entry_time","entry_price","exit_time","exit_price","pnl","hold_minutes"])

    # Holdtime quantiles global aus summary
    hold_q = {
        "q05": global_summary["hold_q05"] if global_summary else np.nan,
        "q25": global_summary["hold_q25"] if global_summary else np.nan,
        "q50": global_summary["hold_q50"] if global_summary else np.nan,
        "q75": global_summary["hold_q75"] if global_summary else np.nan,
        "q95": global_summary["hold_q95"] if global_summary else np.nan,
    }
    hold_q_df = pd.DataFrame([hold_q])

    # outputs
    (out_dir / "combo_stats.csv").write_text("")  # touch for atomicity hint
    agg.to_csv(out_dir / "combo_stats.csv", index=False)

    top_all.to_csv(out_dir / "top_trades.csv", index=False)
    worst_all.to_csv(out_dir / "worst_trades.csv", index=False)
    hold_q_df.to_csv(out_dir / "holdtime_quantiles.csv", index=False)

    summary_path = out_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(global_summary or {}, f, ensure_ascii=True, indent=2)

    print(f"[INFO] Wrote: {out_dir/'summary.json'}")
    print(f"[INFO] Wrote: {out_dir/'combo_stats.csv'}")
    print(f"[INFO] Wrote: {out_dir/'top_trades.csv'}")
    print(f"[INFO] Wrote: {out_dir/'worst_trades.csv'}")
    print(f"[INFO] Wrote: {out_dir/'holdtime_quantiles.csv'}")
    print("[INFO] Done.")

if __name__ == "__main__":
    main()
