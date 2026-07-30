"""Deterministic S7 incremental-rebuild and chronological-split helpers."""

from __future__ import annotations

from rcc002.s7.constants import INTERVAL_MILLISECONDS, MAX_HORIZON


def invalidation_start_index(
    changed_index: int,
    *,
    max_horizon: int = MAX_HORIZON,
) -> int:
    if (
        isinstance(changed_index, bool)
        or not isinstance(changed_index, int)
        or changed_index < 0
    ):
        raise ValueError("changed_index must be a non-negative integer")
    if (
        isinstance(max_horizon, bool)
        or not isinstance(max_horizon, int)
        or max_horizon < 1
    ):
        raise ValueError("max_horizon must be a positive integer")
    return max(0, changed_index - max_horizon)


def label_crosses_split(
    *,
    row_open_time: int,
    split_open_time: int,
    horizon_bars: int,
) -> bool:
    """Return true when t+h reaches or enters the following split."""

    for name, value in (
        ("row_open_time", row_open_time),
        ("split_open_time", split_open_time),
        ("horizon_bars", horizon_bars),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{name} must be an integer")
    if horizon_bars < 1:
        raise ValueError("horizon_bars must be positive")
    return (
        row_open_time + horizon_bars * INTERVAL_MILLISECONDS
        >= split_open_time
    )


__all__ = ["invalidation_start_index", "label_crosses_split"]
