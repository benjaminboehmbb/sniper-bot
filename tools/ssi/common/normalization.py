from __future__ import annotations

from math import isfinite


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    if lower > upper:
        raise ValueError("lower bound must be <= upper bound")

    if not isfinite(value):
        raise ValueError(f"value must be finite: {value}")

    return max(lower, min(upper, value))


def normalize_linear(
    value: float,
    *,
    lower: float,
    upper: float,
    invert: bool = False,
) -> float:
    if lower >= upper:
        raise ValueError("lower must be < upper")

    if not isfinite(value):
        raise ValueError(f"value must be finite: {value}")

    normalized = (value - lower) / (upper - lower)
    normalized = clamp(normalized)

    if invert:
        normalized = 1.0 - normalized

    return clamp(normalized)


def normalize_symmetric(
    value: float,
    *,
    scale: float,
    center: float = 0.0,
) -> float:
    if scale <= 0:
        raise ValueError("scale must be > 0")

    shifted = value - center
    normalized = 0.5 + (shifted / (2.0 * scale))

    return clamp(normalized)


def normalize_abs_penalty(
    value: float,
    *,
    max_abs: float,
) -> float:
    if max_abs <= 0:
        raise ValueError("max_abs must be > 0")

    penalty = abs(value) / max_abs
    return clamp(1.0 - penalty)


def bool_score(value: bool) -> float:
    return 1.0 if value else 0.0
