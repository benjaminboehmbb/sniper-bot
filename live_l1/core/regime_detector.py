#!/usr/bin/env python3
# live_l1/core/regime_detector.py
# Passive regime detector for L1.
# ASCII-only.
#
# IMPORTANT:
# This module must not change trading decisions.
# It only classifies and reports regime context.

from __future__ import annotations

from dataclasses import dataclass

from live_l1.core.feature_snapshot import FeatureSnapshot


@dataclass(frozen=True)
class RegimeSnapshot:
    label: str
    ma200_signal: int
    atr_signal: int
    mfi_signal: int
    score: int
    risk_label: str


def _score(features: FeatureSnapshot) -> int:
    return int(
        features.signal("rsi_signal")
        + features.signal("bollinger_signal")
        + features.signal("stoch_signal")
        + features.signal("cci_signal")
    )


def detect_regime(features: FeatureSnapshot) -> RegimeSnapshot:
    ma200 = int(features.signal("ma200_signal"))
    atr = int(features.signal("atr_signal"))
    mfi = int(features.signal("mfi_signal"))
    score = _score(features)

    if ma200 > 0:
        label = "bull"
    elif ma200 < 0:
        label = "bear"
    else:
        label = "chop"

    if atr == -1:
        risk_label = "bad_atr"
    elif atr == 1:
        risk_label = "good_atr"
    else:
        risk_label = "neutral_atr"

    return RegimeSnapshot(
        label=label,
        ma200_signal=ma200,
        atr_signal=atr,
        mfi_signal=mfi,
        score=score,
        risk_label=risk_label,
    )
