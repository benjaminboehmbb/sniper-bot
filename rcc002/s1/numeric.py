"""S1 numeric field parsing.

Transcribed from RCC_002_DATA_VALIDATION_2026-07-23.md §7.2 (Numerisches
Parsing): numeric fields MUST be read without locale-dependent ambiguity,
recognize NaN/+Inf/-Inf, report invalid strings as a parsing error, and be
converted to the canonical type without prior rounding. §7.2 itself states a
parsing error in a mandatory OHLCV field is CRITICAL; §14.1 states the same
CRITICAL severity applies more broadly to nulls/invalid values in
"Primärschlüssel-, Zeit- oder OHLCV-Pflichtfeldern" (primary-key, time, or
OHLCV mandatory fields) — so a parsing failure in the mandatory `open_time`
field is CRITICAL for the same reason, even though it is a time field, not
an OHLCV field.
"""

from __future__ import annotations

from rcc002.reason_codes import REASON_CODE_SEVERITY, Severity

OHLCV_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {"open", "high", "low", "close", "volume"}
)

# §14.1's broader CRITICAL category: primary-key, time, or OHLCV mandatory
# fields. `market_type`/`symbol`/`interval` (primary-key fields) are strings,
# not parsed through this numeric module, so are not listed here.
CRITICAL_NUMERIC_FIELDS: frozenset[str] = OHLCV_REQUIRED_FIELDS | {
    "open_time",
    "close_time",
}

_TIME_FIELDS: frozenset[str] = frozenset({"open_time", "close_time"})


def _reason_code_for_field(field_name: str) -> str:
    """Which §16.2 reason code a parsing failure on this field corresponds to."""
    return "DV_PARSE_TIMESTAMP_FAILED" if field_name in _TIME_FIELDS else "DV_PARSE_NUMERIC_FAILED"


class NumericParsingError(ValueError):
    """A numeric parsing failure for a mandatory field (§7.2, §14.1).

    `reason_code` is `DV_PARSE_TIMESTAMP_FAILED` for `open_time`/`close_time`,
    else `DV_PARSE_NUMERIC_FAILED` (§16.2). `critical` is True exactly when
    the field is one of §14.1's mandatory primary-key/time/OHLCV fields *and*
    the corresponding reason code's registered severity
    (`rcc002.reason_codes.REASON_CODE_SEVERITY`) is `CRITICAL` — reconciled
    against the central registry rather than hardcoded locally, so the two
    can never silently drift apart.
    """

    def __init__(self, field_name: str, raw_value: str) -> None:
        self.field_name = field_name
        self.raw_value = raw_value
        self.reason_code = _reason_code_for_field(field_name)
        self.critical = (
            field_name in CRITICAL_NUMERIC_FIELDS
            and REASON_CODE_SEVERITY[self.reason_code] is Severity.CRITICAL
        )
        severity = "CRITICAL" if self.critical else "ERROR"
        super().__init__(
            f"{severity}: could not parse {field_name!r} as a numeric "
            f"value: {raw_value!r}"
        )


def parse_numeric_field(field_name: str, raw_value: str) -> float:
    """Parse one numeric field per Data Validation §7.2.

    `float()` in Python is locale-independent (always uses `.` as the
    decimal separator, never a thousands separator), satisfies "ohne
    localeabhängige Mehrdeutigkeit gelesen werden", and recognizes
    "nan"/"inf"/"-inf"/"infinity"/"-infinity" case-insensitively, satisfying
    "`NaN`, `+Inf` und `-Inf` erkennen". It performs no rounding.
    """
    stripped = raw_value.strip()
    try:
        return float(stripped)
    except ValueError as exc:
        raise NumericParsingError(field_name, raw_value) from exc


def parse_integer_field(field_name: str, raw_value: str) -> int:
    """Parse one integer (epoch-millisecond timestamp) field.

    Same §7.2 discipline as parse_numeric_field, applied to the integer
    timestamp fields (`open_time`, `close_time`) rather than the float
    OHLCV fields.
    """
    stripped = raw_value.strip()
    try:
        return int(stripped)
    except ValueError as exc:
        raise NumericParsingError(field_name, raw_value) from exc
