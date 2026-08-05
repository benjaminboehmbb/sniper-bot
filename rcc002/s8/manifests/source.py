"""Source Manifest builder (Reproducibility and Manifest Specification
SS8.3).

Wraps an already-built, certified :class:`rcc002.s0.source_identity.SourceSnapshot`
(the sole normative owner of S0 provenance identity) rather than
recomputing any of its fields. A ``SourceSnapshot`` only exists once
``build_source_snapshot`` has already passed every coverage/ordinal/digest
reconciliation check, so ``coverage_reconciliation`` is always reported as
``PASS`` here -- a snapshot that failed reconciliation never reaches this
builder.
"""

from __future__ import annotations

from rcc002.s0.profiles import COLUMN_PROFILE_ID, TIMESTAMP_UNIT_PROFILE_ID
from rcc002.s0.source_identity import (
    DATASET_KIND,
    MARKET_TYPE,
    PROVIDER,
    SOURCE_RETRIEVAL_PROFILE_ID,
    SOURCE_RETRIEVAL_PROFILE_VERSION,
    SOURCE_ROW_ID_PROFILE_ID,
    SOURCE_ROW_ID_PROFILE_VERSION,
    SourceSnapshot,
)
from rcc002.s8.manifests.common import build_common_envelope, finalize_and_validate
from rcc002.s8.reason_codes import ManifestValidationError

_MANIFEST_TYPE = "source"
_SCHEMA_VERSION = "1.0.0"


def build_source_manifest(
    *,
    snapshot: SourceSnapshot,
    retrieved_at_utc: str,
    license_or_terms_ref: "str | None",
    created_at_utc: str,
    producer_component: str,
    producer_version: str,
    status: str = "candidate",
) -> dict[str, object]:
    if not isinstance(snapshot, SourceSnapshot):
        raise ManifestValidationError("snapshot must be a certified SourceSnapshot")

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
            "source_snapshot_id": snapshot.source_snapshot_id,
            "source_snapshot_preimage_sha256": snapshot.preimage_sha256,
            "source_retrieval_profile_id": SOURCE_RETRIEVAL_PROFILE_ID,
            "source_retrieval_profile_version": SOURCE_RETRIEVAL_PROFILE_VERSION,
            "source_row_id_profile_id": SOURCE_ROW_ID_PROFILE_ID,
            "source_row_id_profile_version": SOURCE_ROW_ID_PROFILE_VERSION,
            "provider": PROVIDER,
            "market_type": MARKET_TYPE,
            "dataset_kind": DATASET_KIND,
            "symbol": snapshot.symbol,
            "interval": snapshot.interval,
            "column_profile_id": COLUMN_PROFILE_ID,
            "timestamp_unit_profile_id": TIMESTAMP_UNIT_PROFILE_ID,
            "source_revision": snapshot.source_revision,
            "retrieved_at_utc": retrieved_at_utc,
            "source_files": [
                item.as_preimage() for item in snapshot.source_files
            ],
            "actual_coverage": {
                "min_open_time_utc_ms": snapshot.actual_coverage_min_open_time_utc_ms,
                "max_close_time_utc_ms": snapshot.actual_coverage_max_close_time_utc_ms,
                "record_count": snapshot.source_record_count,
            },
            "coverage_reconciliation": {"status": "PASS", "exceptions": []},
            "license_or_terms_ref": license_or_terms_ref,
        }
    )
    return finalize_and_validate(
        manifest, manifest_type=_MANIFEST_TYPE, manifest_schema_version=_SCHEMA_VERSION
    )


__all__ = ["build_source_manifest"]
