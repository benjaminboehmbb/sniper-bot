"""Pure deterministic formulas for RCC-002 S5."""

from __future__ import annotations

import math
from numbers import Real

from rcc002.s5.constants import (
    RegimeState,
    TrendStrength,
    VolatilityRelative,
)


class RegimeFormulaError(ValueError):
    """Base error for invalid S5 formula inputs."""


class SlopeDenominatorInvalid(RegimeFormulaError):
    """Raised when the historical SMA200 denominator is invalid."""


def _finite_real(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise RegimeFormulaError(f"{name} must be a finite real number")
    result = float(value)
    if not math.isfinite(result):
        raise RegimeFormulaError(f"{name} must be a finite real number")
    return result


def ma200_slope_1440_pct(
    current_sma200: float,
    reference_sma200: float,
) -> float:
    """Return ``100 * ((current / reference) - 1)`` in exact order."""

    current = _finite_real(current_sma200, "current_sma200")
    reference = _finite_real(reference_sma200, "reference_sma200")
    if reference <= 0.0:
        raise SlopeDenominatorInvalid(
            "reference_sma200 must be positive"
        )
    ratio = current / reference
    offset = ratio - 1.0
    result = 100.0 * offset
    if not math.isfinite(result):
        raise RegimeFormulaError("slope result is not finite")
    return result


def classify_raw_regime(
    close: float,
    sma200: float,
    slope_pct: float,
) -> RegimeState:
    close_value = _finite_real(close, "close")
    sma_value = _finite_real(sma200, "sma200")
    slope_value = _finite_real(slope_pct, "slope_pct")
    if close_value > sma_value and slope_value > 0.0:
        return RegimeState.BULL
    if close_value < sma_value and slope_value < 0.0:
        return RegimeState.BEAR
    return RegimeState.SIDE


def classify_trend_strength(adx: float) -> TrendStrength:
    value = _finite_real(adx, "adx")
    if value < 0.0 or value > 100.0:
        raise RegimeFormulaError("adx must be within [0, 100]")
    if value <= 15.0:
        return TrendStrength.WEAK
    if value <= 25.0:
        return TrendStrength.DEVELOPING
    return TrendStrength.STRONG


def classify_volatility_relative(
    state_atr_relative_d: int,
) -> VolatilityRelative:
    if isinstance(state_atr_relative_d, bool) or not isinstance(
        state_atr_relative_d, int
    ):
        raise RegimeFormulaError(
            "state_atr_relative_d must be an integer"
        )
    mapping = {
        -1: VolatilityRelative.BELOW_REFERENCE,
        0: VolatilityRelative.AT_REFERENCE,
        1: VolatilityRelative.ABOVE_REFERENCE,
    }
    try:
        return mapping[state_atr_relative_d]
    except KeyError as exc:
        raise RegimeFormulaError(
            "state_atr_relative_d must be -1, 0, or 1"
        ) from exc


__all__ = [
    "RegimeFormulaError",
    "SlopeDenominatorInvalid",
    "classify_raw_regime",
    "classify_trend_strength",
    "classify_volatility_relative",
    "ma200_slope_1440_pct",
]
