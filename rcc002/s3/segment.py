"""S3 `indicator_segment_id` formation.

Transcribed from Indicator Specification §21.2. A new `indicator_segment_id`
begins at the first row of each `market_segment_id`, whenever
`quality_gate_pass` changes relative to the previous row, or after an
explicit recursive state reset. This implementation covers full serial
(non-incremental) builds only; the explicit-state-reset trigger is exposed
as a parameter for a future incremental-build caller and is always `False`
in a full serial build (see `rcc002.s3.compute` module docstring for the
disclosed state-snapshot-continuation scope boundary).
"""

from __future__ import annotations

import dataclasses
import hashlib

from rcc002.s3.constants import (
    INDICATOR_PROFILE_ID,
    INDICATOR_PROFILE_VERSION,
    INDICATOR_SEGMENT_PROFILE_ID,
    INDICATOR_SEGMENT_PROFILE_VERSION,
)


def compute_indicator_segment_id(
    *, market_segment_id: str, first_open_time_ms: int, quality_gate_pass: bool
) -> str:
    """§21.2: deterministic derivation, no random UUID."""
    canonical_string = "|".join(
        [
            market_segment_id,
            str(first_open_time_ms),
            str(quality_gate_pass),
            INDICATOR_PROFILE_ID,
            INDICATOR_PROFILE_VERSION,
            INDICATOR_SEGMENT_PROFILE_ID,
            INDICATOR_SEGMENT_PROFILE_VERSION,
        ]
    )
    digest = hashlib.sha256(canonical_string.encode("utf-8")).hexdigest()
    return f"{INDICATOR_SEGMENT_PROFILE_ID}:{INDICATOR_SEGMENT_PROFILE_VERSION}:{digest}"


@dataclasses.dataclass(frozen=True)
class IndicatorSegment:
    """One maximal contiguous run of rows sharing exactly one
    `market_segment_id` and constant `quality_gate_pass` (§21.2)."""

    indicator_segment_id: str
    row_indices: tuple[int, ...]  # positions into the caller's row list
    quality_gate_pass: bool


def split_into_indicator_segments(
    market_segment_ids: list[str],
    quality_gate_passes: list[bool],
    open_times: list[int],
    *,
    explicit_state_resets: list[bool] | None = None,
) -> list[IndicatorSegment]:
    """Partition one already-time-sorted row sequence into indicator
    segments per §21.2's three triggers."""
    n = len(market_segment_ids)
    if n == 0:
        return []
    resets = explicit_state_resets or [False] * n

    segments: list[IndicatorSegment] = []
    start = 0
    for i in range(1, n + 1):
        boundary = (
            i == n
            or market_segment_ids[i] != market_segment_ids[start]
            or quality_gate_passes[i] != quality_gate_passes[start]
            or resets[i]
        )
        if boundary:
            segment_id = compute_indicator_segment_id(
                market_segment_id=market_segment_ids[start],
                first_open_time_ms=open_times[start],
                quality_gate_pass=quality_gate_passes[start],
            )
            segments.append(
                IndicatorSegment(
                    indicator_segment_id=segment_id,
                    row_indices=tuple(range(start, i)),
                    quality_gate_pass=quality_gate_passes[start],
                )
            )
            start = i
    return segments
