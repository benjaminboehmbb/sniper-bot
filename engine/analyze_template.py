#!/usr/bin/env python3
# engine/analyze_template.py
# ASCII only.
#
# Safe-Mode Analyzer:
# - Block-MP: jede CPU laedt die Price-CSV genau 1x
# - Robuste Spalten-Aufloesung (case-insensitive, *_signal-Aliase)
# - Worker laden ALLE Spalten (kein usecols), dann Sanitizing
# - NaN/Inf werden bereinigt, Trades mit fehlenden Preisen werden uebersprungen
# - Ergebnisse gefiltert per min_trades/max_trades
#
# CLI-Beispiel:
# PYTHONIOENCODING=UTF-8 \
# python -u engine/analyze_template.py \
#   --data data/price_data_with_signals.csv \
#   --strategies data/strategies/k3/strategies_k3_shard1.csv \
#   --sim long --k 3 \
#   --threshold 0.60 --cooldown 0 --require-ma200 1 \
#   --min-trades 50 --max-trades 50000 \
#   --num-procs 8 --progress-step 1000 \
#   --save-trades 0 --output-dir results/k3/long

import argparse
import ast
import csv
import datetime as _dt
import multiprocessing as mp
import os
import sys
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd

# Optionaler externer SimTrader (falls vorhanden)
_SIMTRADER = None
try:
    from engine import simtrader as _SIMTRADER  # type: ignore
except Exception:
    _SIMTRADER = None

# ---------------- Utils ----------------

def _ts() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")

def _info(msg: str) -> None:
    sys.stdout.write("[INFO] " + msg + "\n"); sys.stdout.flush()

def _warn(msg: str) -> None:
    sys.stderr.write("[WARN] " + msg + "\n"); sys.stderr.flush()

def _err(msg: str) -> None:
    sys.stderr.write("[ERROR] " + msg + "\n"); sys.stderr.flush()

def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def _read_strategies_csv(path: str) -> List[str]:
    combos: List[str] = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        if "Combination" not in reader.fieldnames:
            raise RuntimeError("Missing column 'Combination' in strategies CSV: " + path)
        for row in reader:
            combos.append(row["Combination"])
    return combos

def _parse_combo(combo_str: str) -> Dict[str, float]:
    d = ast.literal_eval(combo_str)
    clean: Dict[str, float] = {}
    for k, v in d.items():
        clean[str(k)] = float(v)
    return clean

# Aliase fuer flexible Spalten-Aufloesung
_ALIASES = {
    "bb": "bollinger",
    "bbands": "bollinger",
    "boll": "bollinger",
    "ema": "ema50",
    "sma200": "ma200",
    "ma": "ma200",
    "stochastic": "stoch",
}

def _lower_map(cols: List[str]) -> Dict[str, str]:
    return {c.lower(): c for c in cols}

def _candidate_names(base: str) -> List[str]:
    b = base
    if b in _ALIASES:
        b = _ALIASES[b]
    if b.endswith("_signal"):
        root = b[:-7]
        return [b, root, root + "_signal"]
    else:
        return [b, b + "_signal"]

def _resolve_signal_column(df: pd.DataFrame, name: str) -> str:
    cols = list(df.columns)
    lmap = _lower_map(cols)
    # 1) direkte Kandidaten
    for cand in _candidate_names(name):
        if cand in df.columns:
            return cand
        lc = cand.lower()
        if lc in lmap:
            return lmap[lc]
    # 2) breitere Suche
    base = _ALIASES.get(name, name)
    base_l = base.lower()
    # a) Prefix
    for c in cols:
        if c.lower().startswith(base_l):
            return c
    # b) Contains + "signal"
    for c in cols:
        cl = c.lower()
        if (base_l in cl) and ("signal" in cl):
            return c
    # 3) typische Varianten
    _common = {
        "macd": ["macd_signal", "macd_hist", "macd_diff", "macd"],
        "rsi": ["rsi_signal", "rsi"],
        "bollinger": ["bollinger_signal", "bb_signal", "bollinger"],
        "stoch": ["stoch_signal", "stoch_k", "stoch_d", "stoch"],
        "ema50": ["ema50_signal", "ema50"],
        "ma200": ["ma200_signal", "ma200"],
        "adx": ["adx_signal", "adx"],
        "cci": ["cci_signal", "cci"],
        "mfi": ["mfi_signal", "mfi"],
        "obv": ["obv_signal", "obv"],
        "roc": ["roc_signal", "roc"],
        "atr": ["atr_signal", "atr"],
    }
    root = base_l
    if root in _common:
        for cand in _common[root]:
            if cand in df.columns:
                return cand
            lc = cand.lower()
            if lc in lmap:
                return lmap[lc]
    raise KeyError("Signal column not found for '%s'." % name)

def _get_time_col(df: pd.DataFrame) -> str:
    if "open_time" in df.columns:
        return "open_time"
    if "timestamp" in df.columns:
        return "timestamp"
    cols_l = _lower_map(list(df.columns))
    if "open_time" in cols_l:
        return cols_l["open_time"]
    if "timestamp" in cols_l:
        return cols_l["timestamp"]
    raise RuntimeError("No time column ('open_time' or 'timestamp').")

# ---------------- Fallback Backtest ----------------

def _fallback_backtest(df: pd.DataFrame,
                       combo: Dict[str, float],
                       params: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    thr = float(params.get("threshold", 0.0))
    cooldown = int(params.get("cooldown", 0))
    max_hold = int(params.get("max_hold", 0))
    require_ma200 = int(params.get("require_ma200", 0)) == 1
    sim_mode = str(params.get("sim", "long"))

    close = df["close"].values
    n = len(df)

    cols, weights = [], []
    for k, w in combo.items():
        col = _resolve_signal_column(df, k)
        cols.append(col)
        weights.append(float(w))
    cols_arr = df[cols].values

    ma200_allow = None
    if require_ma200:
        try:
            ma_col = _resolve_signal_column(df, "ma200")
            if ma_col.endswith("_signal"):
                ma200_allow = (df[ma_col].values > 0)
            else:
                ma200_allow = (df["close"].values > df[ma_col].values)
        except Exception:
            ma200_allow = None

    position = 0
    entry_i = -1
    trades: List[Dict[str, Any]] = []
    cd = 0

    i = 0
    while i < n - 1:
        if cd > 0:
            cd -= 1

        # Score
        score = 0.0
        row_vec = cols_arr[i]
        for j in range(len(weights)):
            score += weights[j] * float(row_vec[j])

        # Filter ma200, falls gefordert
        if ma200_allow is not None and not bool(ma200_allow[i]):
            score = -1e18 if sim_mode == "long" else 1e18

        if position == 0 and cd == 0:
            if sim_mode == "long" and score > thr:
                position = 1
                entry_i = i
            elif sim_mode == "short" and score < -thr:
                position = -1
                entry_i = i
        else:
            exit_now = True
            if max_hold > 0 and (i - entry_i) >= max_hold:
                exit_now = True
            if exit_now:
                p1 = close[i + 1]
                p0 = close[entry_i]
                if pd.notna(p0) and pd.notna(p1):
                    pnl = (p1 - p0) if position == 1 else (p0 - p1)
                    trades.append({"entry_idx": int(entry_i), "exit_idx": int(i + 1), "pnl": float(pnl)})
                # sonst Trade skippen
                position = 0
                entry_i = -1
                cd = cooldown
        i += 1

    num_trades = len(trades)
    total_pnl = float(sum(t["pnl"] for t in trades)) if num_trades > 0 else 0.0
    avg_pnl = float(total_pnl / num_trades) if num_trades > 0 else 0.0
    hits = int(sum(1 for t in trades if t["pnl"] > 0))
    misses = int(num_trades - hits)
    winrate = float(hits / num_trades) if num_trades > 0 else 0.0

    res = {
        "num_trades": int(num_trades),
        "total_pnl": total_pnl,
        "avg_pnl": avg_pnl,
        "winrate": winrate,
        "hits": hits,
        "misses": misses,
    }
    return res, trades

def _run_one(df: pd.DataFrame, combo_str: str, params: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "combination": combo_str,
        "num_trades": 0,
        "total_pnl": 0.0,
        "avg_pnl": 0.0,
        "winrate": 0.0,
        "hits": 0,
        "misses": 0,
        "error": "",
    }
    try:
        combo = _parse_combo(combo_str)
        if int(params.get("normalize", 0)) == 1:
            s = sum(abs(v) for v in combo.values())
            if s > 0:
                combo = {k: v / s for k, v in combo.items()}

        if _SIMTRADER is not None and hasattr(_SIMTRADER, "run_backtest"):
            res, _ = _SIMTRADER.run_backtest(df, combo, params)  # type: ignore
        else:
            res, _ = _fallback_backtest(df, combo, params)
        out.update(res)
    except Exception as e:
        out["error"] = str(e)
    return out

# ---------------- Worker (Safe Mode: alle Spalten) ----------------

def _worker_block(args) -> Dict[str, Any]:
    block_id, data_path, combos_block, params, progress_step = args

    # CSV laden (alle Spalten), dann Sanitizing
    df = pd.read_csv(data_path)
    # sanitize
    df = df.replace([np.inf, -np.inf], np.nan)
    if "close" not in df.columns:
        raise RuntimeError("Required column 'close' missing in price CSV.")
    df = df.dropna(subset=["close"])
    for c in df.columns:
        if str(c).lower().endswith("_signal"):
            df[c] = df[c].fillna(0)

    results: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    total = len(combos_block)
    done = 0

    for combo_str in combos_block:
        out = _run_one(df, combo_str, params)
        if out.get("error"):
            errors.append(out)
        else:
            nt = int(out.get("num_trades", 0))
            if nt >= params["min_trades"] and nt <= params["max_trades"]:
                results.append(out)
        done += 1
        if progress_step > 0 and (done % progress_step == 0):
            _info("Worker %d progress %d/%d (%.2f%%)" % (block_id, done, total, (done * 100.0) / total))

    return {"block_id": block_id, "results": results, "errors": errors}

# ---------------- Main ----------------

def main():
    ap = argparse.ArgumentParser(description="Universal analyze backend (Block-MP, robust, SAFE all-columns).")
    ap.add_argument("--data", required=True, type=str)
    ap.add_argument("--strategies", required=True, type=str)
    ap.add_argument("--sim", required=True, choices=["long", "short"])
    ap.add_argument("--k", required=True, type=int)

    ap.add_argument("--threshold", type=float, default=0.0)
    ap.add_argument("--cooldown", type=int, default=0)
    ap.add_argument("--max-hold", dest="max_hold", type=int, default=0)
    ap.add_argument("--require-ma200", dest="require_ma200", type=int, default=0)

    ap.add_argument("--min-trades", dest="min_trades", type=int, default=0)
    ap.add_argument("--max-trades", dest="max_trades", type=int, default=250000)

    ap.add_argument("--num-procs", type=int, default=max(1, mp.cpu_count() // 2))
    ap.add_argument("--progress-step", dest="progress_step", type=int, default=500)
    ap.add_argument("--save-trades", dest="save_trades", type=int, default=0)
    ap.add_argument("--output-dir", dest="output_dir", type=str, required=True)
    ap.add_argument("--normalize", type=int, default=0)

    args = ap.parse_args()
    _ensure_dir(args.output_dir)

    # Kopf pruefen
    df0 = pd.read_csv(args.data, nrows=5)
    _ = _get_time_col(df0)
    if "close" not in df0.columns and "Close" in df0.columns:
        df0 = df0.rename(columns={"Close": "close"})
    if "close" not in df0.columns:
        raise RuntimeError("Required column 'close' missing in price CSV.")

    combos = _read_strategies_csv(args.strategies)
    total = len(combos)
    if total == 0:
        raise RuntimeError("No combinations in strategies CSV.")

    params = {
        "sim": args.sim,
        "k": args.k,
        "threshold": float(args.threshold),
        "cooldown": int(args.cooldown),
        "max_hold": int(args.max_hold),
        "require_ma200": int(args.require_ma200),
        "min_trades": int(args.min_trades),
        "max_trades": int(args.max_trades),
        "normalize": int(args.normalize),
        "save_trades": int(args.save_trades),
    }

    _info("Starting SAFE block-MP: combinations=%d, procs=%d" % (total, args.num_procs))

    # Bloecke bilden
    nprocs = max(1, int(args.num_procs))
    blocks: List[List[str]] = [[] for _ in range(nprocs)]
    for idx, cstr in enumerate(combos):
        blocks[idx % nprocs].append(cstr)

    tasks = []
    for b_id in range(nprocs):
        if not blocks[b_id]:
            continue
        tasks.append((b_id, args.data, blocks[b_id], params, int(args.progress_step)))

    results_all: List[Dict[str, Any]] = []
    errors_all: List[Dict[str, Any]] = []

    if nprocs == 1:
        out = _worker_block(tasks[0])
        results_all.extend(out["results"])
        errors_all.extend(out["errors"])
    else:
        with mp.Pool(processes=nprocs) as pool:
            for out in pool.imap_unordered(_worker_block, tasks, chunksize=1):
                results_all.extend(out["results"])
                errors_all.extend(out["errors"])

    ts = _ts()
    out_name = "strategy_results_%s_k%d_%s.csv" % (args.sim, args.k, ts)
    out_path = os.path.join(args.output_dir, out_name)
    _ensure_dir(args.output_dir)

    fieldnames = ["combination", "num_trades", "total_pnl", "avg_pnl", "winrate", "hits", "misses", "error"]
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results_all:
            w.writerow(r)
        for e in errors_all:
            w.writerow(e)

    _info("Wrote results: %s (rows=%d, errors=%d)" % (out_path, len(results_all), len(errors_all)))
    if errors_all:
        err_path = os.path.join(args.output_dir, "errors_%s_k%d_%s.csv" % (args.sim, args.k, ts))
        with open(err_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for e in errors_all:
                w.writerow(e)
        _warn("Errors written: %s (count=%d)" % (err_path, len(errors_all)))

    _info("Done.")
    return 0

if __name__ == "__main__":
    sys.exit(main())




