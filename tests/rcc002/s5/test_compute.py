"""End-to-end computation tests for RCC-002 S5."""

from __future__ import annotations

import dataclasses
import unittest

from rcc002.s3.schema import IndicatorField
from rcc002.s4.compute import compute_signals
from rcc002.s4.schema import SignalField
from rcc002.s5.compute import compute_regimes
from rcc002.s5.constants import (
    SLOPE_LOOKBACK_BARS,
    RegimeState,
    TrendStrength,
    VolatilityRelative,
)
from tests.rcc002.s4.test_compute import _make_row, _make_rows


def _s4_rows(count: int):
    return compute_signals(_make_rows(count)).rows


class TestComputeRegimes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _s4_rows(1_445)
        cls.result = compute_regimes(
            cls.rows, parent_build_id="full-build"
        )

    def test_empty_input(self) -> None:
        result = compute_regimes([], parent_build_id="empty-build")
        self.assertEqual(result.rows, ())
        self.assertIsNone(result.final_state)
        self.assertFalse(result.prior_state_accepted)

    def test_row_count_and_s4_preservation(self) -> None:
        self.assertEqual(len(self.result.rows), len(self.rows))
        for name in (
            "source_row_id", "close", "indicators", "signals",
            "signal_schema_ref",
        ):
            self.assertEqual(
                getattr(self.result.rows[-1], name),
                getattr(self.rows[-1], name),
            )

    def test_output_dictionaries_do_not_alias_upstream(self) -> None:
        source = _s4_rows(1)[0]
        output = compute_regimes(
            (source,), parent_build_id="container-copy"
        ).rows[0]
        self.assertIsNot(output.indicators, source.indicators)
        self.assertIsNot(output.signals, source.signals)
        output.indicators.clear()
        output.signals.clear()
        self.assertTrue(source.indicators)
        self.assertTrue(source.signals)

    def test_pre_slope_warmup(self) -> None:
        row = self.result.rows[SLOPE_LOOKBACK_BARS - 1]
        self.assertIs(row.regime_raw, RegimeState.UNKNOWN)
        self.assertIsNone(row.ma200_slope_1440_pct)
        self.assertIn("REG_WARMUP_INCOMPLETE", row.regime_reason_codes)
        self.assertNotIn(
            "REG_EFFECTIVE_UNCONFIRMED", row.regime_reason_codes
        )

    def test_first_slope_is_at_index_1440(self) -> None:
        row = self.result.rows[SLOPE_LOOKBACK_BARS]
        self.assertEqual(row.ma200_slope_1440_pct, 0.0)
        self.assertIs(row.regime_raw, RegimeState.SIDE)
        self.assertEqual(row.regime_candidate_count, 1)
        self.assertIn(
            "REG_EFFECTIVE_UNCONFIRMED", row.regime_reason_codes
        )

    def test_three_bar_confirmation(self) -> None:
        first = self.result.rows[1_440]
        second = self.result.rows[1_441]
        third = self.result.rows[1_442]
        self.assertEqual(first.regime_candidate_count, 1)
        self.assertEqual(second.regime_candidate_count, 2)
        self.assertEqual(third.regime_candidate_count, 3)
        self.assertTrue(third.regime_transition_flag)
        self.assertIs(third.regime_effective, RegimeState.SIDE)
        self.assertTrue(third.regime_valid)

    def test_post_confirmation_candidate_remains_saturated(self) -> None:
        row = self.result.rows[1_443]
        self.assertIs(row.regime_candidate, RegimeState.SIDE)
        self.assertEqual(row.regime_candidate_count, 3)
        self.assertFalse(row.regime_transition_flag)

    def test_default_context_classification(self) -> None:
        row = self.result.rows[-1]
        self.assertIs(row.trend_strength, TrendStrength.DEVELOPING)
        self.assertTrue(row.trend_strength_valid)
        self.assertIs(
            row.volatility_relative,
            VolatilityRelative.AT_REFERENCE,
        )
        self.assertTrue(row.volatility_relative_valid)

    def test_final_state_is_checksummed_and_bounded(self) -> None:
        state = self.result.final_state
        assert state is not None
        self.assertEqual(len(state.sma200_context_state), 1_440)
        self.assertEqual(len(state.state_payload_sha256), 64)

    def test_nonempty_parent_build_required(self) -> None:
        with self.assertRaises(ValueError):
            compute_regimes(self.rows[:1], parent_build_id="")

    def test_only_one_series_per_call(self) -> None:
        other = dataclasses.replace(
            self.rows[1], symbol="ETHUSDT"
        )
        with self.assertRaises(ValueError):
            compute_regimes(
                (self.rows[0], other), parent_build_id="build"
            )

    def test_only_1m_supported(self) -> None:
        row = dataclasses.replace(self.rows[0], interval="5m")
        with self.assertRaises(ValueError):
            compute_regimes((row,), parent_build_id="build")

    def test_quality_gate_failure_is_fail_closed(self) -> None:
        row = dataclasses.replace(
            self.rows[0],
            quality_gate_pass=False,
            quality_status="ERROR",
            quality_reason_codes=("DV_NUMERIC_PARSE_FAILED",),
        )
        result = compute_regimes((row,), parent_build_id="build")
        output = result.rows[0]
        self.assertIs(output.regime_raw, RegimeState.UNKNOWN)
        self.assertIn(
            "REG_INPUT_QUALITY_GATE_FAILED",
            output.regime_reason_codes,
        )

    def test_invalid_sma_is_fail_closed(self) -> None:
        row = self.rows[0]
        indicators = dict(row.indicators)
        indicators["sma_close_200"] = IndicatorField(
            value=None,
            valid=False,
            warmup_complete=False,
            reason_codes=("IND_WARMUP_INCOMPLETE",),
        )
        output = compute_regimes(
            (dataclasses.replace(row, indicators=indicators),),
            parent_build_id="build",
        ).rows[0]
        self.assertIn("REG_INPUT_INVALID", output.regime_reason_codes)

    def test_nonpositive_reference_has_specific_reason(self) -> None:
        source = [
            _make_row(
                index,
                indicator_overrides={
                    "sma_close_200": 0.0 if index == 0 else 100.0
                },
            )
            for index in range(1_441)
        ]
        output = compute_regimes(
            compute_signals(source).rows,
            parent_build_id="denominator-build",
        ).rows[-1]
        self.assertIn(
            "REG_SLOPE_DENOMINATOR_INVALID",
            output.regime_reason_codes,
        )

    def test_invalid_adx_only_invalidates_trend_context(self) -> None:
        row = self.rows[-1]
        indicators = dict(row.indicators)
        indicators["adx_wilder_14"] = IndicatorField(
            value=None,
            valid=False,
            warmup_complete=True,
            reason_codes=("IND_INPUT_INVALID",),
        )
        output = compute_regimes(
            (dataclasses.replace(row, indicators=indicators),),
            parent_build_id="build",
        ).rows[0]
        self.assertFalse(output.trend_strength_valid)
        self.assertEqual(
            output.trend_strength_reason_codes,
            ("REG_TREND_STRENGTH_INPUT_INVALID",),
        )

    def test_invalid_atr_state_only_invalidates_volatility_context(
        self,
    ) -> None:
        row = self.rows[-1]
        signals = dict(row.signals)
        signals["state_atr_relative_d"] = SignalField(
            value=None,
            valid=False,
            reason_codes=("SIG_INPUT_INVALID",),
        )
        output = compute_regimes(
            (dataclasses.replace(row, signals=signals),),
            parent_build_id="build",
        ).rows[0]
        self.assertFalse(output.volatility_relative_valid)
        self.assertEqual(
            output.volatility_relative_reason_codes,
            ("REG_VOLATILITY_INPUT_INVALID",),
        )

    def test_state_continuation_matches_full_build(self) -> None:
        first = compute_regimes(
            self.rows[:1_441], parent_build_id="split-build"
        )
        second = compute_regimes(
            self.rows[1_441:],
            parent_build_id="split-build",
            prior_state=first.final_state,
        )
        full = compute_regimes(
            self.rows, parent_build_id="split-build"
        )
        self.assertTrue(second.prior_state_accepted)
        self.assertEqual(
            first.rows + second.rows,
            full.rows,
        )
        self.assertEqual(second.final_state, full.final_state)

    def test_partition_at_segment_boundary_matches_serial(self) -> None:
        boundary = 1_443
        rows = (
            self.rows[:boundary]
            + tuple(
                dataclasses.replace(
                    row,
                    market_segment_id="market-segment-2",
                    indicator_segment_id="indicator-segment-2",
                )
                for row in self.rows[boundary:]
            )
        )
        full = compute_regimes(
            rows, parent_build_id="segment-parity"
        )
        first = compute_regimes(
            rows[:boundary], parent_build_id="segment-parity"
        )
        second = compute_regimes(
            rows[boundary:],
            parent_build_id="segment-parity",
            prior_state=first.final_state,
        )
        self.assertFalse(second.prior_state_accepted)
        self.assertIn(
            "REG_SEGMENT_RESET",
            second.rows[0].regime_reason_codes,
        )
        self.assertTrue(second.rows[0].regime_transition_flag)
        self.assertIs(
            second.rows[0].regime_transition_from,
            RegimeState.SIDE,
        )
        self.assertIs(
            second.rows[0].regime_transition_to,
            RegimeState.UNKNOWN,
        )
        self.assertEqual(first.rows + second.rows, full.rows)
        self.assertEqual(second.final_state, full.final_state)

    def test_wrong_parent_rejects_prior_state(self) -> None:
        first = compute_regimes(
            self.rows[:1_441], parent_build_id="build-a"
        )
        second = compute_regimes(
            self.rows[1_441:],
            parent_build_id="build-b",
            prior_state=first.final_state,
        )
        self.assertFalse(second.prior_state_accepted)
        self.assertIs(
            second.rows[0].regime_raw, RegimeState.UNKNOWN
        )

    def test_noncontiguous_prior_state_rejected(self) -> None:
        first = compute_regimes(
            self.rows[:1_440], parent_build_id="build"
        )
        second = compute_regimes(
            self.rows[1_441:],
            parent_build_id="build",
            prior_state=first.final_state,
        )
        self.assertFalse(second.prior_state_accepted)

    def test_segment_reset_is_reported_once(self) -> None:
        base = list(self.rows[:3])
        reset = [
            dataclasses.replace(
                row,
                market_segment_id="market-segment-2",
                indicator_segment_id="indicator-segment-2",
            )
            for row in base[1:]
        ]
        result = compute_regimes(
            (base[0], *reset), parent_build_id="segment-build"
        )
        self.assertNotIn(
            "REG_SEGMENT_RESET", result.rows[0].regime_reason_codes
        )
        self.assertIn(
            "REG_SEGMENT_RESET", result.rows[1].regime_reason_codes
        )
        self.assertFalse(result.rows[1].regime_transition_flag)
        self.assertIsNone(result.rows[1].regime_transition_from)
        self.assertIsNone(result.rows[1].regime_transition_to)
        self.assertNotIn(
            "REG_SEGMENT_RESET", result.rows[2].regime_reason_codes
        )

    def test_declared_gap_without_segment_reset_is_rejected(self) -> None:
        second = dataclasses.replace(
            self.rows[1], quality_gap_before=True
        )
        with self.assertRaises(ValueError):
            compute_regimes(
                (self.rows[0], second),
                parent_build_id="gap-build",
            )

    def test_certified_s3_warmup_indices(self) -> None:
        source = []
        for index in range(1_642):
            sma = (
                IndicatorField(
                    value=None,
                    valid=False,
                    warmup_complete=False,
                    reason_codes=("IND_WARMUP_INCOMPLETE",),
                )
                if index < 199
                else 100.0
            )
            source.append(
                _make_row(
                    index,
                    indicator_overrides={"sma_close_200": sma},
                )
            )
        result = compute_regimes(
            compute_signals(source).rows,
            parent_build_id="warmup-build",
        )
        self.assertIs(
            result.rows[1_638].regime_raw, RegimeState.UNKNOWN
        )
        self.assertIs(
            result.rows[1_639].regime_raw, RegimeState.SIDE
        )
        self.assertIs(
            result.rows[1_641].regime_effective, RegimeState.SIDE
        )

    def test_confirmed_bull_to_side_transition(self) -> None:
        source = []
        for index in range(1_446):
            sma = 100.0 + index / 10_000.0
            close = sma if index >= 1_443 else 200.0
            source.append(
                _make_row(
                    index,
                    close=close,
                    indicator_overrides={"sma_close_200": sma},
                )
            )
        result = compute_regimes(
            compute_signals(source).rows,
            parent_build_id="transition-build",
        )
        first, second, third = result.rows[-3:]
        self.assertIs(first.regime_effective, RegimeState.BULL)
        self.assertEqual(first.regime_candidate_count, 1)
        self.assertIs(second.regime_effective, RegimeState.BULL)
        self.assertEqual(second.regime_candidate_count, 2)
        self.assertTrue(third.regime_transition_flag)
        self.assertIs(
            third.regime_transition_from, RegimeState.BULL
        )
        self.assertIs(
            third.regime_transition_to, RegimeState.SIDE
        )
        self.assertIs(third.regime_effective, RegimeState.SIDE)

    def test_future_rows_do_not_change_prefix(self) -> None:
        prefix = compute_regimes(
            self.rows[:1_443], parent_build_id="causal-build"
        )
        extended = compute_regimes(
            self.rows, parent_build_id="causal-build"
        )
        self.assertEqual(prefix.rows, extended.rows[:1_443])

    def test_tampered_state_checksum_is_rejected(self) -> None:
        first = compute_regimes(
            self.rows[:1_441], parent_build_id="hash-build"
        )
        state = first.final_state
        assert state is not None
        object.__setattr__(
            state, "state_payload_sha256", "0" * 64
        )
        second = compute_regimes(
            self.rows[1_441:],
            parent_build_id="hash-build",
            prior_state=state,
        )
        self.assertFalse(second.prior_state_accepted)

    def test_bull_golden_path(self) -> None:
        source = [
            _make_row(
                index,
                close=200.0,
                indicator_overrides={
                    "sma_close_200": 100.0 + index / 10_000.0
                },
            )
            for index in range(1_443)
        ]
        result = compute_regimes(
            compute_signals(source).rows,
            parent_build_id="bull-build",
        )
        self.assertIs(result.rows[-1].regime_raw, RegimeState.BULL)
        self.assertIs(
            result.rows[-1].regime_effective, RegimeState.BULL
        )


if __name__ == "__main__":
    unittest.main()
