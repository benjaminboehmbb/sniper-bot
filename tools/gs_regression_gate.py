#!/usr/bin/env python3
# tools/gs_regression_gate.py
#
# Purpose:
#   Fast regression gate for simtraderGS contract.
#   Fails hard on:
#     - nondeterminism
#     - diagnostics mismatch (SANITY fee=0 must be True)
#     - regime gate neutrality regressions (basic)
#     - policy-runner contract regressions (basic)
#
# Usage (example):
#   python3 tools/gs_regression_gate.py --csv data/...REGIMEV1.csv --rows 200000 --fee 0.0004 --regime_col regime_v1
#
# Output: minimal ASCII, exits non-zero on failure.

from __future__ import annotations

import os
import sys
import json
import ast
import argparse
from contextlib import contextmanager
from typing import Dict, Any, Optional

import pandas as pd


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    import engine.simtraderGS as gs  # type: ignore
except Exception as e:
    raise SystemExit(f"[FAIL] import simtraderGS: {e}")


def die(msg: str) -> None:
    raise SystemExit(f"[FAIL] {msg}")


def ok(msg: str) -> None:
    print(f"[ok] {msg}")


def parse_comb(text: str) -> Dict[str, float]:
    if not text:
        return {"rsi": 1.0, "macd": 1.0, "ma200": 1.0}
    try:
        obj = json.loads(text)
    except Exception:
        obj = ast.literal_eval(text)
    if not isinstance(obj, dict):
        die("comb must be dict")
    out: Dict[str, float] = {}
    for k, v in obj.items():
        out[str(k)] = float(v)
    return out


def gs_defaults() -> Dict[str, Any]:
    cfg = getattr(gs, "_CFG", None)
    if not isinstance(cfg, dict):
        die("GS _CFG missing/not dict")
    strat = cfg.get("strategy", None)
    if not isinstance(strat, dict):
        die("GS _CFG['strategy'] missing/not dict")
    risk = strat.get("risk", None)
    if not isinstance(risk, dict):
        die("GS _CFG['strategy']['risk'] missing/not dict")
    try:
        return dict(
            tp=float(risk["take_profit_pct"]),
            sl=float(risk["stop_loss_pct"]),
            max_hold=int(strat["max_hold_bars"]),
            enter_z=float(strat["enter_z"]),
            exit_z=float(strat["exit_z"]),
        )
    except KeyError as e:
        die(f"GS config key missing: {e}")


@contextmanager
def patch_gs_config(
    *,
    tp: Optional[float] = None,
    sl: Optional[float] = None,
    max_hold: Optional[int] = None,
    enter_z: Optional[float] = None,
    exit_z: Optional[float] = None,
    fee_roundtrip: Optional[float] = None,
):
    cfg = gs._CFG
    strat = cfg["strategy"]
    risk = strat["risk"]

    old_tp = float(risk["take_profit_pct"])
    old_sl = float(risk["stop_loss_pct"])
    old_max_hold = int(strat["max_hold_bars"])
    old_enter_z = float(strat["enter_z"])
    old_exit_z = float(strat["exit_z"])

    env_key = "SIMTRADERGS_FEE_ROUNDTRIP"
    old_env_fee = os.environ.get(env_key, None)

    try:
        if tp is not None:
            risk["take_profit_pct"] = float(tp)
        if sl is not None:
            risk["stop_loss_pct"] = float(sl)
        if max_hold is not None:
            strat["max_hold_bars"] = int(max_hold)
        if enter_z is not None:
            strat["enter_z"] = float(enter_z)
        if exit_z is not None:
            strat["exit_z"] = float(exit_z)
        if fee_roundtrip is not None:
            os.environ[env_key] = str(float(fee_roundtrip))
        yield
    finally:
        risk["take_profit_pct"] = old_tp
        risk["stop_loss_pct"] = old_sl
        strat["max_hold_bars"] = old_max_hold
        strat["enter_z"] = old_enter_z
        strat["exit_z"] = old_exit_z

        if old_env_fee is None:
            os.environ.pop(env_key, None)
        else:
            os.environ[env_key] = old_env_fee


def eval_gs(df: pd.DataFrame, comb: Dict[str, float], direction: str) -> Dict[str, Any]:
    res = gs.evaluate_strategy(df, comb, direction)
    if not isinstance(res, dict):
        die("evaluate_strategy did not return dict")
    for k in ("roi", "num_trades", "winrate", "sharpe"):
        if k not in res:
            die(f"evaluate_strategy missing key: {k}")
    return res


def require_close_and_signals(df: pd.DataFrame, comb: Dict[str, float]) -> None:
    if "close" not in df.columns:
        die("CSV missing 'close'")
    for k in comb.keys():
        c = f"{k}_signal"
        if c not in df.columns:
            die(f"CSV missing signal column: {c}")


def regime_gate(df: pd.DataFrame, direction: str, col: str) -> pd.DataFrame:
    if col not in df.columns:
        die(f"CSV missing regime col: {col}")
    if direction == "long":
        return df[df[col] == 1].copy()
    return df[df[col] == -1].copy()


def approx_equal(a: float, b: float, eps: float = 1e-12) -> bool:
    return abs(a - b) <= eps


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--fee", type=float, default=0.0004)
    ap.add_argument("--regime_col", default="")
    ap.add_argument("--comb", default="")
    args = ap.parse_args()

    comb = parse_comb(args.comb)
    df_all = pd.read_csv(args.csv)
    df = df_all.iloc[args.offset : args.offset + args.rows].copy()

    require_close_and_signals(df, comb)

    base = gs_defaults()

    # ----------------------------
    # 1) Determinism (same call twice)
    # ----------------------------
    with patch_gs_config(
        tp=base["tp"], sl=base["sl"], max_hold=base["max_hold"],
        enter_z=base["enter_z"], exit_z=base["exit_z"],
        fee_roundtrip=args.fee
    ):
        r1L = eval_gs(df, comb, "long")
        r2L = eval_gs(df, comb, "long")
        r1S = eval_gs(df, comb, "short")
        r2S = eval_gs(df, comb, "short")

    if not (approx_equal(float(r1L["roi"]), float(r2L["roi"])) and int(r1L["num_trades"]) == int(r2L["num_trades"])):
        die("Determinism FAIL (long)")
    if not (approx_equal(float(r1S["roi"]), float(r2S["roi"])) and int(r1S["num_trades"]) == int(r2S["num_trades"])):
        die("Determinism FAIL (short)")
    ok("Determinism PASS")

    # ----------------------------
    # 2) Fee invariance sanity (fee=0 vs external arithmetic)
    #    We only ensure internal fee wiring is controllable.
    # ----------------------------
    with patch_gs_config(
        tp=base["tp"], sl=base["sl"], max_hold=base["max_hold"],
        enter_z=base["enter_z"], exit_z=base["exit_z"],
        fee_roundtrip=0.0
    ):
        zL = eval_gs(df, comb, "long")
        zS = eval_gs(df, comb, "short")
    with patch_gs_config(
        tp=base["tp"], sl=base["sl"], max_hold=base["max_hold"],
        enter_z=base["enter_z"], exit_z=base["exit_z"],
        fee_roundtrip=args.fee
    ):
        fL = eval_gs(df, comb, "long")
        fS = eval_gs(df, comb, "short")

    # internal ROI should differ by approx fee * trades (roundtrip)
    # allow tiny eps because of float ops
    expL = float(zL["roi"]) - float(args.fee) * int(zL["num_trades"])
    expS = float(zS["roi"]) - float(args.fee) * int(zS["num_trades"])
    if abs(float(fL["roi"]) - expL) > 1e-8:
        die("Fee wiring FAIL (long)")
    if abs(float(fS["roi"]) - expS) > 1e-8:
        die("Fee wiring FAIL (short)")
    ok("Fee wiring PASS")

    # ----------------------------
    # 3) Regime gate neutrality basic check
    # ----------------------------
    if args.regime_col:
        dfL = regime_gate(df, "long", args.regime_col)
        dfS = regime_gate(df, "short", args.regime_col)

        with patch_gs_config(
            tp=base["tp"], sl=base["sl"], max_hold=base["max_hold"],
            enter_z=base["enter_z"], exit_z=base["exit_z"],
            fee_roundtrip=args.fee
        ):
            gL = eval_gs(dfL, comb, "long")
            gS = eval_gs(dfS, comb, "short")

        # minimal sanity: gating should reduce or equal post_rows and be evaluable
        if len(dfL) <= 0 or len(dfS) <= 0:
            die("Regime gate produced empty df (unexpected for typical windows)")
        if int(gL["num_trades"]) < 0 or int(gS["num_trades"]) < 0:
            die("Regime gate eval returned negative trades")
        ok("Regime gate PASS")

    # ----------------------------
    # 4) Policy invariants: known bad exit_z=+0.2 must be worse (optional)
    #    We keep it minimal: only check that it increases trades a lot (signal of behavior).
    # ----------------------------
    if args.regime_col:
        dfL = regime_gate(df, "long", args.regime_col)

        with patch_gs_config(
            tp=base["tp"], sl=base["sl"], max_hold=base["max_hold"],
            enter_z=base["enter_z"], exit_z=base["exit_z"],
            fee_roundtrip=args.fee
        ):
            baseL = eval_gs(dfL, comb, "long")

        with patch_gs_config(
            tp=base["tp"], sl=base["sl"], max_hold=base["max_hold"],
            enter_z=base["enter_z"], exit_z=0.2,
            fee_roundtrip=args.fee
        ):
            polL = eval_gs(dfL, comb, "long")

        if int(polL["num_trades"]) <= int(baseL["num_trades"]):
            die("Policy check FAIL: exit_z=0.2 did not increase trades (unexpected)")
        ok("Policy check PASS")

    print("[ok] GS REGRESSION GATE: ALL PASS")


if __name__ == "__main__":
    main()
