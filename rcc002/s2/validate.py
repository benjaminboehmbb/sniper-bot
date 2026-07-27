"""S2 validation orchestration.

Ties together schema/timestamp validation, duplicate resolution, gap/segment
formation, OHLCV invariants, optional anomaly detection, and the
quality_status/quality_gate_pass derivation, per
`RCC_002_DATA_VALIDATION_2026-07-23.md` §5-§20 and
`RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` §7.3.

Scope notes (deliberate, not silent gaps — each corresponds to a registered
reason code this minimal implementation cannot yet exercise):

- `DV_TIME_NOT_UTC`: not reachable. This package's canonical timestamps are
  already int64 UTC-millisecond values by construction (Data Validation
  §8.1; `docs/POLICIES/TIME_STANDARD.md`); no naive/ambiguous-timezone input
  path exists here to violate it.
- `DV_SCHEMA_REQUIRED_COLUMN_MISSING`, `DV_SCHEMA_UNEXPECTED_COLUMN`,
  `DV_SCHEMA_FINGERPRINT_MISMATCH`: not reachable. `S1Row` is a fully typed,
  validated dataclass with exactly the certified minimal field set; no raw,
  untyped column-level data reaches this module for these checks to apply
  to (S1 already owns and enforces the column contract).
- `DV_GAP_UNEXPLAINED`: implemented, but only for the `UNKNOWN` class by
  elimination. The other gap classes (`PROVIDER_OUTAGE_CONFIRMED`,
  `MARKET_NOT_AVAILABLE`, `SOURCE_FILE_MISSING`, `SOURCE_ROW_MISSING`,
  `PARSING_LOSS`, `FILTERING_LOSS`) require external evidence (provider-
  outage confirmation, market-calendar data, S0/S1 loss accounting) this
  implementation does not model and does not invent; absent any such
  evidence, every detected gap is classified `UNKNOWN` (Data Validation
  §11.2) by elimination.

  GOVERNANCE DECISION RECORD (implementation-level binding of an otherwise
  unspecified row-attachment target — approved 2026-07-27; NOT certified
  normative specification text, and no certified specification was
  modified to produce it): the certified text specifies `quality_gap_
  before`/`quality_gap_after` at row level (§11.3.2) and the gap's own
  classification as a property of a separate gap-level record (§11.1;
  `gap_report.csv`, §19), without stating which row (if any) a
  `quality_reason_codes` entry for gap classification should attach to.
  This implementation attaches both `DV_GAP_DETECTED` and (absent
  contrary evidence) `DV_GAP_UNEXPLAINED` exclusively to the first row
  after the gap — never to the row before it, and never to both —
  because: (1) the discontinuity first becomes observable, during ordered
  validation, at that row; (2) that row is also where the new
  `market_segment_id` begins (§11.3.1); (3) the row before the gap remains
  the valid terminal row of the preceding segment; (4) attaching the
  finding to both boundary rows would double-count one gap in row-level
  quality statistics. A future `gap_report.csv` (artifact-report
  generation; out of scope for Step 4, see below) may additionally carry
  one independent gap-level record without contradicting this row-level
  choice.
- `DV_SYNTHETIC_ROW_NONCANONICAL`: not reachable. The optional synthetic
  continuity view (§11.4, MAY) is not implemented; this module never
  produces a synthetic row.
- `DV_APPROVED_WARNING_ACTIVE`: not implemented. This is a Publication Gate
  (§20) concept — a versioned, governance-approved exception record — which
  is a separate, not-yet-implemented mechanism from row-level validation.
"""

from __future__ import annotations

import dataclasses
from typing import Callable, Sequence

from rcc002.reason_codes import (
    QUALITY_RULE_VERSION,
    derive_quality_status,
    sort_reason_codes,
)
from rcc002.s1.schema import S1Row
from rcc002.s1.time import is_interval_aligned, require_interval_duration_ms
from rcc002.s2.anomalies import AnomalyThresholds, detect_anomalies
from rcc002.s2.duplicates import (
    CollapsedGroup,
    ResolvedConflict,
    resolve_duplicates,
)
from rcc002.s2.invariants import check_ohlcv_invariants
from rcc002.s2.schema import S2Row
from rcc002.s2.segment import annotate_gaps_and_segments


class MixedSeriesInputError(ValueError):
    """Raised when input rows do not all share the same (market_type,
    symbol, interval) series identity.

    `validate_rows` processes exactly one series per call, matching S1's
    own per-call scope (`rcc002.s1.normalize.normalize_rows`).
    """


class RowReconciliationFailedError(Exception):
    """DV_ROW_RECONCILIATION_FAILED (CRITICAL): an internal accounting
    equation (Data Validation §17.2/§17.3) did not hold. This is a defensive
    self-consistency check on this module's own bookkeeping, not expected to
    ever trigger for correct input; per §16.1, CRITICAL severity's build
    effect is abort."""


@dataclasses.dataclass(frozen=True)
class ReconciliationSummary:
    """Data Validation §17.2/§17.3 reconciliation counts."""

    s1_input_rows: int
    duplicate_rows_removed: int
    s1_unique_valid_rows: int
    s2_observed_rows: int
    in_range_rows: int
    out_of_range_rows: int
    expected_intervals: int | None
    observed_unique_intervals: int | None
    missing_intervals: int | None


@dataclasses.dataclass(frozen=True)
class S2Result:
    rows: tuple[S2Row, ...]
    reconciliation: ReconciliationSummary
    collapsed_groups: tuple[CollapsedGroup, ...]
    resolved_conflicts: tuple[ResolvedConflict, ...]


def _quality_gate_pass(
    *,
    quality_is_observed: bool,
    quality_is_synthetic: bool,
    quality_has_source_conflict: bool,
    quality_timestamp_valid: bool,
    quality_ohlc_valid: bool,
    quality_volume_valid: bool,
    quality_market_values_valid: bool,
    active_codes: list[str],
) -> bool:
    """Data Validation §15.1, verbatim formula.

    "jeder aktive `WARN` durch das versionierte Qualitätsprofil ausdrücklich
    als nicht blockierend klassifiziert ist": no such profile is defined
    yet (Data Validation §25.1 lists it as a still-open parameter, distinct
    from and not resolved by this Step's `quality_rule_version` binding —
    see DVSEV-001 Scientific Consistency Review Observation DVSEV001-O1).
    Fail-closed default: absent that profile, ANY active WARN blocks
    `quality_gate_pass`, exactly as an active ERROR/CRITICAL would.
    """
    from rcc002.reason_codes import REASON_CODE_SEVERITY, Severity

    if not (
        quality_is_observed
        and not quality_is_synthetic
        and not quality_has_source_conflict
        and quality_timestamp_valid
        and quality_ohlc_valid
        and quality_volume_valid
        and quality_market_values_valid
    ):
        return False
    for code in active_codes:
        if REASON_CODE_SEVERITY[code] in (Severity.ERROR, Severity.CRITICAL, Severity.WARN):
            return False
    return True


def validate_rows(
    s1_rows: Sequence[S1Row],
    *,
    multi_provider: bool = False,
    conflict_resolution_rule: Callable[[Sequence[S1Row]], S1Row | None] | None = None,
    expected_start_ms: int | None = None,
    expected_end_ms: int | None = None,
    anomaly_thresholds: AnomalyThresholds | None = None,
) -> S2Result:
    """Validate one series' worth of S1 rows into canonical S2 rows.

    All rows in `s1_rows` must share the same (`market_type`, `symbol`,
    `interval`) — one series per call, matching S1's own scope. Rows are
    grouped by `provider` for gap/segment purposes only when
    `multi_provider=True` (matching `S1Row.canonical_key`'s own convention).

    Raises `MixedSeriesInputError` if the input spans more than one series,
    `rcc002.s2.duplicates.ConflictingDuplicatesWithoutResolutionRuleError` if
    an unresolved conflicting duplicate is found (§10.2, build abort), or
    `RowReconciliationFailedError` if this module's own row-count bookkeeping
    is internally inconsistent (§17, defensive CRITICAL self-check).
    """
    if not s1_rows:
        return S2Result(
            rows=(),
            reconciliation=ReconciliationSummary(
                s1_input_rows=0,
                duplicate_rows_removed=0,
                s1_unique_valid_rows=0,
                s2_observed_rows=0,
                in_range_rows=0,
                out_of_range_rows=0,
                expected_intervals=None,
                observed_unique_intervals=None,
                missing_intervals=None,
            ),
            collapsed_groups=(),
            resolved_conflicts=(),
        )

    series_identities = {(row.market_type, row.symbol, row.interval) for row in s1_rows}
    if len(series_identities) != 1:
        raise MixedSeriesInputError(
            f"validate_rows requires exactly one (market_type, symbol, interval) "
            f"series per call; got {sorted(series_identities)}"
        )
    interval = next(iter(series_identities))[2]
    interval_duration_ms = require_interval_duration_ms(interval)

    dedup_result = resolve_duplicates(
        s1_rows,
        multi_provider=multi_provider,
        conflict_resolution_rule=conflict_resolution_rule,
    )
    deduped_rows = sorted(
        dedup_result.rows, key=lambda row: row.canonical_key(multi_provider=multi_provider)
    )

    # Group by provider for gap/segment purposes only in multi-provider mode.
    provider_groups: dict[str | None, list[S1Row]] = {}
    for row in deduped_rows:
        key = row.provider if multi_provider else None
        provider_groups.setdefault(key, []).append(row)

    gap_annotation_by_source_row_id: dict[str, object] = {}
    for provider_key, group_rows in provider_groups.items():
        annotations = annotate_gaps_and_segments(
            group_rows,
            interval=interval,
            interval_duration_ms=interval_duration_ms,
            provider=provider_key,
            market_type=group_rows[0].market_type,
            symbol=group_rows[0].symbol,
            multi_provider=multi_provider,
        )
        for annotation in annotations:
            gap_annotation_by_source_row_id[annotation.source_row_id] = annotation

    gap_before_by_source_row_id = {
        source_row_id: annotation.gap_before
        for source_row_id, annotation in gap_annotation_by_source_row_id.items()
    }
    anomaly_findings = None
    if anomaly_thresholds is not None:
        anomaly_findings = detect_anomalies(
            deduped_rows,
            thresholds=anomaly_thresholds,
            gap_before_by_source_row_id=gap_before_by_source_row_id,
        )

    in_range_count = 0
    out_of_range_count = 0

    s2_rows: list[S2Row] = []
    for row in deduped_rows:
        active_codes: list[str] = []

        timestamp_valid = is_interval_aligned(row.open_time, row.interval)
        if not timestamp_valid:
            active_codes.append("DV_TIME_MISALIGNED")

        in_range = True
        if expected_start_ms is not None and row.open_time < expected_start_ms:
            in_range = False
        if expected_end_ms is not None and row.open_time > expected_end_ms:
            in_range = False
        if expected_start_ms is not None or expected_end_ms is not None:
            if in_range:
                in_range_count += 1
            else:
                out_of_range_count += 1
                active_codes.append("DV_TIME_OUT_OF_RANGE")
        else:
            in_range_count += 1

        invariants = check_ohlcv_invariants(
            open=row.open, high=row.high, low=row.low, close=row.close, volume=row.volume
        )
        if invariants.nonfinite_fields:
            active_codes.append("DV_NUMERIC_NONFINITE")
        if invariants.ohlc_invariant_violated:
            active_codes.append("DV_OHLC_INVARIANT_FAILED")
        if invariants.volume_negative:
            active_codes.append("DV_VOLUME_NEGATIVE")
        if invariants.volume_zero_observed:
            active_codes.append("DV_VOLUME_ZERO_OBSERVED")

        annotation = gap_annotation_by_source_row_id[row.source_row_id]
        if annotation.gap_before:  # type: ignore[attr-defined]
            # Implementation-level binding (see module docstring): both gap
            # codes attach exclusively to the first row after the gap.
            active_codes.append("DV_GAP_DETECTED")
            # No gap-classification evidence is modeled in this
            # implementation (see module docstring); every detected gap is
            # therefore UNKNOWN by elimination, per Data Validation §11.2.
            active_codes.append("DV_GAP_UNEXPLAINED")
            active_codes.append("DV_TIME_GAP_SEGMENT_STARTED")

        is_collapse_primary = (
            row.source_row_id in dedup_result.identical_collapse_primary_source_row_ids
        )
        if is_collapse_primary:
            active_codes.append("DV_DUPLICATE_IDENTICAL_COLLAPSED")

        is_conflict_resolved = row.source_row_id in dedup_result.conflict_resolved_source_row_ids
        if is_conflict_resolved:
            active_codes.append("DV_SOURCE_CONFLICT_RESOLVED")

        if anomaly_findings is not None:
            if row.source_row_id in anomaly_findings.extreme_candle_return:
                active_codes.append("DV_ANOMALY_EXTREME_CANDLE_RETURN")
            if row.source_row_id in anomaly_findings.extreme_high_low_range:
                active_codes.append("DV_ANOMALY_EXTREME_HIGH_LOW_RANGE")
            if row.source_row_id in anomaly_findings.extreme_volume:
                active_codes.append("DV_ANOMALY_EXTREME_VOLUME")
            if row.source_row_id in anomaly_findings.zero_volume_cluster:
                active_codes.append("DV_ANOMALY_ZERO_VOLUME_CLUSTER")
            if row.source_row_id in anomaly_findings.repeated_identical_ohlc:
                active_codes.append("DV_ANOMALY_REPEATED_IDENTICAL_OHLC")
            if row.source_row_id in anomaly_findings.partition_boundary_jump:
                active_codes.append("DV_ANOMALY_PARTITION_BOUNDARY_JUMP")

        quality_market_values_valid = invariants.ohlc_valid and invariants.volume_valid
        quality_has_source_conflict = False  # unresolved conflicts abort; see module docstring

        sorted_codes = tuple(sort_reason_codes(active_codes))
        quality_status = derive_quality_status(active_codes)
        gate_pass = _quality_gate_pass(
            quality_is_observed=True,
            quality_is_synthetic=False,
            quality_has_source_conflict=quality_has_source_conflict,
            quality_timestamp_valid=timestamp_valid,
            quality_ohlc_valid=invariants.ohlc_valid,
            quality_volume_valid=invariants.volume_valid,
            quality_market_values_valid=quality_market_values_valid,
            active_codes=active_codes,
        )

        s2_rows.append(
            S2Row(
                source_snapshot_id=row.source_snapshot_id,
                source_row_id=row.source_row_id,
                provider=row.provider,
                market_type=row.market_type,
                symbol=row.symbol,
                interval=row.interval,
                open_time=row.open_time,
                close_time=row.close_time,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume,
                market_segment_id=annotation.market_segment_id,  # type: ignore[attr-defined]
                quality_is_observed=True,
                quality_is_synthetic=False,
                quality_has_source_conflict=quality_has_source_conflict,
                quality_gap_before=annotation.gap_before,  # type: ignore[attr-defined]
                quality_gap_after=annotation.gap_after,  # type: ignore[attr-defined]
                quality_timestamp_valid=timestamp_valid,
                quality_ohlc_valid=invariants.ohlc_valid,
                quality_volume_valid=invariants.volume_valid,
                quality_market_values_valid=quality_market_values_valid,
                quality_status=quality_status,
                quality_reason_codes=sorted_codes,
                quality_rule_version=QUALITY_RULE_VERSION,
                quality_gate_pass=gate_pass,
            )
        )

    # --- Reconciliation (§17.2/§17.3) ---
    s1_input_rows = len(s1_rows)
    s1_unique_valid_rows = len(deduped_rows)
    duplicate_rows_removed = s1_input_rows - s1_unique_valid_rows
    s2_observed_rows = len(s2_rows)

    if s2_observed_rows != s1_unique_valid_rows:
        raise RowReconciliationFailedError(
            f"s2_observed_rows ({s2_observed_rows}) != s1_unique_valid_rows "
            f"({s1_unique_valid_rows}); DV_ROW_RECONCILIATION_FAILED"
        )

    expected_intervals = None
    observed_unique_intervals = None
    missing_intervals = None
    if expected_start_ms is not None and expected_end_ms is not None:
        if (expected_end_ms - expected_start_ms) % interval_duration_ms != 0:
            raise ValueError(
                "expected_start_ms/expected_end_ms must be an exact multiple "
                "of interval_duration_ms apart, per Data Validation §9.1"
            )
        expected_intervals = (expected_end_ms - expected_start_ms) // interval_duration_ms + 1
        observed_unique_intervals = in_range_count
        missing_intervals = expected_intervals - observed_unique_intervals
        if expected_intervals != observed_unique_intervals + missing_intervals:
            raise RowReconciliationFailedError(
                "expected_intervals != observed_unique_intervals + missing_intervals; "
                "DV_ROW_RECONCILIATION_FAILED"
            )

    reconciliation = ReconciliationSummary(
        s1_input_rows=s1_input_rows,
        duplicate_rows_removed=duplicate_rows_removed,
        s1_unique_valid_rows=s1_unique_valid_rows,
        s2_observed_rows=s2_observed_rows,
        in_range_rows=in_range_count,
        out_of_range_rows=out_of_range_count,
        expected_intervals=expected_intervals,
        observed_unique_intervals=observed_unique_intervals,
        missing_intervals=missing_intervals,
    )

    return S2Result(
        rows=tuple(s2_rows),
        reconciliation=reconciliation,
        collapsed_groups=dedup_result.collapsed_groups,
        resolved_conflicts=dedup_result.resolved_conflicts,
    )
