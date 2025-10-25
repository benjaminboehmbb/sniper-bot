#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
report_top_strategies.py
Liest results/warehouse/strategy_results.parquet und erzeugt
automatische Reports (CSV + Markdown) für Top-Strategien.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
WAREHOUSE = PROJECT_ROOT / "results" / "warehouse" / "strategy_results.parquet"
REPORT_DIR = PROJECT_ROOT / "results" / "reports"

# Default-Filter (kannst du später anpassen)
MIN_TRADES = 30
TOP_K = 50          # pro n
SORT_BY = ["roi","winrate"]  # erst nach roi, dann winrate

def main():
    if not WAREHOUSE.exists():
        print("❌ Warehouse nicht gefunden. Bitte zuerst ingest_results.py ausführen.")
        return
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(WAREHOUSE)
    # Grundfilter
    df = df.copy()
    df["n"] = df["n"].fillna("unknown")
    df = df[df["num_trades"] >= MIN_TRADES].copy()

    # Ranking
    df["_sort_key"] = df[SORT_BY[0]].rank(ascending=False, method="first")
    if len(SORT_BY) > 1:
        # combine rank keys
        df["_sort2"] = df[SORT_BY[1]].rank(ascending=False, method="first")
        df["_rank_sum"] = df["_sort_key"]*1000 + df["_sort2"]
    else:
        df["_rank_sum"] = df["_sort_key"]

    summaries = []
    for n_val, group in df.groupby("n"):
        g = group.sort_values(by=["_rank_sum"], ascending=True).head(TOP_K)
        out_csv = REPORT_DIR / f"top_{TOP_K}_{n_val}.csv"
        g.drop(columns=["_sort_key","_sort2","_rank_sum"], errors="ignore").to_csv(out_csv, index=False)
        summaries.append((n_val, out_csv))

    # Gesamtliste (TopK je n zusammengeführt)
    combined = pd.concat([pd.read_csv(p) for _, p in summaries], ignore_index=True) if summaries else pd.DataFrame()
    if not combined.empty:
        combined.to_csv(REPORT_DIR / "top_overall.csv", index=False)

    # Markdown-Übersicht
    md = ["# Top-Strategien Report",
          "",
          f"- Mindest-Trades: **{MIN_TRADES}**",
          f"- Kriterium: **{', '.join(SORT_BY)}**, Top {TOP_K} je n",
          ""]
    for n_val, p in summaries:
        md.append(f"- **{n_val}** → [{p.name}](./{p.name})")
    (REPORT_DIR / "README.md").write_text("\n".join(md), encoding="utf-8")

    print("✅ Reports geschrieben nach:", REPORT_DIR)

if __name__ == "__main__":
    main()
