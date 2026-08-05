"""Dataset Manifest builder (Reproducibility and Manifest Specification
SS8.5/SS8.6/SS8.7).

Only ever emits schema version 1.0.2 (SS8.6: Dataset Manifest 1.0.0 and
1.0.1 are withdrawn for prospective S8 production; new code must not emit
either). This
builder assembles the deterministic dataset-manifest *candidate*: it must
never contain a Review Manifest id, a Reproduction Manifest id, or a
Release Ledger hash (SS8.5) -- none of this builder's parameters accept
those, by construction.
"""

from __future__ import annotations

import dataclasses

from rcc002.constants import ViewId
from rcc002.s8.manifests.common import (
    DATASET_MANIFEST_PRODUCTION_VERSION,
    build_common_envelope,
    finalize_and_validate,
)
from rcc002.s8.reason_codes import ManifestValidationError
from rcc002.s8.views import VIEW_DEFINITIONS, VIEW_ORDER

_MANIFEST_TYPE = "dataset"
_SCHEMA_VERSION = DATASET_MANIFEST_PRODUCTION_VERSION
_QUALITY_STATUSES = frozenset({"PASS", "PASS_WITH_APPROVED_EXCEPTIONS", "FAIL"})
_REVIEW_TYPES = frozenset(
    {"scientific", "architecture", "editorial", "internal", "reproduction"}
)


@dataclasses.dataclass(frozen=True, slots=True)
class DataArtifactEntry:
    logical_name: str
    relative_path: str
    artifact_id: str
    byte_sha256: str
    semantic_sha256: str
    physical_layout_sha256: str
    size_bytes: int
    schema_ref: str
    schema_fingerprint_sha256: str
    view_allowlist_sha256: "str | None"

    def as_dict(self) -> dict[str, object]:
        return {"artifact_class": "DATA_ARTIFACT", **dataclasses.asdict(self)}


@dataclasses.dataclass(frozen=True, slots=True)
class SchemaArtifactEntry:
    logical_name: str
    relative_path: str
    byte_sha256: str
    size_bytes: int

    def as_dict(self) -> dict[str, object]:
        return {"artifact_class": "SCHEMA_ARTIFACT", **dataclasses.asdict(self)}


@dataclasses.dataclass(frozen=True, slots=True)
class ChildManifestEntry:
    manifest_type: str
    manifest_id: str
    relative_path: str
    byte_sha256: str
    size_bytes: int

    def as_dict(self) -> dict[str, object]:
        if self.manifest_type not in ("source", "stage", "run"):
            raise ManifestValidationError(
                "a dataset manifest's child_manifests may only reference "
                "already-final pre-Dataset source/stage/run manifests"
            )
        return {"artifact_class": "CONTROL_MANIFEST", **dataclasses.asdict(self)}


@dataclasses.dataclass(frozen=True, slots=True)
class VersionedReference:
    id: str
    version: str
    sha256: str

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


def _views_block() -> list[dict[str, object]]:
    return [
        {
            "schema_id": VIEW_DEFINITIONS[view_id].schema_id,
            "schema_version": VIEW_DEFINITIONS[view_id].schema_version,
            "schema_ref": VIEW_DEFINITIONS[view_id].schema_ref,
            "schema_fingerprint_sha256": VIEW_DEFINITIONS[
                view_id
            ].schema_fingerprint_sha256,
            "allowlist_sha256": VIEW_DEFINITIONS[view_id].allowlist_sha256,
        }
        for view_id in VIEW_ORDER
    ]


def build_dataset_manifest(
    *,
    dataset_id: str,
    dataset_artifact_set_id: str,
    dataset_artifact_set_preimage_sha256: str,
    build_id: str,
    publication_run_id: str,
    source_snapshot_ids: "list[str]",
    artifacts: "list[DataArtifactEntry]",
    schema_artifacts: "list[SchemaArtifactEntry]",
    child_manifests: "list[ChildManifestEntry]",
    stages: "list[VersionedReference]",
    registries: "list[VersionedReference]",
    specification_profile: "list[VersionedReference]",
    code_provenance: dict[str, object],
    semantic_build_configuration: "tuple[str, str]",
    physical_publication_configuration: "tuple[str, str]",
    environment_reference: VersionedReference,
    quality_summary: dict[str, object],
    dataset_lineage_graph_sha256: str,
    knowledge_lineage_graph_sha256: str,
    supersedes: "list[str]",
    review_requirements: "list[tuple[str, bool]]",
    created_at_utc: str,
    producer_component: str,
    producer_version: str,
    dataset_profile: str = "rcc002-canonical",
) -> dict[str, object]:
    if not source_snapshot_ids:
        raise ManifestValidationError("dataset manifest requires source_snapshot_ids")
    if not artifacts:
        raise ManifestValidationError("dataset manifest requires at least one artifact")
    if not schema_artifacts:
        raise ManifestValidationError(
            "dataset manifest requires at least one schema artifact"
        )
    if not child_manifests:
        raise ManifestValidationError(
            "dataset manifest requires at least one child manifest"
        )
    if len(stages) < 8:
        raise ManifestValidationError("dataset manifest requires at least 8 stages")
    if not registries:
        raise ManifestValidationError("dataset manifest requires at least one registry")
    if len(specification_profile) != 7:
        raise ManifestValidationError(
            "dataset manifest requires exactly the 7-document specification profile"
        )
    if quality_summary.get("status") not in _QUALITY_STATUSES:
        raise ManifestValidationError("invalid quality_summary.status")
    for review_type, _required in review_requirements:
        if review_type not in _REVIEW_TYPES:
            raise ManifestValidationError(f"invalid review_type: {review_type!r}")
    if not review_requirements:
        raise ManifestValidationError("dataset manifest requires review_requirements")

    manifest = build_common_envelope(
        manifest_type=_MANIFEST_TYPE,
        manifest_schema_version=_SCHEMA_VERSION,
        status="candidate",
        producer_component=producer_component,
        producer_version=producer_version,
        created_at_utc=created_at_utc,
    )
    manifest.update(
        {
            "dataset_id": dataset_id,
            "dataset_artifact_set_id": dataset_artifact_set_id,
            "dataset_artifact_set_preimage_sha256": (
                dataset_artifact_set_preimage_sha256
            ),
            "dataset_profile": dataset_profile,
            "build_id": build_id,
            "publication_run_id": publication_run_id,
            "source_snapshot_ids": list(source_snapshot_ids),
            "artifacts": [item.as_dict() for item in artifacts],
            "schema_artifacts": [item.as_dict() for item in schema_artifacts],
            "child_manifests": [item.as_dict() for item in child_manifests],
            "stages": [item.as_dict() for item in stages],
            "registries": [item.as_dict() for item in registries],
            "views": _views_block(),
            "specification_profile": [
                item.as_dict() for item in specification_profile
            ],
            "code_provenance": dict(code_provenance),
            "semantic_build_configuration": {
                "profile_id": semantic_build_configuration[0],
                "canonical_sha256": semantic_build_configuration[1],
            },
            "physical_publication_configuration": {
                "profile_id": physical_publication_configuration[0],
                "canonical_sha256": physical_publication_configuration[1],
            },
            "environment_reference": environment_reference.as_dict(),
            "quality_summary": dict(quality_summary),
            "dataset_lineage": {
                "graph_sha256": dataset_lineage_graph_sha256,
                "acyclic": True,
            },
            "knowledge_lineage": {
                "graph_sha256": knowledge_lineage_graph_sha256,
                "acyclic": True,
            },
            "publication_candidate": {
                "status": "candidate",
                "supersedes": list(supersedes),
            },
            "review_requirements": [
                {"review_type": review_type, "required": required}
                for review_type, required in review_requirements
            ],
        }
    )
    return finalize_and_validate(
        manifest, manifest_type=_MANIFEST_TYPE, manifest_schema_version=_SCHEMA_VERSION
    )


__all__ = [
    "ChildManifestEntry",
    "DataArtifactEntry",
    "SchemaArtifactEntry",
    "VersionedReference",
    "build_dataset_manifest",
]
