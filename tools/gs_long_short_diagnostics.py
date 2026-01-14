#!/usr/bin/env python3
# tools/gs_long_short_diagnostics.py
#
# Purpose:
#   Diagnose LONG/SHORT-Logik von engine/simtraderGS.py gegen eine instrumentierte
#   Referenzsimulation (Trade-Counts, Exit-Gruende, Returns, Holds).
#
# Key properties:
#   - CONTRACT MODE:
#       SANITY (fee=0): DIAG_DEFAULT vs BASE must match EXACTLY.
#   - POLICY MODE (when overrides are provided):
#       1) Still enforce CONTRACT sanity on DEFAULT params (hard invariant).
#       2) Run DIAG with overrides and report deltas vs DIAG_DEFAULT.
#       3) Do NOT compare override run to BASE (GS core uses fixed defaults).
#
# ASCII-only.

from __future__ import annotations

import os
import sys
import json
import ast
import argparse
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
import pandas as pd


def repo_root_from_this_file() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, ".."))


REPO_ROOT = repo_root_from_this_file()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    import engine.simtraderGS as gs  # type: ignore
    from engine.simtraderGS import evaluate_strategy  # type: ignore
except Exception as e:
    raise SystemExit(f"[FATAL] cannot import engine.simtraderGS: {e}")


def _fail(msg: str) -> None:
    raise SystemExit(msg)


def _parse_comb(text: str) -> Dict[str, float]:
    text = (text or "").strip()
    if not text:
        return {"rsi": 1.0, "macd": 1.0, "ma200": 1.0}
    try:
        obj = json.loads(text)
    except Exception:
        obj = ast.literal_eval(text)
    if not isinstance(obj, dict):
        _fail("COMB must be a dict-like string.")
    out: Dict[str, float] = {}
    for k, v in obj.items():
        try:
            out[str(k)] = float(v)
        except Exception:
            pass
    return out


def _load_csv_window(path: str, rows: int) -> pd.DataFrame:
    if not os.path.isabs(path):
        path = os.path.join(REPO_ROOT, path)
    if not os.path.isfile(path):
        _fail(f"CSV not found: {path}")
    df = pd.read_csv(path)
    if rows <= 0:
        _fail("ROWS must be > 0")
    df = df.iloc[:rows].copy()
    return df


def _get_gs_defaults() -> Dict[str, Any]:
    # engine/simtraderGS.py defines _CFG as the authoritative defaults
    cfg = getattr(gs, "_CFG", None)
    if not isinstance(cfg, dict):
        _fail("engine/simtraderGS.py does not expose _CFG dict. Cannot read defaults.")
    strat = cfg.get("strategy", {})
    risk = strat.get("risk", {})
    return {
        "tp": float(risk.get("take_profit_pct", 0.04)),
        "sl": float(risk.get("stop_loss_pct", 0.02)),
        "max_hold": int(strat.get("max_hold_bars", 1440)),
        "enter_z": float(strat.get("enter_z", 1.0)),
        "exit_z": float(strat.get("exit_z", 0.0)),
    }


@dataclass
class DiagResult:
    roi: float
    num_trades: int
    winrate: float
    sharpe: float
    avg_trade: float
    pnl_sum: float
    returns: np.ndarray
    exit_counts: Dict[str, int]
    hold_bars: np.ndarray


def _compute_stats(returns: np.ndarray) -> Tuple[float, float, float, float]:
    # returns are per-trade ROIs (fee_internal assumed 0 in DIAG)
    n = int(returns.size)
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0
    roi = float(np.sum(returns))
    winrate = float(np.mean(returns > 0.0))
    avg_trade = float(np.mean(returns))
    # sharpe here: mean/std * sqrt(n), with guard
    std = float(np.std(returns))
    sharpe = 0.0 if std == 0.0 else float((avg_trade / std) * np.sqrt(n))
    return roi, winrate, avg_trade, sharpe


def _simulate_diag(
    df: pd.DataFrame,
    comb: Dict[str, float],
    direction: str,
    tp: float,
    sl: float,
    max_hold: int,
    enter_z: float,
    exit_z: float,
) -> DiagResult:
    # Expect discrete signals in {-1,0,1}. Score = sum(w_i * signal_i).
    # Entry/Exit as defined in simtraderGS contract comments.
    d = direction.lower().strip()
    if d not in ("long", "short"):
        _fail("direction must be long or short")

    close = df["close"].to_numpy(dtype=float)
    n = close.size

    # Build score
    score = np.zeros(n, dtype=float)
    missing: List[str] = []
    for k, w in comb.items():
        col = f"{k}_signal"
        if col not in df.columns:
            missing.append(col)
            continue
        sig = df[col].to_numpy(dtype=float)
        score += float(w) * sig
    if missing:
        _fail(f"Missing signal columns: {missing}")

    # Contract: long entry score > +enter_z ; exit score < +exit_z
    #           short entry score < -enter_z ; exit score > -exit_z
    in_pos = False
    entry_i = -1
    entry_px = 0.0
    holds: List[int] = []
    rets: List[float] = []
    exit_counts = {"TP": 0, "SL": 0, "SCORE": 0, "MAXHOLD": 0}

    i = 0
    while i < n:
        if not in_pos:
            if d == "long":
                if score[i] > float(enter_z):
                    in_pos = True
                    entry_i = i
                    entry_px = close[i]
            else:
                if score[i] < -float(enter_z):
                    in_pos = True
                    entry_i = i
                    entry_px = close[i]
            i += 1
            continue

        # in position: advance at least 1 bar
        j = i
        # evaluate exits at j
        hold = j - entry_i
        # price return (no fee_internal in DIAG)
        if d == "long":
            r = (close[j] / entry_px) - 1.0
        else:
            r = (entry_px / close[j]) - 1.0

        # TP/SL thresholds on r
        hit_tp = r >= float(tp)
        hit_sl = r <= -float(sl)

        hit_score = False
        if d == "long":
            hit_score = score[j] < float(exit_z)
        else:
            hit_score = score[j] > -float(exit_z)

        hit_maxhold = hold >= int(max_hold)

        reason = None
        # priority: TP, SL, SCORE, MAXHOLD (match your prior diagnostics behavior)
        if hit_tp:
            reason = "TP"
        elif hit_sl:
            reason = "SL"
        elif hit_score:
            reason = "SCORE"
        elif hit_maxhold:
            reason = "MAXHOLD"

        if reason is not None:
            exit_counts[reason] = exit_counts.get(reason, 0) + 1
            holds.append(hold if hold >= 1 else 1)
            rets.append(float(r))
            in_pos = False
            entry_i = -1
            entry_px = 0.0
            i = j + 1
        else:
            i = j + 1

    returns = np.array(rets, dtype=float)
    hold_bars = np.array(holds, dtype=int)
    roi, winrate, avg_trade, sharpe = _compute_stats(returns)

    return DiagResult(
        roi=roi,
        num_trades=int(returns.size),
        winrate=winrate,
        sharpe=sharpe,
        avg_trade=avg_trade,
        pnl_sum=roi,
        returns=returns,
        exit_counts=exit_counts,
        hold_bars=hold_bars,
    )


def _print_diag_block(title: str, dr: DiagResult, fee: float) -> None:
    print(title)
    print(f"  roi: {dr.roi}")
    print(f"  num_trades: {dr.num_trades}")
    print(f"  winrate: {dr.winrate}")
    print(f"  sharpe: {dr.sharpe}")
    print(f"  pnl_sum: {dr.pnl_sum}")
    print(f"  avg_trade: {dr.avg_trade}")
    roi_fee = dr.roi - float(fee) * int(dr.num_trades)
    print(f"  roi_fee(external): {roi_fee}")
    print("")
    print("EXIT COUNTS:")
    total = max(1, dr.num_trades)
    for k in ["TP", "SL", "SCORE", "MAXHOLD"]:
        c = int(dr.exit_counts.get(k, 0))
        print(f"  {k:7}: {c:6d} ({c/total:.3f})")
    print("HOLD BARS:")
    if dr.num_trades == 0:
        print("  (no trades)")
    else:
        hb = dr.hold_bars
        print(f"  min={int(np.min(hb))} med={float(np.median(hb))} mean={float(np.mean(hb)):.2f} max={int(np.max(hb))}")
    print("")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--rows", type=int, default=20000)
    ap.add_argument("--direction", required=True, choices=["long", "short"])
    ap.add_argument("--fee", type=float, default=0.0004)
    ap.add_argument("--comb", type=str, default="")
    # override knobs (POLICY MODE when any differs from GS defaults)
    ap.add_argument("--tp", type=float, default=None)
    ap.add_argument("--sl", type=float, default=None)
    ap.add_argument("--max_hold", type=int, default=None)
    ap.add_argument("--enter_z", type=float, default=None)
    ap.add_argument("--exit_z", type=float, default=None)

    args = ap.parse_args()

    comb = _parse_comb(args.comb)

    print(f"REPO_ROOT: {REPO_ROOT}")
    print(f"CSV: {args.csv}")
    print(f"ROWS: {args.rows}")
    print(f"COMB: {comb}")
    print("")

    df = _load_csv_window(args.csv, args.rows)

    # BASE always uses GS core defaults. Fee forced to 0 in GS already (per your tool behavior).
    base = evaluate_strategy(df, comb, args.direction)

    print("BASE (simtraderGS, fee forced to 0):")
    for k in ["roi", "num_trades", "winrate", "sharpe", "pnl_sum", "avg_trade"]:
        if k in base:
            print(f"  {k}: {base[k]}")
    roi_fee_base = float(base.get("roi", 0.0)) - float(args.fee) * int(base.get("num_trades", 0))
    print(f"  roi_fee(external): {roi_fee_base}")
    print("")

    defaults = _get_gs_defaults()
    # resolve overrides -> policy params
    tp = defaults["tp"] if args.tp is None else float(args.tp)
    sl = defaults["sl"] if args.sl is None else float(args.sl)
    max_hold = defaults["max_hold"] if args.max_hold is None else int(args.max_hold)
    enter_z = defaults["enter_z"] if args.enter_z is None else float(args.enter_z)
    exit_z = defaults["exit_z"] if args.exit_z is None else float(args.exit_z)

    policy_mode = (
        (tp != defaults["tp"])
        or (sl != defaults["sl"])
        or (max_hold != defaults["max_hold"])
        or (enter_z != defaults["enter_z"])
        or (exit_z != defaults["exit_z"])
    )

    print("============================================================")
    print(f"DIRECTION: {args.direction.upper()}")
    print(f"GS DEFAULTS: tp={defaults['tp']} sl={defaults['sl']} max_hold={defaults['max_hold']} enter_z={defaults['enter_z']} exit_z={defaults['exit_z']}")
    print(f"DIAG PARAMS : tp={tp} sl={sl} max_hold={max_hold} enter_z={enter_z} exit_z={exit_z}")
    print("MODE       :", "POLICY (override)" if policy_mode else "CONTRACT (default)")
    print("============================================================")
    print("")

    # Always run DIAG_DEFAULT and enforce SANITY as hard invariant
    diag_default = _simulate_diag(
        df=df,
        comb=comb,
        direction=args.direction,
        tp=defaults["tp"],
        sl=defaults["sl"],
        max_hold=defaults["max_hold"],
        enter_z=defaults["enter_z"],
        exit_z=defaults["exit_z"],
    )

    # SANITY must match BASE exactly (roi + trades) for default params
    sanity_ok = (abs(diag_default.roi - float(base.get("roi", 0.0))) == 0.0) and (diag_default.num_trades == int(base.get("num_trades", -1)))
    print("SANITY (fee=0): DIAG_DEFAULT vs BASE match:", "True" if sanity_ok else "False")
    print(f"  BASE roi={float(base.get('roi', 0.0)):.12f} trades={int(base.get('num_trades', 0))}")
    print(f"  DIAG roi={diag_default.roi:.12f} trades={diag_default.num_trades}")
    print("")

    if not sanity_ok:
        print("ERROR: Contract mismatch in DEFAULT mode. This should not happen.")
        return 2

    _print_diag_block("DIAG_DEFAULT (contract)", diag_default, args.fee)

    # If no overrides, we are done (contract verified + detailed stats)
    if not policy_mode:
        print("DONE")
        return 0

    # POLICY MODE: run DIAG with overrides and report deltas vs DIAG_DEFAULT
    diag_policy = _simulate_diag(
        df=df,
        comb=comb,
        direction=args.direction,
        tp=tp,
        sl=sl,
        max_hold=max_hold,
        enter_z=enter_z,
        exit_z=exit_z,
    )

    _print_diag_block("DIAG_POLICY (override)", diag_policy, args.fee)

    # Report deltas
    print("DELTA (POLICY - DEFAULT):")
    print(f"  trades: {diag_policy.num_trades - diag_default.num_trades:+d} (policy={diag_policy.num_trades} default={diag_default.num_trades})")
    print(f"  roi   : {diag_policy.roi - diag_default.roi:+.6f} (policy={diag_policy.roi:.6f} default={diag_default.roi:.6f})")
    roi_fee_def = diag_default.roi - float(args.fee) * diag_default.num_trades
    roi_fee_pol = diag_policy.roi - float(args.fee) * diag_policy.num_trades
    print(f"  roi_fee(external): {roi_fee_pol - roi_fee_def:+.6f} (policy={roi_fee_pol:.6f} default={roi_fee_def:.6f})")
    if diag_default.num_trades > 0 and diag_policy.num_trades > 0:
        print(f"  hold mean: {float(np.mean(diag_policy.hold_bars)) - float(np.mean(diag_default.hold_bars)):+.2f}")
        print(f"  hold max : {int(np.max(diag_policy.hold_bars)) - int(np.max(diag_default.hold_bars)):+d}")
    print("")
    print("NOTE: POLICY results are NOT compared to BASE, because simtraderGS uses fixed defaults.")
    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())







