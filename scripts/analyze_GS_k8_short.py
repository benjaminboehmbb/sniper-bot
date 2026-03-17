#!/usr/bin/env python3
# scripts/analyze_GS_k8_short.py
#
# GS analyzer for K8 SHORT using engine.simtraderGS.evaluate_strategy(price_df, comb, direction)
# - Offsets/rows via slicing price_df
# - Fee external: roi_fee = roi - fee * trades
# - Robustness stats across offsets: roi_fee_mean, roi_fee_p25
# - ASCII-only prints
#
# SMOKE:
#   python3 scripts/analyze_GS_k8_short.py --strategies_csv <path> --limit 50
# FULL:
#   python3 scripts/analyze_GS_k8_short.py --strategies_csv <path>

import argparse
import os
import sys
from datetime import datetime
import numpy as np
import pandas as pd
import importlib

OFFSETS_DEFAULT = "0,500000,1000000,1500000"


def parse_args():
    ap = argparse.ArgumentParser(description="Analyze GS K8 SHORT candidates (slice offsets/rows; evaluate_strategy signature).")
    ap.add_argument(
        "--csv",
        default="data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv",
        help="Price CSV (GS)",
    )
    ap.add_argument(
        "--strategies_csv",
        required=True,
        help="Strategies CSV (K8 SHORT candidates)",
    )
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offsets", default=OFFSETS_DEFAULT)
    ap.add_argument("--direction", choices=["long", "short"], default="short")
    ap.add_argument("--fee", type=float, default=0.0004, help="Roundtrip fee per trade (external)")
    ap.add_argument("--limit", type=int, default=0, help="If >0: SMOKE limit rows")
    ap.add_argument("--out_dir", default="results/GS/k8_short")
    ap.add_argument("--progress_step", type=int, default=25)
    return ap.parse_args()


def ensure_project_root_on_path():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return project_root


def safe_eval_dict(s: str) -> dict:
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict literal")
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out


def canonical_signals_key(d: dict) -> str:
    return "+".join(sorted(d.keys()))


def load_price_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if "close" not in df.columns:
        raise RuntimeError("Price CSV missing required column: close")
    return df


def load_strategies(path: str, limit: int) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if "combination" not in df.columns:
        raise RuntimeError("Strategies CSV missing required column: combination")
    if limit and limit > 0:
        df = df.head(limit).copy()
    return df


def compute_fee_adjusted(roi: float, trades: int, fee: float) -> float:
    return float(roi) - float(fee) * float(trades)


def normalize_engine_output(out):
    if isinstance(out, dict):
        roi = out.get("roi", out.get("ROI", np.nan))
        trades = out.get("num_trades", out.get("trades", out.get("n_trades", 0)))
        return float(roi), int(trades)
    if isinstance(out, (tuple, list)) and len(out) >= 2:
        return float(out[0]), int(out[1])
    raise RuntimeError("Engine output unsupported (expected dict or (roi,trades)).")


def q25(x):
    x = np.asarray(x, dtype=float)
    if x.size == 0:
        return np.nan
    return float(np.quantile(x, 0.25))


def main():
    args = parse_args()
    project_root = ensure_project_root_on_path()

    offsets = [int(o.strip()) for o in str(args.offsets).split(",") if o.strip()]
    if not offsets:
        raise RuntimeError("No offsets provided")

    price_df = load_price_csv(args.csv)
    strat_df = load_strategies(args.strategies_csv, args.limit)

    mode = "SMOKE" if args.limit and args.limit > 0 else "FULL"
    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(args.out_dir, f"strategy_results_GS_k8_short_{mode}_{ts}.csv")

    max_end = max(offsets) + int(args.rows)
    if max_end > len(price_df):
        raise RuntimeError(f"Requested window exceeds price_df length: need_end={max_end}, len={len(price_df)}")

    mod = importlib.import_module("engine.simtraderGS")
    if not hasattr(mod, "evaluate_strategy"):
        raise RuntimeError("engine.simtraderGS has no evaluate_strategy function")
    eval_fn = getattr(mod, "evaluate_strategy")

    n_total = len(strat_df)

    print("[info] PROJECT_ROOT:", project_root)
    print("[info] CSV:", args.csv)
    print("[info] STRATEGIES:", args.strategies_csv)
    print("[info] MODE:", mode, "rows:", args.rows, "offsets:", ",".join(str(x) for x in offsets), "fee:", args.fee)
    print("[info] DIRECTION:", args.direction)
    print("[info] ENGINE: engine.simtraderGS.evaluate_strategy(price_df, comb, direction)")
    print("[info] N:", n_total)

    results = []

    for i, row in enumerate(strat_df.itertuples(index=False), start=1):
        comb_str = str(getattr(row, "combination"))
        try:
            comb = safe_eval_dict(comb_str)
        except Exception:
            continue

        rec = {
            "combination": comb_str,
            "signals_key": canonical_signals_key(comb),
        }

        roi_list = []
        roi_fee_list = []
        trades_list = []

        for off in offsets:
            w = price_df.iloc[off:off + int(args.rows)].copy()

            out = eval_fn(w, comb, args.direction)
            roi, trades = normalize_engine_output(out)
            roi_fee = compute_fee_adjusted(roi, trades, args.fee)

            rec[f"roi_off_{off}"] = roi
            rec[f"trades_off_{off}"] = trades
            rec[f"roi_fee_off_{off}"] = roi_fee

            roi_list.append(roi)
            roi_fee_list.append(roi_fee)
            trades_list.append(trades)

        rec["roi_mean"] = float(np.mean(roi_list)) if roi_list else np.nan
        rec["roi_fee_mean"] = float(np.mean(roi_fee_list)) if roi_fee_list else np.nan
        rec["roi_fee_p25"] = q25(roi_fee_list)
        rec["trades_sum"] = int(np.sum(trades_list)) if trades_list else 0

        results.append(rec)

        if args.progress_step > 0 and (i % args.progress_step == 0 or i == n_total):
            pct = 100.0 * i / max(n_total, 1)
            print("[progress] %.2f%% (%d/%d)" % (pct, i, n_total))

    out_df = pd.DataFrame(results)

    core = ["combination", "signals_key", "trades_sum", "roi_mean", "roi_fee_mean", "roi_fee_p25"]
    per_off = []
    for off in offsets:
        per_off.extend([f"roi_off_{off}", f"trades_off_{off}", f"roi_fee_off_{off}"])
    cols = [c for c in core + per_off if c in out_df.columns] + [c for c in out_df.columns if c not in (core + per_off)]
    out_df = out_df[cols]

    out_df.to_csv(out_path, index=False)

    print("[ok] Wrote analyze results:", out_path)
    print("[ok] Rows:", len(out_df))


if __name__ == "__main__":
    main()
