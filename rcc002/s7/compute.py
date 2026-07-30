"""Canonical optimized RCC-002 S6 -> S7 label computation."""

from __future__ import annotations

import bisect
import dataclasses
import math
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from rcc002.s6.constants import GATE_SCHEMA_ID, GATE_SCHEMA_VERSION
from rcc002.s6.schema import S6Row
from rcc002.s7.constants import (
    BARRIER_PROFILE_ID,
    BARRIER_PROFILE_VERSION,
    COST_PROFILE_ID,
    COST_PROFILE_VERSION,
    HORIZONS,
    HORIZON_REGISTRY_ID,
    HORIZON_REGISTRY_VERSION,
    INTERVAL_MILLISECONDS,
    LABEL_METADATA_VALUES,
    LABEL_PROFILE_ID,
    LABEL_PROFILE_VERSION,
    NUMERIC_PROFILE_ID,
    NUMERIC_PROFILE_VERSION,
    REASON_CODE_REGISTRY_VERSION,
    STOP_LOSS_FRACTION,
    SUPPORTED_INTERVAL,
    TAKE_PROFIT_FRACTION,
    BarrierOutcome,
)
from rcc002.s7.formulas import (
    barrier_outcome_at_bar,
    canonical_zero,
    direction_label,
    linear_returns,
    log_returns,
    net_proxy_return,
)
from rcc002.s7.reason_codes import normalize_reason_codes
from rcc002.s7.schema import HorizonLabels, S7Row


_S6_FIELD_NAMES: Final[tuple[str, ...]] = tuple(
    field.name for field in dataclasses.fields(S6Row)
)
_BARRIER_INFORMATION_CODES: Final[frozenset[str]] = frozenset(
    {"LBL_BARRIER_BOTH_HIT", "LBL_BARRIER_TIMEOUT"}
)


@dataclass(frozen=True, slots=True)
class S7Result:
    rows: tuple[S7Row, ...]

    def __post_init__(self) -> None:
        if type(self.rows) is not tuple:
            raise ValueError("rows must be a tuple")
        if any(type(row) is not S7Row for row in self.rows):
            raise ValueError("rows may contain only S7Row instances")


class _BarrierRangeIndex:
    """Range tree locating the first TP/SL candidate in O(log n)."""

    __slots__ = ("length", "max_values", "min_values", "size")

    def __init__(
        self,
        event_highs: tuple[float, ...],
        event_lows: tuple[float, ...],
    ) -> None:
        self.length = len(event_highs)
        size = 1
        while size < self.length:
            size *= 2
        self.size = size
        self.max_values = [-math.inf] * (2 * size)
        self.min_values = [math.inf] * (2 * size)
        for index, value in enumerate(event_highs):
            self.max_values[size + index] = value
        for index, value in enumerate(event_lows):
            self.min_values[size + index] = value
        for node in range(size - 1, 0, -1):
            self.max_values[node] = max(
                self.max_values[node * 2],
                self.max_values[node * 2 + 1],
            )
            self.min_values[node] = min(
                self.min_values[node * 2],
                self.min_values[node * 2 + 1],
            )

    def first_event(
        self,
        *,
        left: int,
        right: int,
        upper: float,
        lower: float,
    ) -> int | None:
        return self._first_event(
            node=1,
            node_left=0,
            node_right=self.size - 1,
            query_left=left,
            query_right=right,
            upper=upper,
            lower=lower,
        )

    def _first_event(
        self,
        *,
        node: int,
        node_left: int,
        node_right: int,
        query_left: int,
        query_right: int,
        upper: float,
        lower: float,
    ) -> int | None:
        if (
            node_right < query_left
            or node_left > query_right
            or (
                self.max_values[node] < upper
                and self.min_values[node] > lower
            )
        ):
            return None
        if node_left == node_right:
            return node_left if node_left < self.length else None
        midpoint = (node_left + node_right) // 2
        first = self._first_event(
            node=node * 2,
            node_left=node_left,
            node_right=midpoint,
            query_left=query_left,
            query_right=query_right,
            upper=upper,
            lower=lower,
        )
        if first is not None:
            return first
        return self._first_event(
            node=node * 2 + 1,
            node_left=midpoint + 1,
            node_right=node_right,
            query_left=query_left,
            query_right=query_right,
            upper=upper,
            lower=lower,
        )


@dataclass(frozen=True, slots=True)
class _BuildContext:
    rows: tuple[S6Row, ...]
    open_times: tuple[int, ...]
    time_to_index: dict[int, int]
    quality_ok: tuple[bool, ...]
    synthetic: tuple[bool, ...]
    open_valid: tuple[bool, ...]
    high_valid: tuple[bool, ...]
    low_valid: tuple[bool, ...]
    close_valid: tuple[bool, ...]
    high_values: tuple[float, ...]
    low_values: tuple[float, ...]
    bad_quality_prefix: tuple[int, ...]
    synthetic_prefix: tuple[int, ...]
    bad_high_low_prefix: tuple[int, ...]
    bad_ohl_prefix: tuple[int, ...]
    boundary_prefix: tuple[int, ...]
    barrier_index: _BarrierRangeIndex


def _copy_s6_values(row: S6Row) -> dict[str, object]:
    values = {name: getattr(row, name) for name in _S6_FIELD_NAMES}
    values["indicators"] = dict(row.indicators)
    values["signals"] = dict(row.signals)
    return values


def _validate_configuration(
    *,
    label_profile_id: str,
    label_profile_version: str,
    horizon_registry_id: str,
    horizon_registry_version: str,
    cost_profile_id: str,
    cost_profile_version: str,
    barrier_profile_id: str,
    barrier_profile_version: str,
    reason_code_registry_version: str,
    numeric_profile_id: str,
    numeric_profile_version: str,
) -> None:
    expected = {
        "label_profile_id": LABEL_PROFILE_ID,
        "label_profile_version": LABEL_PROFILE_VERSION,
        "horizon_registry_id": HORIZON_REGISTRY_ID,
        "horizon_registry_version": HORIZON_REGISTRY_VERSION,
        "cost_profile_id": COST_PROFILE_ID,
        "cost_profile_version": COST_PROFILE_VERSION,
        "barrier_profile_id": BARRIER_PROFILE_ID,
        "barrier_profile_version": BARRIER_PROFILE_VERSION,
        "reason_code_registry_version": REASON_CODE_REGISTRY_VERSION,
        "numeric_profile_id": NUMERIC_PROFILE_ID,
        "numeric_profile_version": NUMERIC_PROFILE_VERSION,
    }
    actual = {
        "label_profile_id": label_profile_id,
        "label_profile_version": label_profile_version,
        "horizon_registry_id": horizon_registry_id,
        "horizon_registry_version": horizon_registry_version,
        "cost_profile_id": cost_profile_id,
        "cost_profile_version": cost_profile_version,
        "barrier_profile_id": barrier_profile_id,
        "barrier_profile_version": barrier_profile_version,
        "reason_code_registry_version": reason_code_registry_version,
        "numeric_profile_id": numeric_profile_id,
        "numeric_profile_version": numeric_profile_version,
    }
    mismatches = [
        name for name in expected if actual[name] != expected[name]
    ]
    if mismatches:
        raise ValueError(
            "unknown or incompatible S7 configuration: "
            + ", ".join(mismatches)
        )


def _validate_input_rows(rows: tuple[S6Row, ...]) -> None:
    series: tuple[str, str, str, str] | None = None
    previous: S6Row | None = None
    seen_keys: set[tuple[str, str, str, str, int]] = set()
    for index, row in enumerate(rows):
        if type(row) is not S6Row:
            raise TypeError(f"row {index} is not an S6Row")
        row.__post_init__()
        if row.gate_schema_id != GATE_SCHEMA_ID:
            raise ValueError("unexpected S6 schema id")
        if row.gate_schema_version != GATE_SCHEMA_VERSION:
            raise ValueError("unexpected S6 schema version")
        if row.interval != SUPPORTED_INTERVAL:
            raise ValueError("S7 V1 supports only the 1m interval")
        for name in (
            "provider",
            "market_type",
            "symbol",
            "market_segment_id",
        ):
            value = getattr(row, name)
            if type(value) is not str or not value:
                raise ValueError(f"{name} must be a non-empty string")
        row_series = (
            row.provider,
            row.market_type,
            row.symbol,
            row.interval,
        )
        if series is None:
            series = row_series
        elif row_series != series:
            raise ValueError("one S7 call may contain only one series")
        key = (*row_series, row.open_time)
        if key in seen_keys:
            raise ValueError("S6 input contains a duplicate primary key")
        seen_keys.add(key)
        if previous is not None:
            if row.open_time <= previous.open_time:
                raise ValueError("S6 input is unordered")
            if (
                row.open_time - previous.open_time
                != INTERVAL_MILLISECONDS
                and row.market_segment_id == previous.market_segment_id
            ):
                raise ValueError(
                    "a timestamp gap requires a market-segment reset"
                )
        previous = row


def _price_valid(value: object) -> bool:
    return (
        type(value) in (int, float)
        and math.isfinite(float(value))
        and float(value) > 0.0
    )


def _quality_contract_passes(row: S6Row) -> bool:
    return (
        row.quality_gate_pass
        and row.quality_is_observed
        and not row.quality_is_synthetic
        and row.quality_timestamp_valid
        and row.quality_ohlc_valid
        and row.quality_market_values_valid
    )


def _prefix(values: Sequence[bool]) -> tuple[int, ...]:
    output = [0]
    total = 0
    for value in values:
        total += int(value)
        output.append(total)
    return tuple(output)


def _range_has(prefix: tuple[int, ...], left: int, right: int) -> bool:
    return prefix[right + 1] != prefix[left]


def _safe_price(value: object, invalid_value: float) -> float:
    return float(value) if _price_valid(value) else invalid_value


def _make_context(rows: tuple[S6Row, ...]) -> _BuildContext:
    quality_ok = tuple(_quality_contract_passes(row) for row in rows)
    synthetic = tuple(row.quality_is_synthetic for row in rows)
    open_valid = tuple(_price_valid(row.open) for row in rows)
    high_valid = tuple(_price_valid(row.high) for row in rows)
    low_valid = tuple(_price_valid(row.low) for row in rows)
    close_valid = tuple(_price_valid(row.close) for row in rows)
    high_values = tuple(
        _safe_price(row.high, -math.inf) for row in rows
    )
    low_values = tuple(_safe_price(row.low, math.inf) for row in rows)
    open_values_high = tuple(
        _safe_price(row.open, -math.inf) for row in rows
    )
    open_values_low = tuple(
        _safe_price(row.open, math.inf) for row in rows
    )
    event_highs = tuple(
        max(open_values_high[index], high_values[index])
        for index in range(len(rows))
    )
    event_lows = tuple(
        min(open_values_low[index], low_values[index])
        for index in range(len(rows))
    )
    boundaries = [False] * len(rows)
    for index in range(1, len(rows)):
        boundaries[index] = (
            rows[index].open_time - rows[index - 1].open_time
            != INTERVAL_MILLISECONDS
            or rows[index].market_segment_id
            != rows[index - 1].market_segment_id
        )
    return _BuildContext(
        rows=rows,
        open_times=tuple(row.open_time for row in rows),
        time_to_index={
            row.open_time: index for index, row in enumerate(rows)
        },
        quality_ok=quality_ok,
        synthetic=synthetic,
        open_valid=open_valid,
        high_valid=high_valid,
        low_valid=low_valid,
        close_valid=close_valid,
        high_values=high_values,
        low_values=low_values,
        bad_quality_prefix=_prefix(
            tuple(not value for value in quality_ok)
        ),
        synthetic_prefix=_prefix(synthetic),
        bad_high_low_prefix=_prefix(
            tuple(
                not (high_valid[index] and low_valid[index])
                for index in range(len(rows))
            )
        ),
        bad_ohl_prefix=_prefix(
            tuple(
                not (
                    open_valid[index]
                    and high_valid[index]
                    and low_valid[index]
                )
                for index in range(len(rows))
            )
        ),
        boundary_prefix=_prefix(boundaries),
        barrier_index=_BarrierRangeIndex(event_highs, event_lows),
    )


def _invalid_horizon(
    *,
    bars: int,
    reason: str,
    available_at: int | None,
) -> HorizonLabels:
    codes = (reason,)
    return HorizonLabels(
        label_horizon_bars=bars,
        label_available_at=available_at,
        fwd_cc_valid=False,
        fwd_cc_reason_codes=codes,
        fwd_cc_label_segment_id=None,
        fwd_cc_long_ret=None,
        fwd_cc_short_ret=None,
        fwd_cc_log_ret=None,
        fwd_cc_short_log_ret=None,
        fwd_noc_valid=False,
        fwd_noc_reason_codes=codes,
        fwd_noc_label_segment_id=None,
        fwd_noc_long_ret=None,
        fwd_noc_short_ret=None,
        fwd_noc_long_net_proxy_fee_rt_0004=None,
        fwd_noc_short_net_proxy_fee_rt_0004=None,
        fwd_excursion_valid=False,
        fwd_excursion_reason_codes=codes,
        fwd_excursion_label_segment_id=None,
        fwd_long_mfe=None,
        fwd_long_mae=None,
        fwd_short_mfe=None,
        fwd_short_mae=None,
        fwd_long_mfe_first_bar=None,
        fwd_long_mae_first_bar=None,
        fwd_short_mfe_first_bar=None,
        fwd_short_mae_first_bar=None,
        label_cc_direction_valid=False,
        label_cc_direction_reason_codes=codes,
        label_cc_direction_segment_id=None,
        label_cc_long_direction=None,
        label_cc_short_direction=None,
        label_noc_direction_valid=False,
        label_noc_direction_reason_codes=codes,
        label_noc_direction_segment_id=None,
        label_noc_long_direction=None,
        label_noc_short_direction=None,
        label_noc_long_net_proxy_fee_rt_0004_direction=None,
        label_noc_short_net_proxy_fee_rt_0004_direction=None,
        barrier_valid=False,
        barrier_reason_codes=codes,
        barrier_label_segment_id=None,
        barrier_long_outcome_tp050_sl020=BarrierOutcome.INVALID,
        barrier_short_outcome_tp050_sl020=BarrierOutcome.INVALID,
        barrier_long_first_hit_bar_tp050_sl020=None,
        barrier_short_first_hit_bar_tp050_sl020=None,
        barrier_long_first_hit_time_tp050_sl020=None,
        barrier_short_first_hit_time_tp050_sl020=None,
    )


def _current_reason_codes(
    context: _BuildContext,
    index: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not context.quality_ok[index]:
        reasons.append("LBL_INPUT_INVALID")
    if context.synthetic[index]:
        reasons.append("LBL_SYNTHETIC_INPUT_DISALLOWED")
    return normalize_reason_codes(reasons)


def _future_reason_codes_at(
    context: _BuildContext,
    indices: tuple[int, ...],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if any(not context.quality_ok[index] for index in indices):
        reasons.append("LBL_FUTURE_BAR_QUALITY_FAILED")
    if any(context.synthetic[index] for index in indices):
        reasons.append("LBL_SYNTHETIC_INPUT_DISALLOWED")
    return normalize_reason_codes(reasons)


def _future_reason_codes_range(
    context: _BuildContext,
    left: int,
    right: int,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if _range_has(context.bad_quality_prefix, left, right):
        reasons.append("LBL_FUTURE_BAR_QUALITY_FAILED")
    if _range_has(context.synthetic_prefix, left, right):
        reasons.append("LBL_SYNTHETIC_INPUT_DISALLOWED")
    return normalize_reason_codes(reasons)


def _rolling_extrema(
    context: _BuildContext,
    *,
    bars: int,
    output_row_count: int,
) -> list[tuple[float, float, int, int] | None]:
    """Calculate all [t+1, t+h] extrema in amortized O(n)."""

    output: list[tuple[float, float, int, int] | None] = [
        None
    ] * output_row_count
    maxima: deque[int] = deque()
    minima: deque[int] = deque()
    last_right = min(
        len(context.rows) - 1,
        output_row_count - 1 + bars,
    )
    for right in range(last_right + 1):
        high = context.high_values[right]
        while maxima and high > context.high_values[maxima[-1]]:
            maxima.pop()
        maxima.append(right)
        low = context.low_values[right]
        while minima and low < context.low_values[minima[-1]]:
            minima.pop()
        minima.append(right)

        index = right - bars
        if index < 0 or index >= output_row_count:
            continue
        while maxima and maxima[0] <= index:
            maxima.popleft()
        while minima and minima[0] <= index:
            minima.popleft()
        output[index] = (
            context.high_values[maxima[0]],
            context.low_values[minima[0]],
            maxima[0],
            minima[0],
        )
    return output


def _excursion_from_extrema(
    *,
    entry: float,
    index: int,
    extrema: tuple[float, float, int, int],
) -> tuple[float, float, float, float, int, int, int, int]:
    max_high, min_low, max_index, min_index = extrema
    long_mfe = canonical_zero((max_high / entry) - 1.0)
    long_mae = canonical_zero((min_low / entry) - 1.0)
    short_mfe = canonical_zero((entry - min_low) / entry)
    short_mae = canonical_zero((entry - max_high) / entry)
    values = (long_mfe, long_mae, short_mfe, short_mae)
    if any(not math.isfinite(value) for value in values):
        raise ArithmeticError("non-finite excursion")
    return (
        *values,
        max_index - index,
        min_index - index,
        min_index - index,
        max_index - index,
    )


def _barrier_for_direction(
    context: _BuildContext,
    *,
    direction: str,
    entry: float,
    index: int,
    end_index: int,
) -> tuple[BarrierOutcome, int | None, int | None]:
    if direction == "LONG":
        upper = entry * (1.0 + TAKE_PROFIT_FRACTION)
        lower = entry * (1.0 - STOP_LOSS_FRACTION)
    elif direction == "SHORT":
        upper = entry * (1.0 + STOP_LOSS_FRACTION)
        lower = entry * (1.0 - TAKE_PROFIT_FRACTION)
    else:
        raise ValueError("direction must be LONG or SHORT")
    hit_index = context.barrier_index.first_event(
        left=index + 1,
        right=end_index,
        upper=upper,
        lower=lower,
    )
    if hit_index is None:
        return BarrierOutcome.TIMEOUT, None, None
    row = context.rows[hit_index]
    outcome = barrier_outcome_at_bar(
        direction=direction,
        entry_price=entry,
        open_price=row.open,
        high_price=row.high,
        low_price=row.low,
    )
    if outcome is None:
        raise RuntimeError("barrier range index returned a false hit")
    return outcome, hit_index - index, row.close_time


def _barrier_values(
    context: _BuildContext,
    *,
    entry: float,
    index: int,
    end_index: int,
) -> tuple[
    BarrierOutcome,
    BarrierOutcome,
    int | None,
    int | None,
    int | None,
    int | None,
]:
    long_outcome, long_bar, long_time = _barrier_for_direction(
        context,
        direction="LONG",
        entry=entry,
        index=index,
        end_index=end_index,
    )
    short_outcome, short_bar, short_time = _barrier_for_direction(
        context,
        direction="SHORT",
        entry=entry,
        index=index,
        end_index=end_index,
    )
    return (
        long_outcome,
        short_outcome,
        long_bar,
        short_bar,
        long_time,
        short_time,
    )


def _all_finite(values: Sequence[float | None]) -> bool:
    return all(
        type(value) in (int, float) and math.isfinite(float(value))
        for value in values
    )


def _compute_complete_horizon(
    *,
    context: _BuildContext,
    index: int,
    end_index: int,
    bars: int,
    extrema: tuple[float, float, int, int],
) -> HorizonLabels:
    current = context.rows[index]
    entry_index = index + 1
    entry_row = context.rows[entry_index]
    end = context.rows[end_index]
    entry = float(entry_row.open) if context.open_valid[entry_index] else 0.0
    segment_id = current.market_segment_id
    common = list(_current_reason_codes(context, index))

    cc_reasons = common + list(
        _future_reason_codes_at(context, (end_index,))
    )
    if not context.close_valid[index]:
        cc_reasons.append("LBL_INPUT_INVALID")
    if not context.close_valid[end_index]:
        cc_reasons.append("LBL_EXIT_PRICE_INVALID")
    cc_reasons_tuple = normalize_reason_codes(cc_reasons)

    noc_indices = (
        (entry_index,)
        if entry_index == end_index
        else (entry_index, end_index)
    )
    noc_reasons = common + list(
        _future_reason_codes_at(context, noc_indices)
    )
    if not context.open_valid[entry_index]:
        noc_reasons.append("LBL_ENTRY_PRICE_INVALID")
    if not context.close_valid[end_index]:
        noc_reasons.append("LBL_EXIT_PRICE_INVALID")
    noc_reasons_tuple = normalize_reason_codes(noc_reasons)

    window_reasons = list(
        _future_reason_codes_range(context, entry_index, end_index)
    )
    excursion_reasons = common + window_reasons
    if not context.open_valid[entry_index]:
        excursion_reasons.append("LBL_ENTRY_PRICE_INVALID")
    if _range_has(
        context.bad_high_low_prefix, entry_index, end_index
    ):
        excursion_reasons.append("LBL_FUTURE_BAR_QUALITY_FAILED")
    excursion_reasons_tuple = normalize_reason_codes(excursion_reasons)

    barrier_reasons = common + window_reasons
    if not context.open_valid[entry_index]:
        barrier_reasons.append("LBL_ENTRY_PRICE_INVALID")
    if _range_has(context.bad_ohl_prefix, entry_index, end_index):
        barrier_reasons.append("LBL_FUTURE_BAR_QUALITY_FAILED")
    barrier_reasons_tuple = normalize_reason_codes(barrier_reasons)

    cc_values: tuple[float | None, ...] = (None,) * 4
    if not cc_reasons_tuple:
        try:
            cc_linear = linear_returns(current.close, end.close)
            cc_log = log_returns(current.close, end.close)
            cc_values = (*cc_linear, *cc_log)
            if not _all_finite(cc_values):
                raise ArithmeticError
        except (ArithmeticError, ValueError, OverflowError):
            cc_reasons_tuple = ("LBL_NONFINITE_RESULT",)
            cc_values = (None,) * 4

    noc_values: tuple[float | None, ...] = (None,) * 4
    if not noc_reasons_tuple:
        try:
            noc_linear = linear_returns(entry, end.close)
            noc_values = (
                *noc_linear,
                net_proxy_return(noc_linear[0]),
                net_proxy_return(noc_linear[1]),
            )
            if not _all_finite(noc_values):
                raise ArithmeticError
        except (ArithmeticError, ValueError, OverflowError):
            noc_reasons_tuple = ("LBL_NONFINITE_RESULT",)
            noc_values = (None,) * 4

    excursion: tuple[float | int | None, ...] = (None,) * 8
    if not excursion_reasons_tuple:
        try:
            excursion = _excursion_from_extrema(
                entry=entry,
                index=index,
                extrema=extrema,
            )
        except (ArithmeticError, ValueError, OverflowError):
            excursion_reasons_tuple = ("LBL_NONFINITE_RESULT",)
            excursion = (None,) * 8

    barrier: tuple[object, ...] = (
        BarrierOutcome.INVALID,
        BarrierOutcome.INVALID,
        None,
        None,
        None,
        None,
    )
    if not barrier_reasons_tuple:
        try:
            barrier = _barrier_values(
                context,
                entry=entry,
                index=index,
                end_index=end_index,
            )
            information: list[str] = []
            if BarrierOutcome.AMBIGUOUS_BOTH_HIT in barrier[:2]:
                information.append("LBL_BARRIER_BOTH_HIT")
            if BarrierOutcome.TIMEOUT in barrier[:2]:
                information.append("LBL_BARRIER_TIMEOUT")
            barrier_reasons_tuple = normalize_reason_codes(information)
        except (ArithmeticError, ValueError, OverflowError):
            barrier_reasons_tuple = ("LBL_NONFINITE_RESULT",)

    cc_valid = not cc_reasons_tuple
    noc_valid = not noc_reasons_tuple
    excursion_valid = not excursion_reasons_tuple
    barrier_valid = not (
        set(barrier_reasons_tuple) - _BARRIER_INFORMATION_CODES
    )
    if not barrier_valid:
        barrier = (
            BarrierOutcome.INVALID,
            BarrierOutcome.INVALID,
            None,
            None,
            None,
            None,
        )

    cc_directions = (
        (
            direction_label(cc_values[0]),
            direction_label(cc_values[1]),
        )
        if cc_valid
        else (None, None)
    )
    noc_directions = (
        tuple(direction_label(value) for value in noc_values)
        if noc_valid
        else (None, None, None, None)
    )

    return HorizonLabels(
        label_horizon_bars=bars,
        label_available_at=end.close_time,
        fwd_cc_valid=cc_valid,
        fwd_cc_reason_codes=cc_reasons_tuple,
        fwd_cc_label_segment_id=segment_id if cc_valid else None,
        fwd_cc_long_ret=cc_values[0],
        fwd_cc_short_ret=cc_values[1],
        fwd_cc_log_ret=cc_values[2],
        fwd_cc_short_log_ret=cc_values[3],
        fwd_noc_valid=noc_valid,
        fwd_noc_reason_codes=noc_reasons_tuple,
        fwd_noc_label_segment_id=segment_id if noc_valid else None,
        fwd_noc_long_ret=noc_values[0],
        fwd_noc_short_ret=noc_values[1],
        fwd_noc_long_net_proxy_fee_rt_0004=noc_values[2],
        fwd_noc_short_net_proxy_fee_rt_0004=noc_values[3],
        fwd_excursion_valid=excursion_valid,
        fwd_excursion_reason_codes=excursion_reasons_tuple,
        fwd_excursion_label_segment_id=(
            segment_id if excursion_valid else None
        ),
        fwd_long_mfe=excursion[0],
        fwd_long_mae=excursion[1],
        fwd_short_mfe=excursion[2],
        fwd_short_mae=excursion[3],
        fwd_long_mfe_first_bar=excursion[4],
        fwd_long_mae_first_bar=excursion[5],
        fwd_short_mfe_first_bar=excursion[6],
        fwd_short_mae_first_bar=excursion[7],
        label_cc_direction_valid=cc_valid,
        label_cc_direction_reason_codes=cc_reasons_tuple,
        label_cc_direction_segment_id=segment_id if cc_valid else None,
        label_cc_long_direction=cc_directions[0],
        label_cc_short_direction=cc_directions[1],
        label_noc_direction_valid=noc_valid,
        label_noc_direction_reason_codes=noc_reasons_tuple,
        label_noc_direction_segment_id=(
            segment_id if noc_valid else None
        ),
        label_noc_long_direction=noc_directions[0],
        label_noc_short_direction=noc_directions[1],
        label_noc_long_net_proxy_fee_rt_0004_direction=(
            noc_directions[2]
        ),
        label_noc_short_net_proxy_fee_rt_0004_direction=(
            noc_directions[3]
        ),
        barrier_valid=barrier_valid,
        barrier_reason_codes=barrier_reasons_tuple,
        barrier_label_segment_id=segment_id if barrier_valid else None,
        barrier_long_outcome_tp050_sl020=barrier[0],
        barrier_short_outcome_tp050_sl020=barrier[1],
        barrier_long_first_hit_bar_tp050_sl020=barrier[2],
        barrier_short_first_hit_bar_tp050_sl020=barrier[3],
        barrier_long_first_hit_time_tp050_sl020=barrier[4],
        barrier_short_first_hit_time_tp050_sl020=barrier[5],
    )


def _compute_horizon(
    *,
    context: _BuildContext,
    index: int,
    bars: int,
    extrema: tuple[float, float, int, int] | None,
) -> HorizonLabels:
    current = context.rows[index]
    target_open_time = (
        current.open_time + bars * INTERVAL_MILLISECONDS
    )
    if context.rows[-1].open_time < target_open_time:
        return _invalid_horizon(
            bars=bars,
            reason="LBL_FUTURE_HORIZON_INCOMPLETE",
            available_at=None,
        )
    end_index = context.time_to_index.get(target_open_time)
    if end_index is None:
        insertion = bisect.bisect_left(
            context.open_times, target_open_time
        )
        available_at = (
            context.rows[insertion].close_time
            if insertion < len(context.rows)
            else None
        )
        return _invalid_horizon(
            bars=bars,
            reason="LBL_WINDOW_CROSSES_MARKET_SEGMENT",
            available_at=available_at,
        )
    if (
        end_index - index != bars
        or _range_has(
            context.boundary_prefix, index + 1, end_index
        )
    ):
        return _invalid_horizon(
            bars=bars,
            reason="LBL_WINDOW_CROSSES_MARKET_SEGMENT",
            available_at=context.rows[end_index].close_time,
        )
    if extrema is None:
        raise RuntimeError("complete horizon is missing rolling extrema")
    return _compute_complete_horizon(
        context=context,
        index=index,
        end_index=end_index,
        bars=bars,
        extrema=extrema,
    )


def compute_labels(
    s6_rows: Sequence[S6Row],
    *,
    output_row_count: int | None = None,
    label_profile_id: str = LABEL_PROFILE_ID,
    label_profile_version: str = LABEL_PROFILE_VERSION,
    horizon_registry_id: str = HORIZON_REGISTRY_ID,
    horizon_registry_version: str = HORIZON_REGISTRY_VERSION,
    cost_profile_id: str = COST_PROFILE_ID,
    cost_profile_version: str = COST_PROFILE_VERSION,
    barrier_profile_id: str = BARRIER_PROFILE_ID,
    barrier_profile_version: str = BARRIER_PROFILE_VERSION,
    reason_code_registry_version: str = REASON_CODE_REGISTRY_VERSION,
    numeric_profile_id: str = NUMERIC_PROFILE_ID,
    numeric_profile_version: str = NUMERIC_PROFILE_VERSION,
) -> S7Result:
    """Build S7 labels with read-only partition overlap support."""

    _validate_configuration(
        label_profile_id=label_profile_id,
        label_profile_version=label_profile_version,
        horizon_registry_id=horizon_registry_id,
        horizon_registry_version=horizon_registry_version,
        cost_profile_id=cost_profile_id,
        cost_profile_version=cost_profile_version,
        barrier_profile_id=barrier_profile_id,
        barrier_profile_version=barrier_profile_version,
        reason_code_registry_version=reason_code_registry_version,
        numeric_profile_id=numeric_profile_id,
        numeric_profile_version=numeric_profile_version,
    )
    rows = tuple(s6_rows)
    if output_row_count is None:
        output_row_count = len(rows)
    if (
        type(output_row_count) is not int
        or not 0 <= output_row_count <= len(rows)
    ):
        raise ValueError("output_row_count must be in 0...len(rows)")
    if not rows:
        return S7Result(rows=())
    _validate_input_rows(rows)
    context = _make_context(rows)
    horizon_maps: list[dict[str, HorizonLabels]] = [
        {} for _ in range(output_row_count)
    ]
    for horizon in HORIZONS:
        extrema = _rolling_extrema(
            context,
            bars=horizon.bars,
            output_row_count=output_row_count,
        )
        for index in range(output_row_count):
            horizon_maps[index][horizon.horizon_id] = _compute_horizon(
                context=context,
                index=index,
                bars=horizon.bars,
                extrema=extrema[index],
            )

    output = [
        S7Row(
            **_copy_s6_values(rows[index]),
            **LABEL_METADATA_VALUES,
            horizons=horizon_maps[index],
        )
        for index in range(output_row_count)
    ]
    if len(output) != output_row_count:
        raise RuntimeError("S7 row-count invariant failed")
    for source, result in zip(
        rows[:output_row_count], output, strict=True
    ):
        for name in _S6_FIELD_NAMES:
            source_value = getattr(source, name)
            result_value = getattr(result, name)
            if (
                source_value is not result_value
                and source_value != result_value
            ):
                raise RuntimeError(
                    f"S6 -> S7 preservation failed for {name}"
                )
    return S7Result(rows=tuple(output))


__all__ = ["S7Result", "compute_labels"]
