"""Semantic manifest and release validation for RCC-002 S8_EXPORT.

Layered on top of (never a replacement for) the structural JSON Schema
validation in ``rcc002.s8.manifests.common.validate_structural``: secret
scanning, portable-path safety, parent-existence, lineage acyclicity, and
byte/semantic artifact-inventory reconciliation.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Iterable, Mapping

from rcc002.s8.reason_codes import ManifestValidationError

_SECRET_PATTERN = re.compile(
    r"password|secret|token|private[_-]?key", re.IGNORECASE
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def scan_for_secrets(value: object, *, path: str = "$") -> None:
    """Recursively reject any string key or value that looks secret-like.

    Mirrors the per-field ``not: password|secret|token|private[_-]?key``
    pattern already used throughout the certified manifest schemas, but
    applies it recursively to arbitrary structures (for example a
    not-yet-hashed ``semantic_build_configuration`` payload) rather than
    only to individually-declared schema properties.
    """
    if isinstance(value, str):
        if _SECRET_PATTERN.search(value):
            raise ManifestValidationError(
                f"secret-like value at {path}: value matches a prohibited pattern"
            )
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(key, str) and _SECRET_PATTERN.search(key):
                raise ManifestValidationError(
                    f"secret-like key at {path}: {key!r}"
                )
            scan_for_secrets(item, path=f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            scan_for_secrets(item, path=f"{path}[{index}]")
        return


def require_portable_relative_path(path: str) -> str:
    """Reject an absolute path, a Windows drive path, a parent-traversal
    component, or a backslash (matches the certified ``portable_path``
    schema pattern, reusable outside a jsonschema context)."""
    if not isinstance(path, str) or not path:
        raise ManifestValidationError("relative_path must be a non-empty string")
    if path.startswith("/"):
        raise ManifestValidationError(f"absolute path is forbidden: {path!r}")
    if re.match(r"^[A-Za-z]:[\\/]", path):
        raise ManifestValidationError(f"drive-letter path is forbidden: {path!r}")
    if "\\" in path:
        raise ManifestValidationError(f"backslash path is forbidden: {path!r}")
    if any(part == ".." for part in path.split("/")):
        raise ManifestValidationError(f"parent-traversal path is forbidden: {path!r}")
    return path


def require_parents_exist(
    parent_relative_paths: Iterable[str],
    known_relative_paths: "set[str]",
    *,
    context: str,
) -> None:
    """Reject any referenced parent artifact absent from the known set."""
    missing = sorted(
        {path for path in parent_relative_paths if path not in known_relative_paths}
    )
    if missing:
        raise ManifestValidationError(
            f"{context}: missing parent artifact(s): {missing!r}"
        )


def require_acyclic(
    nodes: Iterable[str], edges: Iterable["tuple[str, str]"]
) -> None:
    """Reject a lineage graph that is not acyclic (SS11.2/SS11.3).

    ``edges`` are ``(from_node, to_node)`` "derived from" pairs. Raises
    fail-closed on any self-loop, dangling edge endpoint, or cycle.
    """
    node_set = set(nodes)
    adjacency: dict[str, list[str]] = {node: [] for node in node_set}
    for src, dst in edges:
        if src == dst:
            raise ManifestValidationError(f"lineage self-loop at node {src!r}")
        if src not in node_set or dst not in node_set:
            raise ManifestValidationError(
                f"lineage edge references an unknown node: ({src!r}, {dst!r})"
            )
        adjacency[src].append(dst)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in node_set}

    def visit(start: str) -> None:
        stack = [(start, iter(adjacency[start]))]
        color[start] = GRAY
        while stack:
            node, children = stack[-1]
            advanced = False
            for child in children:
                if color[child] == GRAY:
                    raise ManifestValidationError(
                        f"lineage graph contains a cycle involving {child!r}"
                    )
                if color[child] == WHITE:
                    color[child] = GRAY
                    stack.append((child, iter(adjacency[child])))
                    advanced = True
                    break
            if not advanced:
                color[node] = BLACK
                stack.pop()

    for node in node_set:
        if color[node] == WHITE:
            visit(node)


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def reconcile_artifact_inventory(
    entries: Iterable[Mapping[str, object]],
    resolve_bytes: Callable[[str], bytes],
) -> None:
    """Verify every inventoried artifact's declared byte hash and size
    against its actual bytes (mandatory item 12).

    ``entries`` are dataset-manifest-style dicts each carrying at least
    ``relative_path``, ``byte_sha256``, and (optionally) ``size_bytes``.
    ``resolve_bytes`` maps a relative path to its actual current bytes
    (a caller-supplied, explicit I/O boundary -- this function performs
    no filesystem access itself).
    """
    for entry in entries:
        relative_path = entry.get("relative_path")
        require_portable_relative_path(relative_path)  # type: ignore[arg-type]
        declared_hash = entry.get("byte_sha256")
        if not isinstance(declared_hash, str) or not _SHA256_RE.match(declared_hash):
            raise ManifestValidationError(
                f"{relative_path}: byte_sha256 must be a 64-character lowercase hex digest"
            )
        actual_bytes = resolve_bytes(relative_path)  # type: ignore[arg-type]
        actual_hash = sha256_of_bytes(actual_bytes)
        if actual_hash != declared_hash:
            raise ManifestValidationError(
                f"{relative_path}: declared byte_sha256 {declared_hash} does not "
                f"match actual {actual_hash}"
            )
        declared_size = entry.get("size_bytes")
        if declared_size is not None and declared_size != len(actual_bytes):
            raise ManifestValidationError(
                f"{relative_path}: declared size_bytes {declared_size} does not "
                f"match actual {len(actual_bytes)}"
            )


def reconcile_semantic_hash(
    *, declared_semantic_sha256: str, recomputed_semantic_sha256: str, context: str
) -> None:
    """Verify a declared ``semantic_sha256`` against an independently
    recomputed one (SS7.3 semantic fingerprint reconciliation)."""
    if not _SHA256_RE.match(declared_semantic_sha256):
        raise ManifestValidationError(f"{context}: malformed declared semantic_sha256")
    if declared_semantic_sha256 != recomputed_semantic_sha256:
        raise ManifestValidationError(
            f"{context}: declared semantic_sha256 {declared_semantic_sha256} "
            f"does not match the recomputed fingerprint "
            f"{recomputed_semantic_sha256}"
        )


__all__ = [
    "reconcile_artifact_inventory",
    "reconcile_semantic_hash",
    "require_acyclic",
    "require_parents_exist",
    "require_portable_relative_path",
    "scan_for_secrets",
    "sha256_of_bytes",
]
