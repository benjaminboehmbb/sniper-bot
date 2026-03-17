#!/usr/bin/env python3
# Post-GS H3: Asset-Transfer (BTC vs ETH) — LONG_FINAL_CANONICAL
# FIX: robust engine-import via sys.path (WSL-safe)

import os
import sys
import json
import time
import glob
import ast
from datetime import datetime, timezone

# -----------------------
# FIX: ensure project root in sys.path
# -----------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine import simtraderGS as gs  # noqa: E402

import pandas as pd


# -----------------------
# Paths
# -----------------------
BTC_GS_CSV = (
    "data/btcusdt_1m_2026-01-07/simtraderGS/"
    "btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"
)

ETH_GS_COMPAT_CSV = (
    "data/ethusdt_1m_postGS/simtraderGS/"
    "ethusdt_1m_price_2017_2025_GS_COMPAT_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"
)

STRATEGY_DIR = "strategies/GS/LONG_FINAL_CANONICAL"

OUT_ROOT = "results/POST_GS/H3_asset"
OUT_BTC = os.path.join(OUT_ROOT, "btc_1m")
OUT_ETH = os.path.join(OUT_ROOT, "eth_1m")
OUT_META = os.path.join(OUT_ROOT, "meta")
OUT_LOGS = os.path.join(OUT_ROOT, "logs")


# -----------------------
# Helpers
# -----------------------
def utc_ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")


def ensure_dirs():
    for p in [OUT_ROOT, OUT_BTC, OUT_ETH, OUT_META, OUT_LOGS]:
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


def eval_one(price_csv, comb, direction="long"):
    df = pd.read_csv(price_csv)
    t0 = time.time()
    res = gs.evaluate_strategy(df, comb, direction=direction)
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

    # ---- BTC
    btc_res = eval_one(BTC_GS_CSV, comb, direction="long")
    btc_out = os.path.join(
        OUT_BTC, f"strategy_results_POST_GS_H3_LONG_BTC_1m_{run_id}.csv"
    )
    write_results(btc_res, btc_out)

    # ---- ETH
    eth_res = eval_one(ETH_GS_COMPAT_CSV, comb, direction="long")
    eth_out = os.path.join(
        OUT_ETH, f"strategy_results_POST_GS_H3_LONG_ETH_1m_{run_id}.csv"
    )
    write_results(eth_res, eth_out)

    # ---- Meta
    meta_csv = os.path.join(
        OUT_META, f"meta_compare_POST_GS_H3_LONG_BTC_vs_ETH_{run_id}.csv"
    )

    pd.DataFrame([{
        "run_id": run_id,
        "direction": "long",
        "strategy_file": comb_file,
        "fee_roundtrip": fee_rt,

        "btc_roi": btc_res.get("roi"),
        "btc_winrate": btc_res.get("winrate"),
        "btc_num_trades": btc_res.get("num_trades"),
        "btc_sharpe": btc_res.get("sharpe"),

        "eth_roi": eth_res.get("roi"),
        "eth_winrate": eth_res.get("winrate"),
        "eth_num_trades": eth_res.get("num_trades"),
        "eth_sharpe": eth_res.get("sharpe"),

        "delta_roi_eth_minus_btc":
            None if btc_res.get("roi") is None else eth_res.get("roi") - btc_res.get("roi"),
    }]).to_csv(meta_csv, index=False)

    write_manifest(
        os.path.join(OUT_META, f"run_manifest_POST_GS_H3_{run_id}.json"),
        {
            "run_id": run_id,
            "device": os.environ.get("DEVICE", "AR15"),
            "env": os.environ.get("ENV", "WSL"),
            "fee_roundtrip": fee_rt,
            "inputs": {
                "btc_csv": BTC_GS_CSV,
                "eth_csv": ETH_GS_COMPAT_CSV,
                "strategy_file": comb_file,
            },
            "outputs": {
                "btc": btc_out,
                "eth": eth_out,
                "meta": meta_csv,
            },
        },
    )

    print("[ok] H3 LONG asset-transfer completed")
    print("[out]", OUT_ROOT)


if __name__ == "__main__":
    main()

