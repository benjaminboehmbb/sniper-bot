"""S3 recursive-indicator state snapshot.

Transcribed from Indicator Specification §22.3 (logical state contract) and
§22.4 (state safety checks). Scope note: this module implements the state
*contract* (the snapshot's shape and checksum) as required by §26.1's output
contract and §31.1's readiness criteria. It does NOT implement the
incremental-build continuation *mechanism* (§22.4's safety-check-driven
resume/abort flow) — this initial implementation computes full serial
builds only, so `IND_STATE_MISSING`/`IND_STATE_MISMATCH`/`IND_PROFILE_
MISMATCH`/`IND_SCHEMA_MISMATCH` are registered (see `rcc002.s3.reason_codes`)
but not reachable yet; incremental-build support is a disclosed, deferred
extension, not a silently-skipped requirement.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json

from rcc002.s3.constants import (
    INDICATOR_PROFILE_ID,
    INDICATOR_PROFILE_VERSION,
    INDICATOR_STATE_SCHEMA_ID,
    INDICATOR_STATE_SCHEMA_REF,
    INDICATOR_STATE_SCHEMA_VERSION,
)


@dataclasses.dataclass(frozen=True)
class IndicatorStateSnapshot:
    """§22.3's logical state contract, for one completed partition."""

    last_canonical_key: tuple[object, ...]
    market_segment_id: str
    indicator_segment_id: str
    indicator_profile_id: str
    indicator_profile_version: str
    ema_states: dict[str, float]  # e.g. "ema_close_50", "ema_fast_12", "ema_slow_26", "macd_signal_9"
    rsi_avg_gain: float | None
    rsi_avg_loss: float | None
    atr_state: float | None
    obv_state: float | None
    adx_tr_sum: float | None
    adx_plus_dm_sum: float | None
    adx_minus_dm_sum: float | None
    adx_state: float | None
    previous_ohlc: dict[str, float]  # e.g. "close", "high", "low" of the last row
    warmup_buffers: dict[str, tuple[float, ...]]
    warmup_counters: dict[str, int]
    indicator_state_schema_id: str = INDICATOR_STATE_SCHEMA_ID
    indicator_state_schema_version: str = INDICATOR_STATE_SCHEMA_VERSION
    indicator_state_schema_ref: str = INDICATOR_STATE_SCHEMA_REF
    checksum: str = ""

    def with_checksum(self) -> "IndicatorStateSnapshot":
        return dataclasses.replace(self, checksum=compute_state_checksum(self))


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def compute_state_checksum(state: IndicatorStateSnapshot) -> str:
    """Implementation-owned, versioned checksum profile
    (`RCC002_S3_STATE_CHECKSUM_V1`, disclosed here — not certified normative
    text): SHA-256 over a canonical (sorted-key) JSON representation of every
    state field except `checksum` itself.
    """
    payload = dataclasses.asdict(state)
    payload.pop("checksum", None)
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def is_state_usable(
    state: IndicatorStateSnapshot,
    *,
    expected_parent_build_id: str,
    actual_parent_build_id: str,
    next_canonical_key: tuple[object, ...],
    key_directly_follows: bool,
) -> bool:
    """§22.4's safety checks. Not yet wired into `rcc002.s3.compute` (see
    module docstring); provided for a future incremental-build caller."""
    if expected_parent_build_id != actual_parent_build_id:
        return False
    if not key_directly_follows:
        return False
    if compute_state_checksum(state) != state.checksum:
        return False
    if state.indicator_profile_id != INDICATOR_PROFILE_ID:
        return False
    if state.indicator_profile_version != INDICATOR_PROFILE_VERSION:
        return False
    if state.indicator_state_schema_ref != INDICATOR_STATE_SCHEMA_REF:
        return False
    return True
