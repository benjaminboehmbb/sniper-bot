"""RCC_JSON_CANONICALIZATION_V1 helpers for RCC-002 S8_EXPORT.

Reuses the certified RFC 8785/JCS-compatible canonicalization already
established by ``rcc002.s0.source_identity.canonical_json_bytes`` (NFC
string normalization, UTF-8, sorted object keys, compact separators,
non-finite numbers forbidden) rather than duplicating it (Reproducibility
and Manifest Specification SS6.2). This module only adds the S8-specific
pieces the Reproducibility and Manifest Specification requires on top of
that: a SHA-256 helper, the canonical-decimal-string grammar (SS6.3), and
UTC timestamp formatting (SS6.8).
"""

from __future__ import annotations

import datetime
import decimal
import hashlib
import math

from rcc002.s0.source_identity import canonical_json_bytes
from rcc002.s8.reason_codes import CanonicalizationError


def sha256_hex(data: bytes) -> str:
    if not isinstance(data, (bytes, bytearray)):
        raise CanonicalizationError("sha256_hex requires bytes")
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: object) -> bytes:
    """RCC_JSON_CANONICALIZATION_V1 bytes for a canonicalizable value."""
    try:
        return canonical_json_bytes(value)
    except (TypeError, ValueError) as exc:
        raise CanonicalizationError(str(exc)) from exc


def canonical_sha256(value: object) -> str:
    """SHA-256 of the RCC_JSON_CANONICALIZATION_V1 bytes of ``value``."""
    return sha256_hex(canonical_bytes(value))


def _decimal_from(value: "decimal.Decimal | int | str") -> decimal.Decimal:
    if isinstance(value, bool):
        raise CanonicalizationError("a Boolean is not a canonical decimal")
    if isinstance(value, float):
        raise CanonicalizationError(
            "a binary float is not accepted as a canonical decimal input; "
            "pass a decimal.Decimal or a numeral string instead"
        )
    if isinstance(value, decimal.Decimal):
        return value
    if isinstance(value, int):
        return decimal.Decimal(value)
    if isinstance(value, str):
        try:
            return decimal.Decimal(value)
        except decimal.InvalidOperation as exc:
            raise CanonicalizationError(
                f"not a decimal numeral: {value!r}"
            ) from exc
    raise CanonicalizationError(
        f"unsupported canonical-decimal input type: {type(value)!r}"
    )


def format_canonical_decimal(value: "decimal.Decimal | int | str") -> str:
    """Canonical decimal string per Reproducibility and Manifest Spec SS6.3.

    Optional leading minus, at least one integer digit, an optional decimal
    point followed by one or more digits only when needed. No leading plus,
    no exponent, no unnecessary leading or trailing zeros; ``-0`` becomes
    ``0``.
    """
    dec = _decimal_from(value)
    if not dec.is_finite():
        raise CanonicalizationError(
            "NaN and Infinity are forbidden canonical decimal values"
        )
    sign, digits, exponent = dec.as_tuple()
    digit_str = "".join(str(d) for d in digits)
    if exponent >= 0:
        integer_part = digit_str + "0" * exponent
        frac_part = ""
    elif -exponent >= len(digit_str):
        integer_part = "0"
        frac_part = "0" * (-exponent - len(digit_str)) + digit_str
    else:
        split = len(digit_str) + exponent
        integer_part = digit_str[:split]
        frac_part = digit_str[split:]
    integer_part = integer_part.lstrip("0") or "0"
    frac_part = frac_part.rstrip("0")
    result = integer_part if not frac_part else f"{integer_part}.{frac_part}"
    if sign and result != "0":
        result = "-" + result
    return result


def format_utc_timestamp(moment: datetime.datetime) -> str:
    """ISO-8601 UTC timestamp with a literal ``Z`` suffix (SS6.8)."""
    if not isinstance(moment, datetime.datetime):
        raise CanonicalizationError("timestamp must be a datetime.datetime")
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise CanonicalizationError(
            "timestamp must be timezone-aware and UTC"
        )
    if moment.utcoffset() != datetime.timedelta(0):
        raise CanonicalizationError("timestamp must use a zero UTC offset")
    if moment.microsecond:
        return moment.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def reject_non_finite(value: object) -> None:
    """Explicitly reject NaN/Infinity wherever a raw float slips through."""
    if isinstance(value, float) and not math.isfinite(value):
        raise CanonicalizationError("non-finite float is forbidden")


__all__ = [
    "canonical_bytes",
    "canonical_sha256",
    "format_canonical_decimal",
    "format_utc_timestamp",
    "reject_non_finite",
    "sha256_hex",
]
