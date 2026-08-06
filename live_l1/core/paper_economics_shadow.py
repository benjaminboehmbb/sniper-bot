#!/usr/bin/env python3
"""Read-only Paper Execution Economics shadow adapter.

This adapter translates explicit runtime configuration and a legacy entry
candidate into the pure IU-1 economics contract.  It owns no account or
position state, performs no persistence, and cannot authorize the active L1
execution path.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any, Mapping, Optional

from live_l1.core.paper_economics import (
    EntryAuthorization,
    PaperEconomicsConfig,
    PaperEconomicsError,
    ReasonCode,
    authorize_entry,
)


ZERO = Decimal("0")
ONE = Decimal("1")
DECIMAL_CONTEXT = Context(
    prec=50,
    rounding=ROUND_HALF_EVEN,
    Emin=-999999,
    Emax=999999,
)

MODE_OFF = "OFF"
MODE_SHADOW = "SHADOW"
MODE_INVALID = "INVALID"

SHADOW_CONFIG_MISSING = "PEE_CONFIG_MISSING"
SHADOW_CONFIG_INVALID = "PEE_CONFIG_INVALID"
SHADOW_MODE_INVALID = "PEE_CONFIG_MODE_INVALID"
SHADOW_OBSERVATION_ERROR = "PEE_SHADOW_OBSERVATION_ERROR"
SHADOW_NOT_CANDIDATE = "PEE_SHADOW_NOT_ENTRY_CANDIDATE"

ENVIRONMENT_FIELDS: Mapping[str, str] = {
    "PEE_SCHEMA_VERSION": "schema_version",
    "PEE_ECONOMICS_MODEL_VERSION": "economics_model_version",
    "PEE_ECONOMICS_PROFILE_ID": "economics_profile_id",
    "PEE_QUOTE_CURRENCY": "quote_currency",
    "PEE_STARTING_EQUITY_QUOTE": "starting_equity_quote",
    "PEE_RISK_PER_TRADE_RATE": "risk_per_trade_rate",
    "PEE_MAX_POSITION_NOTIONAL_RATE": "max_position_notional_rate",
    "PEE_ENTRY_FEE_RATE": "entry_fee_rate",
    "PEE_EXIT_FEE_RATE": "exit_fee_rate",
    "PEE_ENTRY_SLIPPAGE_BPS": "entry_slippage_bps",
    "PEE_EXIT_SLIPPAGE_BPS": "exit_slippage_bps",
    "PEE_QUANTITY_STEP": "quantity_step",
    "PEE_MIN_QUANTITY": "min_quantity",
    "PEE_MIN_NOTIONAL_QUOTE": "min_notional_quote",
    "PEE_MAX_DAILY_LOSS_RATE": "max_daily_loss_rate",
    "PEE_MAX_DAILY_FEE_RATE": "max_daily_fee_rate",
    "PEE_MAX_REALIZED_DRAWDOWN_RATE": "max_realized_drawdown_rate",
}
REFERENCE_STOP_RATE_ENV = "PEE_REFERENCE_STOP_RATE"


def _decimal_from_text(value: object, field_name: str) -> Decimal:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty decimal string")
    try:
        result = Decimal(value.strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} is not a valid decimal") from exc
    if not result.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return ZERO if result == ZERO else result


def _canonical_decimal(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    result = format(value, "f")
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    return result


def _stable_id(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ShadowEconomicsSettings:
    mode: str
    config: Optional[PaperEconomicsConfig]
    reference_stop_rate: Optional[Decimal]
    reason_code: str
    detail: str

    @property
    def ready(self) -> bool:
        return (
            self.mode == MODE_SHADOW
            and self.config is not None
            and self.reference_stop_rate is not None
            and self.reason_code == ReasonCode.AUTHORIZED
        )


@dataclass(frozen=True)
class ShadowEntryObservation:
    observation_id: str
    tick_id: int
    snapshot_id: str
    timestamp_utc: str
    intent_id: str
    side: str
    reference_entry_price: str
    reference_stop_price: str
    allowed: bool
    reason_code: str
    findings: tuple[str, ...]
    hypothetical_quantity: str
    risk_budget_quote: str
    entry_notional_quote: str
    modeled_stop_loss_quote: str
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str
    shadow_only: int = 1

    def to_log_fields(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "tick": self.tick_id,
            "snapshot_id": self.snapshot_id,
            "timestamp_utc": self.timestamp_utc,
            "side": self.side,
            "reference_entry_price": self.reference_entry_price,
            "reference_stop_price": self.reference_stop_price,
            "pee_allowed": int(self.allowed),
            "pee_reason_code": self.reason_code,
            "pee_findings": "|".join(self.findings),
            "hypothetical_quantity": self.hypothetical_quantity,
            "risk_budget_quote": self.risk_budget_quote,
            "entry_notional_quote": self.entry_notional_quote,
            "modeled_stop_loss_quote": self.modeled_stop_loss_quote,
            "economics_profile_id": self.economics_profile_id,
            "economics_model_version": self.economics_model_version,
            "config_fingerprint": self.config_fingerprint,
            "shadow_only": self.shadow_only,
        }


def load_shadow_settings(environment: Mapping[str, str]) -> ShadowEconomicsSettings:
    mode = str(environment.get("PEE_MODE", MODE_OFF)).strip().upper()
    if mode == MODE_OFF:
        return ShadowEconomicsSettings(
            mode=MODE_OFF,
            config=None,
            reference_stop_rate=None,
            reason_code="PEE_SHADOW_OFF",
            detail="paper economics shadow is disabled",
        )
    if mode != MODE_SHADOW:
        return ShadowEconomicsSettings(
            mode=MODE_INVALID,
            config=None,
            reference_stop_rate=None,
            reason_code=SHADOW_MODE_INVALID,
            detail="PEE_MODE must be OFF or SHADOW during IU-3",
        )

    required_names = tuple(ENVIRONMENT_FIELDS) + (REFERENCE_STOP_RATE_ENV,)
    missing = tuple(
        name
        for name in required_names
        if not str(environment.get(name, "")).strip()
    )
    if missing:
        return ShadowEconomicsSettings(
            mode=MODE_SHADOW,
            config=None,
            reference_stop_rate=None,
            reason_code=SHADOW_CONFIG_MISSING,
            detail="missing required fields: " + ",".join(missing),
        )

    values: dict[str, object] = {
        target: str(environment[source]).strip()
        for source, target in ENVIRONMENT_FIELDS.items()
    }
    try:
        values["schema_version"] = int(str(values["schema_version"]))
        config = PaperEconomicsConfig(**values)
        stop_rate = _decimal_from_text(
            environment[REFERENCE_STOP_RATE_ENV],
            REFERENCE_STOP_RATE_ENV,
        )
        if stop_rate <= ZERO or stop_rate >= ONE:
            raise ValueError("PEE_REFERENCE_STOP_RATE must be greater than zero and less than one")
    except (PaperEconomicsError, TypeError, ValueError) as exc:
        reason_code = getattr(exc, "reason_code", SHADOW_CONFIG_INVALID)
        return ShadowEconomicsSettings(
            mode=MODE_SHADOW,
            config=None,
            reference_stop_rate=None,
            reason_code=reason_code,
            detail=str(exc),
        )

    return ShadowEconomicsSettings(
        mode=MODE_SHADOW,
        config=config,
        reference_stop_rate=stop_rate,
        reason_code=ReasonCode.AUTHORIZED,
        detail="shadow configuration valid",
    )


def _rejected_observation(
    *,
    settings: ShadowEconomicsSettings,
    tick_id: int,
    snapshot_id: str,
    timestamp_utc: str,
    intent_id: str,
    side: str,
    reference_entry_price: str,
    reason_code: str,
    detail: str,
) -> ShadowEntryObservation:
    identity = {
        "tick_id": tick_id,
        "snapshot_id": snapshot_id,
        "intent_id": intent_id,
        "side": side,
        "reference_entry_price": reference_entry_price,
        "reason_code": reason_code,
        "mode": settings.mode,
    }
    return ShadowEntryObservation(
        observation_id=_stable_id(identity),
        tick_id=tick_id,
        snapshot_id=snapshot_id,
        timestamp_utc=timestamp_utc,
        intent_id=intent_id,
        side=side,
        reference_entry_price=reference_entry_price,
        reference_stop_price="",
        allowed=False,
        reason_code=reason_code,
        findings=(detail,),
        hypothetical_quantity="0",
        risk_budget_quote="",
        entry_notional_quote="",
        modeled_stop_loss_quote="",
        economics_profile_id="",
        economics_model_version="",
        config_fingerprint="",
    )


def observe_shadow_entry_candidate(
    *,
    settings: ShadowEconomicsSettings,
    current_position: str,
    intent_final: str,
    reference_entry_price: str,
    tick_id: int,
    snapshot_id: str,
    timestamp_utc: str,
    intent_id: str,
) -> Optional[ShadowEntryObservation]:
    """Return one read-only observation for a FLAT BUY/SELL candidate."""

    if settings.mode == MODE_OFF:
        return None
    position = str(current_position).strip().upper()
    intent = str(intent_final).strip().upper()
    if position != "FLAT" or intent not in ("BUY", "SELL"):
        return None
    side = "LONG" if intent == "BUY" else "SHORT"
    entry_text = str(reference_entry_price).strip()

    if not settings.ready or settings.config is None or settings.reference_stop_rate is None:
        return _rejected_observation(
            settings=settings,
            tick_id=tick_id,
            snapshot_id=snapshot_id,
            timestamp_utc=timestamp_utc,
            intent_id=intent_id,
            side=side,
            reference_entry_price=entry_text,
            reason_code=settings.reason_code,
            detail=settings.detail,
        )

    try:
        entry_price = _decimal_from_text(entry_text, "reference_entry_price")
        if entry_price <= ZERO:
            raise ValueError("reference_entry_price must be greater than zero")
        if side == "LONG":
            stop_price = DECIMAL_CONTEXT.multiply(
                entry_price,
                DECIMAL_CONTEXT.subtract(ONE, settings.reference_stop_rate),
            )
        else:
            stop_price = DECIMAL_CONTEXT.multiply(
                entry_price,
                DECIMAL_CONTEXT.add(ONE, settings.reference_stop_rate),
            )
        authorization = authorize_entry(
            side=side,
            realized_equity_quote=settings.config.starting_equity_quote,
            reference_entry_price=entry_price,
            reference_stop_price=stop_price,
            config=settings.config,
        )
    except Exception as exc:
        return _rejected_observation(
            settings=settings,
            tick_id=tick_id,
            snapshot_id=snapshot_id,
            timestamp_utc=timestamp_utc,
            intent_id=intent_id,
            side=side,
            reference_entry_price=entry_text,
            reason_code=getattr(exc, "reason_code", SHADOW_OBSERVATION_ERROR),
            detail=str(exc),
        )

    return _observation_from_authorization(
        settings=settings,
        authorization=authorization,
        side=side,
        entry_price=entry_price,
        stop_price=stop_price,
        tick_id=tick_id,
        snapshot_id=snapshot_id,
        timestamp_utc=timestamp_utc,
        intent_id=intent_id,
    )


def _observation_from_authorization(
    *,
    settings: ShadowEconomicsSettings,
    authorization: EntryAuthorization,
    side: str,
    entry_price: Decimal,
    stop_price: Decimal,
    tick_id: int,
    snapshot_id: str,
    timestamp_utc: str,
    intent_id: str,
) -> ShadowEntryObservation:
    config = settings.config
    if config is None:
        raise ValueError("valid shadow observation requires config")
    quote = authorization.quote
    quantity = _canonical_decimal(authorization.quantity)
    risk_budget = "" if quote is None else _canonical_decimal(quote.risk_budget_quote)
    entry_notional = "" if quote is None else _canonical_decimal(quote.entry_notional_quote)
    stop_loss = "" if quote is None else _canonical_decimal(quote.modeled_stop_loss_quote)
    identity = {
        "tick_id": tick_id,
        "snapshot_id": snapshot_id,
        "intent_id": intent_id,
        "side": side,
        "reference_entry_price": _canonical_decimal(entry_price),
        "reference_stop_price": _canonical_decimal(stop_price),
        "reason_code": authorization.reason_code,
        "config_fingerprint": config.config_fingerprint,
    }
    return ShadowEntryObservation(
        observation_id=_stable_id(identity),
        tick_id=tick_id,
        snapshot_id=snapshot_id,
        timestamp_utc=timestamp_utc,
        intent_id=intent_id,
        side=side,
        reference_entry_price=_canonical_decimal(entry_price),
        reference_stop_price=_canonical_decimal(stop_price),
        allowed=authorization.allowed,
        reason_code=authorization.reason_code,
        findings=authorization.findings,
        hypothetical_quantity=quantity,
        risk_budget_quote=risk_budget,
        entry_notional_quote=entry_notional,
        modeled_stop_loss_quote=stop_loss,
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


def add_legacy_execution_outcome(
    observation: ShadowEntryObservation,
    *,
    legacy_action: str,
    legacy_executed: bool,
    legacy_position_before: str,
    legacy_position_after: str,
) -> dict[str, Any]:
    fields = observation.to_log_fields()
    executed = bool(legacy_executed)
    if executed and observation.allowed:
        parity_code = "PEE_SHADOW_LEGACY_EXECUTED_PEE_ALLOWED"
    elif executed and not observation.allowed:
        parity_code = "PEE_SHADOW_LEGACY_EXECUTED_PEE_REJECTED"
    elif not executed and observation.allowed:
        parity_code = "PEE_SHADOW_LEGACY_NOT_EXECUTED_PEE_ALLOWED"
    else:
        parity_code = "PEE_SHADOW_LEGACY_NOT_EXECUTED_PEE_REJECTED"
    fields.update(
        {
            "legacy_action": str(legacy_action),
            "legacy_executed": int(executed),
            "legacy_position_before": str(legacy_position_before),
            "legacy_position_after": str(legacy_position_after),
            "parity_code": parity_code,
        }
    )
    return fields


__all__ = [
    "ENVIRONMENT_FIELDS",
    "MODE_INVALID",
    "MODE_OFF",
    "MODE_SHADOW",
    "REFERENCE_STOP_RATE_ENV",
    "SHADOW_CONFIG_INVALID",
    "SHADOW_CONFIG_MISSING",
    "SHADOW_MODE_INVALID",
    "ShadowEconomicsSettings",
    "ShadowEntryObservation",
    "add_legacy_execution_outcome",
    "load_shadow_settings",
    "observe_shadow_entry_candidate",
]
