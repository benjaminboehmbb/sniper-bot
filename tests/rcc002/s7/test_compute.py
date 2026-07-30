"""End-to-end S7 validity, horizon, and parity tests."""

from __future__ import annotations

import dataclasses
import math
import random
import unittest

from rcc002.s7.compute import compute_labels
from rcc002.s7.constants import HORIZONS, BarrierOutcome
from rcc002.s7.formulas import barrier_outcomes, excursion_values
from tests.rcc002.s7._helpers import (
    make_s6_rows,
    mark_quality_failed,
)


class TestHandCalculatedReturns(unittest.TestCase):
    def test_h001_all_families(self) -> None:
        rows = make_s6_rows(
            (100.0, 110.0),
            opens=(100.0, 100.0),
            highs=(100.0, 112.0),
            lows=(100.0, 95.0),
        )
        labels = compute_labels(rows, output_row_count=1).rows[0].horizons[
            "H001"
        ]
        self.assertAlmostEqual(labels.fwd_cc_long_ret, 0.1, places=15)
        self.assertAlmostEqual(labels.fwd_cc_short_ret, -0.1, places=15)
        self.assertAlmostEqual(labels.fwd_noc_long_ret, 0.1, places=15)
        self.assertAlmostEqual(labels.fwd_noc_short_ret, -0.1, places=15)
        self.assertAlmostEqual(
            labels.fwd_noc_long_net_proxy_fee_rt_0004,
            0.0996,
            places=15,
        )
        self.assertEqual(labels.label_cc_long_direction, 1)
        self.assertEqual(labels.label_cc_short_direction, -1)
        self.assertEqual(labels.fwd_long_mfe_first_bar, 1)
        self.assertEqual(labels.fwd_long_mae_first_bar, 1)
        self.assertIs(
            labels.barrier_long_outcome_tp050_sl020,
            BarrierOutcome.AMBIGUOUS_BOTH_HIT,
        )
        self.assertEqual(
            labels.barrier_reason_codes,
            ("LBL_BARRIER_BOTH_HIT",),
        )
        self.assertTrue(labels.barrier_valid)

    def test_no_deadband_and_short_symmetry(self) -> None:
        rows = make_s6_rows((100.0, math.nextafter(100.0, math.inf)))
        labels = compute_labels(rows, output_row_count=1).rows[0].horizons[
            "H001"
        ]
        self.assertEqual(labels.label_cc_long_direction, 1)
        self.assertEqual(labels.label_cc_short_direction, -1)
        self.assertEqual(
            labels.fwd_cc_short_ret, -labels.fwd_cc_long_ret
        )


class TestHorizonsAndValidity(unittest.TestCase):
    def test_every_horizon_uses_exact_t_plus_h(self) -> None:
        prices = tuple(100.0 + index for index in range(1441))
        row = compute_labels(
            make_s6_rows(prices), output_row_count=1
        ).rows[0]
        for horizon in HORIZONS:
            with self.subTest(horizon=horizon.horizon_id):
                labels = row.horizons[horizon.horizon_id]
                expected = prices[horizon.bars] / prices[0] - 1.0
                self.assertAlmostEqual(
                    labels.fwd_cc_long_ret, expected, places=15
                )
                self.assertEqual(
                    labels.label_horizon_bars, horizon.bars
                )

    def test_tail_is_preserved_and_exclusively_incomplete(self) -> None:
        rows = make_s6_rows((100.0, 101.0, 102.0))
        output = compute_labels(rows).rows
        self.assertEqual(len(output), len(rows))
        self.assertTrue(output[0].horizons["H001"].fwd_cc_valid)
        for row in output:
            for horizon_id, labels in row.horizons.items():
                if not labels.fwd_cc_valid and (
                    labels.fwd_cc_reason_codes
                    == ("LBL_FUTURE_HORIZON_INCOMPLETE",)
                ):
                    self.assertIsNone(labels.fwd_cc_long_ret)
                    self.assertIsNone(labels.label_available_at)
                    self.assertIs(
                        labels.barrier_long_outcome_tp050_sl020,
                        BarrierOutcome.INVALID,
                    )

    def test_market_segment_crossing_invalidates_all_families(self) -> None:
        rows = make_s6_rows(
            (100.0, 101.0),
            segment_ids=("segment-a", "segment-b"),
        )
        labels = compute_labels(rows, output_row_count=1).rows[0].horizons[
            "H001"
        ]
        expected = ("LBL_WINDOW_CROSSES_MARKET_SEGMENT",)
        self.assertEqual(labels.fwd_cc_reason_codes, expected)
        self.assertEqual(labels.fwd_noc_reason_codes, expected)
        self.assertEqual(labels.fwd_excursion_reason_codes, expected)
        self.assertEqual(labels.barrier_reason_codes, expected)

    def test_timestamp_gap_is_segment_crossing_not_tail(self) -> None:
        rows = list(make_s6_rows((100.0, 101.0, 102.0)))
        rows[1] = dataclasses.replace(
            rows[1],
            open_time=rows[1].open_time + 60_000,
            close_time=rows[1].close_time + 60_000,
            gate_evaluated_at=rows[1].gate_evaluated_at + 60_000,
            market_segment_id="segment-b",
        )
        rows[2] = dataclasses.replace(
            rows[2],
            open_time=rows[2].open_time + 60_000,
            close_time=rows[2].close_time + 60_000,
            gate_evaluated_at=rows[2].gate_evaluated_at + 60_000,
            market_segment_id="segment-b",
        )
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H001"]
        self.assertEqual(
            labels.fwd_cc_reason_codes,
            ("LBL_WINDOW_CROSSES_MARKET_SEGMENT",),
        )

    def test_future_quality_and_synthetic_codes(self) -> None:
        rows = list(make_s6_rows((100.0, 101.0)))
        rows[1] = mark_quality_failed(rows[1], synthetic=True)
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H001"]
        expected = (
            "LBL_FUTURE_BAR_QUALITY_FAILED",
            "LBL_SYNTHETIC_INPUT_DISALLOWED",
        )
        self.assertEqual(labels.fwd_cc_reason_codes, expected)
        self.assertFalse(labels.fwd_cc_valid)
        self.assertIsNone(labels.fwd_cc_long_ret)

    def test_intermediate_quality_failure_is_family_local(self) -> None:
        rows = list(
            make_s6_rows(
                (100.0, 101.0, 102.0, 103.0, 104.0, 105.0)
            )
        )
        rows[3] = mark_quality_failed(rows[3])
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H005"]
        self.assertTrue(labels.fwd_cc_valid)
        self.assertTrue(labels.fwd_noc_valid)
        self.assertTrue(labels.label_cc_direction_valid)
        self.assertTrue(labels.label_noc_direction_valid)
        self.assertFalse(labels.fwd_excursion_valid)
        self.assertFalse(labels.barrier_valid)
        self.assertEqual(
            labels.fwd_excursion_reason_codes,
            ("LBL_FUTURE_BAR_QUALITY_FAILED",),
        )

    def test_intermediate_synthetic_bar_is_family_local(self) -> None:
        rows = list(
            make_s6_rows(
                (100.0, 101.0, 102.0, 103.0, 104.0, 105.0)
            )
        )
        rows[3] = mark_quality_failed(rows[3], synthetic=True)
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H005"]
        self.assertTrue(labels.fwd_cc_valid)
        self.assertTrue(labels.fwd_noc_valid)
        self.assertEqual(
            labels.fwd_excursion_reason_codes,
            (
                "LBL_FUTURE_BAR_QUALITY_FAILED",
                "LBL_SYNTHETIC_INPUT_DISALLOWED",
            ),
        )

    def test_entry_quality_failure_does_not_invalidate_cc(self) -> None:
        rows = list(
            make_s6_rows(
                (100.0, 101.0, 102.0, 103.0, 104.0, 105.0)
            )
        )
        rows[1] = mark_quality_failed(rows[1])
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H005"]
        self.assertTrue(labels.fwd_cc_valid)
        self.assertFalse(labels.fwd_noc_valid)
        self.assertFalse(labels.fwd_excursion_valid)
        self.assertFalse(labels.barrier_valid)

    def test_exit_quality_failure_invalidates_all_families(self) -> None:
        rows = list(
            make_s6_rows(
                (100.0, 101.0, 102.0, 103.0, 104.0, 105.0)
            )
        )
        rows[5] = mark_quality_failed(rows[5])
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H005"]
        self.assertFalse(labels.fwd_cc_valid)
        self.assertFalse(labels.fwd_noc_valid)
        self.assertFalse(labels.fwd_excursion_valid)
        self.assertFalse(labels.barrier_valid)

    def test_invalid_signal_row_is_input_invalid_for_all_families(
        self,
    ) -> None:
        rows = list(make_s6_rows((100.0, 101.0)))
        rows[0] = mark_quality_failed(rows[0])
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H001"]
        for codes in (
            labels.fwd_cc_reason_codes,
            labels.fwd_noc_reason_codes,
            labels.fwd_excursion_reason_codes,
            labels.label_cc_direction_reason_codes,
            labels.label_noc_direction_reason_codes,
            labels.barrier_reason_codes,
        ):
            self.assertEqual(codes, ("LBL_INPUT_INVALID",))

    def test_invalid_signal_entry_and_exit_are_family_local(self) -> None:
        rows = list(
            make_s6_rows(
                (100.0, 101.0),
                opens=(100.0, 0.0),
                highs=(100.0, 102.0),
                lows=(100.0, 99.0),
            )
        )
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H001"]
        self.assertTrue(labels.fwd_cc_valid)
        self.assertEqual(
            labels.fwd_noc_reason_codes,
            ("LBL_ENTRY_PRICE_INVALID",),
        )
        self.assertFalse(labels.fwd_excursion_valid)
        self.assertFalse(labels.barrier_valid)

        rows = list(make_s6_rows((100.0, 101.0)))
        rows[1] = dataclasses.replace(rows[1], close=0.0)
        labels = compute_labels(
            tuple(rows), output_row_count=1
        ).rows[0].horizons["H001"]
        self.assertEqual(
            labels.fwd_cc_reason_codes,
            ("LBL_EXIT_PRICE_INVALID",),
        )
        self.assertEqual(
            labels.fwd_noc_reason_codes,
            ("LBL_EXIT_PRICE_INVALID",),
        )
        self.assertTrue(labels.fwd_excursion_valid)
        self.assertTrue(labels.barrier_valid)


class TestContractsAndParity(unittest.TestCase):
    def test_s6_fields_and_mutable_containers_are_preserved(self) -> None:
        source = make_s6_rows((100.0, 101.0))[0]
        result = compute_labels(
            make_s6_rows((100.0, 101.0)), output_row_count=1
        ).rows[0]
        for field in dataclasses.fields(type(source)):
            self.assertEqual(
                getattr(result, field.name), getattr(source, field.name)
            )
        self.assertIsNot(result.indicators, source.indicators)
        self.assertIsNot(result.signals, source.signals)
        result.indicators.clear()
        result.signals.clear()
        self.assertTrue(source.indicators)
        self.assertTrue(source.signals)

    def test_partition_with_forward_overlap_matches_serial(self) -> None:
        rows = make_s6_rows(
            tuple(100.0 + (index % 7) for index in range(20))
        )
        serial = compute_labels(rows).rows
        partitioned = []
        partition_size = 6
        for start in range(0, len(rows), partition_size):
            owned = min(partition_size, len(rows) - start)
            partition_rows = rows[start:]
            partitioned.extend(
                compute_labels(
                    partition_rows, output_row_count=owned
                ).rows
            )
        self.assertEqual(tuple(partitioned), serial)

    def test_optimized_windows_match_naive_formula_oracle(self) -> None:
        generator = random.Random(730)
        closes = [100.0]
        opens = [100.0]
        highs = [101.0]
        lows = [99.0]
        for _ in range(1, 90):
            open_price = closes[-1]
            close = open_price * (1.0 + generator.uniform(-0.01, 0.01))
            opens.append(open_price)
            closes.append(close)
            highs.append(max(open_price, close) * 1.01)
            lows.append(min(open_price, close) * 0.99)
        rows = make_s6_rows(
            tuple(closes),
            opens=tuple(opens),
            highs=tuple(highs),
            lows=tuple(lows),
        )
        output = compute_labels(rows).rows
        for index, result in enumerate(output):
            for horizon in HORIZONS:
                if index + horizon.bars >= len(rows):
                    continue
                with self.subTest(
                    index=index, horizon=horizon.horizon_id
                ):
                    future = rows[index + 1 : index + horizon.bars + 1]
                    expected_excursion = excursion_values(
                        entry_price=future[0].open,
                        highs=tuple(row.high for row in future),
                        lows=tuple(row.low for row in future),
                    )
                    expected_barrier = barrier_outcomes(
                        entry_price=future[0].open,
                        future_rows=tuple(
                            (
                                row.open,
                                row.high,
                                row.low,
                                row.close_time,
                            )
                            for row in future
                        ),
                    )
                    labels = result.horizons[horizon.horizon_id]
                    actual_excursion = (
                        labels.fwd_long_mfe,
                        labels.fwd_long_mae,
                        labels.fwd_short_mfe,
                        labels.fwd_short_mae,
                        labels.fwd_long_mfe_first_bar,
                        labels.fwd_long_mae_first_bar,
                        labels.fwd_short_mfe_first_bar,
                        labels.fwd_short_mae_first_bar,
                    )
                    actual_barrier = (
                        labels.barrier_long_outcome_tp050_sl020,
                        labels.barrier_short_outcome_tp050_sl020,
                        labels.barrier_long_first_hit_bar_tp050_sl020,
                        labels.barrier_short_first_hit_bar_tp050_sl020,
                        labels.barrier_long_first_hit_time_tp050_sl020,
                        labels.barrier_short_first_hit_time_tp050_sl020,
                    )
                    self.assertEqual(actual_excursion, expected_excursion)
                    self.assertEqual(actual_barrier, expected_barrier)

    def test_prefix_causality(self) -> None:
        base = make_s6_rows(tuple(100.0 + i for i in range(10)))
        extended = make_s6_rows(tuple(100.0 + i for i in range(15)))
        base_output = compute_labels(base).rows
        extended_output = compute_labels(extended).rows
        # H005 for rows whose horizon was already complete is unchanged.
        for index in range(5):
            self.assertEqual(
                base_output[index].horizons["H005"],
                extended_output[index].horizons["H005"],
            )

    def test_change_after_horizon_does_not_change_label(self) -> None:
        rows = make_s6_rows((100.0, 101.0, 102.0, 103.0))
        changed = list(rows)
        changed[3] = dataclasses.replace(
            changed[3],
            open=999.0,
            high=999.0,
            low=999.0,
            close=999.0,
        )
        original = compute_labels(
            rows, output_row_count=1
        ).rows[0].horizons["H001"]
        modified = compute_labels(
            tuple(changed), output_row_count=1
        ).rows[0].horizons["H001"]
        self.assertEqual(original, modified)

    def test_profile_and_input_contracts_fail_closed(self) -> None:
        rows = make_s6_rows((100.0, 101.0))
        with self.assertRaises(ValueError):
            compute_labels(rows, cost_profile_id="UNKNOWN")
        with self.assertRaises(TypeError):
            compute_labels((object(),))
        with self.assertRaises(ValueError):
            compute_labels(tuple(reversed(rows)))

    def test_all_profile_dimensions_are_exact(self) -> None:
        rows = make_s6_rows((100.0, 101.0))
        cases = (
            {"label_profile_id": "UNKNOWN"},
            {"horizon_registry_id": "UNKNOWN"},
            {"barrier_profile_id": "UNKNOWN"},
            {"reason_code_registry_version": "2.0.0"},
            {"numeric_profile_id": "UNKNOWN"},
        )
        for arguments in cases:
            with self.subTest(arguments=arguments):
                with self.assertRaises(ValueError):
                    compute_labels(rows, **arguments)

    def test_output_overlap_count_is_validated(self) -> None:
        rows = make_s6_rows((100.0, 101.0))
        for count in (-1, 3, True):
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    compute_labels(rows, output_row_count=count)


if __name__ == "__main__":
    unittest.main()
