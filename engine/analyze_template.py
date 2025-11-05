#!/usr/bin/env python3
# engine/analyze_template.py
# Universelle Analyse-Engine mit optionaler Regime-Filterung
# K2–K12 (Long/Short), rueckwaertskompatibel (macd_hist -> macd Fallback)

import argparse
import pandas as pd
import numpy as np
import multiprocessing as mp
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------
# Utils
# ------------------------------------------------------------

def parse_combination(raw):
    if isinstance(raw, str):
        try:
            return eval(raw)
        except Exception:
            return {}
    return raw

def ensure_compat_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Fallback: wenn 'macd' fehlt, aber 'macd_hist' existiert
    if "macd" not in df.columns and "macd_hist" in df.columns:
        df = df.copy()
        df["macd"] = df["macd_hist"]
    return df

# ------------------------------------------------------------
# Single strategy eval
# ------------------------------------------------------------

def evaluate_strategy(args):
    combo, df, sim, threshold, cooldown, require_ma200, min_trades, max_trades, normalize, use_regime = args
    try:
        weights = parse_combination(combo)
        if not isinstance(weights, dict) or not weights:
            return None

        # Nur Spalten verwenden, die existieren
        cols = [c for c in weights.keys() if c in df.columns]
        if not cols:
            return None

        sig = np.zeros(len(df), dtype=np.float64)
        # Wichtig: nur ueber vorhandene Spalten iterieren
        for c in cols:
            w = float(weights[c])
            sig += df[c].values * w

        if normalize:
            mu = sig.mean()
            sd = sig.std()
            sig = (sig - mu) / (sd + 1e-9)

        # Regime-Filter
        if use_regime and "regime_signal" in df.columns:
            sig = sig * df["regime_signal"].values

        thr = threshold
        pos = 0
        last_trade = -10**9
        pnl = []
        entry = 0.0

        close = df["close"].values

        for i in range(1, len(sig)):
            # Cooldown
            if cooldown > 0 and (i - last_trade) < cooldown:
                continue

            if sim == "long":
                if sig[i] > thr and pos == 0:
                    pos = 1
                    entry = close[i]
                    last_trade = i
                elif sig[i] < -thr and pos == 1:
                    pnl.append(close[i] - entry)
                    pos = 0
                    last_trade = i

            else:  # short
                if sig[i] < -thr and pos == 0:
                    pos = -1
                    entry = close[i]
                    last_trade = i
                elif sig[i] > thr and pos == -1:
                    pnl.append(entry - close[i])
                    pos = 0
                    last_trade = i

        num_trades = len(pnl)
        if num_trades < min_trades or num_trades > max_trades:
            return None

        pnl = np.asarray(pnl, dtype=np.float64)
        total_pnl = float(pnl.sum())
        avg_pnl = float(pnl.mean()) if num_trades > 0 else 0.0
        winrate = float((pnl > 0).mean()) if num_trades > 0 else 0.0
        roi = total_pnl / max(1.0, num_trades)

        return {
            "Combination": str(weights),
            "num_trades": int(num_trades),
            "total_pnl": total_pnl,
            "avg_pnl": avg_pnl,
            "winrate": winrate,
            "roi": roi
        }

    except Exception as e:
        return {"Combination": str(combo), "error": str(e)}

# ------------------------------------------------------------
# MP engine
# ------------------------------------------------------------

def run_pool(df, combos, sim, threshold, cooldown, require_ma200, min_trades,
             max_trades, num_procs, progress_step, normalize, use_regime):

    args_list = [
        (combo, df, sim, threshold, cooldown, require_ma200,
         min_trades, max_trades, normalize, use_regime)
        for combo in combos
    ]

    results = []
    with mp.get_context("spawn").Pool(processes=num_procs) as pool:
        for idx, res in enumerate(pool.imap_unordered(evaluate_strategy, args_list), 1):
            if res:
                results.append(res)
            if progress_step > 0 and (idx % progress_step == 0):
                print(f"[{idx}/{len(combos)} processed]")

    return results

# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--strategies", required=True)
    ap.add_argument("--sim", required=True, choices=["long", "short"])
    ap.add_argument("--k", required=True, type=int)
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--cooldown", type=int, default=0)
    ap.add_argument("--max-hold", type=int, default=0)
    ap.add_argument("--require-ma200", type=int, default=1)
    ap.add_argument("--min-trades", type=int, default=50)
    ap.add_argument("--max-trades", type=int, default=50000)
    ap.add_argument("--num-procs", type=int, default=14)
    ap.add_argument("--progress-step", type=int, default=2)
    ap.add_argument("--save-trades", type=int, default=0)
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--normalize", type=int, default=0)
    ap.add_argument("--use-regime", type=int, default=1)
    args = ap.parse_args()

    data_path = Path(args.data)
    strat_path = Path(args.strategies)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("[INFO] Loading data:", data_path)
    df = pd.read_parquet(str(data_path)) if str(data_path).endswith(".parquet") else pd.read_csv(str(data_path))
    df = ensure_compat_columns(df)  # macd_hist -> macd (falls noetig)

    print("[INFO] Loading strategies:", strat_path)
    combos = pd.read_csv(strat_path)["Combination"].tolist()
    print(f"[INFO] {len(combos)} strategies loaded")

    results = run_pool(
        df, combos, args.sim, args.threshold, args.cooldown,
        args.require_ma200, args.min_trades, args.max_trades,
        args.num_procs, args.progress_step, args.normalize, args.use_regime
    )

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_file = out_dir / f"strategy_results_{args.sim}_k{args.k}_{ts}.csv"
    df_out = pd.DataFrame(results)
    errors = int(df_out["error"].notna().sum()) if "error" in df_out.columns else 0
    df_out.to_csv(out_file, index=False)
    print(f"[INFO] Wrote results: {out_file} (rows={len(df_out)}, errors={errors})")
    print("[INFO] Done.")

if __name__ == "__main__":
    main()






