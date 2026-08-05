"""Reproduction Manifest builder (Reproducibility and Manifest
Specification SS8.1/SS17). References its subject Dataset Manifest
candidate one-way, never the reverse (SS8.5)."""

from __future__ import annotations

import dataclasses

from rcc002.s8.manifests.common import build_common_envelope, finalize_and_validate
from rcc002.s8.reason_codes import ManifestValidationError

_MANIFEST_TYPE = "reproduction"
_SCHEMA_VERSION = "1.0.0"
_EQUALITY_RESULTS = frozenset({"E0", "E1", "E2", "E3"})
_FINAL_STATUSES = frozenset({"PASS", "FAIL"})


@dataclasses.dataclass(frozen=True, slots=True)
class EnvironmentReference:
    profile_id: str
    canonical_sha256: str

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True, slots=True)
class ArtifactComparison:
    logical_name: str
    byte_equal: bool
    semantic_equal: bool
    within_registered_tolerance: bool
    classification_equal: bool

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


def build_reproduction_manifest(
    *,
    subject_dataset_manifest_id: str,
    subject_dataset_manifest_byte_sha256: str,
    source_run_id: str,
    source_build_id: str,
    target_run_id: str,
    target_build_id: str,
    source_environment: EnvironmentReference,
    target_environment: EnvironmentReference,
    environment_differences: "list[str]",
    artifact_comparisons: "list[ArtifactComparison]",
    comparison_report_relative_path: str,
    equality_result: str,
    deviations: "list[str]",
    final_status: str,
    created_at_utc: str,
    producer_component: str,
    producer_version: str,
    status: str = "final",
) -> dict[str, object]:
    if equality_result not in _EQUALITY_RESULTS:
        raise ManifestValidationError(f"invalid equality_result: {equality_result!r}")
    if final_status not in _FINAL_STATUSES:
        raise ManifestValidationError(f"invalid final_status: {final_status!r}")
    if not artifact_comparisons:
        raise ManifestValidationError(
            "a reproduction manifest requires at least one artifact comparison"
        )
    if final_status == "PASS" and equality_result not in {"E2", "E3"}:
        raise ManifestValidationError(
            "published RCC-002 data requires at least E2 (SS7.4); a PASS "
            "reproduction cannot report E0/E1"
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
            "subject_dataset_manifest_id": subject_dataset_manifest_id,
            "subject_dataset_manifest_byte_sha256": subject_dataset_manifest_byte_sha256,
            "source_run_id": source_run_id,
            "source_build_id": source_build_id,
            "target_run_id": target_run_id,
            "target_build_id": target_build_id,
            "source_environment": source_environment.as_dict(),
            "target_environment": target_environment.as_dict(),
            "environment_differences": list(environment_differences),
            "artifact_comparisons": [
                item.as_dict() for item in artifact_comparisons
            ],
            "comparison_report_relative_path": comparison_report_relative_path,
            "equality_result": equality_result,
            "deviations": list(deviations),
            "final_status": final_status,
        }
    )
    return finalize_and_validate(
        manifest, manifest_type=_MANIFEST_TYPE, manifest_schema_version=_SCHEMA_VERSION
    )


__all__ = [
    "ArtifactComparison",
    "EnvironmentReference",
    "build_reproduction_manifest",
]
