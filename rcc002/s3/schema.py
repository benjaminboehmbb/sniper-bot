"""The canonical S3 row schema.

Transcribed from Indicator Specification §26 (Ausgabevertrag). Every one of
the 22 canonical indicator fields (§5) shares the identical companion-field
shape (`x`, `x_valid`, `x_warmup_complete`, `x_reason_codes`); rather than
declaring 88 flat dataclass fields, this module represents them as an
ordered `dict[str, IndicatorField]` keyed by the allowlist field name in
`rcc002.s3.constants.INDICATOR_FIELD_ALLOWLIST` order (Python dicts preserve
insertion order) — the logical schema (§26.1/§26.3) is unchanged; this is
only this implementation's in-memory representation, the same kind of
representational choice already made for `quality_reason_codes` (a tuple,
not one boolean field per possible code).
"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class IndicatorField:
    """One canonical indicator field group: `x`, `x_valid`,
    `x_warmup_complete`, `x_reason_codes` (§5, §20.1, §20.2)."""

    value: float | None
    valid: bool
    warmup_complete: bool
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reason_codes, tuple):
            raise ValueError("reason_codes must be an (ordered) tuple, never None")
        if self.valid and self.value is None:
            raise ValueError("a valid indicator field cannot have value=None")
        if not self.valid and self.value is not None:
            raise ValueError("an invalid indicator field must have value=None (§3.5)")


@dataclasses.dataclass(frozen=True)
class S3Row:
    """One canonical S3_INDICATORS row (Indicator Specification §26.1)."""

    # --- S2 fields, unchanged (Data Validation §15) ---
    source_snapshot_id: str
    source_row_id: str
    provider: str
    market_type: str
    symbol: str
    interval: str
    open_time: int
    close_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    market_segment_id: str
    quality_is_observed: bool
    quality_is_synthetic: bool
    quality_has_source_conflict: bool
    quality_gap_before: bool
    quality_gap_after: bool
    quality_timestamp_valid: bool
    quality_ohlc_valid: bool
    quality_volume_valid: bool
    quality_market_values_valid: bool
    quality_status: str
    quality_reason_codes: tuple[str, ...]
    quality_rule_version: str
    quality_gate_pass: bool

    # --- S3 metadata (§26.3, columns 2-6) ---
    indicator_profile_id: str
    indicator_profile_version: str
    indicator_schema_id: str
    indicator_schema_version: str
    indicator_segment_id: str

    # --- Indicator groups, in allowlist order (§5, §26.3 column 7) ---
    indicators: dict[str, IndicatorField]

    def __post_init__(self) -> None:
        from rcc002.s3.constants import INDICATOR_FIELD_ALLOWLIST

        if set(self.indicators) != set(INDICATOR_FIELD_ALLOWLIST):
            raise ValueError(
                "indicators must contain exactly the certified allowlist fields"
            )
