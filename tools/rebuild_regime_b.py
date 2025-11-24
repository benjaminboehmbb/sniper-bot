import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd


def rebuild_regime_b(
    input_path="data/price_data_with_signals_regime.csv",
    output_path="data/price_data_with_signals_regime_v2.csv",
):
    if not os.path.exists(input_path):
        print("ERROR: Input file not found:", input_path)
        sys.exit(1)

    print("[INFO] Loading:", input_path)
    df = pd.read_csv(input_path)

    required_cols = ["close", "ma200", "ema50", "adx", "roc", "atr"]
    for col in required_cols:
        if col not in df.columns:
            print("ERROR: Column missing:", col)
            print("Columns available:", list(df.columns))
            sys.exit(1)

    close = df["close"].astype(float)
    ma200 = df["ma200"].astype(float)
    ema50 = df["ema50"].astype(float)
    adx = df["adx"].astype(float)
    roc = df["roc"].astype(float)

    # Returns
    ret = close.pct_change().fillna(0.0)
    df["ret"] = ret

    # Rolling sums / vols fuer Crash Erkennung
    roll_ret_20 = ret.rolling(window=20, min_periods=20).sum()
    roll_vol_20 = ret.rolling(window=20, min_periods=20).std()

    vol_thresh = roll_vol_20.quantile(0.70)

    strong_trend = adx >= 20.0

    bull_mask = (
        (close > ma200)
        & (ema50 > ma200)
        & (roc > 0.0)
        & strong_trend
    )

    bear_mask = (
        (close < ma200)
        & (ema50 < ma200)
        & (roc < 0.0)
        & strong_trend
    )

    crash_mask = (
        bear_mask
        & (roll_ret_20 < -0.15)
        & (roll_vol_20 > vol_thresh)
    )

    n = len(df)
    regime = np.full(n, "side", dtype=object)

    # Reihenfolge: erst bull/bear, dann crash als Override
    regime[bull_mask] = "bull"
    regime[bear_mask] = "bear"
    regime[crash_mask] = "crash"

    regime_signal = np.zeros(n, dtype=int)
    regime_bull = np.zeros(n, dtype=int)
    regime_bear = np.zeros(n, dtype=int)

    regime_bull[regime == "bull"] = 1
    regime_bear[(regime == "bear") | (regime == "crash")] = 1

    regime_signal[regime == "bull"] = 1
    regime_signal[(regime == "bear") | (regime == "crash")] = -1

    # Alte Regime-Spalten entfernen, falls vorhanden
    for col in ["market_regime", "regime_signal", "regime_bull", "regime_bear"]:
        if col in df.columns:
            df = df.drop(columns=[col])

    df["market_regime"] = regime
    df["regime_signal"] = regime_signal
    df["regime_bull"] = regime_bull
    df["regime_bear"] = regime_bear

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("[INFO] Rebuilt regime B at", ts)
    print("[INFO] Regime counts:")
    print(df["market_regime"].value_counts())

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print("[INFO] Wrote:", output_path)


if __name__ == "__main__":
    rebuild_regime_b()
