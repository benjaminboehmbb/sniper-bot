"""Registered S0 Source Manifest 1.0.0 and historical alias compatibility."""

from __future__ import annotations

import dataclasses
import re
from datetime import datetime

from rcc002.s0.profiles import (
    COLUMN_PROFILE_ID,
    SOURCE_RETRIEVAL_PROFILE_ID,
    SOURCE_RETRIEVAL_PROFILE_VERSION,
    TIMESTAMP_UNIT_PROFILE_ID,
    SourceProfileError,
)
from rcc002.s0.source_identity import (
    DATASET_KIND,
    MARKET_TYPE,
    PROVIDER,
    SOURCE_ROW_ID_PROFILE_ID,
    SOURCE_ROW_ID_PROFILE_VERSION,
    SourceFileIdentity,
    SourceSnapshot,
    build_source_snapshot,
)

_SHA256_HEX_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_ID_PATTERN = re.compile(r"^manifest:sha256:[0-9a-f]{64}$")
_SOURCE_SNAPSHOT_ID_PATTERN = re.compile(
    r"^source:sha256:[0-9a-f]{64}$"
)

SOURCE_MANIFEST_SCHEMA_ID = "rcc002.source-manifest"
SOURCE_MANIFEST_SCHEMA_VERSION = "1.0.0"
SOURCE_MANIFEST_SCHEMA_REF = "rcc002.source-manifest/1.0.0"
SOURCE_MANIFEST_TYPE = "source"
PROJECT = "RCC-002"

# One-directional legacy alias migration (Data Pipeline §7.1 / Data
# Validation §5.1): "Die umgekehrte Abbildung ist unzulässig." Versioned per
# the specification's own requirement that legacy-alias acceptance occur
# "durch ein versioniertes Migrationsprofil".
LEGACY_ALIAS_MIGRATION_PROFILE_ID = "RCC002_S0_LEGACY_ALIAS_MIGRATION_V1"

LEGACY_ALIAS_MAP: dict[str, str] = {
    "source_provider": "provider",
    "source_retrieved_at_utc": "retrieved_at_utc",
}


def validate_legacy_provider(provider: object) -> None:
    """Reject the registered provider on the generic legacy ingestion path."""
    if (
        isinstance(provider, str)
        and provider.casefold() == PROVIDER.casefold()
    ):
        raise SourceProfileError(
            "RCC_SOURCE_REGISTERED_PROVIDER_LEGACY_PATH_FORBIDDEN",
            "BINANCE_VISION sources must use the registered archive scan, "
            "Source Snapshot V1, and Source Manifest 1.0.0 path",
        )


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
class LegacySourceManifest:
    """Historical generic one-file manifest; read-only compatibility only."""

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
        validate_legacy_provider(self.provider)

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


def _validate_utc_timestamp(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError(f"{name} must be a canonical UTC timestamp")
    try:
        datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid UTC timestamp") from exc


@dataclasses.dataclass(frozen=True, slots=True)
class ManifestProducer:
    component: str
    version: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.component, str)
            or not self.component
            or not isinstance(self.version, str)
            or not self.version
        ):
            raise ValueError("producer component and version are required")

    def as_dict(self) -> dict[str, str]:
        return {
            "component": self.component,
            "version": self.version,
        }


@dataclasses.dataclass(frozen=True, slots=True)
class ActualCoverage:
    min_open_time_utc_ms: int
    max_close_time_utc_ms: int
    record_count: int

    def __post_init__(self) -> None:
        for name in (
            "min_open_time_utc_ms",
            "max_close_time_utc_ms",
            "record_count",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
        if self.record_count <= 0:
            raise ValueError("record_count must be positive")
        if self.min_open_time_utc_ms > self.max_close_time_utc_ms:
            raise ValueError("actual coverage minimum exceeds maximum")

    def as_dict(self) -> dict[str, int]:
        return {
            "min_open_time_utc_ms": self.min_open_time_utc_ms,
            "max_close_time_utc_ms": self.max_close_time_utc_ms,
            "record_count": self.record_count,
        }


@dataclasses.dataclass(frozen=True, slots=True)
class CoverageReconciliation:
    status: str
    exceptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in {
            "PASS",
            "PASS_WITH_REGISTERED_EXCEPTIONS",
            "FAIL",
        }:
            raise ValueError("unregistered coverage reconciliation status")
        if not isinstance(self.exceptions, tuple):
            raise ValueError("coverage exceptions must be an ordered tuple")
        if any(not isinstance(item, str) or not item for item in self.exceptions):
            raise ValueError("coverage exceptions must be non-empty strings")
        if self.status == "PASS" and self.exceptions:
            raise ValueError("PASS reconciliation cannot contain exceptions")
        if (
            self.status == "PASS_WITH_REGISTERED_EXCEPTIONS"
            and not self.exceptions
        ):
            raise ValueError(
                "registered-exception status requires an exception"
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "exceptions": list(self.exceptions),
        }


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class SourceManifest:
    """Canonical registered multi-file Source Manifest 1.0.0."""

    manifest_id: str
    created_at_utc: str
    producer: ManifestProducer
    status: str
    source_snapshot_id: str
    source_snapshot_preimage_sha256: str
    symbol: str
    source_revision: str | None
    retrieved_at_utc: str
    source_files: tuple[SourceFileIdentity, ...]
    actual_coverage: ActualCoverage
    coverage_reconciliation: CoverageReconciliation
    license_or_terms_ref: str | None = None
    manifest_schema_id: str = SOURCE_MANIFEST_SCHEMA_ID
    manifest_schema_version: str = SOURCE_MANIFEST_SCHEMA_VERSION
    manifest_schema_ref: str = SOURCE_MANIFEST_SCHEMA_REF
    manifest_type: str = SOURCE_MANIFEST_TYPE
    project: str = PROJECT
    source_retrieval_profile_id: str = SOURCE_RETRIEVAL_PROFILE_ID
    source_retrieval_profile_version: str = (
        SOURCE_RETRIEVAL_PROFILE_VERSION
    )
    source_row_id_profile_id: str = SOURCE_ROW_ID_PROFILE_ID
    source_row_id_profile_version: str = SOURCE_ROW_ID_PROFILE_VERSION
    provider: str = PROVIDER
    market_type: str = MARKET_TYPE
    dataset_kind: str = DATASET_KIND
    interval: str = "1m"
    column_profile_id: str = COLUMN_PROFILE_ID
    timestamp_unit_profile_id: str = TIMESTAMP_UNIT_PROFILE_ID

    def __post_init__(self) -> None:
        expected_constants = {
            "manifest_schema_id": SOURCE_MANIFEST_SCHEMA_ID,
            "manifest_schema_version": SOURCE_MANIFEST_SCHEMA_VERSION,
            "manifest_schema_ref": SOURCE_MANIFEST_SCHEMA_REF,
            "manifest_type": SOURCE_MANIFEST_TYPE,
            "project": PROJECT,
            "source_retrieval_profile_id": SOURCE_RETRIEVAL_PROFILE_ID,
            "source_retrieval_profile_version": (
                SOURCE_RETRIEVAL_PROFILE_VERSION
            ),
            "source_row_id_profile_id": SOURCE_ROW_ID_PROFILE_ID,
            "source_row_id_profile_version": SOURCE_ROW_ID_PROFILE_VERSION,
            "provider": PROVIDER,
            "market_type": MARKET_TYPE,
            "dataset_kind": DATASET_KIND,
            "interval": "1m",
            "column_profile_id": COLUMN_PROFILE_ID,
            "timestamp_unit_profile_id": TIMESTAMP_UNIT_PROFILE_ID,
        }
        for name, expected in expected_constants.items():
            if getattr(self, name) != expected:
                raise ValueError(f"{name} must equal {expected!r}")
        if self.status not in {
            "candidate",
            "published",
            "superseded",
            "withdrawn",
        }:
            raise ValueError("unregistered Source Manifest status")
        if not _MANIFEST_ID_PATTERN.fullmatch(self.manifest_id):
            raise ValueError("manifest_id is not canonical")
        if not _SOURCE_SNAPSHOT_ID_PATTERN.fullmatch(
            self.source_snapshot_id
        ):
            raise ValueError("source_snapshot_id is not canonical")
        if not _SHA256_HEX_PATTERN.fullmatch(
            self.source_snapshot_preimage_sha256
        ):
            raise ValueError(
                "source_snapshot_preimage_sha256 is not canonical"
            )
        if not isinstance(self.source_files, tuple) or not self.source_files:
            raise ValueError("source_files must be a non-empty ordered tuple")
        if self.source_revision is not None and (
            not isinstance(self.source_revision, str)
            or not self.source_revision
        ):
            raise ValueError("source_revision must be null or non-empty")
        if self.license_or_terms_ref is not None and (
            not isinstance(self.license_or_terms_ref, str)
            or not self.license_or_terms_ref
        ):
            raise ValueError(
                "license_or_terms_ref must be null or non-empty"
            )
        _validate_utc_timestamp("created_at_utc", self.created_at_utc)
        _validate_utc_timestamp("retrieved_at_utc", self.retrieved_at_utc)

        snapshot = build_source_snapshot(
            self.source_files,
            source_revision=self.source_revision,
        )
        if self.source_files != snapshot.source_files:
            raise SourceProfileError(
                "RCC_SOURCE_FILE_ORDER_MISMATCH",
                "source_files must equal the canonical ordered source "
                "snapshot file array",
            )
        expected_identity = (
            snapshot.source_snapshot_id,
            snapshot.preimage_sha256,
            snapshot.symbol,
            snapshot.interval,
            snapshot.actual_coverage_min_open_time_utc_ms,
            snapshot.actual_coverage_max_close_time_utc_ms,
            snapshot.source_record_count,
        )
        actual_identity = (
            self.source_snapshot_id,
            self.source_snapshot_preimage_sha256,
            self.symbol,
            self.interval,
            self.actual_coverage.min_open_time_utc_ms,
            self.actual_coverage.max_close_time_utc_ms,
            self.actual_coverage.record_count,
        )
        if actual_identity != expected_identity:
            raise ValueError(
                "Source Manifest identity or coverage contradicts source files"
            )

    @classmethod
    def from_snapshot(
        cls,
        snapshot: SourceSnapshot,
        *,
        manifest_id: str,
        created_at_utc: str,
        producer: ManifestProducer,
        status: str,
        retrieved_at_utc: str,
        coverage_reconciliation: CoverageReconciliation,
        license_or_terms_ref: str | None = None,
    ) -> SourceManifest:
        return cls(
            manifest_id=manifest_id,
            created_at_utc=created_at_utc,
            producer=producer,
            status=status,
            source_snapshot_id=snapshot.source_snapshot_id,
            source_snapshot_preimage_sha256=snapshot.preimage_sha256,
            symbol=snapshot.symbol,
            source_revision=snapshot.source_revision,
            retrieved_at_utc=retrieved_at_utc,
            source_files=snapshot.source_files,
            actual_coverage=ActualCoverage(
                min_open_time_utc_ms=(
                    snapshot.actual_coverage_min_open_time_utc_ms
                ),
                max_close_time_utc_ms=(
                    snapshot.actual_coverage_max_close_time_utc_ms
                ),
                record_count=snapshot.source_record_count,
            ),
            coverage_reconciliation=coverage_reconciliation,
            license_or_terms_ref=license_or_terms_ref,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "manifest_schema_id": self.manifest_schema_id,
            "manifest_schema_version": self.manifest_schema_version,
            "manifest_schema_ref": self.manifest_schema_ref,
            "manifest_type": self.manifest_type,
            "manifest_id": self.manifest_id,
            "created_at_utc": self.created_at_utc,
            "producer": self.producer.as_dict(),
            "project": self.project,
            "status": self.status,
            "source_snapshot_id": self.source_snapshot_id,
            "source_snapshot_preimage_sha256": (
                self.source_snapshot_preimage_sha256
            ),
            "source_retrieval_profile_id": (
                self.source_retrieval_profile_id
            ),
            "source_retrieval_profile_version": (
                self.source_retrieval_profile_version
            ),
            "source_row_id_profile_id": self.source_row_id_profile_id,
            "source_row_id_profile_version": (
                self.source_row_id_profile_version
            ),
            "provider": self.provider,
            "market_type": self.market_type,
            "dataset_kind": self.dataset_kind,
            "symbol": self.symbol,
            "interval": self.interval,
            "column_profile_id": self.column_profile_id,
            "timestamp_unit_profile_id": self.timestamp_unit_profile_id,
            "source_revision": self.source_revision,
            "retrieved_at_utc": self.retrieved_at_utc,
            "source_files": [
                item.as_preimage() for item in self.source_files
            ],
            "actual_coverage": self.actual_coverage.as_dict(),
            "coverage_reconciliation": (
                self.coverage_reconciliation.as_dict()
            ),
            "license_or_terms_ref": self.license_or_terms_ref,
        }


__all__ = [
    "ActualCoverage",
    "ConflictingLegacyAliasError",
    "CoverageReconciliation",
    "LEGACY_ALIAS_MAP",
    "LEGACY_ALIAS_MIGRATION_PROFILE_ID",
    "LegacySourceManifest",
    "ManifestProducer",
    "SourceManifest",
    "migrate_legacy_aliases",
    "validate_legacy_provider",
]
