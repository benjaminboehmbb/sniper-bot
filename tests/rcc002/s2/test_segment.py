"""Unit tests for rcc002.s2.segment."""

import unittest

from rcc002.s1.schema import S1Row
from rcc002.s2.segment import (
    MARKET_SEGMENT_ID_PROFILE_ID,
    annotate_gaps_and_segments,
    compute_market_segment_id,
)

SNAPSHOT = "source:sha256:" + "a" * 64


def make_row(source_row_id: str, open_time: int) -> S1Row:
    return S1Row(
        source_snapshot_id=SNAPSHOT,
        source_row_id=source_row_id,
        provider="binance",
        market_type="spot",
        symbol="BTCUSDT",
        interval="1m",
        open_time=open_time,
        close_time=open_time + 59_999,
        open=1.0,
        high=2.0,
        low=0.5,
        close=1.5,
        volume=100.0,
    )


class ComputeMarketSegmentIdTests(unittest.TestCase):
    def test_deterministic(self) -> None:
        kwargs = dict(
            provider=None,
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
            first_open_time_ms=0,
            multi_provider=False,
        )
        self.assertEqual(compute_market_segment_id(**kwargs), compute_market_segment_id(**kwargs))

    def test_embeds_profile_id(self) -> None:
        segment_id = compute_market_segment_id(
            provider=None,
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
            first_open_time_ms=0,
            multi_provider=False,
        )
        self.assertIn(MARKET_SEGMENT_ID_PROFILE_ID, segment_id)

    def test_distinct_for_distinct_first_open_time(self) -> None:
        base = dict(
            provider=None, market_type="spot", symbol="BTCUSDT", interval="1m", multi_provider=False
        )
        self.assertNotEqual(
            compute_market_segment_id(first_open_time_ms=0, **base),
            compute_market_segment_id(first_open_time_ms=60_000, **base),
        )

    def test_no_random_uuid_is_used(self) -> None:
        # Two independently-computed IDs for the same identity must match
        # exactly (a random UUID would never satisfy this).
        kwargs = dict(
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
            first_open_time_ms=120_000,
            multi_provider=True,
        )
        self.assertEqual(compute_market_segment_id(**kwargs), compute_market_segment_id(**kwargs))


class AnnotateGapsAndSegmentsTests(unittest.TestCase):
    def _annotate(self, rows):
        return annotate_gaps_and_segments(
            rows,
            interval="1m",
            interval_duration_ms=60_000,
            provider=None,
            market_type="spot",
            symbol="BTCUSDT",
            multi_provider=False,
        )

    def test_empty_input_yields_empty_output(self) -> None:
        self.assertEqual(self._annotate([]), [])

    def test_contiguous_rows_share_one_segment_no_gaps(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000), make_row("r2", 120_000)]
        annotations = self._annotate(rows)
        segment_ids = {a.market_segment_id for a in annotations}
        self.assertEqual(len(segment_ids), 1)
        self.assertFalse(any(a.gap_before or a.gap_after for a in annotations))
        self.assertFalse(any(a.gap_detected for a in annotations))

    def test_gap_flags_adjacent_rows(self) -> None:
        # r0 at 0, r1 at 180000 (a 2-interval gap), skipping 60000 and 120000
        rows = [make_row("r0", 0), make_row("r1", 180_000)]
        annotations = self._annotate(rows)
        by_id = {a.source_row_id: a for a in annotations}
        self.assertTrue(by_id["r0"].gap_after)
        self.assertFalse(by_id["r0"].gap_before)
        self.assertTrue(by_id["r1"].gap_before)
        self.assertFalse(by_id["r1"].gap_after)
        self.assertTrue(by_id["r0"].gap_detected)
        self.assertTrue(by_id["r1"].gap_detected)

    def test_gap_starts_new_segment(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 180_000)]
        annotations = self._annotate(rows)
        by_id = {a.source_row_id: a for a in annotations}
        self.assertNotEqual(by_id["r0"].market_segment_id, by_id["r1"].market_segment_id)

    def test_first_row_starts_segment_without_gap(self) -> None:
        rows = [make_row("r0", 0)]
        annotations = self._annotate(rows)
        self.assertFalse(annotations[0].gap_before)
        self.assertFalse(annotations[0].gap_detected)


if __name__ == "__main__":
    unittest.main()
