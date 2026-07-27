"""Canonical in-memory schema for RCC-002 S4 signal transformation.

The normative physical S4 schema preserves every S3 field unchanged and adds:

- five S4 metadata fields;
- 24 registered S4 base fields;
- immediately after each base field, ``y_valid`` and ``y_reason_codes``.

This module represents each physical base-field group as one ``SignalField``
object and stores the groups in canonical ``SIGNAL_BASE_FIELDS`` order. This
matches the established grouped representation used by ``rcc002.s3.schema``
without changing the normative physical schema.
"""

from __future__ import annotations

import dataclasses
import math
from numbers import Integral, Real

from rcc002.s3.schema import S3Row
from rcc002.s4.constants import (
    FIELD_DEFINITIONS,
    SIGNAL_BASE_FIELDS,
    SIGNAL_METADATA_VALUES,
)
from rcc002.s4.reason_codes import (
    normalize_reason_codes,
    reason_codes_are_invalidating,
)


@dataclasses.dataclass(frozen=True, slots=True)
class SignalField:
    """One canonical S4 field group: ``y``, ``y_valid``, reason codes."""

    value: int | float | None
    valid: bool
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.valid) is not bool:
            raise ValueError("valid must be a non-null Boolean")

        if not isinstance(self.reason_codes, tuple):
            raise ValueError(
                "reason_codes must be an ordered tuple, never None"
            )

        normalized_codes = normalize_reason_codes(self.reason_codes)

        if self.reason_codes != normalized_codes:
            raise ValueError(
                "reason_codes must be deduplicated and in canonical order"
            )

        if self.valid:
            if self.value is None:
                raise ValueError(
                    "a valid S4 signal field cannot have value=None"
                )

            if reason_codes_are_invalidating(self.reason_codes):
                raise ValueError(
                    "a valid S4 field cannot contain an invalidating "
                    "reason code"
                )
        elif self.value is not None:
            raise ValueError(
                "an invalid S4 signal field must have value=None"
            )


@dataclasses.dataclass(frozen=True)
class S4Row(S3Row):
    """One canonical RCC-002 S4_SIGNALS row."""

    # S4 metadata
    signal_profile_id: str
    signal_profile_version: str
    signal_schema_id: str
    signal_schema_version: str
    signal_schema_ref: str

    # S4 groups in SIGNAL_BASE_FIELDS order
    signals: dict[str, SignalField]

    def __post_init__(self) -> None:
        super().__post_init__()

        self._validate_metadata()
        self._validate_signal_registry()
        self._validate_signal_values()

    def _validate_metadata(self) -> None:
        for field_name, expected_value in SIGNAL_METADATA_VALUES.items():
            actual_value = getattr(self, field_name)

            if actual_value != expected_value:
                raise ValueError(
                    f"{field_name} must equal {expected_value!r}; "
                    f"received {actual_value!r}"
                )

    def _validate_signal_registry(self) -> None:
        if not isinstance(self.signals, dict):
            raise ValueError(
                "signals must be a dict in canonical field order"
            )

        if tuple(self.signals) != SIGNAL_BASE_FIELDS:
            raise ValueError(
                "signals must contain exactly the 24 registered S4 fields "
                "in canonical order"
            )

        for field_name, field_value in self.signals.items():
            if not isinstance(field_value, SignalField):
                raise ValueError(
                    f"{field_name} must contain a SignalField instance"
                )

    def _validate_signal_values(self) -> None:
        for field_name in SIGNAL_BASE_FIELDS:
            field = self.signals[field_name]
            definition = FIELD_DEFINITIONS[field_name]

            if not field.valid:
                continue

            value = field.value

            if value is None:
                raise ValueError(
                    f"{field_name}: valid field unexpectedly has no value"
                )

            if definition.allowed_discrete_values is not None:
                if isinstance(value, bool) or not isinstance(value, Integral):
                    raise ValueError(
                        f"{field_name} must contain an integer discrete value"
                    )

                int_value = int(value)

                if int_value not in definition.allowed_discrete_values:
                    raise ValueError(
                        f"{field_name}={int_value} is outside its registered "
                        "discrete domain"
                    )

                continue

            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError(
                    f"{field_name} must contain a real continuous value"
                )

            float_value = float(value)

            if not math.isfinite(float_value):
                raise ValueError(
                    f"{field_name} must contain a finite value"
                )

            if not (
                definition.minimum
                <= float_value
                <= definition.maximum
            ):
                raise ValueError(
                    f"{field_name}={float_value!r} is outside the "
                    f"registered range [{definition.minimum}, "
                    f"{definition.maximum}]"
                )


def make_signal_field(
    *,
    value: int | float | None,
    valid: bool,
    reason_codes: tuple[str, ...] = (),
) -> SignalField:
    """Construct one validated S4 signal field."""

    return SignalField(
        value=value,
        valid=valid,
        reason_codes=normalize_reason_codes(reason_codes),
    )


def make_empty_signal_map() -> dict[str, SignalField]:
    """Create a canonical all-invalid S4 signal map.

    This helper is intended for controlled fail-closed construction. The
    caller must replace or assign the required reason codes before publishing
    a row if the applicable specification rule requires one.
    """

    return {
        field_name: SignalField(
            value=None,
            valid=False,
            reason_codes=(),
        )
        for field_name in SIGNAL_BASE_FIELDS
    }


__all__ = [
    "SignalField",
    "S4Row",
    "make_signal_field",
    "make_empty_signal_map",
]
