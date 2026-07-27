"""S2 gap detection and `market_segment_id` formation.

Transcribed from RCC_002_DATA_VALIDATION_2026-07-23.md §11 ("Lückenerkennung"),
specifically §11.1 (Definition), §11.3.1 (Kanonische Marktsegment-ID), and
§11.3.2 (Gap-Felder).
"""

from __future__ import annotations

import dataclasses
import hashlib

# §11.3.1: "Die ID muss deterministisch aus: kanonischer Marktidentität;
# erstem `open_time` des Segments; Intervall; `segment_id_profile_id`;
# `segment_id_profile_version` gebildet werden. Eine zufällige UUID ist
# unzulässig." §25.1 lists the "Segment-ID-Kanonisierungsprofil" itself as
# an open implementation parameter (same category as `source_row_id`'s own
# profile) — self-defined and versioned here, not resolved at the
# specification level.
MARKET_SEGMENT_ID_PROFILE_ID = "RCC002_S2_MARKET_SEGMENT_ID_V1"
MARKET_SEGMENT_ID_PROFILE_VERSION = "1"


def compute_market_segment_id(
    *,
    provider: str | None,
    market_type: str,
    symbol: str,
    interval: str,
    first_open_time_ms: int,
    multi_provider: bool,
) -> str:
    """Deterministically derive `market_segment_id` for a new segment.

    Canonical market identity includes `provider` only when `multi_provider`
    is True, matching this package's existing canonical-key convention
    (rcc002.s1.schema.S1Row.canonical_key).
    """
    identity_parts = (
        [provider, market_type, symbol, interval] if multi_provider else [market_type, symbol, interval]
    )
    canonical_string = "|".join(
        [
            *identity_parts,
            str(first_open_time_ms),
            MARKET_SEGMENT_ID_PROFILE_ID,
            MARKET_SEGMENT_ID_PROFILE_VERSION,
        ]
    )
    digest = hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()
    return f"{MARKET_SEGMENT_ID_PROFILE_ID}:{MARKET_SEGMENT_ID_PROFILE_VERSION}:{digest}"


@dataclasses.dataclass(frozen=True)
class RowGapAnnotation:
    """Per-row gap/segment annotation, keyed by `source_row_id`."""

    source_row_id: str
    market_segment_id: str
    gap_before: bool
    gap_after: bool
    gap_detected: bool  # True if gap_before or gap_after (general boundary indicator;
    # rcc002.s2.validate attaches DV_GAP_DETECTED/DV_GAP_UNEXPLAINED using
    # `gap_before` alone, not this field — see its module docstring)


def annotate_gaps_and_segments(
    rows_sorted_by_open_time: list,
    *,
    interval: str,
    interval_duration_ms: int,
    provider: str | None,
    market_type: str,
    symbol: str,
    multi_provider: bool,
) -> list[RowGapAnnotation]:
    """Compute gap flags and `market_segment_id` for one already-deduplicated,
    single-series row sequence, sorted ascending by `open_time`.

    A new segment begins at the first row, and after any deviation from the
    exactly-expected next `open_time` (§11.3.1). §11.3.2: no gap flag is
    raised at the outer edge of the requested range purely for data missing
    outside it — this function only ever compares *consecutive rows already
    present*, so that case does not arise here by construction (the caller
    is responsible for not including out-of-range synthetic boundary rows).
    """
    annotations: list[RowGapAnnotation] = []
    if not rows_sorted_by_open_time:
        return annotations

    segment_id = compute_market_segment_id(
        provider=provider,
        market_type=market_type,
        symbol=symbol,
        interval=interval,
        first_open_time_ms=rows_sorted_by_open_time[0].open_time,
        multi_provider=multi_provider,
    )
    gap_before_flags = [False] * len(rows_sorted_by_open_time)
    gap_after_flags = [False] * len(rows_sorted_by_open_time)
    segment_ids = [segment_id] * len(rows_sorted_by_open_time)

    for i in range(1, len(rows_sorted_by_open_time)):
        previous_row = rows_sorted_by_open_time[i - 1]
        current_row = rows_sorted_by_open_time[i]
        expected_next = previous_row.open_time + interval_duration_ms
        if current_row.open_time != expected_next:
            gap_after_flags[i - 1] = True
            gap_before_flags[i] = True
            segment_id = compute_market_segment_id(
                provider=provider,
                market_type=market_type,
                symbol=symbol,
                interval=interval,
                first_open_time_ms=current_row.open_time,
                multi_provider=multi_provider,
            )
        segment_ids[i] = segment_id

    for i, row in enumerate(rows_sorted_by_open_time):
        annotations.append(
            RowGapAnnotation(
                source_row_id=row.source_row_id,
                market_segment_id=segment_ids[i],
                gap_before=gap_before_flags[i],
                gap_after=gap_after_flags[i],
                gap_detected=gap_before_flags[i] or gap_after_flags[i],
            )
        )
    return annotations
