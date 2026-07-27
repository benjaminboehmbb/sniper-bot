"""Unit tests for rcc002.s1.row_id."""

import unittest

from rcc002.s1.row_id import (
    SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID,
    compute_source_row_id,
)

SNAPSHOT = "source:sha256:" + "a" * 64


class ComputeSourceRowIdTests(unittest.TestCase):
    def test_is_a_string(self) -> None:
        self.assertIsInstance(compute_source_row_id(SNAPSHOT, 0), str)

    def test_deterministic(self) -> None:
        self.assertEqual(
            compute_source_row_id(SNAPSHOT, 5), compute_source_row_id(SNAPSHOT, 5)
        )

    def test_distinct_for_distinct_indices(self) -> None:
        self.assertNotEqual(
            compute_source_row_id(SNAPSHOT, 0), compute_source_row_id(SNAPSHOT, 1)
        )

    def test_distinct_for_distinct_snapshots(self) -> None:
        other_snapshot = "source:sha256:" + "b" * 64
        self.assertNotEqual(
            compute_source_row_id(SNAPSHOT, 0),
            compute_source_row_id(other_snapshot, 0),
        )

    def test_embeds_versioned_profile_id(self) -> None:
        row_id = compute_source_row_id(SNAPSHOT, 0)
        self.assertIn(SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID, row_id)

    def test_negative_index_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compute_source_row_id(SNAPSHOT, -1)

    def test_lexicographic_order_matches_numeric_order(self) -> None:
        ids = [compute_source_row_id(SNAPSHOT, i) for i in (1, 2, 10, 20, 100)]
        self.assertEqual(ids, sorted(ids))


if __name__ == "__main__":
    unittest.main()
