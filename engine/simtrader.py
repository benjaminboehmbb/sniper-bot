# engine/simtrader.py
# Einfacher, performanter Evaluator fuer LONG/SHORT auf Basis der *_signal-Spalten.
# - Erwartet im DataFrame: close und *_signal-Spalten (diskret -1/0/1)
# - Score = Summe(weight_i * signal_i)
# - SHORT: Entry score > enter_z | Exit score < exit_z | TP/SL | max_hold
# - LONG:  Entry score < -enter_z | Exit score > -exit_z | TP/SL | max_hold
# - Rueckgabe: dict mit roi, num_trades, winrate, sharpe (keine Trades-Liste)
from __future__ import annotations
import os
from typing import Dict, Any, List
import numpy as np
np.seterr(divide="ignore", invalid="ignore", over="ignore", under="ignore")
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")
try:
    import yaml
except Exception:
    yaml = None

def _load_cfg() -> Dict[str, Any]:
    if yaml is None:
        return {}
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}
_CFG = _load_cfg()

def _cfg(path: List[str], default=None):
    cur = _CFG
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur

# ------------------------------------------------------------
# Caches
# ------------------------------------------------------------
_DF: pd.DataFrame | None = None
_CLOSE: np.ndarray | None = None
_SIG: Dict[str, np.ndarray] = {}

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
    global _DF, _CLOSE
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
    _CLOSE = _finite_array(df["close"].to_numpy(dtype=float), fill=0.0)

def _set_df(df: pd.DataFrame):
    global _DF, _CLOSE, _SIG
    if "close" not in df.columns:
        raise ValueError("DataFrame fehlt Spalte 'close'")
    df = df.copy()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    _DF = df
    _CLOSE = _finite_array(df["close"].to_numpy(dtype=float), fill=0.0)
    _SIG = {}

def _prep_signals():
    global _SIG
    if _SIG:
        return
    _ensure_df_loaded()
    df = _DF
    sig = {}
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
    return float(0.0 if sd < eps else (mu / sd) * np.sqrt(252*24*60))

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
            i += 1; continue
        entry_px = close[i]
        j = i + 1
        exited = False
        j_end = min(n, i + max_hold + 1)
        while j < j_end:
            r = -(close[j] - entry_px) / entry_px
            if not np.isfinite(r): r = 0.0
            if r >= tp:
                returns.append(r); wins += 1; num += 1; i = j + 1; exited = True; break
            if r <= -sl:
                returns.append(r); num += 1; i = j + 1; exited = True; break
            if score[j] < exit_z:
                returns.append(r); wins += int(r > 0); num += 1; i = j + 1; exited = True; break
            j += 1
        if not exited:
            r = -(close[j_end - 1] - entry_px) / entry_px
            if not np.isfinite(r): r = 0.0
            returns.append(r); wins += int(r > 0); num += 1
            i = j_end
    rets = np.array(returns, dtype=float) if returns else np.empty(0)
    if rets.size: rets = _finite_array(rets, fill=0.0)
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
            i += 1; continue
        entry_px = close[i]
        j = i + 1
        exited = False
        j_end = min(n, i + max_hold + 1)
        while j < j_end:
            r = (close[j] - entry_px) / entry_px
            if not np.isfinite(r): r = 0.0
            if r >= tp:
                returns.append(r); wins += 1; num += 1; i = j + 1; exited = True; break
            if r <= -sl:
                returns.append(r); num += 1; i = j + 1; exited = True; break
            if score[j] < exit_z:
                returns.append(r); wins += int(r > 0); num += 1; i = j + 1; exited = True; break
            j += 1
        if not exited:
            r = (close[j_end - 1] - entry_px) / entry_px
            if not np.isfinite(r): r = 0.0
            returns.append(r); wins += int(r > 0); num += 1
            i = j_end
    rets = np.array(returns, dtype=float) if returns else np.empty(0)
    if rets.size: rets = _finite_array(rets, fill=0.0)
    roi = float(rets.sum()) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0
    sharpe = _sharpe_from_rets(rets)
    return {"roi": roi, "num_trades": int(num), "winrate": winrate, "sharpe": sharpe}

def evaluate_strategy(i: int, comb: Any, direction: str, df: pd.DataFrame | None = None) -> Dict[str, Any]:
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
            # mappe "mfi" -> "mfi_signal", etc.
            col = KEYMAP.get(k, k)
            if col in z:
                try:
                    weight = float(w)
                except Exception:
                    continue
                score += weight * z[col]
    score = _finite_array(score, fill=0.0)

    # Parameter
    tp = float(_cfg(["strategy","risk","take_profit_pct"], 0.04))
    sl = float(_cfg(["strategy","risk","stop_loss_pct"], 0.02))
    max_hold = int(_cfg(["strategy","max_hold_bars"], 1440))
    enter_z = float(_cfg(["strategy","enter_z"], 1.0))
    exit_z  = float(_cfg(["strategy","exit_z"], 0.0))

    # Richtung
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

    res["pnl_sum"] = float(res.get("roi", 0.0))
    for k in ("roi", "winrate", "sharpe", "pnl_sum"):
        v = res.get(k, 0.0)
        if not isinstance(v, (int, float)) or not np.isfinite(float(v)):
            res[k] = 0.0
        else:
            res[k] = float(v)
    res["num_trades"] = int(res.get("num_trades", 0) or 0)
    return res

