# -*- coding: utf-8 -*-
"""
Blueprint Analyse-Pipeline (vollständig)
- Liest:  data/btcusdt_1m_spot.csv
- Erzeugt: data/price_data_with_signals.csv (+ optional 5m/15m)
- Berechnet 14 Signale: 12 Kern + 2 Momentum (ema50_cross_ma200, rsi_derivative)
- Dependencies: pandas, numpy
"""
import os
from datetime import datetime, timezone
import numpy as np
import pandas as pd

# -------------------------- Pfade & Optionen --------------------------
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
IN_1M = os.path.join(DATA_DIR, "btcusdt_1m_spot.csv")
OUT_1M = os.path.join(DATA_DIR, "price_data_with_signals.csv")
OUT_5M = os.path.join(DATA_DIR, "price_data_with_signals_5m.csv")
OUT_15M= os.path.join(DATA_DIR, "price_data_with_signals_15m.csv")

MAKE_5M   = True
MAKE_15M  = True
BACKUP    = True

# Perioden
RSI_P=14; MACD_FAST=12; MACD_SLOW=26; MACD_SIG=9
BOLL_P=20; BOLL_K=2
MA200_P=200; EMA50_P=50; EMA200_P=200
STOCH_P=14; ATR_P=14; ADX_P=14; CCI_P=20; MFI_P=14

# Aliase
TIME_ALIASES  = ["timestamp","open_time","time","date","datetime"]
OPEN_ALIASES  = ["open"]
HIGH_ALIASES  = ["high"]
LOW_ALIASES   = ["low"]
CLOSE_ALIASES = ["close","price","last"]
VOL_ALIASES   = ["volume","vol","quote_volume"]

# -------------------------- Utils --------------------------
def _find_col(df, aliases, required=True, name=""):
    for c in aliases:
        if c in df.columns: return c
    if required:
        raise ValueError(f"Spalte nicht gefunden ({name or aliases}). Verfügbar: {list(df.columns)}")
    return None

def _to_utc_datetime(s):
    if np.issubdtype(s.dtype, np.number):
        s_int = s.astype("int64")
        unit = "ms" if s_int.max() > 10_000_000_000 else "s"
        return pd.to_datetime(s_int, unit=unit, utc=True)
    parsed = pd.to_datetime(s, utc=True, errors="coerce")
    return parsed

def _backup(path):
    if BACKUP and os.path.exists(path):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
        base, ext = os.path.splitext(path)
        dst = f"{base}_backup_{ts}{ext}"
        os.replace(path, dst)

def _clip_unit(x, lo=-1.0, hi=1.0):
    return np.minimum(np.maximum(x, lo), hi)

def _tanh_z(x, win=100):
    s = pd.Series(x, copy=False)
    m = s.rolling(win, min_periods=max(1, win//5)).mean()
    v = s.rolling(win, min_periods=max(1, win//5)).std(ddof=0)
    z = (s - m) / (v.replace(0, np.nan))
    return np.tanh(z).to_numpy()

# -------------------------- Indikatoren --------------------------
def rsi(close, period=14):
    d = np.diff(close, prepend=close[0])
    up = np.where(d>0, d, 0.0); dn = np.where(d<0, -d, 0.0)
    alpha = 1/period
    up_ema = pd.Series(up).ewm(alpha=alpha, adjust=False).mean().to_numpy()
    dn_ema = pd.Series(dn).ewm(alpha=alpha, adjust=False).mean().to_numpy()
    rs = up_ema / (dn_ema + 1e-12)
    rsi = 100 - 100/(1+rs)
    return (rsi - 50.0)/50.0

def macd_hist(close, fast=12, slow=26, sig=9):
    ema_fast = pd.Series(close).ewm(span=fast, adjust=False).mean()
    ema_slow = pd.Series(close).ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=sig, adjust=False).mean()
    hist = (macd - signal).to_numpy()
    return _tanh_z(hist, win=200)

def bollinger_signal(close, period=20, k=2):
    s = pd.Series(close)
    ma = s.rolling(period, min_periods=max(1, period//2)).mean()
    sd = s.rolling(period, min_periods=max(1, period//2)).std(ddof=0)
    bb = (s - ma) / (k*sd.replace(0, np.nan))
    return _clip_unit(bb.to_numpy())

def ma_distance_signal(close, period):
    s = pd.Series(close)
    ma = s.rolling(period, min_periods=max(1, period//2)).mean()
    dist = (s - ma) / s.replace(0, np.nan)
    dist = dist.clip(lower=-0.1, upper=0.1) / 0.1
    return dist.fillna(0.0).to_numpy()

def ema_distance_signal(close, period):
    ema = pd.Series(close).ewm(span=period, adjust=False).mean()
    dist = (pd.Series(close) - ema) / pd.Series(close).replace(0, np.nan)
    dist = dist.clip(lower=-0.1, upper=0.1) / 0.1
    return dist.fillna(0.0).to_numpy()

def stoch_signal(close, high, low, period=14):
    c = pd.Series(close); h = pd.Series(high); l = pd.Series(low)
    hh = h.rolling(period, min_periods=max(1, period//2)).max()
    ll = l.rolling(period, min_periods=max(1, period//2)).min()
    k = (c - ll) / (hh - ll).replace(0, np.nan) * 100.0
    return ((k - 50.0)/50.0).fillna(0.0).to_numpy()

def true_range(high, low, close):
    prev_close = pd.Series(close).shift(1).fillna(close[0])
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    return tr

def atr_signal(high, low, close, period=14):
    tr = true_range(np.array(high), np.array(low), np.array(close))
    atr = pd.Series(tr).ewm(alpha=1/period, adjust=False).mean()
    rel = (atr / pd.Series(close).replace(0, np.nan)).to_numpy()
    return _tanh_z(rel, win=200)

def adx_signal(high, low, close, period=14):
    h = pd.Series(high); l = pd.Series(low); c = pd.Series(close)
    up_move = h.diff(); dn_move = -l.diff()
    plus_dm  = up_move.where((up_move > dn_move) & (up_move > 0), 0.0)
    minus_dm = dn_move.where((dn_move > up_move) & (dn_move > 0), 0.0)
    tr = true_range(h.to_numpy(), l.to_numpy(), c.to_numpy())
    tr_ema = pd.Series(tr).ewm(alpha=1/period, adjust=False).mean()
    plus_di  = 100 * (pd.Series(plus_dm).ewm(alpha=1/period, adjust=False).mean() / tr_ema.replace(0,np.nan))
    minus_di = 100 * (pd.Series(minus_dm).ewm(alpha=1/period, adjust=False).mean() / tr_ema.replace(0,np.nan))
    dx = ( (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0,np.nan) ) * 100
    adx = dx.ewm(alpha=1/period, adjust=False).mean().fillna(0.0)
    sign = np.sign(ema_distance_signal(close, EMA50_P))
    return (adx.to_numpy()/100.0 * sign).astype(float)

def cci_signal(high, low, close, period=20):
    tp = (pd.Series(high)+pd.Series(low)+pd.Series(close))/3.0
    ma = tp.rolling(period, min_periods=max(1, period//2)).mean()
    md = (tp - ma).abs().rolling(period, min_periods=max(1, period//2)).mean()
    cci = (tp - ma) / (0.015 * md.replace(0, np.nan))
    return _tanh_z(cci.to_numpy(), win=200)

def mfi_signal(high, low, close, volume, period=14):
    tp = (pd.Series(high)+pd.Series(low)+pd.Series(close))/3.0
    d_tp = tp.diff().fillna(0.0)
    pmf = np.where(d_tp > 0, tp*volume, 0.0)
    nmf = np.where(d_tp < 0, tp*volume, 0.0)
    pmf_sum = pd.Series(pmf).rolling(period, min_periods=max(1, period//2)).sum()
    nmf_sum = pd.Series(nmf).rolling(period, min_periods=max(1, period//2)).sum().replace(0, np.nan)
    mfr = pmf_sum / nmf_sum
    mfi = 100 - (100 / (1 + mfr))
    return ((mfi - 50.0)/50.0).fillna(0.0).to_numpy()

def obv_signal(close, volume):
    delta = pd.Series(close).diff().fillna(0.0)
    direction = np.sign(delta)
    obv = (pd.Series(volume) * direction).cumsum()
    return _tanh_z(obv.to_numpy(), win=400)

# ===== Momentum (NEU) =====
def ema50_cross_ma200_signal(close):
    ema50 = pd.Series(close).ewm(span=EMA50_P, adjust=False).mean()
    ma200 = pd.Series(close).rolling(MA200_P, min_periods=max(1, MA200_P//2)).mean()
    diff = (ema50 - ma200) / pd.Series(close).replace(0, np.nan)
    # sanft clippen und skalieren → −1..+1
    diff = diff.clip(lower=-0.1, upper=0.1) / 0.1
    return diff.fillna(0.0).to_numpy()

def rsi_derivative_signal(close, period=RSI_P):
    r = rsi(np.asarray(close, dtype=float), period)
    dr = pd.Series(r).diff().fillna(0.0)
    return _tanh_z(dr.to_numpy(), win=200)

# -------------------------- Kernpipeline --------------------------
def compute_signals(df):
    tcol = _find_col(df, TIME_ALIASES, True, "time")
    ocol = _find_col(df, OPEN_ALIASES, False, "open")
    hcol = _find_col(df, HIGH_ALIASES, True,  "high")
    lcol = _find_col(df, LOW_ALIASES,  True,  "low")
    ccol = _find_col(df, CLOSE_ALIASES,True,  "close")
    vcol = _find_col(df, VOL_ALIASES,  False, "volume")

    ts = _to_utc_datetime(df[tcol])
    if ts.isna().any():
        raise ValueError("Ungültige Zeitstempel erkannt.")
    if getattr(ts.dt, "tz", None) is not None:
        ts = ts.dt.tz_convert("UTC").dt.tz_localize(None)

    out = pd.DataFrame({
        "timestamp": ts,
        "open":  df[ocol] if ocol else df[ccol],
        "high":  df[hcol],
        "low":   df[lcol],
        "close": df[ccol],
        "volume": df[vcol] if vcol else 0.0,
    }).sort_values("timestamp").reset_index(drop=True)

    o = out["open"].to_numpy(dtype=float)
    h = out["high"].to_numpy(dtype=float)
    l = out["low"].to_numpy(dtype=float)
    c = out["close"].to_numpy(dtype=float)
    v = out["volume"].to_numpy(dtype=float)

    # 12 Kernsignale
    out["rsi_signal"]        = rsi(c, RSI_P)
    out["macd_signal"]       = macd_hist(c, MACD_FAST, MACD_SLOW, MACD_SIG)
    out["bollinger_signal"]  = bollinger_signal(c, BOLL_P, BOLL_K)
    out["ma200_signal"]      = ma_distance_signal(c, MA200_P)
    out["stoch_signal"]      = stoch_signal(c, h, l, STOCH_P)
    out["atr_signal"]        = atr_signal(h, l, c, ATR_P)
    out["ema50_signal"]      = ema_distance_signal(c, EMA50_P)
    out["ema200_signal"]     = ema_distance_signal(c, EMA200_P)
    out["adx_signal"]        = adx_signal(h, l, c, ADX_P)
    out["cci_signal"]        = cci_signal(h, l, c, CCI_P)
    out["mfi_signal"]        = mfi_signal(h, l, c, v if vcol else np.zeros_like(c), MFI_P)
    out["obv_signal"]        = obv_signal(c, v if vcol else np.zeros_like(c))

    # 2 Momentum-Signale (NEU)
    out["ema50_cross_ma200_signal"] = ema50_cross_ma200_signal(c)
    out["rsi_derivative_signal"]    = rsi_derivative_signal(c, RSI_P)

    return out

def resample_ohlcv(df, rule):
    g = df.set_index("timestamp").groupby(pd.Grouper(freq=rule))
    o = g["open"].first()
    h = g["high"].max()
    l = g["low"].min()
    c = g["close"].last()
    v = g["volume"].sum()
    res = pd.DataFrame({"timestamp": o.index, "open": o, "high": h, "low": l, "close": c, "volume": v}).dropna()
    res = res.reset_index(drop=True)
    return res

def compute_and_save(input_csv, out_csv, do_resample=None):
    print(f"📥 Lese: {os.path.relpath(input_csv, ROOT)}")
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Eingabe nicht gefunden: {input_csv}")

    raw = pd.read_csv(input_csv)
    df1m = compute_signals(raw)

    if BACKUP and os.path.exists(out_csv):
        _backup(out_csv)
    df1m.to_csv(out_csv, index=False)
    print(f"✅ Geschrieben: {os.path.relpath(out_csv, ROOT)}  | Zeilen: {len(df1m):,}")

    if do_resample:
        for rule, outp in do_resample:
            rs = resample_ohlcv(df1m[["timestamp","open","high","low","close","volume"]], rule)
            rs_signals = compute_signals(rs)
            if BACKUP and os.path.exists(outp):
                _backup(outp)
            rs_signals.to_csv(outp, index=False)
            print(f"✅ Resample {rule}: {os.path.relpath(outp, ROOT)}  | Zeilen: {len(rs_signals):,}")

# -------------------------- main --------------------------
if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    resamples = []
    if MAKE_5M:  resamples.append(("5T", OUT_5M))
    if MAKE_15M: resamples.append(("15T", OUT_15M))

    compute_and_save(
        IN_1M,
        OUT_1M,
        do_resample=resamples if len(resamples)>0 else None
    )

