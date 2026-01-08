#!/usr/bin/env python3
# tools/gs_long_short_diagnostics.py
#
# Purpose:
#   Diagnose LONG/SHORT contract of engine/simtraderGS.py against a fully
#   instrumented replica simulator (DIAG) that MUST match the GS contract.
#
# Hard invariant:
#   SANITY (fee=0): DIAG vs BASE match MUST be True (roi + num_trades).
#   Otherwise: hard-fail with actionable debug output.
#
# Notes:
# - ASCII-only.
# - DIAG computes fee-adjusted ROI externally as: roi_fee = roi - fee_roundtrip * num_trades
#   (matches tools/gs_smoke_suite.py).
# - BASE is evaluated with SIMTRADERGS_FEE_ROUNDTRIP forced to 0 to ensure the
#   contract comparison is fee-free and deterministic.
#
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from contextlib import contextmanager
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


# ----------------------------
# Repo root + import engine/*
# ----------------------------
def _repo_root_from_this_file() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, ".."))


REPO_ROOT = _repo_root_from_this_file()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    import engine.simtraderGS as gs  # type: ignore
    gs_evaluate_strategy = gs.evaluate_strategy  # type: ignore
except Exception as e:
    raise SystemExit(f"ERROR: cannot import engine.simtraderGS.evaluate_strategy: {e}")


# Prefer GS constants to guarantee identical mapping.
SIGNALS = list(getattr(gs, "SIGNALS", [
    "rsi_signal", "macd_signal", "bollinger_signal",
    "ma200_signal", "stoch_signal", "atr_signal", "ema50_signal",
    "adx_signal", "cci_signal", "mfi_signal", "obv_signal", "roc_signal",
]))
KEYMAP = dict(getattr(gs, "KEYMAP", {
    "rsi": "rsi_signal",
    "macd": "macd_signal",
    "bollinger": "bollinger_signal",
    "ma200": "ma200_signal",
    "stoch": "stoch_signal",
    "atr": "atr_signal",
    "ema50": "ema50_signal",
    "adx": "adx_signal",
    "cci": "cci_signal",
    "mfi": "mfi_signal",
    "obv": "obv_signal",
    "roc": "roc_signal",
}))


# ----------------------------
# Helpers
# ----------------------------
def _finite_array(a: Any, fill: float = 0.0) -> np.ndarray:
    arr = np.asarray(a, dtype=float)
    return np.nan_to_num(arr, nan=fill, posinf=fill, neginf=fill)


def _normalize_signal(arr: np.ndarray) -> np.ndarray:
    arr = _finite_array(arr, fill=0.0)
    # normalize to -1/0/1 (exactly like simtraderGS)
    return np.where(arr > 0.0, 1.0, np.where(arr < 0.0, -1.0, 0.0)).astype(float)


def _parse_comb(s: str) -> Dict[str, float]:
    """
    Accepts:
      - JSON dict string: {"rsi":1.0,"macd":1.0}
      - Python dict literal: {'rsi': 1.0, 'macd': 1.0}
    """
    s = (s or "").strip()
    if not s:
        return {"rsi": 1.0, "macd": 1.0, "ma200": 1.0}
    try:
        obj = json.loads(s)
    except Exception:
        obj = ast.literal_eval(s)
    if not isinstance(obj, dict):
        raise SystemExit("ERROR: --comb must evaluate to a dict")
    out: Dict[str, float] = {}
    for k, v in obj.items():
        try:
            out[str(k)] = float(v)
        except Exception:
            continue
    return out


def _build_score(df: pd.DataFrame, comb: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
    if "close" not in df.columns:
        raise SystemExit("ERROR: close column missing")

    close = _finite_array(df["close"].to_numpy(dtype=float), fill=0.0)

    sig: Dict[str, np.ndarray] = {}
    for col in SIGNALS:
        if col in df.columns:
            sig[col] = _normalize_signal(df[col].to_numpy(dtype=float))

    score = np.zeros_like(close, dtype=float)
    for k, w in comb.items():
        col = KEYMAP.get(k, k)
        if col in sig:
            score += float(w) * sig[col]

    return _finite_array(score, fill=0.0), close


def _quantiles_str(x: np.ndarray) -> str:
    if x.size == 0:
        return "q05=NA q25=NA q50=NA q75=NA q95=NA"
    qs = np.quantile(x, [0.05, 0.25, 0.50, 0.75, 0.95])
    return (
        f"q05={qs[0]:+.8f} q25={qs[1]:+.8f} q50={qs[2]:+.8f} "
        f"q75={qs[3]:+.8f} q95={qs[4]:+.8f}"
    )


def _almost_equal(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(float(a) - float(b)) <= tol


def _roi_fee(roi: float, num_trades: int, fee_roundtrip: float) -> float:
    if num_trades <= 0:
        return float(roi)
    return float(roi - float(fee_roundtrip) * int(num_trades))


@contextmanager
def _force_env_fee_zero() -> Any:
    key = "SIMTRADERGS_FEE_ROUNDTRIP"
    old = os.environ.get(key)
    os.environ[key] = "0"
    try:
        yield
    finally:
        if old is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old


# ----------------------------
# Exact DIAG replica of simtraderGS contract v1
# (copied from engine/simtraderGS.py semantics, but instrumented)
# ----------------------------
def _simulate_long_diag(
    score: np.ndarray,
    close: np.ndarray,
    tp: float,
    sl: float,
    max_hold: int,
    enter_z: float,
    exit_z: float,
    fee_rt_internal: float,
) -> Dict[str, Any]:
    n = score.shape[0]
    entries = score > enter_z

    i = 0
    returns: List[float] = []
    wins = 0
    num = 0

    exit_counts = {"TP": 0, "SL": 0, "SCORE": 0, "MAXHOLD": 0}
    hold_bars: List[int] = []
    # store a few trades for debugging
    trades_preview: List[Dict[str, Any]] = []

    while i < n:
        if not entries[i]:
            i += 1
            continue

        entry_px = float(close[i])
        j = i + 1
        exited = False
        j_end = min(n, i + max_hold + 1)

        while j < j_end:
            r = (float(close[j]) - entry_px) / entry_px
            if not np.isfinite(r):
                r = 0.0

            if r >= tp:
                r = r - fee_rt_internal
                returns.append(r)
                wins += 1
                num += 1
                exit_counts["TP"] += 1
                hold_bars.append(j - i)
                if len(trades_preview) < 5:
                    trades_preview.append({"i": i, "j": j, "reason": "TP", "r": r})
                i = j + 1
                exited = True
                break

            if r <= -sl:
                r = r - fee_rt_internal
                returns.append(r)
                wins += 1 if r > 0 else 0
                num += 1
                exit_counts["SL"] += 1
                hold_bars.append(j - i)
                if len(trades_preview) < 5:
                    trades_preview.append({"i": i, "j": j, "reason": "SL", "r": r})
                i = j + 1
                exited = True
                break

            if float(score[j]) < exit_z:
                r = r - fee_rt_internal
                returns.append(r)
                wins += 1 if r > 0 else 0
                num += 1
                exit_counts["SCORE"] += 1
                hold_bars.append(j - i)
                if len(trades_preview) < 5:
                    trades_preview.append({"i": i, "j": j, "reason": "SCORE", "r": r})
                i = j + 1
                exited = True
                break

            j += 1

        if not exited:
            j_last = j_end - 1
            r = (float(close[j_last]) - entry_px) / entry_px
            if not np.isfinite(r):
                r = 0.0
            r = r - fee_rt_internal
            returns.append(r)
            wins += 1 if r > 0 else 0
            num += 1
            exit_counts["MAXHOLD"] += 1
            hold_bars.append(j_last - i)
            if len(trades_preview) < 5:
                trades_preview.append({"i": i, "j": j_last, "reason": "MAXHOLD", "r": r})
            i = j_end

    rets = np.asarray(returns, dtype=float) if returns else np.empty(0, dtype=float)
    rets = _finite_array(rets, fill=0.0) if rets.size else rets

    roi = float(np.sum(rets)) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0

    return {
        "roi": roi,
        "num_trades": int(num),
        "winrate": winrate,
        "returns": rets,
        "exit_counts": exit_counts,
        "hold_bars": np.asarray(hold_bars, dtype=int),
        "trades_preview": trades_preview,
    }


def _simulate_short_diag(
    score: np.ndarray,
    close: np.ndarray,
    tp: float,
    sl: float,
    max_hold: int,
    enter_z: float,
    exit_z: float,
    fee_rt_internal: float,
) -> Dict[str, Any]:
    n = score.shape[0]

    # EXACT GS SHORT ENTRY / EXIT:
    # Entry: score < -enter_z
    # Exit:  score > -exit_z
    entries = score < (-enter_z)
    exit_thr = (-exit_z)

    i = 0
    returns: List[float] = []
    wins = 0
    num = 0

    exit_counts = {"TP": 0, "SL": 0, "SCORE": 0, "MAXHOLD": 0}
    hold_bars: List[int] = []
    trades_preview: List[Dict[str, Any]] = []

    while i < n:
        if not entries[i]:
            i += 1
            continue

        entry_px = float(close[i])
        j = i + 1
        exited = False
        j_end = min(n, i + max_hold + 1)

        while j < j_end:
            r = (entry_px - float(close[j])) / entry_px
            if not np.isfinite(r):
                r = 0.0

            if r >= tp:
                r = r - fee_rt_internal
                returns.append(r)
                wins += 1
                num += 1
                exit_counts["TP"] += 1
                hold_bars.append(j - i)
                if len(trades_preview) < 5:
                    trades_preview.append({"i": i, "j": j, "reason": "TP", "r": r})
                i = j + 1
                exited = True
                break

            if r <= -sl:
                r = r - fee_rt_internal
                returns.append(r)
                wins += 1 if r > 0 else 0
                num += 1
                exit_counts["SL"] += 1
                hold_bars.append(j - i)
                if len(trades_preview) < 5:
                    trades_preview.append({"i": i, "j": j, "reason": "SL", "r": r})
                i = j + 1
                exited = True
                break

            if float(score[j]) > exit_thr:
                r = r - fee_rt_internal
                returns.append(r)
                wins += 1 if r > 0 else 0
                num += 1
                exit_counts["SCORE"] += 1
                hold_bars.append(j - i)
                if len(trades_preview) < 5:
                    trades_preview.append({"i": i, "j": j, "reason": "SCORE", "r": r})
                i = j + 1
                exited = True
                break

            j += 1

        if not exited:
            j_last = j_end - 1
            r = (entry_px - float(close[j_last])) / entry_px
            if not np.isfinite(r):
                r = 0.0
            r = r - fee_rt_internal
            returns.append(r)
            wins += 1 if r > 0 else 0
            num += 1
            exit_counts["MAXHOLD"] += 1
            hold_bars.append(j_last - i)
            if len(trades_preview) < 5:
                trades_preview.append({"i": i, "j": j_last, "reason": "MAXHOLD", "r": r})
            i = j_end

    rets = np.asarray(returns, dtype=float) if returns else np.empty(0, dtype=float)
    rets = _finite_array(rets, fill=0.0) if rets.size else rets

    roi = float(np.sum(rets)) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0

    return {
        "roi": roi,
        "num_trades": int(num),
        "winrate": winrate,
        "returns": rets,
        "exit_counts": exit_counts,
        "hold_bars": np.asarray(hold_bars, dtype=int),
        "trades_preview": trades_preview,
    }


def _print_block(direction: str, fee_roundtrip: float, ref: Dict[str, Any]) -> None:
    rets = ref["returns"]
    holds = ref["hold_bars"]
    exits = ref["exit_counts"]
    trades = int(ref["num_trades"])

    print("============================================================")
    print(f"DIRECTION: {direction.upper()}")
    print(f"TRADES: {trades}")
    print("EXIT COUNTS:")
    if trades > 0:
        for k in ("TP", "SL", "SCORE", "MAXHOLD"):
            v = int(exits.get(k, 0))
            print(f"  {k:<7}: {v:6d} ({v / trades:.3f})")
    else:
        for k in ("TP", "SL", "SCORE", "MAXHOLD"):
            print(f"  {k:<7}: {0:6d} (0.000)")

    print("RETURNS (fee_internal=0):")
    if rets.size:
        print(f"  {_quantiles_str(rets)}")
        print(f"  mean={float(np.mean(rets)):+.8f} sum(roi)={float(np.sum(rets)):+.8f}")
    else:
        print("  (none)")

    roi = float(ref.get("roi", 0.0))
    nt = int(ref.get("num_trades", 0))
    roi_fee = _roi_fee(roi, nt, fee_roundtrip)
    print(f"ROI_FEE (external): roi_fee = roi - fee*trades = {roi_fee:+.8f} (fee={fee_roundtrip})")

    print("HOLD BARS:")
    if holds.size:
        print(
            f"  min={int(np.min(holds))} med={float(np.median(holds))} "
            f"mean={float(np.mean(holds)):.2f} max={int(np.max(holds))}"
        )
    else:
        print("  (none)")

    tpv = ref.get("trades_preview", [])
    if isinstance(tpv, list) and tpv:
        print("TRADES PREVIEW (first up to 5):")
        for t in tpv:
            try:
                print(f"  i={t['i']} j={t['j']} reason={t['reason']} r={t['r']:+.8f}")
            except Exception:
                pass

    print("============================================================")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV path (with close + *_signal columns)")
    ap.add_argument("--rows", type=int, default=20000, help="nrows to load")
    ap.add_argument("--direction", choices=["long", "short"], default="short")
    ap.add_argument("--fee", type=float, default=0.0004, help="roundtrip fee used for ROI_FEE reporting only")
    ap.add_argument("--tp", type=float, default=0.04)
    ap.add_argument("--sl", type=float, default=0.02)
    ap.add_argument("--max_hold", type=int, default=1440)
    ap.add_argument("--enter_z", type=float, default=1.0)
    ap.add_argument("--exit_z", type=float, default=0.0)
    ap.add_argument("--comb", type=str, default="", help="comb dict as JSON or Python literal")
    args = ap.parse_args()

    print(f"REPO_ROOT: {REPO_ROOT}")
    print(f"CSV: {args.csv}")
    print(f"ROWS: {args.rows}")

    csv_path = args.csv
    if not os.path.isfile(csv_path):
        raise SystemExit(f"ERROR: csv not found: {csv_path}")

    df = pd.read_csv(csv_path, nrows=int(args.rows))
    comb = _parse_comb(args.comb)
    print(f"COMB: {comb}")
    print("")

    # --- BASE: engine.simtraderGS.evaluate_strategy (FORCE fee=0 for contract match) ---
    with _force_env_fee_zero():
        base = gs_evaluate_strategy(df, comb, args.direction)

    base_roi = float(base.get("roi", 0.0))
    base_tr = int(base.get("num_trades", 0))
    print("BASE (simtraderGS, fee forced to 0):")
    for k in ("roi", "num_trades", "winrate", "sharpe", "pnl_sum", "avg_trade"):
        if k in base:
            print(f"  {k}: {base[k]}")
    print(f"  roi_fee(external): {_roi_fee(base_roi, base_tr, float(args.fee))}")
    print("")

    # --- DIAG: exact replica with fee_internal=0 (contract comparison) ---
    score, close = _build_score(df, comb)

    direction = str(args.direction).lower().strip()
    tp = float(args.tp)
    sl = float(args.sl)
    max_hold = int(args.max_hold)
    enter_z = float(args.enter_z)
    exit_z = float(args.exit_z)

    if direction == "long":
        diag0 = _simulate_long_diag(score, close, tp, sl, max_hold, enter_z, exit_z, fee_rt_internal=0.0)
    else:
        diag0 = _simulate_short_diag(score, close, tp, sl, max_hold, enter_z, exit_z, fee_rt_internal=0.0)

    # Print instrumentation (fee external only)
    _print_block(direction=direction, fee_roundtrip=float(args.fee), ref=diag0)

    diag_roi = float(diag0["roi"])
    diag_tr = int(diag0["num_trades"])

    ok = _almost_equal(diag_roi, base_roi) and (diag_tr == base_tr)

    print("------------------------------------------------------------")
    print(f"SANITY (fee=0): DIAG vs BASE match: {ok}")
    print(f"  BASE roi={base_roi:+.12f} trades={base_tr}")
    print(f"  DIAG roi={diag_roi:+.12f} trades={diag_tr}")

    if not ok:
        # Actionable debug: show diffs that typically indicate contract drift.
        print("------------------------------------------------------------")
        print("ERROR: Contract mismatch. This should not happen.")
        print("Likely causes:")
        print("  - engine/simtraderGS.py contract changed (entry/exit/advance/order).")
        print("  - score/signals normalization differs (check *_signal columns, KEYMAP/SIGNALS).")
        print("  - fee was applied internally in GS despite forcing env fee=0 (unexpected).")
        print("")
        print("First checks:")
        print("  1) Ensure you run from repo root, and the imported engine/simtraderGS.py is the intended file.")
        print("  2) Verify df columns: close + the signals used by COMB exist and are in {-1,0,1}.")
        print("  3) Re-run with --rows 5000 for faster iteration.")
        raise SystemExit(2)

    print("============================================================")
    print("DONE")


if __name__ == "__main__":
    main()






