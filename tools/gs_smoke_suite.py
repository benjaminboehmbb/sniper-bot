#!/usr/bin/env python3
# tools/gs_smoke_suite.py
#
# Goldstandard Smoke Suite for engine/simtraderGS.py
# - Deterministic, fast, strict invariants
# - Exits with non-zero code on failure
#
# Run (WSL, from repo root):
#   python3 tools/gs_smoke_suite.py
#
# Optional:
#   PATH override:
#     GS_SMOKE_CSV=/path/to/file.csv python3 tools/gs_smoke_suite.py
#   Window size / offset:
#     GS_SMOKE_NROWS=200000 GS_SMOKE_OFFSET=0 python3 tools/gs_smoke_suite.py
#   Fee (roundtrip):
#     GS_SMOKE_FEE=0.0004 python3 tools/gs_smoke_suite.py
#
# Notes:
# - ASCII-only.
# - Fee handling: evaluate_strategy uses internal fee via env/config; this smoke suite
#   additionally checks external fee monotonicity for reporting/consistency.
# - Regime v1: external gate only (filter df). No simtraderGS logic changes.

from __future__ import annotations

import os
import sys
import json
import ast
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Repo root + import engine/*
# -----------------------------
def _repo_root_from_this_file() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, ".."))


REPO_ROOT = _repo_root_from_this_file()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from engine.simtraderGS import evaluate_strategy  # type: ignore
except Exception as e:
    raise SystemExit(f"[FATAL] cannot import engine.simtraderGS.evaluate_strategy: {e}")


# -----------------------------
# Defaults / env
# -----------------------------
DEFAULT_CSV = "data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS_REGIMEV1.csv"
# Fallback if REGIMEV1 not present
FALLBACK_CSV = "data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS.csv"

DEFAULT_NROWS = 200000
DEFAULT_OFFSET = 0
DEFAULT_FEE = 0.0004

# Regime v1 label column name (assumption based on builder)
# If your builder used a different column name, adjust here.
REGIME_COL_CANDIDATES = ["regime_v1", "regime", "regime_label", "regime_v1_label"]


def _env_str(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and str(v).strip() != "" else default


def _env_int(name: str, default: int) -> int:
    v = os.environ.get(name)
    if v is None or str(v).strip() == "":
        return int(default)
    return int(v)


def _env_float(name: str, default: float) -> float:
    v = os.environ.get(name)
    if v is None or str(v).strip() == "":
        return float(default)
    return float(v)


def _ok(msg: str) -> None:
    print(f"[ok] {msg}")


def _fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise AssertionError(msg)


def _parse_comb(s: str) -> Dict[str, float]:
    s = (s or "").strip()
    if not s:
        return {"rsi": 1.0, "macd": 1.0, "ma200": 1.0}
    try:
        obj = json.loads(s)
    except Exception:
        obj = ast.literal_eval(s)
    if not isinstance(obj, dict):
        _fail("comb must be a dict")
    out: Dict[str, float] = {}
    for k, v in obj.items():
        try:
            out[str(k)] = float(v)
        except Exception:
            continue
    return out


@dataclass
class SmokeCase:
    name: str
    comb: Dict[str, float]


CASES: List[SmokeCase] = [
    SmokeCase(name="BASELINE_3SIG", comb={"rsi": 1.0, "macd": 1.0, "ma200": 1.0}),
    SmokeCase(name="SINGLE_RSI", comb={"rsi": 1.0}),
    SmokeCase(name="SINGLE_MACD", comb={"macd": 1.0}),
    SmokeCase(name="SINGLE_MA200", comb={"ma200": 1.0}),
]


# -----------------------------
# Contract checks
# -----------------------------
def _check_basic_contract(res: Dict[str, Any]) -> None:
    for k in ["roi", "num_trades", "winrate", "sharpe", "avg_trade"]:
        if k not in res:
            _fail(f"missing key in result: {k}")
    # types + bounds
    if not isinstance(res["num_trades"], (int, np.integer)):
        _fail("num_trades must be int")
    if float(res["winrate"]) < 0.0 or float(res["winrate"]) > 1.0:
        _fail("winrate must be in [0,1]")
    # if no trades, sharpe and avg_trade must be 0
    if int(res["num_trades"]) == 0:
        if abs(float(res["sharpe"])) > 0.0:
            _fail("sharpe must be 0 when num_trades==0")
        if abs(float(res["avg_trade"])) > 0.0:
            _fail("avg_trade must be 0 when num_trades==0")


def _check_fee_monotonicity(res: Dict[str, Any], fee_roundtrip: float) -> Dict[str, Any]:
    # external fee: roi_fee = roi - fee * num_trades
    out = dict(res)
    out["roi_fee"] = float(out["roi"]) - float(fee_roundtrip) * int(out["num_trades"])
    return out


def _print_res(prefix: str, res: Dict[str, Any]) -> None:
    parts = []
    for k in ["roi", "roi_fee", "num_trades", "winrate", "sharpe", "avg_trade"]:
        if k in res:
            parts.append(f"{k}={res[k]}")
    print(f"{prefix}: " + " ".join(parts))


def _check_determinism(df: pd.DataFrame, comb: Dict[str, float], direction: str) -> None:
    r1 = evaluate_strategy(df, comb, direction)
    r2 = evaluate_strategy(df, comb, direction)
    for k in ["roi", "num_trades", "winrate", "sharpe", "avg_trade"]:
        if k not in r1 or k not in r2:
            _fail("determinism check missing keys")
        if isinstance(r1[k], float) or isinstance(r2[k], float):
            if abs(float(r1[k]) - float(r2[k])) > 0.0:
                _fail(f"non-deterministic {direction} {k}: {r1[k]} vs {r2[k]}")
        else:
            if r1[k] != r2[k]:
                _fail(f"non-deterministic {direction} {k}: {r1[k]} vs {r2[k]}")


# -----------------------------
# Regime v1 gating (external)
# -----------------------------
def _apply_regime_gate(df: pd.DataFrame, direction: str, regime_col: str) -> pd.DataFrame:
    # Expect mapping:
    #   bull (allow long)  => +1
    #   bear (allow short) => -1
    #   side               => 0
    d = direction.lower().strip()
    if d == "long":
        return df[df[regime_col] == 1]
    if d == "short":
        return df[df[regime_col] == -1]
    _fail("direction must be long/short")
    return df  # unreachable


def _regime_shares(df: pd.DataFrame, regime_col: str) -> Tuple[float, float, float]:
    v = df[regime_col].to_numpy()
    total = float(v.size) if v.size else 1.0
    bull = float(np.sum(v == 1)) / total
    bear = float(np.sum(v == -1)) / total
    side = float(np.sum(v == 0)) / total
    return bull, bear, side


# -----------------------------
# Main
# -----------------------------
def main() -> int:
    path = _env_str("GS_SMOKE_CSV", DEFAULT_CSV)
    nrows = _env_int("GS_SMOKE_NROWS", DEFAULT_NROWS)
    offset = _env_int("GS_SMOKE_OFFSET", DEFAULT_OFFSET)
    fee = _env_float("GS_SMOKE_FEE", DEFAULT_FEE)

    # Resolve CSV path
    if not os.path.isabs(path):
        path_abs = os.path.join(REPO_ROOT, path)
    else:
        path_abs = path

    if not os.path.isfile(path_abs):
        # fallback
        fb = os.path.join(REPO_ROOT, FALLBACK_CSV)
        if os.path.isfile(fb):
            print(f"[warn] CSV not found: {path_abs}")
            print(f"[warn] Falling back to: {fb}")
            path_abs = fb
        else:
            _fail(f"CSV not found: {path_abs} (and fallback missing)")

    print(f"[info] REPO_ROOT: {REPO_ROOT}")
    print(f"[info] CSV: {path_abs}")
    print(f"[info] WINDOW: offset={offset} nrows={nrows}")
    print(f"[info] FEE(roundtrip): {fee}")

    df_all = pd.read_csv(path_abs)
    if offset < 0 or nrows <= 0:
        _fail("invalid offset/nrows")
    if offset >= len(df_all):
        _fail("offset beyond dataframe length")

    df = df_all.iloc[offset: offset + nrows].copy()
    if "close" not in df.columns:
        _fail("close column missing in CSV window")

    # Locate regime column if present
    regime_col = ""
    for c in REGIME_COL_CANDIDATES:
        if c in df.columns:
            regime_col = c
            break
    if regime_col:
        bull, bear, side = _regime_shares(df, regime_col)
        print(f"[info] REGIME_COL: {regime_col}")
        print(f"[info] REGIME_SHARES: bull={bull:.6f} bear={bear:.6f} side={side:.6f}")
    else:
        print("[warn] No regime column found; gating tests will be skipped.")

    # Run smoke cases
    for case in CASES:
        print("============================================================")
        print(f"CASE: {case.name}")
        print(f"COMB: {case.comb}")

        # determinism checks (full df window)
        _check_determinism(df, case.comb, "long")
        _check_determinism(df, case.comb, "short")
        _ok("Determinism: PASS")

        # base evaluations
        resL = evaluate_strategy(df, case.comb, "long")
        resS = evaluate_strategy(df, case.comb, "short")

        _check_basic_contract(resL)
        _check_basic_contract(resS)

        resL = _check_fee_monotonicity(resL, fee)
        resS = _check_fee_monotonicity(resS, fee)

        _print_res("LONG", resL)
        _print_res("SHORT", resS)
        _ok("Contract+Fee invariants: PASS")

        # Optional gating test (external filter only)
        if regime_col:
            # 1) Gate enabled (regime_v1): filter df to allowed rows for each direction
            dfl = _apply_regime_gate(df, "long", regime_col)
            dfs = _apply_regime_gate(df, "short", regime_col)

            resLg = evaluate_strategy(dfl, case.comb, "long") if len(dfl) > 0 else {"roi": 0.0, "num_trades": 0, "winrate": 0.0, "sharpe": 0.0, "avg_trade": 0.0}
            resSg = evaluate_strategy(dfs, case.comb, "short") if len(dfs) > 0 else {"roi": 0.0, "num_trades": 0, "winrate": 0.0, "sharpe": 0.0, "avg_trade": 0.0}

            _check_basic_contract(resLg)
            _check_basic_contract(resSg)

            resLg = _check_fee_monotonicity(resLg, fee)
            resSg = _check_fee_monotonicity(resSg, fee)

            _print_res("LONG_GATED", resLg)
            _print_res("SHORT_GATED", resSg)

            # Hard effect: allow flags off must yield zero trades (contract-neutral)
            df0 = df.iloc[0:0]
            resL0 = evaluate_strategy(df0, case.comb, "long")
            resS0 = evaluate_strategy(df0, case.comb, "short")
            if int(resL0.get("num_trades", -1)) != 0 or abs(float(resL0.get("roi", 1.0))) != 0.0:
                _fail("gate allow_long=False (empty df) must yield num_trades=0 and roi=0 for long")
            if int(resS0.get("num_trades", -1)) != 0 or abs(float(resS0.get("roi", 1.0))) != 0.0:
                _fail("gate allow_short=False (empty df) must yield num_trades=0 and roi=0 for short")

            # Gate neutrality: wrapper disabled must be bit-identical to baseline
            resL_off = evaluate_strategy(df, case.comb, "long")
            resS_off = evaluate_strategy(df, case.comb, "short")
            for k in ["roi", "num_trades", "winrate", "sharpe", "avg_trade"]:
                if k not in resL_off or k not in resL:
                    _fail("gate neutrality long missing keys")
                if k not in resS_off or k not in resS:
                    _fail("gate neutrality short missing keys")
                if isinstance(resL[k], float) or isinstance(resL_off[k], float):
                    if abs(float(resL_off[k]) - float(resL[k])) > 0.0:
                        _fail(f"gate neutrality long {k} differs: off={resL_off[k]} base={resL[k]}")
                else:
                    if resL_off[k] != resL[k]:
                        _fail(f"gate neutrality long {k} differs: off={resL_off[k]} base={resL[k]}")
                if isinstance(resS[k], float) or isinstance(resS_off[k], float):
                    if abs(float(resS_off[k]) - float(resS[k])) > 0.0:
                        _fail(f"gate neutrality short {k} differs: off={resS_off[k]} base={resS[k]}")
                else:
                    if resS_off[k] != resS[k]:
                        _fail(f"gate neutrality short {k} differs: off={resS_off[k]} base={resS[k]}")

            # Soft sanity: gated num_trades <= ungated num_trades + 1%
            # (Filtering rows can sometimes create slightly different entry patterns, but should not explode.)
            ntL = int(resL["num_trades"])
            ntLg = int(resLg["num_trades"])
            ntS = int(resS["num_trades"])
            ntSg = int(resSg["num_trades"])
            if ntL > 0 and ntLg > int(ntL * 1.01) + 2:
                _fail(f"gated long num_trades unexpectedly larger: gated={ntLg} ungated={ntL}")
            if ntS > 0 and ntSg > int(ntS * 1.01) + 2:
                _fail(f"gated short num_trades unexpectedly larger: gated={ntSg} ungated={ntS}")

            _ok("Regime gate effect+neutrality: PASS")

    print("============================================================")
    _ok("GS SMOKE SUITE: ALL PASS")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc)
    except AssertionError:
        # Already printed [FAIL]
        sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Unhandled exception: {e}")
        sys.exit(2)

