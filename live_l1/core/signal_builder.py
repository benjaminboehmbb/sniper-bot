#!/usr/bin/env python3
# live_l1/core/signal_builder.py
# Online 1m signal builder for Live L1.
# ASCII-only.

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["timestamp_utc", "open", "high", "low", "close", "volume"]

SIGNAL_KEYS = [
    "rsi_signal",
    "bollinger_signal",
    "stoch_signal",
    "cci_signal",
    "ma200_signal",
    "mfi_signal",
    "atr_signal",
    "macd_signal",
    "ema50_signal",
    "adx_signal",
    "obv_signal",
    "roc_signal",
]

MIN_ROWS = 1441


def _safe_ewm(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def _to_int_signal(value: Any, threshold_pos: float = 0.0, threshold_neg: float = 0.0) -> int:
    try:
        v = float(value)
    except Exception:
        return 0
    if not np.isfinite(v):
        return 0
    if v > threshold_pos:
        return 1
    if v < threshold_neg:
        return -1
    return 0


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def _macd_hist(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.Series:
    ema_fast = _safe_ewm(close, fast)
    ema_slow = _safe_ewm(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = _safe_ewm(macd_line, signal)
    return macd_line - signal_line


def _bollinger_z(close: pd.Series, period: int = 20) -> pd.Series:
    ma = close.rolling(period, min_periods=period).mean()
    sd = close.rolling(period, min_periods=period).std(ddof=0)
    return (close - ma) / sd.replace(0.0, np.nan)


def _atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def _stoch_k(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    ll = low.rolling(period, min_periods=period).min()
    hh = high.rolling(period, min_periods=period).max()
    return 100.0 * (close - ll) / (hh - ll).replace(0.0, np.nan)


def _cci(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> pd.Series:
    tp = (high + low + close) / 3.0
    sma = tp.rolling(period, min_periods=period).mean()
    mad = (tp - sma).abs().rolling(period, min_periods=period).mean()
    return (tp - sma) / (0.015 * mad.replace(0.0, np.nan))


def _roc(close: pd.Series, period: int = 12) -> pd.Series:
    prev = close.shift(period)
    return (close - prev) / prev.replace(0.0, np.nan) * 100.0


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff()).fillna(0.0)
    return (direction * volume).cumsum()


def _mfi(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    volume: pd.Series,
    period: int = 14,
) -> pd.Series:
    tp = (high + low + close) / 3.0
    mf = tp * volume
    pos = mf.where(tp.diff() > 0.0, 0.0)
    neg = mf.where(tp.diff() < 0.0, 0.0).abs()
    pos_sum = pos.rolling(period, min_periods=period).sum()
    neg_sum = neg.rolling(period, min_periods=period).sum()
    mr = pos_sum / neg_sum.replace(0.0, np.nan)
    return 100.0 - (100.0 / (1.0 + mr))


def _adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    up = high.diff()
    dn = -low.diff()

    plus_dm = up.where((up > dn) & (up > 0.0), 0.0)
    minus_dm = dn.where((dn > up) & (dn > 0.0), 0.0)

    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr_v = tr.rolling(period, min_periods=period).mean()
    plus_di = 100.0 * (plus_dm.rolling(period, min_periods=period).mean() / atr_v.replace(0.0, np.nan))
    minus_di = 100.0 * (minus_dm.rolling(period, min_periods=period).mean() / atr_v.replace(0.0, np.nan))
    dx = 100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0.0, np.nan)
    return dx.rolling(period, min_periods=period).mean()


def _validate_input(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise KeyError("Missing required columns: " + ",".join(missing))

    if len(df) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} rows, got {len(df)}")


def build_online_signals(df: pd.DataFrame, include_debug: bool = False) -> dict:
    _validate_input(df)

    work = df.copy()

    close = pd.to_numeric(work["close"], errors="coerce")
    high = pd.to_numeric(work["high"], errors="coerce")
    low = pd.to_numeric(work["low"], errors="coerce")
    volume = pd.to_numeric(work["volume"], errors="coerce").fillna(0.0)

    if close.isna().any() or high.isna().any() or low.isna().any():
        raise ValueError("NaN detected in OHLC after numeric conversion")

    rsi_v = _rsi(close, 14)
    macd_h = _macd_hist(close)
    boll_z = _bollinger_z(close, 20)
    ma200 = close.rolling(200, min_periods=200).mean()
    ema50 = _safe_ewm(close, 50)
    stoch_v = _stoch_k(high, low, close, 14)
    atr_v = _atr(high, low, close, 14)
    cci_v = _cci(high, low, close, 20)
    roc_v = _roc(close, 12)
    obv_v = _obv(close, volume)
    mfi_v = _mfi(high, low, close, volume, 14)
    adx_v = _adx(high, low, close, 14)

    last_close = float(close.iloc[-1])
    last_ma200 = float(ma200.iloc[-1]) if np.isfinite(ma200.iloc[-1]) else np.nan
    last_ema50 = float(ema50.iloc[-1]) if np.isfinite(ema50.iloc[-1]) else np.nan
    last_atr_rel = float(atr_v.iloc[-1] / last_close) if last_close > 0.0 and np.isfinite(atr_v.iloc[-1]) else np.nan
    last_obv_delta = float(obv_v.diff().iloc[-1]) if len(obv_v) >= 2 and np.isfinite(obv_v.diff().iloc[-1]) else 0.0

    out = {
        "rsi_signal": 1 if float(rsi_v.iloc[-1]) < 30.0 else (-1 if float(rsi_v.iloc[-1]) > 70.0 else 0),
        "bollinger_signal": 1 if float(boll_z.iloc[-1]) < -2.0 else (-1 if float(boll_z.iloc[-1]) > 2.0 else 0),
        "stoch_signal": 1 if float(stoch_v.iloc[-1]) < 20.0 else (-1 if float(stoch_v.iloc[-1]) > 80.0 else 0),
        "cci_signal": 1 if float(cci_v.iloc[-1]) < -100.0 else (-1 if float(cci_v.iloc[-1]) > 100.0 else 0),
        "ma200_signal": 1 if last_close > last_ma200 else (-1 if last_close < last_ma200 else 0),
        "mfi_signal": 1 if float(mfi_v.iloc[-1]) < 20.0 else (-1 if float(mfi_v.iloc[-1]) > 80.0 else 0),
        "atr_signal": -1 if np.isfinite(last_atr_rel) and last_atr_rel > 0.05 else 0,
        "macd_signal": _to_int_signal(macd_h.iloc[-1]),
        "ema50_signal": 1 if last_close > last_ema50 else (-1 if last_close < last_ema50 else 0),
        "adx_signal": 1 if float(adx_v.iloc[-1]) >= 20.0 else 0,
        "obv_signal": _to_int_signal(last_obv_delta),
        "roc_signal": _to_int_signal(roc_v.iloc[-1]),
    }

    if include_debug:
        out.update(
            {
                "rsi": float(rsi_v.iloc[-1]) if np.isfinite(rsi_v.iloc[-1]) else np.nan,
                "bollinger_z": float(boll_z.iloc[-1]) if np.isfinite(boll_z.iloc[-1]) else np.nan,
                "stoch_k": float(stoch_v.iloc[-1]) if np.isfinite(stoch_v.iloc[-1]) else np.nan,
                "cci": float(cci_v.iloc[-1]) if np.isfinite(cci_v.iloc[-1]) else np.nan,
                "ma200": last_ma200,
                "mfi": float(mfi_v.iloc[-1]) if np.isfinite(mfi_v.iloc[-1]) else np.nan,
                "atr": float(atr_v.iloc[-1]) if np.isfinite(atr_v.iloc[-1]) else np.nan,
                "macd_hist": float(macd_h.iloc[-1]) if np.isfinite(macd_h.iloc[-1]) else np.nan,
                "ema50": last_ema50,
                "adx": float(adx_v.iloc[-1]) if np.isfinite(adx_v.iloc[-1]) else np.nan,
                "obv": float(obv_v.iloc[-1]) if np.isfinite(obv_v.iloc[-1]) else np.nan,
                "roc": float(roc_v.iloc[-1]) if np.isfinite(roc_v.iloc[-1]) else np.nan,
            }
        )

    return out
