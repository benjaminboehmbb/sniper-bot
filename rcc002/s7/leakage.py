"""Fail-closed S7 leakage guards for downstream non-label views."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from rcc002.s7.constants import S7_FIELD_REGISTRY


S7_PREFIXES = ("fwd_", "label_", "barrier_")


def assert_no_s7_fields(
    field_names: Iterable[str],
    *,
    field_owners: Mapping[str, str],
    positive_allowlist: frozenset[str],
) -> None:
    """Reject S7, prefixed, ownerless, unknown, or non-allowlisted fields."""

    for field_name in field_names:
        if not isinstance(field_name, str) or not field_name:
            raise ValueError("view fields must be non-empty strings")
        owner = field_owners.get(field_name)
        if owner is None:
            raise ValueError(f"field has no registered owner: {field_name}")
        if (
            field_name in S7_FIELD_REGISTRY
            or owner == "S7_LABELS"
            or field_name.startswith(S7_PREFIXES)
        ):
            raise ValueError(
                f"S7 field is forbidden in this view: {field_name}"
            )
        if field_name not in positive_allowlist:
            raise ValueError(
                f"field is absent from the positive allowlist: {field_name}"
            )


__all__ = ["S7_PREFIXES", "assert_no_s7_fields"]
