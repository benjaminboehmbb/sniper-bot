"""Canonical RCC-002 S4 signal-transformation orchestration.

This module performs the full serial S3 -> S4 build.  It coordinates the
certified pure formulas, field-local validity propagation, additional S4
rolling warm-up, reason-code assignment, output construction, and S3 -> S4
reconciliation.

It deliberately does not own mathematical signal definitions, reason-code
normalization, or the S4 row schema.  Those responsibilities belong to
``rcc002.s4.formulas``, ``rcc002.s4.reason_codes``, and
``rcc002.s4.schema`` respectively.

Scope:

* full serial, row-preserving, order-preserving builds;
* causal 50-row OBV/volume and 200-row ATR helpers;
* no segment creation or modification;
* no regime, gate, strategy, return, or label logic;
* partitioned execution requires caller-supplied overlap until the separately
  reviewed S4 state-snapshot continuation contract is implemented.
"""

from __future__ import annotations

import dataclasses
import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from numbers import Integral, Real
from types import MappingProxyType
from typing import Final, TypeAlias

from rcc002.s3.constants import (
    INDICATOR_FIELD_ALLOWLIST,
    INDICATOR_PROFILE_ID,
    INDICATOR_PROFILE_VERSION,
    INDICATOR_SCHEMA_ID,
    INDICATOR_SCHEMA_VERSION,
)
from rcc002.s3.schema import IndicatorField, S3Row
from rcc002.s4 import formulas
from rcc002.s4.constants import (
    EXPECTED_INPUT_SCHEMA_ID,
    EXPECTED_INPUT_SCHEMA_VERSION,
    FIELD_DEFINITIONS,
    SIGNAL_BASE_FIELDS,
    SIGNAL_METADATA_VALUES,
)
from rcc002.s4.formulas import SignalFormulaConflict
from rcc002.s4.reason_codes import normalize_reason_codes
from rcc002.s4.schema import S4Row, SignalField


SignalValue: TypeAlias = int | float
Formula: TypeAlias = Callable[..., SignalValue]


@dataclass(frozen=True, slots=True)
class S4Result:
    """Immutable result of one full serial S4 build."""

    rows: tuple[S4Row, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.rows, tuple):
            raise ValueError("rows must be a tuple")
        if any(not isinstance(row, S4Row) for row in self.rows):
            raise ValueError("rows may contain only S4Row instances")


@dataclass(frozen=True, slots=True)
class SignalDependency:
    """Registered current-row and rolling inputs of one S4 field."""

    indicator_fields: tuple[str, ...] = ()
    row_fields: tuple[str, ...] = ()
    rolling_window: int | None = None
    rolling_indicator_fields: tuple[str, ...] = ()
    rolling_row_fields: tuple[str, ...] = ()


SIGNAL_DEPENDENCIES: Final[Mapping[str, SignalDependency]] = (
    MappingProxyType(
        {
            "sig_rsi_mr_d": SignalDependency(
                indicator_fields=("rsi_wilder_14",)
            ),
            "sig_macd_momentum_d": SignalDependency(
                indicator_fields=("macd_hist_12_26_9",)
            ),
            "sig_bollinger_mr_d": SignalDependency(
                indicator_fields=("bb_lower_20_2", "bb_upper_20_2"),
                row_fields=("close",),
            ),
            "sig_stoch_mr_d": SignalDependency(
                indicator_fields=("stoch_k_14",)
            ),
            "sig_cci_mr_d": SignalDependency(
                indicator_fields=("cci_20",)
            ),
            "sig_mfi_mr_d": SignalDependency(
                indicator_fields=("mfi_14",)
            ),
            "sig_obv_momentum_d": SignalDependency(
                indicator_fields=("obv",),
                row_fields=("volume",),
                rolling_window=50,
                rolling_indicator_fields=("obv",),
                rolling_row_fields=("volume",),
            ),
            "sig_roc_momentum_d": SignalDependency(
                indicator_fields=("roc_close_12_pct",)
            ),
            "state_ma200_trend_d": SignalDependency(
                indicator_fields=("sma_close_200",),
                row_fields=("close",),
            ),
            "state_ema50_trend_d": SignalDependency(
                indicator_fields=("ema_close_50",),
                row_fields=("close",),
            ),
            "state_atr_relative_d": SignalDependency(
                indicator_fields=("atr_wilder_14",),
                rolling_window=200,
                rolling_indicator_fields=("atr_wilder_14",),
            ),
            "state_adx_strength_d": SignalDependency(
                indicator_fields=("adx_wilder_14",)
            ),
            "score_rsi_mr_c": SignalDependency(
                indicator_fields=("rsi_wilder_14",)
            ),
            "score_macd_momentum_c": SignalDependency(
                indicator_fields=(
                    "macd_hist_12_26_9",
                    "atr_wilder_14",
                )
            ),
            "score_bollinger_mr_c": SignalDependency(
                indicator_fields=("bb_mid_20", "bb_upper_20_2"),
                row_fields=("close",),
            ),
            "score_stoch_mr_c": SignalDependency(
                indicator_fields=("stoch_k_14",)
            ),
            "score_cci_mr_c": SignalDependency(
                indicator_fields=("cci_20",)
            ),
            "score_mfi_mr_c": SignalDependency(
                indicator_fields=("mfi_14",)
            ),
            "score_obv_momentum_c": SignalDependency(
                indicator_fields=("obv",),
                row_fields=("volume",),
                rolling_window=50,
                rolling_indicator_fields=("obv",),
                rolling_row_fields=("volume",),
            ),
            "score_roc_momentum_c": SignalDependency(
                indicator_fields=(
                    "roc_close_12_pct",
                    "atr_wilder_14",
                ),
                row_fields=("close",),
            ),
            "score_ma200_trend_c": SignalDependency(
                indicator_fields=("sma_close_200", "atr_wilder_14"),
                row_fields=("close",),
            ),
            "score_ema50_trend_c": SignalDependency(
                indicator_fields=("ema_close_50", "atr_wilder_14"),
                row_fields=("close",),
            ),
            "score_atr_relative_c": SignalDependency(
                indicator_fields=("atr_wilder_14",),
                rolling_window=200,
                rolling_indicator_fields=("atr_wilder_14",),
            ),
            "score_adx_strength_c": SignalDependency(
                indicator_fields=("adx_wilder_14",)
            ),
        }
    )
)

if tuple(SIGNAL_DEPENDENCIES) != SIGNAL_BASE_FIELDS:
    raise RuntimeError(
        "SIGNAL_DEPENDENCIES order must match SIGNAL_BASE_FIELDS"
    )


FORMULAS: Final[Mapping[str, Formula]] = MappingProxyType(
    {
        "sig_rsi_mr_d": formulas.sig_rsi_mr_d,
        "sig_macd_momentum_d": formulas.sig_macd_momentum_d,
        "sig_bollinger_mr_d": formulas.sig_bollinger_mr_d,
        "sig_stoch_mr_d": formulas.sig_stoch_mr_d,
        "sig_cci_mr_d": formulas.sig_cci_mr_d,
        "sig_mfi_mr_d": formulas.sig_mfi_mr_d,
        "sig_obv_momentum_d": formulas.sig_obv_momentum_d,
        "sig_roc_momentum_d": formulas.sig_roc_momentum_d,
        "state_ma200_trend_d": formulas.state_ma200_trend_d,
        "state_ema50_trend_d": formulas.state_ema50_trend_d,
        "state_atr_relative_d": formulas.state_atr_relative_d,
        "state_adx_strength_d": formulas.state_adx_strength_d,
        "score_rsi_mr_c": formulas.score_rsi_mr_c,
        "score_macd_momentum_c": formulas.score_macd_momentum_c,
        "score_bollinger_mr_c": formulas.score_bollinger_mr_c,
        "score_stoch_mr_c": formulas.score_stoch_mr_c,
        "score_cci_mr_c": formulas.score_cci_mr_c,
        "score_mfi_mr_c": formulas.score_mfi_mr_c,
        "score_obv_momentum_c": formulas.score_obv_momentum_c,
        "score_roc_momentum_c": formulas.score_roc_momentum_c,
        "score_ma200_trend_c": formulas.score_ma200_trend_c,
        "score_ema50_trend_c": formulas.score_ema50_trend_c,
        "score_atr_relative_c": formulas.score_atr_relative_c,
        "score_adx_strength_c": formulas.score_adx_strength_c,
    }
)

if tuple(FORMULAS) != SIGNAL_BASE_FIELDS:
    raise RuntimeError("FORMULAS order must match SIGNAL_BASE_FIELDS")


_S3_FIELD_NAMES: Final[tuple[str, ...]] = tuple(
    field.name for field in dataclasses.fields(S3Row)
)

_S3_SINGLE_FIELD_RANGES: Final[
    Mapping[str, tuple[float, float]]
] = MappingProxyType(
    {
        "rsi_wilder_14": (0.0, 100.0),
        "stoch_k_14": (0.0, 100.0),
        "atr_wilder_14": (0.0, math.inf),
        "mfi_14": (0.0, 100.0),
        "plus_di_14": (0.0, 100.0),
        "minus_di_14": (0.0, 100.0),
        "dx_14": (0.0, 100.0),
        "adx_wilder_14": (0.0, 100.0),
        "bb_width_20_2": (0.0, math.inf),
    }
)


def _canonical_key(row: S3Row) -> tuple[str, str, str, int]:
    return (
        row.market_type,
        row.symbol,
        row.interval,
        row.open_time,
    )


def _validate_indicator_field(
    name: str,
    field: IndicatorField,
) -> None:
    if not isinstance(field, IndicatorField):
        raise ValueError(f"{name} must be an IndicatorField")
    if not isinstance(field.reason_codes, tuple):
        raise ValueError(f"{name} reason_codes must be a tuple")
    if field.valid and not field.warmup_complete:
        raise ValueError(
            f"{name} cannot be valid before warm-up completion"
        )

    if field.valid:
        if field.value is None or not math.isfinite(field.value):
            raise ValueError(
                f"{name} has a nonfinite or missing valid value"
            )

        bounds = _S3_SINGLE_FIELD_RANGES.get(name)
        if bounds is not None and not (
            bounds[0] <= field.value <= bounds[1]
        ):
            raise ValueError(
                f"{name} violates the certified S3 range"
            )
    elif field.value is not None:
        raise ValueError(
            f"{name} is invalid but carries a numeric value"
        )


def _validate_s3_row(row: S3Row) -> None:
    if row.indicator_schema_id != EXPECTED_INPUT_SCHEMA_ID:
        raise ValueError("SIG_SCHEMA_MISMATCH: unexpected S3 schema id")
    if row.indicator_schema_version != EXPECTED_INPUT_SCHEMA_VERSION:
        raise ValueError(
            "SIG_SCHEMA_MISMATCH: unexpected S3 schema version"
        )
    if row.indicator_schema_id != INDICATOR_SCHEMA_ID:
        raise ValueError(
            "SIG_SCHEMA_MISMATCH: repository S3 schema id disagrees"
        )
    if row.indicator_schema_version != INDICATOR_SCHEMA_VERSION:
        raise ValueError(
            "SIG_SCHEMA_MISMATCH: repository S3 schema version disagrees"
        )
    if row.indicator_profile_id != INDICATOR_PROFILE_ID:
        raise ValueError(
            "SIG_PROFILE_MISMATCH: unexpected indicator profile id"
        )
    if row.indicator_profile_version != INDICATOR_PROFILE_VERSION:
        raise ValueError(
            "SIG_PROFILE_MISMATCH: unexpected indicator profile version"
        )
    if not row.indicator_segment_id:
        raise ValueError("indicator_segment_id must be non-empty")
    if tuple(row.indicators) != tuple(INDICATOR_FIELD_ALLOWLIST):
        raise ValueError(
            "S3 indicators are not in the certified allowlist order"
        )

    for name, field in row.indicators.items():
        _validate_indicator_field(name, field)

    if row.quality_gate_pass:
        if not math.isfinite(row.close) or row.close <= 0.0:
            raise ValueError(
                "a gate-passing S3 row requires finite positive close"
            )
        if not math.isfinite(row.volume) or row.volume < 0.0:
            raise ValueError(
                "a gate-passing S3 row requires finite nonnegative volume"
            )

    mid = row.indicators["bb_mid_20"]
    upper = row.indicators["bb_upper_20_2"]
    lower = row.indicators["bb_lower_20_2"]
    if mid.valid and upper.valid and lower.valid:
        assert mid.value is not None
        assert upper.value is not None
        assert lower.value is not None
        if not upper.value >= mid.value >= lower.value:
            raise ValueError(
                "S3 Bollinger fields violate upper >= mid >= lower"
            )


def _validate_input_rows(s3_rows: Sequence[S3Row]) -> None:
    previous_key: tuple[str, str, str, int] | None = None

    for index, row in enumerate(s3_rows):
        if not isinstance(row, S3Row):
            raise TypeError(f"row {index} is not an S3Row")

        _validate_s3_row(row)
        key = _canonical_key(row)

        if previous_key is not None and key <= previous_key:
            raise ValueError(
                "S3 rows are duplicated or not in canonical order"
            )

        previous_key = key


def _indicator_field(
    row: S3Row,
    name: str,
) -> IndicatorField:
    try:
        return row.indicators[name]
    except KeyError as exc:
        raise ValueError(
            f"missing required S3 indicator field: {name}"
        ) from exc


def _required_indicator_values(
    row: S3Row,
    names: Sequence[str],
) -> dict[str, float] | None:
    values: dict[str, float] = {}

    for name in names:
        field = _indicator_field(row, name)

        if (
            not field.valid
            or not field.warmup_complete
            or field.value is None
            or not math.isfinite(field.value)
        ):
            return None

        values[name] = field.value

    return values


def _required_row_values(
    row: S3Row,
    names: Sequence[str],
) -> dict[str, float] | None:
    values: dict[str, float] = {}

    for name in names:
        value = getattr(row, name, None)

        if (
            isinstance(value, bool)
            or not isinstance(value, Real)
            or not math.isfinite(float(value))
        ):
            return None

        float_value = float(value)

        if name == "close" and float_value <= 0.0:
            return None
        if name == "volume" and float_value < 0.0:
            return None

        values[name] = float_value

    return values


def _same_indicator_segment(
    rows: Sequence[S3Row],
    start: int,
    end_inclusive: int,
) -> bool:
    segment_id = rows[end_inclusive].indicator_segment_id

    return all(
        rows[index].indicator_segment_id == segment_id
        for index in range(start, end_inclusive + 1)
    )


@dataclass(frozen=True, slots=True)
class _WindowResult:
    indicator_values: Mapping[str, tuple[float, ...]]
    row_values: Mapping[str, tuple[float, ...]]
    reason_codes: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.reason_codes


def _window_rows(
    rows: Sequence[S3Row],
    index: int,
    dependency: SignalDependency,
) -> _WindowResult:
    window = dependency.rolling_window

    if window is None:
        return _WindowResult(
            indicator_values=MappingProxyType({}),
            row_values=MappingProxyType({}),
            reason_codes=(),
        )
    if window <= 0:
        raise RuntimeError("registered rolling window must be positive")

    start = index - window + 1

    if start < 0:
        return _WindowResult(
            indicator_values=MappingProxyType({}),
            row_values=MappingProxyType({}),
            reason_codes=("SIG_WARMUP_INCOMPLETE",),
        )

    if not _same_indicator_segment(rows, start, index):
        return _WindowResult(
            indicator_values=MappingProxyType({}),
            row_values=MappingProxyType({}),
            reason_codes=normalize_reason_codes(
                (
                    "SIG_WARMUP_INCOMPLETE",
                    "SIG_WINDOW_CROSSES_INDICATOR_SEGMENT",
                )
            ),
        )

    indicator_values: dict[str, tuple[float, ...]] = {}

    for name in dependency.rolling_indicator_fields:
        collected: list[float] = []

        for row in rows[start : index + 1]:
            field = _indicator_field(row, name)

            if (
                not row.quality_gate_pass
                or not field.valid
                or not field.warmup_complete
                or field.value is None
                or not math.isfinite(field.value)
            ):
                return _WindowResult(
                    indicator_values=MappingProxyType({}),
                    row_values=MappingProxyType({}),
                    reason_codes=("SIG_WARMUP_INCOMPLETE",),
                )

            collected.append(field.value)

        indicator_values[name] = tuple(collected)

    row_values: dict[str, tuple[float, ...]] = {}

    for name in dependency.rolling_row_fields:
        collected = []

        for row in rows[start : index + 1]:
            values = _required_row_values(row, (name,))

            if not row.quality_gate_pass or values is None:
                return _WindowResult(
                    indicator_values=MappingProxyType({}),
                    row_values=MappingProxyType({}),
                    reason_codes=("SIG_WARMUP_INCOMPLETE",),
                )

            collected.append(values[name])

        row_values[name] = tuple(collected)

    return _WindowResult(
        indicator_values=MappingProxyType(indicator_values),
        row_values=MappingProxyType(row_values),
        reason_codes=(),
    )


def _ordered_sum(values: Sequence[float]) -> float:
    total = 0.0

    for value in values:
        total = total + value

    return total


def _rolling_mean(values: Sequence[float]) -> float:
    if not values:
        raise ValueError("rolling mean requires at least one value")

    return _ordered_sum(values) / float(len(values))


def _invalid_field(*reason_codes: str) -> SignalField:
    if not reason_codes:
        raise ValueError("an invalid S4 field requires a reason code")

    return SignalField(
        value=None,
        valid=False,
        reason_codes=normalize_reason_codes(reason_codes),
    )


def _result_in_registered_range(
    name: str,
    value: SignalValue,
) -> bool:
    if isinstance(value, bool):
        return False

    definition = FIELD_DEFINITIONS[name]

    if definition.allowed_discrete_values is not None:
        return (
            isinstance(value, Integral)
            and int(value) in definition.allowed_discrete_values
        )

    return (
        isinstance(value, Real)
        and math.isfinite(float(value))
        and definition.minimum
        <= float(value)
        <= definition.maximum
    )


def _finalize_formula_result(
    name: str,
    value: SignalValue,
) -> SignalField:
    if not isinstance(value, Real) or isinstance(value, bool):
        return _invalid_field("SIG_RANGE_INVARIANT_FAILED")
    if not math.isfinite(float(value)):
        return _invalid_field("SIG_NONFINITE_RESULT")
    if not _result_in_registered_range(name, value):
        return _invalid_field("SIG_RANGE_INVARIANT_FAILED")

    return SignalField(
        value=value,
        valid=True,
        reason_codes=(),
    )


def _formula_arguments(
    name: str,
    indicator_values: Mapping[str, float],
    row_values: Mapping[str, float],
    window: _WindowResult,
) -> tuple[float, ...]:
    if name == "sig_rsi_mr_d":
        return (indicator_values["rsi_wilder_14"],)
    if name == "sig_macd_momentum_d":
        return (indicator_values["macd_hist_12_26_9"],)
    if name == "sig_bollinger_mr_d":
        return (
            row_values["close"],
            indicator_values["bb_lower_20_2"],
            indicator_values["bb_upper_20_2"],
        )
    if name == "sig_stoch_mr_d":
        return (indicator_values["stoch_k_14"],)
    if name == "sig_cci_mr_d":
        return (indicator_values["cci_20"],)
    if name == "sig_mfi_mr_d":
        return (indicator_values["mfi_14"],)
    if name == "sig_obv_momentum_d":
        return (
            indicator_values["obv"],
            _rolling_mean(window.indicator_values["obv"]),
        )
    if name == "sig_roc_momentum_d":
        return (indicator_values["roc_close_12_pct"],)
    if name == "state_ma200_trend_d":
        return (
            row_values["close"],
            indicator_values["sma_close_200"],
        )
    if name == "state_ema50_trend_d":
        return (
            row_values["close"],
            indicator_values["ema_close_50"],
        )
    if name == "state_atr_relative_d":
        return (
            indicator_values["atr_wilder_14"],
            _rolling_mean(
                window.indicator_values["atr_wilder_14"]
            ),
        )
    if name == "state_adx_strength_d":
        return (indicator_values["adx_wilder_14"],)
    if name == "score_rsi_mr_c":
        return (indicator_values["rsi_wilder_14"],)
    if name == "score_macd_momentum_c":
        return (
            indicator_values["macd_hist_12_26_9"],
            indicator_values["atr_wilder_14"],
        )
    if name == "score_bollinger_mr_c":
        return (
            row_values["close"],
            indicator_values["bb_mid_20"],
            indicator_values["bb_upper_20_2"],
        )
    if name == "score_stoch_mr_c":
        return (indicator_values["stoch_k_14"],)
    if name == "score_cci_mr_c":
        return (indicator_values["cci_20"],)
    if name == "score_mfi_mr_c":
        return (indicator_values["mfi_14"],)
    if name == "score_obv_momentum_c":
        return (
            indicator_values["obv"],
            _rolling_mean(window.indicator_values["obv"]),
            _ordered_sum(window.row_values["volume"]),
        )
    if name == "score_roc_momentum_c":
        return (
            indicator_values["roc_close_12_pct"],
            indicator_values["atr_wilder_14"],
            row_values["close"],
        )
    if name == "score_ma200_trend_c":
        return (
            row_values["close"],
            indicator_values["sma_close_200"],
            indicator_values["atr_wilder_14"],
        )
    if name == "score_ema50_trend_c":
        return (
            row_values["close"],
            indicator_values["ema_close_50"],
            indicator_values["atr_wilder_14"],
        )
    if name == "score_atr_relative_c":
        return (
            indicator_values["atr_wilder_14"],
            _rolling_mean(
                window.indicator_values["atr_wilder_14"]
            ),
        )
    if name == "score_adx_strength_c":
        return (indicator_values["adx_wilder_14"],)

    raise RuntimeError(f"unregistered S4 formula field: {name}")


def _compute_signal_field(
    rows: Sequence[S3Row],
    index: int,
    name: str,
) -> SignalField:
    row = rows[index]
    dependency = SIGNAL_DEPENDENCIES[name]

    if not row.quality_gate_pass:
        return _invalid_field("SIG_INPUT_QUALITY_GATE_FAILED")

    indicator_values = _required_indicator_values(
        row, dependency.indicator_fields
    )
    row_values = _required_row_values(row, dependency.row_fields)

    if indicator_values is None or row_values is None:
        return _invalid_field("SIG_INPUT_INVALID")

    window = _window_rows(rows, index, dependency)

    if not window.valid:
        return _invalid_field(*window.reason_codes)

    arguments = _formula_arguments(
        name,
        indicator_values,
        row_values,
        window,
    )

    try:
        value = FORMULAS[name](*arguments)
    except SignalFormulaConflict as conflict:
        return _invalid_field(conflict.reason_code)

    return _finalize_formula_result(name, value)


def _copy_s3_values(row: S3Row) -> dict[str, object]:
    return {
        field_name: getattr(row, field_name)
        for field_name in _S3_FIELD_NAMES
    }


def _build_s4_row(
    rows: Sequence[S3Row],
    index: int,
) -> S4Row:
    source = rows[index]
    signals = {
        name: _compute_signal_field(rows, index, name)
        for name in SIGNAL_BASE_FIELDS
    }

    return S4Row(
        **_copy_s3_values(source),
        **SIGNAL_METADATA_VALUES,
        signals=signals,
    )


def _verify_row_preservation(
    source_rows: Sequence[S3Row],
    output_rows: Sequence[S4Row],
) -> None:
    if len(source_rows) != len(output_rows):
        raise RuntimeError("S4 row-count invariant failed")

    for index, (source, output) in enumerate(
        zip(source_rows, output_rows, strict=True)
    ):
        for field_name in _S3_FIELD_NAMES:
            source_value = getattr(source, field_name)
            output_value = getattr(output, field_name)

            if (
                source_value is not output_value
                and source_value != output_value
            ):
                raise RuntimeError(
                    "S3 -> S4 reconciliation failed at "
                    f"row {index}, field {field_name}"
                )


def compute_signals(s3_rows: Sequence[S3Row]) -> S4Result:
    """Compute the canonical 24-field S4 profile.

    Stage-wide schema, profile, key, ordering, or upstream-invariant failures
    abort before output.  Field-local input, warm-up, denominator, finite, and
    range failures remain row-preserving invalid S4 fields with certified
    reason codes.
    """

    rows = tuple(s3_rows)

    if not rows:
        return S4Result(rows=())

    _validate_input_rows(rows)

    output_rows = tuple(
        _build_s4_row(rows, index)
        for index in range(len(rows))
    )

    _verify_row_preservation(rows, output_rows)

    return S4Result(rows=output_rows)


__all__ = [
    "FORMULAS",
    "S4Result",
    "SIGNAL_DEPENDENCIES",
    "SignalDependency",
    "compute_signals",
]
