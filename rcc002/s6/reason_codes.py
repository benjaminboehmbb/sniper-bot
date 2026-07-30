"""Reason-code validation and ordering for RCC-002 S6."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from rcc002.s6.constants import (
    LONG_REASON_CODES,
    NEUTRAL_REASON_CODES,
    REASON_CODE_PRIORITY,
    REASON_CODE_REGISTRY,
    SHORT_REASON_CODES,
)


GateDirection = Literal["LONG", "SHORT"]


class GateReasonCodeError(ValueError):
    """Raised for an invalid or directionally misplaced S6 reason code."""


def validate_reason_code(code: str) -> str:
    if not isinstance(code, str) or not code:
        raise GateReasonCodeError(
            "S6 reason codes must be non-empty strings"
        )
    if code not in REASON_CODE_REGISTRY:
        raise GateReasonCodeError(f"Unknown S6 reason code: {code}")
    return code


def normalize_reason_codes(
    codes: Iterable[str] | None,
) -> tuple[str, ...]:
    if codes is None:
        return ()
    unique = {validate_reason_code(code) for code in codes}
    return tuple(sorted(unique, key=REASON_CODE_PRIORITY.__getitem__))


def normalize_direction_reason_codes(
    codes: Iterable[str] | None,
    *,
    direction: GateDirection,
) -> tuple[str, ...]:
    normalized = normalize_reason_codes(codes)
    allowed = (
        NEUTRAL_REASON_CODES | LONG_REASON_CODES
        if direction == "LONG"
        else NEUTRAL_REASON_CODES | SHORT_REASON_CODES
    )
    misplaced = set(normalized) - allowed
    if misplaced:
        raise GateReasonCodeError(
            f"{direction} reason list contains directionally invalid codes: "
            f"{sorted(misplaced)!r}"
        )
    return normalized


__all__ = [
    "GateDirection",
    "GateReasonCodeError",
    "normalize_direction_reason_codes",
    "normalize_reason_codes",
    "validate_reason_code",
]
