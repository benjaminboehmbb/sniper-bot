"""Exact S8 view projection: S7Row -> one flat, allowlisted row dict.

Two independent gates run for every requested field, matching Data
Pipeline Specification SS7.9/SS8.7 ("Praefixpruefungen ergaenzen die
Eigentums- und Leakage-Pruefung, ersetzen sie aber nicht"):

1. stage/leakage-based: the field must resolve in the certified field
   registry, and (for the four non-label views) its owner stage must not
   be ``S7_LABELS``;
2. prefix-based: for the four non-label views, the field name itself must
   not start with ``fwd_``, ``label_`` or ``barrier_``.

Either violation alone is fail-closed rejection of the *entire* view
(never a partial/row-level repair).
"""

from __future__ import annotations

import enum

from rcc002.s3.constants import INDICATOR_FIELD_ALLOWLIST
from rcc002.s4.constants import SIGNAL_BASE_FIELDS
from rcc002.s7.schema import S7Row, flatten_s7_extension
from rcc002.constants import ViewId
from rcc002.s8.field_registry import FIELD_OWNER_STAGE, resolve_field
from rcc002.s8.reason_codes import ViewProjectionError
from rcc002.s8.views import (
    PROHIBITED_NON_LABEL_PREFIXES,
    VIEW_DEFINITIONS,
    view_forbids_field_owner_stage,
)

_LABEL_STAGE = "S7_LABELS"
_GROUPED_ATTRS = ("indicators", "signals", "horizons")


def _normalize_scalar(value: object) -> object:
    if isinstance(value, enum.Enum):
        return value.value
    return value


def flatten_row(row: S7Row) -> dict[str, object]:
    """Expand one canonical S7Row to every field name it can supply.

    This includes fields outside every view's allowlist (for example the
    S1/S2-internal ``source_file_ordinal``/``original_record_index``
    bookkeeping fields); :func:`project_view` is solely responsible for
    restricting the output to a specific view's exact allowlist.
    """
    if not isinstance(row, S7Row):
        raise ViewProjectionError("row must be a canonical S7Row")

    flat: dict[str, object] = {}
    for field in row.__dataclass_fields__:
        if field in _GROUPED_ATTRS:
            continue
        flat[field] = _normalize_scalar(getattr(row, field))

    for name in INDICATOR_FIELD_ALLOWLIST:
        indicator = row.indicators[name]
        flat[name] = _normalize_scalar(indicator.value)
        flat[f"{name}_valid"] = indicator.valid
        flat[f"{name}_warmup_complete"] = indicator.warmup_complete
        flat[f"{name}_reason_codes"] = indicator.reason_codes

    for name in SIGNAL_BASE_FIELDS:
        signal = row.signals[name]
        flat[name] = _normalize_scalar(signal.value)
        flat[f"{name}_valid"] = signal.valid
        flat[f"{name}_reason_codes"] = signal.reason_codes

    for name, value in flatten_s7_extension(row).items():
        flat[name] = _normalize_scalar(value)

    return flat


def _reject_field_for_view(view_id: ViewId, field: str) -> None:
    owner_stage, _leakage_class = resolve_field(field)
    definition = VIEW_DEFINITIONS[view_id]

    if view_forbids_field_owner_stage(view_id, owner_stage):
        raise ViewProjectionError(
            f"{view_id.value}: field {field!r} is owned by {owner_stage} "
            f"and forbidden in a non-label view"
        )
    if not definition.s7_allowed and field.startswith(PROHIBITED_NON_LABEL_PREFIXES):
        raise ViewProjectionError(
            f"{view_id.value}: field {field!r} has a prohibited prefix "
            f"for a non-label view"
        )


def project_view(
    view_id: ViewId,
    row: S7Row,
    *,
    flattened: dict[str, object] | None = None,
) -> dict[str, object]:
    """Project one row onto exactly ``view_id``'s certified field list.

    Raises :class:`ViewProjectionError` fail-closed for any unknown field,
    any field without a unique registry owner, any field forbidden for
    this view by owner stage, or any field with a prohibited prefix for a
    non-label view. ``flattened`` lets callers amortize repeated
    :func:`flatten_row` calls across the six views of the same row.
    """
    if view_id not in VIEW_DEFINITIONS:
        raise ViewProjectionError(f"unregistered view: {view_id!r}")
    definition = VIEW_DEFINITIONS[view_id]
    flat = flatten_row(row) if flattened is None else flattened

    projected: dict[str, object] = {}
    for field in definition.fields:
        if field not in FIELD_OWNER_STAGE:
            raise ViewProjectionError(f"unregistered field: {field!r}")
        _reject_field_for_view(view_id, field)
        if field not in flat:
            raise ViewProjectionError(
                f"{view_id.value}: row does not supply registered field "
                f"{field!r}"
            )
        projected[field] = flat[field]

    if tuple(projected) != definition.fields:
        raise ViewProjectionError(
            f"{view_id.value}: projected field order diverged from the "
            f"certified allowlist order"
        )
    return projected


def project_rows(
    view_id: ViewId,
    rows: "list[S7Row] | tuple[S7Row, ...]",
) -> list[dict[str, object]]:
    """Project every row onto ``view_id``, preserving input row order."""
    return [project_view(view_id, row) for row in rows]


__all__ = [
    "flatten_row",
    "project_rows",
    "project_view",
]
