"""Run Manifest builder (Reproducibility and Manifest Specification
SS8.1/SS5.5)."""

from __future__ import annotations

import dataclasses

from rcc002.s8.manifests.common import build_common_envelope, finalize_and_validate
from rcc002.s8.reason_codes import ManifestValidationError

_MANIFEST_TYPE = "run"
_SCHEMA_VERSION = "1.0.0"
_OUTCOME_STATUSES = frozenset({"PASS", "FAIL", "NOT_ATTEMPTED", "QUARANTINED"})


@dataclasses.dataclass(frozen=True, slots=True)
class CodeProvenance:
    repository: str
    commit_sha: str
    worktree_clean: bool
    dirty_patch_sha256: "str | None"
    entrypoint: str

    def as_dict(self) -> dict[str, object]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True, slots=True)
class Library:
    name: str
    version: str


@dataclasses.dataclass(frozen=True, slots=True)
class EnvironmentRecord:
    environment_identity_profile_id: str
    environment_identity_sha256: str
    python_version: str
    lockfile_relative_path: str
    lockfile_byte_sha256: str
    platform: str
    libraries: "tuple[Library, ...]"

    def as_dict(self) -> dict[str, object]:
        return {
            "environment_identity_profile_id": self.environment_identity_profile_id,
            "environment_identity_sha256": self.environment_identity_sha256,
            "python_version": self.python_version,
            "lockfile_relative_path": self.lockfile_relative_path,
            "lockfile_byte_sha256": self.lockfile_byte_sha256,
            "platform": self.platform,
            "libraries": [
                {"name": lib.name, "version": lib.version} for lib in self.libraries
            ],
        }


@dataclasses.dataclass(frozen=True, slots=True)
class Outcome:
    status: str
    reason_codes: "tuple[str, ...]" = ()

    def as_dict(self) -> dict[str, object]:
        if self.status not in _OUTCOME_STATUSES:
            raise ManifestValidationError(f"invalid outcome status: {self.status!r}")
        return {"status": self.status, "reason_codes": list(self.reason_codes)}


def build_run_manifest(
    *,
    run_id: str,
    build_id: str,
    started_at_utc: str,
    ended_at_utc: str,
    code_provenance: CodeProvenance,
    environment: EnvironmentRecord,
    semantic_build_configuration_sha256: str,
    physical_publication_configuration_sha256: str,
    effective_cli_arguments: "list[str]",
    validation_outcome: Outcome,
    publication_outcome: Outcome,
    created_at_utc: str,
    producer_component: str,
    producer_version: str,
    status: str = "candidate",
) -> dict[str, object]:
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
            "run_id": run_id,
            "build_id": build_id,
            "started_at_utc": started_at_utc,
            "ended_at_utc": ended_at_utc,
            "code_provenance": code_provenance.as_dict(),
            "environment": environment.as_dict(),
            "execution_parameters": {
                "semantic_build_configuration_sha256": (
                    semantic_build_configuration_sha256
                ),
                "physical_publication_configuration_sha256": (
                    physical_publication_configuration_sha256
                ),
                "effective_cli_arguments": list(effective_cli_arguments),
            },
            "validation_outcome": validation_outcome.as_dict(),
            "publication_outcome": publication_outcome.as_dict(),
        }
    )
    return finalize_and_validate(
        manifest, manifest_type=_MANIFEST_TYPE, manifest_schema_version=_SCHEMA_VERSION
    )


__all__ = [
    "CodeProvenance",
    "EnvironmentRecord",
    "Library",
    "Outcome",
    "build_run_manifest",
]
