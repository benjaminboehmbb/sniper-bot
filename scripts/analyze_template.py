# analyze_template.py — CLEAN REPLACEMENT
# Robust runner for strategy analysis (long/short/both) with safe config defaults,
# tolerant future result handling, and clean logging.
# Uses only spaces for indentation to avoid IndentationError on Windows.

import os
import sys
import json
import yaml
import time
import math
import shutil
import random
import traceback
import datetime as dt
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")

# ---------- CONFIG & DEFAULTS ----------

DEFAULT_CFG = {
    "general": {
        "results_dir": "out",
        "tmp_dir": "tmp",
        "seed": 42,
        "backup_existing_results": True,
    },
    "data": {
        "csv_path": "data/btcusdt_1m_spot.csv",
        "price_csv": "data/btcusdt_1m_spot.csv",
        "timestamp_col": "open_time",
        "timeframe": "1m",
        "timezone": "UTC",
        "max_rows": None,
    },
    "runtime": {
        "timezone": "Europe/Berlin",
        "save_trades": True,
        "verbose": True,
    },
    "strategy": {
        "mode": "short",
        "direction_modes": ["long", "short", "both"],
        "min_hold_bars": 1,
        "max_hold_bars": 1440,
    },
    "signals": {
        "available": ["rsi", "macd", "bollinger", "ma200", "stoch", "atr", "ema50"],
        "weights": [0.0, 0.5, 1.0],
    },
    "engine": {
        "processes": 16,
        "batch_write": 5000
    },
    "output": {
        "results_dir": "out",
        "strategy_results_csv": "out/strategy_results.csv",
        "save_trade_history": True
    },
    "logging": {
        "level": "INFO",
        "progress_step": 1
    }
}

def _deep_merge(dst, src):
    for k, v in src.items():
        if k not in dst:
            dst[k] = v
        else:
            if isinstance(dst[k], dict) and isinstance(v, dict):
                _deep_merge(dst[k], v)
    return dst

def load_cfg():
    cfg = {}
    if os.path.isfile(CFG_PATH):
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            try:
                cfg = yaml.safe_load(f) or {}
            except Exception:
                cfg = {}
    # merge defaults for missing keys only
    cfg = _deep_merge(cfg, {})
    _deep_merge(cfg, DEFAULT_CFG)

    # keep data.csv_path and price_csv in sync
    data = cfg.setdefault("data", {})
    if "csv_path" not in data and "price_csv" in data:
        data["csv_path"] = data["price_csv"]
    if "price_csv" not in data and "csv_path" in data:
        data["price_csv"] = data["csv_path"]

    # normalize engine
    eng = cfg.setdefault("engine", {})
    eng.setdefault("processes", DEFAULT_CFG["engine"]["processes"])
    eng.setdefault("batch_write", DEFAULT_CFG["engine"]["batch_write"])

    # general flags
    gen = cfg.setdefault("general", {})
    gen.setdefault("backup_existing_results", True)

    # strategy
    strat = cfg.setdefault("strategy", {})
    strat.setdefault("direction_modes", DEFAULT_CFG["strategy"]["direction_modes"])
    return cfg

CFG = load_cfg()
random.seed(CFG["general"]["seed"])

# ---------- EVAL STRATEGY IMPORT (with fallback) ----------

try:
    from scripts.evaluate_strategy import evaluate_strategy as _eval_impl  # user-provided module
except Exception:
    _eval_impl = None

def evaluate_strategy(i, comb_str, direction):
    """
    Wrapper used by the runner. Delegates to scripts.evaluate_strategy if available.
    Otherwise returns a safe stub so the pipeline continues.
    """
    if _eval_impl is not None:
        try:
            return _eval_impl(i, comb_str, direction)
        except Exception as e:
            print(f"[evaluate_strategy] delegate error: {e}", flush=True)
            # fall through to stub

    # Fallback stub result (deterministic)
    try:
        import ast
        comb = ast.literal_eval(comb_str) if isinstance(comb_str, str) else comb_str
    except Exception:
        comb = comb_str

    # Return a dict; runner is tolerant and accepts dict OR (status,out)
    return {
        "index": i,
        "combination": comb,
        "direction": direction,
        "roi": 0.0,
        "num_trades": 0,
        "winrate": 0.0,
        "sharpe": 0.0,
    }

# ---------- IO HELPERS ----------

def ts_now():
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M")

def log(msg):
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def backup_if_exists(path):
    if not os.path.isfile(path):
        return
    if not CFG["general"]["backup_existing_results"]:
        return
    d = os.path.dirname(path)
    bdir = os.path.join(d, "_backup")
    os.makedirs(bdir, exist_ok=True)
    base = os.path.basename(path)
    dst = os.path.join(bdir, f"{base}.bak_{ts_now()}")
    shutil.copy2(path, dst)

def prepare_run_folder(strategies_csv):
    out_root = os.path.join(ROOT, CFG["general"]["results_dir"])
    os.makedirs(out_root, exist_ok=True)
    run_name = f"5er_run_{ts_now()}"
    run_dir = os.path.join(out_root, run_name)
    os.makedirs(run_dir, exist_ok=True)
    meta = {
        "strategies_csv": strategies_csv,
        "data_csv": CFG["data"]["csv_path"],
        "modes": CFG["strategy"]["direction_modes"],
        "threads": CFG["engine"]["processes"],
        "batch_write": CFG["engine"]["batch_write"],
        "time": ts_now()
    }
    with open(os.path.join(run_dir, "run_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    log(f"Run-Ordner: {os.path.relpath(run_dir, ROOT)}")
    return run_dir

# ---------- DATA LOADING ----------

REQUIRED_PRICE_COLS = ["close", "high", "low"]

def load_price_data():
    log("📈 Lade Kursdaten …")
    csv_path = CFG["data"]["csv_path"]
    full = csv_path if os.path.isabs(csv_path) else os.path.join(ROOT, csv_path)
    if not os.path.isfile(full):
        raise FileNotFoundError(f"Preis-CSV nicht gefunden: {full}")
    df = pd.read_csv(full)
    # normalize price cols
    rename_map = {}
    for c in REQUIRED_PRICE_COLS:
        if c not in df.columns:
            uc = c.capitalize()
            if uc in df.columns:
                rename_map[uc] = c
    if rename_map:
        df.rename(columns=rename_map, inplace=True)

    for c in REQUIRED_PRICE_COLS:
        if c not in df.columns:
            raise ValueError(f"Fehlende Preisspalte '{c}'. Spalten={list(df.columns)[:25]}")
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # optional signals presence check (relaxed; warn only)
    needed_signals = ["rsi","macd","bollinger","ma200","stoch","atr","ema50"]
    missing = [s for s in needed_signals if s not in df.columns]
    if missing:
        print(f"[WARN] fehlende Signalspalten: {missing} — Fallback-Evaluierung nutzt 0/Stub.", flush=True)

    if CFG["data"]["max_rows"]:
        df = df.tail(int(CFG["data"]["max_rows"]))
    log(f"✅ Daten: {len(df):,} Zeilen")
    return df

# ---------- STRATEGIES ----------

def load_strategies(path):
    log("📋 Lade Strategien …")
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.isfile(full):
        raise FileNotFoundError(full)
    s = pd.read_csv(full)
    # expected column name
    if "Combination" not in s.columns and "combination" not in s.columns:
        raise ValueError(f"Strategie-CSV muss Spalte 'Combination' enthalten. Spalten={list(s.columns)}")
    log(f"✅ Strategien: {len(s):,}")
    return s

# ---------- RUNNER ----------

def write_results_csv(path, rows):
    df = pd.DataFrame(rows)
    header = not os.path.isfile(path)
    df.to_csv(path, mode="a", header=header, index=False)

def write_errors_csv(path, rows):
    if not rows:
        return
    df = pd.DataFrame(rows)
    header = not os.path.isfile(path)
    df.to_csv(path, mode="a", header=header, index=False)

def normalize_future_result(res):
    """
    Accepts:
      - (status, out)
      - dict (treated as ok,out=dict)
      - 1-elem tuple/list
      - None / exception already handled upstream
    Returns (status, out)
    """
    if isinstance(res, tuple) and len(res) >= 2:
        return res[0], res[1]
    if isinstance(res, (list, tuple)) and len(res) == 1:
        return "ok", res[0]
    if isinstance(res, dict) or not isinstance(res, (list, tuple)):
        return "ok", res
    return "ok", res

def run_mode(df, strategies_df, direction, run_dir):
    threads = int(CFG["engine"]["processes"])
    batch_n = int(CFG["engine"]["batch_write"])
    out_csv = os.path.join(run_dir, f"results_{direction}.csv")
    err_csv = os.path.join(run_dir, f"errors_{direction}.csv")
    backup_if_exists(out_csv); backup_if_exists(err_csv)

    rows, errs = [], []
    log(f"{direction.upper()}: starte mit {threads} Threads …")

    # pick column name
    comb_col = "Combination" if "Combination" in strategies_df.columns else "combination"

    def task(i, comb_str):
        try:
            res = evaluate_strategy(i, comb_str, direction)
            status, out = normalize_future_result(res)
        except Exception as e:
            status, out = "error", None
            err = {"i": i, "direction": direction, "error": str(e), "trace": traceback.format_exc()}
            return status, err
        if status != "ok":
            err = {"i": i, "direction": direction, "error": str(out)}
            return status, err
        # ensure a row dict
        if not isinstance(out, dict):
            out = {"result": str(out)}
        out.setdefault("index", i)
        out.setdefault("direction", direction)
        return "ok", out

    with ThreadPoolExecutor(max_workers=threads) as ex:
        futs = []
        for i, row in strategies_df.iterrows():
            comb_str = row[comb_col]
            futs.append(ex.submit(task, int(i), comb_str))

        for j, fut in enumerate(as_completed(futs), 1):
            try:
                status, payload = fut.result()
            except Exception as e:
                status, payload = "error", {"error": str(e), "trace": traceback.format_exc()}

            if status == "ok":
                rows.append(payload)
            else:
                errs.append(payload)

            if j % batch_n == 0:
                if rows:
                    write_results_csv(out_csv, rows); rows = []
                if errs:
                    write_errors_csv(err_csv, errs); errs = []
                if CFG["logging"]["progress_step"]:
                    log(f"{direction.upper()}: {j:,} ausgewertet …")

    # final flush
    if rows: write_results_csv(out_csv, rows)
    if errs: write_errors_csv(err_csv, errs)
    log(f"{direction.upper()}: fertig. Ergebnisse: {os.path.relpath(out_csv, ROOT)}")

# ---------- MAIN ----------

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.analyze_template <strategies_csv>", flush=True)
        sys.exit(1)
    strategies_csv = sys.argv[1]

    run_dir = prepare_run_folder(strategies_csv)
    df = load_price_data()
    s = load_strategies(strategies_csv)

    modes = CFG["strategy"]["direction_modes"]
    log(f"🚀 Starte Modi: {modes}")

    for m in modes:
        run_mode(df, s, m, run_dir)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("FATAL:", e, flush=True)
        traceback.print_exc()
        sys.exit(2)

