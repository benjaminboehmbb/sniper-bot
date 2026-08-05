"""Stage Manifest builder (Reproducibility and Manifest Specification
SS8.4)."""

from __future__ import annotations

import dataclasses

from rcc002.s8.manifests.common import build_common_envelope, finalize_and_validate
from rcc002.s8.reason_codes import ManifestValidationError

_MANIFEST_TYPE = "stage"
_SCHEMA_VERSION = "1.0.0"

_STAGE_IDS = frozenset(
    {
        "S0_SOURCE",
        "S1_NORMALIZED",
        "S2_VALIDATED",
        "S3_INDICATORS",
        "S4_SIGNALS",
        "S5_REGIMES",
        "S6_GATES",
        "S7_LABELS",
        "S8_EXPORT",
    }
)


@dataclasses.dataclass(frozen=True, slots=True)
class SchemaRecord:
    schema_id: str
    schema_version: str
    schema_fingerprint_sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "schema_ref": f"{self.schema_id}/{self.schema_version}",
            "schema_fingerprint_sha256": self.schema_fingerprint_sha256,
        }


@dataclasses.dataclass(frozen=True, slots=True)
class ArtifactReference:
    artifact_id: str
    relative_path: str
    byte_sha256: str

    def as_dict(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "relative_path": self.relative_path,
            "byte_sha256": self.byte_sha256,
        }


@dataclasses.dataclass(frozen=True, slots=True)
class VersionedReference:
    id: str
    version: str
    sha256: str

    def as_dict(self) -> dict[str, object]:
        return {"id": self.id, "version": self.version, "sha256": self.sha256}


@dataclasses.dataclass(frozen=True, slots=True)
class ReconciliationResult:
    input_rows: int
    output_rows: int
    primary_key_verified: bool
    row_order_verified: bool
    segment_reconciliation_status: str
    validity_reconciliation_status: str

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True, slots=True)
class ValidationResult:
    status: str
    tests_passed: int
    tests_failed: int

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


def build_stage_manifest(
    *,
    stage_id: str,
    stage_version: str,
    component: "tuple[str, str]",
    build_id: str,
    run_id: str,
    input_schema: "SchemaRecord | None",
    output_schema: SchemaRecord,
    parents: "list[ArtifactReference]",
    outputs: "list[ArtifactReference]",
    semantic_build_configuration_sha256: str,
    physical_publication_configuration_sha256: "str | None",
    specification_profile: "list[VersionedReference]",
    registries: "list[VersionedReference]",
    reconciliation: ReconciliationResult,
    validation: ValidationResult,
    warnings: "list[str]",
    failures: "list[str]",
    publication_status: str,
    created_at_utc: str,
    producer_component: str,
    producer_version: str,
    status: str = "candidate",
) -> dict[str, object]:
    if stage_id not in _STAGE_IDS:
        raise ManifestValidationError(f"unknown stage_id: {stage_id!r}")
    if not outputs:
        raise ManifestValidationError("a stage manifest requires at least one output")
    if not specification_profile:
        raise ManifestValidationError(
            "a stage manifest requires a non-empty specification profile"
        )

    manifest = build_common_envelope(
        manifest_type=_MANIFEST_TYPE,
        manifest_schema_version=_SCHEMA_VERSION,
        status=status,
        producer_component=producer_component,
        producer_version=producer_version,
        created_at_utc=created_at_utc,
    )
    manifest.update(
        {
            "stage_id": stage_id,
            "stage_version": stage_version,
            "component": {"component": component[0], "version": component[1]},
            "build_id": build_id,
            "run_id": run_id,
            "input_schema": input_schema.as_dict() if input_schema else None,
            "output_schema": output_schema.as_dict(),
            "parents": [item.as_dict() for item in parents],
            "outputs": [item.as_dict() for item in outputs],
            "semantic_build_configuration_sha256": semantic_build_configuration_sha256,
            "physical_publication_configuration_sha256": (
                physical_publication_configuration_sha256
            ),
            "specification_profile": [
                item.as_dict() for item in specification_profile
            ],
            "registries": [item.as_dict() for item in registries],
            "reconciliation": reconciliation.as_dict(),
            "validation": validation.as_dict(),
            "warnings": list(warnings),
            "failures": list(failures),
            "publication": {"status": publication_status},
        }
    )
    return finalize_and_validate(
        manifest, manifest_type=_MANIFEST_TYPE, manifest_schema_version=_SCHEMA_VERSION
    )


__all__ = [
    "ArtifactReference",
    "ReconciliationResult",
    "SchemaRecord",
    "ValidationResult",
    "VersionedReference",
    "build_stage_manifest",
]
