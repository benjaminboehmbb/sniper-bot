"""Pure Float64 formula helpers for RCC-002 S7."""

from __future__ import annotations

import math
from collections.abc import Sequence

from rcc002.s7.constants import (
    STOP_LOSS_FRACTION,
    TAKE_PROFIT_FRACTION,
    TOTAL_COST_FRACTION,
    BarrierOutcome,
)


def _finite_positive(value: float) -> float:
    if type(value) not in (int, float):
        raise ValueError("price must be an int or float")
    result = float(value)
    if not math.isfinite(result) or result <= 0.0:
        raise ValueError("price must be finite and strictly positive")
    return result


def canonical_zero(value: float) -> float:
    """Normalize IEEE-754 negative zero to canonical positive zero."""

    return 0.0 if value == 0.0 else value


def linear_returns(
    entry_price: float,
    exit_price: float,
) -> tuple[float, float]:
    entry = _finite_positive(entry_price)
    exit_ = _finite_positive(exit_price)
    long_return = canonical_zero((exit_ / entry) - 1.0)
    # The normative identity short_return = -long_return is materialized
    # directly so it remains bit-exact in binary64.
    short_return = canonical_zero(-long_return)
    if not math.isfinite(long_return) or not math.isfinite(short_return):
        raise ArithmeticError("non-finite linear return")
    return long_return, short_return


def log_returns(
    entry_price: float,
    exit_price: float,
) -> tuple[float, float]:
    entry = _finite_positive(entry_price)
    exit_ = _finite_positive(exit_price)
    long_return = canonical_zero(math.log(exit_ / entry))
    short_return = canonical_zero(-long_return)
    if not math.isfinite(long_return) or not math.isfinite(short_return):
        raise ArithmeticError("non-finite log return")
    return long_return, short_return


def net_proxy_return(gross_return: float) -> float:
    result = canonical_zero(float(gross_return) - TOTAL_COST_FRACTION)
    if not math.isfinite(result):
        raise ArithmeticError("non-finite net proxy return")
    return result


def direction_label(value: float) -> int:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("direction input must be finite")
    if result > 0.0:
        return 1
    if result < 0.0:
        return -1
    return 0


def excursion_values(
    *,
    entry_price: float,
    highs: Sequence[float],
    lows: Sequence[float],
) -> tuple[float, float, float, float, int, int, int, int]:
    entry = _finite_positive(entry_price)
    if not highs or len(highs) != len(lows):
        raise ValueError("excursion window must be non-empty and aligned")
    high_values = tuple(_finite_positive(value) for value in highs)
    low_values = tuple(_finite_positive(value) for value in lows)
    max_high = max(high_values)
    min_low = min(low_values)
    max_high_offset = high_values.index(max_high) + 1
    min_low_offset = low_values.index(min_low) + 1
    long_mfe = canonical_zero((max_high / entry) - 1.0)
    long_mae = canonical_zero((min_low / entry) - 1.0)
    short_mfe = canonical_zero((entry - min_low) / entry)
    short_mae = canonical_zero((entry - max_high) / entry)
    values = (long_mfe, long_mae, short_mfe, short_mae)
    if any(not math.isfinite(value) for value in values):
        raise ArithmeticError("non-finite excursion")
    return (
        *values,
        max_high_offset,
        min_low_offset,
        min_low_offset,
        max_high_offset,
    )


def _barrier_for_direction(
    *,
    direction: str,
    entry_price: float,
    future_rows: Sequence[tuple[float, float, float, int]],
) -> tuple[BarrierOutcome, int | None, int | None]:
    entry = _finite_positive(entry_price)
    for offset, (open_, high, low, close_time) in enumerate(
        future_rows, start=1
    ):
        outcome = barrier_outcome_at_bar(
            direction=direction,
            entry_price=entry,
            open_price=open_,
            high_price=high,
            low_price=low,
        )
        if outcome is not None:
            return outcome, offset, int(close_time)

    return BarrierOutcome.TIMEOUT, None, None


def barrier_outcome_at_bar(
    *,
    direction: str,
    entry_price: float,
    open_price: float,
    high_price: float,
    low_price: float,
) -> BarrierOutcome | None:
    """Evaluate one bar after the first-hit index has been located."""

    entry = _finite_positive(entry_price)
    open_value = _finite_positive(open_price)
    high_value = _finite_positive(high_price)
    low_value = _finite_positive(low_price)
    if direction == "LONG":
        tp_price = entry * (1.0 + TAKE_PROFIT_FRACTION)
        sl_price = entry * (1.0 - STOP_LOSS_FRACTION)
        if open_value >= tp_price:
            return BarrierOutcome.TP_FIRST
        if open_value <= sl_price:
            return BarrierOutcome.SL_FIRST
        tp_hit = high_value >= tp_price
        sl_hit = low_value <= sl_price
    elif direction == "SHORT":
        tp_price = entry * (1.0 - TAKE_PROFIT_FRACTION)
        sl_price = entry * (1.0 + STOP_LOSS_FRACTION)
        if open_value <= tp_price:
            return BarrierOutcome.TP_FIRST
        if open_value >= sl_price:
            return BarrierOutcome.SL_FIRST
        tp_hit = low_value <= tp_price
        sl_hit = high_value >= sl_price
    else:
        raise ValueError("direction must be LONG or SHORT")

    if tp_hit and sl_hit:
        return BarrierOutcome.AMBIGUOUS_BOTH_HIT
    if tp_hit:
        return BarrierOutcome.TP_FIRST
    if sl_hit:
        return BarrierOutcome.SL_FIRST
    return None


def barrier_outcomes(
    *,
    entry_price: float,
    future_rows: Sequence[tuple[float, float, float, int]],
) -> tuple[
    BarrierOutcome,
    BarrierOutcome,
    int | None,
    int | None,
    int | None,
    int | None,
]:
    if not future_rows:
        raise ValueError("barrier window must be non-empty")
    long_outcome, long_bar, long_time = _barrier_for_direction(
        direction="LONG",
        entry_price=entry_price,
        future_rows=future_rows,
    )
    short_outcome, short_bar, short_time = _barrier_for_direction(
        direction="SHORT",
        entry_price=entry_price,
        future_rows=future_rows,
    )
    return (
        long_outcome,
        short_outcome,
        long_bar,
        short_bar,
        long_time,
        short_time,
    )


__all__ = [
    "barrier_outcome_at_bar",
    "barrier_outcomes",
    "canonical_zero",
    "direction_label",
    "excursion_values",
    "linear_returns",
    "log_returns",
    "net_proxy_return",
]
