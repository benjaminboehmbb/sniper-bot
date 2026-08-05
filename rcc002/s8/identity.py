"""Deterministic RCC-002 S8 identity builders (Reproducibility and Manifest
Specification SS5).

``source_snapshot_id`` is deliberately *not* reimplemented here: it is
already fully implemented and certified by
``rcc002.s0.source_identity.build_source_snapshot`` (the sole normative
owner of S0 provenance, per Source Manifest SS8.3). This module builds
every identity that is genuinely S8's own: ``build_id``, ``run_id``,
``artifact_id``, ``dataset_id``, ``dataset_artifact_set_id``, and the
generic ``manifest_id`` finalization algorithm (SS5.9) shared by all six
manifest types.

Semantic identity (``build_id``, ``dataset_id``) and physical/publication
identity (``artifact_id``, ``dataset_artifact_set_id``) are kept in
separate functions with disjoint preimage shapes, matching SS5.6/SS5.7/
SS5.8: a pure repartitioning changes the latter but never the former.
"""

from __future__ import annotations

import dataclasses
import datetime
import re
import uuid

from rcc002.s8.canonical import canonical_sha256
from rcc002.s8.reason_codes import IdentityError

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

_ID_PREFIX: dict[str, str] = {
    "source": "source",
    "build": "build",
    "artifact": "artifact",
    "dataset": "dataset",
    "dataset_artifact_set": "dataset-artifact-set",
    "manifest": "manifest",
}


def _require_sha256(name: str, value: object) -> str:
    if not isinstance(value, str) or not _SHA256_RE.match(value):
        raise IdentityError(f"{name} must be a 64-character lowercase hex digest")
    return value


def _require_nonempty_str(name: str, value: object) -> str:
    if not isinstance(value, str) or not value:
        raise IdentityError(f"{name} must be a non-empty string")
    return value


def _formatted_id(kind: str, digest: str) -> str:
    return f"{_ID_PREFIX[kind]}:sha256:{digest}"


def _finalize(kind: str, preimage: dict[str, object]) -> tuple[str, str]:
    digest = canonical_sha256(preimage)
    return _formatted_id(kind, digest), digest


@dataclasses.dataclass(frozen=True, slots=True)
class SpecificationProfileEntry:
    id: str
    version: str
    sha256: str

    def as_preimage(self) -> dict[str, str]:
        return {
            "id": _require_nonempty_str("specification_profile.id", self.id),
            "version": _require_nonempty_str(
                "specification_profile.version", self.version
            ),
            "sha256": _require_sha256("specification_profile.sha256", self.sha256),
        }


def build_id(
    *,
    parent_identities: "list[str]",
    code_commit_sha: str,
    dirty_patch_sha256: "str | None",
    semantic_build_configuration_sha256: str,
    specification_profile: "list[SpecificationProfileEntry]",
    pipeline_profile_id: str,
    schema_ids: "list[str]",
    environment_identity_profile_id: str,
    environment_identity_sha256: str,
    stage_or_stage_range: str,
) -> tuple[str, str]:
    """Compute ``build_id`` per SS5.4. Returns ``(build_id, preimage_sha256)``.

    Deliberately excludes (per SS5.4's explicit prohibition list): run
    start/end time, hostname, a random UUID, a temporary path,
    ``manifest_id``, the hash of the manifest that will contain this
    ``build_id``, ``physical_publication_configuration_sha256``,
    ``physical_layout_sha256``, ``artifact_id``, and
    ``dataset_artifact_set_id``.
    """
    if not parent_identities:
        raise IdentityError("build_id requires at least one parent identity")
    if not isinstance(code_commit_sha, str) or not _COMMIT_RE.match(code_commit_sha):
        raise IdentityError("code_commit_sha must be a 40-character lowercase hex SHA")
    if dirty_patch_sha256 is not None:
        _require_sha256("dirty_patch_sha256", dirty_patch_sha256)
    _require_sha256(
        "semantic_build_configuration_sha256", semantic_build_configuration_sha256
    )
    if not specification_profile:
        raise IdentityError("build_id requires a non-empty specification profile")
    if not schema_ids:
        raise IdentityError("build_id requires at least one schema id")
    _require_nonempty_str("pipeline_profile_id", pipeline_profile_id)
    _require_nonempty_str(
        "environment_identity_profile_id", environment_identity_profile_id
    )
    _require_sha256("environment_identity_sha256", environment_identity_sha256)
    _require_nonempty_str("stage_or_stage_range", stage_or_stage_range)

    preimage = {
        "identity_profile_id": "RCC002_BUILD_ID_V1",
        "parent_identities": list(parent_identities),
        "code_commit_sha": code_commit_sha,
        "dirty_patch_sha256": dirty_patch_sha256,
        "semantic_build_configuration_sha256": semantic_build_configuration_sha256,
        "specification_profile": [
            entry.as_preimage() for entry in specification_profile
        ],
        "pipeline_profile_id": pipeline_profile_id,
        "schema_ids": list(schema_ids),
        "environment_identity_profile_id": environment_identity_profile_id,
        "environment_identity_sha256": environment_identity_sha256,
        "stage_or_stage_range": stage_or_stage_range,
    }
    return _finalize("build", preimage)


def new_run_id(*, moment: "datetime.datetime | None" = None) -> str:
    """A fresh, nondeterministic ``run_id`` (SS5.2): ``run:<UTC>:<UUIDv7-or-v4>``."""
    if moment is None:
        moment = datetime.datetime.now(datetime.timezone.utc)
    if moment.tzinfo is None or moment.utcoffset() != datetime.timedelta(0):
        raise IdentityError("run_id timestamp must be timezone-aware UTC")
    timestamp = moment.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    make_uuid = getattr(uuid, "uuid7", uuid.uuid4)
    return f"run:{timestamp}:{make_uuid()}"


@dataclasses.dataclass(frozen=True, slots=True)
class DataArtifactIdentity:
    """Physical identity of one stored data artifact (SS5.6)."""

    schema_ref: str
    semantic_sha256: str
    physical_layout_sha256: str
    byte_sha256: str
    row_count: int
    logical_time_coverage: "tuple[int, int]"

    def as_preimage(self) -> dict[str, object]:
        _require_nonempty_str("schema_ref", self.schema_ref)
        _require_sha256("semantic_sha256", self.semantic_sha256)
        _require_sha256("physical_layout_sha256", self.physical_layout_sha256)
        _require_sha256("byte_sha256", self.byte_sha256)
        if isinstance(self.row_count, bool) or not isinstance(self.row_count, int):
            raise IdentityError("row_count must be an integer")
        if self.row_count < 0:
            raise IdentityError("row_count must be non-negative")
        start, end = self.logical_time_coverage
        for name, value in (("coverage_start", start), ("coverage_end", end)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise IdentityError(f"{name} must be an integer timestamp")
        if start > end:
            raise IdentityError("logical_time_coverage start exceeds end")
        return {
            "identity_profile_id": "RCC002_ARTIFACT_ID_V1",
            "schema_ref": self.schema_ref,
            "semantic_sha256": self.semantic_sha256,
            "physical_layout_sha256": self.physical_layout_sha256,
            "byte_sha256": self.byte_sha256,
            "row_count": self.row_count,
            "logical_time_coverage": {
                "min_open_time": start,
                "max_open_time": end,
            },
        }


def artifact_id(identity: DataArtifactIdentity) -> tuple[str, str]:
    """Compute ``artifact_id`` per SS5.6 (physical/data-container identity)."""
    return _finalize("artifact", identity.as_preimage())


@dataclasses.dataclass(frozen=True, slots=True)
class DatasetComponent:
    logical_name: str
    schema_ref: str
    semantic_sha256: str
    row_count: int
    logical_time_coverage: "tuple[int, int]"

    def as_preimage(self) -> dict[str, object]:
        _require_nonempty_str("logical_name", self.logical_name)
        _require_nonempty_str("schema_ref", self.schema_ref)
        _require_sha256("semantic_sha256", self.semantic_sha256)
        if isinstance(self.row_count, bool) or not isinstance(self.row_count, int):
            raise IdentityError("row_count must be an integer")
        start, end = self.logical_time_coverage
        for name, value in (("coverage_start", start), ("coverage_end", end)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise IdentityError(f"{name} must be an integer timestamp")
        return {
            "logical_name": self.logical_name,
            "schema_ref": self.schema_ref,
            "semantic_sha256": self.semantic_sha256,
            "row_count": self.row_count,
            "logical_time_coverage": {"min_open_time": start, "max_open_time": end},
        }


def dataset_id(
    *,
    components: "list[DatasetComponent]",
    release_schema_id: str,
    dataset_profile: str,
    build_id_value: str,
    semantic_build_configuration_sha256: str,
    quality_status: str,
    specification_profile: "list[SpecificationProfileEntry]",
) -> tuple[str, str]:
    """Compute ``dataset_id`` per SS5.7. Never influenced by ``artifact_id``,
    ``physical_layout_sha256``, ``byte_sha256``, file paths, partitioning,
    or writer profile."""
    if not components:
        raise IdentityError("dataset_id requires at least one logical component")
    names = [component.logical_name for component in components]
    if len(set(names)) != len(names):
        raise IdentityError("dataset_id logical component names must be unique")
    _require_nonempty_str("release_schema_id", release_schema_id)
    _require_nonempty_str("dataset_profile", dataset_profile)
    if not build_id_value.startswith("build:sha256:"):
        raise IdentityError("build_id_value must be a build:sha256:<digest> id")
    _require_sha256(
        "semantic_build_configuration_sha256", semantic_build_configuration_sha256
    )
    _require_nonempty_str("quality_status", quality_status)
    if not specification_profile:
        raise IdentityError("dataset_id requires a non-empty specification profile")

    preimage = {
        "identity_profile_id": "RCC002_DATASET_ID_V1",
        "components": [component.as_preimage() for component in components],
        "release_schema_id": release_schema_id,
        "dataset_profile": dataset_profile,
        "build_id": build_id_value,
        "semantic_build_configuration_sha256": semantic_build_configuration_sha256,
        "quality_status": quality_status,
        "specification_profile": [
            entry.as_preimage() for entry in specification_profile
        ],
    }
    return _finalize("dataset", preimage)


@dataclasses.dataclass(frozen=True, slots=True)
class PublishedDataArtifact:
    """One published ``DATA_ARTIFACT`` entry inside a dataset artifact set."""

    logical_name: str
    relative_path: str
    artifact_id_value: str
    byte_sha256: str
    semantic_sha256: str
    physical_layout_sha256: str
    size_bytes: int
    schema_ref: str
    schema_fingerprint_sha256: str
    view_allowlist_sha256: "str | None"

    def as_preimage(self) -> dict[str, object]:
        _require_nonempty_str("logical_name", self.logical_name)
        _require_nonempty_str("relative_path", self.relative_path)
        if not self.artifact_id_value.startswith("artifact:sha256:"):
            raise IdentityError("artifact_id_value must be an artifact:sha256:<digest> id")
        _require_sha256("byte_sha256", self.byte_sha256)
        _require_sha256("semantic_sha256", self.semantic_sha256)
        _require_sha256("physical_layout_sha256", self.physical_layout_sha256)
        if isinstance(self.size_bytes, bool) or not isinstance(self.size_bytes, int):
            raise IdentityError("size_bytes must be an integer")
        if self.size_bytes < 0:
            raise IdentityError("size_bytes must be non-negative")
        _require_nonempty_str("schema_ref", self.schema_ref)
        _require_sha256("schema_fingerprint_sha256", self.schema_fingerprint_sha256)
        if self.view_allowlist_sha256 is not None:
            _require_sha256("view_allowlist_sha256", self.view_allowlist_sha256)
        return {
            "logical_name": self.logical_name,
            "relative_path": self.relative_path,
            "artifact_id": self.artifact_id_value,
            "byte_sha256": self.byte_sha256,
            "semantic_sha256": self.semantic_sha256,
            "physical_layout_sha256": self.physical_layout_sha256,
            "size_bytes": self.size_bytes,
            "schema_ref": self.schema_ref,
            "schema_fingerprint_sha256": self.schema_fingerprint_sha256,
            "view_allowlist_sha256": self.view_allowlist_sha256,
        }


def dataset_artifact_set_id(
    *,
    dataset_id_value: str,
    physical_publication_configuration_sha256: str,
    data_artifacts: "list[PublishedDataArtifact]",
) -> tuple[str, str]:
    """Compute ``dataset_artifact_set_id`` per the exact SS5.8 preimage.

    ``data_artifacts`` is sorted by normalized ``relative_path`` then
    ``logical_name`` (SS5.8); only ``DATA_ARTIFACT`` entries participate.
    """
    if not dataset_id_value.startswith("dataset:sha256:"):
        raise IdentityError("dataset_id_value must be a dataset:sha256:<digest> id")
    _require_sha256(
        "physical_publication_configuration_sha256",
        physical_publication_configuration_sha256,
    )
    if not data_artifacts:
        raise IdentityError("dataset_artifact_set_id requires at least one artifact")

    ordered = sorted(
        data_artifacts, key=lambda item: (item.relative_path, item.logical_name)
    )
    paths = [item.relative_path for item in ordered]
    if len(set(paths)) != len(paths):
        raise IdentityError("dataset_artifact_set_id has duplicate relative_path entries")

    preimage = {
        "identity_profile_id": "RCC002_DATASET_ARTIFACT_SET_ID_V1",
        "dataset_id": dataset_id_value,
        "physical_publication_configuration_sha256": (
            physical_publication_configuration_sha256
        ),
        "data_artifacts": [item.as_preimage() for item in ordered],
    }
    return _finalize("dataset_artifact_set", preimage)


def finalize_manifest_id(manifest: dict[str, object]) -> tuple[str, dict[str, object]]:
    """Compute ``manifest_id`` per SS5.9 and return ``(manifest_id, manifest)``.

    Algorithm: canonicalize the manifest content *without* the
    ``manifest_id`` field, SHA-256 the canonical bytes, and set that as
    ``manifest_id``. The manifest must not already contain its own final
    byte hash or byte size (those belong to a downstream release record,
    never to the manifest itself), which this function does not add.
    """
    if not isinstance(manifest, dict):
        raise IdentityError("manifest must be a dict")
    if "manifest_id" in manifest and manifest["manifest_id"] not in (None, ""):
        raise IdentityError(
            "manifest must not already carry a manifest_id when finalizing"
        )
    for forbidden in ("byte_sha256", "file_size_bytes"):
        if forbidden in manifest:
            raise IdentityError(
                f"a manifest must not self-report {forbidden!r}"
            )
    without_id = {key: value for key, value in manifest.items() if key != "manifest_id"}
    digest = canonical_sha256(without_id)
    finalized = dict(manifest)
    finalized["manifest_id"] = _formatted_id("manifest", digest)
    return finalized["manifest_id"], finalized


__all__ = [
    "DataArtifactIdentity",
    "DatasetComponent",
    "PublishedDataArtifact",
    "SpecificationProfileEntry",
    "artifact_id",
    "build_id",
    "dataset_artifact_set_id",
    "dataset_id",
    "finalize_manifest_id",
    "new_run_id",
]
