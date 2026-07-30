"""Reason-code normalization for RCC-002 S7 label families."""

from __future__ import annotations

from collections.abc import Iterable

from rcc002.s7.constants import (
    REASON_CODE_PRIORITY,
    REASON_CODE_REGISTRY,
    ROW_REASON_CODES,
)


class LabelReasonCodeError(ValueError):
    """Raised for an unknown or stage-only row reason code."""


def validate_row_reason_code(code: str) -> str:
    if not isinstance(code, str) or not code:
        raise LabelReasonCodeError(
            "S7 reason codes must be non-empty strings"
        )
    if code not in REASON_CODE_REGISTRY:
        raise LabelReasonCodeError(f"unknown S7 reason code: {code}")
    if code not in ROW_REASON_CODES:
        raise LabelReasonCodeError(
            f"stage-only S7 reason code cannot occur on a row: {code}"
        )
    return code


def normalize_reason_codes(
    codes: Iterable[str] | None,
) -> tuple[str, ...]:
    if codes is None:
        return ()
    unique = {validate_row_reason_code(code) for code in codes}
    return tuple(sorted(unique, key=REASON_CODE_PRIORITY.__getitem__))


__all__ = [
    "LabelReasonCodeError",
    "normalize_reason_codes",
    "validate_row_reason_code",
]
