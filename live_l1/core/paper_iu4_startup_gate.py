#!/usr/bin/env python3
"""Inactive startup and operating-mode gate for the future IU-4 adapter.

This module is pure except for validated read access through
PaperAtomicCoordinator.  It is deliberately not imported by the active loop.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from live_l1.core.paper_entry_throttle import canonical_utc_timestamp
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator


MODE_OFF = "OFF"
MODE_SHADOW = "SHADOW"
MODE_ENFORCED = "ENFORCED"
IU4_MODES = frozenset({MODE_OFF, MODE_SHADOW, MODE_ENFORCED})


class IU4StartupReasonCode:
    OFF = "PEE_IU4_STARTUP_OFF"
    SHADOW_READY = "PEE_IU4_SHADOW_READY"
    ENFORCED_READY = "PEE_IU4_ENFORCED_READY"
    REQUEST_INVALID = "PEE_IU4_STARTUP_REQUEST_INVALID"
    COORDINATOR_REQUIRED = "PEE_IU4_COORDINATOR_REQUIRED"
    IDENTITY_MISMATCH = "PEE_IU4_STARTUP_IDENTITY_MISMATCH"
    REPOSITORY_COMMIT_REQUIRED = "PEE_IU4_REPOSITORY_COMMIT_REQUIRED"
    REPOSITORY_COMMIT_MISMATCH = "PEE_IU4_REPOSITORY_COMMIT_MISMATCH"
    RECONCILIATION_FAILED = "PEE_IU4_RECONCILIATION_FAILED"
    PAPER_PROFILE_REQUIRED = "PEE_IU4_PAPER_PROFILE_REQUIRED"
    RECOVERY_REQUIRED = "PEE_IU4_STARTUP_RECOVERY_REQUIRED"
    RECONCILIATION_GATE_REQUIRED = "PEE_IU4_RECONCILIATION_GATE_REQUIRED"
    AUTHORIZATION_REQUIRED = "PEE_IU4_AUTHORIZATION_REQUIRED"
    AUTHORIZATION_TRUST_REQUIRED = "PEE_IU4_AUTHORIZATION_TRUST_REQUIRED"
    AUTHORIZATION_TRUST_MISMATCH = "PEE_IU4_AUTHORIZATION_TRUST_MISMATCH"
    AUTHORIZATION_MISMATCH = "PEE_IU4_AUTHORIZATION_MISMATCH"
    AUTHORIZATION_NOT_YET_VALID = "PEE_IU4_AUTHORIZATION_NOT_YET_VALID"
    AUTHORIZATION_EXPIRED = "PEE_IU4_AUTHORIZATION_EXPIRED"


class IU4StartupGateError(ValueError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


def _text(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise IU4StartupGateError(
            IU4StartupReasonCode.REQUEST_INVALID,
            f"{field_name} must be a string",
        )
    result = value.strip()
    if not allow_empty and not result:
        raise IU4StartupGateError(
            IU4StartupReasonCode.REQUEST_INVALID,
            f"{field_name} must not be empty",
        )
    return result


def _boolean(value: object, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise IU4StartupGateError(
            IU4StartupReasonCode.REQUEST_INVALID,
            f"{field_name} must be boolean",
        )
    return value


def _sha256(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    result = _text(value, field_name, allow_empty=allow_empty).lower()
    if not result and allow_empty:
        return ""
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise IU4StartupGateError(
            IU4StartupReasonCode.REQUEST_INVALID,
            f"{field_name} must be a lowercase SHA-256 digest",
        )
    return result


def _commit_sha(value: object, *, allow_empty: bool = False) -> str:
    result = _text(value, "repository_commit_sha", allow_empty=allow_empty).lower()
    if not result and allow_empty:
        return ""
    if len(result) != 40 or any(character not in "0123456789abcdef" for character in result):
        raise IU4StartupGateError(
            IU4StartupReasonCode.REQUEST_INVALID,
            "repository_commit_sha must be a full lowercase Git commit SHA",
        )
    return result


def _timestamp(value: object, field_name: str) -> str:
    try:
        return canonical_utc_timestamp(value, field_name)
    except Exception as exc:
        raise IU4StartupGateError(
            IU4StartupReasonCode.REQUEST_INVALID,
            f"{field_name} must be a timezone-aware whole-second timestamp",
        ) from exc


def _as_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00")


@dataclass(frozen=True)
class IU4ActivationAuthorizationV1:
    schema_version: int
    authorization_id: str
    authorization_reference: str
    approved_mode: str
    coordinator_id: str
    symbol: str
    economics_profile_id: str
    economics_model_version: str
    economics_config_fingerprint: str
    throttle_policy_profile_id: str
    throttle_policy_model_version: str
    throttle_policy_fingerprint: str
    repository_commit_sha: str
    valid_from_utc: str
    valid_until_utc: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "IU4ActivationAuthorizationV1 requires schema_version 1",
            )
        for name in (
            "authorization_reference",
            "coordinator_id",
            "symbol",
            "economics_profile_id",
            "economics_model_version",
            "throttle_policy_profile_id",
            "throttle_policy_model_version",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        mode = _text(self.approved_mode, "approved_mode").upper()
        if mode != MODE_ENFORCED:
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "activation authorization can approve ENFORCED only",
            )
        object.__setattr__(self, "approved_mode", mode)
        for name in ("symbol",):
            object.__setattr__(self, name, getattr(self, name).upper())
        for name in (
            "economics_config_fingerprint",
            "throttle_policy_fingerprint",
        ):
            object.__setattr__(self, name, _sha256(getattr(self, name), name))
        object.__setattr__(
            self,
            "repository_commit_sha",
            _commit_sha(self.repository_commit_sha),
        )
        object.__setattr__(
            self,
            "valid_from_utc",
            _timestamp(self.valid_from_utc, "valid_from_utc"),
        )
        object.__setattr__(
            self,
            "valid_until_utc",
            _timestamp(self.valid_until_utc, "valid_until_utc"),
        )
        if _as_datetime(self.valid_until_utc) <= _as_datetime(self.valid_from_utc):
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "authorization validity window must be increasing",
            )
        expected_id = f"PEE-IU4-AUTH-{self.authorization_fingerprint}"
        authorization_id = _text(
            self.authorization_id,
            "authorization_id",
            allow_empty=True,
        )
        if authorization_id and authorization_id != expected_id:
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "authorization_id does not match its canonical payload",
            )
        object.__setattr__(self, "authorization_id", expected_id)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "authorization_id"
        }

    @property
    def authorization_fingerprint(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_record(self) -> dict[str, Any]:
        return {"authorization_id": self.authorization_id, **self.canonical_payload()}

    @classmethod
    def from_record(
        cls,
        record: Mapping[str, Any],
    ) -> "IU4ActivationAuthorizationV1":
        if set(record) != set(cls.__dataclass_fields__):
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "authorization fields are missing or unknown",
            )
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True)
class IU4StartupModeRequestV1:
    schema_version: int
    mode: str
    startup_timestamp_utc: str
    operational_profile: str
    startup_recovery_enabled: bool
    reconciliation_gate_enabled: bool
    repository_commit_sha: str
    expected_coordinator_id: str
    expected_symbol: str
    expected_economics_profile_id: str
    expected_economics_model_version: str
    expected_economics_config_fingerprint: str
    expected_throttle_policy_profile_id: str
    expected_throttle_policy_model_version: str
    expected_throttle_policy_fingerprint: str
    authorization: IU4ActivationAuthorizationV1 | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "IU4StartupModeRequestV1 requires schema_version 1",
            )
        mode = _text(self.mode, "mode").upper()
        if mode not in IU4_MODES:
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "IU-4 mode must be OFF, SHADOW, or ENFORCED",
            )
        object.__setattr__(self, "mode", mode)
        object.__setattr__(
            self,
            "startup_timestamp_utc",
            _timestamp(self.startup_timestamp_utc, "startup_timestamp_utc"),
        )
        object.__setattr__(
            self,
            "operational_profile",
            _text(
                self.operational_profile,
                "operational_profile",
                allow_empty=(mode == MODE_OFF),
            ).upper(),
        )
        object.__setattr__(
            self,
            "startup_recovery_enabled",
            _boolean(self.startup_recovery_enabled, "startup_recovery_enabled"),
        )
        object.__setattr__(
            self,
            "reconciliation_gate_enabled",
            _boolean(self.reconciliation_gate_enabled, "reconciliation_gate_enabled"),
        )
        require_identity = mode != MODE_OFF
        for name in (
            "expected_coordinator_id",
            "expected_symbol",
            "expected_economics_profile_id",
            "expected_economics_model_version",
            "expected_throttle_policy_profile_id",
            "expected_throttle_policy_model_version",
        ):
            object.__setattr__(
                self,
                name,
                _text(getattr(self, name), name, allow_empty=not require_identity),
            )
        object.__setattr__(self, "expected_symbol", self.expected_symbol.upper())
        object.__setattr__(
            self,
            "repository_commit_sha",
            _commit_sha(self.repository_commit_sha, allow_empty=not require_identity),
        )
        for name in (
            "expected_economics_config_fingerprint",
            "expected_throttle_policy_fingerprint",
        ):
            object.__setattr__(
                self,
                name,
                _sha256(getattr(self, name), name, allow_empty=not require_identity),
            )
        if mode == MODE_ENFORCED and not isinstance(
            self.authorization,
            IU4ActivationAuthorizationV1,
        ):
            raise IU4StartupGateError(
                IU4StartupReasonCode.AUTHORIZATION_REQUIRED,
                "ENFORCED requires an activation authorization",
            )
        if mode != MODE_ENFORCED and self.authorization is not None:
            raise IU4StartupGateError(
                IU4StartupReasonCode.REQUEST_INVALID,
                "OFF/SHADOW must not carry an ENFORCED authorization",
            )

    @classmethod
    def off(cls, *, startup_timestamp_utc: str) -> "IU4StartupModeRequestV1":
        return cls(
            schema_version=1,
            mode=MODE_OFF,
            startup_timestamp_utc=startup_timestamp_utc,
            operational_profile="",
            startup_recovery_enabled=False,
            reconciliation_gate_enabled=False,
            repository_commit_sha="",
            expected_coordinator_id="",
            expected_symbol="",
            expected_economics_profile_id="",
            expected_economics_model_version="",
            expected_economics_config_fingerprint="",
            expected_throttle_policy_profile_id="",
            expected_throttle_policy_model_version="",
            expected_throttle_policy_fingerprint="",
            authorization=None,
        )


@dataclass(frozen=True)
class IU4StartupGateDecisionV1:
    schema_version: int
    passed: bool
    mode: str
    adapter_execution_enabled: bool
    shadow_observation_enabled: bool
    state_mutation_allowed: bool
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    atomic_state_fingerprint: str
    atomic_transaction_sequence: int
    authorization_id: str


def _decision(
    request: IU4StartupModeRequestV1,
    *,
    passed: bool,
    reason_codes: tuple[str, ...],
    state_fingerprint: str = "",
    transaction_sequence: int = 0,
    entry_allowed: bool = False,
) -> IU4StartupGateDecisionV1:
    enforced = passed and request.mode == MODE_ENFORCED
    shadow = passed and request.mode == MODE_SHADOW
    return IU4StartupGateDecisionV1(
        schema_version=1,
        passed=passed,
        mode=request.mode,
        adapter_execution_enabled=enforced,
        shadow_observation_enabled=shadow,
        state_mutation_allowed=enforced,
        entry_allowed=enforced and entry_allowed,
        exit_allowed=True,
        reason_codes=reason_codes,
        atomic_state_fingerprint=state_fingerprint,
        atomic_transaction_sequence=transaction_sequence,
        authorization_id=(
            "" if request.authorization is None else request.authorization.authorization_id
        ),
    )


def _identity_matches(
    request: IU4StartupModeRequestV1,
    coordinator: PaperAtomicCoordinator,
) -> bool:
    return all(
        (
            request.expected_coordinator_id == coordinator.coordinator_id,
            request.expected_symbol == coordinator.symbol,
            request.expected_economics_profile_id
            == coordinator.config.economics_profile_id,
            request.expected_economics_model_version
            == coordinator.config.economics_model_version,
            request.expected_economics_config_fingerprint
            == coordinator.config.config_fingerprint,
            request.expected_throttle_policy_profile_id
            == coordinator.throttle_policy.policy_profile_id,
            request.expected_throttle_policy_model_version
            == coordinator.throttle_policy.policy_model_version,
            request.expected_throttle_policy_fingerprint
            == coordinator.throttle_policy.policy_fingerprint,
        )
    )


def _authorization_reason(
    request: IU4StartupModeRequestV1,
) -> str | None:
    authorization = request.authorization
    if authorization is None:
        return IU4StartupReasonCode.AUTHORIZATION_REQUIRED
    identities_match = all(
        (
            authorization.approved_mode == request.mode,
            authorization.coordinator_id == request.expected_coordinator_id,
            authorization.symbol == request.expected_symbol,
            authorization.economics_profile_id
            == request.expected_economics_profile_id,
            authorization.economics_model_version
            == request.expected_economics_model_version,
            authorization.economics_config_fingerprint
            == request.expected_economics_config_fingerprint,
            authorization.throttle_policy_profile_id
            == request.expected_throttle_policy_profile_id,
            authorization.throttle_policy_model_version
            == request.expected_throttle_policy_model_version,
            authorization.throttle_policy_fingerprint
            == request.expected_throttle_policy_fingerprint,
            authorization.repository_commit_sha == request.repository_commit_sha,
        )
    )
    if not identities_match:
        return IU4StartupReasonCode.AUTHORIZATION_MISMATCH
    startup = _as_datetime(request.startup_timestamp_utc)
    if startup < _as_datetime(authorization.valid_from_utc):
        return IU4StartupReasonCode.AUTHORIZATION_NOT_YET_VALID
    if startup > _as_datetime(authorization.valid_until_utc):
        return IU4StartupReasonCode.AUTHORIZATION_EXPIRED
    return None


def evaluate_iu4_startup_gate(
    request: IU4StartupModeRequestV1,
    coordinator: PaperAtomicCoordinator | None,
    *,
    running_repository_commit_sha: str | None = None,
    trusted_authorization_id: str | None = None,
) -> IU4StartupGateDecisionV1:
    """Evaluate one startup request without activating or importing the adapter."""
    if not isinstance(request, IU4StartupModeRequestV1):
        raise IU4StartupGateError(
            IU4StartupReasonCode.REQUEST_INVALID,
            "gate requires IU4StartupModeRequestV1",
        )
    if request.mode == MODE_OFF:
        return _decision(
            request,
            passed=True,
            reason_codes=(IU4StartupReasonCode.OFF,),
        )
    if not isinstance(coordinator, PaperAtomicCoordinator):
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.COORDINATOR_REQUIRED,),
        )
    if not _identity_matches(request, coordinator):
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.IDENTITY_MISMATCH,),
        )
    if running_repository_commit_sha is None:
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.REPOSITORY_COMMIT_REQUIRED,),
        )
    running_commit = _commit_sha(running_repository_commit_sha)
    if running_commit != request.repository_commit_sha:
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.REPOSITORY_COMMIT_MISMATCH,),
        )
    if not request.reconciliation_gate_enabled:
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.RECONCILIATION_GATE_REQUIRED,),
        )

    report = coordinator.reconciliation_report()
    if not report.consistent:
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.RECONCILIATION_FAILED, *report.reason_codes),
            transaction_sequence=report.snapshot_transaction_sequence,
        )
    state = coordinator.load_state()
    if request.mode == MODE_SHADOW:
        return _decision(
            request,
            passed=True,
            reason_codes=(IU4StartupReasonCode.SHADOW_READY,),
            state_fingerprint=state.state_fingerprint,
            transaction_sequence=state.transaction_sequence,
        )
    if request.operational_profile != "PAPER":
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.PAPER_PROFILE_REQUIRED,),
            state_fingerprint=state.state_fingerprint,
            transaction_sequence=state.transaction_sequence,
        )
    if not request.startup_recovery_enabled:
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.RECOVERY_REQUIRED,),
            state_fingerprint=state.state_fingerprint,
            transaction_sequence=state.transaction_sequence,
        )
    if trusted_authorization_id is None:
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.AUTHORIZATION_TRUST_REQUIRED,),
            state_fingerprint=state.state_fingerprint,
            transaction_sequence=state.transaction_sequence,
        )
    trusted_id = _text(trusted_authorization_id, "trusted_authorization_id")
    assert request.authorization is not None
    if trusted_id != request.authorization.authorization_id:
        return _decision(
            request,
            passed=False,
            reason_codes=(IU4StartupReasonCode.AUTHORIZATION_TRUST_MISMATCH,),
            state_fingerprint=state.state_fingerprint,
            transaction_sequence=state.transaction_sequence,
        )
    authorization_reason = _authorization_reason(request)
    if authorization_reason is not None:
        return _decision(
            request,
            passed=False,
            reason_codes=(authorization_reason,),
            state_fingerprint=state.state_fingerprint,
            transaction_sequence=state.transaction_sequence,
        )
    reasons = (
        (IU4StartupReasonCode.ENFORCED_READY,)
        if state.risk.entry_allowed
        else (IU4StartupReasonCode.ENFORCED_READY, *state.risk.reason_codes)
    )
    return _decision(
        request,
        passed=True,
        reason_codes=reasons,
        state_fingerprint=state.state_fingerprint,
        transaction_sequence=state.transaction_sequence,
        entry_allowed=state.risk.entry_allowed,
    )


__all__ = [
    "IU4ActivationAuthorizationV1",
    "IU4StartupGateDecisionV1",
    "IU4StartupGateError",
    "IU4StartupModeRequestV1",
    "IU4StartupReasonCode",
    "MODE_ENFORCED",
    "MODE_OFF",
    "MODE_SHADOW",
    "evaluate_iu4_startup_gate",
]
