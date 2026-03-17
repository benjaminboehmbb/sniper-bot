#!/usr/bin/env python3
# Post-GS H5: Execution-Realität (Fees + Entry-Slippage)
#
# Compare ETH LONG_FINAL_CANONICAL:
#  - Controller OFF vs ON (Entry-Gate allow_long==1)
#  - Cost grid S0/S1/S2
#
# Quality Gates:
#  (1) Slippage wirkt (Entry-Preis verändert) -> hard assert
#  (2) Signal-Neutralisierung korrekt (Controller ON) -> hard assert
#  (3) Trade-Reduktion ON < OFF -> warn
#
# Usage:
#   python3 scripts/post_gs_h5_execution_realism_run.py
#   (Fee is set per scenario via env before each eval)

import os
import sys
import json
import time
import glob
import ast
from datetime import datetime, timezone

# --- sys.path FIX (WSL-safe)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine import simtraderGS as gs  # noqa: E402
import pandas as pd
import numpy as np

# -----------------------
# Paths
# -----------------------
ETH_GS_COMPAT_CSV = (
    "data/ethusdt_1m_postGS/simtraderGS/"
    "ethusdt_1m_price_2017_2025_GS_COMPAT_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"
)
STRATEGY_DIR = "strategies/GS/LONG_FINAL_CANONICAL"

OUT_ROOT = "results/POST_GS/H5_execution"
OUT_ETH = os.path.join(OUT_ROOT, "eth_1m")
OUT_META = os.path.join(OUT_ROOT, "meta")
OUT_LOGS = os.path.join(OUT_ROOT, "logs")

# -----------------------
# Cost Grid
# -----------------------
COST_GRID = [
    {"name": "S0", "fee_rt": 0.0004, "slip_entry": 0.0000},
    {"name": "S1", "fee_rt": 0.0008, "slip_entry": 0.0002},
    {"name": "S2", "fee_rt": 0.0012, "slip_entry": 0.0005},
]

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
        raise RuntimeError(f"Expected exactly 1 canonical CSV in {STRATEGY_DIR}, found {len(files)}")
    df = pd.read_csv(files[0])
    col = [c for c in ["combination","Combination","strategy","Strategy"] if c in df.columns]
    if not col:
        raise RuntimeError("No combination column found in canonical CSV")
    comb = ast.literal_eval(str(df.iloc[0][col[0]]))
    return comb, os.path.basename(files[0])

def preflight_df(df):
    req = ["timestamp_utc","open","high","low","close","volume","allow_long"]
    sig_cols = [c for c in df.columns if c.endswith("_signal")]
    miss = [c for c in req if c not in df.columns]
    if miss:
        raise RuntimeError(f"Missing columns: {miss}")
    if not sig_cols:
        raise RuntimeError("No *_signal columns")
    ts = pd.to_datetime(df["timestamp_utc"], utc=True, errors="raise")
    if not ts.is_monotonic_increasing or ts.duplicated().any():
        raise RuntimeError("timestamp_utc invalid")
    return sig_cols

def apply_controller(df, sig_cols, enabled: bool):
    if not enabled:
        return df.copy(), np.zeros(len(df), dtype=bool)
    gated = df.copy()
    mask_block = gated["allow_long"] != 1
    if mask_block.any():
        gated.loc[mask_block, sig_cols] = 0.0
    return gated, mask_block

def verify_neutralization(df, sig_cols, mask_block):
    if mask_block.any():
        sums = df.loc[mask_block, sig_cols].sum(axis=1)
        bad = (sums != 0).sum()
        if bad:
            raise RuntimeError(f"Signal-neutralization failed on {bad} rows")

def apply_entry_slippage(df, slip_entry):
    """
    Entry-side slippage approximation:
    - Inflate 'open' price by (1+slip_entry) uniformly.
    - This biases entries conservatively without touching exits.
    """
    if slip_entry <= 0:
        return df.copy(), 0.0
    out = df.copy()
    before = out["open"].copy()
    out["open"] = out["open"] * (1.0 + slip_entry)
    # Gate: ensure slippage had an effect
    delta = (out["open"] - before).abs().sum()
    if delta <= 0:
        raise RuntimeError("Slippage had no effect on open prices")
    return out, float(delta)

def eval_once(df, comb):
    t0 = time.time()
    res = gs.evaluate_strategy(df, comb, direction="long")
    res["_elapsed_s"] = round(time.time() - t0, 2)
    return res

def write_row(path, row):
    pd.DataFrame([row]).to_csv(path, index=False)

# -----------------------
# Main
# -----------------------
def main():
    ensure_dirs()
    run_id = utc_ts()

    comb, comb_file = load_single_canonical_comb()
    df_base = pd.read_csv(ETH_GS_COMPAT_CSV)
    sig_cols = preflight_df(df_base)

    rows_meta = []

    for sc in COST_GRID:
        # set fee for GS (per scenario)
        os.environ["SIMTRADERGS_FEE_ROUNDTRIP"] = str(sc["fee_rt"])

        # --- Controller OFF
        df_off_ctrl, mask_off = apply_controller(df_base, sig_cols, enabled=False)
        df_off_slip, delta_off = apply_entry_slippage(df_off_ctrl, sc["slip_entry"])
        res_off = eval_once(df_off_slip, comb)

        # --- Controller ON
        df_on_ctrl, mask_on = apply_controller(df_base, sig_cols, enabled=True)
        verify_neutralization(df_on_ctrl, sig_cols, mask_on)
        df_on_slip, delta_on = apply_entry_slippage(df_on_ctrl, sc["slip_entry"])
        res_on = eval_once(df_on_slip, comb)

        # Warn if trades not reduced
        if (res_on.get("num_trades") is not None and res_off.get("num_trades") is not None
            and res_on["num_trades"] >= res_off["num_trades"]):
            print(f"[warn] Trades not reduced for {sc['name']} (ON>=OFF)")

        # Write per-scenario result CSVs
        out_off = os.path.join(
            OUT_ETH, f"strategy_results_POST_GS_H5_LONG_ETH_{sc['name']}_CTRL_OFF_{run_id}.csv"
        )
        out_on = os.path.join(
            OUT_ETH, f"strategy_results_POST_GS_H5_LONG_ETH_{sc['name']}_CTRL_ON_{run_id}.csv"
        )
        write_row(out_off, {**res_off, "scenario": sc["name"], "controller": "OFF"})
        write_row(out_on,  {**res_on,  "scenario": sc["name"], "controller": "ON"})

        rows_meta.append({
            "run_id": run_id,
            "scenario": sc["name"],
            "fee_roundtrip": sc["fee_rt"],
            "slip_entry": sc["slip_entry"],
            "strategy_file": comb_file,

            "off_roi": res_off.get("roi"),
            "off_sharpe": res_off.get("sharpe"),
            "off_winrate": res_off.get("winrate"),
            "off_num_trades": res_off.get("num_trades"),

            "on_roi": res_on.get("roi"),
            "on_sharpe": res_on.get("sharpe"),
            "on_winrate": res_on.get("winrate"),
            "on_num_trades": res_on.get("num_trades"),

            "delta_roi_on_minus_off":
                (None if res_on.get("roi") is None or res_off.get("roi") is None
                 else res_on["roi"] - res_off["roi"]),
            "delta_sharpe_on_minus_off":
                (None if res_on.get("sharpe") is None or res_off.get("sharpe") is None
                 else res_on["sharpe"] - res_off["sharpe"]),

            "slip_effect_sum_off": delta_off,
            "slip_effect_sum_on":  delta_on,
        })

    meta_csv = os.path.join(
        OUT_META, f"meta_compare_POST_GS_H5_LONG_ETH_CTRL_ON_vs_OFF_{run_id}.csv"
    )
    pd.DataFrame(rows_meta).to_csv(meta_csv, index=False)

    # Manifest
    with open(os.path.join(OUT_META, f"run_manifest_POST_GS_H5_{run_id}.json"), "w") as f:
        json.dump({
            "run_id": run_id,
            "grid": COST_GRID,
            "controller": "entry_gate_allow_long_eq_1",
            "inputs": {
                "eth_csv": ETH_GS_COMPAT_CSV,
                "strategy_file": comb_file,
            },
            "outputs": {
                "eth_dir": OUT_ETH,
                "meta_csv": meta_csv,
            },
            "device": os.environ.get("DEVICE", "AR15"),
            "env": os.environ.get("ENV", "WSL"),
        }, f, indent=2)

    print("[ok] H5 completed (Execution-Realität)")
    print("[out]", OUT_ROOT)

if __name__ == "__main__":
    main()
