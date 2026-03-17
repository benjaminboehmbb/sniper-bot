#!/usr/bin/env python3
# scripts/select_GS_k12_long_TOP250_CANONICAL.py
#
# Purpose:
#   Create a GS-contract-compliant LONG FINAL (K12) by canonicalizing
#   combinations and re-selecting TOP-250 from K12 LONG FULL results.
#
# Contract enforced:
#   - comb contains ONLY short keys (rsi, macd, ...)
#   - no *_signal keys allowed in comb
#   - exactly 12 unique signals (the full GS set)
#   - all weights == 1.0
#   - deterministic output
#
# Robustness metric:
#   - roi_fee_p25 is computed deterministically from roi_fee_off_{offset} columns
#
# Output:
#   strategies/GS/LONG_FINAL_CANONICAL/
#     strategies_GS_k12_long_TOP250_FINAL_CANONICAL_<ts>.csv
#
# FINALs are NOT overwritten.

import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd


# -----------------------------
# CONFIG (explicit & fixed)
# -----------------------------
INPUT_FULL = (
    "results/GS/k12_long/"
    "strategy_results_GS_k12_long_FULL_2026-01-09_15-46-13.csv"
)

OUT_DIR = "strategies/GS/LONG_FINAL_CANONICAL"
TOP_N = 250

OFFSETS = [0, 500000, 1000000, 1500000]

# Canonical short keys (GS contract)
SHORT_KEYS = {
    "rsi", "macd", "bollinger",
    "ma200", "stoch", "atr", "ema50",
    "adx", "cci", "mfi", "obv", "roc",
}

# Map *_signal -> short key
SIGNAL_TO_SHORT = {
    "rsi_signal": "rsi",
    "macd_signal": "macd",
    "bollinger_signal": "bollinger",
    "ma200_signal": "ma200",
    "stoch_signal": "stoch",
    "atr_signal": "atr",
    "ema50_signal": "ema50",
    "adx_signal": "adx",
    "cci_signal": "cci",
    "mfi_signal": "mfi",
    "obv_signal": "obv",
    "roc_signal": "roc",
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


def canonicalize_combination(d: dict) -> dict:
    """
    Enforce GS contract:
    - allow short keys and *_signal keys as inputs,
      but canonical output is ONLY short keys
    - map *_signal -> short key
    - forbid duplicates after mapping (alias + *_signal -> reject)
    - enforce weight == 1.0
    - enforce exactly 12 unique signals == full GS set
    """
    out = {}

    for k, v in d.items():
        if k in SIGNAL_TO_SHORT:
            sk = SIGNAL_TO_SHORT[k]
        elif k in SHORT_KEYS:
            sk = k
        else:
            # unknown key -> reject
            return None

        # weight must be 1.0
        if abs(float(v) - 1.0) > 1e-12:
            return None

        if sk in out:
            # duplicate after canonicalization -> reject
            # (prevents alias + *_signal double-counting)
            return None

        out[sk] = 1.0

    # must be exactly K12
    if len(out) != 12:
        return None

    # must contain all canonical signals
    if set(out.keys()) != SHORT_KEYS:
        return None

    return out


def canonical_dict_str(d: dict) -> str:
    # deterministic formatting
    keys = sorted(d.keys())
    return "{" + ", ".join(f"'{k}': 1.0" for k in keys) + "}"


def compute_roi_fee_p25(row) -> float:
    vals = []
    for off in OFFSETS:
        col = f"roi_fee_off_{off}"
        vals.append(float(row[col]))
    return float(np.quantile(vals, 0.25))


def validate_input_columns(df: pd.DataFrame):
    required = {"combination", "roi_fee_mean"}
    for off in OFFSETS:
        required.add(f"roi_fee_off_{off}")

    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"[fatal] Missing required columns: {missing}")


# -----------------------------
# Main
# -----------------------------
def main():
    if not os.path.exists(INPUT_FULL):
        raise SystemExit(f"[fatal] Missing input file: {INPUT_FULL}")

    os.makedirs(OUT_DIR, exist_ok=True)

    df = pd.read_csv(INPUT_FULL)
    validate_input_columns(df)

    canonical_rows = []
    rejected = 0

    for _, row in df.iterrows():
        try:
            comb_raw = safe_eval_dict(row["combination"])
        except Exception:
            rejected += 1
            continue

        comb_can = canonicalize_combination(comb_raw)
        if comb_can is None:
            rejected += 1
            continue

        try:
            p25 = compute_roi_fee_p25(row)
            mean = float(row["roi_fee_mean"])
        except Exception:
            rejected += 1
            continue

        canonical_rows.append(
            {
                "combination": canonical_dict_str(comb_can),
                "signals_key": "+".join(sorted(comb_can.keys())),
                "roi_fee_p25": p25,
                "roi_fee_mean": mean,
            }
        )

    if not canonical_rows:
        raise SystemExit("[fatal] No valid canonical K12 strategies found")

    df_can = pd.DataFrame(canonical_rows)

    # Deterministic ranking
    df_can = df_can.sort_values(
        by=["roi_fee_p25", "roi_fee_mean"],
        ascending=[False, False],
        kind="mergesort",
    )

    # Drop duplicates on the canonical combination string (safety)
    df_can = df_can.drop_duplicates(subset=["combination"], keep="first").reset_index(drop=True)

    df_top = df_can.head(TOP_N).copy()

    if len(df_top) < TOP_N:
        raise SystemExit(
            f"[fatal] Only {len(df_top)} canonical strategies found, expected {TOP_N}. "
            "This indicates the FULL file does not contain enough clean K12=12/12 combinations "
            "after strict canonicalization."
        )

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(
        OUT_DIR,
        f"strategies_GS_k12_long_TOP250_FINAL_CANONICAL_{ts}.csv",
    )

    df_top.to_csv(out_path, index=False)

    print("[ok] INPUT FULL:", INPUT_FULL)
    print("[ok] Rejected (non-canonical):", rejected)
    print("[ok] Canonical candidates (deduped):", len(df_can))
    print("[ok] Wrote:", out_path)


if __name__ == "__main__":
    main()

