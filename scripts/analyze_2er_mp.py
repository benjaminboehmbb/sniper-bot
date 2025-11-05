#!/usr/bin/env python3
"""
analyze_2er_mp_v2.py
Multiprocessing-Analyse für 2er-Kombinationen mit Schwellenwert und optionalem AND-Modus.
- Long-only (roi, num_trades, winrate, accuracy; *_short-Spalten sind 0 für Schema-Kompatibilität)
- Fortschritt in Prozent (Schritte konfigurierbar)
- Reine ASCII-Logs (Windows-cp1252 sicher)
--Lief auf Workstation am 29.10.2025 in wenigen minuten
"""

import argparse
import ast
import csv
import datetime as dt
import json
import math
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from multiprocessing import Pool

# ====== Globale Variablen, die in init_worker gesetzt werden ======
RET_NEXT = None             # np.ndarray[float64], forward return per Bar
SIGNALS: Dict[str, np.ndarray] = {}  # name -> np.ndarray[int8] (0/1)
DATA_INFO = {}              # Metadaten für Logging

# ------------------------ Worker-Initialisierung ------------------------
def init_worker(data_path: str):
    """
    Lädt Kursdaten und Signalsäulen EINMAL pro Prozess.
    Erwartete Spalten in data/price_data_with_signals.csv:
      - close (float)
      - <signal>_signal (0/1) für: rsi, macd, bollinger, ma200, stoch, atr,
        ema50, adx, cci, mfi, obv, roc
    """
    global RET_NEXT, SIGNALS, DATA_INFO

    # Speicherfreundlich laden
    df = pd.read_csv(
        data_path,
        usecols=lambda c: c == "close" or c.endswith("_signal"),
        low_memory=False
    )

    close = pd.to_numeric(df["close"], errors="coerce").astype("float64")
    # Vorwärts-Return (nächster Balken)
    # Hinweis: fill_method=None in neueren Pandas empfohlen, hier explizit fillna
    ret_next = close.pct_change().shift(-1).fillna(0.0).to_numpy(dtype=np.float64)
    RET_NEXT = ret_next

    # Signals: in int8 mappen (0/1)
    sig_cols = [c for c in df.columns if c.endswith("_signal")]
    SIGNALS = {}
    for c in sig_cols:
        # coerced to 0/1 int8
        arr = pd.to_numeric(df[c], errors="coerce").fillna(0.0).astype("int8").to_numpy()
        SIGNALS[c[:-7]] = arr  # "rsi_signal" -> "rsi"

    DATA_INFO = {
        "rows": len(df),
        "signals": sorted(list(SIGNALS.keys()))
    }

# ----------------------------- Kernlogik -----------------------------
def simulate_long_binary(mask: np.ndarray) -> Tuple[float, int, float, float]:
    """
    Sehr schnelle, robuste Long-Only-Simulation auf Masken-Basis.
    - mask: 0/1, wann wir "im Markt" sind (Entry intrabar, Exit am Ende des Bars)
    Kennzahlen:
      roi: (Produkt (1+r_t) über alle aktiven Bars) - 1
      num_trades: Anzahl aktiver Bars (Proxy; schnell und stabil)
      winrate: Anteil der aktiven Bars mit r_t > 0
      accuracy: identisch zu winrate (Schema-kompatibel)
    """
    if mask.sum() == 0:
        return 0.0, 0, 0.0, 0.0

    r = RET_NEXT * mask
    # Numerisch stabil: Summe der Log-Returns von (1+r)
    # (vermeidet Overflow bei langen Zeiträumen)
    with np.errstate(invalid="ignore", divide="ignore"):
        roi = math.exp(np.log1p(r).sum()) - 1.0

    num_trades = int(mask.sum())
    positives = int((RET_NEXT > 0).astype("int8").dot(mask.astype("int8")))
    winrate = positives / num_trades if num_trades > 0 else 0.0
    accuracy = winrate
    return float(roi), num_trades, float(winrate), float(accuracy)

def build_mask_for_combo(combo: Dict[str, float], threshold: float, and_mode: bool) -> np.ndarray:
    """
    Erzeugt eine Binärmaske für eine 2er-Kombination.
    - and_mode=False: gewichtete Summe der aktiven Signale >= threshold
    - and_mode=True: alle beteiligten Signale müssen aktiv sein (logisches UND)
    """
    keys = list(combo.keys())
    if len(keys) == 0:
        return np.zeros_like(RET_NEXT, dtype="int8")

    if and_mode:
        m = np.ones_like(RET_NEXT, dtype="int8")
        for k in keys:
            sig = SIGNALS.get(k)
            if sig is None:
                return np.zeros_like(RET_NEXT, dtype="int8")
            m = m & sig
        return m.astype("int8")

    # gewichtete Summe aktiver Signale
    # Gewichtung * (0/1), threshold typischerweise 0.5..1.5
    acc = np.zeros_like(RET_NEXT, dtype="float64")
    for k, w in combo.items():
        sig = SIGNALS.get(k)
        if sig is None:
            # unbekanntes Signal -> Maske Null, damit sicher
            return np.zeros_like(RET_NEXT, dtype="int8")
        acc += float(w) * (sig > 0)

    return (acc >= float(threshold)).astype("int8")

def worker(task: Tuple[int, str, float, bool]) -> Tuple[int, str, float, int, float, float]:
    """
    task: (row_id, combo_str, threshold, and_mode)
    combo_str ist ein Dict-String, z. B. "{'rsi': 0.3, 'macd': 0.7}"
    """
    idx, combo_str, threshold, and_mode = task
    try:
        combo = ast.literal_eval(combo_str)
        if not isinstance(combo, dict):
            raise ValueError("Combination is not a dict")

        mask = build_mask_for_combo(combo, threshold, and_mode)
        roi, ntrades, winrate, accuracy = simulate_long_binary(mask)
        return (idx, combo_str, roi, ntrades, winrate, accuracy)
    except Exception as e:
        # Bei Fehlern neutralen Datensatz liefern (und in der Hauptschleife ggf. loggen)
        return (idx, combo_str, 0.0, 0, 0.0, 0.0)

# ----------------------------- Main -----------------------------
def parse_args():
    ap = argparse.ArgumentParser(
        prog="analyze_2er_mp_v2",
        description="MP-Analyse für 2er-Kombinationen (Long-only) mit Threshold und optionalem AND-Modus."
    )
    ap.add_argument("--data", required=True, help="Pfad zu data/price_data_with_signals.csv")
    ap.add_argument("--strategies", required=True, help="Pfad zu data/strategies_k2_shard*.csv")
    ap.add_argument("--n", type=int, default=200000, help="max. Strategien lesen")
    ap.add_argument("--num-procs", type=int, default=20, help="Anzahl Prozesse")
    ap.add_argument("--chunksize", type=int, default=512, help="Chunkgröße für Strategien (Aufgabengröße)")
    ap.add_argument("--progress_step", type=int, default=2, help="Prozent-Schritte für Fortschritt")
    ap.add_argument("--sim", choices=["long"], default="long", help="nur long unterstützt (Schema bleibt kompatibel)")
    ap.add_argument("--threshold", type=float, default=0.6, help="Schwellenwert für gewichtete Summe")
    ap.add_argument("--and-mode", action="store_true", help="Alle beteiligten Signale müssen gleichzeitig aktiv sein")
    return ap.parse_args()

def read_strategies(path: str, n: int) -> pd.DataFrame:
    # Erwartete Spalten: id (optional), Combination (Dict-String)
    usecols = None
    try:
        # Erst Kopf lesen, um Spalten zu sehen
        head = pd.read_csv(path, nrows=0)
        if "Combination" in head.columns:
            usecols = ["Combination"]
        elif "strategy" in head.columns:
            # Fallback (alte Benennung)
            usecols = ["strategy"]
        else:
            usecols = None
    except Exception:
        pass

    df = pd.read_csv(path, usecols=usecols, nrows=n, low_memory=False)
    if "Combination" not in df.columns:
        if "strategy" in df.columns:
            df = df.rename(columns={"strategy": "Combination"})
        else:
            # Notfall: gesamtes File lesen und Spalte suchen
            df = pd.read_csv(path, nrows=n, low_memory=False)
            if "Combination" not in df.columns:
                raise ValueError("CSV hat keine Spalte 'Combination'")

    # Nur 2er-Kombinationen behalten, falls gemischt
    # Wir filtern heuristisch über String: genau zwei Keys
    def is_2er(s: str) -> bool:
        try:
            d = ast.literal_eval(s)
            return isinstance(d, dict) and len(d) == 2
        except Exception:
            return False

    df = df[df["Combination"].apply(is_2er)].reset_index(drop=True)
    df.insert(0, "id", np.arange(len(df)))
    return df

def main():
    args = parse_args()

    # Output-Struktur
    ts = dt.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = Path(f"analysis_output_2er/{ts}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / f"strategy_results_2er_{ts}.csv"
    meta_json = out_dir / "run_meta.json"
    err_csv = out_dir / f"errors_2er_{ts}.csv"

    # Metadaten schreiben (früh)
    meta = {
        "run_id": ts,
        "n": args.n,
        "data": str(Path(args.data).resolve()),
        "strategies": str(Path(args.strategies).resolve()),
        "params": {
            "num_procs": args.num_procs,
            "chunksize": args.chunksize,
            "progress_step": args.progress_step,
            "sim": args.sim,
            "threshold": args.threshold,
            "and_mode": bool(args.and_mode),
        },
        "started_at": dt.datetime.utcnow().isoformat()
    }
    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Strategien laden
    df_strat = read_strategies(args.strategies, args.n)
    total = len(df_strat)
    if total == 0:
        print("Keine 2er-Strategien gefunden.")
        return

    print(f"Strategies loaded: {total}")
    print(f"Args: procs={args.num_procs} chunk={args.chunksize} progress_step={args.progress_step}% "
          f"threshold={args.threshold} and_mode={args.and_mode}")

    # Pool starten
    with Pool(processes=args.num_procs, initializer=init_worker, initargs=(args.data,)) as pool:
        # Tasks erzeugen
        tasks: List[Tuple[int, str, float, bool]] = [
            (int(row.id), str(row.Combination), float(args.threshold), bool(args.and_mode))
            for _, row in df_strat.iterrows()
        ]

        # Fortschritt
        next_mark = args.progress_step
        done = 0

        # Ergebnisse sammeln in Listen (am Ende einmalig schreiben)
        res_id: List[int] = []
        res_combo: List[str] = []
        res_roi: List[float] = []
        res_ntr: List[int] = []
        res_win: List[float] = []
        res_acc: List[float] = []

        print("Init workers and load data per process...")

        for out in pool.imap(worker, tasks, chunksize=args.chunksize):
            idx, combo_str, roi, ntr, win, acc = out
            res_id.append(idx)
            res_combo.append(combo_str)
            res_roi.append(roi)
            res_ntr.append(ntr)
            res_win.append(win)
            res_acc.append(acc)

            done += 1
            pct = (done * 100) // total
            if pct >= next_mark:
                now = dt.datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] progress {pct}%  ({done}/{total})")
                while next_mark <= pct:
                    next_mark += args.progress_step

    # DataFrame bauen und speichern
    out_df = pd.DataFrame({
        "id": res_id,
        "Combination": res_combo,
        "roi": res_roi,
        "num_trades": res_ntr,
        "winrate": res_win,
        "accuracy": res_acc,
        # Schema-Kompatibilität
        "roi_long": res_roi,
        "roi_short": [0.0] * len(res_id),
        "num_trades_long": res_ntr,
        "num_trades_short": [0] * len(res_id),
    }).sort_values("id")

    out_df.to_csv(out_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"DONE  results: {out_csv}")

if __name__ == "__main__":
    main()


