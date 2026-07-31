"""S0 ingestion orchestration.

Ties together the file-integrity checks (rcc002/s0/integrity.py) and the
source_manifest model (rcc002/s0/manifest.py) into a single ingestion result
for one source file.

S8BCP-001 Revision 2 closes the previously deferred source-identity gaps for
the registered Binance Vision Spot kline profile. The strict archive-period,
timestamp, coverage, and Source Snapshot V1 implementation lives in
``rcc002.s0.profiles`` and ``rcc002.s0.source_identity``.

``ingest_source`` remains the legacy generic plain-CSV entry point and keeps
accepting a caller-supplied snapshot identity. New registered Binance builds
must use the strict profile implementation and may not use this legacy path
to bypass archive scanning or aggregate source identity.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from rcc002.s0.integrity import (
    IntegrityCheckResult,
    SourceFileState,
    TruncationFinding,
    check_exists,
    check_header_present,
    check_nonempty,
    check_not_disallowed_format,
    check_provider_checksum,
    check_readable,
    check_spreadsheet_truncation_boundary,
    compute_source_byte_sha256,
    count_data_rows,
)
from rcc002.s0.manifest import (
    LegacySourceManifest,
    migrate_legacy_aliases,
    validate_legacy_provider,
)


@dataclasses.dataclass(frozen=True)
class IngestionResult:
    """Outcome of ingesting one S0 source file.

    `manifest` is populated only when `state is SourceFileState.VERIFIED`.
    `checks` records every mandatory check from Data Validation §6.2, in
    order, regardless of outcome. `truncation_finding` is populated whenever
    the row count matches a Data Validation §6.3 boundary, independent of
    overall file state.
    """

    state: SourceFileState
    checks: tuple[IntegrityCheckResult, ...]
    truncation_finding: TruncationFinding | None
    manifest: LegacySourceManifest | None


def ingest_source(
    path: Path,
    *,
    source_snapshot_id: str,
    provider: str,
    market_type: str,
    symbol: str,
    interval: str,
    retrieved_at_utc: int,
    source_format: str,
    source_location: str,
    source_revision: str | None = None,
    license_or_terms_ref: str | None = None,
    provider_sha256: str | None = None,
    upstream_has_more_rows_or_longer_range: bool = False,
    raw_metadata: dict[str, object] | None = None,
) -> IngestionResult:
    """Run the S0 mandatory integrity checks and, if VERIFIED, build the
    source_manifest for one source file.

    `source_snapshot_id` is supplied by the caller because this function is
    the legacy generic plain-CSV entry point. Registered Binance Vision builds
    derive it through ``rcc002.s0.source_identity`` before constructing their
    aggregate Source Manifest.

    `raw_metadata`, if given, is passed through `migrate_legacy_aliases`
    first (Data Pipeline §7.1 / Data Validation §5.1) and any resulting
    canonical keys override the corresponding keyword arguments above. This
    lets callers pass metadata sourced from a legacy-aliased origin without
    handling the alias migration themselves.
    """
    if raw_metadata is not None:
        migrated = migrate_legacy_aliases(raw_metadata)
        provider = str(migrated.get("provider", provider))
        retrieved_at_utc = int(migrated.get("retrieved_at_utc", retrieved_at_utc))
    validate_legacy_provider(provider)

    checks: list[IntegrityCheckResult] = [
        check_exists(path),
        check_readable(path),
        check_nonempty(path),
        check_not_disallowed_format(path),
    ]

    # §6.2's remaining checks (header parsable, local SHA-256, provider
    # checksum match) require the file to already exist, be readable, and be
    # non-empty; per §6.1's own state list, a file failing any prerequisite
    # check cannot be VERIFIED, so those checks are only attempted once the
    # prerequisites already hold.
    if not all(c.passed for c in checks):
        state = SourceFileState.MISSING if not checks[0].passed else SourceFileState.CORRUPT
        return IngestionResult(
            state=state,
            checks=tuple(checks),
            truncation_finding=None,
            manifest=None,
        )

    header_check = check_header_present(path, source_format)
    checks.append(header_check)
    if not header_check.passed:
        return IngestionResult(
            state=SourceFileState.CORRUPT,
            checks=tuple(checks),
            truncation_finding=None,
            manifest=None,
        )

    local_sha256 = compute_source_byte_sha256(path)
    checks.append(IntegrityCheckResult("local_sha256_computed", True, local_sha256))

    checksum_check = check_provider_checksum(local_sha256, provider_sha256)
    checks.append(checksum_check)

    data_row_count = count_data_rows(path, source_format)
    truncation_finding = check_spreadsheet_truncation_boundary(
        data_row_count,
        upstream_has_more_rows_or_longer_range=upstream_has_more_rows_or_longer_range,
    )

    if not checksum_check.passed:
        return IngestionResult(
            state=SourceFileState.CHECKSUM_MISMATCH,
            checks=tuple(checks),
            truncation_finding=truncation_finding,
            manifest=None,
        )

    manifest = LegacySourceManifest(
        source_snapshot_id=source_snapshot_id,
        provider=provider,
        market_type=market_type,
        symbol=symbol,
        interval=interval,
        retrieved_at_utc=retrieved_at_utc,
        source_file_name=path.name,
        source_byte_sha256=local_sha256,
        source_format=source_format,
        source_location=source_location,
        source_revision=source_revision,
        license_or_terms_ref=license_or_terms_ref,
    )

    return IngestionResult(
        state=SourceFileState.VERIFIED,
        checks=tuple(checks),
        truncation_finding=truncation_finding,
        manifest=manifest,
    )
