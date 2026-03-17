#!/usr/bin/env python3
# scripts/build_GS_k12_short_RESULTS_CANONICAL.py
#
# Build GS-contract-compliant SHORT canonical RESULTS for K12 (structural endpoint).
# Under the contract (12 signals, unweighted, short keys), there is exactly ONE
# canonical K12 strategy. We evaluate it across the fixed offsets/rows and
# compute fee externally:
#   roi_fee = roi - FEE * num_trades
#
# We write (N=1):
#   results/GS/k12_short/strategy_results_GS_k12_short_FULL_CANONICAL_<ts>.csv
#
# This script is READ-ONLY with respect to FINAL artifacts (does not touch strategies/GS/SHORT_FINAL).
# ASCII-only logs.

import os
import sys
from datetime import datetime
import numpy as np
import pandas as pd

# Ensure repo root is on PYTHONPATH so `engine` is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.simtraderGS import evaluate_strategy  # noqa: E402

# -----------------------------
# FIXED GS INPUTS
# -----------------------------
PRICE_CSV = (
    "data/btcusdt_1m_2026-01-07/simtraderGS/"
    "btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"
)

ROWS = 200_000
OFFSETS = [0, 500000, 1000000, 1500000]
FEE = 0.0004
DIRECTION = "short"

OUT_RESULTS_DIR = "results/GS/k12_short"

SHORT_KEYS = [
    "adx", "atr", "bollinger", "cci", "ema50", "ma200",
    "macd", "mfi", "obv", "roc", "rsi", "stoch"
]

# The only canonical K12 under the contract
CANON_COMB = {k: 1.0 for k in SHORT_KEYS}


def canonical_dict_str(d: dict) -> str:
    keys = sorted(d.keys())
    return "{" + ", ".join(f"'{k}': 1.0" for k in keys) + "}"


def compute_p25(vals):
    return float(np.quantile(vals, 0.25))


def slice_window(df: pd.DataFrame, offset: int, rows: int) -> pd.DataFrame:
    w = df.iloc[offset: offset + rows].copy()
    if len(w) != rows:
        raise ValueError(f"window size mismatch at offset={offset}: got {len(w)} expected {rows}")
    return w


def main():
    if not os.path.exists(PRICE_CSV):
        raise SystemExit(f"[fatal] missing PRICE_CSV: {PRICE_CSV}")

    os.makedirs(OUT_RESULTS_DIR, exist_ok=True)

    price_df = pd.read_csv(PRICE_CSV)

    res = {
        "combination": canonical_dict_str(CANON_COMB),
        "signals_key": "+".join(sorted(CANON_COMB.keys())),
        "num_trades_sum": 0,
        "roi_mean": 0.0,
        "roi_fee_mean": 0.0,
    }

    roi_fee_off = []

    for off in OFFSETS:
        window_df = slice_window(price_df, off, ROWS)

        r = evaluate_strategy(
            price_df=window_df,
            comb=CANON_COMB,
            direction=DIRECTION,
        )

        if "roi" not in r or "num_trades" not in r:
            raise SystemExit(f"[fatal] evaluate_strategy missing keys at offset={off}: got keys={list(r.keys())}")

        roi = float(r["roi"])
        num_trades = int(r["num_trades"])
        roi_fee = roi - (FEE * num_trades)

        res[f"roi_off_{off}"] = roi
        res[f"num_trades_off_{off}"] = num_trades
        res[f"roi_fee_off_{off}"] = roi_fee

        # keep additional GS outputs if present
        for extra_key in ["winrate", "sharpe", "pnl_sum", "avg_trade"]:
            if extra_key in r:
                res[f"{extra_key}_off_{off}"] = float(r[extra_key])

        roi_fee_off.append(roi_fee)
        res["num_trades_sum"] += num_trades
        res["roi_mean"] += roi
        res["roi_fee_mean"] += roi_fee

    res["roi_mean"] /= float(len(OFFSETS))
    res["roi_fee_mean"] /= float(len(OFFSETS))
    res["roi_fee_p25"] = compute_p25(roi_fee_off)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_results = os.path.join(
        OUT_RESULTS_DIR,
        f"strategy_results_GS_k12_short_FULL_CANONICAL_{ts}.csv"
    )
    pd.DataFrame([res]).to_csv(out_results, index=False)

    print("[ok] wrote results:", out_results)
    print("[ok] rows:", 1)


if __name__ == "__main__":
    main()
