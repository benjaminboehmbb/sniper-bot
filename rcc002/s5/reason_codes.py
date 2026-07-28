"""Reason-code validation and canonical ordering for RCC-002 S5."""

from __future__ import annotations

from collections.abc import Iterable

from rcc002.s5.constants import (
    REASON_CODE_PRIORITY,
    REASON_CODE_REGISTRY,
)


class RegimeReasonCodeError(ValueError):
    """Raised for an invalid or unregistered S5 reason code."""


def validate_reason_code(code: str) -> str:
    if not isinstance(code, str) or not code:
        raise RegimeReasonCodeError(
            "S5 reason codes must be non-empty strings"
        )
    if code not in REASON_CODE_REGISTRY:
        raise RegimeReasonCodeError(
            f"Unknown S5 reason code: {code}"
        )
    return code


def normalize_reason_codes(
    codes: Iterable[str] | None,
) -> tuple[str, ...]:
    if codes is None:
        return ()
    unique = {validate_reason_code(code) for code in codes}
    return tuple(sorted(unique, key=REASON_CODE_PRIORITY.__getitem__))


__all__ = [
    "RegimeReasonCodeError",
    "normalize_reason_codes",
    "validate_reason_code",
]
