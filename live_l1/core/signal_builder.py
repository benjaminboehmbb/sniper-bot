#!/usr/bin/env python3
# live_l1/core/signal_builder.py
# Online GS-compatible 1m signal builder for Live L1.
# ASCII-only.

from __future__ import annotations

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = ["timestamp_utc", "open", "high", "low", "close", "volume"]

SIGNAL_COLUMNS = [
    "rsi_signal",
    "macd_signal",
    "bollinger_signal",
    "ma200_signal",
    "stoch_signal",
    "atr_signal",
    "ema50_signal",
    "adx_signal",
    "cci_signal",
    "mfi_signal",
    "obv_signal",
    "roc_signal",
]

MIN_ROWS = 1441


def _safe_ewm(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False, min_periods=span).mean()


def _to_signal_score(series: pd.Series, lo: float, hi: float) -> pd.Series:
    s = series.copy()
    s = s.clip(lower=lo, upper=hi)
    mid = (lo + hi) / 2.0
    half = (hi - lo) / 2.0
    if half == 0.0:
        half = 1.0
    return ((s - mid) / half).clip(-1.0, 1.0)


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


def _validate_input(df: pd.DataFrame, min_rows: int = MIN_ROWS) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise KeyError("Missing required columns: " + ",".join(missing))

    if len(df) < min_rows:
        raise ValueError(f"Need at least {min_rows} rows, got {len(df)}")


def _to_live_int(value: object) -> int:
    try:
        return int(float(value))
    except Exception:
        return 0


def build_signal_frame(df: pd.DataFrame) -> pd.DataFrame:
    _validate_input(df)

    out = df.copy()

    close = pd.to_numeric(out["close"], errors="coerce")
    high = pd.to_numeric(out["high"], errors="coerce")
    low = pd.to_numeric(out["low"], errors="coerce")
    volume = pd.to_numeric(out["volume"], errors="coerce").fillna(0.0)

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

    ma_rel = (close - ma200) / ma200.replace(0.0, np.nan)
    ema_rel = (close - ema50) / ema50.replace(0.0, np.nan)
    atr_rel = atr_v / close.replace(0.0, np.nan)
    obv_roc = (obv_v - obv_v.shift(50)) / obv_v.shift(50).replace(0.0, np.nan)

    out["rsi_signal"] = _to_signal_score(rsi_v, 0.0, 100.0)
    out["macd_signal"] = _to_signal_score(macd_h, -1.0, 1.0)
    out["bollinger_signal"] = _to_signal_score(boll_z, -3.0, 3.0)
    out["ma200_signal"] = _to_signal_score(ma_rel, -0.2, 0.2)
    out["stoch_signal"] = _to_signal_score(stoch_v, 0.0, 100.0)
    out["atr_signal"] = -_to_signal_score(atr_rel, 0.0, 0.05)
    out["ema50_signal"] = _to_signal_score(ema_rel, -0.1, 0.1)
    out["adx_signal"] = _to_signal_score(adx_v, 0.0, 60.0)
    out["cci_signal"] = _to_signal_score(cci_v, -200.0, 200.0)
    out["mfi_signal"] = _to_signal_score(mfi_v, 0.0, 100.0)
    out["obv_signal"] = _to_signal_score(obv_roc, -0.2, 0.2)
    out["roc_signal"] = _to_signal_score(roc_v, -10.0, 10.0)

    return out


def build_online_signals(df: pd.DataFrame) -> dict[str, int]:
    frame = build_signal_frame(df)
    last = frame.iloc[-1]

    return {col: _to_live_int(last.get(col, 0)) for col in SIGNAL_COLUMNS}
