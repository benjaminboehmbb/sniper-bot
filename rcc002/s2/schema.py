"""The canonical S2 row schema.

Transcribed from RCC_002_DATA_VALIDATION_2026-07-23.md §15 ("Qualitätsfelder"):
"S2 führt sämtliche kanonischen S1-Felder und den vollständigen
Primärschlüssel unverändert weiter. Die nachfolgenden Qualitätsfelder werden
ausschließlich ergänzt."
"""

from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class S2Row:
    """One canonical S2_VALIDATED row (Data Validation §15).

    All 15 S1 fields are carried through unchanged (byte-identical values,
    same types); `quality_*` fields are additive per §15's own statement
    that S2 "ausschließlich ergänzt" (only adds) fields.
    """

    # --- S1 fields, unchanged (Data Pipeline §7.2 / Data Validation §7.1) ---
    source_snapshot_id: str
    source_row_id: str
    source_file_ordinal: int
    original_record_index: int
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

    # --- S2 quality fields (Data Validation §15) ---
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
    quality_status: str  # "PASS" | "WARN" | "ERROR" | "CRITICAL"
    quality_reason_codes: tuple[str, ...]  # never None; empty tuple if none active
    quality_rule_version: str
    quality_gate_pass: bool

    def __post_init__(self) -> None:
        if self.quality_status not in ("PASS", "WARN", "ERROR", "CRITICAL"):
            raise ValueError(
                f"quality_status must be one of PASS/WARN/ERROR/CRITICAL, "
                f"got {self.quality_status!r}"
            )
        if not isinstance(self.quality_reason_codes, tuple):
            raise ValueError("quality_reason_codes must be an (ordered) tuple, never None")
