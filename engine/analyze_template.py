#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_template.py
Analyzer mit Hold-Time-Filter und effizientem Multiprocessing (kein DF in jedem Task).

ASCII-only Ausgaben. Erwartet:
- Daten-CSV mit 'open_time' oder 'timestamp' oder 'time'
- Strategien-CSV mit Spalte 'Combination' (Dict-String)
"""

import os, sys, ast, json, math, argparse
from datetime import datetime
from multiprocessing import Pool, cpu_count
import pandas as pd
import numpy as np

# --------- Logging / Utils ---------
def log(msg: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts} UTC] {msg}", flush=True)

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def parse_timestamp(series: pd.Series) -> pd.Series:
    s = series.copy()
    def _c(v):
        if pd.isna(v): return pd.NaT
        try:
            fv = float(v)
            if fv > 1e12: return pd.to_datetime(int(fv), unit="ms", utc=False)
            if fv > 1e9:  return pd.to_datetime(int(fv), unit="s", utc=False)
        except Exception:
            pass
        try:
            return pd.to_datetime(v, utc=False)
        except Exception:
            return pd.NaT
    return s.map(_c)

def parse_combination(cell: str) -> dict:
    if isinstance(cell, dict): return cell
    try: return ast.literal_eval(str(cell))
    except Exception: return {}

# --------- Hold-time Filter ---------
def _to_dt(x):
    if x is None: return None
    if isinstance(x, (np.integer, int, float)):
        fv = float(x)
        if fv > 1e12: return pd.to_datetime(int(fv), unit="ms")
        if fv > 1e9:  return pd.to_datetime(int(fv), unit="s")
        return None
    try: return pd.to_datetime(x)
    except Exception: return None

def compute_hold_minutes_from_trade(trade: dict, idx_to_time: pd.Series = None) -> float:
    et = None; xt = None
    for k in ("entry_time","entry_at","t_entry","timestamp_entry"):
        if k in trade: et = _to_dt(trade[k]); break
    if et is None and "entry_ts" in trade: et = _to_dt(trade["entry_ts"])
    if et is None and "entry_idx" in trade and idx_to_time is not None:
        try: et = pd.to_datetime(idx_to_time.iloc[int(trade["entry_idx"])])
        except Exception: et = None
    for k in ("exit_time","exit_at","t_exit","timestamp_exit"):
        if k in trade: xt = _to_dt(trade[k]); break
    if xt is None and "exit_ts" in trade: xt = _to_dt(trade["exit_ts"])
    if xt is None and "exit_idx" in trade and idx_to_time is not None:
        try: xt = pd.to_datetime(idx_to_time.iloc[int(trade["exit_idx"])])
        except Exception: xt = None
    if et is None or xt is None: return math.inf
    d = (xt - et).total_seconds() / 60.0
    if not np.isfinite(d): return math.inf
    return max(0.0, float(d))

def filter_trades_by_hold(trades: list, min_mins: int = None, max_mins: int = None, idx_to_time: pd.Series = None) -> list:
    if trades is None: return []
    if min_mins is None and max_mins is None: return trades
    out = []
    for tr in trades:
        hm = compute_hold_minutes_from_trade(tr, idx_to_time=idx_to_time)
        ok = True
        if min_mins is not None and (not np.isfinite(hm) or hm < float(min_mins)): ok = False
        if ok and max_mins is not None and (not np.isfinite(hm) or hm > float(max_mins)): ok = False
        if ok: out.append(tr)
    return out

def basic_metrics_from_trades(trades: list) -> dict:
    n = len(trades); pnls = []; wins = 0
    for tr in trades:
        pnl = None
        if "pnl" in tr and tr["pnl"] is not None:
            try: pnl = float(tr["pnl"])
            except Exception: pnl = None
        if pnl is None and ("entry_price" in tr and "exit_price" in tr):
            try:
                e = float(tr["entry_price"]); x = float(tr["exit_price"])
                side = tr.get("side","long")
                pnl = (e - x)/e if side=="short" else (x - e)/e
            except Exception: pnl = 0.0
        if pnl is None: pnl = 0.0
        pnls.append(pnl); 
        if pnl > 0: wins += 1
    pnl_sum = float(np.sum(pnls)) if n>0 else 0.0
    winrate = float(wins)/float(n) if n>0 else 0.0
    return {"roi": pnl_sum, "num_trades": n, "winrate": winrate, "pnl_sum": pnl_sum}

# --------- Optional user simulator ---------
def _import_user_simulator():
    try:
        import importlib
        m = importlib.import_module("engine.simtrader")
        if hasattr(m,"simulate_strategy"): return m.simulate_strategy
    except Exception: pass
    try:
        import importlib
        m = importlib.import_module("simtrader")
        if hasattr(m,"simulate_strategy"): return m.simulate_strategy
    except Exception: pass
    return None

# --------- Fallback simulator ---------
def _fallback_sim(data_df: pd.DataFrame, combo: dict, sim: str, threshold: float, cooldown: int, require_ma200: int, normalize: int, use_regime: int):
    df = data_df
    def norm_col(s: pd.Series):
        if s.dtype.kind in "biufc":
            mn = float(np.nanmin(s.values)); mx = float(np.nanmax(s.values))
            if mx > mn: return (s - mn)/(mx - mn)
        return s
    score = None
    for k, w in combo.items():
        col = k
        if col not in df.columns:
            for alt in (f"{k}_signal", k.lower(), k.upper()):
                if alt in df.columns: col = alt; break
        if col not in df.columns: continue
        s = df[col].astype(float)
        if normalize == 1: s = norm_col(s)
        sc = float(w)*s
        score = sc if score is None else (score + sc)
    if score is None: return {"trades": [], "meta": {"reason": "no_signals"}}
    _score = score.values.copy()

    if require_ma200 == 1:
        ma_col = None
        for a in ("ma200","MA200","ma200_signal"):
            if a in df.columns: ma_col = a; break
        if ma_col is not None:
            price_col = "close" if "close" in df.columns else df.columns[0]
            if sim == "long":
                mask_ok = (df[price_col].astype(float) > df[ma_col].astype(float)).values
            else:
                mask_ok = (df[price_col].astype(float) < df[ma_col].astype(float)).values
            _score[~mask_ok] = 0.0

    thr = float(threshold); in_pos = False; entry_idx = None; trades = []
    last_exit_idx = -10**9
    price_col = "close" if "close" in df.columns else df.columns[0]
    closev = df[price_col].astype(float).values

    for i in range(len(df)):
        sc = _score[i]
        if not in_pos:
            if i - last_exit_idx < int(cooldown): continue
            if sim == "long":
                if sc >= thr: in_pos=True; entry_idx=i
            else:
                if sc <= -thr: in_pos=True; entry_idx=i
        else:
            if sim == "long":
                if sc < thr:
                    exit_idx=i; e=closev[entry_idx]; x=closev[exit_idx]
                    trades.append({"side":"long","entry_idx":entry_idx,"exit_idx":exit_idx,"entry_price":e,"exit_price":x})
                    in_pos=False; entry_idx=None; last_exit_idx=i
            else:
                if sc > -thr:
                    exit_idx=i; e=closev[entry_idx]; x=closev[exit_idx]
                    trades.append({"side":"short","entry_idx":entry_idx,"exit_idx":exit_idx,"entry_price":e,"exit_price":x})
                    in_pos=False; entry_idx=None; last_exit_idx=i

    ts_col = None
    for c in ("open_time","timestamp","time"):
        if c in df.columns: ts_col=c; break
    if ts_col is not None:
        tsv = df[ts_col].values
        for tr in trades:
            try:
                tr["entry_time"] = tsv[int(tr.get("entry_idx",-1))]
                tr["exit_time"]  = tsv[int(tr.get("exit_idx",-1))]
            except Exception: pass
    return {"trades": trades, "meta": {}}

# --------- Globals for workers ---------
GLOBAL_DATA_DF = None
GLOBAL_TIME_MAP = None
GLOBAL_CFG = None
GLOBAL_SIM = None

def _init_worker(data_df, time_map, cfg_small, sim_func):
    global GLOBAL_DATA_DF, GLOBAL_TIME_MAP, GLOBAL_CFG, GLOBAL_SIM
    GLOBAL_DATA_DF = data_df
    GLOBAL_TIME_MAP = time_map
    GLOBAL_CFG = cfg_small
    GLOBAL_SIM = sim_func

def evaluate_one(task):
    idx, combo_row = task
    combo = parse_combination(combo_row)

    cfg = GLOBAL_CFG
    sim = cfg["sim"]
    threshold = cfg["threshold"]
    cooldown = cfg["cooldown"]
    require_ma200 = cfg["require_ma200"]
    normalize = cfg["normalize"]
    use_regime = cfg["use_regime"]
    min_trades = cfg["min_trades"]
    max_trades = cfg["max_trades"]
    min_hold = cfg["min_hold_mins"]
    max_hold = cfg["max_hold_mins"]
    save_trades = cfg["save_trades"]

    # simulate
    if GLOBAL_SIM is not None:
        try:
            result = GLOBAL_SIM(
                data_df=GLOBAL_DATA_DF,
                combo=combo,
                sim=sim,
                threshold=threshold,
                cooldown=cooldown,
                require_ma200=require_ma200,
                normalize=normalize,
                use_regime=use_regime
            )
        except TypeError:
            result = GLOBAL_SIM(GLOBAL_DATA_DF, combo, sim, threshold, cooldown, require_ma200)
    else:
        result = _fallback_sim(GLOBAL_DATA_DF, combo, sim, threshold, cooldown, require_ma200, normalize, use_regime)

    trades = result.get("trades", [])
    trades_f = filter_trades_by_hold(trades, min_mins=min_hold, max_mins=max_hold, idx_to_time=GLOBAL_TIME_MAP)

    if min_trades is not None and len(trades_f) < int(min_trades):
        metrics = {"roi": 0.0, "num_trades": len(trades_f), "winrate": 0.0, "pnl_sum": 0.0}
    elif max_trades is not None and len(trades_f) > int(max_trades):
        metrics = {"roi": 0.0, "num_trades": len(trades_f), "winrate": 0.0, "pnl_sum": 0.0}
    else:
        metrics = basic_metrics_from_trades(trades_f)

    out = {
        "index": idx,
        "Combination": json.dumps(combo, sort_keys=True),
        "roi": metrics["roi"],
        "num_trades": metrics["num_trades"],
        "winrate": metrics["winrate"],
        "pnl_sum": metrics["pnl_sum"],
    }
    if save_trades == 1:
        out["trades"] = trades_f
    return out

def main():
    p = argparse.ArgumentParser(description="Analyze strategies with Hold-Time filter (minutes).")
    p.add_argument("--data", required=True)
    p.add_argument("--strategies", required=True)
    p.add_argument("--sim", choices=["long","short"], default="long")
    p.add_argument("--k", type=int, default=None)
    p.add_argument("--threshold", type=float, default=0.60)
    p.add_argument("--cooldown", type=int, default=0)
    p.add_argument("--require-ma200", type=int, default=0)
    p.add_argument("--min-trades", type=int, default=0)
    p.add_argument("--max-trades", type=int, default=500000)
    p.add_argument("--num-procs", type=int, default=max(1, cpu_count()//2))
    p.add_argument("--chunksize", type=int, default=32)
    p.add_argument("--progress-step", type=int, default=2)
    p.add_argument("--save-trades", type=int, default=0)
    p.add_argument("--normalize", type=int, default=0)
    p.add_argument("--use-regime", type=int, default=0)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--min-hold-mins", type=int, default=None)
    p.add_argument("--max-hold-mins", type=int, default=None)
    args = p.parse_args()

    ensure_dir(args.output_dir)
    results_csv = os.path.join(args.output_dir, "strategy_results.csv")
    trades_dir = os.path.join(args.output_dir, "trades"); ensure_dir(trades_dir)

    if os.path.isfile(results_csv):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup = os.path.join(args.output_dir, f"strategy_results_backup_{ts}.csv")
        log(f"Existing results detected. Backup to {backup}")
        try: os.rename(results_csv, backup)
        except Exception: pass

    log(f"Loading data: {args.data}")
    df = pd.read_csv(args.data)

    ts_col = None
    for c in ("open_time","timestamp","time"):
        if c in df.columns: ts_col=c; break
    if ts_col is None:
        df["open_time"] = np.arange(len(df), dtype=np.int64)
        ts_col = "open_time"
    time_map = parse_timestamp(df[ts_col])

    log(f"Loading strategies: {args.strategies}")
    strat_df = pd.read_csv(args.strategies)
    if "Combination" not in strat_df.columns:
        raise ValueError("Strategies CSV must contain column 'Combination'.")

    total = len(strat_df)
    log(f"{total} strategies loaded")

    user_sim = _import_user_simulator()
    if user_sim is not None: log("Using simulate_strategy from user simtrader.")
    else: log("User simtrader not found. Using fallback simulator.")

    cfg_small = {
        "sim": args.sim,
        "threshold": args.threshold,
        "cooldown": args.cooldown,
        "require_ma200": args.require_ma200,
        "normalize": args.normalize,
        "use_regime": args.use_regime,
        "min_trades": args.min_trades,
        "max_trades": args.max_trades,
        "min_hold_mins": args.min_hold_mins,
        "max_hold_mins": args.max_hold_mins,
        "save_trades": args.save_trades,
        "progress_step": max(1, int(args.progress_step)),
    }

    tasks = [(i, strat_df["Combination"].iat[i]) for i in range(total)]
    results = []; last_pct = -1

    # Single-process fast path for tiny runs or debug
    if int(args.num_procs) <= 1:
        # init globals
        _init_worker(df, time_map, cfg_small, user_sim)
        for j, t in enumerate(tasks):
            res = evaluate_one(t); results.append(res)
            pct = int((100.0*len(results))/max(total,1))
            if pct // cfg_small["progress_step"] > last_pct // cfg_small["progress_step"]:
                last_pct = pct; log(f"Progress {pct}% ({len(results)}/{total})")
    else:
        with Pool(processes=int(args.num_procs),
                  initializer=_init_worker,
                  initargs=(df, time_map, cfg_small, user_sim)) as pool:
            for j, res in enumerate(pool.imap_unordered(evaluate_one, tasks, chunksize=int(args.chunksize))):
                results.append(res)
                pct = int((100.0*len(results))/max(total,1))
                if pct // cfg_small["progress_step"] > last_pct // cfg_small["progress_step"]:
                    last_pct = pct; log(f"Progress {pct}% ({len(results)}/{total})")

    res_df = pd.DataFrame(results)
    if "trades" in res_df.columns:
        log("Writing per-strategy trades to files")
        for _, row in res_df.iterrows():
            if isinstance(row.get("trades", None), list):
                fname = os.path.join(trades_dir, f"trades_{row['index']:08d}.json")
                try:
                    with open(fname, "w", encoding="utf-8") as f:
                        json.dump(row["trades"], f, ensure_ascii=True)
                except Exception: pass
        res_df = res_df.drop(columns=["trades"], errors="ignore")

    res_df = res_df.sort_values(by=["roi"], ascending=False)
    res_df.to_csv(results_csv, index=False)
    log(f"Saved results to {results_csv}")
    log("Done.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"FATAL: {e}")
        sys.exit(1)








