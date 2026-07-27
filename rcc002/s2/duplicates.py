"""S2 duplicate detection and resolution.

Transcribed from RCC_002_DATA_VALIDATION_2026-07-23.md §10 ("Duplikate und
Quellkollisionen"). Duplicate removal here is an accounted-for, certified
category, not a Row Preservation violation: Data Pipeline §5.8's row
preservation principle concerns `quality_gate_pass`-based deletion of rows
already admitted to the canonical pipeline; deduplication is a separate,
explicitly sanctioned mechanism, confirmed by Data Validation §17.1's own
reconciliation equation `parsed_rows = normalized_rows + duplicate_rows_
removed + out_of_scope_rows`, which treats `duplicate_rows_removed` as an
accounted, expected term.
"""

from __future__ import annotations

import dataclasses
from typing import Callable, Sequence

from rcc002.s1.schema import S1Row

# Implementation-owned, versioned, self-defined identical-duplicate
# collapse rule (§10.1: "MAY ... reduziert werden, wenn ... die
# Deduplizierungsregel versioniert ist"). Primary row = lexicographically
# smallest `source_row_id`, which (per rcc002.s1.row_id's zero-padded
# encoding) corresponds to the earliest original per-file occurrence.
IDENTICAL_DUPLICATE_COLLAPSE_PROFILE_ID = "RCC002_S2_DUPLICATE_COLLAPSE_V1"

# Canonical value fields compared for identical-vs-conflicting
# classification (everything except the primary-key fields themselves and
# per-source provenance fields, which naturally differ row to row).
_COMPARISON_FIELDS: tuple[str, ...] = ("close_time", "open", "high", "low", "close", "volume")


class ConflictingDuplicatesWithoutResolutionRuleError(Exception):
    """§10.2: "Ohne diese Regel bricht der Build ab."

    Raised when a canonical-key group has conflicting values (differ in at
    least one of `_COMPARISON_FIELDS`) and no `conflict_resolution_rule`
    was supplied, or the supplied rule declined to resolve this group.
    """

    def __init__(self, canonical_key: tuple[object, ...], rows: Sequence[S1Row]) -> None:
        self.canonical_key = canonical_key
        self.rows = tuple(rows)
        super().__init__(
            f"{len(self.rows)} conflicting duplicate rows for canonical key "
            f"{canonical_key!r} and no approved resolution rule was supplied "
            f"or the supplied rule declined to resolve this group; build "
            f"aborts per Data Validation §10.2"
        )


@dataclasses.dataclass(frozen=True)
class CollapsedGroup:
    """Lineage record for one identical-duplicate collapse (§10.1)."""

    canonical_key: tuple[object, ...]
    primary_source_row_id: str
    collapsed_source_row_ids: tuple[str, ...]  # every OTHER source_row_id in the group


@dataclasses.dataclass(frozen=True)
class ResolvedConflict:
    """Lineage record for one resolved conflicting-duplicate group (§10.2/§15.2)."""

    canonical_key: tuple[object, ...]
    winning_source_row_id: str
    discarded_source_row_ids: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class DuplicateResolutionResult:
    rows: tuple[S1Row, ...]  # exactly one row per canonical key, PK-unique
    collapsed_groups: tuple[CollapsedGroup, ...]
    resolved_conflicts: tuple[ResolvedConflict, ...]
    # source_row_id -> True if this row is the surviving row of a resolved
    # conflict (drives quality_has_source_conflict=False + DV_SOURCE_CONFLICT_RESOLVED)
    conflict_resolved_source_row_ids: frozenset[str]
    # source_row_id -> True if this row is the surviving row of an identical
    # collapse (drives DV_DUPLICATE_IDENTICAL_COLLAPSED)
    identical_collapse_primary_source_row_ids: frozenset[str]


def _values_identical(rows: Sequence[S1Row]) -> bool:
    first = rows[0]
    return all(
        all(getattr(row, field) == getattr(first, field) for field in _COMPARISON_FIELDS)
        for row in rows[1:]
    )


def resolve_duplicates(
    rows: Sequence[S1Row],
    *,
    multi_provider: bool = False,
    conflict_resolution_rule: Callable[[Sequence[S1Row]], S1Row | None] | None = None,
) -> DuplicateResolutionResult:
    """Group `rows` by canonical key and resolve any duplicates.

    `conflict_resolution_rule`, if given, receives the full list of
    conflicting rows for one canonical key and must return the winning
    `S1Row` (which must be one of the input rows), or `None` to decline
    (treated identically to no rule being supplied for that group — the
    whole build aborts, per §10.2). No default resolution rule is invented:
    §10.2 requires it to be "separat genehmigt", which this implementation
    cannot supply on its own.
    """
    groups: dict[tuple[object, ...], list[S1Row]] = {}
    order: list[tuple[object, ...]] = []
    for row in rows:
        key = row.canonical_key(multi_provider=multi_provider)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(row)

    result_rows: list[S1Row] = []
    collapsed_groups: list[CollapsedGroup] = []
    resolved_conflicts: list[ResolvedConflict] = []
    conflict_resolved_ids: set[str] = set()
    collapse_primary_ids: set[str] = set()

    for key in order:
        group = groups[key]
        if len(group) == 1:
            result_rows.append(group[0])
            continue

        if _values_identical(group):
            primary = min(group, key=lambda r: r.source_row_id)
            others = tuple(
                r.source_row_id for r in group if r.source_row_id != primary.source_row_id
            )
            collapsed_groups.append(
                CollapsedGroup(
                    canonical_key=key,
                    primary_source_row_id=primary.source_row_id,
                    collapsed_source_row_ids=others,
                )
            )
            collapse_primary_ids.add(primary.source_row_id)
            result_rows.append(primary)
            continue

        # Conflicting duplicates (§10.2): CRITICAL; requires an approved
        # deterministic resolution rule, or the build aborts.
        winner: S1Row | None = None
        if conflict_resolution_rule is not None:
            winner = conflict_resolution_rule(group)
        if winner is None:
            raise ConflictingDuplicatesWithoutResolutionRuleError(key, group)
        if winner not in group:
            raise ValueError(
                "conflict_resolution_rule must return one of the rows it was "
                "given, or None to decline"
            )
        discarded = tuple(
            r.source_row_id for r in group if r.source_row_id != winner.source_row_id
        )
        resolved_conflicts.append(
            ResolvedConflict(
                canonical_key=key,
                winning_source_row_id=winner.source_row_id,
                discarded_source_row_ids=discarded,
            )
        )
        conflict_resolved_ids.add(winner.source_row_id)
        result_rows.append(winner)

    return DuplicateResolutionResult(
        rows=tuple(result_rows),
        collapsed_groups=tuple(collapsed_groups),
        resolved_conflicts=tuple(resolved_conflicts),
        conflict_resolved_source_row_ids=frozenset(conflict_resolved_ids),
        identical_collapse_primary_source_row_ids=frozenset(collapse_primary_ids),
    )
