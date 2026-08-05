"""Artifact classification from the certified release artifact class
registry (``registries/rcc002/release/release_artifact_class_registry.v1.json``).

Loaded, not duplicated: every class name, placement rule, and path rule
below is read from the registry file at import time. Classification is
``EXACTLY_ONE_CLASS_PER_RELEASED_FILE`` with
``unknown_or_multiple_match_action: FAIL_RELEASE`` (the registry's own
stated cardinality rule) -- an unmatched or ambiguously-matched path is a
fail-closed :class:`ArtifactClassificationError`, never a best-effort guess.
"""

from __future__ import annotations

import json
import os

from rcc002.s8.reason_codes import ArtifactClassificationError

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_REGISTRY_PATH = os.path.join(
    _REPO_ROOT,
    "registries",
    "rcc002",
    "release",
    "release_artifact_class_registry.v1.json",
)

with open(_REGISTRY_PATH, encoding="utf-8") as _handle:
    _REGISTRY: dict[str, object] = json.load(_handle)

REGISTRY_ID: str = _REGISTRY["registry_id"]
REGISTRY_VERSION: str = _REGISTRY["registry_version"]

ARTIFACT_CLASSES: frozenset[str] = frozenset(
    entry["artifact_class"] for entry in _REGISTRY["classes"]
)
_ENTERS_DATASET_ARTIFACT_SET: dict[str, bool] = {
    entry["artifact_class"]: entry["enters_dataset_artifact_set_id"]
    for entry in _REGISTRY["classes"]
}
_DATASET_MANIFEST_PLACEMENT: dict[str, str] = {
    entry["artifact_class"]: entry["dataset_manifest_placement"]
    for entry in _REGISTRY["classes"]
}

_EXACT_PATH_RULES: dict[str, str] = {
    rule["exact_path"]: rule["artifact_class"]
    for rule in _REGISTRY["correction_bundle_path_rules"]
    if "exact_path" in rule
}
_PREFIX_RULES: "tuple[tuple[str, str], ...]" = tuple(
    (rule["path_prefix"], rule["artifact_class"])
    for rule in _REGISTRY["correction_bundle_path_rules"]
    if "path_prefix" in rule
)

DATA_ARTIFACTS_SORT_ORDER: "tuple[str, ...]" = tuple(
    _REGISTRY["dataset_release_rules"]["data_artifacts_sort_order"]
)


def enters_dataset_artifact_set_id(artifact_class: str) -> bool:
    if artifact_class not in _ENTERS_DATASET_ARTIFACT_SET:
        raise ArtifactClassificationError(
            f"unregistered artifact class: {artifact_class!r}"
        )
    return _ENTERS_DATASET_ARTIFACT_SET[artifact_class]


def dataset_manifest_placement(artifact_class: str) -> str:
    if artifact_class not in _DATASET_MANIFEST_PLACEMENT:
        raise ArtifactClassificationError(
            f"unregistered artifact class: {artifact_class!r}"
        )
    return _DATASET_MANIFEST_PLACEMENT[artifact_class]


def classify_path(relative_path: str) -> str:
    """Resolve ``relative_path`` to exactly one registered artifact class.

    Fail-closed on zero or more-than-one match, matching the registry's
    own ``unknown_or_multiple_match_action: FAIL_RELEASE`` rule.
    """
    if not isinstance(relative_path, str) or not relative_path:
        raise ArtifactClassificationError("relative_path must be a non-empty string")
    normalized = relative_path.replace("\\", "/").lstrip("./")

    if normalized in _EXACT_PATH_RULES:
        return _EXACT_PATH_RULES[normalized]

    matches = {
        artifact_class
        for prefix, artifact_class in _PREFIX_RULES
        if normalized.startswith(prefix)
    }
    if len(matches) == 1:
        return next(iter(matches))
    if not matches:
        raise ArtifactClassificationError(
            f"no registered artifact class matches path: {relative_path!r}"
        )
    raise ArtifactClassificationError(
        f"path matches more than one artifact class rule: {relative_path!r} "
        f"-> {sorted(matches)!r}"
    )


__all__ = [
    "ARTIFACT_CLASSES",
    "DATA_ARTIFACTS_SORT_ORDER",
    "REGISTRY_ID",
    "REGISTRY_VERSION",
    "classify_path",
    "dataset_manifest_placement",
    "enters_dataset_artifact_set_id",
]
