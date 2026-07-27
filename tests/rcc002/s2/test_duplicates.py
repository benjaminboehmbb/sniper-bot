"""Unit tests for rcc002.s2.duplicates."""

import unittest

from rcc002.s1.schema import S1Row
from rcc002.s2.duplicates import (
    ConflictingDuplicatesWithoutResolutionRuleError,
    resolve_duplicates,
)

SNAPSHOT = "source:sha256:" + "a" * 64


def make_row(source_row_id: str, open_time: int, **overrides: object) -> S1Row:
    fields: dict[str, object] = dict(
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
    fields.update(overrides)
    return S1Row(**fields)  # type: ignore[arg-type]


class NoDuplicatesTests(unittest.TestCase):
    def test_single_row_per_key_passes_through(self) -> None:
        rows = [make_row("r0", 0), make_row("r1", 60_000)]
        result = resolve_duplicates(rows)
        self.assertEqual(len(result.rows), 2)
        self.assertEqual(result.collapsed_groups, ())
        self.assertEqual(result.resolved_conflicts, ())


class IdenticalDuplicateCollapseTests(unittest.TestCase):
    def test_identical_duplicates_collapse_to_one_row(self) -> None:
        rows = [make_row("r1", 0), make_row("r0", 0)]  # same values, different source_row_id
        result = resolve_duplicates(rows)
        self.assertEqual(len(result.rows), 1)

    def test_primary_is_lexicographically_smallest_source_row_id(self) -> None:
        rows = [make_row("r1", 0), make_row("r0", 0)]
        result = resolve_duplicates(rows)
        self.assertEqual(result.rows[0].source_row_id, "r0")

    def test_collapsed_group_records_other_source_row_ids(self) -> None:
        rows = [make_row("r1", 0), make_row("r0", 0)]
        result = resolve_duplicates(rows)
        self.assertEqual(len(result.collapsed_groups), 1)
        self.assertEqual(result.collapsed_groups[0].collapsed_source_row_ids, ("r1",))

    def test_primary_row_id_in_identical_collapse_primary_set(self) -> None:
        rows = [make_row("r1", 0), make_row("r0", 0)]
        result = resolve_duplicates(rows)
        self.assertIn("r0", result.identical_collapse_primary_source_row_ids)


class ConflictingDuplicateTests(unittest.TestCase):
    def test_no_resolution_rule_raises(self) -> None:
        rows = [make_row("r0", 0, close=1.5), make_row("r1", 0, close=9.9)]
        with self.assertRaises(ConflictingDuplicatesWithoutResolutionRuleError):
            resolve_duplicates(rows)

    def test_rule_returning_none_raises(self) -> None:
        rows = [make_row("r0", 0, close=1.5), make_row("r1", 0, close=9.9)]
        with self.assertRaises(ConflictingDuplicatesWithoutResolutionRuleError):
            resolve_duplicates(rows, conflict_resolution_rule=lambda group: None)

    def test_rule_selecting_winner_resolves(self) -> None:
        rows = [make_row("r0", 0, close=1.5), make_row("r1", 0, close=9.9)]
        result = resolve_duplicates(
            rows, conflict_resolution_rule=lambda group: max(group, key=lambda r: r.close)
        )
        self.assertEqual(len(result.rows), 1)
        self.assertEqual(result.rows[0].source_row_id, "r1")

    def test_resolved_conflict_records_discarded_ids(self) -> None:
        rows = [make_row("r0", 0, close=1.5), make_row("r1", 0, close=9.9)]
        result = resolve_duplicates(
            rows, conflict_resolution_rule=lambda group: max(group, key=lambda r: r.close)
        )
        self.assertEqual(len(result.resolved_conflicts), 1)
        self.assertEqual(result.resolved_conflicts[0].discarded_source_row_ids, ("r0",))
        self.assertIn("r1", result.conflict_resolved_source_row_ids)

    def test_rule_returning_row_not_in_group_raises(self) -> None:
        rows = [make_row("r0", 0, close=1.5), make_row("r1", 0, close=9.9)]
        other_row = make_row("r2", 60_000, close=1.5)
        with self.assertRaises(ValueError):
            resolve_duplicates(rows, conflict_resolution_rule=lambda group: other_row)


if __name__ == "__main__":
    unittest.main()
