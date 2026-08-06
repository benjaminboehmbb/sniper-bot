#!/usr/bin/env python3
"""Fail-safe bridge from the active L1 loop to PEE shadow observations.

The bridge accepts scalar copies of legacy inputs and never receives mutable
runtime state.  Shadow calculation or logging preparation failures therefore
cannot authorize, reject, or mutate legacy execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from live_l1.core.paper_economics_shadow import (
    MODE_INVALID,
    MODE_OFF,
    ShadowEconomicsSettings,
    ShadowEntryObservation,
    add_legacy_execution_outcome,
    load_shadow_settings,
    observe_shadow_entry_candidate,
)


SHADOW_RUNTIME_ERROR = "PEE_SHADOW_RUNTIME_ERROR"
SHADOW_PARITY_UNKNOWN = "PEE_SHADOW_PARITY_UNKNOWN"


@dataclass(frozen=True)
class RuntimeShadowAttempt:
    observation: Optional[ShadowEntryObservation]
    candidate: bool
    tick_id: int
    snapshot_id: str
    timestamp_utc: str
    intent_id: str
    side: str
    reference_entry_price: str
    error_reason_code: str = ""
    error_detail: str = ""


def load_runtime_shadow_settings(
    environment: Mapping[str, str],
) -> ShadowEconomicsSettings:
    """Load settings without allowing a shadow failure to stop L1 startup."""

    try:
        return load_shadow_settings(environment)
    except Exception as exc:
        return ShadowEconomicsSettings(
            mode=MODE_INVALID,
            config=None,
            reference_stop_rate=None,
            reason_code=SHADOW_RUNTIME_ERROR,
            detail=str(exc),
        )


def shadow_startup_log_fields(
    settings: ShadowEconomicsSettings,
) -> dict[str, Any]:
    if settings.mode == MODE_OFF:
        return {}
    config = settings.config
    return {
        "pee_shadow_mode": settings.mode,
        "pee_shadow_ready": int(settings.ready),
        "pee_shadow_reason_code": settings.reason_code,
        "pee_economics_profile_id": "" if config is None else config.economics_profile_id,
        "pee_economics_model_version": "" if config is None else config.economics_model_version,
        "pee_config_fingerprint": "" if config is None else config.config_fingerprint,
    }


def observe_runtime_shadow(
    *,
    settings: ShadowEconomicsSettings,
    current_position: str,
    intent_final: str,
    reference_entry_price: str,
    tick_id: int,
    snapshot_id: str,
    timestamp_utc: str,
    intent_id: str,
) -> RuntimeShadowAttempt:
    """Calculate one shadow observation from immutable scalar inputs."""

    position = str(current_position).strip().upper()
    intent = str(intent_final).strip().upper()
    candidate = position == "FLAT" and intent in ("BUY", "SELL")
    side = "LONG" if intent == "BUY" else "SHORT" if intent == "SELL" else ""
    values = {
        "candidate": candidate,
        "tick_id": int(tick_id),
        "snapshot_id": str(snapshot_id),
        "timestamp_utc": str(timestamp_utc),
        "intent_id": str(intent_id),
        "side": side,
        "reference_entry_price": str(reference_entry_price),
    }
    if settings.mode == MODE_OFF or not candidate:
        return RuntimeShadowAttempt(observation=None, **values)

    try:
        observation = observe_shadow_entry_candidate(
            settings=settings,
            current_position=position,
            intent_final=intent,
            reference_entry_price=values["reference_entry_price"],
            tick_id=values["tick_id"],
            snapshot_id=values["snapshot_id"],
            timestamp_utc=values["timestamp_utc"],
            intent_id=values["intent_id"],
        )
        return RuntimeShadowAttempt(observation=observation, **values)
    except Exception as exc:
        return RuntimeShadowAttempt(
            observation=None,
            error_reason_code=getattr(exc, "reason_code", SHADOW_RUNTIME_ERROR),
            error_detail=str(exc),
            **values,
        )


def build_runtime_shadow_log_fields(
    attempt: RuntimeShadowAttempt,
    *,
    settings: ShadowEconomicsSettings,
    legacy_action: str,
    legacy_executed: bool,
    legacy_position_before: str,
    legacy_position_after: str,
) -> Optional[dict[str, Any]]:
    """Build audit fields after legacy execution without changing its result."""

    if not attempt.candidate or settings.mode == MODE_OFF:
        return None
    if attempt.observation is not None:
        return add_legacy_execution_outcome(
            attempt.observation,
            legacy_action=legacy_action,
            legacy_executed=legacy_executed,
            legacy_position_before=legacy_position_before,
            legacy_position_after=legacy_position_after,
        )

    config = settings.config
    return {
        "tick": attempt.tick_id,
        "snapshot_id": attempt.snapshot_id,
        "timestamp_utc": attempt.timestamp_utc,
        "side": attempt.side,
        "reference_entry_price": attempt.reference_entry_price,
        "reference_stop_price": "",
        "pee_allowed": 0,
        "pee_reason_code": attempt.error_reason_code or SHADOW_RUNTIME_ERROR,
        "pee_findings": attempt.error_detail or "shadow observation missing",
        "hypothetical_quantity": "0",
        "risk_budget_quote": "",
        "entry_notional_quote": "",
        "modeled_stop_loss_quote": "",
        "economics_profile_id": "" if config is None else config.economics_profile_id,
        "economics_model_version": "" if config is None else config.economics_model_version,
        "config_fingerprint": "" if config is None else config.config_fingerprint,
        "shadow_only": 1,
        "legacy_action": str(legacy_action),
        "legacy_executed": int(bool(legacy_executed)),
        "legacy_position_before": str(legacy_position_before),
        "legacy_position_after": str(legacy_position_after),
        "parity_code": SHADOW_PARITY_UNKNOWN,
    }


__all__ = [
    "RuntimeShadowAttempt",
    "SHADOW_PARITY_UNKNOWN",
    "SHADOW_RUNTIME_ERROR",
    "build_runtime_shadow_log_fields",
    "load_runtime_shadow_settings",
    "observe_runtime_shadow",
    "shadow_startup_log_fields",
]
