"""The certified seven-document RCC-002 specification profile
(Dataset Manifest Schema 1.0.2, ``specification_profile`` prefixItems;
Reproducibility and Manifest Specification SS8.6/SS12.3).

Document IDs, versions, and their owning file are transcribed from the
certified Dataset Manifest 1.0.2 schema's ``specification_profile``
``prefixItems`` (each entry's ``id``/``version`` is a schema-level
``const``). Each document's SHA-256 is computed mechanically from the
current file content -- never hardcoded -- so this module cannot go
stale relative to the certified specification documents on disk (S8
Implementation Readiness Review RR-004 SS8, non-blocking obligation 3).
"""

from __future__ import annotations

import hashlib
import os

from rcc002.s8.identity import SpecificationProfileEntry
from rcc002.s8.reason_codes import ManifestValidationError

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_SPEC_DIR = os.path.join(_REPO_ROOT, "docs", "specifications")

# (doc_id, version, filename), in the certified prefixItems order.
_PROFILE_TABLE: "tuple[tuple[str, str, str], ...]" = (
    (
        "RCC_002_DATA_PIPELINE_SPECIFICATION",
        "0.9.0",
        "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
    ),
    ("RCC-002-DV", "0.6.0", "RCC_002_DATA_VALIDATION_2026-07-23.md"),
    ("RCC-002-IS", "0.4.3", "RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md"),
    ("RCC-002-ST", "0.4.2", "RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md"),
    ("RCC-002-RG", "0.5.1", "RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md"),
    (
        "RCC-002-LF",
        "0.5.0",
        "RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md",
    ),
    ("RCC-002-RM", "0.9.1", "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md"),
)


def _file_sha256(filename: str) -> str:
    path = os.path.join(_SPEC_DIR, filename)
    if not os.path.isfile(path):
        raise ManifestValidationError(
            f"certified specification document missing: {filename!r}"
        )
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def current_specification_profile() -> "tuple[SpecificationProfileEntry, ...]":
    """The seven certified documents with their current on-disk SHA-256,
    in the exact certified order."""
    return tuple(
        SpecificationProfileEntry(id=doc_id, version=version, sha256=_file_sha256(filename))
        for doc_id, version, filename in _PROFILE_TABLE
    )


__all__ = ["current_specification_profile"]
