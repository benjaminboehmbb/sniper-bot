"""Incremental invalidation and chronological split-purge tests."""

from __future__ import annotations

import unittest

from rcc002.s7.planning import (
    invalidation_start_index,
    label_crosses_split,
)


class TestIncrementalPlanning(unittest.TestCase):
    def test_changed_bar_invalidates_k_minus_max_horizon_through_k(
        self,
    ) -> None:
        self.assertEqual(invalidation_start_index(2000), 560)
        self.assertEqual(invalidation_start_index(100), 0)


class TestSplitPurging(unittest.TestCase):
    def test_endpoint_at_or_after_boundary_is_purged(self) -> None:
        split = 1_800_000_600_000
        self.assertTrue(
            label_crosses_split(
                row_open_time=1_800_000_300_000,
                split_open_time=split,
                horizon_bars=5,
            )
        )
        self.assertFalse(
            label_crosses_split(
                row_open_time=1_800_000_240_000,
                split_open_time=split,
                horizon_bars=5,
            )
        )


if __name__ == "__main__":
    unittest.main()
