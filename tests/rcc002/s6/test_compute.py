"""End-to-end profile and contract tests for RCC-002 S6."""

from __future__ import annotations

import dataclasses
import unittest

from rcc002.s5.constants import RegimeState, TrendStrength
from rcc002.s6.compute import compute_gates
from rcc002.s6.constants import (
    GATE_RESEARCH_OPEN_V1,
    GATE_TREND_ALIGNED_V1,
    GATE_TREND_STRENGTH_ALIGNED_V1,
    GateState,
)
from tests.rcc002.s6._helpers import (
    canonical_s5_rows,
    failed_quality_row,
    invalid_regime_row,
    invalid_strength_row,
    valid_s5_row,
)


class TestDataGateAndResearchOpen(unittest.TestCase):
    def test_default_profile_is_research_open(self) -> None:
        output = compute_gates((invalid_regime_row(),)).rows[0]
        self.assertEqual(output.gate_profile_id, GATE_RESEARCH_OPEN_V1)
        self.assertTrue(output.gate_valid)
        self.assertIs(output.gate_state, GateState.ALLOW_BOTH)
        self.assertTrue(output.allow_long)
        self.assertTrue(output.allow_short)
        self.assertEqual(
            output.gate_reason_codes_long,
            ("GATE_LONG_ALLOWED_RESEARCH_OPEN",),
        )
        self.assertEqual(
            output.gate_reason_codes_short,
            ("GATE_SHORT_ALLOWED_RESEARCH_OPEN",),
        )

    def test_quality_failure_is_valid_block_both(self) -> None:
        for profile in (
            GATE_RESEARCH_OPEN_V1,
            GATE_TREND_ALIGNED_V1,
            GATE_TREND_STRENGTH_ALIGNED_V1,
        ):
            with self.subTest(profile=profile):
                output = compute_gates(
                    (failed_quality_row(),),
                    gate_profile_id=profile,
                ).rows[0]
                self.assertFalse(output.data_gate_pass)
                self.assertTrue(output.gate_valid)
                self.assertIs(output.gate_state, GateState.BLOCK_BOTH)
                self.assertFalse(output.allow_long)
                self.assertFalse(output.allow_short)
                self.assertEqual(
                    output.gate_reason_codes_long,
                    ("GATE_DATA_QUALITY_FAILED",),
                )
                self.assertEqual(
                    output.gate_reason_codes_short,
                    ("GATE_DATA_QUALITY_FAILED",),
                )

    def test_research_open_ignores_invalid_regime_and_strength(self) -> None:
        for row in (invalid_regime_row(), invalid_strength_row()):
            with self.subTest(row=row):
                output = compute_gates((row,)).rows[0]
                self.assertTrue(output.gate_valid)
                self.assertIs(output.gate_state, GateState.ALLOW_BOTH)


class TestTrendAligned(unittest.TestCase):
    def test_complete_valid_regime_truth_table(self) -> None:
        expected = {
            RegimeState.BULL: (
                True,
                False,
                GateState.ALLOW_LONG_ONLY,
                ("GATE_LONG_ALLOWED_BULL",),
                ("GATE_SHORT_BLOCKED_BULL",),
            ),
            RegimeState.SIDE: (
                False,
                False,
                GateState.BLOCK_BOTH,
                ("GATE_LONG_BLOCKED_SIDE",),
                ("GATE_SHORT_BLOCKED_SIDE",),
            ),
            RegimeState.BEAR: (
                False,
                True,
                GateState.ALLOW_SHORT_ONLY,
                ("GATE_LONG_BLOCKED_BEAR",),
                ("GATE_SHORT_ALLOWED_BEAR",),
            ),
        }
        for regime, values in expected.items():
            with self.subTest(regime=regime):
                output = compute_gates(
                    (valid_s5_row(regime=regime),),
                    gate_profile_id=GATE_TREND_ALIGNED_V1,
                ).rows[0]
                self.assertEqual(
                    (
                        output.allow_long,
                        output.allow_short,
                        output.gate_state,
                        output.gate_reason_codes_long,
                        output.gate_reason_codes_short,
                    ),
                    values,
                )
                self.assertTrue(output.gate_valid)

    def test_unknown_regime_is_invalid(self) -> None:
        output = compute_gates(
            (invalid_regime_row(),),
            gate_profile_id=GATE_TREND_ALIGNED_V1,
        ).rows[0]
        self.assertFalse(output.gate_valid)
        self.assertIs(output.gate_state, GateState.INVALID)
        self.assertEqual(
            output.gate_reason_codes_long,
            (
                "GATE_WARMUP_INCOMPLETE",
                "GATE_REGIME_UNKNOWN",
            ),
        )
        self.assertEqual(
            output.gate_reason_codes_short,
            (
                "GATE_WARMUP_INCOMPLETE",
                "GATE_REGIME_UNKNOWN",
            ),
        )

    def test_segment_reset_reason_is_mapped(self) -> None:
        row = dataclasses.replace(
            invalid_regime_row(),
            regime_reason_codes=(
                "REG_WINDOW_CROSSES_INDICATOR_SEGMENT",
                "REG_SEGMENT_RESET",
            ),
        )
        output = compute_gates(
            (row,),
            gate_profile_id=GATE_TREND_ALIGNED_V1,
        ).rows[0]
        expected = (
            "GATE_SEGMENT_RESET",
            "GATE_REGIME_UNKNOWN",
        )
        self.assertEqual(output.gate_reason_codes_long, expected)
        self.assertEqual(output.gate_reason_codes_short, expected)

    def test_effective_unconfirmed_maps_to_warmup(self) -> None:
        row = dataclasses.replace(
            invalid_regime_row(),
            regime_raw=RegimeState.SIDE,
            regime_candidate=RegimeState.SIDE,
            regime_candidate_count=1,
            ma200_slope_1440_pct=0.0,
            regime_reason_codes=("REG_EFFECTIVE_UNCONFIRMED",),
        )
        output = compute_gates(
            (row,),
            gate_profile_id=GATE_TREND_ALIGNED_V1,
        ).rows[0]
        expected = (
            "GATE_WARMUP_INCOMPLETE",
            "GATE_REGIME_UNKNOWN",
        )
        self.assertEqual(output.gate_reason_codes_long, expected)
        self.assertEqual(output.gate_reason_codes_short, expected)

    def test_adx_is_not_required(self) -> None:
        output = compute_gates(
            (invalid_strength_row(),),
            gate_profile_id=GATE_TREND_ALIGNED_V1,
        ).rows[0]
        self.assertTrue(output.gate_valid)
        self.assertTrue(output.allow_long)


class TestTrendStrengthAligned(unittest.TestCase):
    def test_developing_and_strong_allow_aligned_direction(self) -> None:
        for strength in (
            TrendStrength.DEVELOPING,
            TrendStrength.STRONG,
        ):
            for regime, state, allowed_code in (
                (
                    RegimeState.BULL,
                    GateState.ALLOW_LONG_ONLY,
                    "GATE_LONG_ALLOWED_BULL_WITH_STRENGTH",
                ),
                (
                    RegimeState.BEAR,
                    GateState.ALLOW_SHORT_ONLY,
                    "GATE_SHORT_ALLOWED_BEAR_WITH_STRENGTH",
                ),
            ):
                with self.subTest(strength=strength, regime=regime):
                    output = compute_gates(
                        (
                            valid_s5_row(
                                regime=regime, strength=strength
                            ),
                        ),
                        gate_profile_id=(
                            GATE_TREND_STRENGTH_ALIGNED_V1
                        ),
                    ).rows[0]
                    self.assertIs(output.gate_state, state)
                    self.assertIn(
                        allowed_code,
                        output.gate_reason_codes_long
                        + output.gate_reason_codes_short,
                    )

    def test_side_blocks_both_at_sufficient_strength(self) -> None:
        output = compute_gates(
            (
                valid_s5_row(
                    regime=RegimeState.SIDE,
                    strength=TrendStrength.STRONG,
                ),
            ),
            gate_profile_id=GATE_TREND_STRENGTH_ALIGNED_V1,
        ).rows[0]
        self.assertTrue(output.gate_valid)
        self.assertIs(output.gate_state, GateState.BLOCK_BOTH)
        self.assertEqual(
            output.gate_reason_codes_long,
            ("GATE_LONG_BLOCKED_SIDE",),
        )
        self.assertEqual(
            output.gate_reason_codes_short,
            ("GATE_SHORT_BLOCKED_SIDE",),
        )

    def test_weak_blocks_both_with_all_applicable_reasons(self) -> None:
        expected = {
            RegimeState.BULL: (
                ("GATE_LONG_BLOCKED_WEAK_TREND",),
                (
                    "GATE_SHORT_BLOCKED_BULL",
                    "GATE_SHORT_BLOCKED_WEAK_TREND",
                ),
            ),
            RegimeState.SIDE: (
                (
                    "GATE_LONG_BLOCKED_SIDE",
                    "GATE_LONG_BLOCKED_WEAK_TREND",
                ),
                (
                    "GATE_SHORT_BLOCKED_SIDE",
                    "GATE_SHORT_BLOCKED_WEAK_TREND",
                ),
            ),
            RegimeState.BEAR: (
                (
                    "GATE_LONG_BLOCKED_BEAR",
                    "GATE_LONG_BLOCKED_WEAK_TREND",
                ),
                ("GATE_SHORT_BLOCKED_WEAK_TREND",),
            ),
        }
        for regime, reasons in expected.items():
            with self.subTest(regime=regime):
                output = compute_gates(
                    (
                        valid_s5_row(
                            regime=regime,
                            strength=TrendStrength.WEAK,
                        ),
                    ),
                    gate_profile_id=(
                        GATE_TREND_STRENGTH_ALIGNED_V1
                    ),
                ).rows[0]
                self.assertTrue(output.gate_valid)
                self.assertIs(output.gate_state, GateState.BLOCK_BOTH)
                self.assertEqual(
                    (
                        output.gate_reason_codes_long,
                        output.gate_reason_codes_short,
                    ),
                    reasons,
                )

    def test_unknown_strength_is_invalid(self) -> None:
        output = compute_gates(
            (invalid_strength_row(),),
            gate_profile_id=GATE_TREND_STRENGTH_ALIGNED_V1,
        ).rows[0]
        self.assertFalse(output.gate_valid)
        self.assertIs(output.gate_state, GateState.INVALID)
        self.assertEqual(
            output.gate_reason_codes_long,
            ("GATE_TREND_STRENGTH_UNKNOWN",),
        )
        self.assertEqual(
            output.gate_reason_codes_short,
            ("GATE_TREND_STRENGTH_UNKNOWN",),
        )

    def test_invalid_regime_and_strength_keep_both_reasons(self) -> None:
        row = dataclasses.replace(
            invalid_regime_row(),
            trend_strength=TrendStrength.UNKNOWN,
            trend_strength_valid=False,
            trend_strength_reason_codes=(
                "REG_TREND_STRENGTH_INPUT_INVALID",
            ),
        )
        output = compute_gates(
            (row,),
            gate_profile_id=GATE_TREND_STRENGTH_ALIGNED_V1,
        ).rows[0]
        expected = (
            "GATE_WARMUP_INCOMPLETE",
            "GATE_REGIME_UNKNOWN",
            "GATE_TREND_STRENGTH_UNKNOWN",
        )
        self.assertEqual(output.gate_reason_codes_long, expected)
        self.assertEqual(output.gate_reason_codes_short, expected)


class TestS6Contracts(unittest.TestCase):
    def test_empty_input(self) -> None:
        self.assertEqual(compute_gates(()).rows, ())

    def test_unknown_profile_and_version_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compute_gates((), gate_profile_id="UNKNOWN")
        with self.assertRaises(ValueError):
            compute_gates((), gate_profile_version="2.0.0")

    def test_row_count_and_s5_preservation(self) -> None:
        source = canonical_s5_rows()[-3:]
        result = compute_gates(source)
        self.assertEqual(len(result.rows), len(source))
        for input_row, output_row in zip(
            source, result.rows, strict=True
        ):
            for name in (
                "source_row_id",
                "open_time",
                "close",
                "indicators",
                "signals",
                "regime_effective",
                "regime_reason_codes",
            ):
                self.assertEqual(
                    getattr(output_row, name),
                    getattr(input_row, name),
                )

    def test_output_containers_do_not_alias_upstream(self) -> None:
        source = valid_s5_row()
        output = compute_gates((source,)).rows[0]
        self.assertIsNot(output.indicators, source.indicators)
        self.assertIsNot(output.signals, source.signals)
        output.indicators.clear()
        output.signals.clear()
        self.assertTrue(source.indicators)
        self.assertTrue(source.signals)

    def test_gate_evaluated_at_equals_close_time(self) -> None:
        source = valid_s5_row()
        output = compute_gates((source,)).rows[0]
        self.assertEqual(output.gate_evaluated_at, source.close_time)

    def test_partition_parity_for_each_profile(self) -> None:
        source = canonical_s5_rows()[-3:]
        for profile in (
            GATE_RESEARCH_OPEN_V1,
            GATE_TREND_ALIGNED_V1,
            GATE_TREND_STRENGTH_ALIGNED_V1,
        ):
            with self.subTest(profile=profile):
                full = compute_gates(
                    source, gate_profile_id=profile
                ).rows
                split = (
                    compute_gates(
                        source[:1], gate_profile_id=profile
                    ).rows
                    + compute_gates(
                        source[1:], gate_profile_id=profile
                    ).rows
                )
                self.assertEqual(split, full)

    def test_prefix_is_not_changed_by_future_rows(self) -> None:
        source = canonical_s5_rows()[-3:]
        prefix = compute_gates(
            source[:2],
            gate_profile_id=GATE_TREND_ALIGNED_V1,
        ).rows
        full = compute_gates(
            source,
            gate_profile_id=GATE_TREND_ALIGNED_V1,
        ).rows
        self.assertEqual(prefix, full[:2])

    def test_rejects_non_s5_input(self) -> None:
        with self.assertRaises(TypeError):
            compute_gates((object(),))  # type: ignore[arg-type]

    def test_rejects_unordered_input(self) -> None:
        source = canonical_s5_rows()[-3:]
        with self.assertRaises(ValueError):
            compute_gates((source[1], source[0]))

    def test_rejects_mixed_series(self) -> None:
        first = valid_s5_row()
        second = dataclasses.replace(
            canonical_s5_rows()[-2], symbol="ETHUSDT"
        )
        with self.assertRaises(ValueError):
            compute_gates((first, second))

    def test_rejects_unknown_s5_schema_major(self) -> None:
        row = dataclasses.replace(valid_s5_row())
        object.__setattr__(row, "regime_schema_version", "2.0.0")
        with self.assertRaises(ValueError):
            compute_gates((row,))

    def test_no_forbidden_alias_or_downstream_fields(self) -> None:
        field_names = {
            field.name
            for field in dataclasses.fields(
                type(compute_gates((valid_s5_row(),)).rows[0])
            )
        }
        self.assertNotIn("gate_inputs_valid", field_names)
        self.assertNotIn("gate_reason_mask", field_names)
        self.assertFalse(
            {
                "forward_return",
                "label",
                "strategy_entry",
                "position_size",
            }
            & field_names
        )


if __name__ == "__main__":
    unittest.main()
