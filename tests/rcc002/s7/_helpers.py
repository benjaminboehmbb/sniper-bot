"""Deterministic S7 fixtures built from a canonical S6 row."""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from functools import lru_cache

from rcc002.s6.compute import compute_gates
from rcc002.s6.schema import S6Row
from tests.rcc002.s6._helpers import valid_s5_row


@lru_cache(maxsize=1)
def base_s6_row() -> S6Row:
    return compute_gates((valid_s5_row(),)).rows[0]


def make_s6_rows(
    prices: Sequence[float],
    *,
    opens: Sequence[float] | None = None,
    highs: Sequence[float] | None = None,
    lows: Sequence[float] | None = None,
    segment_ids: Sequence[str] | None = None,
    start_time: int = 1_800_000_000_000,
) -> tuple[S6Row, ...]:
    count = len(prices)
    opens = prices if opens is None else opens
    highs = prices if highs is None else highs
    lows = prices if lows is None else lows
    segment_ids = (
        ("segment-1",) * count
        if segment_ids is None
        else segment_ids
    )
    if not all(
        len(values) == count
        for values in (opens, highs, lows, segment_ids)
    ):
        raise ValueError("fixture sequences must have equal length")
    base = base_s6_row()
    rows: list[S6Row] = []
    for index in range(count):
        open_time = start_time + index * 60_000
        close_time = open_time + 59_999
        rows.append(
            dataclasses.replace(
                base,
                source_row_id=f"s7-row-{index}",
                open_time=open_time,
                close_time=close_time,
                gate_evaluated_at=close_time,
                open=float(opens[index]),
                high=float(highs[index]),
                low=float(lows[index]),
                close=float(prices[index]),
                market_segment_id=segment_ids[index],
            )
        )
    return tuple(rows)


def mark_quality_failed(
    row: S6Row,
    *,
    synthetic: bool = False,
) -> S6Row:
    return dataclasses.replace(
        row,
        quality_gate_pass=False,
        quality_is_synthetic=synthetic,
        quality_status="ERROR",
        quality_reason_codes=("DV_NUMERIC_PARSE_FAILED",),
        data_gate_pass=False,
        allow_long=False,
        allow_short=False,
        gate_state=type(row.gate_state).BLOCK_BOTH,
        gate_reason_codes_long=("GATE_DATA_QUALITY_FAILED",),
        gate_reason_codes_short=("GATE_DATA_QUALITY_FAILED",),
        gate_valid=True,
    )


__all__ = ["base_s6_row", "make_s6_rows", "mark_quality_failed"]
