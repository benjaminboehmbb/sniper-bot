"""Shared scaffolding for the six RCC-002 S8 manifest builders.

Structural validation loads and reuses the certified JSON Schemas under
``schemas/rcc002/manifests/`` (never a reimplementation of them); semantic
validation is layered on top by ``rcc002.s8.validation`` and the
individual builder modules.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache

import jsonschema

from rcc002.s8.identity import finalize_manifest_id
from rcc002.s8.reason_codes import ManifestValidationError

_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
_SCHEMA_ROOT = os.path.join(_REPO_ROOT, "schemas", "rcc002", "manifests")

PROJECT = "RCC-002"

# manifest_type -> schema directory name
_SCHEMA_DIR_NAME: dict[str, str] = {
    "source": "source-manifest",
    "stage": "stage-manifest",
    "run": "run-manifest",
    "dataset": "dataset-manifest",
    "review": "review-manifest",
    "reproduction": "reproduction-manifest",
}

_SCHEMA_ID: dict[str, str] = {
    "source": "rcc002.source-manifest",
    "stage": "rcc002.stage-manifest",
    "run": "rcc002.run-manifest",
    "dataset": "rcc002.dataset-manifest",
    "review": "rcc002.review-manifest",
    "reproduction": "rcc002.reproduction-manifest",
}

# The only Dataset Manifest version new S8 code may ever emit (Reproducibility
# and Manifest Specification SS8.6, RCC-002-S8-CAND-BCP-001-REV9: "Prospektive
# S8-Kandidaten MUESSEN Schema 1.0.2 verwenden."). Schema 1.0.0 and 1.0.1 are
# withdrawn for prospective S8 production ("neuer Code DARF Dataset Manifest
# 1.0.0/1.0.1 NICHT ausgeben") while remaining certified, byte-identical
# historical artifacts for historical verification.
DATASET_MANIFEST_PRODUCTION_VERSION = "1.0.2"
_PROHIBITED_DATASET_MANIFEST_VERSIONS = frozenset({"1.0.0", "1.0.1"})


@lru_cache(maxsize=None)
def _load_schema(manifest_type: str, version: str) -> dict:
    if manifest_type not in _SCHEMA_DIR_NAME:
        raise ManifestValidationError(f"unknown manifest type: {manifest_type!r}")
    if manifest_type == "dataset" and version in _PROHIBITED_DATASET_MANIFEST_VERSIONS:
        raise ManifestValidationError(
            f"Dataset Manifest {version} is withdrawn for prospective S8 "
            "production; new code may only emit "
            f"{DATASET_MANIFEST_PRODUCTION_VERSION}"
        )
    path = os.path.join(
        _SCHEMA_ROOT, _SCHEMA_DIR_NAME[manifest_type], f"{version}.schema.json"
    )
    if not os.path.isfile(path):
        raise ManifestValidationError(
            f"no certified schema for {manifest_type}/{version}"
        )
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def schema_ref(manifest_type: str, version: str) -> str:
    if manifest_type not in _SCHEMA_ID:
        raise ManifestValidationError(f"unknown manifest type: {manifest_type!r}")
    return f"{_SCHEMA_ID[manifest_type]}/{version}"


def validate_structural(manifest: dict, manifest_type: str, version: str) -> None:
    """Validate ``manifest`` against the certified JSON Schema.

    Raises :class:`ManifestValidationError` fail-closed for any schema
    violation, with every violation's JSON pointer and message collected
    (not merely the first).
    """
    schema = _load_schema(manifest_type, version)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema, format_checker=jsonschema.FormatChecker())
    errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.path))
    if errors:
        details = "; ".join(
            f"{'/'.join(str(p) for p in error.path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise ManifestValidationError(
            f"{manifest_type}-manifest/{version} failed structural "
            f"validation: {details}"
        )


def build_common_envelope(
    *,
    manifest_type: str,
    manifest_schema_version: str,
    status: str,
    producer_component: str,
    producer_version: str,
    created_at_utc: str,
) -> dict[str, object]:
    """The SS8.2 mandatory-in-every-manifest field block, without ``manifest_id``
    (finalized separately, once the full manifest body is assembled)."""
    if manifest_type not in _SCHEMA_ID:
        raise ManifestValidationError(f"unknown manifest type: {manifest_type!r}")
    return {
        "manifest_schema_id": _SCHEMA_ID[manifest_type],
        "manifest_schema_version": manifest_schema_version,
        "manifest_schema_ref": schema_ref(manifest_type, manifest_schema_version),
        "manifest_type": manifest_type,
        "created_at_utc": created_at_utc,
        "producer": {"component": producer_component, "version": producer_version},
        "project": PROJECT,
        "status": status,
    }


def finalize_and_validate(
    manifest_without_id: dict[str, object],
    *,
    manifest_type: str,
    manifest_schema_version: str,
) -> dict[str, object]:
    """Compute ``manifest_id`` (SS5.9) and structurally validate the result."""
    _manifest_id, finalized = finalize_manifest_id(manifest_without_id)
    validate_structural(finalized, manifest_type, manifest_schema_version)
    return finalized


__all__ = [
    "DATASET_MANIFEST_PRODUCTION_VERSION",
    "PROJECT",
    "build_common_envelope",
    "finalize_and_validate",
    "schema_ref",
    "validate_structural",
]
