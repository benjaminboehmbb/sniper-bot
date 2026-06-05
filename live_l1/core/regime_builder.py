#!/usr/bin/env python3
# live_l1/core/regime_builder.py
# Online regime_v1 builder for Live L1.
# ASCII-only.

from __future__ import annotations

import pandas as pd

MIN_ROWS = 1640


def build_regime_frame(df: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")

    required = ["close"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError("Missing required columns: " + ",".join(missing))

    if len(df) < MIN_ROWS:
        raise ValueError(f"Need at least {MIN_ROWS} rows, got {len(df)}")

    out = df.copy()

    close = pd.to_numeric(out["close"], errors="coerce")

    ma200 = close.rolling(200, min_periods=200).mean()
    ma200_slope_1440 = ma200.diff(1440)

    bull = (close > ma200) & (ma200_slope_1440 > 0)
    bear = (close < ma200) & (ma200_slope_1440 < 0)

    regime = pd.Series(0, index=out.index, dtype="int64")
    regime[bull.fillna(False)] = 1
    regime[bear.fillna(False)] = -1

    out["ma200"] = ma200
    out["ma200_slope_1440"] = ma200_slope_1440
    out["regime_v1"] = regime

    return out


def build_online_regime(df: pd.DataFrame) -> int:
    frame = build_regime_frame(df)
    return int(frame.iloc[-1]["regime_v1"])


