#!/usr/bin/env python3
# scripts/post_gs_h3_build_eth_signals_regime_gs_compat.py
#
# Build ETHUSDT 1m GS-compatible input with:
# - 12 signal columns (adx, atr, bollinger, cci, ema50, ma200, macd, mfi, obv, roc, rsi, stoch)
# - regime_v1
# - allow_long_old / allow_short_old (placeholder compatibility, conservative)
# - allow_long / allow_short via asymmetric gate (simple, deterministic)
#
# Input:
#   data/ethusdt_1m_postGS/normalized/ethusdt_1m_price_2017_2025_POSTGS_RAWONLY_FIXED_UTC_MINUTE_*.csv
#
# Output:
#   data/ethusdt_1m_postGS/simtraderGS/ethusdt_1m_price_2017_2025_GS_COMPAT_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv
#
# Notes:
# - This does NOT touch engine/simtraderGS.py (Post-GS layer only).
# - ASCII-only logs/prints.

import os
import sys
import glob
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

IN_GLOB = str(REPO_ROOT / "data" / "ethusdt_1m_postGS" / "normalized" / "ethusdt_1m_price_2017_2025_POSTGS_RAWONLY_FIXED_UTC_MINUTE_*.csv")
OUT_DIR = REPO_ROOT / "data" / "ethusdt_1m_postGS" / "simtraderGS"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_CSV = OUT_DIR / "ethusdt_1m_price_2017_2025_GS_COMPAT_WITH_SIGNALS_REGIMEV1_ASYMGATE.csv"

LOG_DIR = REPO_ROOT / "results" / "POST_GS" / "H3_asset" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------
# helpers
# ---------------------------

def now_ts():
    return datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

def die(msg, code=2):
    print(f"[FATAL] {msg}")
    sys.exit(code)

def safe_ewm(series, span):
    return series.ewm(span=span, adjust=False, min_periods=span).mean()

def rsi(close, period=14):
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean()
    rs = avg_gain / (avg_loss.replace(0.0, np.nan))
    out = 100.0 - (100.0 / (1.0 + rs))
    return out

def macd_hist(close, fast=12, slow=26, signal=9):
    ema_fast = safe_ewm(close, fast)
    ema_slow = safe_ewm(close, slow)
    macd_line = ema_fast - ema_slow
    signal_line = safe_ewm(macd_line, signal)
    hist = macd_line - signal_line
    return hist

def bollinger_z(close, period=20, k=2.0):
    ma = close.rolling(period, min_periods=period).mean()
    sd = close.rolling(period, min_periods=period).std(ddof=0)
    upper = ma + k * sd
    lower = ma - k * sd
    # z-score relative to middle band (avoid div0)
    z = (close - ma) / (sd.replace(0.0, np.nan))
    return z, upper, lower

def atr(high, low, close, period=14):
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()

def stoch_k(high, low, close, k_period=14):
    ll = low.rolling(k_period, min_periods=k_period).min()
    hh = high.rolling(k_period, min_periods=k_period).max()
    k = 100.0 * (close - ll) / ((hh - ll).replace(0.0, np.nan))
    return k

def cci(high, low, close, period=20):
    tp = (high + low + close) / 3.0
    sma = tp.rolling(period, min_periods=period).mean()
    mad = (tp - sma).abs().rolling(period, min_periods=period).mean()
    out = (tp - sma) / (0.015 * (mad.replace(0.0, np.nan)))
    return out

def roc(close, period=12):
    prev = close.shift(period)
    return (close - prev) / (prev.replace(0.0, np.nan)) * 100.0

def obv(close, volume):
    direction = np.sign(close.diff()).fillna(0.0)
    return (direction * volume).cumsum()

def mfi(high, low, close, volume, period=14):
    tp = (high + low + close) / 3.0
    mf = tp * volume
    pos = mf.where(tp.diff() > 0.0, 0.0)
    neg = mf.where(tp.diff() < 0.0, 0.0).abs()
    pos_sum = pos.rolling(period, min_periods=period).sum()
    neg_sum = neg.rolling(period, min_periods=period).sum()
    mr = pos_sum / (neg_sum.replace(0.0, np.nan))
    out = 100.0 - (100.0 / (1.0 + mr))
    return out

def adx(high, low, close, period=14):
    # Wilder's ADX (simplified rolling variant, deterministic)
    up = high.diff()
    dn = -low.diff()
    plus_dm = up.where((up > dn) & (up > 0), 0.0)
    minus_dm = dn.where((dn > up) & (dn > 0), 0.0)

    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low).abs(),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)

    atr_v = tr.rolling(period, min_periods=period).mean()
    plus_di = 100.0 * (plus_dm.rolling(period, min_periods=period).mean() / atr_v.replace(0.0, np.nan))
    minus_di = 100.0 * (minus_dm.rolling(period, min_periods=period).mean() / atr_v.replace(0.0, np.nan))
    dx = (100.0 * (plus_di - minus_di).abs() / ((plus_di + minus_di).replace(0.0, np.nan)))
    adx_v = dx.rolling(period, min_periods=period).mean()
    return adx_v

def to_signal_score(series, lo, hi):
    # Map indicator to [-1, +1] via clipping and linear scaling around 0
    s = series.copy()
    s = s.clip(lower=lo, upper=hi)
    mid = (lo + hi) / 2.0
    half = (hi - lo) / 2.0
    out = (s - mid) / (half if half != 0 else 1.0)
    return out.clip(-1.0, 1.0)

def load_input_latest():
    files = sorted(glob.glob(IN_GLOB))
    if not files:
        die(f"No input matched: {IN_GLOB}")
    # latest by filename timestamp
    inp = files[-1]
    print(f"[load] input: {inp}")
    return inp, pd.read_csv(inp)

# ---------------------------
# main build
# ---------------------------

def main():
    run_id = now_ts()
    inp_path, df = load_input_latest()

    required = ["timestamp_utc","open","high","low","close","volume"]
    for c in required:
        if c not in df.columns:
            die(f"Missing required col: {c}")

    # Parse timestamp
    ts = pd.to_datetime(df["timestamp_utc"], utc=True, errors="raise", format="mixed")
    if (ts.dt.second != 0).any():
        die("timestamp_utc not minute-aligned; run the FIX script first.")

    # Ensure monotonic
    if not ts.is_monotonic_increasing:
        die("timestamp_utc not monotonic increasing")

    close = pd.to_numeric(df["close"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low  = pd.to_numeric(df["low"], errors="coerce")
    vol  = pd.to_numeric(df["volume"], errors="coerce").fillna(0.0)

    if close.isna().any() or high.isna().any() or low.isna().any():
        die("NaNs in OHLC after numeric coercion")

    # --- Indicators
    rsi_v = rsi(close, 14)
    macd_h = macd_hist(close)
    boll_z, _, _ = bollinger_z(close, 20, 2.0)
    ma200 = close.rolling(200, min_periods=200).mean()
    ema50 = safe_ewm(close, 50)
    stoch_v = stoch_k(high, low, close, 14)
    atr_v = atr(high, low, close, 14)
    cci_v = cci(high, low, close, 20)
    roc_v = roc(close, 12)
    obv_v = obv(close, vol)
    mfi_v = mfi(high, low, close, vol, 14)
    adx_v = adx(high, low, close, 14)

    # --- Signals in [-1, +1]
    # These bounds are conservative and deterministic, not fitted.
    df["rsi_signal"] = to_signal_score(rsi_v, 0.0, 100.0) * 1.0
    df["macd_signal"] = to_signal_score(macd_h, -1.0, 1.0)
    df["bollinger_signal"] = to_signal_score(boll_z, -3.0, 3.0)

    # MA200 signal: (close - ma200)/ma200 clipped
    ma_rel = (close - ma200) / (ma200.replace(0.0, np.nan))
    df["ma200_signal"] = to_signal_score(ma_rel, -0.2, 0.2)

    # Stoch: scale 0..100
    df["stoch_signal"] = to_signal_score(stoch_v, 0.0, 100.0)

    # ATR signal: volatility proxy (atr/close), higher vol -> negative (conservative)
    atr_rel = atr_v / (close.replace(0.0, np.nan))
    df["atr_signal"] = -to_signal_score(atr_rel, 0.0, 0.05)

    # EMA50 signal: (close-ema)/ema
    ema_rel = (close - ema50) / (ema50.replace(0.0, np.nan))
    df["ema50_signal"] = to_signal_score(ema_rel, -0.1, 0.1)

    # ADX signal: 0..60 typical
    df["adx_signal"] = to_signal_score(adx_v, 0.0, 60.0)

    # CCI: typically -200..200
    df["cci_signal"] = to_signal_score(cci_v, -200.0, 200.0)

    # MFI: 0..100
    df["mfi_signal"] = to_signal_score(mfi_v, 0.0, 100.0)

    # OBV: use rate of change over 50 to normalize
    obv_roc = (obv_v - obv_v.shift(50)) / (obv_v.shift(50).replace(0.0, np.nan))
    df["obv_signal"] = to_signal_score(obv_roc, -0.2, 0.2)

    # ROC: percent
    df["roc_signal"] = to_signal_score(roc_v, -10.0, 10.0)

    # --- Regime v1 (simple trend regime based on MA200 slope)
    # regime_v1:
    #   1 = bull, 0 = side, -1 = bear
    ma200_slope = ma200.diff(1440)  # 1 day slope in 1m
    bull = (close > ma200) & (ma200_slope > 0)
    bear = (close < ma200) & (ma200_slope < 0)
    regime = pd.Series(0, index=df.index, dtype="int64")
    regime[bull.fillna(False)] = 1
    regime[bear.fillna(False)] = -1
    df["regime_v1"] = regime

    # allow_* gates
    # old gates: keep as raw regime-based allow (compat placeholders)
    df["allow_long_old"] = (df["regime_v1"] >= 0).astype("int64")
    df["allow_short_old"] = (df["regime_v1"] <= 0).astype("int64")

    # asymmetric gate: conservative
    # long allowed in bull + side when ADX not extreme low
    # short allowed in bear only when ADX above threshold
    adx_thr_long = 15.0
    adx_thr_short = 20.0
    df["allow_long"] = ((df["regime_v1"] >= 0) & (adx_v.fillna(0.0) >= adx_thr_long)).astype("int64")
    df["allow_short"] = ((df["regime_v1"] == -1) & (adx_v.fillna(0.0) >= adx_thr_short)).astype("int64")

    # Final column order EXACT as BTC GS input
    out_cols = [
        "timestamp_utc","open","high","low","close","volume",
        "rsi_signal","macd_signal","bollinger_signal","ma200_signal","stoch_signal","atr_signal","ema50_signal",
        "adx_signal","cci_signal","mfi_signal","obv_signal","roc_signal",
        "regime_v1","allow_long_old","allow_short_old","allow_long","allow_short"
    ]
    for c in out_cols:
        if c not in df.columns:
            die(f"Missing output column: {c}")

    out = df[out_cols].copy()

    # Drop rows with any NaN in signals/regime (warm-up periods)
    before = len(out)
    out = out.dropna()
    dropped = before - len(out)

    out.to_csv(OUT_CSV, index=False)

    mf = {
        "utc_written": datetime.utcnow().isoformat(timespec="seconds"),
        "input_csv": inp_path,
        "output_csv": str(OUT_CSV),
        "rows_in": int(before),
        "rows_out": int(len(out)),
        "rows_dropped_warmup": int(dropped),
        "notes": "GS-compatible ETH build with 23 columns; indicators computed locally; regime+asymgate conservative.",
    }
    mf_path = OUT_DIR / f"manifest_ethusdt_1m_GS_COMPAT_{run_id}.json"
    pd.Series(mf).to_json(mf_path, indent=2)

    print(f"[ok] wrote: {OUT_CSV}")
    print(f"[ok] rows_out={len(out)} dropped_warmup={dropped}")
    print(f"[ok] manifest: {mf_path}")

if __name__ == "__main__":
    main()
