#!/usr/bin/env python3
# tools/gs_short_diagnostics.py
#
# Zweck:
# - Diagnose der GS-Trade-Logik fuer SHORT (und optional LONG) inkl. Exit-Reason Counts.
# - Wichtig: Die Diagnose-Simulation MUSS exakt zur simtraderGS-Logik passen.
#
# Ausgabe:
# - BASE (aus engine.simtraderGS.evaluate_strategy)
# - DIAG (eigene Simulation) + Exit Counts, Returns Quantile, Hold Bars
# - Sanity: BASE vs DIAG (ROI/num_trades) muessen matchen (kleine Rundungsabweichung ok)

from __future__ import annotations

import os
import sys
from typing import Dict, Any, Tuple, List

import numpy as np
import pandas as pd


def repo_root_from_this_file() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, ".."))


def finite_array(a: np.ndarray, fill: float = 0.0) -> np.ndarray:
    if not isinstance(a, np.ndarray):
        a = np.asarray(a, dtype=float)
    return np.nan_to_num(a.astype(float), nan=fill, posinf=fill, neginf=fill)


SIGNALS = [
    "rsi_signal", "macd_signal", "bollinger_signal",
    "ma200_signal", "stoch_signal", "atr_signal", "ema50_signal",
    "adx_signal", "cci_signal", "mfi_signal", "obv_signal", "roc_signal",
]

KEYMAP = {
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
}


def build_score(df: pd.DataFrame, comb: Dict[str, float]) -> np.ndarray:
    # expects *_signal columns already present (discrete -1/0/1 or numeric)
    score = np.zeros(len(df), dtype=float)

    for k, w in comb.items():
        col = KEYMAP.get(k, k)
        if col not in df.columns:
            continue
        try:
            weight = float(w)
        except Exception:
            continue

        arr = finite_array(df[col].to_numpy(dtype=float), fill=0.0)
        arr = np.where(arr > 0.0, 1.0, np.where(arr < 0.0, -1.0, 0.0)).astype(float)
        score += weight * arr

    return finite_array(score, fill=0.0)


def sharpe_from_rets(rets: np.ndarray) -> float:
    if rets.size < 2:
        return 0.0
    mu = float(np.mean(rets))
    sd = float(np.std(rets))
    if not np.isfinite(sd) or sd <= 1e-12:
        return 0.0
    return mu / sd


def simulate_short_with_reasons(
    score: np.ndarray,
    close: np.ndarray,
    tp: float,
    sl: float,
    max_hold: int,
    enter_z: float,
    exit_z: float,
    fee_roundtrip: float,
) -> Tuple[Dict[str, Any], Dict[str, int], np.ndarray, np.ndarray]:
    # CORRECT SHORT:
    # Entry: score < -enter_z
    # Exit:  score > -exit_z
    n = score.shape[0]
    entries = score < (-enter_z)
    exit_thr = (-exit_z)

    returns: List[float] = []
    holds: List[int] = []
    reasons = {"TP": 0, "SL": 0, "SCORE": 0, "MAXHOLD": 0}

    wins = 0
    num = 0
    i = 0

    while i < n:
        if not entries[i]:
            i += 1
            continue

        entry_px = close[i]
        j = i + 1
        exited = False
        j_end = min(n, i + max_hold + 1)

        while j < j_end:
            r = (entry_px - close[j]) / entry_px
            if not np.isfinite(r):
                r = 0.0

            if r >= tp:
                r = r - fee_roundtrip
                returns.append(float(r))
                holds.append(j - i)
                reasons["TP"] += 1
                wins += 1
                num += 1
                i = j + 1
                exited = True
                break

            if r <= -sl:
                r = r - fee_roundtrip
                returns.append(float(r))
                holds.append(j - i)
                reasons["SL"] += 1
                num += 1
                i = j + 1
                exited = True
                break

            if score[j] > exit_thr:
                r = r - fee_roundtrip
                returns.append(float(r))
                holds.append(j - i)
                reasons["SCORE"] += 1
                wins += int(r > 0)
                num += 1
                i = j + 1
                exited = True
                break

            j += 1

        if not exited:
            j = j_end - 1
            r = (entry_px - close[j]) / entry_px
            if not np.isfinite(r):
                r = 0.0
            r = r - fee_roundtrip
            returns.append(float(r))
            holds.append(j - i)
            reasons["MAXHOLD"] += 1
            wins += int(r > 0)
            num += 1
            i = j_end

    rets = np.array(returns, dtype=float) if returns else np.empty(0, dtype=float)
    h = np.array(holds, dtype=int) if holds else np.empty(0, dtype=int)
    if rets.size:
        rets = finite_array(rets, fill=0.0)

    roi = float(rets.sum()) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0
    sharpe = sharpe_from_rets(rets)

    res = {
        "roi": roi,
        "num_trades": int(num),
        "winrate": winrate,
        "sharpe": float(sharpe),
        "pnl_sum": roi,
        "avg_trade": float(roi / num) if num else 0.0,
    }
    return res, reasons, rets, h


def print_block(direction: str, fee: float, diag: Dict[str, Any], reasons: Dict[str, int], rets: np.ndarray, holds: np.ndarray) -> None:
    print("=" * 60)
    print(f"DIRECTION: {direction.upper()}")
    print(f"FEE (roundtrip): {fee}")
    print(f"TRADES: {diag['num_trades']}")
    print("EXIT COUNTS:")
    total = diag["num_trades"] if diag["num_trades"] else 0
    for k in ("TP", "SL", "SCORE", "MAXHOLD"):
        v = reasons.get(k, 0)
        frac = (v / total) if total else 0.0
        print(f"  {k:<7}: {v:6d} ({frac:0.3f})")

    if rets.size:
        qs = np.quantile(rets, [0.05, 0.25, 0.50, 0.75, 0.95])
        print("RETURNS:")
        print(
            "  q05={:+0.5f} q25={:+0.5f} q50={:+0.5f} q75={:+0.5f} q95={:+0.5f}".format(
                float(qs[0]), float(qs[1]), float(qs[2]), float(qs[3]), float(qs[4])
            )
        )
        print(f"  mean={np.mean(rets):+0.5f} sum={np.sum(rets):+0.5f}")
    else:
        print("RETURNS: (none)")

    if holds.size:
        print("HOLD BARS:")
        print(f"  min={int(np.min(holds))} med={float(np.median(holds))} mean={float(np.mean(holds)):.1f} max={int(np.max(holds))}")
    else:
        print("HOLD BARS: (none)")


def main() -> int:
    repo = repo_root_from_this_file()
    sys.path.insert(0, repo)

    from engine.simtraderGS import evaluate_strategy  # noqa

    price_csv = os.environ.get(
        "GS_PRICE_CSV",
        "data/btcusdt_1m_2026-01-07/simtraderGS/btcusdt_1m_price_2017_2025_GS_PLUS_FORWARD_WITH_SIGNALS.csv",
    )
    nrows = int(os.environ.get("GS_NROWS", "20000"))

    comb = {"rsi": 1.0, "macd": 1.0, "ma200": 1.0}

    df = pd.read_csv(os.path.join(repo, price_csv), nrows=nrows)
    if "close" not in df.columns:
        raise SystemExit("Missing column: close")

    close = finite_array(df["close"].to_numpy(dtype=float), fill=0.0)
    score = build_score(df, comb)

    # Parameters (hard-coded as current GS defaults; keep aligned)
    tp = 0.04
    sl = 0.02
    max_hold = 1440
    enter_z = 1.0
    exit_z = 0.0

    print(f"REPO_ROOT: {repo}")
    print(f"ROWS: {len(df)}")
    print(f"COMB: {comb}")
    print("")
    print("BASE (simtraderGS):")
    base_short = evaluate_strategy(df, comb, "short")
    for k in ("roi", "num_trades", "winrate", "sharpe", "pnl_sum", "avg_trade"):
        print(f"  {k}: {base_short.get(k)}")
    print("")

    # Fee scenarios for DIAG
    for fee in (0.0, 0.0004):
        diag, reasons, rets, holds = simulate_short_with_reasons(
            score=score,
            close=close,
            tp=tp,
            sl=sl,
            max_hold=max_hold,
            enter_z=enter_z,
            exit_z=exit_z,
            fee_roundtrip=fee,
        )
        print_block("short", fee, diag, reasons, rets, holds)

        # Sanity vs BASE only for fee=0.0 (BASE currently has fee=0 unless env set)
        if fee == 0.0:
            d_roi = float(diag.get("roi", 0.0))
            b_roi = float(base_short.get("roi", 0.0))
            d_nt = int(diag.get("num_trades", 0))
            b_nt = int(base_short.get("num_trades", 0))
            ok = (abs(d_roi - b_roi) < 1e-9) and (d_nt == b_nt)
            print("-" * 60)
            print(f"SANITY (fee=0): DIAG vs BASE match: {ok}")
            print(f"  BASE roi={b_roi:+0.10f} trades={b_nt}")
            print(f"  DIAG roi={d_roi:+0.10f} trades={d_nt}")

    print("=" * 60)
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


