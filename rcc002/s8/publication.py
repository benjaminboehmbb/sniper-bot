"""Atomic S8 publication mechanics and release-ledger generation
(Reproducibility and Manifest Specification SS14.2/SS14.3).

This module never touches a real repository or dataset path: every
function operates on an explicit ``publish_root`` supplied by the caller
(normally a temporary directory in tests), matching this candidate's
scope boundary -- no runtime dataset, publication artifact, or repository
cache file may be created outside a caller-chosen sandbox.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from collections.abc import Iterable, Mapping

from rcc002.s8.reason_codes import PublicationError
from rcc002.s8.states import BuildState, require_publishable
from rcc002.s8.validation import require_portable_relative_path

_REQUIRED_PUBLICATION_GATES = (
    "all_required_artifacts_exist",
    "all_checksums_computed",
    "all_manifest_schemas_valid",
    "all_required_checks_passed",
    "no_parent_artifact_missing",
    "dataset_manifest_complete",
)


def require_publication_gates(gates: Mapping[str, bool]) -> None:
    """SS14.2: publication may not begin until every named gate is True."""
    missing = [name for name in _REQUIRED_PUBLICATION_GATES if not gates.get(name)]
    if missing:
        raise PublicationError(
            f"publication gates not satisfied: {missing!r}"
        )


def write_candidate_files(
    publish_root: str,
    files: Mapping[str, bytes],
) -> str:
    """Write every file under a fresh, unique temporary directory first
    (SS14.2: "Ein Build MUSS zunaechst in einem eindeutigen temporaeren
    Verzeichnis schreiben."). Returns the temporary directory path.
    """
    os.makedirs(publish_root, exist_ok=True)
    staging_dir = tempfile.mkdtemp(prefix=".s8-staging-", dir=publish_root)
    for relative_path, content in files.items():
        require_portable_relative_path(relative_path)
        target = os.path.join(staging_dir, relative_path)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "xb") as handle:
            handle.write(content)
    return staging_dir


def publish_atomically(
    staging_dir: str,
    publish_root: str,
    dataset_artifact_set_id: str,
    *,
    build_state: "BuildState | str",
    gates: Mapping[str, bool],
) -> str:
    """Atomically publish a fully-checked staging directory (SS14.2/14.3).

    The publication target directory name is the ``dataset_artifact_set_id``
    digest itself; a pre-existing target with the same name is an
    immutable, already-published artifact set and is never overwritten
    (SS14.3) -- this function raises instead of touching it.
    """
    require_publishable(build_state)
    require_publication_gates(gates)
    if not dataset_artifact_set_id.startswith("dataset-artifact-set:sha256:"):
        raise PublicationError(
            "dataset_artifact_set_id must be a dataset-artifact-set:sha256:<digest> id"
        )
    digest = dataset_artifact_set_id.rsplit(":", 1)[-1]
    target = os.path.join(publish_root, digest)
    if os.path.exists(target):
        raise PublicationError(
            f"refusing to overwrite an already-published artifact set: {target!r}"
        )
    os.makedirs(publish_root, exist_ok=True)
    os.rename(staging_dir, target)  # atomic within the same filesystem
    return target


def require_not_diagnostic_publication(
    build_state: "BuildState | str", *, context: str
) -> None:
    """SS14.4: a failed or quarantined partial result may be *kept* for
    diagnostics but must never appear under a final publication path."""
    from rcc002.s8.states import require_not_diagnostic_only

    require_not_diagnostic_only(build_state, context=context)


def build_release_ledger(files: Mapping[str, bytes], *, self_path: str) -> str:
    """Build the ``RELEASE_LEDGER`` content (SS5.9/SS14.2 step 6):
    ``sha256  ./<path>`` lines, ``LC_ALL=C`` lexical path order, excluding
    the ledger's own path, one trailing LF, no self-hash.
    """
    if self_path in files:
        raise PublicationError(
            "the release ledger must not list its own path (no self-entry)"
        )
    lines = []
    for relative_path in sorted(files):
        require_portable_relative_path(relative_path)
        digest = hashlib.sha256(files[relative_path]).hexdigest()
        lines.append(f"{digest}  ./{relative_path}")
    return "\n".join(lines) + "\n" if lines else ""


def verify_no_silent_overwrite(
    existing_dataset_artifact_set_ids: Iterable[str],
    new_dataset_artifact_set_id: str,
) -> None:
    """SS14.3: a genuinely new physical artifact set must never collide
    with an already-published one under the same identity."""
    if new_dataset_artifact_set_id in set(existing_dataset_artifact_set_ids):
        raise PublicationError(
            f"dataset_artifact_set_id {new_dataset_artifact_set_id!r} is "
            f"already published; repackaging must mint a new identity, "
            f"never reuse an existing one"
        )


__all__ = [
    "build_release_ledger",
    "publish_atomically",
    "require_not_diagnostic_publication",
    "require_publication_gates",
    "verify_no_silent_overwrite",
    "write_candidate_files",
]
