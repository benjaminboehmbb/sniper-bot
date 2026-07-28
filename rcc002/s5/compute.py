"""Canonical serial RCC-002 S4 -> S5 regime computation."""

from __future__ import annotations

import dataclasses
import math
from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Integral, Real
from typing import Final

from rcc002.s3.schema import IndicatorField
from rcc002.s4.constants import (
    SIGNAL_BASE_FIELDS,
    SIGNAL_PROFILE_ID,
    SIGNAL_PROFILE_VERSION,
    SIGNAL_SCHEMA_ID,
    SIGNAL_SCHEMA_VERSION,
)
from rcc002.s4.schema import S4Row, SignalField
from rcc002.s5 import formulas
from rcc002.s5.constants import (
    CONFIRM_BARS,
    INTERVAL_MILLISECONDS,
    REGIME_METADATA_VALUES,
    SLOPE_LOOKBACK_BARS,
    SUPPORTED_INTERVAL,
    RegimeState,
    TrendStrength,
    VolatilityRelative,
)
from rcc002.s5.formulas import (
    RegimeFormulaError,
    SlopeDenominatorInvalid,
)
from rcc002.s5.reason_codes import normalize_reason_codes
from rcc002.s5.schema import S5Row
from rcc002.s5.state import (
    RegimeStateSnapshot,
    compute_state_hash,
    make_state_snapshot,
)


_S4_FIELD_NAMES: Final[tuple[str, ...]] = tuple(
    field.name for field in dataclasses.fields(S4Row)
)


@dataclass(frozen=True, slots=True)
class S5Result:
    rows: tuple[S5Row, ...]
    final_state: RegimeStateSnapshot | None
    prior_state_accepted: bool

    def __post_init__(self) -> None:
        if not isinstance(self.rows, tuple):
            raise ValueError("rows must be a tuple")
        if any(not isinstance(row, S5Row) for row in self.rows):
            raise ValueError("rows may contain only S5Row instances")
        if (
            self.final_state is not None
            and not isinstance(self.final_state, RegimeStateSnapshot)
        ):
            raise ValueError("final_state must be a RegimeStateSnapshot")
        if type(self.prior_state_accepted) is not bool:
            raise ValueError("prior_state_accepted must be Boolean")


def _copy_s4_values(row: S4Row) -> dict[str, object]:
    values = {
        name: getattr(row, name)
        for name in _S4_FIELD_NAMES
    }
    # S3/S4 use mutable dict containers around immutable field values.
    # Give S5 independent containers so later consumers cannot mutate an
    # upstream in-memory row through a shared dictionary reference.
    values["indicators"] = dict(row.indicators)
    values["signals"] = dict(row.signals)
    return values


def _finite_real(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, Real)
        and math.isfinite(float(value))
    )


def _valid_indicator(row: S4Row, name: str) -> float | None:
    field = row.indicators.get(name)
    if (
        not isinstance(field, IndicatorField)
        or not field.valid
        or not field.warmup_complete
        or field.value is None
        or not _finite_real(field.value)
    ):
        return None
    return float(field.value)


def _valid_signal(row: S4Row, name: str) -> int | float | None:
    field = row.signals.get(name)
    if (
        not isinstance(field, SignalField)
        or not field.valid
        or field.value is None
        or isinstance(field.value, bool)
        or not isinstance(field.value, Real)
        or not math.isfinite(float(field.value))
    ):
        return None
    return field.value


def _validate_input_rows(rows: tuple[S4Row, ...]) -> None:
    series: tuple[str, str, str] | None = None
    previous: S4Row | None = None
    for index, row in enumerate(rows):
        if type(row) is not S4Row:
            raise TypeError(f"row {index} is not an S4Row")
        row.__post_init__()
        if row.signal_schema_id != SIGNAL_SCHEMA_ID:
            raise ValueError("unexpected S4 schema id")
        if row.signal_schema_version != SIGNAL_SCHEMA_VERSION:
            raise ValueError("unexpected S4 schema version")
        if row.signal_profile_id != SIGNAL_PROFILE_ID:
            raise ValueError("unexpected S4 signal profile id")
        if row.signal_profile_version != SIGNAL_PROFILE_VERSION:
            raise ValueError("unexpected S4 signal profile version")
        if tuple(row.signals) != SIGNAL_BASE_FIELDS:
            raise ValueError("S4 signal registry is not canonical")
        for name in (
            "market_type",
            "symbol",
            "market_segment_id",
            "indicator_segment_id",
        ):
            if not isinstance(getattr(row, name), str) or not getattr(
                row, name
            ):
                raise ValueError(f"{name} must be a non-empty string")
        if row.interval != SUPPORTED_INTERVAL:
            raise ValueError("S5 V1 supports only the 1m interval")
        key = (row.market_type, row.symbol, row.interval)
        if series is None:
            series = key
        elif key != series:
            raise ValueError("one S5 call may contain only one series")
        if previous is not None:
            if row.open_time <= previous.open_time:
                raise ValueError("S4 input is duplicated or unordered")
            if (
                row.open_time - previous.open_time
                != INTERVAL_MILLISECONDS
                and row.indicator_segment_id
                == previous.indicator_segment_id
            ):
                raise ValueError(
                    "a timestamp gap requires an indicator-segment reset"
                )
            if (
                row.indicator_segment_id
                == previous.indicator_segment_id
                and (
                    row.quality_gap_before
                    or previous.quality_gap_after
                )
            ):
                raise ValueError(
                    "a declared gap requires an indicator-segment reset"
                )
        previous = row


def _prior_state_status(
    prior: RegimeStateSnapshot | None,
    first: S4Row,
    parent_build_id: str,
) -> tuple[bool, bool]:
    """Return ``(continuation_accepted, trusted_segment_boundary)``."""

    if type(prior) is not RegimeStateSnapshot:
        return False, False
    try:
        prior.__post_init__()
        checksum_valid = (
            bool(prior.state_payload_sha256)
            and prior.state_payload_sha256 == compute_state_hash(prior)
        )
    except (TypeError, ValueError):
        return False, False
    direct_predecessor = (
        checksum_valid
        and prior.parent_build_id == parent_build_id
        and prior.market_type == first.market_type
        and prior.symbol == first.symbol
        and prior.interval == first.interval
        and prior.last_open_time + INTERVAL_MILLISECONDS
        == first.open_time
    )
    if not direct_predecessor:
        return False, False
    same_segments = (
        prior.market_segment_id == first.market_segment_id
        and prior.indicator_segment_id == first.indicator_segment_id
    )
    return same_segments, not same_segments


def _context_fields(
    row: S4Row,
) -> tuple[
    TrendStrength, bool, tuple[str, ...],
    VolatilityRelative, bool, tuple[str, ...],
]:
    adx = _valid_indicator(row, "adx_wilder_14")
    if adx is None:
        trend = TrendStrength.UNKNOWN
        trend_valid = False
        trend_reasons = ("REG_TREND_STRENGTH_INPUT_INVALID",)
    else:
        try:
            trend = formulas.classify_trend_strength(adx)
            trend_valid = True
            trend_reasons = ()
        except RegimeFormulaError:
            trend = TrendStrength.UNKNOWN
            trend_valid = False
            trend_reasons = ("REG_TREND_STRENGTH_INPUT_INVALID",)

    atr_state = _valid_signal(row, "state_atr_relative_d")
    if not isinstance(atr_state, Integral):
        volatility = VolatilityRelative.UNKNOWN
        volatility_valid = False
        volatility_reasons = ("REG_VOLATILITY_INPUT_INVALID",)
    else:
        try:
            volatility = formulas.classify_volatility_relative(
                int(atr_state)
            )
            volatility_valid = True
            volatility_reasons = ()
        except RegimeFormulaError:
            volatility = VolatilityRelative.UNKNOWN
            volatility_valid = False
            volatility_reasons = ("REG_VOLATILITY_INPUT_INVALID",)

    return (
        trend,
        trend_valid,
        normalize_reason_codes(trend_reasons),
        volatility,
        volatility_valid,
        normalize_reason_codes(volatility_reasons),
    )


def _advance_confirmation(
    raw: RegimeState,
    effective: RegimeState,
    candidate: RegimeState,
    count: int,
) -> tuple[
    RegimeState,
    RegimeState,
    int,
    bool,
    RegimeState | None,
    RegimeState | None,
]:
    """Advance the exact three-confirmation persisted state machine."""

    if raw is RegimeState.UNKNOWN:
        transition = effective is not RegimeState.UNKNOWN
        return (
            RegimeState.UNKNOWN,
            RegimeState.UNKNOWN,
            0,
            transition,
            effective if transition else None,
            RegimeState.UNKNOWN if transition else None,
        )

    new_count = (
        min(count + 1, CONFIRM_BARS)
        if candidate is raw
        else 1
    )
    transition = (
        new_count >= CONFIRM_BARS and raw is not effective
    )
    new_effective = raw if transition else effective
    return (
        new_effective,
        raw,
        new_count,
        transition,
        effective if transition else None,
        raw if transition else None,
    )


def compute_regimes(
    s4_rows: Sequence[S4Row],
    *,
    parent_build_id: str,
    prior_state: RegimeStateSnapshot | None = None,
) -> S5Result:
    """Compute S5 regimes serially and return a resumable final snapshot."""

    if not isinstance(parent_build_id, str) or not parent_build_id:
        raise ValueError("parent_build_id must be a non-empty string")
    rows = tuple(s4_rows)
    if not rows:
        return S5Result(
            rows=(), final_state=None, prior_state_accepted=False
        )
    _validate_input_rows(rows)

    accepted, initial_segment_reset = _prior_state_status(
        prior_state, rows[0], parent_build_id
    )
    if accepted:
        assert prior_state is not None
        context = list(prior_state.sma200_context_state)
        effective = prior_state.regime_effective
        candidate = prior_state.regime_candidate
        candidate_count = prior_state.regime_candidate_count
    else:
        context = []
        effective = (
            prior_state.regime_effective
            if initial_segment_reset
            and isinstance(prior_state, RegimeStateSnapshot)
            else RegimeState.UNKNOWN
        )
        candidate = RegimeState.UNKNOWN
        candidate_count = 0

    output: list[S5Row] = []
    previous: S4Row | None = None

    for index, row in enumerate(rows):
        segment_reset = (
            (index == 0 and initial_segment_reset)
            or (
                previous is not None
                and (
                    row.market_segment_id
                    != previous.market_segment_id
                    or row.indicator_segment_id
                    != previous.indicator_segment_id
                )
            )
        )
        if segment_reset:
            context = []
            candidate = RegimeState.UNKNOWN
            candidate_count = 0

        reasons: list[str] = []
        if segment_reset:
            reasons.extend(
                (
                    "REG_WINDOW_CROSSES_INDICATOR_SEGMENT",
                    "REG_SEGMENT_RESET",
                )
            )
        if not row.quality_gate_pass:
            reasons.append("REG_INPUT_QUALITY_GATE_FAILED")

        sma = _valid_indicator(row, "sma_close_200")
        close = float(row.close) if _finite_real(row.close) else None
        if (
            sma is None
            or sma <= 0.0
            or close is None
            or close <= 0.0
        ):
            reasons.append("REG_INPUT_INVALID")

        slope: float | None = None
        raw = RegimeState.UNKNOWN
        required_inputs_valid = (
            row.quality_gate_pass
            and sma is not None
            and sma > 0.0
            and close is not None
            and close > 0.0
        )
        if required_inputs_valid:
            if len(context) < SLOPE_LOOKBACK_BARS:
                reasons.append("REG_WARMUP_INCOMPLETE")
            else:
                try:
                    slope = formulas.ma200_slope_1440_pct(
                        sma, context[0]
                    )
                    raw = formulas.classify_raw_regime(
                        close, sma, slope
                    )
                except SlopeDenominatorInvalid:
                    reasons.append("REG_SLOPE_DENOMINATOR_INVALID")
                except RegimeFormulaError:
                    reasons.append("REG_NONFINITE_RESULT")

        (
            row_effective,
            row_candidate,
            row_candidate_count,
            transition,
            transition_from,
            transition_to,
        ) = _advance_confirmation(
            raw, effective, candidate, candidate_count
        )
        effective = row_effective
        candidate = row_candidate
        candidate_count = row_candidate_count

        if (
            raw is not RegimeState.UNKNOWN
            and effective is RegimeState.UNKNOWN
        ):
            reasons.append("REG_EFFECTIVE_UNCONFIRMED")

        normalized_reasons = normalize_reason_codes(reasons)
        regime_valid = (
            raw is not RegimeState.UNKNOWN
            and effective is not RegimeState.UNKNOWN
            and slope is not None
            and not normalized_reasons
        )
        (
            trend,
            trend_valid,
            trend_reasons,
            volatility,
            volatility_valid,
            volatility_reasons,
        ) = _context_fields(row)

        output.append(
            S5Row(
                **_copy_s4_values(row),
                regime_raw=raw,
                regime_effective=effective,
                regime_candidate=row_candidate,
                regime_candidate_count=row_candidate_count,
                regime_transition_flag=transition,
                regime_transition_from=transition_from,
                regime_transition_to=transition_to,
                ma200_slope_1440_pct=slope,
                trend_strength=trend,
                trend_strength_valid=trend_valid,
                trend_strength_reason_codes=trend_reasons,
                volatility_relative=volatility,
                volatility_relative_valid=volatility_valid,
                volatility_relative_reason_codes=volatility_reasons,
                **REGIME_METADATA_VALUES,
                regime_valid=regime_valid,
                regime_reason_codes=normalized_reasons,
            )
        )

        context_input_valid = sma is not None
        if context_input_valid:
            assert sma is not None
            context.append(sma)
            if len(context) > SLOPE_LOOKBACK_BARS:
                del context[0]
        else:
            context = []
            effective = RegimeState.UNKNOWN
            candidate = RegimeState.UNKNOWN
            candidate_count = 0

        previous = row

    final = rows[-1]
    final_state = make_state_snapshot(
        parent_build_id=parent_build_id,
        market_type=final.market_type,
        symbol=final.symbol,
        interval=final.interval,
        last_open_time=final.open_time,
        market_segment_id=final.market_segment_id,
        indicator_segment_id=final.indicator_segment_id,
        sma200_context_state=tuple(context),
        regime_effective=effective,
        regime_candidate=candidate,
        regime_candidate_count=candidate_count,
    )

    if len(output) != len(rows):
        raise RuntimeError("S5 row-count invariant failed")
    for source, result in zip(rows, output, strict=True):
        for name in _S4_FIELD_NAMES:
            source_value = getattr(source, name)
            result_value = getattr(result, name)
            if (
                source_value is not result_value
                and source_value != result_value
            ):
                raise RuntimeError(
                    f"S4 -> S5 preservation failed for {name}"
                )

    return S5Result(
        rows=tuple(output),
        final_state=final_state,
        prior_state_accepted=accepted,
    )


__all__ = ["S5Result", "compute_regimes"]
