# engine/simtrader.py
# Einfacher, performanter Evaluator fuer LONG/SHORT auf Basis der *_signal-Spalten.
# - Erwartet im DataFrame: close und *_signal-Spalten (diskret -1/0/1)
# - Score = Summe(weight_i * signal_i)
# - SHORT: Entry score > enter_z | Exit score < exit_z | TP/SL | max_hold
# - LONG:  Entry score > enter_z | Exit score < exit_z | TP/SL | max_hold
# - Rueckgabe: dict mit roi, num_trades, winrate, sharpe (keine Trades-Liste)
#
# PERFORMANCE-FIX (WICHTIG):
# - Vorher wurde bei jedem evaluate_strategy(df, ...) _set_df(df) aufgerufen, und _set_df setzte _SIG = {}.
#   Dadurch wurden Signal-Arrays praktisch pro Strategie neu aufgebaut.
# - Jetzt: DF/Signals werden pro Worker gecached. _SIG wird nur invalidiert, wenn sich df wirklich aendert.
#
from __future__ import annotations

import os
from typing import Dict, Any, List

import numpy as np
np.seterr(divide="ignore", invalid="ignore", over="ignore", under="ignore")
import pandas as pd


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))

# ------------------------------------------------------------
# Config (minimal)
# ------------------------------------------------------------
_CFG: Dict[str, Any] = {
    "data": {"csv_path": "data/price_data_with_signals.csv"},
    "strategy": {
        "risk": {"take_profit_pct": 0.04, "stop_loss_pct": 0.02},
        "max_hold_bars": 1440,
        "enter_z": 1.0,
        "exit_z": 0.0,
    },
}


def _cfg(keys: List[str], default: Any) -> Any:
    cur: Any = _CFG
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


# ------------------------------------------------------------
# Caches
# ------------------------------------------------------------
_DF: pd.DataFrame | None = None
_CLOSE: np.ndarray | None = None
_SIG: Dict[str, np.ndarray] = {}
_DF_ID: int | None = None  # identity of currently cached df (for per-worker caching)

# *** WICHTIG: Alle 12 Signale abdecken ***
SIGNALS = [
    "rsi_signal", "macd_signal", "bollinger_signal",
    "ma200_signal", "stoch_signal", "atr_signal", "ema50_signal",
    "adx_signal", "cci_signal", "mfi_signal", "obv_signal", "roc_signal",
]

# Kurzschluessel -> *_signal Spalten
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


def _csv_path() -> str:
    data = _CFG.get("data", {}) if isinstance(_CFG, dict) else {}
    path = data.get("csv_path") or data.get("price_csv") or "data/btcusdt_1m_spot.csv"
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def _finite_array(a: np.ndarray, fill: float = 0.0) -> np.ndarray:
    if not isinstance(a, np.ndarray):
        a = np.asarray(a, dtype=float)
    return np.nan_to_num(a.astype(float), nan=fill, posinf=fill, neginf=fill)


def _set_df(df: pd.DataFrame) -> None:
    global _DF, _CLOSE, _SIG, _DF_ID
    df_id = id(df)
    if _DF is df and _DF_ID == df_id and _CLOSE is not None:
        return
    _DF = df
    _DF_ID = df_id
    _CLOSE = None
    _SIG = {}


def _ensure_df_loaded() -> None:
    global _DF
    if _DF is not None:
        return
    path = _csv_path()
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Price CSV not found: {path}")
    _set_df(pd.read_csv(path))


def _prep_signals() -> None:
    global _DF, _CLOSE, _SIG
    if _DF is None:
        _ensure_df_loaded()
    assert _DF is not None

    if _CLOSE is None:
        if "close" not in _DF.columns:
            raise ValueError(f"price_df missing required column 'close'. columns={list(_DF.columns)}")
        _CLOSE = _finite_array(_DF["close"].to_numpy(dtype=float), fill=0.0)

    if _SIG:
        return

    for col in SIGNALS:
        if col in _DF.columns:
            arr = _finite_array(_DF[col].to_numpy(dtype=float), fill=0.0)
            # (optional) normalize to -1/0/1 if someone wrote floats
            arr = np.where(arr > 0.0, 1.0, np.where(arr < 0.0, -1.0, 0.0)).astype(float)
            _SIG[col] = arr


def _sharpe_from_rets(rets: np.ndarray) -> float:
    if rets.size < 2:
        return 0.0
    mu = float(np.mean(rets))
    sd = float(np.std(rets))
    if not np.isfinite(sd) or sd <= 1e-12:
        return 0.0
    return mu / sd


def _simulate_short(score: np.ndarray, close: np.ndarray, tp: float, sl: float,
                    max_hold: int, enter_z: float, exit_z: float) -> Dict[str, Any]:
    n = score.shape[0]
    entries = score > enter_z
    i = 0
    returns = []
    wins = 0
    num = 0
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
                returns.append(r); wins += 1; num += 1; i = j + 1; exited = True; break
            if r <= -sl:
                returns.append(r); num += 1; i = j + 1; exited = True; break
            if score[j] < exit_z:
                returns.append(r); wins += int(r > 0); num += 1; i = j + 1; exited = True; break
            j += 1
        if not exited:
            j = j_end - 1
            r = (entry_px - close[j]) / entry_px
            if not np.isfinite(r):
                r = 0.0
            returns.append(r); wins += int(r > 0); num += 1
            i = j_end
    rets = np.array(returns, dtype=float) if returns else np.empty(0)
    if rets.size:
        rets = _finite_array(rets, fill=0.0)
    roi = float(rets.sum()) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0
    sharpe = _sharpe_from_rets(rets)
    return {"roi": roi, "num_trades": int(num), "winrate": winrate, "sharpe": sharpe}


def _simulate_long(score: np.ndarray, close: np.ndarray, tp: float, sl: float,
                   max_hold: int, enter_z: float, exit_z: float) -> Dict[str, Any]:
    n = score.shape[0]
    entries = score > enter_z
    i = 0
    returns = []
    wins = 0
    num = 0
    while i < n:
        if not entries[i]:
            i += 1
            continue
        entry_px = close[i]
        j = i + 1
        exited = False
        j_end = min(n, i + max_hold + 1)
        while j < j_end:
            r = (close[j] - entry_px) / entry_px
            if not np.isfinite(r):
                r = 0.0
            if r >= tp:
                returns.append(r); wins += 1; num += 1; i = j + 1; exited = True; break
            if r <= -sl:
                returns.append(r); num += 1; i = j + 1; exited = True; break
            if score[j] < exit_z:
                returns.append(r); wins += int(r > 0); num += 1; i = j + 1; exited = True; break
            j += 1
        if not exited:
            j = j_end - 1
            r = (close[j] - entry_px) / entry_px
            if not np.isfinite(r):
                r = 0.0
            returns.append(r); wins += int(r > 0); num += 1
            i = j_end
    rets = np.array(returns, dtype=float) if returns else np.empty(0)
    if rets.size:
        rets = _finite_array(rets, fill=0.0)
    roi = float(rets.sum()) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0
    sharpe = _sharpe_from_rets(rets)
    return {"roi": roi, "num_trades": int(num), "winrate": winrate, "sharpe": sharpe}


def _eval_core(comb: Any, direction: str, df: pd.DataFrame | None = None) -> Dict[str, Any]:
    # Kombination parsen
    if isinstance(comb, str):
        try:
            import ast
            comb = ast.literal_eval(comb)
        except Exception:
            comb = {}

    # DF setzen / laden
    if df is not None:
        _set_df(df)
    else:
        _ensure_df_loaded()

    # Signals vorbereiten
    _prep_signals()
    z = _SIG
    close = _CLOSE
    assert close is not None

    # Score bilden
    score = np.zeros_like(close, dtype=float)
    if isinstance(comb, dict):
        for k, w in comb.items():
            col = KEYMAP.get(k, k)
            if col in z:
                try:
                    weight = float(w)
                except Exception:
                    continue
                score += weight * z[col]
    score = _finite_array(score, fill=0.0)

    # Parameter
    tp = float(_cfg(["strategy", "risk", "take_profit_pct"], 0.04))
    sl = float(_cfg(["strategy", "risk", "stop_loss_pct"], 0.02))
    max_hold = int(_cfg(["strategy", "max_hold_bars"], 1440))
    enter_z = float(_cfg(["strategy", "enter_z"], 1.0))
    exit_z = float(_cfg(["strategy", "exit_z"], 0.0))

    # Richtung
    direction = str(direction).lower().strip()
    if direction == "short":
        res = _simulate_short(score, close, tp, sl, max_hold, enter_z, exit_z)
    elif direction == "long":
        res = _simulate_long(score, close, tp, sl, max_hold, enter_z, exit_z)
    else:
        raise ValueError("direction must be 'long' or 'short'")

    # pnl_sum ist identisch zu roi (Summe der Trade-Returns)
    res["pnl_sum"] = float(res.get("roi", 0.0))

    # sanitize numerics
    for k in ("roi", "winrate", "sharpe", "pnl_sum"):
        v = res.get(k, 0.0)
        if not isinstance(v, (int, float)) or not np.isfinite(float(v)):
            res[k] = 0.0
        else:
            res[k] = float(v)

    res["num_trades"] = int(res.get("num_trades", 0) or 0)

    # avg_trade (billig, aus vorhandenen Werten)
    nt = res["num_trades"]
    ps = res["pnl_sum"]
    res["avg_trade"] = float(ps / nt) if nt else 0.0

    return res


def evaluate_strategy(price_df: pd.DataFrame, comb: Any, direction: str) -> Dict[str, Any]:
    """Goldstandard evaluator (Contract v1).

    Contract (verbindlich):
      evaluate_strategy(price_df, comb, direction)

    - price_df: DataFrame mit mindestens 'close' sowie *_signal-Spalten (diskret -1/0/1).
    - comb: dict (oder String-Dict), Keys sind Kurz-Keys (z.B. 'rsi') oder bereits '*_signal'.
    - direction: 'long' oder 'short'

    Rueckgabe: dict mit mindestens roi, num_trades, winrate, sharpe (optional weitere Kennzahlen).
    """
    if not isinstance(price_df, pd.DataFrame):
        raise TypeError("price_df must be a pandas DataFrame")

    if "close" not in price_df.columns:
        raise ValueError(f"price_df missing required column 'close'. columns={list(price_df.columns)}")

    d = str(direction).lower().strip()
    if d not in ("long", "short"):
        raise ValueError("direction must be 'long' or 'short'")

    return _eval_core(comb=comb, direction=d, df=price_df)
