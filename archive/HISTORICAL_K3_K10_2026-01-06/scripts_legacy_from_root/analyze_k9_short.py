#!/usr/bin/env python3
# ASCII-only script. No emojis, no unicode symbols.

import argparse
import csv
import glob
import inspect
import importlib
import importlib.util
import json
import os
import sys
import time
from datetime import datetime
from multiprocessing import Pool

import pandas as pd


# --- Make repo root importable (critical for WSL) ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

PRICE_DF = None


def utc_ts():
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")


def backup_if_exists(path: str):
    if os.path.isfile(path):
        base, ext = os.path.splitext(path)
        bkp = f"{base}_backup_{utc_ts()}{ext}"
        os.replace(path, bkp)
        print(f"[info] Existing output backed up to: {bkp}")


def ensure_dir_for_file(path: str):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)


def parse_combo(s: str) -> dict:
    s = str(s).strip()
    try:
        d = json.loads(s)
        if not isinstance(d, dict):
            return {}
        out = {}
        for k, v in d.items():
            out[str(k)] = float(v)
        return out
    except Exception:
        return {}


def import_from_path(py_path: str, module_name: str):
    if not os.path.isfile(py_path):
        return None
    spec = importlib.util.spec_from_file_location(module_name, py_path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def import_evaluator():
    """
    Robust import:
    1) normal imports: engine.simtrader / simtrader / simtrader2
    2) file-based imports: engine/simtrader.py, simtrader.py, etc (even without __init__.py)
    """
    tried = []

    # 1) normal module imports
    for modpath in ["engine.simtrader", "simtrader", "engine.simtrader2", "simtrader2"]:
        try:
            m = importlib.import_module(modpath)
            if hasattr(m, "evaluate_strategy"):
                return getattr(m, "evaluate_strategy"), modpath
            tried.append((modpath, "import ok but no evaluate_strategy"))
        except Exception as e:
            tried.append((modpath, str(e)))

    # 2) file-based imports
    candidates = [
        (os.path.join(REPO_ROOT, "engine", "simtrader.py"), "engine_simtrader_file"),
        (os.path.join(REPO_ROOT, "engine", "simtrader2.py"), "engine_simtrader2_file"),
        (os.path.join(REPO_ROOT, "simtrader.py"), "simtrader_file"),
        (os.path.join(REPO_ROOT, "simtrader2.py"), "simtrader2_file"),
        (os.path.join(REPO_ROOT, "scripts", "simtrader.py"), "scripts_simtrader_file"),
        (os.path.join(REPO_ROOT, "scripts", "simtrader2.py"), "scripts_simtrader2_file"),
    ]

    for py_path, name in candidates:
        try:
            m = import_from_path(py_path, name)
            if m is not None and hasattr(m, "evaluate_strategy"):
                return getattr(m, "evaluate_strategy"), py_path
            if m is not None:
                tried.append((py_path, "loaded but no evaluate_strategy"))
        except Exception as e:
            tried.append((py_path, str(e)))

    print("[error] Could not import evaluate_strategy.")
    print("[info] Repo root assumed:", REPO_ROOT)
    print("[info] Tried (module/path -> error):")
    for t, err in tried:
        print(" -", t, ":", err)
    sys.exit(1)


def init_worker(price_path: str):
    global PRICE_DF
    PRICE_DF = pd.read_csv(price_path)

    # Minimal, robust sanity checks (no hard dependency on timestamp/open_time)
    required = ["close"]
    missing = [c for c in required if c not in PRICE_DF.columns]
    if missing:
        print("[error] price data missing required columns:", missing)
        print("[info] columns:", list(PRICE_DF.columns))
        raise SystemExit(2)

    # Warn if no time column exists (not required for simtrader)
    cols = set(PRICE_DF.columns)
    if "open_time" not in cols and "timestamp" not in cols and "datetime" not in cols:
        print("[warn] price data missing open_time/timestamp/datetime (not required, but check your pipeline).")


def call_evaluate(evaluate_strategy, combo: dict):
    global PRICE_DF
    sig = inspect.signature(evaluate_strategy)
    params = list(sig.parameters.keys())

    kwargs = {}
    # normalize to SHORT + regime usage (if supported)
    if "side" in params:
        kwargs["side"] = "short"
    if "direction" in params:
        kwargs["direction"] = "short"
    if "is_short" in params:
        kwargs["is_short"] = True
    if "use_regime" in params:
        kwargs["use_regime"] = True
    if "regime" in params:
        kwargs["regime"] = True
    if "mode" in params:
        kwargs["mode"] = "regime"

    try:
        return evaluate_strategy(PRICE_DF, combo, **kwargs)
    except TypeError:
        try:
            return evaluate_strategy(combo, PRICE_DF, **kwargs)
        except TypeError:
            return evaluate_strategy(PRICE_DF, **{"combination": combo, **kwargs})


def normalize_result(res):
    out = {
        "roi": None,
        "winrate": None,
        "num_trades": None,
        "avg_trade": None,
        "profit_factor": None,
        "sharpe": None,
        "max_dd": None,
        "error": "",
    }

    if res is None:
        out["error"] = "evaluate_strategy returned None"
        return out

    if isinstance(res, dict):
        for k in list(out.keys()):
            if k in res:
                out[k] = res.get(k)
        if out["winrate"] is None and "accuracy" in res:
            out["winrate"] = res.get("accuracy")
        if out["num_trades"] is None and "trades" in res:
            out["num_trades"] = res.get("trades")
        return out

    for k in ["roi", "winrate", "num_trades", "avg_trade", "profit_factor", "sharpe", "max_dd"]:
        if hasattr(res, k):
            out[k] = getattr(res, k)

    if out["winrate"] is None and hasattr(res, "accuracy"):
        out["winrate"] = getattr(res, "accuracy")

    return out


def worker_task(args):
    combo_json, source, seed_rank, evaluator_mod = args
    evaluate_strategy, _ = evaluator_mod

    combo = parse_combo(combo_json)
    if not combo:
        return {
            "Combination": combo_json,
            "source": source,
            "seed_rank": seed_rank,
            "roi": None,
            "winrate": None,
            "num_trades": None,
            "avg_trade": None,
            "profit_factor": None,
            "sharpe": None,
            "max_dd": None,
            "error": "bad Combination json",
        }

    try:
        res = call_evaluate(evaluate_strategy, combo)
        m = normalize_result(res)
        return {
            "Combination": combo_json,
            "source": source,
            "seed_rank": seed_rank,
            **m,
        }
    except Exception as e:
        return {
            "Combination": combo_json,
            "source": source,
            "seed_rank": seed_rank,
            "roi": None,
            "winrate": None,
            "num_trades": None,
            "avg_trade": None,
            "profit_factor": None,
            "sharpe": None,
            "max_dd": None,
            "error": str(e),
        }


def progress_line(done, total, t0, last_print, step_pct=5.0):
    if total <= 0:
        return None, last_print
    pct = (done / total) * 100.0
    if pct < last_print + step_pct and done != total:
        return None, last_print
    dt = time.time() - t0
    rate = done / dt if dt > 0 else 0.0
    eta = (total - done) / rate if rate > 0 else 0.0
    msg = f"[progress] {pct:6.2f}% ({done}/{total}) rate={rate:,.2f}/s elapsed={dt/60.0:,.1f}m eta={eta/60.0:,.1f}m"
    return msg, pct


def write_rows(path, fieldnames, rows, append):
    ensure_dir_for_file(path)
    mode = "a" if append else "w"
    with open(path, mode, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if not append:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-glob", required=True,
                    help="CSV(s) with column Combination; supports glob, or a single file path.")
    ap.add_argument("--out", required=True,
                    help="Output CSV path for results.")
    ap.add_argument("--price-data", default="data/price_data_with_signals_regime_short.csv")
    ap.add_argument("--num-procs", type=int, default=4)
    ap.add_argument("--batch-write", type=int, default=2000)
    ap.add_argument("--progress-step", type=float, default=5.0)
    ap.add_argument("--limit", type=int, default=0,
                    help="If >0, only analyze first N strategies (smoke/intermediate tests).")
    args = ap.parse_args()

    files = sorted(glob.glob(args.input_glob))
    if not files and os.path.isfile(args.input_glob):
        files = [args.input_glob]
    if not files:
        print("[error] No input files matched:", args.input_glob)
        sys.exit(1)

    if not os.path.isfile(args.price_data):
        print("[error] price data not found:", args.price_data)
        sys.exit(1)

    parts = []
    for f in files:
        parts.append(pd.read_csv(f))
    s = pd.concat(parts, ignore_index=True)

    if "Combination" not in s.columns:
        print("[error] missing column Combination in strategies.")
        print("[info] columns:", list(s.columns))
        sys.exit(1)

    if "source" not in s.columns:
        s["source"] = "seed_expansion"
    if "seed_rank" not in s.columns:
        s["seed_rank"] = 0

    if args.limit and args.limit > 0:
        s = s.head(int(args.limit)).copy()

    total = len(s)
    print("[info] Input rows:", total)
    print("[info] Using price data:", args.price_data)
    print("[info] Procs:", args.num_procs, " batch_write:", args.batch_write)

    out_main = args.out
    backup_if_exists(out_main)

    base, ext = os.path.splitext(out_main)
    out_merge = f"{base}_MERGE_SEEDS_PLUS_RANDOMPASS{ext}"
    backup_if_exists(out_merge)

    evaluate_strategy, src = import_evaluator()
    evaluator_mod = (evaluate_strategy, src)
    print("[info] evaluator source:", src)

    t0 = time.time()
    last_print = -999.0

    fieldnames = [
        "Combination", "source", "seed_rank",
        "roi", "winrate", "num_trades", "avg_trade", "profit_factor", "sharpe", "max_dd",
        "error"
    ]

    buffer_rows = []
    wrote_any = False

    tasks = [(row["Combination"], row.get("source", ""), int(row.get("seed_rank", 0)), evaluator_mod)
             for _, row in s.iterrows()]

    with Pool(processes=args.num_procs, initializer=init_worker, initargs=(args.price_data,)) as pool:
        for idx, res in enumerate(pool.imap_unordered(worker_task, tasks, chunksize=200), start=1):
            buffer_rows.append(res)

            if len(buffer_rows) >= args.batch_write:
                write_rows(out_main, fieldnames, buffer_rows, append=wrote_any)
                wrote_any = True
                buffer_rows = []

            msg, last_print = progress_line(idx, total, t0, last_print, step_pct=args.progress_step)
            if msg:
                print(msg)

        if buffer_rows:
            write_rows(out_main, fieldnames, buffer_rows, append=wrote_any)

    print("[ok] Wrote analyze results:", out_main)

    # --- Gate + Merge seeds + random pass ---
    dfres = pd.read_csv(out_main)

    if "source" in dfres.columns:
        seeds = dfres[dfres["source"] == "seed_expansion"].copy()
        rands = dfres[dfres["source"] == "random"].copy()
    else:
        seeds = dfres.copy()
        rands = dfres.iloc[0:0].copy()

    for col in ["roi", "winrate"]:
        if col in seeds.columns:
            seeds[col] = pd.to_numeric(seeds[col], errors="coerce")
        if col in rands.columns:
            rands[col] = pd.to_numeric(rands[col], errors="coerce")

    seeds_ok = seeds.dropna(subset=["roi", "winrate"])
    if len(seeds_ok) == 0:
        merged = seeds.copy()
        merged.to_csv(out_merge, index=False)
        print("[warn] No valid seed rows for gating. Wrote seeds only:", out_merge)
        return

    roi_p90 = float(seeds_ok["roi"].quantile(0.90))
    wr_med = float(seeds_ok["winrate"].median())

    rand_pass = rands.dropna(subset=["roi", "winrate"])
    rand_pass = rand_pass[(rand_pass["roi"] > roi_p90) & (rand_pass["winrate"] > wr_med)].copy()

    merged = pd.concat([seeds, rand_pass], ignore_index=True)
    merged.to_csv(out_merge, index=False)

    print("[gate] SEED rows:", len(seeds), "p90 roi:", roi_p90, "median winrate:", wr_med)
    print("[gate] RAND rows:", len(rands), "pass:", len(rand_pass))
    print("[ok] Wrote gated merged output:", out_merge)


if __name__ == "__main__":
    main()
