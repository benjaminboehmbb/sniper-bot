#!/usr/bin/env python3
# scripts/select_GS_k7_long_top250_for_k8_seeds.py
#
# GS-compatible selector for K7 LONG results that contain:
# - combination (JSON: {"rsi":1.0,"macd":1.0,...})
# - roi_fee_mean
# - roi_fee_off_* columns
# - trades_sum
#
# We derive signals_key from combination keys (sorted, comma-joined).
# Gate on roi_fee_p25 (robustness), rank by roi_fee_mean then p25 then trades_sum.
# Output: strategies/GS/k8_long/... seeds with signals_key.

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import List

import pandas as pd


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def derive_signals_key(combination_json: str) -> str:
    d = json.loads(combination_json)
    keys = sorted(list(d.keys()))
    return ",".join(keys)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k7_full_csv", required=True)
    ap.add_argument("--top_n", type=int, default=250)
    ap.add_argument("--require_p25_ge", type=float, default=-0.6)
    ap.add_argument("--out_dir", default="strategies/GS/k8_long")
    args = ap.parse_args()

    df = pd.read_csv(args.k7_full_csv)

    for c in ["roi_fee_mean", "trades_sum", "combination"]:
        if c not in df.columns:
            raise RuntimeError(f"Missing column '{c}' in K7 results CSV.")

    roi_cols: List[str] = [c for c in df.columns if c.startswith("roi_fee_off_")]
    if not roi_cols:
        raise RuntimeError("No roi_fee_off_* columns found in K7 results CSV.")

    # Derive robustness metrics
    df["roi_fee_p25"] = df[roi_cols].quantile(0.25, axis=1)
    df["roi_fee_min"] = df[roi_cols].min(axis=1)

    # Derive signals_key
    df["signals_key"] = df["combination"].apply(derive_signals_key)

    # Gate
    gated = df[df["roi_fee_p25"] >= float(args.require_p25_ge)].copy()
    if gated.empty:
        raise RuntimeError("No rows left after roi_fee_p25 gate. Lower --require_p25_ge.")

    # Rank
    gated = gated.sort_values(
        by=["roi_fee_mean", "roi_fee_p25", "roi_fee_min", "trades_sum"],
        ascending=[False, False, False, False],
    )

    seeds = gated.head(int(args.top_n)).copy()

    os.makedirs(args.out_dir, exist_ok=True)
    out_path = os.path.join(
        args.out_dir,
        f"strategies_GS_k8_long_seeds_top{len(seeds)}_minRoiP25{args.require_p25_ge}_{ts()}.csv",
    )

    out = pd.DataFrame(
        {
            "k": 8,
            "direction": "long",
            "source": "k8_long_seeds_from_k7_long_top",
            "roi_fee_mean": seeds["roi_fee_mean"].astype(float),
            "roi_fee_p25": seeds["roi_fee_p25"].astype(float),
            "roi_fee_min": seeds["roi_fee_min"].astype(float),
            "trades_sum": seeds["trades_sum"].astype(int),
            "signals_key": seeds["signals_key"].astype(str),
            "combination": seeds["combination"].astype(str),
        }
    )
    out.to_csv(out_path, index=False)

    print("OK WROTE:", out_path)
    print("SEEDS:", len(out))
    print("ROI_FEE_MEAN range:", float(out["roi_fee_mean"].min()), float(out["roi_fee_mean"].max()))
    print("ROI_FEE_P25 range :", float(out["roi_fee_p25"].min()), float(out["roi_fee_p25"].max()))
    print("ROI_FEE_MIN range :", float(out["roi_fee_min"].min()), float(out["roi_fee_min"].max()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


