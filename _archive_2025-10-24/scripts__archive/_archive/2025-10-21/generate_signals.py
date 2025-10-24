# scripts/generate_signals.py
# Berechnet RSI, MACD, Bollinger, MA200, Stoch, ATR, EMA50 und schreibt die CSV (mit Backup).
# Läuft im project root: ~/Desktop/sniper-bot
# Benötigt: pandas, numpy, pyyaml (pyyaml ist nur für config-path optional)

import os, sys, shutil, datetime
import pandas as pd
import numpy as np

# --- Helfer -------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base_config.yaml")
DEFAULT_CSV = os.path.join(ROOT, "data", "btcusdt_1m_spot.csv")

def get_csv_path():
    # Falls pyyaml vorhanden, versuche Pfad aus config zu lesen, sonst Default
    try:
        import yaml
        if os.path.isfile(CFG_PATH):
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
            p = cfg.get("data", {}).get("csv_path") or cfg.get("data", {}).get("price_csv")
            if p:
                return os.path.join(ROOT, p.replace("/", os.sep))
    except Exception:
        pass
    return DEFAULT_CSV

def backup_file(path):
    if not os.path.isfile(path):
        return None
    bak_dir = os.path.join(os.path.dirname(path), "_backup")
    os.makedirs(bak_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dst = os.path.join(bak_dir, os.path.basename(path) + f".bak_{ts}")
    shutil.copy2(path, dst)
    return dst

# --- Indikatoren -------------------------------------------------
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # Wilder's EMA
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    rs = avg_gain / (avg_loss.replace(0, np.nan))
    r = 100 - (100 / (1 + rs))
    return r.fillna(50.0)  # neutral bei NaN

def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    macd_signal = ema(macd_line, signal)
    macd_hist = macd_line - macd_signal
    return macd_line, macd_signal, macd_hist

def bollinger_bands(series, period=20, stddev=2):
    ma = series.rolling(window=period, min_periods=1).mean()
    sd = series.rolling(window=period, min_periods=1).std(ddof=0)
    upper = ma + stddev * sd
    lower = ma - stddev * sd
    # Provide normalized band distance as a numeric column
    bandwidth = (series - ma) / sd.replace(0, np.nan)
    return ma, upper, lower, bandwidth.fillna(0.0)

def sma(series, period=200):
    return series.rolling(window=period, min_periods=1).mean()

def stoch_k_d(high, low, close, k_period=14, d_period=3):
    low_min = low.rolling(window=k_period, min_periods=1).min()
    high_max = high.rolling(window=k_period, min_periods=1).max()
    k = (close - low_min) / (high_max - low_min).replace(0, np.nan) * 100
    d = k.rolling(window=d_period, min_periods=1).mean()
    return k.fillna(50.0), d.fillna(50.0)

def atr(high, low, close, period=14):
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr_val = tr.ewm(alpha=1/period, adjust=False).mean()
    return atr_val.fillna(0.0)

# --- Main -------------------------------------------------------
def main():
    csv_path = get_csv_path()
    print("CSV path:", csv_path)
    if not os.path.isfile(csv_path):
        print("FEHLER: CSV-Datei existiert nicht:", csv_path)
        sys.exit(2)

    # Backup original CSV
    bak = backup_file(csv_path)
    if bak:
        print("Backup erstellt:", bak)

    # Load CSV (versuche gängige Zeitspalten)
    df = pd.read_csv(csv_path)
    # Prüfe benötigte Spalten
    for col in ["close", "high", "low"]:
        if col not in df.columns:
            # versuche alternative Namen
            if col == "close" and "Close" in df.columns:
                df.rename(columns={"Close":"close"}, inplace=True)
            elif col == "high" and "High" in df.columns:
                df.rename(columns={"High":"high"}, inplace=True)
            elif col == "low" and "Low" in df.columns:
                df.rename(columns={"Low":"low"}, inplace=True)
            else:
                print(f"FEHLER: benötigte Spalte '{col}' fehlt in CSV. Spalten: {list(df.columns)[:20]}")
                sys.exit(3)

    # Ensure numeric
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")
    # optional: volume
    if "volume" in df.columns:
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    # Compute indicators
    print("Berechne Indikatoren ...")
    df["rsi"] = rsi(df["close"], period=14)
    macd_line, macd_signal, macd_hist = macd(df["close"], fast=12, slow=26, signal=9)
    df["macd_line"] = macd_line
    df["macd_signal"] = macd_signal
    df["macd"] = macd_hist  # historgram as 'macd' numeric column
    ma, upper, lower, bw = bollinger_bands(df["close"], period=20, stddev=2)
    df["bollinger_mid"] = ma
    df["bollinger_upper"] = upper
    df["bollinger_lower"] = lower
    df["bollinger"] = bw
    df["ma200"] = sma(df["close"], period=200)
    k, d = stoch_k_d(df.get("high"), df.get("low"), df["close"], k_period=14, d_period=3)
    df["stoch_k"] = k
    df["stoch_d"] = d
    df["stoch"] = k - d
    df["atr"] = atr(df.get("high"), df.get("low"), df["close"], period=14)
    df["ema50"] = ema(df["close"], span=50)

    # Some scripts expect exact column names: create simple fallbacks
    fallback_map = {
        "rsi": "rsi",
        "macd": "macd",
        "bollinger": "bollinger",
        "ma200": "ma200",
        "stoch": "stoch",
        "atr": "atr",
        "ema50": "ema50",
    }
    # ensure keys exist (they do), but create simple numeric copies as final names
    # (already set above)

    # Write back (overwrite original CSV so analyze_template reads it)
    df.to_csv(csv_path, index=False)
    print("FERTIG: Signale geschrieben in:", csv_path)

    # Validate presence
    missing = [k for k in fallback_map.keys() if k not in df.columns]
    if missing:
        print("WARN: Noch fehlende Signalspalten:", missing)
        sys.exit(4)
    else:
        print("Validierung OK — alle Signalspalten vorhanden:")
        print(", ".join(fallback_map.keys()))
        sys.exit(0)

if __name__ == "__main__":
    main()
