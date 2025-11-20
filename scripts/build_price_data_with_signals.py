
import pandas as pd
import numpy as np

fn = "data/btcusdt_1m_spot_filled.csv"
out = "data/price_data_with_signals.csv"

df = pd.read_csv(fn, parse_dates=["open_time_iso"], low_memory=False)
df = df.sort_values("open_time").reset_index(drop=True)
close = df["close"].astype(float)
high = df["high"].astype(float)
low = df["low"].astype(float)
vol = df["volume"].astype(float)

# helpers
def ema(s, span):
    return s.ewm(span=span, adjust=False).mean()

# RSI (14)
delta = close.diff()
gain = delta.where(delta>0, 0.0)
loss = -delta.where(delta<0, 0.0)
avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
rs = avg_gain / (avg_loss.replace(0, np.nan))
rsi = 100 - (100 / (1 + rs))
df["rsi"] = rsi.fillna(50)

# MACD (12,26,9)
macd = ema(close, 12) - ema(close, 26)
macd_signal = ema(macd, 9)
df["macd_hist"] = (macd - macd_signal).fillna(0)

# Bollinger (20,2)
sma20 = close.rolling(20).mean()
std20 = close.rolling(20).std()
df["bb_upper"] = sma20 + 2 * std20
df["bb_lower"] = sma20 - 2 * std20
df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / sma20.replace(0, np.nan)

# MA200 & EMA50
df["ma200"] = close.rolling(200).mean()
df["ema50"] = ema(close, 50)

# Stochastic %K (14)
low14 = low.rolling(14).min()
high14 = high.rolling(14).max()
df["stoch_k"] = 100 * (close - low14) / (high14 - low14).replace(0, np.nan)

# ATR (14)
tr1 = high - low
tr2 = (high - close.shift(1)).abs()
tr3 = (low - close.shift(1)).abs()
tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
df["atr"] = tr.rolling(14).mean()

# ROC (12)
df["roc"] = close.pct_change(12).fillna(0) * 100

# OBV
obv = (np.sign(close.diff().fillna(0)) * vol).fillna(0).cumsum()
df["obv"] = obv

# CCI (20)
tp = (high + low + close) / 3
tp_sma = tp.rolling(20).mean()
tp_md = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
df["cci"] = (tp - tp_sma) / (0.015 * tp_md.replace(0, np.nan))

# MFI (14)
typ = tp
mf = typ * vol
pos = (typ > typ.shift(1)).astype(int)
neg = (typ < typ.shift(1)).astype(int)
pos_mf = (mf * pos).rolling(14).sum()
neg_mf = (mf * neg).rolling(14).sum().replace(0, np.nan)
mfr = pos_mf / neg_mf
df["mfi"] = 100 - (100 / (1 + mfr))

# ADX (14) - simplified Wilder smoothing
up = high.diff()
down = -low.diff()
plus_dm = np.where((up>down) & (up>0), up, 0.0)
minus_dm = np.where((down>up) & (down>0), down, 0.0)
tr14 = tr.rolling(14).sum()
plus_di = 100 * (pd.Series(plus_dm).rolling(14).sum().replace(0, np.nan) / tr14)
minus_di = 100 * (pd.Series(minus_dm).rolling(14).sum().replace(0, np.nan) / tr14)
dx = (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)) * 100
df["adx"] = dx.rolling(14).mean()

# --- derive simple signal columns (numeric: 1 = bullish signal, 0 = no) ---
df["rsi_signal"] = (df["rsi"] < 30).astype(int)
df["macd_signal"] = (df["macd_hist"] > 0).astype(int)
df["bollinger_signal"] = (close < df["bb_lower"]).astype(int)
df["ma200_signal"] = (close > df["ma200"]).astype(int)
df["stoch_signal"] = (df["stoch_k"] < 20).astype(int)
df["atr_signal"] = (df["atr"] > df["atr"].rolling(200).mean().fillna(0)).astype(int)
df["ema50_signal"] = (close > df["ema50"]).astype(int)
df["adx_signal"] = (df["adx"] > 25).astype(int)
df["cci_signal"] = (df["cci"] < -100).astype(int)
df["mfi_signal"] = (df["mfi"] < 20).astype(int)
df["obv_signal"] = (df["obv"] > df["obv"].rolling(50).mean().fillna(0)).astype(int)
df["roc_signal"] = (df["roc"] > 0).astype(int)

# Save (keep original columns + new signals)
cols_keep = list(df.columns)
df.to_csv(out, index=False)
print("OK ->", out)

