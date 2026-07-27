"""Unit tests for rcc002.s3.segment."""

import unittest

from rcc002.s3.segment import compute_indicator_segment_id, split_into_indicator_segments


class ComputeIndicatorSegmentIdTests(unittest.TestCase):
    def test_deterministic(self) -> None:
        kwargs = dict(market_segment_id="m1", first_open_time_ms=0, quality_gate_pass=True)
        self.assertEqual(compute_indicator_segment_id(**kwargs), compute_indicator_segment_id(**kwargs))

    def test_distinct_for_distinct_quality_gate_pass(self) -> None:
        base = dict(market_segment_id="m1", first_open_time_ms=0)
        self.assertNotEqual(
            compute_indicator_segment_id(quality_gate_pass=True, **base),
            compute_indicator_segment_id(quality_gate_pass=False, **base),
        )

    def test_distinct_for_distinct_market_segment(self) -> None:
        base = dict(first_open_time_ms=0, quality_gate_pass=True)
        self.assertNotEqual(
            compute_indicator_segment_id(market_segment_id="m1", **base),
            compute_indicator_segment_id(market_segment_id="m2", **base),
        )

    def test_embeds_profile_id(self) -> None:
        segment_id = compute_indicator_segment_id(
            market_segment_id="m1", first_open_time_ms=0, quality_gate_pass=True
        )
        self.assertIn("RCC002_INDICATOR_SEGMENTATION_V1", segment_id)


class SplitIntoIndicatorSegmentsTests(unittest.TestCase):
    def test_empty_input(self) -> None:
        self.assertEqual(split_into_indicator_segments([], [], []), [])

    def test_single_homogeneous_run_is_one_segment(self) -> None:
        segments = split_into_indicator_segments(
            ["m1", "m1", "m1"], [True, True, True], [0, 60_000, 120_000]
        )
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].row_indices, (0, 1, 2))

    def test_market_segment_change_splits(self) -> None:
        segments = split_into_indicator_segments(
            ["m1", "m2"], [True, True], [0, 60_000]
        )
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].row_indices, (0,))
        self.assertEqual(segments[1].row_indices, (1,))

    def test_quality_gate_pass_toggle_splits(self) -> None:
        segments = split_into_indicator_segments(
            ["m1", "m1", "m1"], [True, False, True], [0, 60_000, 120_000]
        )
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[1].quality_gate_pass, False)

    def test_explicit_reset_splits(self) -> None:
        segments = split_into_indicator_segments(
            ["m1", "m1"], [True, True], [0, 60_000], explicit_state_resets=[False, True]
        )
        self.assertEqual(len(segments), 2)

    def test_segment_ids_differ_across_split(self) -> None:
        segments = split_into_indicator_segments(
            ["m1", "m1", "m1"], [True, False, True], [0, 60_000, 120_000]
        )
        ids = {s.indicator_segment_id for s in segments}
        self.assertEqual(len(ids), 3)


if __name__ == "__main__":
    unittest.main()
