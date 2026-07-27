"""The S0 source_manifest field contract and legacy alias migration.

Field contract transcribed verbatim from:
- RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md §7.1 (S0_SOURCE –
  Rohdatenaufnahme), the source_manifest field table;
- RCC_002_DATA_VALIDATION_2026-07-23.md §5.1 (Mindestmetadaten je Quelle),
  which restates the identical field contract.

Both documents agree the source_manifest has exactly twelve fields, and that
`provider`/`retrieved_at_utc` are the only canonical names for two fields
that also have a one-directional legacy alias mapping.

NOT included here: the three `semantic_build_configuration.source_expectations`
fields (`timezone`, `expected_start`, `expected_end`) — both documents state
explicitly these "sind keine S0-Zeilenfelder und keine Source-Manifest-Felder"
(Data Pipeline §7.1) and belong to a separate normative object owned by the
Reproducibility specification, not to source_manifest.

Deferred (not implemented in this module): deterministic computation of
`source_snapshot_id`. See rcc002/s0/ingest.py module docstring for the two
specific specification gaps that block this, reported rather than assumed.
"""

from __future__ import annotations

import dataclasses
import re

_SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# One-directional legacy alias migration (Data Pipeline §7.1 / Data
# Validation §5.1): "Die umgekehrte Abbildung ist unzulässig." Versioned per
# the specification's own requirement that legacy-alias acceptance occur
# "durch ein versioniertes Migrationsprofil".
LEGACY_ALIAS_MIGRATION_PROFILE_ID = "RCC002_S0_LEGACY_ALIAS_MIGRATION_V1"

LEGACY_ALIAS_MAP: dict[str, str] = {
    "source_provider": "provider",
    "source_retrieved_at_utc": "retrieved_at_utc",
}


class ConflictingLegacyAliasError(ValueError):
    """Raised when both a legacy alias and its canonical field are present.

    Neither Data Pipeline §7.1 nor Data Validation §5.1 defines a precedence
    rule for this case. Per this specification family's uniform fail-closed
    principle (applied consistently at every stage boundary reviewed under
    AIR-004), ambiguous input is rejected rather than silently resolved by
    an unstated preference.
    """


def migrate_legacy_aliases(raw: dict[str, object]) -> dict[str, object]:
    """Migrate legacy source-manifest field aliases to their canonical names.

    Per Data Pipeline §7.1: "Legacy-Aliasse dürfen nur vor Erzeugung des
    kanonischen `source_manifest` durch ein versioniertes Migrationsprofil
    akzeptiert werden und erscheinen weder im kanonischen Source Manifest
    noch im S1-Ausgang." This function performs exactly that migration and
    never leaves a legacy-named key in its output.
    """
    result = dict(raw)
    for legacy_key, canonical_key in LEGACY_ALIAS_MAP.items():
        if legacy_key in result:
            if canonical_key in result:
                raise ConflictingLegacyAliasError(
                    f"both legacy alias {legacy_key!r} and canonical field "
                    f"{canonical_key!r} are present; the specification "
                    f"defines no precedence rule for this case"
                )
            result[canonical_key] = result.pop(legacy_key)
    return result


@dataclasses.dataclass(frozen=True)
class SourceManifest:
    """The S0 source_manifest, per Data Pipeline §7.1 / Data Validation §5.1.

    `source_snapshot_id` is accepted as supplied by the caller. This module
    does not compute it; see rcc002/s0/ingest.py for why that computation is
    currently deferred rather than implemented.
    """

    source_snapshot_id: str
    provider: str
    market_type: str
    symbol: str
    interval: str
    retrieved_at_utc: int  # UTC timestamp in milliseconds
    source_file_name: str
    source_byte_sha256: str
    source_format: str
    source_location: str
    source_revision: str | None = None
    license_or_terms_ref: str | None = None

    def __post_init__(self) -> None:
        # Nullability exactly as specified: only source_revision and
        # license_or_terms_ref may be null (Data Pipeline §7.1 "Nullbar"
        # column); every other field is "Nullbar: Nein".
        required_fields = (
            "source_snapshot_id",
            "provider",
            "market_type",
            "symbol",
            "interval",
            "retrieved_at_utc",
            "source_file_name",
            "source_byte_sha256",
            "source_format",
            "source_location",
        )
        for field_name in required_fields:
            value = getattr(self, field_name)
            if value is None or (isinstance(value, str) and value == ""):
                raise ValueError(
                    f"{field_name!r} is a required (non-nullable) "
                    f"source_manifest field per Data Pipeline §7.1"
                )

        # "64-stelliger Lowercase-Hex-String" (Data Pipeline §7.1).
        if not _SHA256_HEX_PATTERN.match(self.source_byte_sha256):
            raise ValueError(
                "source_byte_sha256 must be a 64-character lowercase hex "
                "string, per Data Pipeline §7.1"
            )

        if not isinstance(self.retrieved_at_utc, int) or isinstance(
            self.retrieved_at_utc, bool
        ):
            raise ValueError(
                "retrieved_at_utc must be an integer UTC timestamp in "
                "milliseconds, per Data Pipeline §7.1"
            )
