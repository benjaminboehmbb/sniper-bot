"""Canonical grouped in-memory schema for RCC-002 S7 labels.

The physical logical schema adds 302 fields.  As in S3 and S4, this Python
representation groups the repeated per-horizon fields while
``flatten_s7_extension`` exposes the exact normative field expansion.
"""

from __future__ import annotations

import dataclasses
import math

from rcc002.s6.schema import S6Row
from rcc002.s7.constants import (
    HORIZON_BY_ID,
    HORIZON_IDS,
    HORIZON_LOCAL_FIELDS,
    LABEL_EXTENSION_FIELDS,
    LABEL_METADATA_FIELDS,
    LABEL_METADATA_VALUES,
    INVALIDATING_REASON_CODES,
    BarrierOutcome,
    expanded_horizon_field_name,
)
from rcc002.s7.reason_codes import normalize_reason_codes


@dataclasses.dataclass(frozen=True, slots=True)
class HorizonLabels:
    label_horizon_bars: int
    label_available_at: int | None

    fwd_cc_valid: bool
    fwd_cc_reason_codes: tuple[str, ...]
    fwd_cc_label_segment_id: str | None
    fwd_cc_long_ret: float | None
    fwd_cc_short_ret: float | None
    fwd_cc_log_ret: float | None
    fwd_cc_short_log_ret: float | None

    fwd_noc_valid: bool
    fwd_noc_reason_codes: tuple[str, ...]
    fwd_noc_label_segment_id: str | None
    fwd_noc_long_ret: float | None
    fwd_noc_short_ret: float | None
    fwd_noc_long_net_proxy_fee_rt_0004: float | None
    fwd_noc_short_net_proxy_fee_rt_0004: float | None

    fwd_excursion_valid: bool
    fwd_excursion_reason_codes: tuple[str, ...]
    fwd_excursion_label_segment_id: str | None
    fwd_long_mfe: float | None
    fwd_long_mae: float | None
    fwd_short_mfe: float | None
    fwd_short_mae: float | None
    fwd_long_mfe_first_bar: int | None
    fwd_long_mae_first_bar: int | None
    fwd_short_mfe_first_bar: int | None
    fwd_short_mae_first_bar: int | None

    label_cc_direction_valid: bool
    label_cc_direction_reason_codes: tuple[str, ...]
    label_cc_direction_segment_id: str | None
    label_cc_long_direction: int | None
    label_cc_short_direction: int | None

    label_noc_direction_valid: bool
    label_noc_direction_reason_codes: tuple[str, ...]
    label_noc_direction_segment_id: str | None
    label_noc_long_direction: int | None
    label_noc_short_direction: int | None
    label_noc_long_net_proxy_fee_rt_0004_direction: int | None
    label_noc_short_net_proxy_fee_rt_0004_direction: int | None

    barrier_valid: bool
    barrier_reason_codes: tuple[str, ...]
    barrier_label_segment_id: str | None
    barrier_long_outcome_tp050_sl020: BarrierOutcome
    barrier_short_outcome_tp050_sl020: BarrierOutcome
    barrier_long_first_hit_bar_tp050_sl020: int | None
    barrier_short_first_hit_bar_tp050_sl020: int | None
    barrier_long_first_hit_time_tp050_sl020: int | None
    barrier_short_first_hit_time_tp050_sl020: int | None

    def __post_init__(self) -> None:
        if tuple(field.name for field in dataclasses.fields(self)) != (
            HORIZON_LOCAL_FIELDS
        ):
            raise RuntimeError("HorizonLabels field order is not canonical")
        if (
            type(self.label_horizon_bars) is not int
            or not 1 <= int(self.label_horizon_bars) <= 1440
        ):
            raise ValueError("label_horizon_bars must be UInt16-like")
        self._validate_timestamp(
            "label_available_at", self.label_available_at
        )
        for family in (
            "fwd_cc",
            "fwd_noc",
            "fwd_excursion",
            "label_cc_direction",
            "label_noc_direction",
            "barrier",
        ):
            self._validate_family(family)
        self._validate_barrier_hits()
        self._validate_numeric_domains()

    @staticmethod
    def _validate_timestamp(name: str, value: int | None) -> None:
        if value is not None and (
            type(value) is not int
        ):
            raise ValueError(f"{name} must be an integer timestamp or None")

    def _validate_family(self, family: str) -> None:
        valid = getattr(self, f"{family}_valid")
        codes = getattr(self, f"{family}_reason_codes")
        segment = getattr(
            self,
            (
                f"{family}_label_segment_id"
                if family.startswith("fwd_") or family == "barrier"
                else f"{family}_segment_id"
            ),
        )
        if type(valid) is not bool:
            raise ValueError(f"{family}_valid must be Boolean")
        if not isinstance(codes, tuple):
            raise ValueError(f"{family}_reason_codes must be a tuple")
        if codes != normalize_reason_codes(codes):
            raise ValueError(f"{family}_reason_codes is not canonical")
        if segment is not None and (
            not isinstance(segment, str) or not segment
        ):
            raise ValueError(f"{family} segment id must be non-empty")
        if valid:
            if family != "barrier" and codes:
                raise ValueError(
                    f"valid {family} may not contain invalidity codes"
                )
            if family == "barrier" and (
                set(codes) & INVALIDATING_REASON_CODES
            ):
                raise ValueError(
                    "valid barrier cannot contain invalidating codes"
                )
        elif not codes:
            raise ValueError(f"invalid {family} requires a reason code")
        elif not (set(codes) & INVALIDATING_REASON_CODES):
            raise ValueError(
                f"invalid {family} requires an invalidating code"
            )

        value_fields = self._family_value_fields(family)
        values = tuple(getattr(self, name) for name in value_fields)
        if valid:
            if segment is None:
                raise ValueError(f"valid {family} requires segment id")
            if family == "barrier":
                outcomes = values[:2]
                if any(
                    outcome is BarrierOutcome.INVALID
                    for outcome in outcomes
                ):
                    raise ValueError(
                        "valid barrier cannot have INVALID outcome"
                    )
            elif any(value is None for value in values):
                raise ValueError(
                    f"valid {family} requires all family values"
                )
        elif family == "barrier":
            if values[:2] != (
                BarrierOutcome.INVALID,
                BarrierOutcome.INVALID,
            ) or any(value is not None for value in values[2:]):
                raise ValueError(
                    "invalid barrier requires INVALID outcomes and null hits"
                )
        elif any(value is not None for value in values):
            raise ValueError(
                f"invalid {family} requires null family values"
            )

    def _validate_barrier_hits(self) -> None:
        if not self.barrier_valid:
            return
        for direction in ("long", "short"):
            outcome = getattr(
                self,
                f"barrier_{direction}_outcome_tp050_sl020",
            )
            hit_bar = getattr(
                self,
                f"barrier_{direction}_first_hit_bar_tp050_sl020",
            )
            hit_time = getattr(
                self,
                f"barrier_{direction}_first_hit_time_tp050_sl020",
            )
            if outcome is BarrierOutcome.TIMEOUT:
                if hit_bar is not None or hit_time is not None:
                    raise ValueError(
                        "TIMEOUT requires null hit bar and hit time"
                    )
            elif hit_bar is None or hit_time is None:
                raise ValueError(
                    "a barrier hit requires hit bar and hit time"
                )

    @staticmethod
    def _family_value_fields(family: str) -> tuple[str, ...]:
        fields = {
            "fwd_cc": (
                "fwd_cc_long_ret",
                "fwd_cc_short_ret",
                "fwd_cc_log_ret",
                "fwd_cc_short_log_ret",
            ),
            "fwd_noc": (
                "fwd_noc_long_ret",
                "fwd_noc_short_ret",
                "fwd_noc_long_net_proxy_fee_rt_0004",
                "fwd_noc_short_net_proxy_fee_rt_0004",
            ),
            "fwd_excursion": (
                "fwd_long_mfe",
                "fwd_long_mae",
                "fwd_short_mfe",
                "fwd_short_mae",
                "fwd_long_mfe_first_bar",
                "fwd_long_mae_first_bar",
                "fwd_short_mfe_first_bar",
                "fwd_short_mae_first_bar",
            ),
            "label_cc_direction": (
                "label_cc_long_direction",
                "label_cc_short_direction",
            ),
            "label_noc_direction": (
                "label_noc_long_direction",
                "label_noc_short_direction",
                "label_noc_long_net_proxy_fee_rt_0004_direction",
                "label_noc_short_net_proxy_fee_rt_0004_direction",
            ),
            "barrier": (
                "barrier_long_outcome_tp050_sl020",
                "barrier_short_outcome_tp050_sl020",
                "barrier_long_first_hit_bar_tp050_sl020",
                "barrier_short_first_hit_bar_tp050_sl020",
                "barrier_long_first_hit_time_tp050_sl020",
                "barrier_short_first_hit_time_tp050_sl020",
            ),
        }
        return fields[family]

    def _validate_numeric_domains(self) -> None:
        for name in HORIZON_LOCAL_FIELDS:
            value = getattr(self, name)
            if name.startswith(("fwd_",)) and (
                name.endswith(("_ret", "_mfe", "_mae"))
                or "net_proxy" in name
                or "log_ret" in name
            ):
                if value is not None and (
                    type(value) not in (int, float)
                    or not math.isfinite(float(value))
                ):
                    raise ValueError(f"{name} must be finite or None")
            if (
                "direction" in name
                and not name.endswith(
                    ("valid", "reason_codes", "segment_id")
                )
                and value is not None
                and (
                    type(value) is not int
                    or int(value) not in (-1, 0, 1)
                )
            ):
                raise ValueError(f"{name} must be -1, 0, 1, or None")
            if "first_bar" in name and value is not None and (
                type(value) is not int
                or not 1 <= int(value) <= self.label_horizon_bars
            ):
                raise ValueError(f"{name} is outside 1...h")
            if "first_hit_time" in name:
                self._validate_timestamp(name, value)

        if self.fwd_excursion_valid:
            if (
                self.fwd_long_mfe < 0.0
                or self.fwd_short_mfe < 0.0
                or self.fwd_long_mae > 0.0
                or self.fwd_short_mae > 0.0
            ):
                raise ValueError("excursion signs violate the contract")


@dataclasses.dataclass(frozen=True)
class S7Row(S6Row):
    label_profile_id: str
    label_profile_version: str
    label_schema_id: str
    label_schema_version: str
    label_schema_ref: str
    horizon_registry_id: str
    horizon_registry_version: str
    cost_profile_id: str
    cost_profile_version: str
    barrier_profile_id: str
    barrier_profile_version: str
    label_reason_code_registry_version: str
    label_numeric_profile_id: str
    label_numeric_profile_version: str
    horizons: dict[str, HorizonLabels]

    def __post_init__(self) -> None:
        super().__post_init__()
        for name, expected in LABEL_METADATA_VALUES.items():
            if getattr(self, name) != expected:
                raise ValueError(f"{name} must equal {expected!r}")
        if not isinstance(self.horizons, dict):
            raise ValueError("horizons must be a canonical ordered dict")
        if tuple(self.horizons) != HORIZON_IDS:
            raise ValueError("horizons must contain the exact registry order")
        for horizon_id, labels in self.horizons.items():
            if not isinstance(labels, HorizonLabels):
                raise ValueError(
                    f"{horizon_id} must contain HorizonLabels"
                )
            if (
                labels.label_horizon_bars
                != HORIZON_BY_ID[horizon_id].bars
            ):
                raise ValueError(
                    f"{horizon_id} has the wrong horizon length"
                )


def flatten_s7_extension(row: S7Row) -> dict[str, object]:
    """Expand the grouped row to the exact 302-field logical S7 extension."""

    if not isinstance(row, S7Row):
        raise TypeError("row must be an S7Row")
    output: dict[str, object] = {
        name: getattr(row, name) for name in LABEL_METADATA_FIELDS
    }
    for horizon_id in HORIZON_IDS:
        labels = row.horizons[horizon_id]
        suffix = HORIZON_BY_ID[horizon_id].suffix
        for local_name in HORIZON_LOCAL_FIELDS:
            output[
                expanded_horizon_field_name(local_name, suffix)
            ] = getattr(labels, local_name)
    if tuple(output) != LABEL_EXTENSION_FIELDS:
        raise RuntimeError("expanded S7 field order is not canonical")
    return output


__all__ = ["HorizonLabels", "S7Row", "flatten_s7_extension"]
