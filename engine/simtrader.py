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


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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


def _ensure_df_loaded():
    global _DF, _CLOSE, _DF_ID
    if _DF is not None:
        return
    p = _csv_path()
    df = pd.read_csv(p)

    for c in ("close", "high", "low"):
        if c not in df.columns and c.capitalize() in df.columns:
            df.rename(columns={c.capitalize(): c}, inplace=True)

    for c in ("close", "high", "low"):
        if c not in df.columns:
            raise ValueError("CSV fehlt Spalte '{}'".format(c))
        df[c] = pd.to_numeric(df[c], errors="coerce")

    _DF = df
    _DF_ID = id(df)
    _CLOSE = _finite_array(df["close"].to_numpy(dtype=float), fill=0.0)


def _set_df(df: pd.DataFrame):
    """Set global DF only when it actually changed.

    PERFORMANCE-KRITISCH:
    - In der alten Version wurde _SIG bei jedem Aufruf geleert -> Signale pro Strategie neu gebaut.
    - Jetzt: DF/Signals werden pro Worker gecached. _SIG wird nur invalidiert, wenn df wirklich wechselt.
    """
    global _DF, _CLOSE, _SIG, _DF_ID

    if df is None:
        raise ValueError("df is None")

    # If the same object is re-used (typical in multiprocessing workers), do nothing.
    if _DF is df:
        return
    if _DF_ID is not None and id(df) == _DF_ID:
        return

    if "close" not in df.columns:
        raise ValueError("DataFrame fehlt Spalte 'close'")

    # Avoid expensive df.copy() per strategy.
    close_series = df["close"]
    if not pd.api.types.is_numeric_dtype(close_series):
        df = df.copy()
        df["close"] = pd.to_numeric(df["close"], errors="coerce")

    _DF = df
    _DF_ID = id(df)
    _CLOSE = _finite_array(df["close"].to_numpy(dtype=float), fill=0.0)

    # Invalidate signals ONLY because DF changed.
    _SIG = {}


def _prep_signals():
    global _SIG
    if _SIG:
        return
    _ensure_df_loaded()
    df = _DF
    sig: Dict[str, np.ndarray] = {}
    n = len(df)
    for col in SIGNALS:
        if col in df.columns:
            x = pd.to_numeric(df[col], errors="coerce").astype(float).to_numpy()
            x = _finite_array(x, fill=0.0)
        else:
            x = np.zeros(n, dtype=float)
        sig[col] = x
    _SIG = sig


def _sharpe_from_rets(rets: np.ndarray, eps: float = 1e-12) -> float:
    if rets.size == 0:
        return 0.0
    mu = rets.mean()
    sd = rets.std()
    return float(0.0 if sd < eps else (mu / sd) * np.sqrt(252 * 24 * 60))


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
            r = -(close[j] - entry_px) / entry_px
            if not np.isfinite(r):
                r = 0.0
            if r >= tp:
                returns.append(r); wins += 1; num += 1; i = j + 1; exited = True; break
            if r <= -sl:
                returns.append(r); wins += 0; num += 1; i = j + 1; exited = True; break
            if score[j] < exit_z:
                returns.append(r); wins += int(r > 0); num += 1; i = j + 1; exited = True; break
            j += 1
        if not exited:
            j = j_end - 1
            r = -(close[j] - entry_px) / entry_px
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
                returns.append(r); wins += 0; num += 1; i = j + 1; exited = True; break
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
        rs = _simulate_short(score, close, tp, sl, max_hold, enter_z, exit_z)
        rl = _simulate_long(score, close, tp, sl, max_hold, enter_z, exit_z)
        res = {
            "roi": float(rs["roi"] + rl["roi"]),
            "num_trades": int(rs["num_trades"] + rl["num_trades"]),
            "winrate": 0.0,
            "sharpe": float(rs["sharpe"] + rl["sharpe"]),
        }

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

    # *** NEU: avg_trade (billig, aus vorhandenen Werten) ***
    nt = res["num_trades"]
    ps = res["pnl_sum"]
    res["avg_trade"] = float(ps / nt) if nt else 0.0

    return res


def evaluate_strategy(*args, **kwargs) -> Dict[str, Any]:
    """
    Backward + forward compatible wrapper.

    Supported calls:
      A) evaluate_strategy(price_df, comb, side="short", ...)   (used by analyze scripts)
      B) evaluate_strategy(price_df, comb, direction="short", ...)
      C) old-style: evaluate_strategy(i, comb, direction, df=None)

    Notes:
      - If a DataFrame is provided, it is used. No internal CSV load is performed.
      - direction/side normalized to "short"/"long".
    """
    # New-style: (df, comb, ...)
    if len(args) >= 2 and isinstance(args[0], pd.DataFrame):
        df = args[0]
        comb = args[1]
        direction = kwargs.get("side") or kwargs.get("direction") or "short"
        direction = str(direction).lower().strip()
        if direction not in ("short", "long"):
            direction = "short"
        return _eval_core(comb=comb, direction=direction, df=df)

    # Old-style: (i, comb, direction, df=None)
    if len(args) >= 3 and isinstance(args[0], (int, np.integer)):
        comb = args[1]
        direction = str(args[2]).lower().strip()
        df = None
        if len(args) >= 4 and isinstance(args[3], pd.DataFrame):
            df = args[3]
        else:
            df = kwargs.get("df", None)
        return _eval_core(comb=comb, direction=direction, df=df)

    # Fallback via kwargs
    comb = kwargs.get("comb", {})
    direction = kwargs.get("direction") or kwargs.get("side") or "short"
    df = kwargs.get("df", None)
    return _eval_core(comb=comb, direction=str(direction), df=df)




