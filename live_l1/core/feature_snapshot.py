#!/usr/bin/env python3
# live_l1/core/feature_snapshot.py
#
# Deterministic Feature Snapshot for L1 pipeline.
# - converts raw MarketSnapshot into a stable feature object
# - centralizes signal access and gate fields
# - ASCII-only

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping


SIGNAL_COLUMNS = (
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
)


def _to_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return int(float(s))
    except Exception:
        return default


def _to_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    s = str(value).strip()
    if s == "":
        return default
    try:
        return float(s)
    except Exception:
        return default


@dataclass(frozen=True)
class FeatureSnapshot:
    snapshot_id: str
    timestamp_utc: str
    symbol: str
    price: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    allow_long: int
    allow_short: int
    regime_v2: int
    signals: Dict[str, int]

    def signal(self, name: str, default: int = 0) -> int:
        return _to_int(self.signals.get(name), default)

    def weighted_signal_score(self, weights: Mapping[str, float]) -> float:
        score = 0.0
        for col, w in weights.items():
            score += float(w) * float(self.signal(col, 0))
        return score

    def signal_score(self) -> int:
        score = 0
        for col in SIGNAL_COLUMNS:
            score += self.signal(col, 0)
        return score


def build_feature_snapshot(snapshot) -> FeatureSnapshot:
    raw_signals = getattr(snapshot, "signals", {}) or {}

    signals: Dict[str, int] = {}
    for col in SIGNAL_COLUMNS:
        signals[col] = _to_int(raw_signals.get(col), 0)

    return FeatureSnapshot(
        snapshot_id=str(getattr(snapshot, "snapshot_id", "")).strip(),
        timestamp_utc=str(getattr(snapshot, "timestamp_utc", "")).strip(),
        symbol=str(getattr(snapshot, "symbol", "")).strip(),
        price=_to_float(getattr(snapshot, "price", 0.0), 0.0),
        open=_to_float(getattr(snapshot, "open", 0.0), 0.0),
        high=_to_float(getattr(snapshot, "high", 0.0), 0.0),
        low=_to_float(getattr(snapshot, "low", 0.0), 0.0),
        close=_to_float(getattr(snapshot, "close", 0.0), 0.0),
        volume=_to_float(getattr(snapshot, "volume", 0.0), 0.0),
        allow_long=_to_int(getattr(snapshot, "allow_long", 0), 0),
        allow_short=_to_int(getattr(snapshot, "allow_short", 0), 0),
        regime_v2=_to_int(getattr(snapshot, "regime_v2", 0), 0),
        signals=signals,
    )