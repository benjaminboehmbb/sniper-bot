from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from tools.ssi.builder.lifecycle_snapshot import LifecycleSnapshot
from tools.ssi.common.normalization import clamp


@dataclass(frozen=True)
class CompatibilityResult:
    value: float
    raw: float
    components: Dict[str, Any]


def _regime_score_for_side(side: str, market_regime: str) -> float:
    regime = market_regime.strip().lower()

    if side == "LONG":
        if "bull" in regime:
            return 1.0
        if "bear" in regime:
            return 0.0
        return 0.5

    if side == "SHORT":
        if "bear" in regime:
            return 1.0
        if "bull" in regime:
            return 0.0
        return 0.5

    return 0.5


def _ma200_score_for_side(side: str, ma200_signal: int | None) -> float:
    if ma200_signal is None:
        return 0.5

    if side == "LONG":
        if ma200_signal > 0:
            return 1.0
        if ma200_signal < 0:
            return 0.0
        return 0.5

    if side == "SHORT":
        if ma200_signal < 0:
            return 1.0
        if ma200_signal > 0:
            return 0.0
        return 0.5

    return 0.5


def calculate_compatibility(
    snapshot: LifecycleSnapshot,
    *,
    regime_weight: float = 0.70,
    ma200_weight: float = 0.30,
) -> CompatibilityResult:
    if regime_weight < 0 or ma200_weight < 0:
        raise ValueError("weights must be >= 0")

    total_weight = regime_weight + ma200_weight
    if total_weight <= 0:
        raise ValueError("sum of weights must be > 0")

    regime_score = _regime_score_for_side(snapshot.side, snapshot.market_regime)
    ma200_score = _ma200_score_for_side(snapshot.side, snapshot.ma200_signal)

    raw = ((regime_score * regime_weight) + (ma200_score * ma200_weight)) / total_weight
    value = clamp(raw)

    return CompatibilityResult(
        value=value,
        raw=raw,
        components={
            "side": snapshot.side,
            "market_regime": snapshot.market_regime,
            "ma200_signal": snapshot.ma200_signal,
            "regime_score": regime_score,
            "ma200_score": ma200_score,
            "regime_weight": regime_weight,
            "ma200_weight": ma200_weight,
            "method": "side_regime_ma200_compatibility_v1",
        },
    )
