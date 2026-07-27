"""S2 anomaly detection (Data Validation §13, "Anomalieerkennung").

§13.2 lists six SHOULD-level (not MUST) minimum flags. §13.3 requires
thresholds to be "robust und kausal berechnet", "pro Asset und Intervall
konfiguriert", with a disclosed warm-up period, "nicht aus dem späteren
Testzeitraum optimiert". §25.1 explicitly lists "statistische Schwellenwerte
für nicht destruktive Anomalieflags" as a still-open implementation
parameter. This module therefore requires the caller to supply every
threshold explicitly (`AnomalyThresholds` has no defaults) — it implements
only the mechanical comparison, not the statistical methodology or the
threshold values themselves, neither of which this implementation invents.

§13.1: "Anomalieerkennung dient der Untersuchung, nicht der stillen
Datenbereinigung." §13.3: "Anomalieflags dürfen die Originalwerte nicht
verändern." Accordingly, every function here only ever reports source_row_ids
to flag; it never modifies a row's OHLCV values.
"""

from __future__ import annotations

import dataclasses
from typing import Sequence


@dataclasses.dataclass(frozen=True)
class AnomalyThresholds:
    """All thresholds are required (no defaults) — see module docstring."""

    extreme_candle_return_abs: float  # |close/prev_close - 1| threshold
    extreme_high_low_range_abs: float  # (high-low)/close threshold
    extreme_volume_abs: float  # absolute volume threshold
    zero_volume_cluster_min_length: int  # consecutive zero-volume rows
    repeated_identical_ohlc_min_length: int  # consecutive identical-OHLC rows


@dataclasses.dataclass(frozen=True)
class AnomalyFindings:
    extreme_candle_return: frozenset[str]
    extreme_high_low_range: frozenset[str]
    extreme_volume: frozenset[str]
    zero_volume_cluster: frozenset[str]
    repeated_identical_ohlc: frozenset[str]
    partition_boundary_jump: frozenset[str]


def detect_anomalies(
    rows_sorted_by_open_time: Sequence,
    *,
    thresholds: AnomalyThresholds,
    gap_before_by_source_row_id: dict[str, bool],
) -> AnomalyFindings:
    """Evaluate all six §13.2 anomaly checks over one sorted row sequence.

    `rows_sorted_by_open_time` must expose `.source_row_id`, `.open`,
    `.high`, `.low`, `.close`, `.volume` (an `S1Row`/`S2Row`-shaped object).
    """
    extreme_return: set[str] = set()
    extreme_range: set[str] = set()
    extreme_volume: set[str] = set()
    zero_volume_cluster: set[str] = set()
    repeated_ohlc: set[str] = set()
    boundary_jump: set[str] = set()

    n = len(rows_sorted_by_open_time)

    for i, row in enumerate(rows_sorted_by_open_time):
        if row.close != 0 and row.high >= row.low:
            range_ratio = abs(row.high - row.low) / abs(row.close)
            if range_ratio > thresholds.extreme_high_low_range_abs:
                extreme_range.add(row.source_row_id)
        if abs(row.volume) > thresholds.extreme_volume_abs:
            extreme_volume.add(row.source_row_id)

        if i > 0:
            prev = rows_sorted_by_open_time[i - 1]
            if prev.close != 0:
                candle_return = row.close / prev.close - 1.0
                if abs(candle_return) > thresholds.extreme_candle_return_abs:
                    extreme_return.add(row.source_row_id)

        is_boundary = gap_before_by_source_row_id.get(row.source_row_id, False)
        if is_boundary and row.source_row_id in extreme_return | extreme_volume:
            boundary_jump.add(row.source_row_id)

    # Consecutive zero-volume clusters.
    run_start = None
    for i in range(n):
        if rows_sorted_by_open_time[i].volume == 0:
            if run_start is None:
                run_start = i
        else:
            if run_start is not None and i - run_start >= thresholds.zero_volume_cluster_min_length:
                for j in range(run_start, i):
                    zero_volume_cluster.add(rows_sorted_by_open_time[j].source_row_id)
            run_start = None
    if run_start is not None and n - run_start >= thresholds.zero_volume_cluster_min_length:
        for j in range(run_start, n):
            zero_volume_cluster.add(rows_sorted_by_open_time[j].source_row_id)

    # Consecutive identical-OHLC runs.
    run_start = None
    for i in range(n):
        if i == 0:
            run_start = 0
            continue
        prev = rows_sorted_by_open_time[i - 1]
        current = rows_sorted_by_open_time[i]
        same = (
            prev.open == current.open
            and prev.high == current.high
            and prev.low == current.low
            and prev.close == current.close
        )
        if not same:
            if run_start is not None and i - run_start >= thresholds.repeated_identical_ohlc_min_length:
                for j in range(run_start, i):
                    repeated_ohlc.add(rows_sorted_by_open_time[j].source_row_id)
            run_start = i
    if run_start is not None and n - run_start >= thresholds.repeated_identical_ohlc_min_length:
        for j in range(run_start, n):
            repeated_ohlc.add(rows_sorted_by_open_time[j].source_row_id)

    return AnomalyFindings(
        extreme_candle_return=frozenset(extreme_return),
        extreme_high_low_range=frozenset(extreme_range),
        extreme_volume=frozenset(extreme_volume),
        zero_volume_cluster=frozenset(zero_volume_cluster),
        repeated_identical_ohlc=frozenset(repeated_ohlc),
        partition_boundary_jump=frozenset(boundary_jump),
    )
