"""Review Manifest builder (Reproducibility and Manifest Specification
SS8.1/SS21). References its subject Dataset Manifest candidate one-way,
never the reverse (SS8.5)."""

from __future__ import annotations

import dataclasses

from rcc002.s8.manifests.common import build_common_envelope, finalize_and_validate
from rcc002.s8.reason_codes import ManifestValidationError

_MANIFEST_TYPE = "review"
_SCHEMA_VERSION = "1.0.0"
_REVIEW_TYPES = frozenset(
    {"internal", "scr", "architecture", "editorial", "certification", "external", "consolidation"}
)
_REVIEWER_SYSTEMS = frozenset({"human", "chatgpt", "gemini", "claude", "other"})
_REVIEW_STATUSES = frozenset({"pending", "passed", "passed_with_findings", "failed"})
_FINDING_SEVERITIES = frozenset({"BLOCKER", "MAJOR", "MINOR", "NOTE"})
_FINDING_STATUSES = frozenset({"OPEN", "CLOSED", "ACCEPTED_LIMITATION"})


@dataclasses.dataclass(frozen=True, slots=True)
class ReviewedArtifact:
    relative_path: str
    byte_sha256: str

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True, slots=True)
class Finding:
    finding_id: str
    severity: str
    status: str
    summary: str

    def as_dict(self) -> dict[str, object]:
        if self.severity not in _FINDING_SEVERITIES:
            raise ManifestValidationError(f"invalid finding severity: {self.severity!r}")
        if self.status not in _FINDING_STATUSES:
            raise ManifestValidationError(f"invalid finding status: {self.status!r}")
        return dataclasses.asdict(self)


def build_review_manifest(
    *,
    subject_dataset_manifest_id: str,
    subject_dataset_manifest_byte_sha256: str,
    review_id: str,
    review_type: str,
    reviewer: str,
    reviewer_system: str,
    reviewed_artifacts: "list[ReviewedArtifact]",
    started_at_utc: str,
    completed_at_utc: str,
    review_status: str,
    findings: "list[Finding]",
    resolution_references: "list[ReviewedArtifact]",
    created_at_utc: str,
    producer_component: str,
    producer_version: str,
    status: str = "final",
    review_artifact_relative_path: "str | None" = None,
    review_artifact_byte_sha256: "str | None" = None,
) -> dict[str, object]:
    if review_type not in _REVIEW_TYPES:
        raise ManifestValidationError(f"invalid review_type: {review_type!r}")
    if reviewer_system not in _REVIEWER_SYSTEMS:
        raise ManifestValidationError(f"invalid reviewer_system: {reviewer_system!r}")
    if review_status not in _REVIEW_STATUSES:
        raise ManifestValidationError(f"invalid review_status: {review_status!r}")
    if not reviewed_artifacts:
        raise ManifestValidationError(
            "a review manifest requires at least one reviewed artifact"
        )
    # An AI (claude/gemini) review recorded as passed/passed_with_findings
    # must point at its own written review artifact -- the same governance
    # pattern already established throughout this repository's RCC-002
    # review chain.
    if reviewer_system in ("claude", "gemini") and review_status in (
        "passed",
        "passed_with_findings",
    ):
        if not review_artifact_relative_path or not review_artifact_byte_sha256:
            raise ManifestValidationError(
                "a passed claude/gemini review requires "
                "review_artifact_relative_path and review_artifact_byte_sha256"
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
            "review_id": review_id,
            "review_type": review_type,
            "reviewer": reviewer,
            "reviewer_system": reviewer_system,
            "reviewed_artifacts": [item.as_dict() for item in reviewed_artifacts],
            "started_at_utc": started_at_utc,
            "completed_at_utc": completed_at_utc,
            "review_status": review_status,
            "findings": [item.as_dict() for item in findings],
            "resolution_references": [
                item.as_dict() for item in resolution_references
            ],
        }
    )
    if review_artifact_relative_path is not None:
        manifest["review_artifact_relative_path"] = review_artifact_relative_path
    if review_artifact_byte_sha256 is not None:
        manifest["review_artifact_byte_sha256"] = review_artifact_byte_sha256
    return finalize_and_validate(
        manifest, manifest_type=_MANIFEST_TYPE, manifest_schema_version=_SCHEMA_VERSION
    )


__all__ = ["Finding", "ReviewedArtifact", "build_review_manifest"]
