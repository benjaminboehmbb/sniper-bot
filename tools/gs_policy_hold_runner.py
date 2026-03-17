#!/usr/bin/env python3
# tools/gs_policy_hold_runner.py
#
# Purpose:
#   Policy experiments (gates + simple parameter overrides) without touching engine/simtraderGS.py.
#   Supports walk-forward validation via multiple offsets in one run.
#
# Key modes:
#   - Single window (default): --rows N --offset K
#   - Multi-window (walk-forward): --rows N --offsets "0,250000,500000"
#
# For gates:
#   --apply_regime_gate --regime_col regime_v1
#   Gate semantics:
#     long  -> keep rows where regime == +1
#     short -> keep rows where regime == -1
#
# Output:
#   For each offset prints ungated DEFAULT summary, then gated DEFAULT summary (if gate enabled),
#   plus a compact one-line "WF" line to compare quickly.
#
# ASCII-only.

from __future__ import annotations

import os
import sys
import json
import ast
import argparse
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


def _fail(msg: str) -> None:
    raise SystemExit(f"[ERROR] {msg}")


def repo_root_from_this_file() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, ".."))


REPO_ROOT = repo_root_from_this_file()
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    import engine.simtraderGS as gs  # type: ignore
except Exception as e:
    raise SystemExit(f"[FATAL] cannot import engine.simtraderGS: {e}")


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


def _get_gs_defaults() -> Dict[str, Any]:
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
class SimParams:
    tp: float
    sl: float
    max_hold: int
    enter_z: float
    exit_z: float


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


def _roi_fee(roi: float, trades: int, fee: float) -> float:
    return float(roi) - float(fee) * int(trades)


def _compute_stats(returns: np.ndarray) -> Tuple[float, float, float, float]:
    n = int(returns.size)
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0
    roi = float(np.sum(returns))
    winrate = float(np.mean(returns > 0.0))
    avg_trade = float(np.mean(returns))
    std = float(np.std(returns))
    sharpe = 0.0 if std == 0.0 else float((avg_trade / std) * np.sqrt(n))
    return roi, winrate, avg_trade, sharpe


def _apply_regime_gate(df: pd.DataFrame, direction: str, regime_col: str) -> pd.DataFrame:
    d = direction.lower().strip()
    if regime_col not in df.columns:
        _fail(f"regime gate requested but column not found: {regime_col}")
    if d == "long":
        return df[df[regime_col] == 1].copy()
    if d == "short":
        return df[df[regime_col] == -1].copy()
    _fail("direction must be long/short")
    return df  # unreachable


def _build_score(df: pd.DataFrame, comb: Dict[str, float]) -> np.ndarray:
    n = len(df)
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
    return score


def _simulate(df: pd.DataFrame, comb: Dict[str, float], direction: str, p: SimParams) -> DiagResult:
    d = direction.lower().strip()
    if d not in ("long", "short"):
        _fail("direction must be long or short")

    close = df["close"].to_numpy(dtype=float)
    n = close.size
    score = _build_score(df, comb)

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
                if score[i] > float(p.enter_z):
                    in_pos = True
                    entry_i = i
                    entry_px = close[i]
            else:
                if score[i] < -float(p.enter_z):
                    in_pos = True
                    entry_i = i
                    entry_px = close[i]
            i += 1
            continue

        j = i
        hold = j - entry_i

        if d == "long":
            r = (close[j] / entry_px) - 1.0
            hit_score = score[j] < float(p.exit_z)
        else:
            r = (entry_px / close[j]) - 1.0
            hit_score = score[j] > -float(p.exit_z)

        hit_tp = r >= float(p.tp)
        hit_sl = r <= -float(p.sl)
        hit_maxhold = hold >= int(p.max_hold)

        reason = None
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


def _print_one(tag: str, r: DiagResult, fee: float) -> None:
    print(
        f"{tag}: trades={r.num_trades} roi={r.roi:.6f} roi_fee={_roi_fee(r.roi, r.num_trades, fee):.6f} "
        f"winrate={r.winrate:.6f} sharpe={r.sharpe:.6f} avg_trade={r.avg_trade:.6f}"
    )


def _parse_offsets(text: str, single_offset: int) -> List[int]:
    t = (text or "").strip()
    if not t:
        return [int(single_offset)]
    out: List[int] = []
    for part in t.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(int(part))
    if not out:
        out = [int(single_offset)]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--rows", type=int, default=200000)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--offsets", type=str, default="", help='Comma-separated offsets for walk-forward, e.g. "0,250000,500000".')
    ap.add_argument("--direction", required=True, choices=["long", "short"])
    ap.add_argument("--fee", type=float, default=0.0004)
    ap.add_argument("--comb", type=str, default="")

    ap.add_argument("--regime_col", type=str, default="")
    ap.add_argument("--apply_regime_gate", action="store_true")

    # Policy override currently supported here (optional)
    ap.add_argument("--max_hold", type=int, default=None)

    args = ap.parse_args()

    if args.rows <= 0:
        _fail("ROWS must be > 0")

    offsets = _parse_offsets(args.offsets, args.offset)

    csv_path = args.csv
    if not os.path.isabs(csv_path):
        csv_path = os.path.join(REPO_ROOT, csv_path)
    if not os.path.isfile(csv_path):
        _fail(f"CSV not found: {csv_path}")

    comb = _parse_comb(args.comb)
    defaults = _get_gs_defaults()

    p_default = SimParams(
        tp=float(defaults["tp"]),
        sl=float(defaults["sl"]),
        max_hold=int(defaults["max_hold"]),
        enter_z=float(defaults["enter_z"]),
        exit_z=float(defaults["exit_z"]),
    )

    p_policy = SimParams(
        tp=float(defaults["tp"]),
        sl=float(defaults["sl"]),
        max_hold=int(defaults["max_hold"] if args.max_hold is None else args.max_hold),
        enter_z=float(defaults["enter_z"]),
        exit_z=float(defaults["exit_z"]),
    )

    print(f"REPO_ROOT: {REPO_ROOT}")
    print(f"CSV: {args.csv}")
    print(f"ROWS(per window): {args.rows}")
    print(f"OFFSETS: {offsets}")
    print(f"DIRECTION: {args.direction}")
    print(f"FEE(roundtrip): {args.fee}")
    print(f"COMB: {comb}")
    print("REGIME_GATE: " + ("ON" if args.apply_regime_gate else "OFF") + (f" col={args.regime_col}" if args.apply_regime_gate else ""))
    print("")
    print(f"DEFAULTS: tp={p_default.tp} sl={p_default.sl} max_hold={p_default.max_hold} enter_z={p_default.enter_z} exit_z={p_default.exit_z}")
    print(f"POLICY  : tp={p_policy.tp} sl={p_policy.sl} max_hold={p_policy.max_hold} enter_z={p_policy.enter_z} exit_z={p_policy.exit_z}")
    print("")

    # Load full CSV once (fast slicing for many offsets). Requires enough RAM.
    df_all = pd.read_csv(csv_path)

    total_len = len(df_all)
    for off in offsets:
        if off < 0 or off >= total_len:
            _fail(f"Offset out of range: {off} (len={total_len})")
        df = df_all.iloc[off : off + args.rows].copy()
        if len(df) < args.rows:
            _fail(f"Window too short at offset={off}: got {len(df)} rows, need {args.rows}")
        if "close" not in df.columns:
            _fail("CSV missing required column: close")

        # Ungated run (always)
        r_ung_def = _simulate(df, comb, args.direction, p_default)
        r_ung_pol = _simulate(df, comb, args.direction, p_policy)

        print("============================================================")
        print(f"WINDOW: offset={off} rows={args.rows} (ungated)")
        _print_one("UNGATED_DEFAULT", r_ung_def, args.fee)
        if args.max_hold is not None:
            _print_one("UNGATED_POLICY", r_ung_pol, args.fee)

        # Gated run (optional)
        if args.apply_regime_gate:
            col = args.regime_col.strip()
            if not col:
                _fail("--apply_regime_gate requires --regime_col")
            df_g = _apply_regime_gate(df, args.direction, col)
            r_g_def = _simulate(df_g, comb, args.direction, p_default)
            r_g_pol = _simulate(df_g, comb, args.direction, p_policy)

            print(f"WINDOW: offset={off} rows={args.rows} (gated post_rows={len(df_g)})")
            _print_one("GATED_DEFAULT", r_g_def, args.fee)
            if args.max_hold is not None:
                _print_one("GATED_POLICY", r_g_pol, args.fee)

            # Compact WF line for quick compare
            print(
                f"WF offset={off} ungated_roi_fee={_roi_fee(r_ung_def.roi, r_ung_def.num_trades, args.fee):.6f} "
                f"gated_roi_fee={_roi_fee(r_g_def.roi, r_g_def.num_trades, args.fee):.6f} "
                f"ungated_trades={r_ung_def.num_trades} gated_trades={r_g_def.num_trades} "
                f"post_rows={len(df_g)}"
            )
        else:
            print(
                f"WF offset={off} ungated_roi_fee={_roi_fee(r_ung_def.roi, r_ung_def.num_trades, args.fee):.6f} "
                f"ungated_trades={r_ung_def.num_trades}"
            )

    print("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())

