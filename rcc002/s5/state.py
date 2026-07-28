"""Canonical checkpoint state for deterministic S5 continuation."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from typing import Any

from rcc002.s5.constants import (
    REGIME_MODEL_ID,
    REGIME_MODEL_VERSION,
    REGIME_STATE_SCHEMA_ID,
    REGIME_STATE_SCHEMA_REF,
    REGIME_STATE_SCHEMA_VERSION,
    SLOPE_LOOKBACK_BARS,
    SMA200_CONTEXT_PROFILE_ID,
    SMA200_CONTEXT_PROFILE_VERSION,
    STATE_HASH_PROFILE_ID,
    STATE_HASH_PROFILE_VERSION,
    RegimeState,
)


def _canonical(value: Any) -> Any:
    if isinstance(value, RegimeState):
        return value.value
    if isinstance(value, dict):
        return {
            key: _canonical(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if dataclasses.is_dataclass(value):
        return {
            field.name: _canonical(getattr(value, field.name))
            for field in dataclasses.fields(value)
            if field.name != "state_payload_sha256"
        }
    return value


def compute_state_hash(snapshot: "RegimeStateSnapshot") -> str:
    payload = json.dumps(
        _canonical(snapshot),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _compute_payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        _canonical(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclasses.dataclass(frozen=True, slots=True)
class RegimeStateSnapshot:
    state_schema_id: str
    state_schema_version: str
    state_schema_ref: str
    parent_build_id: str
    market_type: str
    symbol: str
    interval: str
    last_open_time: int
    market_segment_id: str
    indicator_segment_id: str
    sma200_context_state: tuple[float, ...]
    regime_effective: RegimeState
    regime_candidate: RegimeState
    regime_candidate_count: int
    regime_model_id: str
    regime_model_version: str
    state_profile_id: str
    state_profile_version: str
    state_hash_profile_id: str
    state_hash_profile_version: str
    state_payload_sha256: str

    def __post_init__(self) -> None:
        expected = {
            "state_schema_id": REGIME_STATE_SCHEMA_ID,
            "state_schema_version": REGIME_STATE_SCHEMA_VERSION,
            "state_schema_ref": REGIME_STATE_SCHEMA_REF,
            "regime_model_id": REGIME_MODEL_ID,
            "regime_model_version": REGIME_MODEL_VERSION,
            "state_profile_id": SMA200_CONTEXT_PROFILE_ID,
            "state_profile_version": (
                SMA200_CONTEXT_PROFILE_VERSION
            ),
            "state_hash_profile_id": STATE_HASH_PROFILE_ID,
            "state_hash_profile_version": STATE_HASH_PROFILE_VERSION,
        }
        for name, value in expected.items():
            if getattr(self, name) != value:
                raise ValueError(f"{name} must equal {value!r}")
        for name in (
            "parent_build_id", "market_type", "symbol", "interval",
            "market_segment_id", "indicator_segment_id",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(
                self, name
            ):
                raise ValueError(f"{name} must be a non-empty string")
        if isinstance(self.last_open_time, bool) or not isinstance(
            self.last_open_time, int
        ):
            raise ValueError("last_open_time must be an integer")
        if not isinstance(self.sma200_context_state, tuple):
            raise ValueError("sma200_context_state must be a tuple")
        if len(self.sma200_context_state) > SLOPE_LOOKBACK_BARS:
            raise ValueError("SMA200 context exceeds 1,440 values")
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            for value in self.sma200_context_state
        ):
            raise ValueError("SMA200 context values must be finite")
        if not isinstance(self.regime_effective, RegimeState):
            raise ValueError("regime_effective must be RegimeState")
        if not isinstance(self.regime_candidate, RegimeState):
            raise ValueError("regime_candidate must be RegimeState")
        if (
            isinstance(self.regime_candidate_count, bool)
            or not isinstance(self.regime_candidate_count, int)
            or not 0 <= self.regime_candidate_count <= 3
        ):
            raise ValueError("stored candidate count must be from 0 to 3")
        if (
            self.regime_candidate is RegimeState.UNKNOWN
        ) != (self.regime_candidate_count == 0):
            raise ValueError(
                "UNKNOWN candidate and zero count must occur together"
            )
        if (
            self.regime_candidate_count == 3
            and self.regime_candidate is not self.regime_effective
        ):
            raise ValueError(
                "a saturated candidate must be the effective regime"
            )
        if (
            not isinstance(self.state_payload_sha256, str)
            or len(self.state_payload_sha256) != 64
            or self.state_payload_sha256
            != self.state_payload_sha256.lower()
        ):
            raise ValueError(
                "state_payload_sha256 must be 64 lowercase hex characters"
            )
        try:
            int(self.state_payload_sha256, 16)
        except ValueError as exc:
            raise ValueError(
                "state_payload_sha256 must be lowercase hexadecimal"
            ) from exc
        if self.state_payload_sha256 != compute_state_hash(self):
            raise ValueError("S5 state checksum mismatch")

    def with_checksum(self) -> "RegimeStateSnapshot":
        return dataclasses.replace(
            self,
            state_payload_sha256=compute_state_hash(self),
        )


def make_state_snapshot(
    *,
    parent_build_id: str,
    market_type: str,
    symbol: str,
    interval: str,
    last_open_time: int,
    market_segment_id: str,
    indicator_segment_id: str,
    sma200_context_state: tuple[float, ...],
    regime_effective: RegimeState,
    regime_candidate: RegimeState,
    regime_candidate_count: int,
) -> RegimeStateSnapshot:
    payload: dict[str, Any] = {
        "state_schema_id": REGIME_STATE_SCHEMA_ID,
        "state_schema_version": REGIME_STATE_SCHEMA_VERSION,
        "state_schema_ref": REGIME_STATE_SCHEMA_REF,
        "parent_build_id": parent_build_id,
        "market_type": market_type,
        "symbol": symbol,
        "interval": interval,
        "last_open_time": last_open_time,
        "market_segment_id": market_segment_id,
        "indicator_segment_id": indicator_segment_id,
        "sma200_context_state": sma200_context_state,
        "regime_effective": regime_effective,
        "regime_candidate": regime_candidate,
        "regime_candidate_count": regime_candidate_count,
        "regime_model_id": REGIME_MODEL_ID,
        "regime_model_version": REGIME_MODEL_VERSION,
        "state_profile_id": SMA200_CONTEXT_PROFILE_ID,
        "state_profile_version": (
            SMA200_CONTEXT_PROFILE_VERSION
        ),
        "state_hash_profile_id": STATE_HASH_PROFILE_ID,
        "state_hash_profile_version": STATE_HASH_PROFILE_VERSION,
    }
    return RegimeStateSnapshot(
        **payload,
        state_payload_sha256=_compute_payload_hash(payload),
    )


__all__ = [
    "RegimeStateSnapshot",
    "compute_state_hash",
    "make_state_snapshot",
]
