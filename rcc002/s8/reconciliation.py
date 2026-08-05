"""S7 -> S8 row, key, order, value and count reconciliation.

Enforces Data Pipeline Specification SS7.9.3.1 / Reproducibility and
Manifest Specification SS8.7.1: for every successful view artifact,
``S8_rows == S7_rows`` with exact canonical primary-key preservation, exact
row identity preservation, and exact row order preservation. No row may be
removed, merged, duplicated, reordered, or modified; the only permitted
response to a violation is whole-artifact rejection, never a per-row
repair.

The primary key used for reconciliation is derived from the evaluated
view/schema definition (Data Pipeline Specification SS7.3/SS7.9.5), never
assumed: :func:`primary_key_fields_for_view` reads it from
``rcc002.s8.views.VIEW_DEFINITIONS``, and :func:`resolve_primary_key_fields`
validates it fail-closed before use.
"""

from __future__ import annotations

from collections.abc import Sequence

from rcc002.constants import ViewId
from rcc002.s7.schema import S7Row
from rcc002.s8.projection import project_view
from rcc002.s8.reason_codes import RowReconciliationError
from rcc002.s8.views import VIEW_DEFINITIONS

# Canonical primary key (Data Pipeline Specification SS7.3): a consolidated,
# single-provider-scope dataset uses (market_type, symbol, interval,
# open_time); a not-yet-consolidated, multi-provider dataset additionally
# requires `provider`, immediately preceding `market_type`. Which of the two
# applies is a property of the evaluated schema (see
# `resolve_primary_key_fields`), never a fixed assumption.
CONSOLIDATED_PRIMARY_KEY_FIELDS: tuple[str, ...] = (
    "market_type",
    "symbol",
    "interval",
    "open_time",
)
PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS: tuple[str, ...] = (
    "provider",
    "market_type",
    "symbol",
    "interval",
    "open_time",
)
_KNOWN_PRIMARY_KEY_FIELDS = frozenset(PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS)

# Backward-compatible default for callers that do not name a specific view:
# every currently registered S8 view is consolidated, single-provider scope
# (SS7.9.5 `primary_key_fields`).
PRIMARY_KEY_FIELDS: tuple[str, ...] = CONSOLIDATED_PRIMARY_KEY_FIELDS


def resolve_primary_key_fields(
    schema_primary_key_fields: Sequence[str],
) -> tuple[str, ...]:
    """Validate a schema-declared ``primary_key_fields`` sequence and return
    it as the normative, ordered primary key.

    Data Pipeline Specification SS7.3: the canonical primary key is
    ``(market_type, symbol, interval, open_time)``; a schema whose scope is
    not yet consolidated across providers additionally requires
    ``provider``, immediately preceding ``market_type``. Raises
    :class:`RowReconciliationError` fail-closed for an empty, duplicate,
    unknown-field, or misordered definition -- no other primary-key shape is
    normative.
    """
    fields = tuple(schema_primary_key_fields)
    if not fields:
        raise RowReconciliationError("primary key definition must not be empty")
    if len(set(fields)) != len(fields):
        raise RowReconciliationError(
            f"primary key definition contains duplicate fields: {fields}"
        )
    unknown = sorted(set(fields) - _KNOWN_PRIMARY_KEY_FIELDS)
    if unknown:
        raise RowReconciliationError(
            f"primary key definition contains unknown fields: {unknown}"
        )
    expected = (
        PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS
        if "provider" in fields
        else CONSOLIDATED_PRIMARY_KEY_FIELDS
    )
    if fields != expected:
        raise RowReconciliationError(
            "primary key definition is not in the normative order: "
            f"expected {expected}, got {fields}"
        )
    return fields


def primary_key_fields_for_view(view_id: ViewId) -> tuple[str, ...]:
    """The evaluated view's normative primary key (Data Pipeline
    Specification SS7.9.5 ``primary_key_fields``), fail-closed validated by
    :func:`resolve_primary_key_fields`."""
    return resolve_primary_key_fields(VIEW_DEFINITIONS[view_id].primary_key_fields)


def row_identity_key(
    row: S7Row, primary_key_fields: Sequence[str] = PRIMARY_KEY_FIELDS
) -> tuple[object, ...]:
    if not isinstance(row, S7Row):
        raise RowReconciliationError("row must be a canonical S7Row")
    return tuple(getattr(row, name) for name in primary_key_fields)


def _describe_keys(keys: Sequence[tuple[object, ...]], limit: int = 3) -> str:
    shown = ", ".join(repr(key) for key in keys[:limit])
    suffix = ", ..." if len(keys) > limit else ""
    return f"[{shown}{suffix}]"


def reconcile_row_identity(
    s7_rows: Sequence[S7Row],
    s8_rows: Sequence[S7Row],
    primary_key_fields: Sequence[str] = PRIMARY_KEY_FIELDS,
) -> None:
    """Verify count, uniqueness, identity and order by primary key alone.

    ``primary_key_fields`` defaults to the certified consolidated,
    single-provider-scope key; pass a view-specific key (for example via
    :func:`primary_key_fields_for_view`) to reconcile against a
    provider-specific schema instead.

    Raises :class:`RowReconciliationError` fail-closed; never repairs.
    """
    s7_keys = [row_identity_key(row, primary_key_fields) for row in s7_rows]
    s8_keys = [row_identity_key(row, primary_key_fields) for row in s8_rows]

    if len(set(s7_keys)) != len(s7_keys):
        raise RowReconciliationError(
            "S7 input contains duplicate canonical primary keys"
        )
    if len(s8_keys) != len(set(s8_keys)):
        raise RowReconciliationError(
            "S8 output contains duplicate canonical primary keys"
        )
    if len(s8_rows) != len(s7_rows):
        raise RowReconciliationError(
            f"S8_rows ({len(s8_rows)}) != S7_rows ({len(s7_rows)})"
        )

    s7_key_set = set(s7_keys)
    s8_key_set = set(s8_keys)
    missing = [key for key in s7_keys if key not in s8_key_set]
    if missing:
        raise RowReconciliationError(
            f"S8 output is missing S7 rows: {_describe_keys(missing)}"
        )
    extra = [key for key in s8_keys if key not in s7_key_set]
    if extra:
        raise RowReconciliationError(
            f"S8 output contains rows absent from S7: {_describe_keys(extra)}"
        )
    # Equal length, equal sets, no duplicates on either side: any residual
    # difference in the ordered list is exactly a reordering.
    if s8_keys != s7_keys:
        raise RowReconciliationError(
            "S8 output row order diverges from the S7 input order"
        )


def reconcile_view_artifact(
    view_id: ViewId,
    s7_rows: Sequence[S7Row],
    artifact_rows: Sequence[dict[str, object]],
) -> None:
    """Verify a materialized view artifact against a fresh re-projection.

    This is the complete row-preservation oracle: it independently
    re-derives the expected artifact from ``s7_rows`` via
    :func:`rcc002.s8.projection.project_view` and requires exact list
    equality, which subsumes row count, canonical-key identity, row order,
    and per-field value preservation in one comparison. Any missing,
    duplicated, merged, reordered, or modified row fails closed here.

    The primary key is derived from ``view_id``'s schema definition (see
    :func:`primary_key_fields_for_view`), not assumed.
    """
    primary_key_fields = primary_key_fields_for_view(view_id)
    reconcile_row_identity(
        s7_rows, s7_rows, primary_key_fields
    )  # rejects a malformed S7 input
    if len(artifact_rows) != len(s7_rows):
        raise RowReconciliationError(
            f"S8_rows ({len(artifact_rows)}) != S7_rows ({len(s7_rows)})"
        )
    expected_rows = [project_view(view_id, row) for row in s7_rows]
    for index, (expected, actual) in enumerate(zip(expected_rows, artifact_rows)):
        if not isinstance(actual, dict):
            raise RowReconciliationError(
                f"artifact row {index} is not a projected row mapping"
            )
        if actual != expected:
            raise RowReconciliationError(
                f"artifact row {index} diverges from its S7 re-projection "
                f"(modified, merged, or corrupted row)"
            )


__all__ = [
    "CONSOLIDATED_PRIMARY_KEY_FIELDS",
    "PRIMARY_KEY_FIELDS",
    "PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS",
    "primary_key_fields_for_view",
    "reconcile_row_identity",
    "reconcile_view_artifact",
    "resolve_primary_key_fields",
    "row_identity_key",
]
