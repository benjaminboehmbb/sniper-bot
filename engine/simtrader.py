# scripts/simtrader.py
# Einfache, performante Evaluierung für LONG/SHORT (default Fokus: SHORT).
# - Lädt Kursdaten einmal (Cache)
# - Z-standardisiert die Signalsäulen (Cache)
# - Bildet Score = Summe(gewicht_i * zsignal_i)
# - SHORT: Entry wenn Score > enter_z (Standard 1.0), Exit wenn Score < exit_z (0.0),
#          oder TP/SL, oder max_hold Bars erreicht.
# - Gibt ein dict zurück: roi, num_trades, winrate, sharpe, etc.

import os, yaml, numpy as np, pandas as pd
from typing import Dict, Any, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")

# ---- Konfig lesen (nur einmal) ----
def _load_cfg() -> Dict[str, Any]:
    try:
        with open(CFG_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return cfg
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

# ---- Daten- & ZScore-Cache ----
_DF: pd.DataFrame | None = None
_Z: Dict[str, np.ndarray] = {}
_CLOSE: np.ndarray | None = None

SIGNALS = ["rsi","macd","bollinger","ma200","stoch","atr","ema50"]

def _csv_path() -> str:
    data = _CFG.get("data", {}) if isinstance(_CFG, dict) else {}
    path = data.get("csv_path") or data.get("price_csv") or "data/btcusdt_1m_spot.csv"
    return path if os.path.isabs(path) else os.path.join(ROOT, path)

def _get_df() -> pd.DataFrame:
    global _DF, _CLOSE
    if _DF is None:
        p = _csv_path()
        df = pd.read_csv(p)
        # Normalize price col names
        for c in ["close","high","low"]:
            if c not in df.columns and c.capitalize() in df.columns:
                df.rename(columns={c.capitalize(): c}, inplace=True)
        # Ensure needed columns
        for c in ["close","high","low"]:
            if c not in df.columns:
                raise ValueError(f"CSV fehlt Spalte '{c}'. Spalten={list(df.columns)[:25]}")
            df[c] = pd.to_numeric(df[c], errors="coerce")
        _DF = df
        _CLOSE = df["close"].to_numpy(dtype=float)
    return _DF

def _prep_zscores():
    global _Z
    if _Z:
        return
    df = _get_df()
    for s in SIGNALS:
        if s not in df.columns:
            # fehlende Signale als 0 (neutral)
            _Z[s] = np.zeros(len(df), dtype=float)
            continue
        x = pd.to_numeric(df[s], errors="coerce").astype(float).to_numpy()
        mu = np.nanmean(x)
        sd = np.nanstd(x)
        if sd == 0 or np.isnan(sd):
            z = np.zeros_like(x, dtype=float)
        else:
            z = (x - mu) / sd
            z[np.isnan(z)] = 0.0
        _Z[s] = z

# ---- Utility ----
def _sharpe_from_rets(rets: np.ndarray, eps: float = 1e-12) -> float:
    if rets.size == 0:
        return 0.0
    mu = rets.mean()
    sd = rets.std()
    return float(0.0 if sd < eps else (mu / sd) * np.sqrt(252*24*60))  # 1m Bars -> annualisiert grob

# ---- Kernlogik ----
def _simulate_short(score: np.ndarray,
                    close: np.ndarray,
                    tp: float,
                    sl: float,
                    max_hold: int,
                    enter_z: float,
                    exit_z: float) -> Dict[str, Any]:
    """
    Einfache Short-Logik:
      - Entry wenn score > enter_z
      - Exit wenn score < exit_z oder TP/SL erreicht oder max_hold Bars
      - 1 Stück pro Trade; Rendite = -(close_exit - close_entry)/close_entry
    """
    n = len(score)
    entries = score > enter_z
    i = 0
    returns = []
    wins = 0
    num = 0
    while i < n:
        if not entries[i]:
            i += 1
            continue
        entry_i = i
        entry_px = close[i]
        j = i + 1
        exited = False
        while j < min(n, i + max_hold + 1):
            # live return (short): -(px_j - entry)/entry
            r = -(close[j] - entry_px) / entry_px
            # TP/SL Prüfungen
            if r >= tp:
                returns.append(r); wins += 1; num += 1; i = j + 1; exited = True; break
            if r <= -sl:
                returns.append(r); num += 1; i = j + 1; exited = True; break
            # Score Exit
            if score[j] < exit_z:
                returns.append(r); wins += int(r > 0); num += 1; i = j + 1; exited = True; break
            j += 1
        if not exited:
            # Force exit am letzten betrachteten Balken
            r = -(close[min(j-1, n-1)] - entry_px) / entry_px
            returns.append(r); wins += int(r > 0); num += 1
            i = j
    rets = np.array(returns, dtype=float) if returns else np.empty(0)
    roi = float(rets.sum()) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0
    sharpe = _sharpe_from_rets(rets)
    return {
        "roi": roi,
        "num_trades": int(num),
        "winrate": winrate,
        "sharpe": float(sharpe),
    }

def _simulate_long(score: np.ndarray,
                   close: np.ndarray,
                   tp: float,
                   sl: float,
                   max_hold: int,
                   enter_z: float,
                   exit_z: float) -> Dict[str, Any]:
    """
    Spiegelung für Long (falls gebraucht):
      - Entry wenn score < -enter_z
      - Exit wenn score > -exit_z oder TP/SL oder max_hold
      - Rendite (long): (close_exit - close_entry)/entry
    """
    n = len(score)
    entries = score < -enter_z
    i = 0
    returns = []
    wins = 0
    num = 0
    while i < n:
        if not entries[i]:
            i += 1
            continue
        entry_i = i
        entry_px = close[i]
        j = i + 1
        exited = False
        while j < min(n, i + max_hold + 1):
            r = (close[j] - entry_px) / entry_px
            if r >= tp:
                returns.append(r); wins += 1; num += 1; i = j + 1; exited = True; break
            if r <= -sl:
                returns.append(r); num += 1; i = j + 1; exited = True; break
            if score[j] > -exit_z:
                returns.append(r); wins += int(r > 0); num += 1; i = j + 1; exited = True; break
            j += 1
        if not exited:
            r = (close[min(j-1, n-1)] - entry_px) / entry_px
            returns.append(r); wins += int(r > 0); num += 1
            i = j
    rets = np.array(returns, dtype=float) if returns else np.empty(0)
    roi = float(rets.sum()) if rets.size else 0.0
    winrate = float(wins / num) if num else 0.0
    sharpe = _sharpe_from_rets(rets)
    return {
        "roi": roi,
        "num_trades": int(num),
        "winrate": winrate,
        "sharpe": float(sharpe),
    }

# ---- Öffentliche API ----
def evaluate_strategy(i: int, comb: Any, direction: str, df: pd.DataFrame | None = None) -> Dict[str, Any]:
    """
    i: Index der Strategie
    comb: dict oder str (weights je Signal)
    direction: 'short' | 'long' | 'both'
    df: optional bereits geladenes DataFrame
    return: dict mit Metriken
    """
    # comb normalisieren
    if isinstance(comb, str):
        try:
            import ast
            comb = ast.literal_eval(comb)
        except Exception:
            comb = {}

    # Daten + Zscores vorbereiten
    if df is not None:
        global _DF, _CLOSE, _Z
        _DF = df
        _CLOSE = df["close"].to_numpy(dtype=float)
        _Z = {}  # neu berechnen
    _prep_zscores()
    z = _Z
    close = _CLOSE

    # Score bilden
    # unbekannte Keys ignorieren; fehlen Signale -> z=0 => neutral
    score = np.zeros_like(close, dtype=float)
    if isinstance(comb, dict):
        for k, w in comb.items():
            try:
                weight = float(w)
            except Exception:
                continue
            if k in z:
                score += weight * z[k]

    # Parameter aus CFG mit Defaults
    tp = float(_cfg(["strategy","risk","take_profit_pct"], 0.04))
    sl = float(_cfg(["strategy","risk","stop_loss_pct"], 0.02))
    max_hold = int(_cfg(["strategy","max_hold_bars"], 1440))
    enter_z = float(_cfg(["strategy","enter_z"], 1.0))
    exit_z  = float(_cfg(["strategy","exit_z"], 0.0))

    if direction == "short":
        res = _simulate_short(score, close, tp, sl, max_hold, enter_z, exit_z)
    elif direction == "long":
        res = _simulate_long(score, close, tp, sl, max_hold, enter_z, exit_z)
    else:
        # both: separat berechnen und kombinieren
        res_s = _simulate_short(score, close, tp, sl, max_hold, enter_z, exit_z)
        res_l = _simulate_long(score, close, tp, sl, max_hold, enter_z, exit_z)
        res = {k: (res_s[k] + res_l[k] if isinstance(res_s[k], (int,float)) else res_s[k]) for k in res_s}

    res.update({
        "index": int(i),
        "direction": direction,
    })
    return res
