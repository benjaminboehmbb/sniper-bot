#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ingest_results.py
Scannt alle analysis_output_*/ und deep_out_*/ Ordner,
lädt strategy_results_*.csv, normalisiert Spalten und schreibt sie
idempotent in ein Parquet-Warehouse unter results/warehouse/.
"""

from __future__ import annotations
import re
from pathlib import Path
from datetime import datetime
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
WAREHOUSE_DIR = PROJECT_ROOT / "results" / "warehouse"
WAREHOUSE_FILE = WAREHOUSE_DIR / "strategy_results.parquet"

CSV_GLOB_PATTERNS = [
    "analysis_output_*/*/strategy_results_*.csv",
    "deep_out_*/*/strategy_results*.csv",
    "out_*/*/strategy_results*.csv",  # falls alte Struktur noch genutzt wird
]

def parse_run_meta_from_path(p: Path) -> dict:
    # Erwartete Pfade: analysis_output_4er/2025-09-02_12-34-56/strategy_results_4er_2025-09-02_12-34-56.csv
    # Fallbacks für deep_out_*
    parts = p.parts
    info = {"n": None, "tier": None, "run_id": None, "engine": None}
    # n aus Ordnername analysis_output_Xer
    for part in parts:
        m = re.match(r"analysis_output_(\der)", part)
        if m:
            info["n"] = m.group(1)
    # run_id aus Ordnername direkt über der Datei
    try:
        run_id = p.parent.name
        datetime.strptime(run_id, "%Y-%m-%d_%H-%M-%S")
        info["run_id"] = run_id
    except Exception:
        # versuche aus Dateiname zu lesen
        m = re.search(r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})", p.name)
        if m:
            info["run_id"] = m.group(1)

    # engine evtl. in meta.json – ignorieren wir hier, kann später ergänzt werden
    return info

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    # Pflichtfelder sicherstellen
    rename_map = {}
    for want in ["roi", "num_trades", "winrate", "accuracy", "combination"]:
        if want in cols and cols[want] != want:
            rename_map[cols[want]] = want
    df = df.rename(columns=rename_map)

    # fehlende Spalten ergänzen
    for c in ["roi","num_trades","winrate","accuracy","roi_long","roi_short","num_trades_long","num_trades_short"]:
        if c not in df.columns:
            df[c] = 0.0 if c.startswith("roi") or c in ("winrate","accuracy") else 0

    # IDs sicherstellen
    if "id" not in df.columns:
        # fallback: hash aus Combination
        df["id"] = df["combination"].astype(str).apply(lambda s: pd.util.hash_pandas_object(pd.Series([s])).astype("int64")[0])

    return df

def read_existing() -> pd.DataFrame | None:
    if WAREHOUSE_FILE.exists():
        try:
            return pd.read_parquet(WAREHOUSE_FILE)
        except Exception:
            return None
    return None

def main():
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    existing = read_existing()
    existing_keys = set()
    if existing is not None:
        existing["run_id"] = existing["run_id"].astype(str)
        existing["id"] = existing["id"].astype(str)
        existing_keys = set(zip(existing["run_id"], existing["id"]))

    to_append = []
    seen = 0
    new_rows = 0

    for pattern in CSV_GLOB_PATTERNS:
        for p in PROJECT_ROOT.glob(pattern):
            if not p.is_file():
                continue
            meta = parse_run_meta_from_path(p)
            try:
                df = pd.read_csv(p)
            except Exception as e:
                print(f"[WARN] Konnte {p} nicht lesen: {e}")
                continue
            df = normalize_df(df)
            df["run_id"] = meta["run_id"]
            df["n"] = meta["n"]
            df["source_file"] = str(p.relative_to(PROJECT_ROOT))

            # Dedupe vs. existing
            for _, row in df.iterrows():
                seen += 1
                key = (str(row["run_id"]), str(row["id"]))
                if meta["run_id"] is None:
                    # Ohne run_id immer aufnehmen (selten)
                    to_append.append(row)
                    new_rows += 1
                elif key not in existing_keys:
                    to_append.append(row)
                    new_rows += 1

    if not to_append:
        print("✅ Nichts Neues zu importieren.")
        return

    add_df = pd.DataFrame(to_append)
    if existing is None or existing.empty:
        final = add_df
    else:
        final = pd.concat([existing, add_df], ignore_index=True)

    # sinnvolle dtypes
    for c in ["roi","winrate","accuracy","roi_long","roi_short"]:
        if c in final.columns:
            final[c] = pd.to_numeric(final[c], errors="coerce").fillna(0.0)
    for c in ["num_trades","num_trades_long","num_trades_short"]:
        if c in final.columns:
            final[c] = pd.to_numeric(final[c], errors="coerce").fillna(0).astype("int64")

    final.to_parquet(WAREHOUSE_FILE, index=False)
    print(f"📦 Import fertig. Gelesen: {seen} Zeilen, Neu: {new_rows}.")
    print(f"🗄️  Warehouse: {WAREHOUSE_FILE}")

if __name__ == "__main__":
    main()
