"""Canonical in-memory S6 gate row schema."""

from __future__ import annotations

import dataclasses
from numbers import Integral

from rcc002.s5.schema import S5Row
from rcc002.s6.constants import (
    ALLOWING_REASON_CODES,
    BLOCKING_REASON_CODES,
    GATE_PROFILE_IDS,
    GATE_PROFILE_VERSION,
    GATE_SCHEMA_ID,
    GATE_SCHEMA_REF,
    GATE_SCHEMA_VERSION,
    INVALIDATING_REASON_CODES,
    GateState,
)
from rcc002.s6.formulas import derive_gate_state
from rcc002.s6.reason_codes import normalize_direction_reason_codes


@dataclasses.dataclass(frozen=True)
class S6Row(S5Row):
    allow_long: bool
    allow_short: bool
    data_gate_pass: bool
    gate_state: GateState
    gate_reason_codes_long: tuple[str, ...]
    gate_reason_codes_short: tuple[str, ...]
    gate_profile_id: str
    gate_profile_version: str
    gate_schema_id: str
    gate_schema_version: str
    gate_schema_ref: str
    gate_valid: bool
    gate_evaluated_at: int

    def __post_init__(self) -> None:
        super().__post_init__()
        for name in (
            "allow_long",
            "allow_short",
            "data_gate_pass",
            "gate_valid",
        ):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be Boolean")
        if not isinstance(self.gate_state, GateState):
            raise ValueError("gate_state must be a GateState")
        if self.gate_profile_id not in GATE_PROFILE_IDS:
            raise ValueError("gate_profile_id is not registered")
        metadata = {
            "gate_profile_version": GATE_PROFILE_VERSION,
            "gate_schema_id": GATE_SCHEMA_ID,
            "gate_schema_version": GATE_SCHEMA_VERSION,
            "gate_schema_ref": GATE_SCHEMA_REF,
        }
        for name, expected in metadata.items():
            if getattr(self, name) != expected:
                raise ValueError(f"{name} must equal {expected!r}")
        if (
            isinstance(self.gate_evaluated_at, bool)
            or not isinstance(self.gate_evaluated_at, Integral)
        ):
            raise ValueError(
                "gate_evaluated_at must be an integer UTC timestamp"
            )
        if int(self.gate_evaluated_at) != self.close_time:
            raise ValueError("gate_evaluated_at must equal close_time")

        self._validate_reason_codes()
        self._validate_gate_truth()

    def _validate_reason_codes(self) -> None:
        for name, direction in (
            ("gate_reason_codes_long", "LONG"),
            ("gate_reason_codes_short", "SHORT"),
        ):
            codes = getattr(self, name)
            if not isinstance(codes, tuple):
                raise ValueError(f"{name} must be a tuple")
            if codes != normalize_direction_reason_codes(
                codes, direction=direction
            ):
                raise ValueError(f"{name} is not canonical")

    def _validate_gate_truth(self) -> None:
        expected_state = derive_gate_state(
            gate_valid=self.gate_valid,
            allow_long=self.allow_long,
            allow_short=self.allow_short,
        )
        if self.gate_state is not expected_state:
            raise ValueError("gate_state contradicts gate truth rule")
        if self.data_gate_pass != self.quality_gate_pass:
            raise ValueError(
                "data_gate_pass must equal quality_gate_pass"
            )

        long_codes = set(self.gate_reason_codes_long)
        short_codes = set(self.gate_reason_codes_short)
        if not self.data_gate_pass:
            expected = {"GATE_DATA_QUALITY_FAILED"}
            if (
                not self.gate_valid
                or self.gate_state is not GateState.BLOCK_BOTH
                or long_codes != expected
                or short_codes != expected
            ):
                raise ValueError(
                    "failed data gate must be a valid exact BLOCK_BOTH"
                )
            return

        if self.gate_valid:
            if (
                long_codes & INVALIDATING_REASON_CODES
                or short_codes & INVALIDATING_REASON_CODES
            ):
                raise ValueError(
                    "valid gate cannot contain invalidating reasons"
                )
        elif (
            not long_codes
            or not short_codes
            or not (
                long_codes & INVALIDATING_REASON_CODES
                and short_codes & INVALIDATING_REASON_CODES
            )
        ):
            raise ValueError(
                "invalid gate requires invalidating reasons in both lists"
            )

        self._validate_direction_truth(
            allow=self.allow_long, codes=long_codes
        )
        self._validate_direction_truth(
            allow=self.allow_short, codes=short_codes
        )

    @staticmethod
    def _validate_direction_truth(
        *,
        allow: bool,
        codes: set[str],
    ) -> None:
        allowing = codes & ALLOWING_REASON_CODES
        blocking = codes & BLOCKING_REASON_CODES
        invalidating = codes & INVALIDATING_REASON_CODES
        if allow:
            if len(allowing) != 1 or blocking or invalidating:
                raise ValueError(
                    "an allowed direction requires exactly one allow reason"
                )
        elif allowing:
            raise ValueError(
                "a blocked direction cannot contain an allow reason"
            )


__all__ = ["S6Row"]
