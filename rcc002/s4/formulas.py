"""Pure mathematical formulas for RCC-002 S4 signal transformation.

This module contains no row handling, no warm-up state, no schema checks,
and no input-validity propagation. It implements only the deterministic
mathematical transformations defined by the certified S4 specification.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from numbers import Real


@dataclass(frozen=True, slots=True)
class SignalFormulaConflict(ValueError):
    """A mathematically undefined but normatively classified S4 case."""

    reason_code: str
    message: str

    def __str__(self) -> str:
        return f"{self.reason_code}: {self.message}"


def _finite(value: Real, name: str) -> float:
    """Return one finite real value as float."""

    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")

    result = float(value)

    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")

    return result


def clip(value: Real, lower: Real, upper: Real) -> float:
    """Clip one finite value to the inclusive interval [lower, upper]."""

    x = _finite(value, "value")
    lo = _finite(lower, "lower")
    hi = _finite(upper, "upper")

    if lo > hi:
        raise ValueError("lower must not exceed upper")

    return min(max(x, lo), hi)


def sign3(value: Real) -> int:
    """Return +1, 0, or -1 from the unrounded canonical value."""

    x = _finite(value, "value")

    if x > 0.0:
        return 1

    if x < 0.0:
        return -1

    return 0


# ---------------------------------------------------------------------------
# RSI
# ---------------------------------------------------------------------------

def sig_rsi_mr_d(rsi_wilder_14: Real) -> int:
    rsi = _finite(rsi_wilder_14, "rsi_wilder_14")

    if rsi < 30.0:
        return 1

    if rsi > 70.0:
        return -1

    return 0


def score_rsi_mr_c(rsi_wilder_14: Real) -> float:
    rsi = _finite(rsi_wilder_14, "rsi_wilder_14")
    return clip((50.0 - rsi) / 20.0, -1.0, 1.0)


# ---------------------------------------------------------------------------
# MACD
# ---------------------------------------------------------------------------

def sig_macd_momentum_d(macd_hist_12_26_9: Real) -> int:
    return sign3(macd_hist_12_26_9)


def score_macd_momentum_c(
    macd_hist_12_26_9: Real,
    atr_wilder_14: Real,
) -> float:
    hist = _finite(macd_hist_12_26_9, "macd_hist_12_26_9")
    atr = _finite(atr_wilder_14, "atr_wilder_14")

    if atr < 0.0:
        raise ValueError("atr_wilder_14 must be nonnegative")

    if atr > 0.0:
        return clip(hist / atr, -1.0, 1.0)

    if hist == 0.0:
        return 0.0

    raise SignalFormulaConflict(
        "SIG_MACD_ZERO_ATR_CONFLICT",
        "MACD histogram is nonzero while ATR equals zero",
    )


# ---------------------------------------------------------------------------
# Bollinger Bands
# ---------------------------------------------------------------------------

def sig_bollinger_mr_d(
    close: Real,
    bb_lower_20_2: Real,
    bb_upper_20_2: Real,
) -> int:
    close_value = _finite(close, "close")
    lower = _finite(bb_lower_20_2, "bb_lower_20_2")
    upper = _finite(bb_upper_20_2, "bb_upper_20_2")

    if lower > upper:
        raise ValueError("bb_lower_20_2 must not exceed bb_upper_20_2")

    if close_value < lower:
        return 1

    if close_value > upper:
        return -1

    return 0


def score_bollinger_mr_c(
    close: Real,
    bb_mid_20: Real,
    bb_upper_20_2: Real,
) -> float:
    close_value = _finite(close, "close")
    mid = _finite(bb_mid_20, "bb_mid_20")
    upper = _finite(bb_upper_20_2, "bb_upper_20_2")

    half_band_width = upper - mid

    if half_band_width < 0.0:
        raise ValueError("bb_upper_20_2 must not be below bb_mid_20")

    if half_band_width > 0.0:
        return clip(
            (mid - close_value) / half_band_width,
            -1.0,
            1.0,
        )

    if close_value == mid:
        return 0.0

    raise SignalFormulaConflict(
        "SIG_BB_ZERO_WIDTH_CONFLICT",
        "Bollinger half-band width is zero while close differs from mid",
    )


# ---------------------------------------------------------------------------
# Stochastic
# ---------------------------------------------------------------------------

def sig_stoch_mr_d(stoch_k_14: Real) -> int:
    stoch = _finite(stoch_k_14, "stoch_k_14")

    if stoch < 20.0:
        return 1

    if stoch > 80.0:
        return -1

    return 0


def score_stoch_mr_c(stoch_k_14: Real) -> float:
    stoch = _finite(stoch_k_14, "stoch_k_14")
    return clip((50.0 - stoch) / 30.0, -1.0, 1.0)


# ---------------------------------------------------------------------------
# CCI
# ---------------------------------------------------------------------------

def sig_cci_mr_d(cci_20: Real) -> int:
    cci = _finite(cci_20, "cci_20")

    if cci < -100.0:
        return 1

    if cci > 100.0:
        return -1

    return 0


def score_cci_mr_c(cci_20: Real) -> float:
    cci = _finite(cci_20, "cci_20")
    return clip(-cci / 100.0, -1.0, 1.0)


# ---------------------------------------------------------------------------
# MFI
# ---------------------------------------------------------------------------

def sig_mfi_mr_d(mfi_14: Real) -> int:
    mfi = _finite(mfi_14, "mfi_14")

    if mfi < 20.0:
        return 1

    if mfi > 80.0:
        return -1

    return 0


def score_mfi_mr_c(mfi_14: Real) -> float:
    mfi = _finite(mfi_14, "mfi_14")
    return clip((50.0 - mfi) / 30.0, -1.0, 1.0)


# ---------------------------------------------------------------------------
# OBV
# ---------------------------------------------------------------------------

def sig_obv_momentum_d(
    obv: Real,
    obv_sma_50: Real,
) -> int:
    obv_value = _finite(obv, "obv")
    obv_mean = _finite(obv_sma_50, "obv_sma_50")
    return sign3(obv_value - obv_mean)


def score_obv_momentum_c(
    obv: Real,
    obv_sma_50: Real,
    volume_sum_50: Real,
) -> float:
    obv_value = _finite(obv, "obv")
    obv_mean = _finite(obv_sma_50, "obv_sma_50")
    volume_sum = _finite(volume_sum_50, "volume_sum_50")

    if volume_sum < 0.0:
        raise ValueError("volume_sum_50 must be nonnegative")

    numerator = obv_value - obv_mean

    if volume_sum > 0.0:
        return clip(numerator / volume_sum, -1.0, 1.0)

    if numerator == 0.0:
        return 0.0

    raise SignalFormulaConflict(
        "SIG_OBV_ZERO_VOLUME_CONFLICT",
        "OBV differs from its SMA while 50-bar volume sum equals zero",
    )


# ---------------------------------------------------------------------------
# ROC
# ---------------------------------------------------------------------------

def sig_roc_momentum_d(roc_close_12_pct: Real) -> int:
    return sign3(roc_close_12_pct)


def score_roc_momentum_c(
    roc_close_12_pct: Real,
    atr_wilder_14: Real,
    close: Real,
) -> float:
    roc_pct = _finite(roc_close_12_pct, "roc_close_12_pct")
    atr = _finite(atr_wilder_14, "atr_wilder_14")
    close_value = _finite(close, "close")

    if atr < 0.0:
        raise ValueError("atr_wilder_14 must be nonnegative")

    if close_value <= 0.0:
        raise ValueError("close must be positive")

    atr_fraction = atr / close_value
    roc_fraction = roc_pct / 100.0

    if atr_fraction > 0.0:
        return clip(
            roc_fraction / atr_fraction,
            -1.0,
            1.0,
        )

    if roc_fraction == 0.0:
        return 0.0

    raise SignalFormulaConflict(
        "SIG_ROC_ZERO_ATR_CONFLICT",
        "ROC is nonzero while ATR fraction equals zero",
    )


# ---------------------------------------------------------------------------
# MA200 trend
# ---------------------------------------------------------------------------

def state_ma200_trend_d(
    close: Real,
    sma_close_200: Real,
) -> int:
    close_value = _finite(close, "close")
    sma = _finite(sma_close_200, "sma_close_200")
    return sign3(close_value - sma)


def score_ma200_trend_c(
    close: Real,
    sma_close_200: Real,
    atr_wilder_14: Real,
) -> float:
    close_value = _finite(close, "close")
    sma = _finite(sma_close_200, "sma_close_200")
    atr = _finite(atr_wilder_14, "atr_wilder_14")

    if atr < 0.0:
        raise ValueError("atr_wilder_14 must be nonnegative")

    numerator = close_value - sma

    if atr > 0.0:
        return clip(numerator / atr, -1.0, 1.0)

    if numerator == 0.0:
        return 0.0

    raise SignalFormulaConflict(
        "SIG_MA200_ZERO_ATR_CONFLICT",
        "close differs from SMA200 while ATR equals zero",
    )


# ---------------------------------------------------------------------------
# EMA50 trend
# ---------------------------------------------------------------------------

def state_ema50_trend_d(
    close: Real,
    ema_close_50: Real,
) -> int:
    close_value = _finite(close, "close")
    ema = _finite(ema_close_50, "ema_close_50")
    return sign3(close_value - ema)


def score_ema50_trend_c(
    close: Real,
    ema_close_50: Real,
    atr_wilder_14: Real,
) -> float:
    close_value = _finite(close, "close")
    ema = _finite(ema_close_50, "ema_close_50")
    atr = _finite(atr_wilder_14, "atr_wilder_14")

    if atr < 0.0:
        raise ValueError("atr_wilder_14 must be nonnegative")

    numerator = close_value - ema

    if atr > 0.0:
        return clip(numerator / atr, -1.0, 1.0)

    if numerator == 0.0:
        return 0.0

    raise SignalFormulaConflict(
        "SIG_EMA50_ZERO_ATR_CONFLICT",
        "close differs from EMA50 while ATR equals zero",
    )


# ---------------------------------------------------------------------------
# ATR relative volatility
# ---------------------------------------------------------------------------

def state_atr_relative_d(
    atr_wilder_14: Real,
    atr_sma_200: Real,
) -> int:
    atr = _finite(atr_wilder_14, "atr_wilder_14")
    atr_mean = _finite(atr_sma_200, "atr_sma_200")

    if atr < 0.0 or atr_mean < 0.0:
        raise ValueError("ATR values must be nonnegative")

    return sign3(atr - atr_mean)


def score_atr_relative_c(
    atr_wilder_14: Real,
    atr_sma_200: Real,
) -> float:
    atr = _finite(atr_wilder_14, "atr_wilder_14")
    atr_mean = _finite(atr_sma_200, "atr_sma_200")

    if atr < 0.0 or atr_mean < 0.0:
        raise ValueError("ATR values must be nonnegative")

    if atr > 0.0 and atr_mean > 0.0:
        return clip(
            math.log(atr / atr_mean) / math.log(2.0),
            -1.0,
            1.0,
        )

    if atr == 0.0 and atr_mean == 0.0:
        return 0.0

    if atr == 0.0 and atr_mean > 0.0:
        return -1.0

    raise SignalFormulaConflict(
        "SIG_ATR_RATIO_ZERO_CONFLICT",
        "ATR is positive while ATR-SMA200 equals zero",
    )


# ---------------------------------------------------------------------------
# ADX strength
# ---------------------------------------------------------------------------

def state_adx_strength_d(adx_wilder_14: Real) -> int:
    adx = _finite(adx_wilder_14, "adx_wilder_14")
    return 1 if adx > 25.0 else 0


def score_adx_strength_c(adx_wilder_14: Real) -> float:
    adx = _finite(adx_wilder_14, "adx_wilder_14")
    return clip((adx - 15.0) / 10.0, 0.0, 1.0)


__all__ = [
    "SignalFormulaConflict",
    "clip",
    "sign3",
    "sig_rsi_mr_d",
    "score_rsi_mr_c",
    "sig_macd_momentum_d",
    "score_macd_momentum_c",
    "sig_bollinger_mr_d",
    "score_bollinger_mr_c",
    "sig_stoch_mr_d",
    "score_stoch_mr_c",
    "sig_cci_mr_d",
    "score_cci_mr_c",
    "sig_mfi_mr_d",
    "score_mfi_mr_c",
    "sig_obv_momentum_d",
    "score_obv_momentum_c",
    "sig_roc_momentum_d",
    "score_roc_momentum_c",
    "state_ma200_trend_d",
    "score_ma200_trend_c",
    "state_ema50_trend_d",
    "score_ema50_trend_c",
    "state_atr_relative_d",
    "score_atr_relative_c",
    "state_adx_strength_d",
    "score_adx_strength_c",
]
