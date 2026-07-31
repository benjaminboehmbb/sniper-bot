"""S1 normalization orchestration.

Parses raw S0 source rows into the canonical S1 row schema and sorts them
per Data Validation §8.5. Explicitly does NOT: fill gaps, interpolate
prices, remove duplicates, or compute indicators (Data Pipeline §7.2's
negative list) — duplicate detection is S2's job (Data Pipeline §7.3), so a
stable sort is used here specifically so that rows sharing an identical
canonical key keep their relative order rather than being silently
reordered or merged.

Severity note (interpretive, not a literal quotation — documented here so
the reasoning is auditable): Data Validation §7.2 states a parsing error in
a mandatory OHLCV field is `CRITICAL`, and §14.1 states nulls in
primary-key/time/OHLCV fields are `CRITICAL`. Every numeric field in the
minimal S1 row contract (open/high/low/close/volume) is a mandatory OHLCV
field, and Data Pipeline §7.2's S1 row contract makes every one of them
non-nullable — there is no representation in S1's own schema for "row
admitted with an invalid/placeholder OHLCV value" (that representation,
`quality_*_valid`/`quality_gate_pass`, is introduced only at S2). Consistent
with how this specification family uses `CRITICAL` everywhere else (a
build/artifact-level abort condition, never a silent per-row workaround),
a CRITICAL numeric parsing failure aborts normalization for the whole input
rather than dropping or placeholder-filling the offending row.
"""

from __future__ import annotations

import dataclasses

from rcc002.s0.profiles import (
    ArchivePeriod,
    TimestampUnit,
    normalize_timestamp_pair,
    reconcile_timestamp_to_period,
    resolve_timestamp_unit,
)
from rcc002.s1.numeric import NumericParsingError, parse_integer_field, parse_numeric_field
from rcc002.s1.row_id import compute_source_row_id
from rcc002.s1.schema import S1Row
from rcc002.s1.time import resolve_close_time_ms

OHLCV_FIELD_ORDER: tuple[str, ...] = ("open", "high", "low", "close", "volume")


class NormalizationAbortedError(Exception):
    """Raised when a CRITICAL finding aborts S1 normalization for this input.

    Carries every accumulated NumericParsingError so all CRITICAL findings
    are visible at once, not just the first.
    """

    def __init__(self, critical_errors: list[NumericParsingError]) -> None:
        self.critical_errors = critical_errors
        super().__init__(
            f"{len(critical_errors)} CRITICAL numeric parsing error(s); "
            f"normalization aborted for this input"
        )


def parse_csv_rows(
    text: str,
    column_mapping: dict[str, int],
    *,
    header_mode: str = "PRESENT",
) -> list[dict[str, str]]:
    """Split raw delimited source text into per-row raw string fields.

    `column_mapping` maps required raw-field names (`open_time`, `open`,
    `high`, `low`, `close`, `volume`, and optionally `close_time`) to their
    column index in the source file. No certified specification registers a
    concrete column layout for any provider/format, so this mapping must be
    supplied by the caller rather than assumed.
    """
    lines = text.splitlines()
    if not lines:
        return []
    if header_mode == "PRESENT":
        _header, *data_lines = lines
    elif header_mode == "ABSENT":
        data_lines = lines
    else:
        raise ValueError(f"unsupported registered header_mode {header_mode!r}")
    rows: list[dict[str, str]] = []
    for line in data_lines:
        if not line.strip():
            if header_mode == "ABSENT":
                raise ValueError(
                    "registered headerless source contains an empty record"
                )
            continue
        cells = line.split(",")
        rows.append({name: cells[idx] for name, idx in column_mapping.items()})
    return rows


@dataclasses.dataclass(frozen=True)
class NormalizationResult:
    """Result of normalizing one S0 source file's rows into S1 rows."""

    rows: tuple[S1Row, ...]  # sorted by canonical key (Data Validation §8.5)
    was_resorted: bool


def normalize_rows(
    raw_rows: list[dict[str, str]],
    *,
    source_snapshot_id: str,
    provider: str,
    market_type: str,
    symbol: str,
    interval: str,
    source_file_ordinal: int = 0,
    resolved_timestamp_unit: TimestampUnit | None = None,
    archive_period: ArchivePeriod | None = None,
    multi_provider: bool = False,
) -> NormalizationResult:
    """Normalize raw S0 rows into canonical, sorted S1 rows.

    `raw_rows` are in original source file order; each is a dict of raw
    string values keyed by `open_time`, `open`, `high`, `low`, `close`,
    `volume`, and optionally `close_time` (already extracted per the
    caller's column mapping — see parse_csv_rows).
    """
    critical_errors: list[NumericParsingError] = []
    parsed_rows: list[S1Row] = []
    if archive_period is not None:
        period_unit = resolve_timestamp_unit(archive_period)
        if (
            resolved_timestamp_unit is not None
            and resolved_timestamp_unit is not period_unit
        ):
            raise ValueError(
                "resolved timestamp unit contradicts archive period"
            )
        resolved_timestamp_unit = period_unit

    for original_record_index, raw_row in enumerate(raw_rows):
        source_row_id = compute_source_row_id(
            source_snapshot_id,
            source_file_ordinal,
            original_record_index,
        )
        row_had_critical_error = False

        try:
            raw_open_time = parse_integer_field("open_time", raw_row["open_time"])
        except NumericParsingError as exc:
            critical_errors.append(exc)
            continue  # cannot proceed with the rest of this row without open_time

        ohlcv_values: dict[str, float] = {}
        for field_name in OHLCV_FIELD_ORDER:
            try:
                ohlcv_values[field_name] = parse_numeric_field(field_name, raw_row[field_name])
            except NumericParsingError as exc:
                critical_errors.append(exc)
                row_had_critical_error = True

        raw_close_time = raw_row.get("close_time")
        raw_source_close_time: int | None = None
        if raw_close_time is not None:
            try:
                raw_source_close_time = parse_integer_field(
                    "close_time",
                    raw_close_time,
                )
            except NumericParsingError as exc:
                critical_errors.append(exc)
                row_had_critical_error = True

        if row_had_critical_error:
            continue

        # Interval alignment is NOT enforced here. Data Pipeline §7.3 assigns
        # "Intervallausrichtung" to S2, not S1; S1 only parses and passes the
        # value through unchanged (corrected 2026-07-27, DVSEV-001 Step 4 —
        # see rcc002.s1.time module docstring for the full rationale). A
        # misaligned-but-parseable open_time still yields a valid S1 row.
        if resolved_timestamp_unit is not None:
            if raw_source_close_time is None:
                raise ValueError(
                    "registered timestamp-unit conversion requires close_time"
                )
            open_time_ms, close_time_ms = normalize_timestamp_pair(
                raw_open_time,
                raw_source_close_time,
                resolved_timestamp_unit,
            )
            if archive_period is not None:
                reconcile_timestamp_to_period(
                    open_time_ms,
                    close_time_ms,
                    archive_period,
                )
        else:
            open_time_ms = raw_open_time
            close_time_ms = resolve_close_time_ms(
                open_time_ms,
                interval,
                source_close_time_ms=raw_source_close_time,
            )

        parsed_rows.append(
            S1Row(
                source_snapshot_id=source_snapshot_id,
                source_row_id=source_row_id,
                source_file_ordinal=source_file_ordinal,
                original_record_index=original_record_index,
                provider=provider,
                market_type=market_type,
                symbol=symbol,
                interval=interval,
                open_time=open_time_ms,
                close_time=close_time_ms,
                open=ohlcv_values["open"],
                high=ohlcv_values["high"],
                low=ohlcv_values["low"],
                close=ohlcv_values["close"],
                volume=ohlcv_values["volume"],
            )
        )

    if critical_errors:
        raise NormalizationAbortedError(critical_errors)

    original_order = tuple(parsed_rows)
    sorted_rows = tuple(
        sorted(parsed_rows, key=lambda row: row.canonical_key(multi_provider=multi_provider))
    )
    was_resorted = sorted_rows != original_order

    return NormalizationResult(rows=sorted_rows, was_resorted=was_resorted)


def normalize_registered_rows(
    raw_rows: list[dict[str, str]],
    *,
    archive_period: ArchivePeriod,
    source_snapshot_id: str,
    source_file_ordinal: int,
    provider: str,
    market_type: str,
    symbol: str,
    interval: str,
    multi_provider: bool = False,
) -> NormalizationResult:
    """Normalize one registered source file using its period-selected unit."""
    return normalize_rows(
        raw_rows,
        source_snapshot_id=source_snapshot_id,
        provider=provider,
        market_type=market_type,
        symbol=symbol,
        interval=interval,
        source_file_ordinal=source_file_ordinal,
        archive_period=archive_period,
        multi_provider=multi_provider,
    )
