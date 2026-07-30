"""Canonical stateless RCC-002 S5 -> S6 gate computation."""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final

from rcc002.s5.constants import (
    REGIME_MODEL_ID,
    REGIME_MODEL_VERSION,
    REGIME_SCHEMA_ID,
    REGIME_SCHEMA_VERSION,
    RegimeState,
    TrendStrength,
)
from rcc002.s5.schema import S5Row
from rcc002.s6.constants import (
    DEFAULT_GATE_PROFILE_ID,
    GATE_PROFILE_IDS,
    GATE_PROFILE_VERSION,
    GATE_RESEARCH_OPEN_V1,
    GATE_SCHEMA_ID,
    GATE_SCHEMA_REF,
    GATE_SCHEMA_VERSION,
    GATE_TREND_ALIGNED_V1,
    GATE_TREND_STRENGTH_ALIGNED_V1,
    INTERVAL_MILLISECONDS,
    SUPPORTED_INTERVAL,
)
from rcc002.s6.formulas import derive_gate_state
from rcc002.s6.reason_codes import normalize_direction_reason_codes
from rcc002.s6.schema import S6Row


_S5_FIELD_NAMES: Final[tuple[str, ...]] = tuple(
    field.name for field in dataclasses.fields(S5Row)
)


@dataclass(frozen=True, slots=True)
class S6Result:
    rows: tuple[S6Row, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.rows, tuple):
            raise ValueError("rows must be a tuple")
        if any(not isinstance(row, S6Row) for row in self.rows):
            raise ValueError("rows may contain only S6Row instances")


def _copy_s5_values(row: S5Row) -> dict[str, object]:
    values = {name: getattr(row, name) for name in _S5_FIELD_NAMES}
    values["indicators"] = dict(row.indicators)
    values["signals"] = dict(row.signals)
    return values


def _validate_profile(
    gate_profile_id: str,
    gate_profile_version: str,
) -> None:
    if gate_profile_id not in GATE_PROFILE_IDS:
        raise ValueError("gate_profile_id is not registered")
    if gate_profile_version != GATE_PROFILE_VERSION:
        raise ValueError("gate_profile_version is incompatible")


def _validate_input_rows(rows: tuple[S5Row, ...]) -> None:
    series: tuple[str, str, str, str] | None = None
    previous: S5Row | None = None
    for index, row in enumerate(rows):
        if type(row) is not S5Row:
            raise TypeError(f"row {index} is not an S5Row")
        row.__post_init__()
        if row.regime_schema_id != REGIME_SCHEMA_ID:
            raise ValueError("unexpected S5 schema id")
        if row.regime_schema_version != REGIME_SCHEMA_VERSION:
            raise ValueError("unexpected S5 schema version")
        if row.regime_model_id != REGIME_MODEL_ID:
            raise ValueError("unexpected S5 regime model id")
        if row.regime_model_version != REGIME_MODEL_VERSION:
            raise ValueError("unexpected S5 regime model version")
        for name in (
            "provider",
            "market_type",
            "symbol",
            "market_segment_id",
            "indicator_segment_id",
        ):
            value = getattr(row, name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")
        if row.interval != SUPPORTED_INTERVAL:
            raise ValueError("S6 V1 supports only the 1m interval")
        key = (
            row.provider,
            row.market_type,
            row.symbol,
            row.interval,
        )
        if series is None:
            series = key
        elif key != series:
            raise ValueError("one S6 call may contain only one series")
        if previous is not None:
            if row.open_time <= previous.open_time:
                raise ValueError("S5 input is duplicated or unordered")
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


def _invalid_profile_reasons(
    row: S5Row,
    *,
    require_trend_strength: bool,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    common: list[str] = []
    if not row.regime_valid or row.regime_effective is RegimeState.UNKNOWN:
        if {
            "REG_WARMUP_INCOMPLETE",
            "REG_EFFECTIVE_UNCONFIRMED",
        } & set(row.regime_reason_codes):
            common.append("GATE_WARMUP_INCOMPLETE")
        if {
            "REG_SEGMENT_RESET",
            "REG_WINDOW_CROSSES_INDICATOR_SEGMENT",
        } & set(row.regime_reason_codes):
            common.append("GATE_SEGMENT_RESET")
        common.append("GATE_REGIME_UNKNOWN")

    if require_trend_strength and (
        not row.trend_strength_valid
        or row.trend_strength is TrendStrength.UNKNOWN
    ):
        common.append("GATE_TREND_STRENGTH_UNKNOWN")

    if not common:
        common.append("GATE_INPUT_INVALID")
    return (
        normalize_direction_reason_codes(common, direction="LONG"),
        normalize_direction_reason_codes(common, direction="SHORT"),
    )


def _evaluate_valid_profile(
    row: S5Row,
    *,
    gate_profile_id: str,
) -> tuple[bool, bool, tuple[str, ...], tuple[str, ...]]:
    if gate_profile_id == GATE_RESEARCH_OPEN_V1:
        return (
            True,
            True,
            ("GATE_LONG_ALLOWED_RESEARCH_OPEN",),
            ("GATE_SHORT_ALLOWED_RESEARCH_OPEN",),
        )

    regime = row.regime_effective
    if gate_profile_id == GATE_TREND_ALIGNED_V1:
        if regime is RegimeState.BULL:
            return (
                True,
                False,
                ("GATE_LONG_ALLOWED_BULL",),
                ("GATE_SHORT_BLOCKED_BULL",),
            )
        if regime is RegimeState.SIDE:
            return (
                False,
                False,
                ("GATE_LONG_BLOCKED_SIDE",),
                ("GATE_SHORT_BLOCKED_SIDE",),
            )
        if regime is RegimeState.BEAR:
            return (
                False,
                True,
                ("GATE_LONG_BLOCKED_BEAR",),
                ("GATE_SHORT_ALLOWED_BEAR",),
            )
        raise RuntimeError("validated trend profile has unknown regime")

    if gate_profile_id != GATE_TREND_STRENGTH_ALIGNED_V1:
        raise RuntimeError("unreachable gate profile")
    strength = row.trend_strength
    if strength is TrendStrength.WEAK:
        long_codes = ["GATE_LONG_BLOCKED_WEAK_TREND"]
        short_codes = ["GATE_SHORT_BLOCKED_WEAK_TREND"]
        if regime is RegimeState.BULL:
            short_codes.append("GATE_SHORT_BLOCKED_BULL")
        elif regime is RegimeState.SIDE:
            long_codes.append("GATE_LONG_BLOCKED_SIDE")
            short_codes.append("GATE_SHORT_BLOCKED_SIDE")
        elif regime is RegimeState.BEAR:
            long_codes.append("GATE_LONG_BLOCKED_BEAR")
        else:
            raise RuntimeError("validated strength profile has unknown regime")
        return (
            False,
            False,
            normalize_direction_reason_codes(
                long_codes, direction="LONG"
            ),
            normalize_direction_reason_codes(
                short_codes, direction="SHORT"
            ),
        )
    if strength not in (TrendStrength.DEVELOPING, TrendStrength.STRONG):
        raise RuntimeError("validated strength profile has unknown strength")
    if regime is RegimeState.BULL:
        return (
            True,
            False,
            ("GATE_LONG_ALLOWED_BULL_WITH_STRENGTH",),
            ("GATE_SHORT_BLOCKED_BULL",),
        )
    if regime is RegimeState.SIDE:
        return (
            False,
            False,
            ("GATE_LONG_BLOCKED_SIDE",),
            ("GATE_SHORT_BLOCKED_SIDE",),
        )
    if regime is RegimeState.BEAR:
        return (
            False,
            True,
            ("GATE_LONG_BLOCKED_BEAR",),
            ("GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH",),
        )
    raise RuntimeError("validated strength profile has unknown regime")


def compute_gates(
    s5_rows: Sequence[S5Row],
    *,
    gate_profile_id: str = DEFAULT_GATE_PROFILE_ID,
    gate_profile_version: str = GATE_PROFILE_VERSION,
) -> S6Result:
    """Evaluate exactly one registered S6 profile over canonical S5 rows."""

    _validate_profile(gate_profile_id, gate_profile_version)
    rows = tuple(s5_rows)
    if not rows:
        return S6Result(rows=())
    _validate_input_rows(rows)

    output: list[S6Row] = []
    for row in rows:
        data_gate_pass = row.quality_gate_pass
        if not data_gate_pass:
            gate_valid = True
            allow_long = False
            allow_short = False
            long_reasons = ("GATE_DATA_QUALITY_FAILED",)
            short_reasons = ("GATE_DATA_QUALITY_FAILED",)
        elif gate_profile_id == GATE_RESEARCH_OPEN_V1:
            gate_valid = True
            (
                allow_long,
                allow_short,
                long_reasons,
                short_reasons,
            ) = _evaluate_valid_profile(
                row, gate_profile_id=gate_profile_id
            )
        else:
            require_strength = (
                gate_profile_id
                == GATE_TREND_STRENGTH_ALIGNED_V1
            )
            profile_inputs_valid = (
                row.regime_valid
                and row.regime_effective is not RegimeState.UNKNOWN
                and (
                    not require_strength
                    or (
                        row.trend_strength_valid
                        and row.trend_strength
                        is not TrendStrength.UNKNOWN
                    )
                )
            )
            if not profile_inputs_valid:
                gate_valid = False
                allow_long = False
                allow_short = False
                long_reasons, short_reasons = _invalid_profile_reasons(
                    row, require_trend_strength=require_strength
                )
            else:
                gate_valid = True
                (
                    allow_long,
                    allow_short,
                    long_reasons,
                    short_reasons,
                ) = _evaluate_valid_profile(
                    row, gate_profile_id=gate_profile_id
                )

        long_reasons = normalize_direction_reason_codes(
            long_reasons, direction="LONG"
        )
        short_reasons = normalize_direction_reason_codes(
            short_reasons, direction="SHORT"
        )
        gate_state = derive_gate_state(
            gate_valid=gate_valid,
            allow_long=allow_long,
            allow_short=allow_short,
        )
        output.append(
            S6Row(
                **_copy_s5_values(row),
                allow_long=allow_long,
                allow_short=allow_short,
                data_gate_pass=data_gate_pass,
                gate_state=gate_state,
                gate_reason_codes_long=long_reasons,
                gate_reason_codes_short=short_reasons,
                gate_profile_id=gate_profile_id,
                gate_profile_version=gate_profile_version,
                gate_schema_id=GATE_SCHEMA_ID,
                gate_schema_version=GATE_SCHEMA_VERSION,
                gate_schema_ref=GATE_SCHEMA_REF,
                gate_valid=gate_valid,
                gate_evaluated_at=row.close_time,
            )
        )

    if len(output) != len(rows):
        raise RuntimeError("S6 row-count invariant failed")
    for source, result in zip(rows, output, strict=True):
        for name in _S5_FIELD_NAMES:
            source_value = getattr(source, name)
            result_value = getattr(result, name)
            if (
                source_value is not result_value
                and source_value != result_value
            ):
                raise RuntimeError(
                    f"S5 -> S6 preservation failed for {name}"
                )
    return S6Result(rows=tuple(output))


__all__ = ["S6Result", "compute_gates"]
