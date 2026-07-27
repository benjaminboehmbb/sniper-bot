"""The canonical S1 row schema and its legacy alias migration.

Field contract transcribed verbatim from
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md §7.2 ("Der kanonische
S1-Zeilenvertrag enthält mindestens") and cross-confirmed identical in
RCC_002_DATA_VALIDATION_2026-07-23.md §7.1. Every field is non-nullable
("Nein" in both documents' tables) — unlike the S0 source_manifest, S1's
row contract has no nullable field.
"""

from __future__ import annotations

import dataclasses

# Canonical primary key (Data Pipeline §7.2 / Data Validation §8.2). If
# multiple providers occur within a not-yet-consolidated dataset, `provider`
# joins the key immediately before `market_type` (both documents agree on
# this ordering).
CANONICAL_PRIMARY_KEY_SINGLE_PROVIDER: tuple[str, ...] = (
    "market_type",
    "symbol",
    "interval",
    "open_time",
)
CANONICAL_PRIMARY_KEY_MULTI_PROVIDER: tuple[str, ...] = (
    "provider",
    "market_type",
    "symbol",
    "interval",
    "open_time",
)

# `source_id` is not a canonical field name (Data Pipeline §7.2: "`source_id`
# ist kein kanonischer Feldname. Historische Eingaben müssen ihn über eine
# versionierte Migrationsabbildung in `source_snapshot_id` überführen.").
S1_LEGACY_ALIAS_MIGRATION_PROFILE_ID = "RCC002_S1_LEGACY_ALIAS_MIGRATION_V1"

S1_LEGACY_ALIAS_MAP: dict[str, str] = {
    "source_id": "source_snapshot_id",
}


class S1ConflictingLegacyAliasError(ValueError):
    """Raised when both a legacy alias and its canonical field are present.

    Same fail-closed reasoning as
    rcc002.s0.manifest.ConflictingLegacyAliasError: neither document defines
    a precedence rule for this case, and this specification family's
    uniform fail-closed principle governs ambiguous input.
    """


def migrate_s1_legacy_aliases(raw: dict[str, object]) -> dict[str, object]:
    """Migrate S1 legacy field aliases to their canonical names."""
    result = dict(raw)
    for legacy_key, canonical_key in S1_LEGACY_ALIAS_MAP.items():
        if legacy_key in result:
            if canonical_key in result:
                raise S1ConflictingLegacyAliasError(
                    f"both legacy alias {legacy_key!r} and canonical field "
                    f"{canonical_key!r} are present; the specification "
                    f"defines no precedence rule for this case"
                )
            result[canonical_key] = result.pop(legacy_key)
    return result


@dataclasses.dataclass(frozen=True)
class S1Row:
    """One canonical S1_NORMALIZED row (Data Pipeline §7.2).

    All fields are required (non-nullable) per the specification's own
    S1 row-contract table.
    """

    source_snapshot_id: str
    source_row_id: str
    provider: str
    market_type: str
    symbol: str
    interval: str
    open_time: int  # UTC timestamp in milliseconds
    close_time: int  # UTC timestamp in milliseconds
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        required_string_fields = (
            "source_snapshot_id",
            "source_row_id",
            "provider",
            "market_type",
            "symbol",
            "interval",
        )
        for field_name in required_string_fields:
            value = getattr(self, field_name)
            if not value:
                raise ValueError(
                    f"{field_name!r} is a required (non-nullable) S1 row "
                    f"field per Data Pipeline §7.2"
                )
        for field_name in ("open_time", "close_time"):
            value = getattr(self, field_name)
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(
                    f"{field_name!r} must be an integer UTC timestamp in "
                    f"milliseconds, per Data Pipeline §7.2"
                )
        for field_name in ("open", "high", "low", "close", "volume"):
            value = getattr(self, field_name)
            if not isinstance(value, float):
                raise ValueError(
                    f"{field_name!r} must be a Float64 value, per Data "
                    f"Pipeline §7.2"
                )

    def canonical_key(self, *, multi_provider: bool) -> tuple[object, ...]:
        """The row's value tuple for the canonical primary key/sort order."""
        fields = (
            CANONICAL_PRIMARY_KEY_MULTI_PROVIDER
            if multi_provider
            else CANONICAL_PRIMARY_KEY_SINGLE_PROVIDER
        )
        return tuple(getattr(self, name) for name in fields)
