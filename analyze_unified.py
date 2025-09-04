#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
analyze_unified.py
------------------
Einheitliches, robustes Analyse-Skript für 2er–7er Strategien:
- Einheitliches Setup für alle Kombinationen (2er-7er)
- Long/Short-Simulation via simtrader_selector (Engine-Wahl)
- Automatische Backups, Zeitstempel und Logging
- Multiprocessing optional (Parameter --num-procs)
- Fortschritt, Batch-Write, Fehlerlog
- CSV-Kompat: akzeptiert 'open_time' oder 'timestamp', normiert auf 'timestamp'
- Strategy-CSV: Spalte 'Combination' mit Dict-String
"""

import argparse
import ast
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

import pandas as pd

# SimTrader-Selector statt fixem Import
from simtrader_selector import get_simtrader


def sha1_of_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:10]


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def backup_if_exists(fp: Path) -> None:
    """Backup vorhandener Dateien mit Zeitstempel."""
    if fp.exists():
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup = fp.with_name(fp.stem + f"_backup_{ts}" + fp.suffix)
        try:
            fp.replace(backup)
            print(f"[INFO] Backup angelegt: {backup.name}")
        except Exception as e:
            print(f"[WARN] Konnte Backup nicht anlegen ({fp.name}): {e}")


def load_data(data_path: Path) -> pd.DataFrame:
    """CSV laden und Zeitspalte normalisieren."""
    df = pd.read_csv(data_path)
    cols = {c.lower(): c for c in df.columns}
    if "timestamp" in cols:
        df.rename(columns={cols["timestamp"]: "timestamp"}, inplace=True)
    elif "open_time" in cols:
        df.rename(columns={cols["open_time"]: "timestamp"}, inplace=True)
    else:
        raise ValueError("Weder 'timestamp' noch 'open_time' in Kursdaten gefunden.")
    return df


def parse_combination(s: str) -> Dict[str, float]:
    """
    Erwartet Dict-String wie: "{'rsi_signal': 0.3, 'macd_signal': 0.4, ...}"
    """
    d = ast.literal_eval(s)
    if not isinstance(d, dict):
        raise ValueError("Combination-Spalte ist kein Dict.")
    out = {}
    for k, v in d.items():
        try:
            out[str(k)] = float(v) if not isinstance(v, str) else float(v.strip())
        except Exception:
            raise ValueError(f"Combination enthält ungültigen Wert bei '{k}': {v}")
    return out


def evaluate_one_strategy(idx: int, combo_str: str, df_data: pd.DataFrame,
                          fees: float, slippage: float,
                          sim_kwargs: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """
    Führt Simulation für eine Strategie-Kombination aus.
    Gibt (index, metrics_dict) zurück.
    """
    try:
        weights = parse_combination(combo_str)
        combo_id = sha1_of_text(combo_str)

        SimCls = get_simtrader(sim_kwargs.get("engine", "default"))
        trader = SimCls(df_data, fees=fees, slippage=slippage, **sim_kwargs)
        metrics = trader.run(weights)

        # Standardisierte Felder
        result = {
            "id": combo_id,
            "Combination": combo_str,
            "roi": float(metrics.get("roi", 0.0)),
            "num_trades": int(metrics.get("num_trades", 0)),
            "winrate": float(metrics.get("winrate", 0.0)),
            "accuracy": float(metrics.get("accuracy", 0.0)),
            "roi_long": float(metrics.get("roi_long", 0.0)),
            "roi_short": float(metrics.get("roi_short", 0.0)),
            "num_trades_long": int(metrics.get("num_trades_long", 0)),
            "num_trades_short": int(metrics.get("num_trades_short", 0)),
        }
        return idx, result

    except Exception as e:
        return idx, {
            "error": str(e),
            "Combination": combo_str,
        }


def main():
    ap = argparse.ArgumentParser(description="Einheitliche Analyse für 2er–7er Strategien")
    ap.add_argument("--data", required=True, help="Pfad zu price_data_with_signals.csv")
    ap.add_argument("--strategies", required=True, help="Pfad zur Strategies-CSV (Spalte 'Combination')")
    ap.add_argument("--outdir", default=None, help="Output-Ordner (Default: analysis_output_<N>er)")
    ap.add_argument("--tier", default="", help="Zusatzlabel für Auswertung (fine/full/coarse)")
    ap.add_argument("--num-procs", type=int, default=0, help="Anzahl Prozesse (0/1 = sequentiell)")
    ap.add_argument("--chunksize", type=int, default=256, help="Chunksize für Multiprocessing")
    ap.add_argument("--batch-write", type=int, default=5000, help="Ergebnisse alle N Items flushen")
    ap.add_argument("--progress-step", type=int, default=2, help="Fortschritt in %")
    ap.add_argument("--fees", type=float, default=0.0005, help="Gebühren")
    ap.add_argument("--slippage", type=float, default=0.0002, help="Slippage")
    ap.add_argument("--n", type=int, required=True, help="N der Kombination (2..7)")
    ap.add_argument("--sim", default="default", help="Engine: default | short_dummy")
    ap.add_argument("--save-trades", type=int, default=0, help="Trades speichern (0/1)")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    data_path = (root / args.data).resolve()
    strategies_path = (root / args.strategies).resolve()

    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    outdir = Path(args.outdir) if args.outdir else root / f"analysis_output_{args.n}er"
    outdir = outdir / run_id
    ensure_dir(outdir)

    results_csv = outdir / f"strategy_results_{args.n}er_{run_id}.csv"
    errors_csv = outdir / f"errors_{args.n}er_{run_id}.csv"

    meta = {
        "run_id": run_id,
        "n": args.n,
        "tier": args.tier,
        "data": str(data_path),
        "strategies": str(strategies_path),
        "params": {
            "num_procs": args.num_procs,
            "chunksize": args.chunksize,
            "batch_write": args.batch_write,
            "progress_step": args.progress_step,
            "fees": args.fees,
            "slippage": args.slippage,
            "sim": args.sim,
            "save_trades": args.save_trades,
        },
        "started_at": datetime.now().isoformat(timespec="seconds"),
    }
    (outdir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"📈 Lade Kursdaten: {data_path.name}")
    df_data = load_data(data_path)
    print(f"✅ Kursdaten geladen: {len(df_data):,} Zeilen")

    print(f"📋 Lade Strategien: {strategies_path.name}")
    df_strat = pd.read_csv(strategies_path, usecols=["Combination"])
    total = len(df_strat)
    print(f"✅ Eingelesene Strategien: {total:,}")

    res_fields = [
        "id", "Combination", "roi", "num_trades", "winrate", "accuracy",
        "roi_long", "roi_short", "num_trades_long", "num_trades_short"
    ]
    err_fields = ["Combination", "error"]

    with results_csv.open("w", newline="", encoding="utf-8") as fr, \
         errors_csv.open("w", newline="", encoding="utf-8") as fe:

        res_writer = csv.DictWriter(fr, fieldnames=res_fields)
        err_writer = csv.DictWriter(fe, fieldnames=err_fields)
        res_writer.writeheader()
        err_writer.writeheader()

        sim_kwargs = {"engine": args.sim, "save_trades": bool(args.save_trades)}

        processed = 0
        next_progress = args.progress_step

        def handle_result(tup):
            nonlocal processed, next_progress
            idx, payload = tup
            if "error" in payload:
                err_writer.writerow(payload)
            else:
                res_writer.writerow(payload)

            processed += 1
            if processed % args.batch_write == 0:
                fr.flush()
                fe.flush()

            pct = (processed * 100) // max(total, 1)
            if pct >= next_progress:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Fortschritt: {processed:,}/{total:,} ({pct}%)")
                next_progress += args.progress_step

        # Sequentiell
        if args.num_procs in (0, 1):
            print("🚶 Sequentielle Ausführung…")
            t0 = time.time()
            for i, combo_str in enumerate(df_strat["Combination"].tolist()):
                r = evaluate_one_strategy(i, combo_str, df_data, args.fees, args.slippage, sim_kwargs)
                handle_result(r)
            meta["elapsed"] = round(time.time() - t0, 2)
        else:
            # Multiprocessing
            import multiprocessing as mp
            print(f"🚀 Multiprocessing: {args.num_procs} Prozesse, Chunksize={args.chunksize}…")
            t0 = time.time()

            def worker(idx):
                return evaluate_one_strategy(idx, df_strat.iloc[idx]["Combination"],
                                             df_data, args.fees, args.slippage, sim_kwargs)

            with mp.Pool(processes=args.num_procs) as pool:
                for r in pool.imap_unordered(worker, range(total), chunksize=args.chunksize):
                    handle_result(r)
            meta["elapsed"] = round(time.time() - t0, 2)

    meta["finished_at"] = datetime.now().isoformat(timespec="seconds")
    (outdir / "run_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"✅ Fertig. Ergebnisse: {results_csv.name} | Fehler: {errors_csv.name}")
    print(f"📦 Outdir: {outdir}")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()

