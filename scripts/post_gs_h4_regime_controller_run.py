#!/usr/bin/env python3
# Post-GS H4-A: Regime-Controller Wirksamkeit
# Controller: Entry-Gate only via allow_long == 1
#
# Quality Gates added:
# (1) Controller-Wirkung vorhanden? (warn if mean(allow_long) > 0.90)
# (2) Signal-Neutralisierung korrekt? (abort if any gated row has non-zero signals)
#
# Usage:
#   SIMTRADERGS_FEE_ROUNDTRIP=0.0004 python3 scripts/post_gs_h4_regime_controller_run.py

import os
import sys
import json
import time
import glob
import ast
from datetime import datetime, timezone

# -----------------------
# FIX: ensure project root in sys.path (WSL-safe)
# -----------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine import simtraderGS as gs  # noqa: E402
import pandas as pd


# -----------------------
# Paths
# -----------------------
ETH_GS_COMPAT_CSV = (
    "data/ethusdt_1m_postGS/simtraderGS/"
    "ethusdt_1m_price_2017_2025_GS_COMPAT_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"
)

STRATEGY_DIR = "strategies/GS/LONG_FINAL_CANONICAL"

OUT_ROOT = "results/POST_GS/H4_regime"
OUT_ETH = os.path.join(OUT_ROOT, "eth_1m")
OUT_META = os.path.join(OUT_ROOT, "meta")
OUT_LOGS = os.path.join(OUT_ROOT, "logs")


# -----------------------
# Helpers
# -----------------------
def utc_ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def ensure_dirs():
    for p in [OUT_ROOT, OUT_ETH, OUT_META, OUT_LOGS]:
        os.makedirs(p, exist_ok=True)


def load_single_canonical_comb():
    files = sorted(glob.glob(os.path.join(STRATEGY_DIR, "*.csv")))
    if len(files) != 1:
        raise RuntimeError(
            f"Expected exactly 1 canonical CSV in {STRATEGY_DIR}, found {len(files)}"
        )
    df = pd.read_csv(files[0])
    col = [c for c in ["combination", "Combination", "strategy", "Strategy"] if c in df.columns]
    if not col:
        raise RuntimeError("No combination column found in canonical strategy CSV")
    comb = ast.literal_eval(str(df.iloc[0][col[0]]))
    return comb, os.path.basename(files[0])


def preflight_df(df: pd.DataFrame):
    req_cols = [
        "timestamp_utc", "open", "high", "low", "close", "volume",
        "allow_long"
    ]
    sig_cols = [c for c in df.columns if c.endswith("_signal")]

    missing = [c for c in req_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}")

    if not sig_cols:
        raise RuntimeError("No *_signal columns found")

    # time sanity
    ts = pd.to_datetime(df["timestamp_utc"], utc=True, errors="raise")
    if not ts.is_monotonic_increasing or ts.duplicated().any():
        raise RuntimeError("timestamp_utc not strictly monotonic or has duplicates")

    # (1) Controller-Wirkung vorhanden?
    allow_mean = float(df["allow_long"].mean())
    if allow_mean > 0.90:
        print(f"[warn] allow_long mean is high ({allow_mean:.3f}) — controller effect may be weak")

    return sig_cols, allow_mean


def apply_entry_gate(df: pd.DataFrame, sig_cols):
    """
    Entry-Gate only:
    - Where allow_long != 1, neutralize all signal contributions.
    - Exits remain unchanged (GS exit logic untouched).
    """
    gated = df.copy()
    mask_block = gated["allow_long"] != 1
    if mask_block.any():
        gated.loc[mask_block, sig_cols] = 0.0
    return gated, mask_block


def verify_signal_neutralization(gated_df: pd.DataFrame, sig_cols, mask_block):
    """
    (2) Hard gate: For all blocked rows, sum of signals must be exactly zero.
    Abort if violated.
    """
    if mask_block.any():
        sums = gated_df.loc[mask_block, sig_cols].sum(axis=1)
        bad = (sums != 0).sum()
        if bad > 0:
            raise RuntimeError(
                f"Signal-neutralization failed: {bad} blocked rows have non-zero signal sum"
            )


def eval_one(df: pd.DataFrame, comb):
    t0 = time.time()
    res = gs.evaluate_strategy(df, comb, direction="long")
    res["_elapsed_s"] = round(time.time() - t0, 2)
    return res


def write_results(res_dict, out_csv):
    row = {k: v for k, v in res_dict.items() if not isinstance(v, (list, dict))}
    pd.DataFrame([row]).to_csv(out_csv, index=False)


def write_manifest(path, payload):
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


# -----------------------
# Main
# -----------------------
def main():
    ensure_dirs()
    run_id = utc_ts()
    fee_rt = float(os.environ.get("SIMTRADERGS_FEE_ROUNDTRIP", "0.0"))

    comb, comb_file = load_single_canonical_comb()

    # Load ETH GS-COMPAT
    df_eth = pd.read_csv(ETH_GS_COMPAT_CSV)

    # Preflight
    sig_cols, allow_mean = preflight_df(df_eth)

    # Apply Entry-Gate
    df_eth_gated, mask_block = apply_entry_gate(df_eth, sig_cols)

    # Verify neutralization (hard gate)
    verify_signal_neutralization(df_eth_gated, sig_cols, mask_block)

    # Evaluate
    res = eval_one(df_eth_gated, comb)

    out_csv = os.path.join(
        OUT_ETH, f"strategy_results_POST_GS_H4_LONG_ETH_ENTRYGATE_{run_id}.csv"
    )
    write_results(res, out_csv)

    # Meta
    meta_csv = os.path.join(
        OUT_META, f"meta_POST_GS_H4_LONG_ETH_ENTRYGATE_{run_id}.csv"
    )
    pd.DataFrame([{
        "run_id": run_id,
        "direction": "long",
        "strategy_file": comb_file,
        "controller": "entry_gate_allow_long_eq_1",
        "fee_roundtrip": fee_rt,
        "allow_long_mean": allow_mean,
        "roi": res.get("roi"),
        "winrate": res.get("winrate"),
        "num_trades": res.get("num_trades"),
        "sharpe": res.get("sharpe"),
        "avg_trade": res.get("avg_trade"),
        "pnl_sum": res.get("pnl_sum"),
        "elapsed_s": res.get("_elapsed_s"),
    }]).to_csv(meta_csv, index=False)

    # Manifest
    write_manifest(
        os.path.join(OUT_META, f"run_manifest_POST_GS_H4_{run_id}.json"),
        {
            "run_id": run_id,
            "device": os.environ.get("DEVICE", "AR15"),
            "env": os.environ.get("ENV", "WSL"),
            "fee_roundtrip": fee_rt,
            "controller": "entry_gate_allow_long_eq_1",
            "inputs": {
                "eth_csv": ETH_GS_COMPAT_CSV,
                "strategy_file": comb_file,
            },
            "outputs": {
                "eth": out_csv,
                "meta": meta_csv,
            },
        },
    )

    print("[ok] H4-A completed (Entry-Gate only)")
    print("[out]", OUT_ROOT)


if __name__ == "__main__":
    main()
