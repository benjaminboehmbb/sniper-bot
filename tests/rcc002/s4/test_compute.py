"""Unit tests for the canonical RCC-002 S4 signal transformer."""

from __future__ import annotations

import dataclasses
import math
import unittest
from collections.abc import Mapping, Sequence

import rcc002.s4.compute as s4_compute
from rcc002.s4 import formulas
from rcc002.s3.constants import (
    INDICATOR_FIELD_ALLOWLIST,
    INDICATOR_PROFILE_ID,
    INDICATOR_PROFILE_VERSION,
    INDICATOR_SCHEMA_ID,
    INDICATOR_SCHEMA_REF,
    INDICATOR_SCHEMA_VERSION,
)
from rcc002.s3.schema import IndicatorField, S3Row
from rcc002.s4.compute import (
    FORMULAS,
    SIGNAL_DEPENDENCIES,
    compute_signals,
)
from rcc002.s4.constants import (
    FIELD_DEFINITIONS,
    FORBIDDEN_S4_FIELDS,
    FORBIDDEN_S4_PREFIXES,
    SIGNAL_BASE_FIELDS,
    SIGNAL_PROFILE_ID,
    SIGNAL_PROFILE_VERSION,
    SIGNAL_SCHEMA_ID,
    SIGNAL_SCHEMA_REF,
    SIGNAL_SCHEMA_VERSION,
    is_forbidden_s4_field,
)
from rcc002.s4.formulas import SignalFormulaConflict
from rcc002.s4.reason_codes import (
    SignalReasonCodeError,
    normalize_reason_codes,
)
from rcc002.s4.schema import S4Row, SignalField


_DEFAULT_INDICATOR_VALUES: Mapping[str, float] = {
    "sma_close_200": 100.0,
    "ema_close_50": 100.0,
    "rsi_wilder_14": 50.0,
    "macd_line_12_26": 0.0,
    "macd_signal_line_12_26_9": 0.0,
    "macd_hist_12_26_9": 0.0,
    "bb_mid_20": 100.0,
    "bb_upper_20_2": 110.0,
    "bb_lower_20_2": 90.0,
    "bb_width_20_2": 20.0,
    "stoch_k_14": 50.0,
    "true_range": 1.0,
    "atr_wilder_14": 1.0,
    "roc_close_12_pct": 0.0,
    "obv": 0.0,
    "typical_price": 100.0,
    "cci_20": 0.0,
    "mfi_14": 50.0,
    "plus_di_14": 20.0,
    "minus_di_14": 20.0,
    "dx_14": 0.0,
    "adx_wilder_14": 20.0,
}

if tuple(_DEFAULT_INDICATOR_VALUES) != tuple(
    INDICATOR_FIELD_ALLOWLIST
):
    raise RuntimeError(
        "test defaults must follow the certified S3 indicator order"
    )


def _valid_indicator(value: float) -> IndicatorField:
    return IndicatorField(
        value=value,
        valid=True,
        warmup_complete=True,
        reason_codes=(),
    )


def _invalid_indicator(
    *,
    warmup_complete: bool = False,
    reason_codes: tuple[str, ...] = ("IND_WARMUP_INCOMPLETE",),
) -> IndicatorField:
    return IndicatorField(
        value=None,
        valid=False,
        warmup_complete=warmup_complete,
        reason_codes=reason_codes,
    )


def _make_indicators(
    overrides: Mapping[str, float | IndicatorField] | None = None,
) -> dict[str, IndicatorField]:
    supplied = overrides or {}
    unknown = set(supplied).difference(INDICATOR_FIELD_ALLOWLIST)
    if unknown:
        raise ValueError(f"unknown indicator override(s): {unknown!r}")

    indicators: dict[str, IndicatorField] = {}
    for name in INDICATOR_FIELD_ALLOWLIST:
        value = supplied.get(name, _DEFAULT_INDICATOR_VALUES[name])
        indicators[name] = (
            value
            if isinstance(value, IndicatorField)
            else _valid_indicator(float(value))
        )
    return indicators


def _make_row(
    index: int,
    *,
    close: float = 100.0,
    volume: float = 1.0,
    quality_gate_pass: bool = True,
    indicator_segment_id: str = "indicator-segment-1",
    indicator_overrides: (
        Mapping[str, float | IndicatorField] | None
    ) = None,
    **row_overrides: object,
) -> S3Row:
    values: dict[str, object] = {
        "source_snapshot_id": "snapshot-1",
        "source_row_id": f"source-row-{index}",
        "source_file_ordinal": 0,
        "original_record_index": index,
        "provider": "binance",
        "market_type": "spot",
        "symbol": "BTCUSDT",
        "interval": "1m",
        "open_time": index * 60_000,
        "close_time": index * 60_000 + 59_999,
        "open": close,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": volume,
        "market_segment_id": "market-segment-1",
        "quality_is_observed": True,
        "quality_is_synthetic": False,
        "quality_has_source_conflict": False,
        "quality_gap_before": False,
        "quality_gap_after": False,
        "quality_timestamp_valid": True,
        "quality_ohlc_valid": True,
        "quality_volume_valid": True,
        "quality_market_values_valid": True,
        "quality_status": "PASS",
        "quality_reason_codes": (),
        "quality_rule_version": "1.0.0",
        "quality_gate_pass": quality_gate_pass,
        "indicator_profile_id": INDICATOR_PROFILE_ID,
        "indicator_profile_version": INDICATOR_PROFILE_VERSION,
        "indicator_schema_id": INDICATOR_SCHEMA_ID,
        "indicator_schema_version": INDICATOR_SCHEMA_VERSION,
        "indicator_schema_ref": INDICATOR_SCHEMA_REF,
        "indicator_segment_id": indicator_segment_id,
        "indicators": _make_indicators(indicator_overrides),
    }
    values.update(row_overrides)
    return S3Row(**values)


def _make_rows(
    count: int,
    *,
    row_factory=None,
) -> list[S3Row]:
    factory = row_factory or (lambda index: _make_row(index))
    return [factory(index) for index in range(count)]


def _signal(
    rows: Sequence[S3Row],
    field_name: str,
    *,
    index: int = -1,
) -> SignalField:
    return compute_signals(rows).rows[index].signals[field_name]


def _replace_indicator(
    row: S3Row,
    name: str,
    field: IndicatorField,
) -> S3Row:
    indicators = dict(row.indicators)
    indicators[name] = field
    return dataclasses.replace(row, indicators=indicators)


class TestRegistryAndSchemaContracts(unittest.TestCase):
    def test_formula_registry_is_exact_and_ordered(self) -> None:
        self.assertEqual(tuple(FORMULAS), SIGNAL_BASE_FIELDS)
        self.assertEqual(len(FORMULAS), 24)
        self.assertIs(
            FORMULAS["score_adx_strength_c"],
            formulas.score_adx_strength_c,
        )

    def test_dependency_registry_is_exact_and_ordered(self) -> None:
        self.assertEqual(
            tuple(SIGNAL_DEPENDENCIES), SIGNAL_BASE_FIELDS
        )
        self.assertEqual(len(SIGNAL_DEPENDENCIES), 24)

    def test_adx_strength_score_has_unsigned_range(self) -> None:
        definition = FIELD_DEFINITIONS["score_adx_strength_c"]
        self.assertEqual(definition.minimum, 0.0)
        self.assertEqual(definition.maximum, 1.0)

    def test_empty_input_is_row_preserving(self) -> None:
        self.assertEqual(compute_signals([]).rows, ())

    def test_output_metadata_and_signal_order(self) -> None:
        output = compute_signals([_make_row(0)]).rows[0]
        self.assertEqual(output.signal_profile_id, SIGNAL_PROFILE_ID)
        self.assertEqual(
            output.signal_profile_version, SIGNAL_PROFILE_VERSION
        )
        self.assertEqual(output.signal_schema_id, SIGNAL_SCHEMA_ID)
        self.assertEqual(
            output.signal_schema_version, SIGNAL_SCHEMA_VERSION
        )
        self.assertEqual(output.signal_schema_ref, SIGNAL_SCHEMA_REF)
        self.assertEqual(tuple(output.signals), SIGNAL_BASE_FIELDS)

    def test_all_s3_dataclass_fields_are_preserved(self) -> None:
        source = _make_row(0)
        output = compute_signals([source]).rows[0]
        for field in dataclasses.fields(S3Row):
            with self.subTest(field=field.name):
                self.assertEqual(
                    getattr(output, field.name),
                    getattr(source, field.name),
                )

    def test_output_has_no_s5_s6_or_s7_fields(self) -> None:
        names = {field.name for field in dataclasses.fields(S4Row)}
        self.assertTrue(FORBIDDEN_S4_FIELDS.isdisjoint(names))

        for name in names:
            with self.subTest(field=name):
                self.assertFalse(is_forbidden_s4_field(name))

        for forbidden_name in FORBIDDEN_S4_FIELDS:
            with self.subTest(forbidden=forbidden_name):
                self.assertTrue(
                    is_forbidden_s4_field(forbidden_name)
                )

        for prefix in FORBIDDEN_S4_PREFIXES:
            with self.subTest(prefix=prefix):
                self.assertTrue(
                    is_forbidden_s4_field(f"{prefix}probe")
                )

    def test_signal_field_rejects_invalid_value_pairings(self) -> None:
        with self.assertRaises(ValueError):
            SignalField(value=None, valid=True, reason_codes=())
        with self.assertRaises(ValueError):
            SignalField(value=1, valid=False, reason_codes=())
        with self.assertRaises(ValueError):
            SignalField(
                value=None,
                valid=False,
                reason_codes=["SIG_INPUT_INVALID"],  # type: ignore[arg-type]
            )


class TestStageWideInputRejection(unittest.TestCase):
    def assert_rejected(self, row: S3Row) -> None:
        with self.assertRaises((TypeError, ValueError)):
            compute_signals([row])

    def test_schema_id_mismatch_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(0, indicator_schema_id="unknown.s3")
        )

    def test_schema_version_mismatch_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(0, indicator_schema_version="2.0.0")
        )

    def test_schema_ref_mismatch_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(0, indicator_schema_ref="wrong")
        )

    def test_profile_id_mismatch_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(0, indicator_profile_id="UNKNOWN_PROFILE")
        )

    def test_profile_version_mismatch_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(0, indicator_profile_version="2.0.0")
        )

    def test_empty_indicator_segment_is_rejected(self) -> None:
        self.assert_rejected(_make_row(0, indicator_segment_id=""))

    def test_noncanonical_indicator_order_is_rejected(self) -> None:
        row = _make_row(0)
        reversed_items = reversed(tuple(row.indicators.items()))
        self.assert_rejected(
            dataclasses.replace(row, indicators=dict(reversed_items))
        )

    def test_duplicate_key_is_rejected(self) -> None:
        row = _make_row(0)
        with self.assertRaises(ValueError):
            compute_signals([row, dataclasses.replace(row)])

    def test_noncanonical_sorting_is_rejected(self) -> None:
        rows = [_make_row(1), _make_row(0)]
        with self.assertRaises(ValueError):
            compute_signals(rows)

    def test_valid_nonfinite_indicator_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(
                0,
                indicator_overrides={
                    "cci_20": _valid_indicator(math.inf)
                },
            )
        )

    def test_valid_before_warmup_is_rejected(self) -> None:
        malformed = IndicatorField(
            value=50.0,
            valid=True,
            warmup_complete=False,
            reason_codes=(),
        )
        self.assert_rejected(
            _make_row(
                0,
                indicator_overrides={"rsi_wilder_14": malformed},
            )
        )

    def test_valid_out_of_range_indicator_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(
                0,
                indicator_overrides={
                    "rsi_wilder_14": _valid_indicator(100.001)
                },
            )
        )

    def test_nonpositive_gate_passing_close_is_rejected(self) -> None:
        self.assert_rejected(_make_row(0, close=0.0))

    def test_negative_gate_passing_volume_is_rejected(self) -> None:
        self.assert_rejected(_make_row(0, volume=-1.0))

    def test_bollinger_order_violation_is_rejected(self) -> None:
        self.assert_rejected(
            _make_row(
                0,
                indicator_overrides={
                    "bb_mid_20": 100.0,
                    "bb_upper_20_2": 99.0,
                    "bb_lower_20_2": 90.0,
                },
            )
        )


class TestValidityAndRollingWindows(unittest.TestCase):
    def test_quality_gate_failure_invalidates_all_fields(self) -> None:
        output = compute_signals(
            [_make_row(0, quality_gate_pass=False)]
        ).rows[0]
        for name, field in output.signals.items():
            with self.subTest(field=name):
                self.assertIsNone(field.value)
                self.assertFalse(field.valid)
                self.assertEqual(
                    field.reason_codes,
                    ("SIG_INPUT_QUALITY_GATE_FAILED",),
                )

    def test_invalid_input_is_field_local(self) -> None:
        row = _make_row(
            0,
            indicator_overrides={
                "mfi_14": _invalid_indicator(
                    warmup_complete=True,
                    reason_codes=("IND_RANGE_INVARIANT_FAILED",),
                )
            },
        )
        output = compute_signals([row]).rows[0]
        self.assertTrue(output.signals["sig_rsi_mr_d"].valid)
        self.assertTrue(output.signals["score_rsi_mr_c"].valid)
        self.assertEqual(
            output.signals["sig_mfi_mr_d"].reason_codes,
            ("SIG_INPUT_INVALID",),
        )
        self.assertEqual(
            output.signals["score_mfi_mr_c"].reason_codes,
            ("SIG_INPUT_INVALID",),
        )

    def test_obv_window_first_valid_at_row_50(self) -> None:
        rows = _make_rows(
            50,
            row_factory=lambda index: _make_row(
                index,
                indicator_overrides={"obv": float(index)},
            ),
        )
        result = compute_signals(rows)
        self.assertEqual(
            result.rows[48]
            .signals["sig_obv_momentum_d"]
            .reason_codes,
            ("SIG_WARMUP_INCOMPLETE",),
        )
        self.assertTrue(
            result.rows[49].signals["sig_obv_momentum_d"].valid
        )
        self.assertTrue(
            result.rows[49].signals["score_obv_momentum_c"].valid
        )

    def test_atr_window_first_valid_at_row_200(self) -> None:
        result = compute_signals(_make_rows(200))
        self.assertEqual(
            result.rows[198]
            .signals["state_atr_relative_d"]
            .reason_codes,
            ("SIG_WARMUP_INCOMPLETE",),
        )
        self.assertTrue(
            result.rows[199].signals["state_atr_relative_d"].valid
        )
        self.assertTrue(
            result.rows[199].signals["score_atr_relative_c"].valid
        )

    def test_obv_window_cannot_cross_indicator_segment(self) -> None:
        rows = _make_rows(
            50,
            row_factory=lambda index: _make_row(
                index,
                indicator_segment_id=(
                    "segment-a" if index < 25 else "segment-b"
                ),
                indicator_overrides={"obv": float(index)},
            ),
        )
        field = _signal(rows, "sig_obv_momentum_d")
        self.assertFalse(field.valid)
        self.assertEqual(
            field.reason_codes,
            (
                "SIG_WARMUP_INCOMPLETE",
                "SIG_WINDOW_CROSSES_INDICATOR_SEGMENT",
            ),
        )

    def test_obv_window_restarts_after_segment_boundary(self) -> None:
        rows = _make_rows(
            75,
            row_factory=lambda index: _make_row(
                index,
                indicator_segment_id=(
                    "segment-a" if index < 25 else "segment-b"
                ),
                indicator_overrides={"obv": float(index)},
            ),
        )
        result = compute_signals(rows)
        self.assertTrue(
            result.rows[74].signals["sig_obv_momentum_d"].valid
        )

    def test_historical_invalid_atr_keeps_window_in_warmup(self) -> None:
        rows = _make_rows(200)
        rows[10] = _replace_indicator(
            rows[10],
            "atr_wilder_14",
            _invalid_indicator(),
        )
        field = _signal(rows, "state_atr_relative_d")
        self.assertEqual(
            field.reason_codes, ("SIG_WARMUP_INCOMPLETE",)
        )


class TestDiscreteTransformations(unittest.TestCase):
    def test_rsi_thresholds(self) -> None:
        cases = (
            (29.999, 1),
            (30.0, 0),
            (70.0, 0),
            (70.001, -1),
        )
        for value, expected in cases:
            with self.subTest(rsi=value):
                field = _signal(
                    [
                        _make_row(
                            0,
                            indicator_overrides={
                                "rsi_wilder_14": value
                            },
                        )
                    ],
                    "sig_rsi_mr_d",
                )
                self.assertEqual(field.value, expected)

    def test_stochastic_thresholds(self) -> None:
        cases = ((19.999, 1), (20.0, 0), (80.0, 0), (80.001, -1))
        for value, expected in cases:
            with self.subTest(stoch=value):
                field = _signal(
                    [
                        _make_row(
                            0,
                            indicator_overrides={"stoch_k_14": value},
                        )
                    ],
                    "sig_stoch_mr_d",
                )
                self.assertEqual(field.value, expected)

    def test_cci_thresholds(self) -> None:
        cases = (
            (-100.001, 1),
            (-100.0, 0),
            (100.0, 0),
            (100.001, -1),
        )
        for value, expected in cases:
            with self.subTest(cci=value):
                field = _signal(
                    [
                        _make_row(
                            0,
                            indicator_overrides={"cci_20": value},
                        )
                    ],
                    "sig_cci_mr_d",
                )
                self.assertEqual(field.value, expected)

    def test_mfi_thresholds(self) -> None:
        cases = ((19.999, 1), (20.0, 0), (80.0, 0), (80.001, -1))
        for value, expected in cases:
            with self.subTest(mfi=value):
                field = _signal(
                    [
                        _make_row(
                            0,
                            indicator_overrides={"mfi_14": value},
                        )
                    ],
                    "sig_mfi_mr_d",
                )
                self.assertEqual(field.value, expected)

    def test_bollinger_touch_is_neutral(self) -> None:
        cases = (
            (89.999, 1),
            (90.0, 0),
            (110.0, 0),
            (110.001, -1),
        )
        for close, expected in cases:
            with self.subTest(close=close):
                field = _signal(
                    [_make_row(0, close=close)],
                    "sig_bollinger_mr_d",
                )
                self.assertEqual(field.value, expected)

    def test_sign_based_momentum_fields(self) -> None:
        for indicator, field_name in (
            ("macd_hist_12_26_9", "sig_macd_momentum_d"),
            ("roc_close_12_pct", "sig_roc_momentum_d"),
        ):
            for value, expected in ((-1.0, -1), (0.0, 0), (1.0, 1)):
                with self.subTest(
                    indicator=indicator, value=value
                ):
                    field = _signal(
                        [
                            _make_row(
                                0,
                                indicator_overrides={
                                    indicator: value
                                },
                            )
                        ],
                        field_name,
                    )
                    self.assertEqual(field.value, expected)

    def test_ma_and_ema_trend_direction(self) -> None:
        for field_name, indicator in (
            ("state_ma200_trend_d", "sma_close_200"),
            ("state_ema50_trend_d", "ema_close_50"),
        ):
            for level, expected in (
                (101.0, -1),
                (100.0, 0),
                (99.0, 1),
            ):
                with self.subTest(field=field_name, level=level):
                    field = _signal(
                        [
                            _make_row(
                                0,
                                indicator_overrides={
                                    indicator: level
                                },
                            )
                        ],
                        field_name,
                    )
                    self.assertEqual(field.value, expected)

    def test_adx_discrete_threshold(self) -> None:
        for adx, expected in ((25.0, 0), (25.0001, 1)):
            with self.subTest(adx=adx):
                field = _signal(
                    [
                        _make_row(
                            0,
                            indicator_overrides={
                                "adx_wilder_14": adx
                            },
                        )
                    ],
                    "state_adx_strength_d",
                )
                self.assertEqual(field.value, expected)


class TestContinuousTransformations(unittest.TestCase):
    def assert_anchor_values(
        self,
        *,
        indicator: str,
        field_name: str,
        cases: Sequence[tuple[float, float]],
    ) -> None:
        for value, expected in cases:
            with self.subTest(
                indicator=indicator, value=value
            ):
                field = _signal(
                    [
                        _make_row(
                            0,
                            indicator_overrides={indicator: value},
                        )
                    ],
                    field_name,
                )
                self.assertTrue(field.valid)
                self.assertAlmostEqual(field.value, expected)

    def test_rsi_anchor_values(self) -> None:
        self.assert_anchor_values(
            indicator="rsi_wilder_14",
            field_name="score_rsi_mr_c",
            cases=((30.0, 1.0), (50.0, 0.0), (70.0, -1.0)),
        )

    def test_stochastic_anchor_values(self) -> None:
        self.assert_anchor_values(
            indicator="stoch_k_14",
            field_name="score_stoch_mr_c",
            cases=((20.0, 1.0), (50.0, 0.0), (80.0, -1.0)),
        )

    def test_mfi_anchor_values(self) -> None:
        self.assert_anchor_values(
            indicator="mfi_14",
            field_name="score_mfi_mr_c",
            cases=((20.0, 1.0), (50.0, 0.0), (80.0, -1.0)),
        )

    def test_cci_anchor_values(self) -> None:
        self.assert_anchor_values(
            indicator="cci_20",
            field_name="score_cci_mr_c",
            cases=((-100.0, 1.0), (0.0, 0.0), (100.0, -1.0)),
        )

    def test_bollinger_anchor_values(self) -> None:
        for close, expected in (
            (90.0, 1.0),
            (100.0, 0.0),
            (110.0, -1.0),
        ):
            with self.subTest(close=close):
                field = _signal(
                    [_make_row(0, close=close)],
                    "score_bollinger_mr_c",
                )
                self.assertAlmostEqual(field.value, expected)

    def test_adx_anchor_values(self) -> None:
        self.assert_anchor_values(
            indicator="adx_wilder_14",
            field_name="score_adx_strength_c",
            cases=((15.0, 0.0), (20.0, 0.5), (25.0, 1.0)),
        )

    def test_macd_atr_normalization_and_clipping(self) -> None:
        for histogram, expected in (
            (-2.0, -1.0),
            (0.0, 0.0),
            (0.5, 0.5),
            (2.0, 1.0),
        ):
            with self.subTest(histogram=histogram):
                field = _signal(
                    [
                        _make_row(
                            0,
                            indicator_overrides={
                                "macd_hist_12_26_9": histogram,
                                "atr_wilder_14": 1.0,
                            },
                        )
                    ],
                    "score_macd_momentum_c",
                )
                self.assertEqual(field.value, expected)

    def test_roc_atr_normalization(self) -> None:
        field = _signal(
            [
                _make_row(
                    0,
                    close=100.0,
                    indicator_overrides={
                        "roc_close_12_pct": 1.0,
                        "atr_wilder_14": 2.0,
                    },
                )
            ],
            "score_roc_momentum_c",
        )
        self.assertAlmostEqual(field.value, 0.5)

    def test_ma_and_ema_atr_normalization(self) -> None:
        for field_name, indicator in (
            ("score_ma200_trend_c", "sma_close_200"),
            ("score_ema50_trend_c", "ema_close_50"),
        ):
            field = _signal(
                [
                    _make_row(
                        0,
                        close=101.0,
                        indicator_overrides={
                            indicator: 100.0,
                            "atr_wilder_14": 2.0,
                        },
                    )
                ],
                field_name,
            )
            self.assertAlmostEqual(field.value, 0.5)

    def test_obv_normalization(self) -> None:
        rows = _make_rows(
            50,
            row_factory=lambda index: _make_row(
                index,
                volume=1.0,
                indicator_overrides={"obv": float(index)},
            ),
        )
        field = _signal(rows, "score_obv_momentum_c")
        self.assertAlmostEqual(field.value, 24.5 / 50.0)

    def test_atr_ratio_anchor_values(self) -> None:
        for current, expected in (
            (0.5, -1.0),
            (1.0, 0.0),
            (2.0, 1.0),
        ):
            prior = (200.0 - current) / 199.0
            rows = _make_rows(
                200,
                row_factory=lambda index, p=prior, c=current: _make_row(
                    index,
                    indicator_overrides={
                        "atr_wilder_14": (
                            c if index == 199 else p
                        )
                    },
                ),
            )
            with self.subTest(ratio=current):
                field = _signal(rows, "score_atr_relative_c")
                self.assertAlmostEqual(field.value, expected)


class TestDefinedAndConflictingZeroCases(unittest.TestCase):
    def test_macd_zero_atr_cases(self) -> None:
        valid = _signal(
            [
                _make_row(
                    0,
                    indicator_overrides={
                        "macd_hist_12_26_9": 0.0,
                        "atr_wilder_14": 0.0,
                    },
                )
            ],
            "score_macd_momentum_c",
        )
        self.assertTrue(valid.valid)
        self.assertEqual(valid.value, 0.0)

        invalid = _signal(
            [
                _make_row(
                    0,
                    indicator_overrides={
                        "macd_hist_12_26_9": 1.0,
                        "atr_wilder_14": 0.0,
                    },
                )
            ],
            "score_macd_momentum_c",
        )
        self.assertEqual(
            invalid.reason_codes,
            ("SIG_MACD_ZERO_ATR_CONFLICT",),
        )

    def test_bollinger_zero_width_cases(self) -> None:
        base = {
            "bb_lower_20_2": 100.0,
            "bb_mid_20": 100.0,
            "bb_upper_20_2": 100.0,
            "bb_width_20_2": 0.0,
        }
        valid = _signal(
            [_make_row(0, close=100.0, indicator_overrides=base)],
            "score_bollinger_mr_c",
        )
        self.assertEqual(valid.value, 0.0)

        invalid = _signal(
            [_make_row(0, close=101.0, indicator_overrides=base)],
            "score_bollinger_mr_c",
        )
        self.assertEqual(
            invalid.reason_codes,
            ("SIG_BB_ZERO_WIDTH_CONFLICT",),
        )

    def test_obv_zero_volume_cases(self) -> None:
        flat_rows = _make_rows(
            50,
            row_factory=lambda index: _make_row(
                index,
                volume=0.0,
                indicator_overrides={"obv": 0.0},
            ),
        )
        valid = _signal(flat_rows, "score_obv_momentum_c")
        self.assertEqual(valid.value, 0.0)

        conflict_rows = _make_rows(
            50,
            row_factory=lambda index: _make_row(
                index,
                volume=0.0,
                indicator_overrides={"obv": float(index)},
            ),
        )
        invalid = _signal(
            conflict_rows, "score_obv_momentum_c"
        )
        self.assertEqual(
            invalid.reason_codes,
            ("SIG_OBV_ZERO_VOLUME_CONFLICT",),
        )

    def test_roc_zero_atr_cases(self) -> None:
        valid = _signal(
            [
                _make_row(
                    0,
                    indicator_overrides={
                        "roc_close_12_pct": 0.0,
                        "atr_wilder_14": 0.0,
                    },
                )
            ],
            "score_roc_momentum_c",
        )
        self.assertEqual(valid.value, 0.0)

        invalid = _signal(
            [
                _make_row(
                    0,
                    indicator_overrides={
                        "roc_close_12_pct": 1.0,
                        "atr_wilder_14": 0.0,
                    },
                )
            ],
            "score_roc_momentum_c",
        )
        self.assertEqual(
            invalid.reason_codes,
            ("SIG_ROC_ZERO_ATR_CONFLICT",),
        )

    def test_ma_and_ema_zero_atr_cases(self) -> None:
        cases = (
            (
                "score_ma200_trend_c",
                "sma_close_200",
                "SIG_MA200_ZERO_ATR_CONFLICT",
            ),
            (
                "score_ema50_trend_c",
                "ema_close_50",
                "SIG_EMA50_ZERO_ATR_CONFLICT",
            ),
        )
        for field_name, indicator, reason_code in cases:
            with self.subTest(field=field_name):
                valid = _signal(
                    [
                        _make_row(
                            0,
                            close=100.0,
                            indicator_overrides={
                                indicator: 100.0,
                                "atr_wilder_14": 0.0,
                            },
                        )
                    ],
                    field_name,
                )
                self.assertEqual(valid.value, 0.0)

                invalid = _signal(
                    [
                        _make_row(
                            0,
                            close=101.0,
                            indicator_overrides={
                                indicator: 100.0,
                                "atr_wilder_14": 0.0,
                            },
                        )
                    ],
                    field_name,
                )
                self.assertEqual(
                    invalid.reason_codes, (reason_code,)
                )

    def test_atr_zero_ratio_defined_cases(self) -> None:
        all_zero = _make_rows(
            200,
            row_factory=lambda index: _make_row(
                index,
                indicator_overrides={"atr_wilder_14": 0.0},
            ),
        )
        self.assertEqual(
            _signal(all_zero, "score_atr_relative_c").value,
            0.0,
        )

        current_zero = _make_rows(
            200,
            row_factory=lambda index: _make_row(
                index,
                indicator_overrides={
                    "atr_wilder_14": 0.0 if index == 199 else 1.0
                },
            ),
        )
        self.assertEqual(
            _signal(current_zero, "score_atr_relative_c").value,
            -1.0,
        )

    def test_atr_positive_over_zero_reference_conflict_formula(self) -> None:
        with self.assertRaises(SignalFormulaConflict) as caught:
            formulas.score_atr_relative_c(1.0, 0.0)

        self.assertEqual(
            caught.exception.reason_code,
            "SIG_ATR_RATIO_ZERO_CONFLICT",
        )

    def test_positive_current_atr_makes_rolling_mean_positive(self) -> None:
        rows = _make_rows(
            200,
            row_factory=lambda index: _make_row(
                index,
                indicator_overrides={
                    "atr_wilder_14": 1.0 if index == 199 else 0.0
                },
            ),
        )
        field = _signal(rows, "score_atr_relative_c")
        self.assertTrue(field.valid)
        self.assertEqual(field.value, 1.0)


class TestFinalizationAndCausality(unittest.TestCase):
    def test_valid_outputs_are_finite_and_in_registered_range(
        self,
    ) -> None:
        output = compute_signals(_make_rows(220)).rows[-1]
        for name, field in output.signals.items():
            with self.subTest(field=name):
                self.assertTrue(field.valid)
                self.assertIsNotNone(field.value)
                self.assertTrue(math.isfinite(float(field.value)))
                definition = FIELD_DEFINITIONS[name]
                self.assertGreaterEqual(
                    float(field.value), definition.minimum
                )
                self.assertLessEqual(
                    float(field.value), definition.maximum
                )

    def test_nonfinite_formula_result_is_invalidated(self) -> None:
        field = s4_compute._finalize_formula_result(
            "score_rsi_mr_c", math.inf
        )
        self.assertEqual(
            field.reason_codes, ("SIG_NONFINITE_RESULT",)
        )

    def test_range_violation_is_invalidated(self) -> None:
        field = s4_compute._finalize_formula_result(
            "score_rsi_mr_c", 2.0
        )
        self.assertEqual(
            field.reason_codes,
            ("SIG_RANGE_INVARIANT_FAILED",),
        )

    def test_reason_codes_are_deduplicated_and_sorted(self) -> None:
        self.assertEqual(
            normalize_reason_codes(
                (
                    "SIG_RANGE_INVARIANT_FAILED",
                    "SIG_WARMUP_INCOMPLETE",
                    "SIG_RANGE_INVARIANT_FAILED",
                    "SIG_INPUT_INVALID",
                )
            ),
            (
                "SIG_INPUT_INVALID",
                "SIG_WARMUP_INCOMPLETE",
                "SIG_RANGE_INVARIANT_FAILED",
            ),
        )

    def test_unknown_reason_code_is_rejected(self) -> None:
        with self.assertRaises(SignalReasonCodeError):
            normalize_reason_codes(("SIG_UNKNOWN",))

    def test_future_changes_do_not_change_prior_signals(self) -> None:
        rows = _make_rows(
            220,
            row_factory=lambda index: _make_row(
                index,
                indicator_overrides={"obv": float(index)},
            ),
        )
        baseline = compute_signals(rows).rows[100].signals

        rows[200] = dataclasses.replace(
            rows[200],
            close=105.0,
            indicators=_make_indicators(
                {
                    "rsi_wilder_14": 10.0,
                    "obv": 10_000.0,
                }
            ),
        )
        changed = compute_signals(rows).rows[100].signals
        self.assertEqual(changed, baseline)


if __name__ == "__main__":
    unittest.main()
