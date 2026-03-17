#!/usr/bin/env python3
# scripts/analyze_GS_k12_long_CANONICAL.py
#
# Purpose:
#   Analyze GS-conform K12 LONG candidates (short keys only, unweighted)
#   and write a clean K12 LONG FULL with per-offset metrics.
#
# Contract enforced:
#   - comb contains ONLY short keys
#   - exactly 12 unique signals
#   - all weights == 1.0
#   - deterministic evaluation via simtraderGS.evaluate_strategy
#
# Output:
#   results/GS/k12_long/
#     strategy_results_GS_k12_long_FULL_CANONICAL_<ts>.csv

import os
import sys
from datetime import datetime
import numpy as np
import pandas as pd

# ------------------------------------------------------------------
# Ensure repo root is on PYTHONPATH (so `engine` is importable)
# ------------------------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from engine.simtraderGS import evaluate_strategy  # noqa: E402

# -----------------------------
# CONFIG
# -----------------------------
PRICE_CSV = (
    "data/btcusdt_1m_2026-01-07/simtraderGS/"
    "btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"
)

INPUT_CANDIDATES = (
    "strategies/GS/k12_long/"
    "strategies_GS_k12_long_from_k11_top250_unweighted_2026-01-09_15-39-10.csv"
)

OUT_DIR = "results/GS/k12_long"
OFFSETS = [0, 500000, 1000000, 1500000]
ROWS = 200_000
FEE = 0.0004

SHORT_KEYS = {
    "rsi", "macd", "bollinger",
    "ma200", "stoch", "atr", "ema50",
    "adx", "cci", "mfi", "obv", "roc",
}

# -----------------------------
# Helpers
# -----------------------------
def safe_eval_dict(s: str) -> dict:
    d = eval(s, {"__builtins__": {}}, {})
    if not isinstance(d, dict):
        raise ValueError("combination is not a dict")
    out = {}
    for k, v in d.items():
        out[str(k)] = float(v)
    return out


def validate_combination(d: dict) -> dict | None:
    # must be exactly the 12 GS short keys
    if set(d.keys()) != SHORT_KEYS:
        return None
    # all weights must be 1.0
    for v in d.values():
        if abs(float(v) - 1.0) > 1e-12:
            return None
    return d


def compute_p25(vals):
    return float(np.quantile(vals, 0.25))


# -----------------------------
# Main
# -----------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    price_df = pd.read_csv(PRICE_CSV)
    cand_df = pd.read_csv(INPUT_CANDIDATES)

    if "combination" not in cand_df.columns:
        raise SystemExit("[fatal] candidates CSV missing 'combination'")

    rows_out = []

    for _, row in cand_df.iterrows():
        try:
            comb_raw = safe_eval_dict(row["combination"])
        except Exception:
            continue

        comb = validate_combination(comb_raw)
        if comb is None:
            continue

        res = {
            "combination": row["combination"],
            "signals_key": "+".join(sorted(comb.keys())),
            "trades_sum": 0,
            "roi_mean": 0.0,
            "roi_fee_mean": 0.0,
        }

        roi_fee_off = []

        for off in OFFSETS:
            r = evaluate_strategy(
                price_df=price_df,
                comb=comb,
                direction="long",
                offset=off,
                rows=ROWS,
                fee=FEE,
            )

            res[f"roi_off_{off}"] = r["roi"]
            res[f"trades_off_{off}"] = r["trades"]
            res[f"roi_fee_off_{off}"] = r["roi_fee"]

            roi_fee_off.append(r["roi_fee"])
            res["trades_sum"] += r["trades"]
            res["roi_mean"] += r["roi"]
            res["roi_fee_mean"] += r["roi_fee"]

        res["roi_mean"] /= len(OFFSETS)
        res["roi_fee_mean"] /= len(OFFSETS)
        res["roi_fee_p25"] = compute_p25(roi_fee_off)

        rows_out.append(res)

    if not rows_out:
        raise SystemExit("[fatal] no valid K12 canonical strategies evaluated")

    out_df = pd.DataFrame(rows_out)

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(
        OUT_DIR,
        f"strategy_results_GS_k12_long_FULL_CANONICAL_{ts}.csv"
    )

    out_df.to_csv(out_path, index=False)

    print("[ok] evaluated:", len(out_df))
    print("[ok] wrote:", out_path)


if __name__ == "__main__":
    main()

