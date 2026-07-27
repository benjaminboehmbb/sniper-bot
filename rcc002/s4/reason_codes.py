"""Reason-code handling for RCC-002 S4 signal transformation."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Final

from rcc002.s4.constants import (
    REASON_CODE_PRIORITY,
    REASON_CODE_REGISTRY,
    REASON_CODE_REGISTRY_VERSION,
)


class SignalReasonCodeError(ValueError):
    """Raised when an unknown or invalid S4 reason code is supplied."""


def validate_reason_code(code: str) -> str:
    """Validate and return one registered S4 reason code."""

    if not isinstance(code, str):
        raise SignalReasonCodeError(
            "S4 reason codes must be strings; "
            f"received {type(code).__name__}."
        )

    if not code:
        raise SignalReasonCodeError(
            "S4 reason codes must not be empty."
        )

    if code not in REASON_CODE_REGISTRY:
        raise SignalReasonCodeError(
            f"Unknown S4 reason code: {code}"
        )

    return code


def normalize_reason_codes(
    codes: Iterable[str] | None,
) -> tuple[str, ...]:
    """Validate, deduplicate, and normatively order reason codes."""

    if codes is None:
        return ()

    unique_codes = {
        validate_reason_code(code)
        for code in codes
    }

    return tuple(
        sorted(
            unique_codes,
            key=REASON_CODE_PRIORITY.__getitem__,
        )
    )


@dataclass(frozen=True, slots=True)
class SignalReasonCodes:
    """Immutable, validated, normatively ordered S4 reason codes."""

    values: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "values",
            normalize_reason_codes(self.values),
        )

    def __bool__(self) -> bool:
        return bool(self.values)

    def __contains__(self, code: object) -> bool:
        return code in self.values

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def add(self, *codes: str) -> SignalReasonCodes:
        """Return a new collection containing additional codes."""

        return SignalReasonCodes((*self.values, *codes))

    def merge(
        self,
        *others: SignalReasonCodes | Iterable[str],
    ) -> SignalReasonCodes:
        """Return the ordered union with other collections."""

        combined: list[str] = list(self.values)

        for other in others:
            if isinstance(other, SignalReasonCodes):
                combined.extend(other.values)
            else:
                combined.extend(other)

        return SignalReasonCodes(tuple(combined))

    def has(self, code: str) -> bool:
        """Return whether the collection contains a registered code."""

        validate_reason_code(code)
        return code in self.values

    def is_invalidating(self) -> bool:
        """Return whether any reason code invalidates the signal."""

        return any(
            REASON_CODE_REGISTRY[code].invalidating
            for code in self.values
        )

    def as_tuple(self) -> tuple[str, ...]:
        """Return the canonical immutable representation."""

        return self.values

    def as_list(self) -> list[str]:
        """Return a serialization-friendly ordered list."""

        return list(self.values)


EMPTY_SIGNAL_REASON_CODES: Final[SignalReasonCodes] = SignalReasonCodes()


def make_reason_codes(*codes: str) -> SignalReasonCodes:
    """Construct an immutable reason-code collection."""

    return SignalReasonCodes(codes)


def merge_reason_codes(
    *collections: SignalReasonCodes | Iterable[str] | None,
) -> SignalReasonCodes:
    """Merge multiple optional reason-code collections."""

    combined: list[str] = []

    for collection in collections:
        if collection is None:
            continue

        if isinstance(collection, SignalReasonCodes):
            combined.extend(collection.values)
        else:
            combined.extend(collection)

    return SignalReasonCodes(tuple(combined))


def reason_codes_are_invalidating(
    codes: SignalReasonCodes | Iterable[str] | None,
) -> bool:
    """Return whether the supplied codes contain an invalidating code."""

    if isinstance(codes, SignalReasonCodes):
        normalized = codes
    else:
        normalized = SignalReasonCodes(
            tuple(codes) if codes is not None else ()
        )

    return normalized.is_invalidating()


def assert_reason_code_registry_consistent() -> None:
    """Verify internal consistency of the normative registry."""

    if not REASON_CODE_REGISTRY_VERSION:
        raise RuntimeError(
            "S4 reason-code registry version must not be empty."
        )

    registered_codes = tuple(REASON_CODE_REGISTRY)
    priority_codes = tuple(REASON_CODE_PRIORITY)

    if registered_codes != priority_codes:
        raise RuntimeError(
            "S4 reason-code registry and priority registry differ."
        )

    priorities = tuple(REASON_CODE_PRIORITY.values())

    if priorities != tuple(sorted(priorities)):
        raise RuntimeError(
            "S4 reason-code priorities are not ordered."
        )

    if len(priorities) != len(set(priorities)):
        raise RuntimeError(
            "S4 reason-code priorities are not unique."
        )

    for code, definition in REASON_CODE_REGISTRY.items():
        if definition.code != code:
            raise RuntimeError(
                f"S4 reason-code key mismatch for {code}."
            )

        if definition.priority != REASON_CODE_PRIORITY[code]:
            raise RuntimeError(
                f"S4 reason-code priority mismatch for {code}."
            )

        if not definition.description:
            raise RuntimeError(
                f"S4 reason-code description missing for {code}."
            )


assert_reason_code_registry_consistent()


__all__ = [
    "SignalReasonCodeError",
    "SignalReasonCodes",
    "EMPTY_SIGNAL_REASON_CODES",
    "validate_reason_code",
    "normalize_reason_codes",
    "make_reason_codes",
    "merge_reason_codes",
    "reason_codes_are_invalidating",
    "assert_reason_code_registry_consistent",
]
