"""Unit tests for rcc002.s1.row_id."""

import json
import unittest
from pathlib import Path

from rcc002.s1.row_id import (
    SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID,
    SOURCE_ROW_ID_CANONICALIZATION_PROFILE_VERSION,
    SourceRowIdError,
    compute_source_row_id,
    validate_source_row_id_coordinates,
)

SNAPSHOT = "source:sha256:" + "a" * 64
FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures/rcc002/source/source_identity_golden.v1.json"
)


def negative_case(case_id: str) -> dict[str, object]:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return next(
        case
        for case in fixture["negative_cases"]
        if case["case_id"] == case_id
    )


class ComputeSourceRowIdTests(unittest.TestCase):
    def test_is_a_string(self) -> None:
        self.assertIsInstance(compute_source_row_id(SNAPSHOT, 0, 0), str)

    def test_deterministic(self) -> None:
        self.assertEqual(
            compute_source_row_id(SNAPSHOT, 0, 5),
            compute_source_row_id(SNAPSHOT, 0, 5),
        )

    def test_distinct_for_distinct_indices(self) -> None:
        self.assertNotEqual(
            compute_source_row_id(SNAPSHOT, 0, 0),
            compute_source_row_id(SNAPSHOT, 0, 1),
        )

    def test_distinct_for_distinct_snapshots(self) -> None:
        other_snapshot = "source:sha256:" + "b" * 64
        self.assertNotEqual(
            compute_source_row_id(SNAPSHOT, 0, 0),
            compute_source_row_id(other_snapshot, 0, 0),
        )

    def test_embeds_versioned_profile_id(self) -> None:
        row_id = compute_source_row_id(SNAPSHOT, 0, 0)
        self.assertIn(SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID, row_id)
        self.assertEqual(SOURCE_ROW_ID_CANONICALIZATION_PROFILE_VERSION, "2.0.0")

    def test_negative_index_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compute_source_row_id(SNAPSHOT, 0, -1)

    def test_lexicographic_order_matches_numeric_order(self) -> None:
        ids = [
            compute_source_row_id(SNAPSHOT, 0, i)
            for i in (1, 2, 10, 20, 100)
        ]
        self.assertEqual(ids, sorted(ids))

    def test_file_ordinal_prevents_multi_file_collision(self) -> None:
        self.assertNotEqual(
            compute_source_row_id(SNAPSHOT, 0, 5),
            compute_source_row_id(SNAPSHOT, 1, 5),
        )

    def test_exact_registered_encoding(self) -> None:
        self.assertEqual(
            compute_source_row_id(SNAPSHOT, 12, 1440),
            (
                "RCC002_S1_SOURCE_ROW_ID_V2:"
                f"{SNAPSHOT}:00000012:00000000000000001440"
            ),
        )

    def test_negative_file_ordinal_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compute_source_row_id(SNAPSHOT, -1, 0)

    def test_registered_width_overflow_rejected(self) -> None:
        case = negative_case("row_id_width_overflow")
        with self.assertRaises(SourceRowIdError) as context:
            compute_source_row_id(
                SNAPSHOT,
                int(case["source_file_ordinal"]),
                0,
            )
        self.assertEqual(
            context.exception.reason_code,
            case["expected_error"],
        )
        with self.assertRaises(ValueError):
            compute_source_row_id(SNAPSHOT, 0, 10**20)

    def test_record_index_after_sort_is_rejected(self) -> None:
        case = negative_case("record_index_after_sort")
        source_row_id = compute_source_row_id(SNAPSHOT, 0, 0)
        with self.assertRaises(SourceRowIdError) as context:
            validate_source_row_id_coordinates(
                source_row_id,
                source_snapshot_id=SNAPSHOT,
                source_file_ordinal=0,
                original_record_index=2,
            )
        self.assertEqual(
            context.exception.reason_code,
            case["expected_error"],
        )

    def test_invalid_snapshot_identity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            compute_source_row_id("snapshot-local", 0, 0)


if __name__ == "__main__":
    unittest.main()
