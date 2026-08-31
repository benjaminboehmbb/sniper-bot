#!/usr/bin/env python3
"""Inactive atomic coordinator for complete Paper Execution state.

One aggregate snapshot owns the publication boundary across S2 position,
Paper Account/settlement, derived S4 risk state, and entry throttle.  Every
OPEN/CLOSE/KILL transaction is written to an immutable write-ahead journal before
the aggregate snapshot advances.  Recovery therefore publishes either the
complete state before a transaction or the complete state after it.

This module is deliberately not imported by the active L1 loop.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import fcntl
import threading
from contextlib import contextmanager
from functools import wraps
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from live_l1.core.paper_economics import PaperEconomicsConfig
from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    PaperEntryThrottleError,
    PaperEntryThrottlePolicy,
    PaperEntryThrottleState,
    apply_accepted_entry,
    evaluate_entry_throttle,
)
from live_l1.state.paper_artifacts import (
    EntryEconomicsQuoteArtifactV1,
    PaperAccountState,
    PaperArtifactError,
    PaperRiskStateS4V2,
    PositionArtifactV2,
    PositionStateS2FlatV2,
    PositionStateS2V2,
    TradeRecordV2,
    apply_trade_to_account,
    canonical_json_sha256,
    evaluate_account_entry_guard,
    parse_position_artifact,
)
from live_l1.state.loss_cluster import (
    LossClusterStateError,
    LossClusterStateV2,
    apply_loss_cluster_close,
    apply_loss_cluster_entry_veto,
)
from live_l1.state.iu4_lifecycle_ledger import (
    IU4LifecycleLedgerError,
    IU4LifecycleLedgerV1,
    authority_generation_id,
    fingerprint as lifecycle_fingerprint,
)


ARTIFACT_ATOMIC_TRANSACTION = "paper_atomic_transaction"
TRANSACTION_OPEN = "OPEN"
TRANSACTION_CLOSE = "CLOSE"
TRANSACTION_KILL = "KILL"
TRANSACTION_ENTRY_VETO = "ENTRY_VETO"
TRANSACTION_PROGRESS = "PROGRESS"
KILL_LEVELS = frozenset({"NONE", "SOFT", "HARD", "EMERGENCY"})
POSITION_OPEN_REASON = "PEE_S4_POSITION_OPEN"
ENTRY_DENIAL_PROVENANCE_ARTIFACT = "atomic_entry_denial_provenance_v1"
ENTRY_DENIAL_ORIGINS = frozenset(
    {
        "STATE_CAPABILITY",
        "RUNTIME_GATE_CAPABILITY",
        "ECONOMICS_AUTHORIZATION",
        "ATOMIC_ENTRY_GUARD",
    }
)


class AtomicCoordinatorReasonCode:
    STATE_MISSING = "PEE_ATOMIC_STATE_MISSING"
    STATE_ALREADY_INITIALIZED = "PEE_ATOMIC_STATE_ALREADY_INITIALIZED"
    JSON_INVALID = "PEE_ATOMIC_JSON_INVALID"
    TRANSACTION_INVALID = "PEE_ATOMIC_TRANSACTION_INVALID"
    JOURNAL_CONFLICT = "PEE_ATOMIC_JOURNAL_CONFLICT"
    JOURNAL_GAP = "PEE_ATOMIC_JOURNAL_GAP"
    STATE_AHEAD_OF_JOURNAL = "PEE_ATOMIC_STATE_AHEAD_OF_JOURNAL"
    RECOVERY_REQUIRED = "PEE_ATOMIC_RECOVERY_REQUIRED"
    ENTRY_BLOCKED = "PEE_ATOMIC_ENTRY_BLOCKED"
    IDENTITY_MISMATCH = "PEE_ATOMIC_IDENTITY_MISMATCH"
    ATOMIC_SCHEMA_UNSUPPORTED = "PEE_IU4_ATOMIC_SCHEMA_UNSUPPORTED"
    ENTRY_QUOTE_REQUIRED = "PEE_IU4_ENTRY_QUOTE_REQUIRED"
    PROGRESS_CONFLICT = "PEE_IU4_PROGRESS_CONFLICT"
    AUTHORITY_ROOT_MISMATCH = "PEE_IU4_AUTHORITY_ROOT_MISMATCH"
    AUTHORITY_COMMIT_MISMATCH = "PEE_IU4_AUTHORITY_COMMIT_MISMATCH"
    LIFECYCLE_OPERATION_INCOMPLETE = "PEE_IU4_LIFECYCLE_OPERATION_INCOMPLETE"
    RESOURCE_EXHAUSTED = "PEE_IU4_RESOURCE_EXHAUSTED"


class PaperAtomicCoordinatorError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


class SimulatedAtomicTransactionInterruption(RuntimeError):
    """Test-only interruption after a durable coordinator journal write."""


def _root_exclusive(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        with self._exclusive_root_lock():
            return method(self, *args, **kwargs)

    return wrapped


def _text(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{field_name} must be a string",
        )
    result = value.strip()
    if not allow_empty and not result:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{field_name} must not be empty",
        )
    return result


def _integer(value: object, field_name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{field_name} must be an integer >= {minimum}",
        )
    return value


def _boolean(value: object, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{field_name} must be boolean",
        )
    return value


def _sha256(value: object, field_name: str) -> str:
    result = _text(value, field_name).lower()
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{field_name} must be a lowercase SHA-256 hex digest",
        )
    return result


def _utc_timestamp_seconds(
    value: object,
    field_name: str,
    *,
    allow_empty: bool = False,
) -> str:
    text = _text(value, field_name, allow_empty=allow_empty)
    if not text and allow_empty:
        return ""
    try:
        parsed = datetime.fromisoformat(
            text[:-1] + "+00:00" if text.endswith("Z") else text
        )
    except ValueError as exc:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{field_name} must be an ISO-8601 timestamp",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.microsecond:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{field_name} must be timezone-aware with whole-second resolution",
        )
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.JSON_INVALID,
            f"cannot read valid JSON object from {path}",
        ) from exc
    if not isinstance(value, dict):
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.JSON_INVALID,
            f"JSON root in {path} must be an object",
        )
    return value


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        descriptor = os.open(str(directory), flags)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        _fsync_directory(path.parent)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _create_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        + "\n"
    ).encode("ascii")
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(
            str(path),
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
        created = True
        offset = 0
        while offset < len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise OSError("short Atomic V2 journal write")
            offset += written
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        _fsync_directory(path.parent)
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if created:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


@dataclass(frozen=True)
class PaperRiskStateS4V1:
    schema_version: int
    system_state_id: str
    kill_level: str
    cooldown_until_utc: str
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    position_fingerprint: str
    account_fingerprint: str
    throttle_fingerprint: str
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str
    throttle_policy_profile_id: str
    throttle_policy_model_version: str
    throttle_policy_fingerprint: str
    transaction_sequence: int
    last_transaction_event_id: str
    last_transaction_timestamp_utc: str
    last_transaction_tick_id: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "PaperRiskStateS4V1 requires schema_version 1",
            )
        for name in (
            "system_state_id",
            "economics_profile_id",
            "economics_model_version",
            "throttle_policy_profile_id",
            "throttle_policy_model_version",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        for name in (
            "position_fingerprint",
            "account_fingerprint",
            "throttle_fingerprint",
            "config_fingerprint",
            "throttle_policy_fingerprint",
        ):
            object.__setattr__(self, name, _sha256(getattr(self, name), name))

        kill_level = _text(self.kill_level, "kill_level").upper()
        if kill_level not in KILL_LEVELS:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "kill_level is unsupported",
            )
        object.__setattr__(self, "kill_level", kill_level)
        object.__setattr__(self, "entry_allowed", _boolean(self.entry_allowed, "entry_allowed"))
        object.__setattr__(self, "exit_allowed", _boolean(self.exit_allowed, "exit_allowed"))
        if not self.exit_allowed:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "S4 must never block exits",
            )
        if not isinstance(self.reason_codes, (list, tuple)):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "S4 reason_codes must be a list or tuple",
            )
        if not isinstance(self.reason_codes, tuple):
            object.__setattr__(self, "reason_codes", tuple(self.reason_codes))
        normalized_reasons = tuple(_text(reason, "reason_code") for reason in self.reason_codes)
        if len(set(normalized_reasons)) != len(normalized_reasons):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "S4 reason codes must be unique",
            )
        object.__setattr__(self, "reason_codes", normalized_reasons)
        object.__setattr__(
            self,
            "cooldown_until_utc",
            _utc_timestamp_seconds(
                self.cooldown_until_utc,
                "cooldown_until_utc",
                allow_empty=True,
            ),
        )
        if self.entry_allowed and (
            self.reason_codes or self.cooldown_until_utc or self.kill_level != "NONE"
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "entry-allowed S4 state cannot contain a blocker",
            )
        if not self.entry_allowed and not self.reason_codes:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "entry-blocked S4 state requires a reason code",
            )

        sequence = _integer(self.transaction_sequence, "transaction_sequence")
        tick_id = _integer(self.last_transaction_tick_id, "last_transaction_tick_id")
        event_id = _text(
            self.last_transaction_event_id,
            "last_transaction_event_id",
            allow_empty=True,
        )
        timestamp = _utc_timestamp_seconds(
            self.last_transaction_timestamp_utc,
            "last_transaction_timestamp_utc",
            allow_empty=True,
        )
        if sequence == 0 and (event_id or timestamp or tick_id != 0):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "initial S4 state cannot reference a transaction",
            )
        if sequence > 0 and not (event_id and timestamp):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "non-initial S4 state must reference its transaction head",
            )
        object.__setattr__(self, "transaction_sequence", sequence)
        object.__setattr__(self, "last_transaction_tick_id", tick_id)
        object.__setattr__(self, "last_transaction_event_id", event_id)
        object.__setattr__(self, "last_transaction_timestamp_utc", timestamp)

    def to_record(self) -> dict[str, Any]:
        result = {name: getattr(self, name) for name in self.__dataclass_fields__}
        result["reason_codes"] = list(self.reason_codes)
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PaperRiskStateS4V1":
        values = {name: record.get(name) for name in cls.__dataclass_fields__}
        reasons = record.get("reason_codes")
        if not isinstance(reasons, list):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "S4 reason_codes must be a list",
            )
        values["reason_codes"] = tuple(reasons)
        return cls(**values)

    @property
    def state_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class AtomicPaperStateV1:
    schema_version: int
    coordinator_id: str
    transaction_sequence: int
    last_transaction_event_id: str
    position: PositionArtifactV2
    account: PaperAccountState
    throttle: PaperEntryThrottleState
    risk: PaperRiskStateS4V1

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "AtomicPaperStateV1 requires schema_version 1",
            )
        object.__setattr__(self, "coordinator_id", _text(self.coordinator_id, "coordinator_id"))
        sequence = _integer(self.transaction_sequence, "transaction_sequence")
        event_id = _text(
            self.last_transaction_event_id,
            "last_transaction_event_id",
            allow_empty=True,
        )
        if sequence == 0 and event_id:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "initial atomic state cannot reference a transaction",
            )
        if sequence > 0 and not event_id:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "non-initial atomic state must reference its transaction head",
            )
        object.__setattr__(self, "transaction_sequence", sequence)
        object.__setattr__(self, "last_transaction_event_id", event_id)
        if not isinstance(self.position, (PositionStateS2FlatV2, PositionStateS2V2)):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic position must be a complete S2 V2 state",
            )
        if not isinstance(self.account, PaperAccountState):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic account must be PaperAccountState",
            )
        if not isinstance(self.throttle, PaperEntryThrottleState):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic throttle must be PaperEntryThrottleState",
            )
        if not isinstance(self.risk, PaperRiskStateS4V1):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic risk must be PaperRiskStateS4V1",
            )
        self._validate_cross_state_invariants()

    def _validate_cross_state_invariants(self) -> None:
        if (
            self.position.economics_profile_id != self.account.economics_profile_id
            or self.position.economics_model_version != self.account.economics_model_version
            or self.position.config_fingerprint != self.account.config_fingerprint
            or self.risk.economics_profile_id != self.account.economics_profile_id
            or self.risk.economics_model_version != self.account.economics_model_version
            or self.risk.config_fingerprint != self.account.config_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "S2, account, and S4 economics identities differ",
            )
        if (
            self.risk.throttle_policy_profile_id != self.throttle.policy_profile_id
            or self.risk.throttle_policy_model_version != self.throttle.policy_model_version
            or self.risk.throttle_policy_fingerprint != self.throttle.policy_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "S4 and throttle policy identities differ",
            )
        if (
            self.risk.position_fingerprint != self.position.state_fingerprint
            or self.risk.account_fingerprint != self.account.state_fingerprint
            or self.risk.throttle_fingerprint != self.throttle.state_fingerprint
            or self.risk.system_state_id != self.position.system_state_id
            or self.risk.transaction_sequence != self.transaction_sequence
            or self.risk.last_transaction_event_id != self.last_transaction_event_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "S4 does not bind the exact atomic component heads",
            )

        economic_transaction_count = (
            self.throttle.total_accepted_entry_count + self.account.closed_trade_count
        )
        if self.transaction_sequence < economic_transaction_count:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "transaction sequence cannot trail accepted entries plus settlements",
            )
        if isinstance(self.position, PositionStateS2FlatV2):
            if (
                self.throttle.total_accepted_entry_count != self.account.closed_trade_count
                or self.position.last_closed_trade_id
                != self.account.last_settled_trade_id
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "FLAT S2, account, and throttle heads are not in parity",
                )
        else:
            if (
                self.throttle.total_accepted_entry_count
                != self.account.closed_trade_count + 1
                or self.position.trade_id == self.account.last_settled_trade_id
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "OPEN S2, account, and throttle heads are not in parity",
                )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "coordinator_id": self.coordinator_id,
            "transaction_sequence": self.transaction_sequence,
            "last_transaction_event_id": self.last_transaction_event_id,
            "position": self.position.to_record(),
            "account": self.account.to_record(),
            "throttle": self.throttle.to_record(),
            "risk": self.risk.to_record(),
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AtomicPaperStateV1":
        position_raw = record.get("position")
        account_raw = record.get("account")
        throttle_raw = record.get("throttle")
        risk_raw = record.get("risk")
        if not all(
            isinstance(value, Mapping)
            for value in (position_raw, account_raw, throttle_raw, risk_raw)
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic state requires position, account, throttle, and risk objects",
            )
        position = parse_position_artifact(position_raw)
        if not isinstance(position, (PositionStateS2FlatV2, PositionStateS2V2)):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic state cannot contain legacy S2",
            )
        return cls(
            schema_version=record.get("schema_version"),
            coordinator_id=record.get("coordinator_id"),
            transaction_sequence=record.get("transaction_sequence"),
            last_transaction_event_id=record.get("last_transaction_event_id"),
            position=position,
            account=PaperAccountState.from_record(account_raw),
            throttle=PaperEntryThrottleState.from_record(throttle_raw),
            risk=PaperRiskStateS4V1.from_record(risk_raw),
        )

    @property
    def state_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())

    @property
    def kill_transition_count(self) -> int:
        """Number of journaled non-economic S4 KILL transitions."""
        return self.transaction_sequence - (
            self.throttle.total_accepted_entry_count + self.account.closed_trade_count
        )


def _validate_trade_matches_open(
    trade: TradeRecordV2,
    position: PositionStateS2V2,
) -> None:
    identities = (
        trade.trade_id == position.trade_id,
        trade.system_state_id != "",
        trade.symbol == position.symbol,
        trade.side == position.side,
        trade.quantity == position.quantity,
        trade.reference_entry_price == position.reference_entry_price,
        trade.modeled_entry_fill_price == position.modeled_entry_fill_price,
        trade.entry_notional_quote == position.entry_notional_quote,
        trade.entry_fee_quote == position.entry_fee_quote,
        trade.risk_budget_quote == position.risk_budget_quote,
        trade.modeled_stop_loss_quote == position.modeled_stop_loss_quote,
        trade.entry_timestamp_utc == position.entry_timestamp_utc,
        trade.entry_tick_id == position.entry_tick_id,
        trade.economics_profile_id == position.economics_profile_id,
        trade.economics_model_version == position.economics_model_version,
        trade.config_fingerprint == position.config_fingerprint,
    )
    if not all(identities):
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            "settlement trade does not exactly match the OPEN S2 economics",
        )


def _flat_position_after_trade(
    trade: TradeRecordV2,
    position: PositionStateS2V2,
) -> PositionStateS2FlatV2:
    """Derive the only valid FLAT S2 state for one settled OPEN trade."""

    _validate_trade_matches_open(trade, position)
    return PositionStateS2FlatV2(
        schema_version=2,
        system_state_id=trade.system_state_id,
        symbol=position.symbol,
        position="FLAT",
        side="",
        last_closed_trade_id=trade.trade_id,
        economics_profile_id=position.economics_profile_id,
        economics_model_version=position.economics_model_version,
        config_fingerprint=position.config_fingerprint,
    )


@dataclass(frozen=True)
class S4KillTransitionV1:
    schema_version: int
    transition_event_id: str
    from_kill_level: str
    to_kill_level: str
    reason_code: str
    authorization_reference: str
    transition_timestamp_utc: str
    transition_tick_id: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "S4KillTransitionV1 requires schema_version 1",
            )
        object.__setattr__(
            self,
            "transition_event_id",
            _text(self.transition_event_id, "transition_event_id"),
        )
        for field_name in ("from_kill_level", "to_kill_level"):
            level = _text(getattr(self, field_name), field_name).upper()
            if level not in KILL_LEVELS:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    f"{field_name} is unsupported",
                )
            object.__setattr__(self, field_name, level)
        if self.from_kill_level == self.to_kill_level:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "S4 KILL transition must change the kill level",
            )
        object.__setattr__(self, "reason_code", _text(self.reason_code, "reason_code"))
        object.__setattr__(
            self,
            "authorization_reference",
            _text(self.authorization_reference, "authorization_reference"),
        )
        object.__setattr__(
            self,
            "transition_timestamp_utc",
            _utc_timestamp_seconds(
                self.transition_timestamp_utc,
                "transition_timestamp_utc",
            ),
        )
        object.__setattr__(
            self,
            "transition_tick_id",
            _integer(self.transition_tick_id, "transition_tick_id"),
        )

    def to_record(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "S4KillTransitionV1":
        return cls(
            **{name: record.get(name) for name in cls.__dataclass_fields__}
        )


@dataclass(frozen=True)
class AtomicPaperTransactionV1:
    schema_version: int
    transaction_sequence: int
    transaction_event_id: str
    previous_transaction_event_id: str
    transaction_type: str
    transaction_timestamp_utc: str
    transaction_tick_id: int
    state_before: AtomicPaperStateV1
    state_after: AtomicPaperStateV1
    accepted_entry_event: AcceptedEntryEventV1 | None
    trade: TradeRecordV2 | None
    kill_transition: S4KillTransitionV1 | None = None

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "AtomicPaperTransactionV1 requires schema_version 1",
            )
        if not isinstance(self.state_before, AtomicPaperStateV1) or not isinstance(
            self.state_after,
            AtomicPaperStateV1,
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic transaction requires complete before/after state objects",
            )
        sequence = _integer(self.transaction_sequence, "transaction_sequence", minimum=1)
        event_id = _text(self.transaction_event_id, "transaction_event_id")
        previous_event_id = _text(
            self.previous_transaction_event_id,
            "previous_transaction_event_id",
            allow_empty=True,
        )
        transaction_type = _text(self.transaction_type, "transaction_type").upper()
        timestamp = _utc_timestamp_seconds(
            self.transaction_timestamp_utc,
            "transaction_timestamp_utc",
        )
        tick_id = _integer(self.transaction_tick_id, "transaction_tick_id")
        object.__setattr__(self, "transaction_sequence", sequence)
        object.__setattr__(self, "transaction_event_id", event_id)
        object.__setattr__(self, "previous_transaction_event_id", previous_event_id)
        object.__setattr__(self, "transaction_type", transaction_type)
        object.__setattr__(self, "transaction_timestamp_utc", timestamp)
        object.__setattr__(self, "transaction_tick_id", tick_id)

        if (
            self.state_before.coordinator_id != self.state_after.coordinator_id
            or self.state_before.transaction_sequence + 1 != sequence
            or self.state_after.transaction_sequence != sequence
            or self.state_before.last_transaction_event_id != previous_event_id
            or self.state_after.last_transaction_event_id != event_id
            or self.state_after.risk.last_transaction_timestamp_utc != timestamp
            or self.state_after.risk.last_transaction_tick_id != tick_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "transaction metadata does not match complete before/after states",
            )
        if transaction_type == TRANSACTION_OPEN:
            self._validate_open()
        elif transaction_type == TRANSACTION_CLOSE:
            self._validate_close()
        elif transaction_type == TRANSACTION_KILL:
            self._validate_kill()
        else:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "transaction_type must be OPEN, CLOSE, or KILL",
            )

    def _validate_open(self) -> None:
        if (
            not isinstance(self.state_before.position, PositionStateS2FlatV2)
            or not isinstance(self.state_after.position, PositionStateS2V2)
            or not isinstance(self.accepted_entry_event, AcceptedEntryEventV1)
            or self.trade is not None
            or self.kill_transition is not None
            or self.state_before.account != self.state_after.account
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "OPEN must atomically change only S2, throttle, and bound S4",
            )
        event = self.accepted_entry_event
        position = self.state_after.position
        if (
            event.entry_event_id != self.transaction_event_id
            or event.entry_timestamp_utc != self.transaction_timestamp_utc
            or position.entry_timestamp_utc != self.transaction_timestamp_utc
            or position.entry_tick_id != self.transaction_tick_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "OPEN transaction, throttle event, and S2 entry identities differ",
            )

    def _validate_close(self) -> None:
        if (
            not isinstance(self.state_before.position, PositionStateS2V2)
            or not isinstance(self.state_after.position, PositionStateS2FlatV2)
            or self.accepted_entry_event is not None
            or not isinstance(self.trade, TradeRecordV2)
            or self.kill_transition is not None
            or self.state_before.throttle != self.state_after.throttle
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "CLOSE must atomically change S2, account/settlement, and bound S4",
            )
        trade = self.trade
        if (
            trade.settlement_event_id != self.transaction_event_id
            or trade.exit_timestamp_utc != self.transaction_timestamp_utc
            or trade.exit_tick_id != self.transaction_tick_id
            or self.state_after.position.last_closed_trade_id != trade.trade_id
            or self.state_after.position.system_state_id != trade.system_state_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "CLOSE transaction, settlement, and FLAT S2 identities differ",
            )
        _validate_trade_matches_open(trade, self.state_before.position)

    def _validate_kill(self) -> None:
        transition = self.kill_transition
        if (
            self.accepted_entry_event is not None
            or self.trade is not None
            or not isinstance(transition, S4KillTransitionV1)
            or self.state_before.position != self.state_after.position
            or self.state_before.account != self.state_after.account
            or self.state_before.throttle != self.state_after.throttle
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "KILL must atomically change only the bound S4 state",
            )
        if (
            transition.transition_event_id != self.transaction_event_id
            or transition.transition_timestamp_utc
            != self.transaction_timestamp_utc
            or transition.transition_tick_id != self.transaction_tick_id
            or transition.from_kill_level != self.state_before.risk.kill_level
            or transition.to_kill_level != self.state_after.risk.kill_level
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "KILL transaction and S4 transition identities differ",
            )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_type": ARTIFACT_ATOMIC_TRANSACTION,
            "transaction_sequence": self.transaction_sequence,
            "transaction_event_id": self.transaction_event_id,
            "previous_transaction_event_id": self.previous_transaction_event_id,
            "transaction_type": self.transaction_type,
            "transaction_timestamp_utc": self.transaction_timestamp_utc,
            "transaction_tick_id": self.transaction_tick_id,
            "state_before": self.state_before.to_record(),
            "state_after": self.state_after.to_record(),
            "accepted_entry_event": (
                None
                if self.accepted_entry_event is None
                else self.accepted_entry_event.to_record()
            ),
            "trade": None if self.trade is None else self.trade.to_record(),
            "kill_transition": (
                None
                if self.kill_transition is None
                else self.kill_transition.to_record()
            ),
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AtomicPaperTransactionV1":
        if record.get("artifact_type") != ARTIFACT_ATOMIC_TRANSACTION:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic transaction artifact type is invalid",
            )
        before_raw = record.get("state_before")
        after_raw = record.get("state_after")
        entry_raw = record.get("accepted_entry_event")
        trade_raw = record.get("trade")
        kill_raw = record.get("kill_transition")
        if not isinstance(before_raw, Mapping) or not isinstance(after_raw, Mapping):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic transaction requires complete before/after states",
            )
        if entry_raw is not None and not isinstance(entry_raw, Mapping):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "accepted_entry_event must be an object or null",
            )
        if trade_raw is not None and not isinstance(trade_raw, Mapping):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "trade must be an object or null",
            )
        if kill_raw is not None and not isinstance(kill_raw, Mapping):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "kill_transition must be an object or null",
            )
        return cls(
            schema_version=record.get("schema_version"),
            transaction_sequence=record.get("transaction_sequence"),
            transaction_event_id=record.get("transaction_event_id"),
            previous_transaction_event_id=record.get("previous_transaction_event_id"),
            transaction_type=record.get("transaction_type"),
            transaction_timestamp_utc=record.get("transaction_timestamp_utc"),
            transaction_tick_id=record.get("transaction_tick_id"),
            state_before=AtomicPaperStateV1.from_record(before_raw),
            state_after=AtomicPaperStateV1.from_record(after_raw),
            accepted_entry_event=(
                None
                if entry_raw is None
                else AcceptedEntryEventV1.from_record(entry_raw)
            ),
            trade=None if trade_raw is None else TradeRecordV2.from_record(trade_raw),
            kill_transition=(
                None
                if kill_raw is None
                else S4KillTransitionV1.from_record(kill_raw)
            ),
        )

    @property
    def transaction_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class AtomicCommitResult:
    state: AtomicPaperStateV1
    journal_path: Path
    newly_committed: bool
    already_committed: bool
    recovered_incomplete_commit: bool


@dataclass(frozen=True)
class AtomicRecoveryResult:
    state: AtomicPaperStateV1
    journal_count: int
    recovered_transaction_count: int


@dataclass(frozen=True)
class AtomicReconciliationReport:
    consistent: bool
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    snapshot_transaction_sequence: int
    journal_transaction_count: int
    current_position: str


class PaperAtomicCoordinator:
    """Single-writer logical transaction owner for inactive Paper state."""

    def __init__(
        self,
        root_directory: str | Path,
        config: PaperEconomicsConfig,
        throttle_policy: PaperEntryThrottlePolicy,
        *,
        coordinator_id: str,
        symbol: str,
    ) -> None:
        self.root_directory = Path(root_directory)
        self.config = config
        self.throttle_policy = throttle_policy
        self.coordinator_id = _text(coordinator_id, "coordinator_id")
        self.symbol = _text(symbol, "symbol")
        self.state_path = self.root_directory / "paper_atomic_state.json"
        self.transaction_directory = self.root_directory / "paper_atomic_transactions"

    def _ensure_identity(self, state: AtomicPaperStateV1) -> None:
        if (
            isinstance(state.account.schema_version, bool)
            or not isinstance(state.account.schema_version, int)
            or state.account.schema_version != 1
            or state.coordinator_id != self.coordinator_id
            or state.position.symbol != self.symbol
            or state.position.economics_profile_id != self.config.economics_profile_id
            or state.position.economics_model_version != self.config.economics_model_version
            or state.position.config_fingerprint != self.config.config_fingerprint
            or state.account.quote_currency != self.config.quote_currency
            or state.account.economics_profile_id != self.config.economics_profile_id
            or state.account.economics_model_version != self.config.economics_model_version
            or state.account.config_fingerprint != self.config.config_fingerprint
            or state.throttle.policy_profile_id != self.throttle_policy.policy_profile_id
            or state.throttle.policy_model_version != self.throttle_policy.policy_model_version
            or state.throttle.policy_fingerprint != self.throttle_policy.policy_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "atomic state does not match coordinator identities",
            )

    @staticmethod
    def _unique_reasons(*groups: tuple[str, ...]) -> tuple[str, ...]:
        result: list[str] = []
        for group in groups:
            for reason in group:
                if reason not in result:
                    result.append(reason)
        return tuple(result)

    def _build_risk(
        self,
        *,
        position: PositionArtifactV2,
        account: PaperAccountState,
        throttle: PaperEntryThrottleState,
        transaction_sequence: int,
        event_id: str,
        timestamp_utc: str,
        tick_id: int,
        kill_level: str,
    ) -> PaperRiskStateS4V1:
        timestamp = _utc_timestamp_seconds(timestamp_utc, "timestamp_utc")
        account_decision = evaluate_account_entry_guard(
            account,
            self.config,
            entry_timestamp_utc=timestamp,
        )
        throttle_decision = evaluate_entry_throttle(
            throttle,
            self.throttle_policy,
            entry_timestamp_utc=timestamp,
        )
        normalized_kill_level = _text(kill_level, "kill_level").upper()
        kill_reasons = (
            ()
            if normalized_kill_level == "NONE"
            else (f"PEE_S4_KILL_{normalized_kill_level}",)
        )
        position_reasons = (
            (POSITION_OPEN_REASON,)
            if isinstance(position, PositionStateS2V2)
            else ()
        )
        reasons = self._unique_reasons(
            account_decision.reason_codes,
            throttle_decision.reason_codes,
            kill_reasons,
            position_reasons,
        )
        return PaperRiskStateS4V1(
            schema_version=1,
            system_state_id=position.system_state_id,
            kill_level=normalized_kill_level,
            cooldown_until_utc=throttle_decision.disable_until_utc or "",
            entry_allowed=not reasons,
            exit_allowed=True,
            reason_codes=reasons,
            position_fingerprint=position.state_fingerprint,
            account_fingerprint=account.state_fingerprint,
            throttle_fingerprint=throttle.state_fingerprint,
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
            throttle_policy_profile_id=self.throttle_policy.policy_profile_id,
            throttle_policy_model_version=self.throttle_policy.policy_model_version,
            throttle_policy_fingerprint=self.throttle_policy.policy_fingerprint,
            transaction_sequence=transaction_sequence,
            last_transaction_event_id=event_id,
            last_transaction_timestamp_utc=(
                "" if transaction_sequence == 0 else timestamp
            ),
            last_transaction_tick_id=(0 if transaction_sequence == 0 else tick_id),
        )

    def initialize(
        self,
        *,
        position: PositionStateS2FlatV2,
        account: PaperAccountState,
        throttle: PaperEntryThrottleState,
        kill_level: str = "NONE",
    ) -> AtomicPaperStateV1:
        if (
            not isinstance(position, PositionStateS2FlatV2)
            or not isinstance(account, PaperAccountState)
            or not isinstance(throttle, PaperEntryThrottleState)
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic initialization requires FLAT, account, and throttle objects",
            )
        if (
            account.closed_trade_count != 0
            or throttle.total_accepted_entry_count != 0
            or position.last_closed_trade_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic coordinator initialization requires empty FLAT components",
            )
        initial_timestamp = f"{throttle.utc_day}T00:00:00Z"
        risk = self._build_risk(
            position=position,
            account=account,
            throttle=throttle,
            transaction_sequence=0,
            event_id="",
            timestamp_utc=initial_timestamp,
            tick_id=0,
            kill_level=kill_level,
        )
        state = AtomicPaperStateV1(
            schema_version=1,
            coordinator_id=self.coordinator_id,
            transaction_sequence=0,
            last_transaction_event_id="",
            position=position,
            account=account,
            throttle=throttle,
            risk=risk,
        )
        self._ensure_identity(state)
        if self.state_path.exists():
            existing = self.load_state()
            if existing == state:
                return existing
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.STATE_ALREADY_INITIALIZED,
                "atomic coordinator already exists with different state",
            )
        if self.transaction_directory.exists() and any(
            self.transaction_directory.glob("*.json")
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                "cannot initialize while atomic transaction journal is non-empty",
            )
        _atomic_write_json(self.state_path, state.to_record())
        return state

    def load_state(self) -> AtomicPaperStateV1:
        if not self.state_path.exists():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.STATE_MISSING,
                "atomic coordinator has not been initialized",
            )
        state = AtomicPaperStateV1.from_record(_read_json_object(self.state_path))
        self._ensure_identity(state)
        return state

    def evaluate_entry_block_reasons(
        self,
        *,
        entry_timestamp_utc: str,
    ) -> tuple[str, ...]:
        """Evaluate current entry guards at the candidate event time."""

        current = self.load_state()
        candidate_risk = self._build_risk(
            position=current.position,
            account=current.account,
            throttle=current.throttle,
            transaction_sequence=current.transaction_sequence,
            event_id=current.last_transaction_event_id,
            timestamp_utc=entry_timestamp_utc,
            tick_id=current.risk.last_transaction_tick_id,
            kill_level=current.risk.kill_level,
        )
        return candidate_risk.reason_codes

    def _journal_path(self, sequence: int, event_id: str) -> Path:
        event_hash = hashlib.sha256(event_id.encode("utf-8")).hexdigest()[:20]
        return self.transaction_directory / f"{sequence:020d}_{event_hash}.json"

    def _validate_semantics(self, transaction: AtomicPaperTransactionV1) -> None:
        self._ensure_identity(transaction.state_before)
        self._ensure_identity(transaction.state_after)
        before = transaction.state_before
        after = transaction.state_after
        kill_level = before.risk.kill_level
        if (
            transaction.transaction_type != TRANSACTION_KILL
            and after.risk.kill_level != kill_level
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "OPEN/CLOSE transaction cannot silently change S4 kill level",
            )
        if transaction.transaction_type == TRANSACTION_OPEN:
            event = transaction.accepted_entry_event
            assert event is not None
            pre_risk = self._build_risk(
                position=before.position,
                account=before.account,
                throttle=before.throttle,
                transaction_sequence=before.transaction_sequence,
                event_id=before.last_transaction_event_id,
                timestamp_utc=event.entry_timestamp_utc,
                tick_id=before.risk.last_transaction_tick_id,
                kill_level=kill_level,
            )
            if not pre_risk.entry_allowed:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                    f"OPEN is blocked by {pre_risk.reason_codes[0]}",
                )
            try:
                expected_throttle = apply_accepted_entry(
                    before.throttle,
                    self.throttle_policy,
                    event,
                )
            except PaperEntryThrottleError as exc:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "OPEN throttle transition is not reproducible",
                ) from exc
            if expected_throttle != after.throttle:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "OPEN throttle state_after is not reproducible",
                )
        elif transaction.transaction_type == TRANSACTION_CLOSE:
            trade = transaction.trade
            assert trade is not None
            try:
                expected_account = apply_trade_to_account(before.account, trade)
            except PaperArtifactError as exc:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "CLOSE account settlement is not reproducible",
                ) from exc
            if expected_account != after.account:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "CLOSE account state_after is not reproducible",
                )
        else:
            transition = transaction.kill_transition
            assert transition is not None
            if transition.from_kill_level != kill_level:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "KILL transition was not built from the current S4 kill level",
                )
            kill_level = transition.to_kill_level

        expected_risk = self._build_risk(
            position=after.position,
            account=after.account,
            throttle=after.throttle,
            transaction_sequence=after.transaction_sequence,
            event_id=after.last_transaction_event_id,
            timestamp_utc=transaction.transaction_timestamp_utc,
            tick_id=transaction.transaction_tick_id,
            kill_level=kill_level,
        )
        if expected_risk != after.risk:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "S4 state_after is not reproducible from atomic components",
            )

    def _load_transaction(self, path: Path) -> AtomicPaperTransactionV1:
        transaction = AtomicPaperTransactionV1.from_record(_read_json_object(path))
        self._validate_semantics(transaction)
        return transaction

    def _journal_transactions(self) -> list[tuple[Path, AtomicPaperTransactionV1]]:
        if not self.transaction_directory.exists():
            return []
        entries = [
            (path, self._load_transaction(path))
            for path in sorted(self.transaction_directory.glob("*.json"))
        ]
        previous: AtomicPaperTransactionV1 | None = None
        event_ids: set[str] = set()
        trade_ids: set[str] = set()
        open_trade_ids: set[str] = set()
        for expected_sequence, (path, transaction) in enumerate(entries, start=1):
            if transaction.transaction_sequence != expected_sequence:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_GAP,
                    "atomic transaction sequence is not contiguous",
                )
            if path != self._journal_path(
                transaction.transaction_sequence,
                transaction.transaction_event_id,
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "atomic transaction filename does not match its identity",
                )
            if transaction.transaction_event_id in event_ids:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "atomic transaction event ID is duplicated",
                )
            event_ids.add(transaction.transaction_event_id)
            if transaction.transaction_type == TRANSACTION_OPEN:
                trade_id = transaction.state_after.position.trade_id
                if trade_id in open_trade_ids:
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                        "S2 trade ID is duplicated",
                    )
                open_trade_ids.add(trade_id)
            elif transaction.transaction_type == TRANSACTION_CLOSE:
                assert transaction.trade is not None
                if transaction.trade.trade_id in trade_ids:
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                        "settlement trade ID is duplicated",
                    )
                trade_ids.add(transaction.trade.trade_id)
            if previous is None:
                if transaction.previous_transaction_event_id:
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.JOURNAL_GAP,
                        "first atomic transaction references a predecessor",
                    )
            elif (
                transaction.previous_transaction_event_id
                != previous.transaction_event_id
                or transaction.state_before != previous.state_after
                or transaction.transaction_timestamp_utc
                < previous.transaction_timestamp_utc
                or transaction.transaction_tick_id < previous.transaction_tick_id
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_GAP,
                    "atomic before/after, event, time, or tick chain is broken",
                )
            previous = transaction
        return entries

    def transaction_by_event_id(
        self,
        transaction_event_id: str,
    ) -> AtomicPaperTransactionV1 | None:
        """Return one validated transaction without mutating coordinator state."""
        event_id = _text(transaction_event_id, "transaction_event_id")
        return next(
            (
                transaction
                for _, transaction in self._journal_transactions()
                if transaction.transaction_event_id == event_id
            ),
            None,
        )

    @staticmethod
    def _snapshot_index(
        current: AtomicPaperStateV1,
        entries: list[tuple[Path, AtomicPaperTransactionV1]],
    ) -> int | None:
        sequence = current.transaction_sequence
        if sequence > len(entries):
            return None
        if sequence == 0:
            if entries and current != entries[0][1].state_before:
                return None
            return 0
        if current != entries[sequence - 1][1].state_after:
            return None
        return sequence

    def _commit(
        self,
        transaction: AtomicPaperTransactionV1,
        *,
        simulate_interruption_after_journal: bool,
    ) -> AtomicCommitResult:
        current = self.load_state()
        entries = self._journal_transactions()
        duplicate = next(
            (
                (path, existing)
                for path, existing in entries
                if existing.transaction_event_id == transaction.transaction_event_id
            ),
            None,
        )
        if duplicate is not None:
            path, existing = duplicate
            if existing.transaction_fingerprint != transaction.transaction_fingerprint:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same atomic event contains different transaction data",
                )
            if current == entries[-1][1].state_after:
                return AtomicCommitResult(
                    state=current,
                    journal_path=path,
                    newly_committed=False,
                    already_committed=True,
                    recovered_incomplete_commit=False,
                )
            if current == existing.state_before and existing == entries[-1][1]:
                _atomic_write_json(self.state_path, existing.state_after.to_record())
                return AtomicCommitResult(
                    state=existing.state_after,
                    journal_path=path,
                    newly_committed=False,
                    already_committed=False,
                    recovered_incomplete_commit=True,
                )
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.RECOVERY_REQUIRED,
                "atomic journal requires full recovery",
            )

        snapshot_index = self._snapshot_index(current, entries)
        if snapshot_index is None:
            reason = (
                AtomicCoordinatorReasonCode.STATE_AHEAD_OF_JOURNAL
                if current.transaction_sequence > len(entries)
                else AtomicCoordinatorReasonCode.JOURNAL_CONFLICT
            )
            raise PaperAtomicCoordinatorError(
                reason,
                "atomic snapshot is not a valid journal prefix",
            )
        if snapshot_index != len(entries):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.RECOVERY_REQUIRED,
                "atomic journal is ahead of its snapshot",
            )
        if transaction.state_before != current:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic transaction was not built from the current state",
            )
        if entries and (
            transaction.transaction_timestamp_utc
            < entries[-1][1].transaction_timestamp_utc
            or transaction.transaction_tick_id < entries[-1][1].transaction_tick_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic transaction time/tick must not regress",
            )
        self._validate_semantics(transaction)
        journal_path = self._journal_path(
            transaction.transaction_sequence,
            transaction.transaction_event_id,
        )
        _atomic_write_json(journal_path, transaction.to_record())
        if simulate_interruption_after_journal:
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption after durable atomic journal write"
            )
        _atomic_write_json(self.state_path, transaction.state_after.to_record())
        return AtomicCommitResult(
            state=transaction.state_after,
            journal_path=journal_path,
            newly_committed=True,
            already_committed=False,
            recovered_incomplete_commit=False,
        )

    def commit_open(
        self,
        *,
        position_after: PositionStateS2V2,
        accepted_entry_event: AcceptedEntryEventV1,
        transition_tick_id: int,
        simulate_interruption_after_journal: bool = False,
    ) -> AtomicCommitResult:
        current = self.load_state()
        if not isinstance(position_after, PositionStateS2V2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "commit_open requires a complete OPEN S2 state",
            )
        if not isinstance(accepted_entry_event, AcceptedEntryEventV1):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "commit_open requires AcceptedEntryEventV1",
            )
        entries = self._journal_transactions()
        duplicate = next(
            (
                existing
                for _, existing in entries
                if existing.transaction_event_id
                == accepted_entry_event.entry_event_id
            ),
            None,
        )
        if duplicate is not None:
            if (
                duplicate.transaction_type != TRANSACTION_OPEN
                or duplicate.accepted_entry_event != accepted_entry_event
                or duplicate.state_after.position != position_after
                or duplicate.transaction_tick_id != transition_tick_id
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same OPEN event contains different transaction data",
                )
            return self._commit(
                duplicate,
                simulate_interruption_after_journal=False,
            )
        try:
            throttle_after = apply_accepted_entry(
                current.throttle,
                self.throttle_policy,
                accepted_entry_event,
            )
        except PaperEntryThrottleError as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "OPEN is rejected by the entry throttle",
            ) from exc
        sequence = current.transaction_sequence + 1
        event_id = accepted_entry_event.entry_event_id
        timestamp = accepted_entry_event.entry_timestamp_utc
        tick_id = _integer(transition_tick_id, "transition_tick_id")
        risk_after = self._build_risk(
            position=position_after,
            account=current.account,
            throttle=throttle_after,
            transaction_sequence=sequence,
            event_id=event_id,
            timestamp_utc=timestamp,
            tick_id=tick_id,
            kill_level=current.risk.kill_level,
        )
        state_after = AtomicPaperStateV1(
            schema_version=1,
            coordinator_id=self.coordinator_id,
            transaction_sequence=sequence,
            last_transaction_event_id=event_id,
            position=position_after,
            account=current.account,
            throttle=throttle_after,
            risk=risk_after,
        )
        transaction = AtomicPaperTransactionV1(
            schema_version=1,
            transaction_sequence=sequence,
            transaction_event_id=event_id,
            previous_transaction_event_id=current.last_transaction_event_id,
            transaction_type=TRANSACTION_OPEN,
            transaction_timestamp_utc=timestamp,
            transaction_tick_id=tick_id,
            state_before=current,
            state_after=state_after,
            accepted_entry_event=accepted_entry_event,
            trade=None,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
        )

    def commit_close(
        self,
        *,
        position_after: PositionStateS2FlatV2,
        trade: TradeRecordV2,
        simulate_interruption_after_journal: bool = False,
    ) -> AtomicCommitResult:
        current = self.load_state()
        if not isinstance(position_after, PositionStateS2FlatV2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "commit_close requires a complete FLAT S2 state",
            )
        if not isinstance(trade, TradeRecordV2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "commit_close requires TradeRecordV2",
            )
        if (
            isinstance(trade.schema_version, bool)
            or not isinstance(trade.schema_version, int)
            or trade.schema_version != 2
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "atomic settlement requires integer trade schema_version 2",
            )
        entries = self._journal_transactions()
        duplicate = next(
            (
                existing
                for _, existing in entries
                if existing.transaction_event_id == trade.settlement_event_id
            ),
            None,
        )
        if duplicate is not None:
            if (
                duplicate.transaction_type != TRANSACTION_CLOSE
                or duplicate.trade != trade
                or duplicate.state_after.position != position_after
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same CLOSE event contains different transaction data",
                )
            return self._commit(
                duplicate,
                simulate_interruption_after_journal=False,
            )
        try:
            account_after = apply_trade_to_account(current.account, trade)
        except PaperArtifactError as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "CLOSE settlement cannot be applied to the current account",
            ) from exc
        sequence = current.transaction_sequence + 1
        event_id = trade.settlement_event_id
        timestamp = _utc_timestamp_seconds(trade.exit_timestamp_utc, "exit_timestamp_utc")
        if trade.exit_timestamp_utc != timestamp:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "trade exit timestamp must be canonical UTC seconds",
            )
        risk_after = self._build_risk(
            position=position_after,
            account=account_after,
            throttle=current.throttle,
            transaction_sequence=sequence,
            event_id=event_id,
            timestamp_utc=timestamp,
            tick_id=trade.exit_tick_id,
            kill_level=current.risk.kill_level,
        )
        state_after = AtomicPaperStateV1(
            schema_version=1,
            coordinator_id=self.coordinator_id,
            transaction_sequence=sequence,
            last_transaction_event_id=event_id,
            position=position_after,
            account=account_after,
            throttle=current.throttle,
            risk=risk_after,
        )
        transaction = AtomicPaperTransactionV1(
            schema_version=1,
            transaction_sequence=sequence,
            transaction_event_id=event_id,
            previous_transaction_event_id=current.last_transaction_event_id,
            transaction_type=TRANSACTION_CLOSE,
            transaction_timestamp_utc=timestamp,
            transaction_tick_id=trade.exit_tick_id,
            state_before=current,
            state_after=state_after,
            accepted_entry_event=None,
            trade=trade,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
        )

    def commit_kill_transition(
        self,
        *,
        transition_event_id: str,
        expected_from_kill_level: str,
        target_kill_level: str,
        reason_code: str,
        authorization_reference: str,
        transition_timestamp_utc: str,
        transition_tick_id: int,
        simulate_interruption_after_journal: bool = False,
    ) -> AtomicCommitResult:
        """Durably publish one explicit, authorized S4 kill-level transition."""
        transition = S4KillTransitionV1(
            schema_version=1,
            transition_event_id=transition_event_id,
            from_kill_level=expected_from_kill_level,
            to_kill_level=target_kill_level,
            reason_code=reason_code,
            authorization_reference=authorization_reference,
            transition_timestamp_utc=transition_timestamp_utc,
            transition_tick_id=transition_tick_id,
        )
        current = self.load_state()
        entries = self._journal_transactions()
        duplicate = next(
            (
                existing
                for _, existing in entries
                if existing.transaction_event_id == transition.transition_event_id
            ),
            None,
        )
        if duplicate is not None:
            if (
                duplicate.transaction_type != TRANSACTION_KILL
                or duplicate.kill_transition != transition
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same KILL event contains different transition data",
                )
            return self._commit(
                duplicate,
                simulate_interruption_after_journal=False,
            )
        if current.risk.kill_level != transition.from_kill_level:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "current S4 kill level does not match expected_from_kill_level",
            )

        sequence = current.transaction_sequence + 1
        risk_after = self._build_risk(
            position=current.position,
            account=current.account,
            throttle=current.throttle,
            transaction_sequence=sequence,
            event_id=transition.transition_event_id,
            timestamp_utc=transition.transition_timestamp_utc,
            tick_id=transition.transition_tick_id,
            kill_level=transition.to_kill_level,
        )
        state_after = AtomicPaperStateV1(
            schema_version=1,
            coordinator_id=self.coordinator_id,
            transaction_sequence=sequence,
            last_transaction_event_id=transition.transition_event_id,
            position=current.position,
            account=current.account,
            throttle=current.throttle,
            risk=risk_after,
        )
        transaction = AtomicPaperTransactionV1(
            schema_version=1,
            transaction_sequence=sequence,
            transaction_event_id=transition.transition_event_id,
            previous_transaction_event_id=current.last_transaction_event_id,
            transaction_type=TRANSACTION_KILL,
            transaction_timestamp_utc=transition.transition_timestamp_utc,
            transaction_tick_id=transition.transition_tick_id,
            state_before=current,
            state_after=state_after,
            accepted_entry_event=None,
            trade=None,
            kill_transition=transition,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
        )

    def reconciliation_report(self) -> AtomicReconciliationReport:
        try:
            current = self.load_state()
            entries = self._journal_transactions()
            snapshot_index = self._snapshot_index(current, entries)
            if snapshot_index is None:
                reason = (
                    AtomicCoordinatorReasonCode.STATE_AHEAD_OF_JOURNAL
                    if current.transaction_sequence > len(entries)
                    else AtomicCoordinatorReasonCode.JOURNAL_CONFLICT
                )
                raise PaperAtomicCoordinatorError(
                    reason,
                    "atomic snapshot is not a valid journal prefix",
                )
            if snapshot_index != len(entries):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.RECOVERY_REQUIRED,
                    "atomic transaction journal is ahead of its snapshot",
                )
        except (
            PaperAtomicCoordinatorError,
            PaperArtifactError,
            PaperEntryThrottleError,
        ) as exc:
            return AtomicReconciliationReport(
                consistent=False,
                entry_allowed=False,
                exit_allowed=True,
                reason_codes=(
                    getattr(
                        exc,
                        "reason_code",
                        AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    ),
                ),
                snapshot_transaction_sequence=0,
                journal_transaction_count=0,
                current_position="UNKNOWN",
            )
        return AtomicReconciliationReport(
            consistent=True,
            entry_allowed=current.risk.entry_allowed,
            exit_allowed=True,
            reason_codes=current.risk.reason_codes,
            snapshot_transaction_sequence=current.transaction_sequence,
            journal_transaction_count=len(entries),
            current_position=current.position.position,
        )

    def recover(self) -> AtomicRecoveryResult:
        current = self.load_state()
        entries = self._journal_transactions()
        snapshot_index = self._snapshot_index(current, entries)
        if snapshot_index is None:
            reason = (
                AtomicCoordinatorReasonCode.STATE_AHEAD_OF_JOURNAL
                if current.transaction_sequence > len(entries)
                else AtomicCoordinatorReasonCode.JOURNAL_CONFLICT
            )
            raise PaperAtomicCoordinatorError(
                reason,
                "atomic snapshot is not a valid journal prefix",
            )
        recovered_count = len(entries) - snapshot_index
        if recovered_count == 0:
            return AtomicRecoveryResult(
                state=current,
                journal_count=len(entries),
                recovered_transaction_count=0,
            )
        recovered_state = entries[-1][1].state_after
        _atomic_write_json(self.state_path, recovered_state.to_record())
        return AtomicRecoveryResult(
            state=recovered_state,
            journal_count=len(entries),
            recovered_transaction_count=recovered_count,
        )


def _strict_record_fields(
    record: Mapping[str, Any],
    expected: set[str],
    label: str,
) -> None:
    if not isinstance(record, Mapping) or set(record) != expected:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
            f"{label} fields are incomplete or unknown",
        )


def _canonical_read_json_object(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.JSON_INVALID,
            f"cannot read canonical JSON object from {path}",
        ) from exc
    if not isinstance(value, dict):
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.JSON_INVALID,
            f"JSON root in {path} must be an object",
        )
    expected = (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        + b"\n"
    )
    if raw != expected:
        raise PaperAtomicCoordinatorError(
            AtomicCoordinatorReasonCode.JSON_INVALID,
            f"JSON bytes in {path} are not canonical",
        )
    return value


@dataclass(frozen=True)
class AtomicProgressCursorV1:
    schema_version: int
    snapshot_id: str
    timestamp_utc: str
    tick_id: int
    intent_id: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "AtomicProgressCursorV1 requires schema_version 1",
            )
        snapshot = _text(self.snapshot_id, "snapshot_id", allow_empty=True)
        timestamp = _utc_timestamp_seconds(
            self.timestamp_utc,
            "timestamp_utc",
            allow_empty=True,
        )
        tick = _integer(self.tick_id, "tick_id")
        intent = _text(self.intent_id, "intent_id", allow_empty=True)
        empty = not any((snapshot, timestamp, tick, intent))
        complete = bool(snapshot and timestamp and intent and tick >= 0)
        if not empty and not complete:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                "progress cursor must be either initial or complete",
            )
        object.__setattr__(self, "snapshot_id", snapshot)
        object.__setattr__(self, "timestamp_utc", timestamp)
        object.__setattr__(self, "tick_id", tick)
        object.__setattr__(self, "intent_id", intent)

    @classmethod
    def initial(cls) -> "AtomicProgressCursorV1":
        return cls(
            schema_version=1,
            snapshot_id="",
            timestamp_utc="",
            tick_id=0,
            intent_id="",
        )

    def canonical_payload(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "snapshot_id": self.snapshot_id,
            "timestamp_utc": self.timestamp_utc,
            "tick_id": self.tick_id,
            "intent_id": self.intent_id,
        }
        return payload

    @property
    def cursor_fingerprint(self) -> str:
        return canonical_json_sha256(self.canonical_payload())

    def to_record(self) -> dict[str, Any]:
        result = self.canonical_payload()
        result["cursor_fingerprint"] = self.cursor_fingerprint
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AtomicProgressCursorV1":
        _strict_record_fields(
            record,
            {
                "schema_version",
                "snapshot_id",
                "timestamp_utc",
                "tick_id",
                "intent_id",
                "cursor_fingerprint",
            },
            "progress cursor",
        )
        cursor = cls(
            schema_version=record.get("schema_version"),
            snapshot_id=record.get("snapshot_id"),
            timestamp_utc=record.get("timestamp_utc"),
            tick_id=record.get("tick_id"),
            intent_id=record.get("intent_id"),
        )
        if _sha256(record.get("cursor_fingerprint"), "cursor_fingerprint") != cursor.cursor_fingerprint:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                "progress cursor fingerprint mismatch",
            )
        if dict(record) != cursor.to_record():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                "progress cursor record is not canonical",
            )
        return cursor


@dataclass(frozen=True)
class AtomicEntryDenialProvenanceV1:
    schema_version: int
    artifact_type: str
    transaction_event_id: str
    snapshot_id: str
    timestamp_utc: str
    tick_id: int
    intent_id: str
    intent_action: str
    state_before_fingerprint: str
    denial_origin: str
    denial_reason_code: str
    entry_capability_allowed: bool

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "AtomicEntryDenialProvenanceV1 requires schema_version 1",
            )
        if (
            type(self.artifact_type) is not str
            or self.artifact_type != ENTRY_DENIAL_PROVENANCE_ARTIFACT
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "Atomic entry-denial provenance artifact type is unsupported",
            )
        for name in (
            "transaction_event_id",
            "snapshot_id",
            "intent_id",
        ):
            value = getattr(self, name)
            if type(value) is not str or not value or value != value.strip():
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    f"{name} must be nonempty canonical text",
                )
        if type(self.timestamp_utc) is not str or (
            _utc_timestamp_seconds(self.timestamp_utc, "timestamp_utc")
            != self.timestamp_utc
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "timestamp_utc must be canonical UTC seconds",
            )
        if type(self.tick_id) is not int or self.tick_id < 0:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "tick_id must be an exact non-negative integer",
            )
        if type(self.intent_action) is not str or self.intent_action not in (
            "OPEN_LONG",
            "OPEN_SHORT",
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "intent_action must be OPEN_LONG or OPEN_SHORT",
            )
        if (
            type(self.state_before_fingerprint) is not str
            or _sha256(
                self.state_before_fingerprint,
                "state_before_fingerprint",
            )
            != self.state_before_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "state_before_fingerprint must be canonical lowercase SHA-256",
            )
        if type(self.denial_origin) is not str or (
            self.denial_origin not in ENTRY_DENIAL_ORIGINS
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "denial_origin is unsupported",
            )
        if (
            type(self.denial_reason_code) is not str
            or self.denial_reason_code != "PEE_IU4_ENTRY_BLOCKED"
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "denial_reason_code must be PEE_IU4_ENTRY_BLOCKED",
            )
        if type(self.entry_capability_allowed) is not bool:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "entry_capability_allowed must be an exact bool",
            )

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_type": self.artifact_type,
            "transaction_event_id": self.transaction_event_id,
            "snapshot_id": self.snapshot_id,
            "timestamp_utc": self.timestamp_utc,
            "tick_id": self.tick_id,
            "intent_id": self.intent_id,
            "intent_action": self.intent_action,
            "state_before_fingerprint": self.state_before_fingerprint,
            "denial_origin": self.denial_origin,
            "denial_reason_code": self.denial_reason_code,
            "entry_capability_allowed": self.entry_capability_allowed,
        }

    @property
    def provenance_fingerprint(self) -> str:
        return canonical_json_sha256(self.canonical_payload())

    def to_record(self) -> dict[str, Any]:
        record = self.canonical_payload()
        record["provenance_fingerprint"] = self.provenance_fingerprint
        return record

    @classmethod
    def from_record(
        cls,
        record: Mapping[str, Any],
    ) -> "AtomicEntryDenialProvenanceV1":
        _strict_record_fields(
            record,
            set(cls.__dataclass_fields__) | {"provenance_fingerprint"},
            "entry-denial provenance",
        )
        provenance = cls(
            **{name: record.get(name) for name in cls.__dataclass_fields__}
        )
        if (
            type(record.get("provenance_fingerprint")) is not str
            or _sha256(
                record.get("provenance_fingerprint"),
                "provenance_fingerprint",
            )
            != provenance.provenance_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                "entry-denial provenance fingerprint mismatch",
            )
        if dict(record) != provenance.to_record():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "entry-denial provenance record is not canonical",
            )
        return provenance


@dataclass(frozen=True)
class AtomicEntryVetoCandidateV1:
    schema_version: int
    candidate_id: str
    entry_veto_event_id: str
    snapshot_id: str
    timestamp_utc: str
    tick_id: int
    intent_id: str
    intent_action: str
    symbol: str
    side: str
    loss_cluster_state_fingerprint: str
    denial_reason_code: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "AtomicEntryVetoCandidateV1 requires schema_version 1",
            )
        event_id = _text(self.entry_veto_event_id, "entry_veto_event_id")
        snapshot_id = _text(self.snapshot_id, "snapshot_id")
        timestamp = _utc_timestamp_seconds(self.timestamp_utc, "timestamp_utc")
        tick_id = _integer(self.tick_id, "tick_id", minimum=0)
        intent_id = _text(self.intent_id, "intent_id")
        action = _text(self.intent_action, "intent_action").upper()
        symbol = _text(self.symbol, "symbol").upper()
        side = _text(self.side, "side").upper()
        loss_fingerprint = _sha256(
            self.loss_cluster_state_fingerprint,
            "loss_cluster_state_fingerprint",
        )
        denial = _text(self.denial_reason_code, "denial_reason_code").upper()
        if action not in ("OPEN_LONG", "OPEN_SHORT"):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "ENTRY_VETO candidate must be OPEN_LONG or OPEN_SHORT",
            )
        expected_side = "LONG" if action == "OPEN_LONG" else "SHORT"
        if side != expected_side or denial != "PEE_LOSS_CLUSTER_ENTRY_VETO":
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "ENTRY_VETO candidate side or denial reason is invalid",
            )
        identity_material = {
            "schema_version": 1,
            "entry_veto_event_id": event_id,
            "snapshot_id": snapshot_id,
            "timestamp_utc": timestamp,
            "tick_id": tick_id,
            "intent_id": intent_id,
            "intent_action": action,
            "symbol": symbol,
            "side": side,
            "loss_cluster_state_fingerprint": loss_fingerprint,
            "denial_reason_code": denial,
        }
        expected_candidate_id = (
            f"IU4-ENTRY-VETO-CANDIDATE-{canonical_json_sha256(identity_material)}"
        )
        candidate_id = _text(self.candidate_id, "candidate_id", allow_empty=True)
        if candidate_id and candidate_id != expected_candidate_id:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "ENTRY_VETO candidate ID does not match its canonical identity",
            )
        for name, value in (
            ("candidate_id", expected_candidate_id),
            ("entry_veto_event_id", event_id),
            ("snapshot_id", snapshot_id),
            ("timestamp_utc", timestamp),
            ("tick_id", tick_id),
            ("intent_id", intent_id),
            ("intent_action", action),
            ("symbol", symbol),
            ("side", side),
            ("loss_cluster_state_fingerprint", loss_fingerprint),
            ("denial_reason_code", denial),
        ):
            object.__setattr__(self, name, value)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "candidate_id": self.candidate_id,
            "entry_veto_event_id": self.entry_veto_event_id,
            "snapshot_id": self.snapshot_id,
            "timestamp_utc": self.timestamp_utc,
            "tick_id": self.tick_id,
            "intent_id": self.intent_id,
            "intent_action": self.intent_action,
            "symbol": self.symbol,
            "side": self.side,
            "loss_cluster_state_fingerprint": (
                self.loss_cluster_state_fingerprint
            ),
            "denial_reason_code": self.denial_reason_code,
        }

    @property
    def candidate_fingerprint(self) -> str:
        return canonical_json_sha256(self.canonical_payload())

    def to_record(self) -> dict[str, Any]:
        result = self.canonical_payload()
        result["candidate_fingerprint"] = self.candidate_fingerprint
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AtomicEntryVetoCandidateV1":
        _strict_record_fields(
            record,
            set(cls.__dataclass_fields__) | {"candidate_fingerprint"},
            "ENTRY_VETO candidate",
        )
        candidate = cls(
            **{name: record.get(name) for name in cls.__dataclass_fields__}
        )
        if (
            _sha256(record.get("candidate_fingerprint"), "candidate_fingerprint")
            != candidate.candidate_fingerprint
            or dict(record) != candidate.to_record()
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "ENTRY_VETO candidate record is not canonical",
            )
        return candidate


@dataclass(frozen=True)
class AtomicPaperStateV2:
    schema_version: int
    coordinator_id: str
    system_state_id: str
    transaction_sequence: int
    journal_head: str
    last_transaction_event_id: str
    position: PositionArtifactV2
    account: PaperAccountState
    throttle: PaperEntryThrottleState
    loss_cluster: LossClusterStateV2
    progress_cursor: AtomicProgressCursorV1
    risk: PaperRiskStateS4V2
    entry_quote: EntryEconomicsQuoteArtifactV1 | None
    runtime_control_profile_id: str
    runtime_control_fingerprint: str
    loss_cluster_policy_id: str
    loss_cluster_policy_fingerprint: str
    state_owner_epoch: str
    authority_generation_id: str
    authority_prepare_record_fingerprint: str
    authority_manifest_id: str
    authority_manifest_fingerprint: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 2
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "AtomicPaperStateV2 requires schema_version 2",
            )
        for name in (
            "coordinator_id",
            "system_state_id",
            "runtime_control_profile_id",
            "loss_cluster_policy_id",
            "authority_generation_id",
            "authority_manifest_id",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        for name in (
            "runtime_control_fingerprint",
            "loss_cluster_policy_fingerprint",
            "authority_prepare_record_fingerprint",
            "authority_manifest_fingerprint",
        ):
            object.__setattr__(self, name, _sha256(getattr(self, name), name))
        owner = _text(self.state_owner_epoch, "state_owner_epoch").upper()
        if owner != "PEE":
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "Atomic V2 state_owner_epoch must be PEE",
            )
        object.__setattr__(self, "state_owner_epoch", owner)
        sequence = _integer(self.transaction_sequence, "transaction_sequence")
        event_id = _text(
            self.last_transaction_event_id,
            "last_transaction_event_id",
            allow_empty=True,
        )
        object.__setattr__(self, "transaction_sequence", sequence)
        object.__setattr__(self, "last_transaction_event_id", event_id)
        if sequence == 0:
            if self.journal_head != "EMPTY" or event_id:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "initial Atomic V2 head must be empty",
                )
        else:
            object.__setattr__(self, "journal_head", _sha256(self.journal_head, "journal_head"))
            if not event_id:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "non-initial Atomic V2 state requires an event head",
                )
        if not isinstance(self.position, (PositionStateS2FlatV2, PositionStateS2V2)):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "Atomic V2 requires complete S2 V2",
            )
        if not isinstance(self.account, PaperAccountState):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 requires PaperAccountState",
            )
        if not isinstance(self.throttle, PaperEntryThrottleState):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 requires PaperEntryThrottleState",
            )
        if not isinstance(self.loss_cluster, LossClusterStateV2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 requires LossClusterStateV2",
            )
        if not isinstance(self.progress_cursor, AtomicProgressCursorV1):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 requires AtomicProgressCursorV1",
            )
        if not isinstance(self.risk, PaperRiskStateS4V2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "Atomic V2 rejects S4V1 and requires PaperRiskStateS4V2",
            )
        if self.entry_quote is not None and not isinstance(
            self.entry_quote,
            EntryEconomicsQuoteArtifactV1,
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_QUOTE_REQUIRED,
                "entry_quote must be EntryEconomicsQuoteArtifactV1 or null",
            )
        self._validate_cross_state()

    def _validate_cross_state(self) -> None:
        position = self.position
        risk = self.risk
        if (
            self.system_state_id != position.system_state_id
            or risk.system_state_id != position.system_state_id
            or risk.position_fingerprint != position.state_fingerprint
            or risk.account_fingerprint != self.account.state_fingerprint
            or risk.throttle_fingerprint != self.throttle.state_fingerprint
            or risk.loss_cluster_fingerprint != self.loss_cluster.state_fingerprint
            or risk.progress_cursor_fingerprint
            != self.progress_cursor.cursor_fingerprint
            or risk.transaction_sequence != self.transaction_sequence
            or risk.journal_head != self.journal_head
            or risk.last_transaction_event_id != self.last_transaction_event_id
            or risk.authority_generation_id != self.authority_generation_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "Atomic V2 components or S4 bindings differ",
            )
        if (
            risk.runtime_control_profile_id != self.runtime_control_profile_id
            or risk.runtime_control_fingerprint != self.runtime_control_fingerprint
            or risk.loss_cluster_policy_id != self.loss_cluster_policy_id
            or risk.loss_cluster_policy_fingerprint
            != self.loss_cluster_policy_fingerprint
            or risk.economics_profile_id != self.account.economics_profile_id
            or risk.economics_model_version != self.account.economics_model_version
            or risk.config_fingerprint != self.account.config_fingerprint
            or risk.throttle_policy_profile_id != self.throttle.policy_profile_id
            or risk.throttle_policy_model_version != self.throttle.policy_model_version
            or risk.throttle_policy_fingerprint != self.throttle.policy_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "Atomic V2 profile identities differ",
            )
        if (
            position.economics_profile_id != self.account.economics_profile_id
            or position.economics_model_version != self.account.economics_model_version
            or position.config_fingerprint != self.account.config_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "S2 and account Economics identities differ",
            )
        if isinstance(position, PositionStateS2V2):
            if self.entry_quote is None:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.ENTRY_QUOTE_REQUIRED,
                    "OPEN Atomic V2 state requires a committed Entry Quote",
                )
            quote = self.entry_quote
            if (
                quote.side != position.side
                or quote.reference_entry_price != position.reference_entry_price
                or quote.reference_stop_price != position.reference_stop_price
                or quote.modeled_entry_fill_price != position.modeled_entry_fill_price
                or quote.quantity != position.quantity
                or quote.entry_notional_quote != position.entry_notional_quote
                or quote.entry_fee_quote != position.entry_fee_quote
                or quote.risk_budget_quote != position.risk_budget_quote
                or quote.modeled_stop_loss_quote != position.modeled_stop_loss_quote
                or quote.economics_profile_id != position.economics_profile_id
                or quote.economics_model_version != position.economics_model_version
                or quote.config_fingerprint != position.config_fingerprint
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.ENTRY_QUOTE_REQUIRED,
                    "OPEN S2 and committed Entry Quote differ",
                )
        elif self.entry_quote is not None:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_QUOTE_REQUIRED,
                "FLAT Atomic V2 state requires entry_quote=null",
            )
        accepted = self.throttle.total_accepted_entry_count
        closed = self.account.closed_trade_count
        if isinstance(position, PositionStateS2FlatV2):
            if accepted != closed:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "FLAT Atomic V2 account/throttle counts differ",
                )
        elif accepted != closed + 1:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "OPEN Atomic V2 account/throttle counts differ",
            )

    def business_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "coordinator_id": self.coordinator_id,
            "system_state_id": self.system_state_id,
            "transaction_sequence": self.transaction_sequence,
            "journal_head": self.journal_head,
            "last_transaction_event_id": self.last_transaction_event_id,
            "position": self.position.to_record(),
            "account": self.account.to_record(),
            "throttle": self.throttle.to_record(),
            "loss_cluster": self.loss_cluster.to_record(),
            "progress_cursor": self.progress_cursor.to_record(),
            "risk_business": self.risk.business_payload(),
            "entry_quote": None if self.entry_quote is None else self.entry_quote.to_record(),
            "runtime_control_profile_id": self.runtime_control_profile_id,
            "runtime_control_fingerprint": self.runtime_control_fingerprint,
            "loss_cluster_policy_id": self.loss_cluster_policy_id,
            "loss_cluster_policy_fingerprint": self.loss_cluster_policy_fingerprint,
            "state_owner_epoch": self.state_owner_epoch,
            "authority_manifest_id": self.authority_manifest_id,
            "authority_manifest_fingerprint": self.authority_manifest_fingerprint,
        }

    def core_payload(self) -> dict[str, Any]:
        return {
            "target_business_payload": self.business_payload(),
            "authority_generation_id": self.authority_generation_id,
            "risk_authority_generation_id": self.risk.authority_generation_id,
        }

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_type": "paper_atomic_state_v2",
            "coordinator_id": self.coordinator_id,
            "system_state_id": self.system_state_id,
            "transaction_sequence": self.transaction_sequence,
            "journal_head": self.journal_head,
            "last_transaction_event_id": self.last_transaction_event_id,
            "position": self.position.to_record(),
            "account": self.account.to_record(),
            "throttle": self.throttle.to_record(),
            "loss_cluster": self.loss_cluster.to_record(),
            "progress_cursor": self.progress_cursor.to_record(),
            "risk": self.risk.to_record(),
            "entry_quote": None if self.entry_quote is None else self.entry_quote.to_record(),
            "runtime_control_profile_id": self.runtime_control_profile_id,
            "runtime_control_fingerprint": self.runtime_control_fingerprint,
            "loss_cluster_policy_id": self.loss_cluster_policy_id,
            "loss_cluster_policy_fingerprint": self.loss_cluster_policy_fingerprint,
            "state_owner_epoch": self.state_owner_epoch,
            "authority_generation_id": self.authority_generation_id,
            "authority_prepare_record_fingerprint": self.authority_prepare_record_fingerprint,
            "authority_manifest_id": self.authority_manifest_id,
            "authority_manifest_fingerprint": self.authority_manifest_fingerprint,
        }

    @property
    def state_fingerprint(self) -> str:
        return canonical_json_sha256(self.canonical_payload())

    def to_record(self) -> dict[str, Any]:
        result = self.canonical_payload()
        result["state_fingerprint"] = self.state_fingerprint
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AtomicPaperStateV2":
        expected = {
            "schema_version",
            "artifact_type",
            "coordinator_id",
            "system_state_id",
            "transaction_sequence",
            "journal_head",
            "last_transaction_event_id",
            "position",
            "account",
            "throttle",
            "loss_cluster",
            "progress_cursor",
            "risk",
            "entry_quote",
            "runtime_control_profile_id",
            "runtime_control_fingerprint",
            "loss_cluster_policy_id",
            "loss_cluster_policy_fingerprint",
            "state_owner_epoch",
            "authority_generation_id",
            "authority_prepare_record_fingerprint",
            "authority_manifest_id",
            "authority_manifest_fingerprint",
            "state_fingerprint",
        }
        _strict_record_fields(record, expected, "Atomic V2 state")
        if record.get("artifact_type") != "paper_atomic_state_v2":
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "Atomic V2 artifact type is invalid",
            )
        try:
            position_raw = record.get("position")
            account_raw = record.get("account")
            throttle_raw = record.get("throttle")
            loss_raw = record.get("loss_cluster")
            cursor_raw = record.get("progress_cursor")
            risk_raw = record.get("risk")
            quote_raw = record.get("entry_quote")
            if not all(
                isinstance(value, Mapping)
                for value in (
                    position_raw,
                    account_raw,
                    throttle_raw,
                    loss_raw,
                    cursor_raw,
                    risk_raw,
                )
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "Atomic V2 component records must be objects",
                )
            position = parse_position_artifact(position_raw)
            if not isinstance(position, (PositionStateS2FlatV2, PositionStateS2V2)):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                    "Atomic V2 cannot contain Legacy S2",
                )
            state = cls(
                schema_version=record.get("schema_version"),
                coordinator_id=record.get("coordinator_id"),
                system_state_id=record.get("system_state_id"),
                transaction_sequence=record.get("transaction_sequence"),
                journal_head=record.get("journal_head"),
                last_transaction_event_id=record.get("last_transaction_event_id"),
                position=position,
                account=PaperAccountState.from_record(account_raw),
                throttle=PaperEntryThrottleState.from_record(throttle_raw),
                loss_cluster=LossClusterStateV2.from_record(loss_raw),
                progress_cursor=AtomicProgressCursorV1.from_record(cursor_raw),
                risk=PaperRiskStateS4V2.from_record(risk_raw),
                entry_quote=(
                    None
                    if quote_raw is None
                    else EntryEconomicsQuoteArtifactV1.from_record(quote_raw)
                ),
                runtime_control_profile_id=record.get("runtime_control_profile_id"),
                runtime_control_fingerprint=record.get("runtime_control_fingerprint"),
                loss_cluster_policy_id=record.get("loss_cluster_policy_id"),
                loss_cluster_policy_fingerprint=record.get("loss_cluster_policy_fingerprint"),
                state_owner_epoch=record.get("state_owner_epoch"),
                authority_generation_id=record.get("authority_generation_id"),
                authority_prepare_record_fingerprint=record.get("authority_prepare_record_fingerprint"),
                authority_manifest_id=record.get("authority_manifest_id"),
                authority_manifest_fingerprint=record.get("authority_manifest_fingerprint"),
            )
        except (PaperArtifactError, PaperEntryThrottleError, LossClusterStateError) as exc:
            raise PaperAtomicCoordinatorError(
                getattr(exc, "reason_code", AtomicCoordinatorReasonCode.TRANSACTION_INVALID),
                "Atomic V2 component validation failed",
            ) from exc
        if _sha256(record.get("state_fingerprint"), "state_fingerprint") != state.state_fingerprint:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "Atomic V2 state fingerprint mismatch",
            )
        if dict(record) != state.to_record():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "Atomic V2 state record is not canonical",
            )
        return state


@dataclass(frozen=True)
class AtomicPaperTransactionV2:
    schema_version: int
    transaction_sequence: int
    transaction_event_id: str
    previous_journal_head: str
    ordering_space: str
    primary_effect: str
    transaction_timestamp_utc: str
    causal_tick_id: int
    state_before: AtomicPaperStateV2
    state_after: AtomicPaperStateV2
    accepted_entry_event: AcceptedEntryEventV1 | None = None
    trade: TradeRecordV2 | None = None
    risk_escalation: str = ""
    control_authorization_reference: str = ""
    effect_position: PositionStateS2V2 | None = None
    effect_entry_quote: EntryEconomicsQuoteArtifactV1 | None = None
    effect_progress_cursor: AtomicProgressCursorV1 | None = None
    effect_throttle_policy: PaperEntryThrottlePolicy | None = None
    effect_entry_veto_candidate: AtomicEntryVetoCandidateV1 | None = None
    loss_transition_updated_utc: str = ""
    loss_transition_policy_id: str = ""
    loss_transition_policy_fingerprint: str = ""
    loss_transition_lookback: int = 0
    loss_transition_threshold: int = 0
    loss_transition_pause_entries: int = 0
    effect_target_kill_level: str = ""
    effect_entry_denial_provenance: AtomicEntryDenialProvenanceV1 | None = None

    def __post_init__(self) -> None:
        if self.schema_version != 2:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "AtomicPaperTransactionV2 requires schema_version 2",
            )
        if not isinstance(self.state_before, AtomicPaperStateV2) or not isinstance(
            self.state_after,
            AtomicPaperStateV2,
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 transaction requires complete before/after states",
            )
        sequence = _integer(self.transaction_sequence, "transaction_sequence", minimum=1)
        event_id = _text(self.transaction_event_id, "transaction_event_id")
        previous = self.previous_journal_head
        if previous != "EMPTY":
            previous = _sha256(previous, "previous_journal_head")
        ordering = _text(self.ordering_space, "ordering_space").upper()
        effect = _text(self.primary_effect, "primary_effect").upper()
        timestamp = _utc_timestamp_seconds(
            self.transaction_timestamp_utc,
            "transaction_timestamp_utc",
        )
        tick = _integer(self.causal_tick_id, "causal_tick_id")
        risk_escalation = _text(
            self.risk_escalation,
            "risk_escalation",
            allow_empty=True,
        ).upper()
        control_reference = _text(
            self.control_authorization_reference,
            "control_authorization_reference",
            allow_empty=True,
        )
        loss_updated = _text(
            self.loss_transition_updated_utc,
            "loss_transition_updated_utc",
            allow_empty=True,
        )
        if loss_updated:
            loss_updated = _utc_timestamp_seconds(
                loss_updated,
                "loss_transition_updated_utc",
            )
        loss_policy_id = _text(
            self.loss_transition_policy_id,
            "loss_transition_policy_id",
            allow_empty=True,
        )
        loss_policy_fingerprint = _text(
            self.loss_transition_policy_fingerprint,
            "loss_transition_policy_fingerprint",
            allow_empty=True,
        )
        if loss_policy_fingerprint:
            loss_policy_fingerprint = _sha256(
                loss_policy_fingerprint,
                "loss_transition_policy_fingerprint",
            )
        loss_lookback = _integer(
            self.loss_transition_lookback,
            "loss_transition_lookback",
            minimum=0,
        )
        loss_threshold = _integer(
            self.loss_transition_threshold,
            "loss_transition_threshold",
            minimum=0,
        )
        loss_pause_entries = _integer(
            self.loss_transition_pause_entries,
            "loss_transition_pause_entries",
            minimum=0,
        )
        target_kill_level = _text(
            self.effect_target_kill_level,
            "effect_target_kill_level",
            allow_empty=True,
        ).upper()
        if self.effect_entry_denial_provenance is not None and type(
            self.effect_entry_denial_provenance
        ) is not AtomicEntryDenialProvenanceV1:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "effect_entry_denial_provenance must be the exact artifact type",
            )
        for name, value in (
            ("transaction_sequence", sequence),
            ("transaction_event_id", event_id),
            ("previous_journal_head", previous),
            ("ordering_space", ordering),
            ("primary_effect", effect),
            ("transaction_timestamp_utc", timestamp),
            ("causal_tick_id", tick),
            ("risk_escalation", risk_escalation),
            ("control_authorization_reference", control_reference),
            ("loss_transition_updated_utc", loss_updated),
            ("loss_transition_policy_id", loss_policy_id),
            ("loss_transition_policy_fingerprint", loss_policy_fingerprint),
            ("loss_transition_lookback", loss_lookback),
            ("loss_transition_threshold", loss_threshold),
            ("loss_transition_pause_entries", loss_pause_entries),
            ("effect_target_kill_level", target_kill_level),
        ):
            object.__setattr__(self, name, value)
        before = self.state_before
        after = self.state_after
        if (
            after.transaction_sequence != sequence
            or before.transaction_sequence + 1 != sequence
            or before.journal_head != previous
            or after.last_transaction_event_id != event_id
            or before.authority_generation_id != after.authority_generation_id
            or before.authority_prepare_record_fingerprint
            != after.authority_prepare_record_fingerprint
            or before.authority_manifest_id != after.authority_manifest_id
            or before.authority_manifest_fingerprint
            != after.authority_manifest_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "Atomic V2 transaction metadata or Authority root changed",
            )
        expected_head = self.journal_head_for(
            transaction_sequence=sequence,
            transaction_event_id=event_id,
            previous_journal_head=previous,
            ordering_space=ordering,
            primary_effect=effect,
            transaction_timestamp_utc=timestamp,
            causal_tick_id=tick,
            state_before=before,
            position_after=after.position,
            account_after=after.account,
            throttle_after=after.throttle,
            loss_cluster_after=after.loss_cluster,
            progress_cursor_after=after.progress_cursor,
            entry_quote_after=after.entry_quote,
            accepted_entry_event=self.accepted_entry_event,
            trade=self.trade,
            risk_escalation=risk_escalation,
            effect_position=self.effect_position,
            effect_entry_quote=self.effect_entry_quote,
            effect_progress_cursor=self.effect_progress_cursor,
            effect_throttle_policy=self.effect_throttle_policy,
            effect_entry_veto_candidate=self.effect_entry_veto_candidate,
            loss_transition_updated_utc=loss_updated,
            loss_transition_policy_id=loss_policy_id,
            loss_transition_policy_fingerprint=loss_policy_fingerprint,
            loss_transition_lookback=loss_lookback,
            loss_transition_threshold=loss_threshold,
            loss_transition_pause_entries=loss_pause_entries,
            effect_target_kill_level=target_kill_level,
            kill_level_after=after.risk.kill_level,
            risk_business_after_fingerprint=canonical_json_sha256(
                after.risk.business_payload()
            ),
            control_authorization_reference=control_reference,
            effect_entry_denial_provenance=(
                self.effect_entry_denial_provenance
            ),
        )
        if after.journal_head != expected_head or after.risk.journal_head != expected_head:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                "Atomic V2 journal head does not bind the complete effect",
            )
        self._validate_effect()

    @staticmethod
    def journal_head_for(
        *,
        transaction_sequence: int,
        transaction_event_id: str,
        previous_journal_head: str,
        ordering_space: str,
        primary_effect: str,
        transaction_timestamp_utc: str,
        causal_tick_id: int,
        state_before: AtomicPaperStateV2,
        position_after: PositionArtifactV2,
        account_after: PaperAccountState,
        throttle_after: PaperEntryThrottleState,
        loss_cluster_after: LossClusterStateV2,
        progress_cursor_after: AtomicProgressCursorV1,
        entry_quote_after: EntryEconomicsQuoteArtifactV1 | None,
        accepted_entry_event: AcceptedEntryEventV1 | None,
        trade: TradeRecordV2 | None,
        risk_escalation: str,
        effect_position: PositionStateS2V2 | None,
        effect_entry_quote: EntryEconomicsQuoteArtifactV1 | None,
        effect_progress_cursor: AtomicProgressCursorV1 | None,
        effect_throttle_policy: PaperEntryThrottlePolicy | None,
        effect_entry_veto_candidate: AtomicEntryVetoCandidateV1 | None,
        loss_transition_updated_utc: str,
        loss_transition_policy_id: str,
        loss_transition_policy_fingerprint: str,
        loss_transition_lookback: int,
        loss_transition_threshold: int,
        loss_transition_pause_entries: int,
        effect_target_kill_level: str,
        kill_level_after: str,
        risk_business_after_fingerprint: str,
        control_authorization_reference: str,
        effect_entry_denial_provenance: AtomicEntryDenialProvenanceV1 | None = None,
    ) -> str:
        payload = {
            "schema_version": 2,
            "transaction_sequence": transaction_sequence,
            "transaction_event_id": transaction_event_id,
            "previous_journal_head": previous_journal_head,
            "ordering_space": ordering_space,
            "primary_effect": primary_effect,
            "transaction_timestamp_utc": transaction_timestamp_utc,
            "causal_tick_id": causal_tick_id,
            "state_before_fingerprint": state_before.state_fingerprint,
            "position_after_fingerprint": position_after.state_fingerprint,
            "account_after_fingerprint": account_after.state_fingerprint,
            "throttle_after_fingerprint": throttle_after.state_fingerprint,
            "loss_cluster_after_fingerprint": loss_cluster_after.state_fingerprint,
            "progress_cursor_after_fingerprint": progress_cursor_after.cursor_fingerprint,
            "entry_quote_after_fingerprint": (
                "NONE" if entry_quote_after is None else entry_quote_after.quote_fingerprint
            ),
            "accepted_entry_event_fingerprint": (
                "NONE" if accepted_entry_event is None else accepted_entry_event.event_fingerprint
            ),
            "trade_fingerprint": (
                "NONE" if trade is None else trade.record_fingerprint
            ),
            "risk_escalation": risk_escalation,
            "effect_position_fingerprint": (
                "NONE" if effect_position is None else effect_position.state_fingerprint
            ),
            "effect_entry_quote_fingerprint": (
                "NONE"
                if effect_entry_quote is None
                else effect_entry_quote.quote_fingerprint
            ),
            "effect_progress_cursor_fingerprint": (
                "NONE"
                if effect_progress_cursor is None
                else effect_progress_cursor.cursor_fingerprint
            ),
            "effect_throttle_policy_fingerprint": (
                "NONE"
                if effect_throttle_policy is None
                else effect_throttle_policy.policy_fingerprint
            ),
            "effect_entry_veto_candidate_fingerprint": (
                "NONE"
                if effect_entry_veto_candidate is None
                else effect_entry_veto_candidate.candidate_fingerprint
            ),
            "loss_transition_updated_utc": loss_transition_updated_utc,
            "loss_transition_policy_id": loss_transition_policy_id,
            "loss_transition_policy_fingerprint": loss_transition_policy_fingerprint,
            "loss_transition_lookback": loss_transition_lookback,
            "loss_transition_threshold": loss_transition_threshold,
            "loss_transition_pause_entries": loss_transition_pause_entries,
            "effect_target_kill_level": effect_target_kill_level,
            "kill_level_after": kill_level_after,
            "risk_business_after_fingerprint": risk_business_after_fingerprint,
            "control_authorization_reference": control_authorization_reference,
        }
        if effect_entry_denial_provenance is not None:
            if type(effect_entry_denial_provenance) is not AtomicEntryDenialProvenanceV1:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "journal denial provenance must be the exact artifact type",
                )
            payload["effect_entry_denial_provenance_fingerprint"] = (
                effect_entry_denial_provenance.provenance_fingerprint
            )
        return canonical_json_sha256(payload)

    def _validate_effect(self) -> None:
        before = self.state_before
        after = self.state_after
        if self.ordering_space == "TICK":
            if self.primary_effect not in (
                TRANSACTION_OPEN,
                TRANSACTION_CLOSE,
                TRANSACTION_ENTRY_VETO,
                TRANSACTION_PROGRESS,
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "Tick primary_effect is unsupported",
                )
            if not isinstance(self.effect_progress_cursor, AtomicProgressCursorV1):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                    "Tick transaction requires its exact effect Progress Cursor",
                )
            if after.progress_cursor == before.progress_cursor:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                    "Tick transaction must own one new Progress Cursor",
                )
            if (
                after.progress_cursor != self.effect_progress_cursor
                or self.transaction_timestamp_utc
                != self.effect_progress_cursor.timestamp_utc
                or self.causal_tick_id != self.effect_progress_cursor.tick_id
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                    "Tick transaction and Progress Cursor identity or time differ",
                )
            if self.control_authorization_reference:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "Tick transaction cannot contain Control authorization",
                )
            if self.risk_escalation:
                if (
                    self.risk_escalation != "NONE_TO_SOFT"
                    or before.risk.kill_level != "NONE"
                    or after.risk.kill_level != "SOFT"
                ):
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                        "Tick risk escalation may only be NONE_TO_SOFT",
                    )
            elif after.risk.kill_level != before.risk.kill_level:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "Tick changed Kill Level without NONE_TO_SOFT",
                )
        elif self.ordering_space == "CONTROL":
            if self.primary_effect != TRANSACTION_KILL:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "Control ordering space supports KILL only",
                )
            if after.progress_cursor != before.progress_cursor:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                    "KILL Control transaction cannot own a Progress Cursor",
                )
            if not self.control_authorization_reference or self.risk_escalation:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "KILL requires Control authorization and no Tick escalation",
                )
        else:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "ordering_space must be TICK or CONTROL",
            )
        unchanged_common = (
            before.runtime_control_profile_id == after.runtime_control_profile_id
            and before.runtime_control_fingerprint == after.runtime_control_fingerprint
            and before.loss_cluster_policy_id == after.loss_cluster_policy_id
            and before.loss_cluster_policy_fingerprint
            == after.loss_cluster_policy_fingerprint
        )
        if not unchanged_common:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "Atomic V2 transaction changed a bound profile",
            )
        no_loss_transition = (
            not self.loss_transition_updated_utc
            and not self.loss_transition_policy_id
            and not self.loss_transition_policy_fingerprint
            and self.loss_transition_lookback == 0
            and self.loss_transition_threshold == 0
            and self.loss_transition_pause_entries == 0
        )
        provenance = self.effect_entry_denial_provenance
        if provenance is not None:
            expected_provenance_risk = replace(
                before.risk,
                progress_cursor_fingerprint=(
                    self.effect_progress_cursor.cursor_fingerprint
                    if isinstance(
                        self.effect_progress_cursor,
                        AtomicProgressCursorV1,
                    )
                    else before.risk.progress_cursor_fingerprint
                ),
                transaction_sequence=self.transaction_sequence,
                journal_head=after.journal_head,
                last_transaction_event_id=self.transaction_event_id,
                last_transaction_timestamp_utc=self.transaction_timestamp_utc,
                last_transaction_tick_id=self.causal_tick_id,
            )
            origin_facts_valid = {
                "STATE_CAPABILITY": before.risk.entry_allowed is False,
                "RUNTIME_GATE_CAPABILITY": (
                    before.risk.entry_allowed is True
                    and provenance.entry_capability_allowed is False
                ),
                "ECONOMICS_AUTHORIZATION": (
                    before.risk.entry_allowed is True
                    and provenance.entry_capability_allowed is True
                ),
                "ATOMIC_ENTRY_GUARD": (
                    before.risk.entry_allowed is True
                    and provenance.entry_capability_allowed is True
                ),
            }.get(provenance.denial_origin, False)
            provenance_valid = (
                self.ordering_space == "TICK"
                and self.primary_effect == TRANSACTION_PROGRESS
                and isinstance(before.position, PositionStateS2FlatV2)
                and isinstance(after.position, PositionStateS2FlatV2)
                and before.loss_cluster.pause_entries_remaining == 0
                and "LOSS_CLUSTER_PAUSE" not in before.risk.reason_codes
                and not self.risk_escalation
                and self.transaction_event_id == provenance.transaction_event_id
                and self.transaction_timestamp_utc == provenance.timestamp_utc
                and self.causal_tick_id == provenance.tick_id
                and isinstance(
                    self.effect_progress_cursor,
                    AtomicProgressCursorV1,
                )
                and self.effect_progress_cursor.snapshot_id
                == provenance.snapshot_id
                and self.effect_progress_cursor.timestamp_utc
                == provenance.timestamp_utc
                and self.effect_progress_cursor.tick_id == provenance.tick_id
                and self.effect_progress_cursor.intent_id == provenance.intent_id
                and before.state_fingerprint
                == provenance.state_before_fingerprint
                and provenance.denial_reason_code == "PEE_IU4_ENTRY_BLOCKED"
                and origin_facts_valid
                and after.risk == expected_provenance_risk
            )
            if not provenance_valid:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "entry-denial provenance cross-binding is invalid",
                )
        try:
            if self.primary_effect == TRANSACTION_OPEN:
                expected_throttle = apply_accepted_entry(
                    before.throttle,
                    self.effect_throttle_policy,
                    self.accepted_entry_event,
                )
                valid = (
                    isinstance(before.position, PositionStateS2FlatV2)
                    and isinstance(self.effect_position, PositionStateS2V2)
                    and isinstance(
                        self.effect_entry_quote,
                        EntryEconomicsQuoteArtifactV1,
                    )
                    and isinstance(
                        self.effect_progress_cursor,
                        AtomicProgressCursorV1,
                    )
                    and isinstance(
                        self.effect_throttle_policy,
                        PaperEntryThrottlePolicy,
                    )
                    and self.effect_entry_veto_candidate is None
                    and self.effect_entry_denial_provenance is None
                    and isinstance(self.accepted_entry_event, AcceptedEntryEventV1)
                    and self.transaction_event_id
                    == self.accepted_entry_event.entry_event_id
                    and self.transaction_timestamp_utc
                    == self.accepted_entry_event.entry_timestamp_utc
                    == self.effect_position.entry_timestamp_utc
                    == self.effect_progress_cursor.timestamp_utc
                    and self.causal_tick_id
                    == self.effect_position.entry_tick_id
                    == self.effect_progress_cursor.tick_id
                    and self.trade is None
                    and after.position == self.effect_position
                    and after.entry_quote == self.effect_entry_quote
                    and after.progress_cursor == self.effect_progress_cursor
                    and after.account == before.account
                    and after.throttle == expected_throttle
                    and after.loss_cluster == before.loss_cluster
                    and no_loss_transition
                    and not self.effect_target_kill_level
                )
            elif self.primary_effect == TRANSACTION_CLOSE:
                expected_position = _flat_position_after_trade(
                    self.trade,
                    before.position,
                )
                expected_account = apply_trade_to_account(before.account, self.trade)
                expected_loss = apply_loss_cluster_close(
                    before.loss_cluster,
                    net_pnl_quote=self.trade.net_pnl_quote,
                    updated_utc=self.loss_transition_updated_utc,
                    policy_id=self.loss_transition_policy_id,
                    policy_fingerprint=self.loss_transition_policy_fingerprint,
                    lookback=self.loss_transition_lookback,
                    loss_threshold=self.loss_transition_threshold,
                    pause_entries=self.loss_transition_pause_entries,
                )
                valid = (
                    isinstance(before.position, PositionStateS2V2)
                    and before.entry_quote is not None
                    and isinstance(self.trade, TradeRecordV2)
                    and isinstance(
                        self.effect_progress_cursor,
                        AtomicProgressCursorV1,
                    )
                    and self.accepted_entry_event is None
                    and self.effect_position is None
                    and self.effect_entry_quote is None
                    and self.effect_throttle_policy is None
                    and self.effect_entry_veto_candidate is None
                    and self.effect_entry_denial_provenance is None
                    and self.transaction_event_id == self.trade.settlement_event_id
                    and self.transaction_timestamp_utc
                    == self.trade.exit_timestamp_utc
                    == self.effect_progress_cursor.timestamp_utc
                    and self.causal_tick_id
                    == self.trade.exit_tick_id
                    == self.effect_progress_cursor.tick_id
                    and after.position == expected_position
                    and after.account == expected_account
                    and after.throttle == before.throttle
                    and after.loss_cluster == expected_loss
                    and after.progress_cursor == self.effect_progress_cursor
                    and after.entry_quote is None
                    and not self.effect_target_kill_level
                )
            elif self.primary_effect == TRANSACTION_ENTRY_VETO:
                expected_loss = apply_loss_cluster_entry_veto(
                    before.loss_cluster,
                    updated_utc=self.loss_transition_updated_utc,
                    policy_id=self.loss_transition_policy_id,
                    policy_fingerprint=self.loss_transition_policy_fingerprint,
                )
                valid = (
                    self.accepted_entry_event is None
                    and self.trade is None
                    and self.effect_position is None
                    and self.effect_entry_quote is None
                    and isinstance(
                        self.effect_progress_cursor,
                        AtomicProgressCursorV1,
                    )
                    and self.effect_throttle_policy is None
                    and isinstance(
                        self.effect_entry_veto_candidate,
                        AtomicEntryVetoCandidateV1,
                    )
                    and self.effect_entry_denial_provenance is None
                    and self.transaction_event_id
                    == self.effect_entry_veto_candidate.entry_veto_event_id
                    and self.effect_entry_veto_candidate.snapshot_id
                    == self.effect_progress_cursor.snapshot_id
                    and self.effect_entry_veto_candidate.timestamp_utc
                    == self.transaction_timestamp_utc
                    == self.effect_progress_cursor.timestamp_utc
                    == self.loss_transition_updated_utc
                    and self.effect_entry_veto_candidate.tick_id
                    == self.causal_tick_id
                    == self.effect_progress_cursor.tick_id
                    and self.effect_entry_veto_candidate.intent_id
                    == self.effect_progress_cursor.intent_id
                    and self.effect_entry_veto_candidate.symbol
                    == before.position.symbol
                    and self.effect_entry_veto_candidate.loss_cluster_state_fingerprint
                    == before.loss_cluster.state_fingerprint
                    and self.loss_transition_lookback == 0
                    and self.loss_transition_threshold == 0
                    and self.loss_transition_pause_entries == 0
                    and not self.effect_target_kill_level
                    and before.position == after.position
                    and before.account == after.account
                    and before.throttle == after.throttle
                    and before.entry_quote == after.entry_quote
                    and after.loss_cluster == expected_loss
                    and after.progress_cursor == self.effect_progress_cursor
                )
            elif self.primary_effect == TRANSACTION_PROGRESS:
                valid = (
                    self.accepted_entry_event is None
                    and self.trade is None
                    and self.effect_position is None
                    and self.effect_entry_quote is None
                    and isinstance(
                        self.effect_progress_cursor,
                        AtomicProgressCursorV1,
                    )
                    and self.effect_throttle_policy is None
                    and self.effect_entry_veto_candidate is None
                    and no_loss_transition
                    and not self.effect_target_kill_level
                    and before.position == after.position
                    and before.account == after.account
                    and before.throttle == after.throttle
                    and before.loss_cluster == after.loss_cluster
                    and before.entry_quote == after.entry_quote
                    and after.progress_cursor == self.effect_progress_cursor
                )
            else:
                valid = (
                    self.accepted_entry_event is None
                    and self.trade is None
                    and self.effect_position is None
                    and self.effect_entry_quote is None
                    and self.effect_progress_cursor is None
                    and self.effect_throttle_policy is None
                    and self.effect_entry_veto_candidate is None
                    and self.effect_entry_denial_provenance is None
                    and no_loss_transition
                    and self.effect_target_kill_level == after.risk.kill_level
                    and before.risk.kill_level != after.risk.kill_level
                    and before.position == after.position
                    and before.account == after.account
                    and before.throttle == after.throttle
                    and before.loss_cluster == after.loss_cluster
                    and before.entry_quote == after.entry_quote
                )
        except (
            AttributeError,
            PaperArtifactError,
            PaperEntryThrottleError,
            LossClusterStateError,
        ) as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                f"{self.primary_effect} effect payload cannot be derived",
            ) from exc
        if not valid:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                f"{self.primary_effect} mutation allowlist was violated",
            )
        before_risk = before.risk
        after_risk = after.risk
        if self.primary_effect == TRANSACTION_CLOSE:
            assert self.trade is not None
            expected_loss = before_risk.loss_today
            if self.trade.net_pnl_quote < 0:
                expected_loss += -self.trade.net_pnl_quote
            metrics_valid = (
                after_risk.trades_today == before_risk.trades_today + 1
                and after_risk.trades_6h == before_risk.trades_6h + 1
                and after_risk.loss_today == expected_loss
                and after_risk.last_trade_timestamp_utc
                == self.trade.exit_timestamp_utc
                and after_risk.anomaly_counter == before_risk.anomaly_counter
            )
        else:
            metrics_valid = (
                after_risk.trades_today == before_risk.trades_today
                and after_risk.trades_6h == before_risk.trades_6h
                and after_risk.loss_today == before_risk.loss_today
                and after_risk.last_trade_timestamp_utc
                == before_risk.last_trade_timestamp_utc
                and after_risk.anomaly_counter == before_risk.anomaly_counter
            )
        if not metrics_valid:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                f"{self.primary_effect} changed forbidden S4 business metrics",
            )

    def canonical_payload(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "artifact_type": "paper_atomic_transaction_v2",
            "transaction_sequence": self.transaction_sequence,
            "transaction_event_id": self.transaction_event_id,
            "previous_journal_head": self.previous_journal_head,
            "ordering_space": self.ordering_space,
            "primary_effect": self.primary_effect,
            "transaction_timestamp_utc": self.transaction_timestamp_utc,
            "causal_tick_id": self.causal_tick_id,
            "state_before": self.state_before.to_record(),
            "state_after": self.state_after.to_record(),
            "accepted_entry_event": (
                None
                if self.accepted_entry_event is None
                else self.accepted_entry_event.to_record()
            ),
            "trade": None if self.trade is None else self.trade.to_record(),
            "risk_escalation": self.risk_escalation,
            "control_authorization_reference": self.control_authorization_reference,
            "effect_position": (
                None if self.effect_position is None else self.effect_position.to_record()
            ),
            "effect_entry_quote": (
                None
                if self.effect_entry_quote is None
                else self.effect_entry_quote.to_record()
            ),
            "effect_progress_cursor": (
                None
                if self.effect_progress_cursor is None
                else self.effect_progress_cursor.to_record()
            ),
            "effect_throttle_policy": (
                None
                if self.effect_throttle_policy is None
                else self.effect_throttle_policy.to_record()
            ),
            "effect_entry_veto_candidate": (
                None
                if self.effect_entry_veto_candidate is None
                else self.effect_entry_veto_candidate.to_record()
            ),
            "loss_transition_updated_utc": self.loss_transition_updated_utc,
            "loss_transition_policy_id": self.loss_transition_policy_id,
            "loss_transition_policy_fingerprint": (
                self.loss_transition_policy_fingerprint
            ),
            "loss_transition_lookback": self.loss_transition_lookback,
            "loss_transition_threshold": self.loss_transition_threshold,
            "loss_transition_pause_entries": self.loss_transition_pause_entries,
            "effect_target_kill_level": self.effect_target_kill_level,
        }
        if self.effect_entry_denial_provenance is not None:
            payload["effect_entry_denial_provenance"] = (
                self.effect_entry_denial_provenance.to_record()
            )
        return payload

    @property
    def transaction_fingerprint(self) -> str:
        return canonical_json_sha256(self.canonical_payload())

    def to_record(self) -> dict[str, Any]:
        result = self.canonical_payload()
        result["transaction_fingerprint"] = self.transaction_fingerprint
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "AtomicPaperTransactionV2":
        base_expected = {
            "schema_version",
            "artifact_type",
            "transaction_sequence",
            "transaction_event_id",
            "previous_journal_head",
            "ordering_space",
            "primary_effect",
            "transaction_timestamp_utc",
            "causal_tick_id",
            "state_before",
            "state_after",
            "accepted_entry_event",
            "trade",
            "risk_escalation",
            "control_authorization_reference",
            "effect_position",
            "effect_entry_quote",
            "effect_progress_cursor",
            "effect_throttle_policy",
            "effect_entry_veto_candidate",
            "loss_transition_updated_utc",
            "loss_transition_policy_id",
            "loss_transition_policy_fingerprint",
            "loss_transition_lookback",
            "loss_transition_threshold",
            "loss_transition_pause_entries",
            "effect_target_kill_level",
            "transaction_fingerprint",
        }
        expected = set(base_expected)
        provenance_present = "effect_entry_denial_provenance" in record
        if provenance_present:
            expected.add("effect_entry_denial_provenance")
        _strict_record_fields(record, expected, "Atomic V2 transaction")
        if record.get("artifact_type") != "paper_atomic_transaction_v2":
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "Atomic V2 transaction artifact type is invalid",
            )
        before_raw = record.get("state_before")
        after_raw = record.get("state_after")
        entry_raw = record.get("accepted_entry_event")
        trade_raw = record.get("trade")
        position_effect_raw = record.get("effect_position")
        quote_effect_raw = record.get("effect_entry_quote")
        cursor_effect_raw = record.get("effect_progress_cursor")
        throttle_policy_raw = record.get("effect_throttle_policy")
        entry_veto_candidate_raw = record.get("effect_entry_veto_candidate")
        entry_denial_provenance_raw = (
            record.get("effect_entry_denial_provenance")
            if provenance_present
            else None
        )
        if not isinstance(before_raw, Mapping) or not isinstance(after_raw, Mapping):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 transaction states must be objects",
            )
        for name, value in (
            ("effect_position", position_effect_raw),
            ("effect_entry_quote", quote_effect_raw),
            ("effect_progress_cursor", cursor_effect_raw),
            ("effect_throttle_policy", throttle_policy_raw),
            ("effect_entry_veto_candidate", entry_veto_candidate_raw),
        ):
            if value is not None and not isinstance(value, Mapping):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    f"Atomic V2 transaction {name} must be an object or null",
                )
        if provenance_present and not isinstance(
            entry_denial_provenance_raw,
            Mapping,
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "effect_entry_denial_provenance must be one strict object",
            )
        transaction = cls(
            schema_version=record.get("schema_version"),
            transaction_sequence=record.get("transaction_sequence"),
            transaction_event_id=record.get("transaction_event_id"),
            previous_journal_head=record.get("previous_journal_head"),
            ordering_space=record.get("ordering_space"),
            primary_effect=record.get("primary_effect"),
            transaction_timestamp_utc=record.get("transaction_timestamp_utc"),
            causal_tick_id=record.get("causal_tick_id"),
            state_before=AtomicPaperStateV2.from_record(before_raw),
            state_after=AtomicPaperStateV2.from_record(after_raw),
            accepted_entry_event=(
                None
                if entry_raw is None
                else AcceptedEntryEventV1.from_record(entry_raw)
            ),
            trade=None if trade_raw is None else TradeRecordV2.from_record(trade_raw),
            risk_escalation=record.get("risk_escalation"),
            control_authorization_reference=record.get("control_authorization_reference"),
            effect_position=(
                None
                if position_effect_raw is None
                else PositionStateS2V2.from_record(position_effect_raw)
            ),
            effect_entry_quote=(
                None
                if quote_effect_raw is None
                else EntryEconomicsQuoteArtifactV1.from_record(quote_effect_raw)
            ),
            effect_progress_cursor=(
                None
                if cursor_effect_raw is None
                else AtomicProgressCursorV1.from_record(cursor_effect_raw)
            ),
            effect_throttle_policy=(
                None
                if throttle_policy_raw is None
                else PaperEntryThrottlePolicy.from_record(throttle_policy_raw)
            ),
            effect_entry_veto_candidate=(
                None
                if entry_veto_candidate_raw is None
                else AtomicEntryVetoCandidateV1.from_record(
                    entry_veto_candidate_raw
                )
            ),
            loss_transition_updated_utc=record.get("loss_transition_updated_utc"),
            loss_transition_policy_id=record.get("loss_transition_policy_id"),
            loss_transition_policy_fingerprint=record.get(
                "loss_transition_policy_fingerprint"
            ),
            loss_transition_lookback=record.get("loss_transition_lookback"),
            loss_transition_threshold=record.get("loss_transition_threshold"),
            loss_transition_pause_entries=record.get(
                "loss_transition_pause_entries"
            ),
            effect_target_kill_level=record.get("effect_target_kill_level"),
            effect_entry_denial_provenance=(
                None
                if not provenance_present
                else AtomicEntryDenialProvenanceV1.from_record(
                    entry_denial_provenance_raw
                )
            ),
        )
        if _sha256(record.get("transaction_fingerprint"), "transaction_fingerprint") != transaction.transaction_fingerprint:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                "Atomic V2 transaction fingerprint mismatch",
            )
        if dict(record) != transaction.to_record():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                "Atomic V2 transaction record is not canonical",
            )
        return transaction


@dataclass(frozen=True)
class AtomicV1ToV2MigrationArtifactV1:
    schema_version: int
    migration_id: str
    source_state_path: str
    source_state_fingerprint: str
    source_state_sha256: str
    source_loss_cluster_path: str
    source_loss_cluster_fingerprint: str
    source_loss_cluster_sha256: str
    target_state_path: str
    target_business_fingerprint: str
    target_state_core_fingerprint: str
    target_system_state_id: str
    target_position_fingerprint: str
    target_account_fingerprint: str
    target_throttle_fingerprint: str
    target_loss_cluster_fingerprint: str
    target_progress_cursor_fingerprint: str
    target_risk_business_fingerprint: str
    target_state_owner_epoch: str
    runtime_control_profile_id: str
    runtime_control_fingerprint: str
    loss_cluster_policy_id: str
    loss_cluster_policy_fingerprint: str
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str
    throttle_policy_profile_id: str
    throttle_policy_model_version: str
    throttle_policy_fingerprint: str
    previous_owner_epoch: int
    new_owner_epoch: int
    manifest_id: str
    manifest_fingerprint: str
    approval_id: str
    approval_fingerprint: str
    source_authority_generation_id: str
    source_authority_commit_anchor: str
    operator: str
    migration_timestamp_utc: str

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "AtomicV1ToV2MigrationArtifactV1 requires schema_version 1",
            )
        for name in (
            "migration_id",
            "manifest_id",
            "approval_id",
            "source_authority_generation_id",
            "operator",
            "target_system_state_id",
            "target_state_owner_epoch",
            "runtime_control_profile_id",
            "loss_cluster_policy_id",
            "economics_profile_id",
            "economics_model_version",
            "throttle_policy_profile_id",
            "throttle_policy_model_version",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        for name in (
            "source_state_fingerprint",
            "source_state_sha256",
            "source_loss_cluster_fingerprint",
            "source_loss_cluster_sha256",
            "target_business_fingerprint",
            "target_state_core_fingerprint",
            "target_position_fingerprint",
            "target_account_fingerprint",
            "target_throttle_fingerprint",
            "target_loss_cluster_fingerprint",
            "target_progress_cursor_fingerprint",
            "target_risk_business_fingerprint",
            "runtime_control_fingerprint",
            "loss_cluster_policy_fingerprint",
            "config_fingerprint",
            "throttle_policy_fingerprint",
            "manifest_fingerprint",
            "approval_fingerprint",
            "source_authority_commit_anchor",
        ):
            object.__setattr__(self, name, _sha256(getattr(self, name), name))
        previous_owner = _integer(self.previous_owner_epoch, "previous_owner_epoch")
        new_owner = _integer(self.new_owner_epoch, "new_owner_epoch", minimum=1)
        if new_owner != previous_owner + 1:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                "migration owner epoch must advance exactly once",
            )
        object.__setattr__(self, "previous_owner_epoch", previous_owner)
        object.__setattr__(self, "new_owner_epoch", new_owner)
        paths: list[Path] = []
        for name in ("source_state_path", "source_loss_cluster_path", "target_state_path"):
            path = Path(_text(getattr(self, name), name))
            if not path.is_absolute() or path.is_symlink():
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    f"{name} must be an absolute non-symlink path",
                )
            object.__setattr__(self, name, str(path))
            paths.append(path)
        if len(set(paths)) != len(paths):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "migration source and target paths must be disjoint",
            )
        object.__setattr__(
            self,
            "migration_timestamp_utc",
            _utc_timestamp_seconds(
                self.migration_timestamp_utc,
                "migration_timestamp_utc",
            ),
        )

    def canonical_payload(self) -> dict[str, Any]:
        result = {
            "schema_version": self.schema_version,
            "artifact_type": "atomic_v1_to_v2_migration",
        }
        result.update(
            {name: getattr(self, name) for name in self.__dataclass_fields__}
        )
        return result

    @property
    def artifact_fingerprint(self) -> str:
        return canonical_json_sha256(self.canonical_payload())

    def to_record(self) -> dict[str, Any]:
        result = self.canonical_payload()
        result["artifact_fingerprint"] = self.artifact_fingerprint
        return result

    @classmethod
    def from_record(
        cls,
        record: Mapping[str, Any],
    ) -> "AtomicV1ToV2MigrationArtifactV1":
        expected = {
            "schema_version",
            "artifact_type",
            *cls.__dataclass_fields__,
            "artifact_fingerprint",
        }
        _strict_record_fields(record, expected, "Atomic V1-to-V2 migration")
        if record.get("artifact_type") != "atomic_v1_to_v2_migration":
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "migration artifact type is invalid",
            )
        artifact = cls(
            **{name: record.get(name) for name in cls.__dataclass_fields__}
        )
        if (
            _sha256(record.get("artifact_fingerprint"), "artifact_fingerprint")
            != artifact.artifact_fingerprint
            or dict(record) != artifact.to_record()
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration artifact fingerprint or canonical form is invalid",
            )
        return artifact


@dataclass(frozen=True)
class AtomicCommitResultV2:
    state: AtomicPaperStateV2
    journal_path: Path
    newly_committed: bool
    already_committed: bool
    recovered_incomplete_commit: bool


@dataclass(frozen=True)
class AtomicRecoveryResultV2:
    state: AtomicPaperStateV2
    journal_count: int
    recovered_transaction_count: int


@dataclass(frozen=True)
class AtomicMigrationResultV1:
    target_state: AtomicPaperStateV2
    prepare_record_fingerprint: str
    commit_record_fingerprint: str


class PaperAtomicCoordinatorV2:
    """Inactive single-writer Atomic V2 authority for package I3 only."""

    def __init__(
        self,
        root_directory: str | Path,
        config: PaperEconomicsConfig,
        throttle_policy: PaperEntryThrottlePolicy,
        *,
        coordinator_id: str,
        symbol: str,
        runtime_control_profile_id: str,
        runtime_control_fingerprint: str,
        loss_cluster_policy_id: str,
        loss_cluster_policy_fingerprint: str,
    ) -> None:
        root = Path(root_directory)
        if not root.is_absolute():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 root must be absolute",
            )
        self.root_directory = root
        self.config = config
        self.throttle_policy = throttle_policy
        self.coordinator_id = _text(coordinator_id, "coordinator_id")
        self.symbol = _text(symbol, "symbol")
        self.runtime_control_profile_id = _text(
            runtime_control_profile_id,
            "runtime_control_profile_id",
        )
        self.runtime_control_fingerprint = _sha256(
            runtime_control_fingerprint,
            "runtime_control_fingerprint",
        )
        self.loss_cluster_policy_id = _text(
            loss_cluster_policy_id,
            "loss_cluster_policy_id",
        )
        self.loss_cluster_policy_fingerprint = _sha256(
            loss_cluster_policy_fingerprint,
            "loss_cluster_policy_fingerprint",
        )
        self.state_path = root / "paper_atomic_state_v2.json"
        self.transaction_directory = root / "paper_atomic_transactions_v2"
        self._lock_context = threading.local()

    @contextmanager
    def _exclusive_root_lock(self):
        depth = getattr(self._lock_context, "depth", 0)
        if depth:
            self._lock_context.depth = depth + 1
            try:
                yield
            finally:
                self._lock_context.depth = depth
            return
        descriptor: int | None = None
        try:
            self.root_directory.mkdir(parents=True, exist_ok=True)
            flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            flags |= getattr(os, "O_NOFOLLOW", 0)
            descriptor = os.open(str(self.root_directory), flags)
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            self._lock_context.depth = 1
        except (OSError, MemoryError) as exc:
            if descriptor is not None:
                os.close(descriptor)
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.RESOURCE_EXHAUSTED,
                "Atomic V2 root-exclusive lock could not be acquired",
            ) from exc
        try:
            yield
        finally:
            assert descriptor is not None
            self._lock_context.depth = 0
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)

    def _ensure_identity(self, state: AtomicPaperStateV2) -> None:
        if (
            state.coordinator_id != self.coordinator_id
            or state.position.symbol != self.symbol
            or state.runtime_control_profile_id != self.runtime_control_profile_id
            or state.runtime_control_fingerprint != self.runtime_control_fingerprint
            or state.loss_cluster_policy_id != self.loss_cluster_policy_id
            or state.loss_cluster_policy_fingerprint
            != self.loss_cluster_policy_fingerprint
            or state.account.economics_profile_id != self.config.economics_profile_id
            or state.account.economics_model_version
            != self.config.economics_model_version
            or state.account.config_fingerprint != self.config.config_fingerprint
            or state.throttle.policy_profile_id
            != self.throttle_policy.policy_profile_id
            or state.throttle.policy_model_version
            != self.throttle_policy.policy_model_version
            or state.throttle.policy_fingerprint
            != self.throttle_policy.policy_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                "Atomic V2 state does not match coordinator bindings",
            )

    def initialize(
        self,
        state: AtomicPaperStateV2,
        *,
        committed_authority_target_state_fingerprint: str,
    ) -> AtomicPaperStateV2:
        with self._exclusive_root_lock():
            return self._initialize_locked(
                state,
                committed_authority_target_state_fingerprint=(
                    committed_authority_target_state_fingerprint
                ),
            )

    def _initialize_locked(
        self,
        state: AtomicPaperStateV2,
        *,
        committed_authority_target_state_fingerprint: str,
    ) -> AtomicPaperStateV2:
        if not isinstance(state, AtomicPaperStateV2) or state.transaction_sequence != 0:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 initialization requires a complete sequence-0 target State",
            )
        self._ensure_identity(state)
        if _sha256(
            committed_authority_target_state_fingerprint,
            "committed_authority_target_state_fingerprint",
        ) != state.state_fingerprint:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                "initial Atomic V2 State differs from committed Authority target",
            )
        if self.state_path.exists():
            existing = self.load_state()
            if existing == state:
                return existing
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.STATE_ALREADY_INITIALIZED,
                "Atomic V2 root already contains another State",
            )
        if self.transaction_directory.exists() and any(self.transaction_directory.iterdir()):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                "Atomic V2 initialization requires an empty journal",
            )
        _atomic_write_json(self.state_path, state.to_record())
        return state

    def load_state(self) -> AtomicPaperStateV2:
        if not self.state_path.exists():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.STATE_MISSING,
                "Atomic V2 State is missing",
            )
        state = AtomicPaperStateV2.from_record(
            _canonical_read_json_object(self.state_path)
        )
        self._ensure_identity(state)
        return state

    def _journal_path(self, sequence: int, event_id: str) -> Path:
        suffix = hashlib.sha256(event_id.encode("utf-8")).hexdigest()[:20]
        return self.transaction_directory / f"{sequence:020d}_{suffix}.json"

    def _transactions(self) -> list[tuple[Path, AtomicPaperTransactionV2]]:
        if not self.transaction_directory.exists():
            return []
        paths = sorted(self.transaction_directory.iterdir(), key=lambda path: path.name)
        result: list[tuple[Path, AtomicPaperTransactionV2]] = []
        event_ids: set[str] = set()
        for expected_sequence, path in enumerate(paths, 1):
            if path.is_symlink() or not path.is_file() or not path.name.endswith(".json"):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "unknown Atomic V2 journal entry",
                )
            transaction = AtomicPaperTransactionV2.from_record(
                _canonical_read_json_object(path)
            )
            self._validate_transaction_derivation(transaction)
            if transaction.transaction_sequence != expected_sequence:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_GAP,
                    "Atomic V2 journal sequence is not contiguous",
                )
            if transaction.transaction_event_id in event_ids:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "Atomic V2 journal contains a duplicate Event ID",
                )
            if result:
                previous = result[-1][1]
                if (
                    transaction.previous_journal_head
                    != previous.state_after.journal_head
                    or transaction.state_before != previous.state_after
                ):
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.JOURNAL_GAP,
                        "Atomic V2 journal predecessor chain is broken",
                    )
            event_ids.add(transaction.transaction_event_id)
            result.append((path, transaction))
        return result

    @staticmethod
    def _snapshot_index(
        current: AtomicPaperStateV2,
        entries: list[tuple[Path, AtomicPaperTransactionV2]],
    ) -> int | None:
        sequence = current.transaction_sequence
        if sequence > len(entries):
            return None
        if sequence == 0:
            if entries and current != entries[0][1].state_before:
                return None
            return 0
        if current != entries[sequence - 1][1].state_after:
            return None
        return sequence

    def _existing(self, event_id: str) -> AtomicPaperTransactionV2 | None:
        return next(
            (
                transaction
                for _, transaction in self._transactions()
                if transaction.transaction_event_id == event_id
            ),
            None,
        )

    def _commit(
        self,
        transaction: AtomicPaperTransactionV2,
        *,
        simulate_interruption_after_journal: bool,
        simulate_interruption_at: str = "",
    ) -> AtomicCommitResultV2:
        with self._exclusive_root_lock():
            return self._commit_locked(
                transaction,
                simulate_interruption_after_journal=(
                    simulate_interruption_after_journal
                ),
                simulate_interruption_at=simulate_interruption_at,
            )

    def _commit_locked(
        self,
        transaction: AtomicPaperTransactionV2,
        *,
        simulate_interruption_after_journal: bool,
        simulate_interruption_at: str = "",
    ) -> AtomicCommitResultV2:
        fault_point = _text(
            simulate_interruption_at,
            "simulate_interruption_at",
            allow_empty=True,
        ).upper()
        if fault_point not in (
            "",
            "BEFORE_JOURNAL",
            "AFTER_JOURNAL",
            "BEFORE_SNAPSHOT",
            "AFTER_SNAPSHOT",
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "unsupported Atomic V2 interruption point",
            )
        current = self.load_state()
        entries = self._transactions()
        duplicate = next(
            (
                (path, existing)
                for path, existing in entries
                if existing.transaction_event_id == transaction.transaction_event_id
            ),
            None,
        )
        if duplicate is not None:
            path, existing = duplicate
            if existing.transaction_fingerprint != transaction.transaction_fingerprint:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same Atomic V2 Event ID contains a different payload",
                )
            if current == entries[-1][1].state_after:
                return AtomicCommitResultV2(
                    state=current,
                    journal_path=path,
                    newly_committed=False,
                    already_committed=True,
                    recovered_incomplete_commit=False,
                )
            if current == existing.state_before and existing == entries[-1][1]:
                _atomic_write_json(self.state_path, existing.state_after.to_record())
                return AtomicCommitResultV2(
                    state=existing.state_after,
                    journal_path=path,
                    newly_committed=False,
                    already_committed=False,
                    recovered_incomplete_commit=True,
                )
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.RECOVERY_REQUIRED,
                "Atomic V2 journal requires recovery",
            )
        if transaction.ordering_space == "TICK":
            cursor = transaction.state_after.progress_cursor
            for _, existing in entries:
                if existing.ordering_space != "TICK":
                    continue
                prior = existing.state_after.progress_cursor
                if (
                    prior.snapshot_id == cursor.snapshot_id
                    or prior.tick_id == cursor.tick_id
                ):
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                        "accepted Snapshot/Tick identity already belongs to another transaction",
                    )
        index = self._snapshot_index(current, entries)
        if index is None:
            reason = (
                AtomicCoordinatorReasonCode.STATE_AHEAD_OF_JOURNAL
                if current.transaction_sequence > len(entries)
                else AtomicCoordinatorReasonCode.JOURNAL_CONFLICT
            )
            raise PaperAtomicCoordinatorError(reason, "Atomic V2 snapshot is not a journal prefix")
        if index != len(entries):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.RECOVERY_REQUIRED,
                "Atomic V2 durable journal is ahead of its snapshot",
            )
        if transaction.state_before != current:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 transaction was not built from current State",
            )
        self._validate_transaction_derivation(transaction)
        if entries and (
            transaction.transaction_timestamp_utc
            < entries[-1][1].transaction_timestamp_utc
            or transaction.causal_tick_id < entries[-1][1].causal_tick_id
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 transaction time/tick regressed",
            )
        journal_path = self._journal_path(
            transaction.transaction_sequence,
            transaction.transaction_event_id,
        )
        if fault_point == "BEFORE_JOURNAL":
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption before Atomic V2 journal write"
            )
        try:
            _create_new_json(journal_path, transaction.to_record())
        except FileExistsError as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                "Atomic V2 journal path already exists",
            ) from exc
        except (OSError, MemoryError) as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.RESOURCE_EXHAUSTED,
                "Atomic V2 journal publication failed",
            ) from exc
        if simulate_interruption_after_journal or fault_point == "AFTER_JOURNAL":
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption after durable Atomic V2 journal write"
            )
        if fault_point == "BEFORE_SNAPSHOT":
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption before Atomic V2 snapshot replace"
            )
        try:
            _atomic_write_json(self.state_path, transaction.state_after.to_record())
        except (OSError, MemoryError) as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.RESOURCE_EXHAUSTED,
                "Atomic V2 snapshot publication failed; recovery is required",
            ) from exc
        if fault_point == "AFTER_SNAPSHOT":
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption after Atomic V2 snapshot replace"
            )
        return AtomicCommitResultV2(
            state=transaction.state_after,
            journal_path=journal_path,
            newly_committed=True,
            already_committed=False,
            recovered_incomplete_commit=False,
        )

    @staticmethod
    def _unique_reasons(*groups: tuple[str, ...]) -> tuple[str, ...]:
        result: list[str] = []
        for group in groups:
            for reason in group:
                if reason not in result:
                    result.append(reason)
        return tuple(result)

    def _risk_after(
        self,
        current: AtomicPaperStateV2,
        *,
        position: PositionArtifactV2,
        account: PaperAccountState,
        throttle: PaperEntryThrottleState,
        loss_cluster: LossClusterStateV2,
        progress_cursor: AtomicProgressCursorV1,
        sequence: int,
        journal_head: str,
        event_id: str,
        timestamp: str,
        tick_id: int,
        kill_level: str,
        close_trade: TradeRecordV2 | None = None,
    ) -> PaperRiskStateS4V2:
        account_decision = evaluate_account_entry_guard(
            account,
            self.config,
            entry_timestamp_utc=timestamp,
        )
        throttle_decision = evaluate_entry_throttle(
            throttle,
            self.throttle_policy,
            entry_timestamp_utc=timestamp,
        )
        level = _text(kill_level, "kill_level").upper()
        kill_reasons = () if level == "NONE" else (f"PEE_S4_KILL_{level}",)
        loss_reasons = (
            ("LOSS_CLUSTER_PAUSE",)
            if loss_cluster.pause_entries_remaining > 0
            else ()
        )
        position_reasons = (
            (POSITION_OPEN_REASON,)
            if isinstance(position, PositionStateS2V2)
            else ()
        )
        reasons = self._unique_reasons(
            account_decision.reason_codes,
            throttle_decision.reason_codes,
            loss_reasons,
            kill_reasons,
            position_reasons,
        )
        exit_allowed = level in ("NONE", "SOFT")
        directive = {
            "NONE": "CONTINUE",
            "SOFT": "CONTINUE",
            "HARD": "STOP_LOOP",
            "EMERGENCY": "EXIT_PROCESS",
        }.get(level)
        if directive is None:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "unsupported V2 Kill Level",
            )
        trades_today = current.risk.trades_today
        loss_today = current.risk.loss_today
        trades_6h = current.risk.trades_6h
        last_trade = current.risk.last_trade_timestamp_utc
        if close_trade is not None:
            trades_today += 1
            trades_6h += 1
            last_trade = close_trade.exit_timestamp_utc
            if close_trade.net_pnl_quote < 0:
                loss_today += -close_trade.net_pnl_quote
        return PaperRiskStateS4V2(
            schema_version=2,
            system_state_id=position.system_state_id,
            kill_level=level,
            cooldown_until_utc=throttle_decision.disable_until_utc or "",
            trades_today=trades_today,
            loss_today=loss_today,
            anomaly_counter=current.risk.anomaly_counter,
            trades_6h=trades_6h,
            last_trade_timestamp_utc=last_trade,
            entry_allowed=not reasons and level == "NONE",
            exit_evaluation_allowed=exit_allowed,
            runtime_directive=directive,
            reason_codes=reasons,
            position_fingerprint=position.state_fingerprint,
            account_fingerprint=account.state_fingerprint,
            throttle_fingerprint=throttle.state_fingerprint,
            loss_cluster_fingerprint=loss_cluster.state_fingerprint,
            progress_cursor_fingerprint=progress_cursor.cursor_fingerprint,
            runtime_control_profile_id=self.runtime_control_profile_id,
            runtime_control_fingerprint=self.runtime_control_fingerprint,
            loss_cluster_policy_id=self.loss_cluster_policy_id,
            loss_cluster_policy_fingerprint=self.loss_cluster_policy_fingerprint,
            economics_profile_id=self.config.economics_profile_id,
            economics_model_version=self.config.economics_model_version,
            config_fingerprint=self.config.config_fingerprint,
            throttle_policy_profile_id=self.throttle_policy.policy_profile_id,
            throttle_policy_model_version=self.throttle_policy.policy_model_version,
            throttle_policy_fingerprint=self.throttle_policy.policy_fingerprint,
            authority_generation_id=current.authority_generation_id,
            transaction_sequence=sequence,
            journal_head=journal_head,
            last_transaction_event_id=event_id,
            last_transaction_timestamp_utc=timestamp,
            last_transaction_tick_id=tick_id,
        )

    def _build_transaction(
        self,
        current: AtomicPaperStateV2,
        *,
        event_id: str,
        ordering_space: str,
        effect: str,
        timestamp: str,
        tick_id: int,
        position_after: PositionArtifactV2,
        account_after: PaperAccountState,
        throttle_after: PaperEntryThrottleState,
        loss_after: LossClusterStateV2,
        cursor_after: AtomicProgressCursorV1,
        quote_after: EntryEconomicsQuoteArtifactV1 | None,
        accepted_entry_event: AcceptedEntryEventV1 | None = None,
        trade: TradeRecordV2 | None = None,
        risk_escalation: str = "",
        control_authorization_reference: str = "",
        target_kill_level: str | None = None,
        effect_position: PositionStateS2V2 | None = None,
        effect_entry_quote: EntryEconomicsQuoteArtifactV1 | None = None,
        effect_progress_cursor: AtomicProgressCursorV1 | None = None,
        effect_throttle_policy: PaperEntryThrottlePolicy | None = None,
        effect_entry_veto_candidate: AtomicEntryVetoCandidateV1 | None = None,
        effect_entry_denial_provenance: AtomicEntryDenialProvenanceV1 | None = None,
        loss_transition_updated_utc: str = "",
        loss_transition_policy_id: str = "",
        loss_transition_policy_fingerprint: str = "",
        loss_transition_lookback: int = 0,
        loss_transition_threshold: int = 0,
        loss_transition_pause_entries: int = 0,
    ) -> AtomicPaperTransactionV2:
        sequence = current.transaction_sequence + 1
        level = target_kill_level or (
            "SOFT" if risk_escalation == "NONE_TO_SOFT" else current.risk.kill_level
        )
        provisional_head = hashlib.sha256(
            b"atomic-v2-risk-business-pre-head"
        ).hexdigest()
        if effect_entry_denial_provenance is not None:
            if effect != TRANSACTION_PROGRESS:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                    "entry-denial provenance requires PROGRESS",
                )
            preliminary_risk = replace(
                current.risk,
                progress_cursor_fingerprint=cursor_after.cursor_fingerprint,
                transaction_sequence=sequence,
                journal_head=provisional_head,
                last_transaction_event_id=event_id,
                last_transaction_timestamp_utc=timestamp,
                last_transaction_tick_id=tick_id,
            )
        elif effect == TRANSACTION_KILL:
            kill_reason = f"PEE_S4_KILL_{level}"
            preliminary_risk = replace(
                current.risk,
                kill_level=level,
                entry_allowed=False,
                exit_evaluation_allowed=level in ("NONE", "SOFT"),
                runtime_directive={
                    "NONE": "CONTINUE",
                    "SOFT": "CONTINUE",
                    "HARD": "STOP_LOOP",
                    "EMERGENCY": "EXIT_PROCESS",
                }[level],
                reason_codes=self._unique_reasons(
                    tuple(
                        reason
                        for reason in current.risk.reason_codes
                        if not reason.startswith("PEE_S4_KILL_")
                    ),
                    (kill_reason,),
                ),
                transaction_sequence=sequence,
                journal_head=provisional_head,
                last_transaction_event_id=event_id,
                last_transaction_timestamp_utc=timestamp,
                last_transaction_tick_id=tick_id,
            )
        else:
            preliminary_risk = self._risk_after(
                current,
                position=position_after,
                account=account_after,
                throttle=throttle_after,
                loss_cluster=loss_after,
                progress_cursor=cursor_after,
                sequence=sequence,
                journal_head=provisional_head,
                event_id=event_id,
                timestamp=timestamp,
                tick_id=tick_id,
                kill_level=level,
                close_trade=trade,
            )
        head = AtomicPaperTransactionV2.journal_head_for(
            transaction_sequence=sequence,
            transaction_event_id=event_id,
            previous_journal_head=current.journal_head,
            ordering_space=ordering_space,
            primary_effect=effect,
            transaction_timestamp_utc=timestamp,
            causal_tick_id=tick_id,
            state_before=current,
            position_after=position_after,
            account_after=account_after,
            throttle_after=throttle_after,
            loss_cluster_after=loss_after,
            progress_cursor_after=cursor_after,
            entry_quote_after=quote_after,
            accepted_entry_event=accepted_entry_event,
            trade=trade,
            risk_escalation=risk_escalation,
            effect_position=effect_position,
            effect_entry_quote=effect_entry_quote,
            effect_progress_cursor=effect_progress_cursor,
            effect_throttle_policy=effect_throttle_policy,
            effect_entry_veto_candidate=effect_entry_veto_candidate,
            loss_transition_updated_utc=loss_transition_updated_utc,
            loss_transition_policy_id=loss_transition_policy_id,
            loss_transition_policy_fingerprint=loss_transition_policy_fingerprint,
            loss_transition_lookback=loss_transition_lookback,
            loss_transition_threshold=loss_transition_threshold,
            loss_transition_pause_entries=loss_transition_pause_entries,
            effect_target_kill_level=(target_kill_level or ""),
            kill_level_after=level,
            risk_business_after_fingerprint=canonical_json_sha256(
                preliminary_risk.business_payload()
            ),
            control_authorization_reference=control_authorization_reference,
            effect_entry_denial_provenance=effect_entry_denial_provenance,
        )
        risk_after = replace(preliminary_risk, journal_head=head)
        state_after = AtomicPaperStateV2(
            schema_version=2,
            coordinator_id=current.coordinator_id,
            system_state_id=position_after.system_state_id,
            transaction_sequence=sequence,
            journal_head=head,
            last_transaction_event_id=event_id,
            position=position_after,
            account=account_after,
            throttle=throttle_after,
            loss_cluster=loss_after,
            progress_cursor=cursor_after,
            risk=risk_after,
            entry_quote=quote_after,
            runtime_control_profile_id=current.runtime_control_profile_id,
            runtime_control_fingerprint=current.runtime_control_fingerprint,
            loss_cluster_policy_id=current.loss_cluster_policy_id,
            loss_cluster_policy_fingerprint=current.loss_cluster_policy_fingerprint,
            state_owner_epoch=current.state_owner_epoch,
            authority_generation_id=current.authority_generation_id,
            authority_prepare_record_fingerprint=current.authority_prepare_record_fingerprint,
            authority_manifest_id=current.authority_manifest_id,
            authority_manifest_fingerprint=current.authority_manifest_fingerprint,
        )
        return AtomicPaperTransactionV2(
            schema_version=2,
            transaction_sequence=sequence,
            transaction_event_id=event_id,
            previous_journal_head=current.journal_head,
            ordering_space=ordering_space,
            primary_effect=effect,
            transaction_timestamp_utc=timestamp,
            causal_tick_id=tick_id,
            state_before=current,
            state_after=state_after,
            accepted_entry_event=accepted_entry_event,
            trade=trade,
            risk_escalation=risk_escalation,
            control_authorization_reference=control_authorization_reference,
            effect_position=effect_position,
            effect_entry_quote=effect_entry_quote,
            effect_progress_cursor=effect_progress_cursor,
            effect_throttle_policy=effect_throttle_policy,
            effect_entry_veto_candidate=effect_entry_veto_candidate,
            effect_entry_denial_provenance=effect_entry_denial_provenance,
            loss_transition_updated_utc=loss_transition_updated_utc,
            loss_transition_policy_id=loss_transition_policy_id,
            loss_transition_policy_fingerprint=loss_transition_policy_fingerprint,
            loss_transition_lookback=loss_transition_lookback,
            loss_transition_threshold=loss_transition_threshold,
            loss_transition_pause_entries=loss_transition_pause_entries,
            effect_target_kill_level=(target_kill_level or ""),
        )

    def _validate_transaction_derivation(
        self,
        transaction: AtomicPaperTransactionV2,
    ) -> None:
        before = transaction.state_before
        if transaction.primary_effect == TRANSACTION_OPEN:
            if transaction.effect_throttle_policy != self.throttle_policy:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                    "OPEN effect Throttle policy differs from coordinator binding",
                )
            position_after = transaction.effect_position
            account_after = before.account
            throttle_after = apply_accepted_entry(
                before.throttle,
                self.throttle_policy,
                transaction.accepted_entry_event,
            )
            loss_after = before.loss_cluster
            cursor_after = transaction.effect_progress_cursor
            quote_after = transaction.effect_entry_quote
        elif transaction.primary_effect == TRANSACTION_CLOSE:
            if (
                transaction.loss_transition_policy_id
                != self.loss_cluster_policy_id
                or transaction.loss_transition_policy_fingerprint
                != self.loss_cluster_policy_fingerprint
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                    "CLOSE Loss policy differs from coordinator binding",
                )
            position_after = _flat_position_after_trade(
                transaction.trade,
                before.position,
            )
            account_after = apply_trade_to_account(before.account, transaction.trade)
            throttle_after = before.throttle
            loss_after = apply_loss_cluster_close(
                before.loss_cluster,
                net_pnl_quote=transaction.trade.net_pnl_quote,
                updated_utc=transaction.loss_transition_updated_utc,
                policy_id=transaction.loss_transition_policy_id,
                policy_fingerprint=transaction.loss_transition_policy_fingerprint,
                lookback=transaction.loss_transition_lookback,
                loss_threshold=transaction.loss_transition_threshold,
                pause_entries=transaction.loss_transition_pause_entries,
            )
            cursor_after = transaction.effect_progress_cursor
            quote_after = None
        elif transaction.primary_effect == TRANSACTION_ENTRY_VETO:
            if (
                transaction.loss_transition_policy_id
                != self.loss_cluster_policy_id
                or transaction.loss_transition_policy_fingerprint
                != self.loss_cluster_policy_fingerprint
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.IDENTITY_MISMATCH,
                    "ENTRY_VETO Loss policy differs from coordinator binding",
                )
            position_after = before.position
            account_after = before.account
            throttle_after = before.throttle
            loss_after = apply_loss_cluster_entry_veto(
                before.loss_cluster,
                updated_utc=transaction.loss_transition_updated_utc,
                policy_id=transaction.loss_transition_policy_id,
                policy_fingerprint=transaction.loss_transition_policy_fingerprint,
            )
            cursor_after = transaction.effect_progress_cursor
            quote_after = before.entry_quote
        else:
            position_after = before.position
            account_after = before.account
            throttle_after = before.throttle
            loss_after = before.loss_cluster
            cursor_after = (
                transaction.effect_progress_cursor
                if transaction.primary_effect == TRANSACTION_PROGRESS
                else before.progress_cursor
            )
            quote_after = before.entry_quote
        rebuilt = self._build_transaction(
            transaction.state_before,
            event_id=transaction.transaction_event_id,
            ordering_space=transaction.ordering_space,
            effect=transaction.primary_effect,
            timestamp=transaction.transaction_timestamp_utc,
            tick_id=transaction.causal_tick_id,
            position_after=position_after,
            account_after=account_after,
            throttle_after=throttle_after,
            loss_after=loss_after,
            cursor_after=cursor_after,
            quote_after=quote_after,
            accepted_entry_event=transaction.accepted_entry_event,
            trade=transaction.trade,
            risk_escalation=transaction.risk_escalation,
            control_authorization_reference=(
                transaction.control_authorization_reference
            ),
            target_kill_level=(
                transaction.effect_target_kill_level
                if transaction.primary_effect == TRANSACTION_KILL
                else None
            ),
            effect_position=transaction.effect_position,
            effect_entry_quote=transaction.effect_entry_quote,
            effect_progress_cursor=transaction.effect_progress_cursor,
            effect_throttle_policy=transaction.effect_throttle_policy,
            effect_entry_veto_candidate=transaction.effect_entry_veto_candidate,
            effect_entry_denial_provenance=(
                transaction.effect_entry_denial_provenance
            ),
            loss_transition_updated_utc=transaction.loss_transition_updated_utc,
            loss_transition_policy_id=transaction.loss_transition_policy_id,
            loss_transition_policy_fingerprint=(
                transaction.loss_transition_policy_fingerprint
            ),
            loss_transition_lookback=transaction.loss_transition_lookback,
            loss_transition_threshold=transaction.loss_transition_threshold,
            loss_transition_pause_entries=(
                transaction.loss_transition_pause_entries
            ),
        )
        if rebuilt != transaction:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Atomic V2 transaction is not the exact authoritative derivation",
            )

    @staticmethod
    def _validate_new_cursor(
        current: AtomicPaperStateV2,
        cursor: AtomicProgressCursorV1,
    ) -> None:
        if not isinstance(cursor, AtomicProgressCursorV1) or not cursor.snapshot_id:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                "Tick transaction requires a complete Progress Cursor",
            )
        previous = current.progress_cursor
        if previous.snapshot_id and (
            cursor.snapshot_id == previous.snapshot_id
            or cursor.tick_id <= previous.tick_id
            or cursor.timestamp_utc < previous.timestamp_utc
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                "Progress Cursor regressed",
            )

    @staticmethod
    def _validate_tick_capability(current: AtomicPaperStateV2) -> None:
        if current.risk.kill_level in ("HARD", "EMERGENCY"):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "terminal KILL forbids further Tick transaction evaluation",
            )

    def _validate_open_guards(
        self,
        current: AtomicPaperStateV2,
        *,
        entry_timestamp_utc: str,
    ) -> None:
        account = evaluate_account_entry_guard(
            current.account,
            self.config,
            entry_timestamp_utc=entry_timestamp_utc,
        )
        throttle = evaluate_entry_throttle(
            current.throttle,
            self.throttle_policy,
            entry_timestamp_utc=entry_timestamp_utc,
        )
        authoritative_allowed = (
            account.entry_allowed
            and throttle.entry_allowed
            and current.loss_cluster.pause_entries_remaining == 0
            and current.risk.kill_level == "NONE"
            and isinstance(current.position, PositionStateS2FlatV2)
        )
        if not authoritative_allowed or not current.risk.entry_allowed:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "OPEN failed authoritative Account/Loss/Throttle/Control guards",
            )

    @_root_exclusive
    def commit_progress(
        self,
        *,
        progress_cursor: AtomicProgressCursorV1,
        transaction_event_id: str,
        effect_entry_denial_provenance: AtomicEntryDenialProvenanceV1 | None = None,
        risk_escalation: str = "",
        simulate_interruption_after_journal: bool = False,
        simulate_interruption_at: str = "",
    ) -> AtomicCommitResultV2:
        event_id = _text(transaction_event_id, "transaction_event_id")
        existing = self._existing(event_id)
        if existing is not None:
            if (
                existing.primary_effect != TRANSACTION_PROGRESS
                or existing.state_after.progress_cursor != progress_cursor
                or existing.risk_escalation != risk_escalation
                or existing.effect_entry_denial_provenance
                != effect_entry_denial_provenance
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.PROGRESS_CONFLICT,
                    "same PROGRESS Event ID contains a different payload",
                )
            return self._commit(existing, simulate_interruption_after_journal=False)
        current = self.load_state()
        self._validate_tick_capability(current)
        self._validate_new_cursor(current, progress_cursor)
        escalation = _text(risk_escalation, "risk_escalation", allow_empty=True).upper()
        if escalation not in ("", "NONE_TO_SOFT"):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "Tick risk escalation may only be NONE_TO_SOFT",
            )
        transaction = self._build_transaction(
            current,
            event_id=event_id,
            ordering_space="TICK",
            effect=TRANSACTION_PROGRESS,
            timestamp=progress_cursor.timestamp_utc,
            tick_id=progress_cursor.tick_id,
            position_after=current.position,
            account_after=current.account,
            throttle_after=current.throttle,
            loss_after=current.loss_cluster,
            cursor_after=progress_cursor,
            quote_after=current.entry_quote,
            risk_escalation=escalation,
            effect_progress_cursor=progress_cursor,
            effect_entry_denial_provenance=effect_entry_denial_provenance,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
            simulate_interruption_at=simulate_interruption_at,
        )

    @_root_exclusive
    def commit_open(
        self,
        *,
        position_after: PositionStateS2V2,
        entry_quote: EntryEconomicsQuoteArtifactV1,
        accepted_entry_event: AcceptedEntryEventV1,
        progress_cursor: AtomicProgressCursorV1,
        risk_escalation: str = "",
        simulate_interruption_after_journal: bool = False,
        simulate_interruption_at: str = "",
    ) -> AtomicCommitResultV2:
        if not isinstance(accepted_entry_event, AcceptedEntryEventV1):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "OPEN requires AcceptedEntryEventV1",
            )
        event_id = accepted_entry_event.entry_event_id
        existing = self._existing(event_id)
        if existing is not None:
            if (
                existing.primary_effect != TRANSACTION_OPEN
                or existing.state_after.position != position_after
                or existing.state_after.entry_quote != entry_quote
                or existing.state_after.progress_cursor != progress_cursor
                or existing.accepted_entry_event != accepted_entry_event
                or existing.risk_escalation != risk_escalation
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same OPEN Event ID contains a different payload",
                )
            return self._commit(existing, simulate_interruption_after_journal=False)
        current = self.load_state()
        self._validate_tick_capability(current)
        if not isinstance(current.position, PositionStateS2FlatV2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "OPEN requires FLAT Atomic V2 State",
            )
        self._validate_open_guards(
            current,
            entry_timestamp_utc=progress_cursor.timestamp_utc,
        )
        self._validate_new_cursor(current, progress_cursor)
        try:
            throttle_after = apply_accepted_entry(
                current.throttle,
                self.throttle_policy,
                accepted_entry_event,
            )
        except PaperEntryThrottleError as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "OPEN is blocked by Entry Throttle",
            ) from exc
        transaction = self._build_transaction(
            current,
            event_id=event_id,
            ordering_space="TICK",
            effect=TRANSACTION_OPEN,
            timestamp=progress_cursor.timestamp_utc,
            tick_id=progress_cursor.tick_id,
            position_after=position_after,
            account_after=current.account,
            throttle_after=throttle_after,
            loss_after=current.loss_cluster,
            cursor_after=progress_cursor,
            quote_after=entry_quote,
            accepted_entry_event=accepted_entry_event,
            risk_escalation=_text(risk_escalation, "risk_escalation", allow_empty=True).upper(),
            effect_position=position_after,
            effect_entry_quote=entry_quote,
            effect_progress_cursor=progress_cursor,
            effect_throttle_policy=self.throttle_policy,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
            simulate_interruption_at=simulate_interruption_at,
        )

    @_root_exclusive
    def commit_close(
        self,
        *,
        position_after: PositionStateS2FlatV2,
        trade: TradeRecordV2,
        progress_cursor: AtomicProgressCursorV1,
        loss_updated_utc: str,
        loss_lookback: int = 10,
        loss_threshold: int = 5,
        loss_pause_entries: int = 3,
        risk_escalation: str = "",
        simulate_interruption_after_journal: bool = False,
        simulate_interruption_at: str = "",
    ) -> AtomicCommitResultV2:
        if not isinstance(trade, TradeRecordV2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "CLOSE requires TradeRecordV2",
            )
        event_id = trade.settlement_event_id
        existing = self._existing(event_id)
        if existing is not None:
            if (
                existing.primary_effect != TRANSACTION_CLOSE
                or existing.trade != trade
                or existing.state_after.position != position_after
                or existing.state_after.progress_cursor != progress_cursor
                or existing.risk_escalation != risk_escalation
                or existing.loss_transition_updated_utc
                != _utc_timestamp_seconds(loss_updated_utc, "loss_updated_utc")
                or existing.loss_transition_lookback != loss_lookback
                or existing.loss_transition_threshold != loss_threshold
                or existing.loss_transition_pause_entries != loss_pause_entries
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same CLOSE Event ID contains a different payload",
                )
            return self._commit(existing, simulate_interruption_after_journal=False)
        current = self.load_state()
        self._validate_tick_capability(current)
        if not isinstance(current.position, PositionStateS2V2) or current.entry_quote is None:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_QUOTE_REQUIRED,
                "CLOSE requires OPEN State and committed Entry Quote",
            )
        self._validate_new_cursor(current, progress_cursor)
        _validate_trade_matches_open(trade, current.position)
        expected_position_after = _flat_position_after_trade(trade, current.position)
        if position_after != expected_position_after:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "CLOSE FLAT State does not exactly derive from the settled Trade",
            )
        quote = current.entry_quote
        if (
            trade.side != quote.side
            or trade.quantity != quote.quantity
            or trade.reference_entry_price != quote.reference_entry_price
            or trade.modeled_entry_fill_price != quote.modeled_entry_fill_price
            or trade.entry_fee_quote != quote.entry_fee_quote
            or trade.config_fingerprint != quote.config_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_QUOTE_REQUIRED,
                "CLOSE Trade does not derive from committed Entry Quote",
            )
        try:
            account_after = apply_trade_to_account(current.account, trade)
            loss_after = apply_loss_cluster_close(
                current.loss_cluster,
                net_pnl_quote=trade.net_pnl_quote,
                updated_utc=loss_updated_utc,
                policy_id=self.loss_cluster_policy_id,
                policy_fingerprint=self.loss_cluster_policy_fingerprint,
                lookback=loss_lookback,
                loss_threshold=loss_threshold,
                pause_entries=loss_pause_entries,
            )
        except (PaperArtifactError, LossClusterStateError) as exc:
            raise PaperAtomicCoordinatorError(
                getattr(exc, "reason_code", AtomicCoordinatorReasonCode.TRANSACTION_INVALID),
                "CLOSE Account/Loss transition is invalid",
            ) from exc
        transaction = self._build_transaction(
            current,
            event_id=event_id,
            ordering_space="TICK",
            effect=TRANSACTION_CLOSE,
            timestamp=progress_cursor.timestamp_utc,
            tick_id=progress_cursor.tick_id,
            position_after=position_after,
            account_after=account_after,
            throttle_after=current.throttle,
            loss_after=loss_after,
            cursor_after=progress_cursor,
            quote_after=None,
            trade=trade,
            risk_escalation=_text(risk_escalation, "risk_escalation", allow_empty=True).upper(),
            effect_progress_cursor=progress_cursor,
            loss_transition_updated_utc=loss_updated_utc,
            loss_transition_policy_id=self.loss_cluster_policy_id,
            loss_transition_policy_fingerprint=self.loss_cluster_policy_fingerprint,
            loss_transition_lookback=loss_lookback,
            loss_transition_threshold=loss_threshold,
            loss_transition_pause_entries=loss_pause_entries,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
            simulate_interruption_at=simulate_interruption_at,
        )

    @_root_exclusive
    def commit_entry_veto(
        self,
        *,
        progress_cursor: AtomicProgressCursorV1,
        entry_candidate: AtomicEntryVetoCandidateV1,
        transaction_event_id: str,
        loss_updated_utc: str,
        risk_escalation: str = "",
        simulate_interruption_after_journal: bool = False,
        simulate_interruption_at: str = "",
    ) -> AtomicCommitResultV2:
        event_id = _text(transaction_event_id, "transaction_event_id")
        existing = self._existing(event_id)
        if existing is not None:
            if (
                existing.primary_effect != TRANSACTION_ENTRY_VETO
                or existing.state_after.progress_cursor != progress_cursor
                or existing.effect_entry_veto_candidate != entry_candidate
                or existing.risk_escalation != risk_escalation
                or existing.loss_transition_updated_utc
                != _utc_timestamp_seconds(loss_updated_utc, "loss_updated_utc")
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same ENTRY_VETO Event ID contains a different payload",
                )
            return self._commit(existing, simulate_interruption_after_journal=False)
        current = self.load_state()
        self._validate_tick_capability(current)
        if not isinstance(current.position, PositionStateS2FlatV2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "ENTRY_VETO is only valid for a FLAT Entry candidate",
            )
        self._validate_new_cursor(current, progress_cursor)
        if (
            not isinstance(entry_candidate, AtomicEntryVetoCandidateV1)
            or entry_candidate.entry_veto_event_id != event_id
            or entry_candidate.snapshot_id != progress_cursor.snapshot_id
            or entry_candidate.timestamp_utc != progress_cursor.timestamp_utc
            or entry_candidate.tick_id != progress_cursor.tick_id
            or entry_candidate.intent_id != progress_cursor.intent_id
            or entry_candidate.symbol != current.position.symbol
            or entry_candidate.loss_cluster_state_fingerprint
            != current.loss_cluster.state_fingerprint
            or _utc_timestamp_seconds(loss_updated_utc, "loss_updated_utc")
            != progress_cursor.timestamp_utc
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "ENTRY_VETO requires the exact current OPEN candidate",
            )
        try:
            loss_after = apply_loss_cluster_entry_veto(
                current.loss_cluster,
                updated_utc=loss_updated_utc,
                policy_id=self.loss_cluster_policy_id,
                policy_fingerprint=self.loss_cluster_policy_fingerprint,
            )
        except LossClusterStateError as exc:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ENTRY_BLOCKED,
                "ENTRY_VETO requires an active Loss Cluster pause",
            ) from exc
        transaction = self._build_transaction(
            current,
            event_id=event_id,
            ordering_space="TICK",
            effect=TRANSACTION_ENTRY_VETO,
            timestamp=progress_cursor.timestamp_utc,
            tick_id=progress_cursor.tick_id,
            position_after=current.position,
            account_after=current.account,
            throttle_after=current.throttle,
            loss_after=loss_after,
            cursor_after=progress_cursor,
            quote_after=current.entry_quote,
            risk_escalation=_text(risk_escalation, "risk_escalation", allow_empty=True).upper(),
            effect_progress_cursor=progress_cursor,
            effect_entry_veto_candidate=entry_candidate,
            loss_transition_updated_utc=loss_updated_utc,
            loss_transition_policy_id=self.loss_cluster_policy_id,
            loss_transition_policy_fingerprint=self.loss_cluster_policy_fingerprint,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
            simulate_interruption_at=simulate_interruption_at,
        )

    @_root_exclusive
    def commit_kill(
        self,
        *,
        transaction_event_id: str,
        target_kill_level: str,
        reason_code: str,
        authorization_reference: str,
        transaction_timestamp_utc: str,
        causal_tick_id: int = 0,
        simulate_interruption_after_journal: bool = False,
        simulate_interruption_at: str = "",
    ) -> AtomicCommitResultV2:
        event_id = _text(transaction_event_id, "transaction_event_id")
        target = _text(target_kill_level, "target_kill_level").upper()
        reference = _text(authorization_reference, "authorization_reference")
        reason = _text(reason_code, "reason_code")
        bound_reference = f"{reference}:{reason}"
        existing = self._existing(event_id)
        if existing is not None:
            if (
                existing.primary_effect != TRANSACTION_KILL
                or existing.state_after.risk.kill_level != target
                or existing.control_authorization_reference != bound_reference
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "same KILL Event ID contains a different payload",
                )
            return self._commit(existing, simulate_interruption_after_journal=False)
        current = self.load_state()
        if target not in KILL_LEVELS or target == current.risk.kill_level:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.TRANSACTION_INVALID,
                "KILL requires a different supported target level",
            )
        transaction = self._build_transaction(
            current,
            event_id=event_id,
            ordering_space="CONTROL",
            effect=TRANSACTION_KILL,
            timestamp=_utc_timestamp_seconds(
                transaction_timestamp_utc,
                "transaction_timestamp_utc",
            ),
            tick_id=_integer(causal_tick_id, "causal_tick_id"),
            position_after=current.position,
            account_after=current.account,
            throttle_after=current.throttle,
            loss_after=current.loss_cluster,
            cursor_after=current.progress_cursor,
            quote_after=current.entry_quote,
            control_authorization_reference=bound_reference,
            target_kill_level=target,
        )
        return self._commit(
            transaction,
            simulate_interruption_after_journal=simulate_interruption_after_journal,
            simulate_interruption_at=simulate_interruption_at,
        )

    def recover(self) -> AtomicRecoveryResultV2:
        with self._exclusive_root_lock():
            return self._recover_locked()

    def _recover_locked(self) -> AtomicRecoveryResultV2:
        current = self.load_state()
        entries = self._transactions()
        index = self._snapshot_index(current, entries)
        if index is None:
            reason = (
                AtomicCoordinatorReasonCode.STATE_AHEAD_OF_JOURNAL
                if current.transaction_sequence > len(entries)
                else AtomicCoordinatorReasonCode.JOURNAL_CONFLICT
            )
            raise PaperAtomicCoordinatorError(reason, "Atomic V2 snapshot is not a journal prefix")
        recovered = len(entries) - index
        if recovered:
            current = entries[-1][1].state_after
            _atomic_write_json(self.state_path, current.to_record())
        return AtomicRecoveryResultV2(
            state=current,
            journal_count=len(entries),
            recovered_transaction_count=recovered,
        )

    def i6_validate_authority_root(
        self,
        *,
        committed_target_state_fingerprint: str,
        authority_generation_id: str,
        authority_prepare_record_fingerprint: str,
    ) -> AtomicPaperStateV2:
        """Validate complete journal ancestry from an Authority-COMMIT target.

        This additive I6 primitive is read-only.  It deliberately receives no
        Lifecycle tip or COMMIT fingerprint because neither belongs in the
        Atomic State fingerprint.
        """

        with self._exclusive_root_lock():
            target_fingerprint = _sha256(
                committed_target_state_fingerprint,
                "committed_target_state_fingerprint",
            )
            generation = _text(authority_generation_id, "authority_generation_id")
            prepare_fingerprint = _sha256(
                authority_prepare_record_fingerprint,
                "authority_prepare_record_fingerprint",
            )
            current = self.load_state()
            entries = self._transactions()
            index = self._snapshot_index(current, entries)
            if index is None or index != len(entries):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                    "Atomic snapshot is not the complete durable journal tip",
                )
            base = current if not entries else entries[0][1].state_before
            if (
                base.transaction_sequence != 0
                or base.journal_head != "EMPTY"
                or base.state_fingerprint != target_fingerprint
                or base.authority_generation_id != generation
                or base.authority_prepare_record_fingerprint != prepare_fingerprint
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                    "Atomic journal does not descend from the committed target",
                )
            expected = base
            for _, transaction in entries:
                if (
                    transaction.state_before != expected
                    or transaction.state_before.authority_generation_id != generation
                    or transaction.state_after.authority_generation_id != generation
                    or transaction.state_before.authority_prepare_record_fingerprint
                    != prepare_fingerprint
                    or transaction.state_after.authority_prepare_record_fingerprint
                    != prepare_fingerprint
                ):
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                        "Atomic journal changed its Authority root",
                    )
                expected = transaction.state_after
            if expected != current:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                    "Atomic current State differs from Authority ancestry",
                )
            return current

    def i6_materialize_durable_head(
        self,
        *,
        expected_transaction_sequence: int,
        expected_journal_head: str,
        expected_snapshot_fingerprint: str,
    ) -> AtomicRecoveryResultV2:
        """Materialize only an already durable journal head, without redecision."""

        with self._exclusive_root_lock():
            sequence = _integer(
                expected_transaction_sequence,
                "expected_transaction_sequence",
            )
            head = expected_journal_head
            if head != "EMPTY":
                head = _sha256(head, "expected_journal_head")
            snapshot_fingerprint = _sha256(
                expected_snapshot_fingerprint,
                "expected_snapshot_fingerprint",
            )
            before = self.load_state()
            if before.state_fingerprint != snapshot_fingerprint:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                    "Recovery pre-Snapshot fingerprint differs",
                )
            entries = self._transactions()
            if sequence != len(entries):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_GAP,
                    "Recovery expected sequence is not the durable journal tip",
                )
            durable = before if not entries else entries[-1][1].state_after
            if durable.transaction_sequence != sequence or durable.journal_head != head:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "Recovery expected head differs from the durable journal",
                )
            index = self._snapshot_index(before, entries)
            if index is None:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "Recovery Snapshot is not a valid journal prefix",
                )
            recovered = len(entries) - index
            if recovered:
                _atomic_write_json(self.state_path, durable.to_record())
            return AtomicRecoveryResultV2(
                state=durable,
                journal_count=len(entries),
                recovered_transaction_count=recovered,
            )

    def i6_reconcile_terminal_journal(
        self,
        *,
        runtime_session_open_journal_head: str,
        worker_exclusion_proof_fingerprint: str,
        transaction_event_id: str,
        transaction_timestamp_utc: str,
        causal_tick_id: int,
        control_authorization_reference: str,
        reason_code: str,
    ) -> AtomicCommitResultV2:
        """Journal-first terminal reconciliation after external death proof.

        Trust validation is performed by the I6 boundary before this method is
        called.  The proof fingerprint is bound into the KILL authorization
        reference so a different proof cannot replay the same event.
        """

        with self._exclusive_root_lock():
            proof_fingerprint = _sha256(
                worker_exclusion_proof_fingerprint,
                "worker_exclusion_proof_fingerprint",
            )
            open_head = runtime_session_open_journal_head
            if open_head != "EMPTY":
                open_head = _sha256(open_head, "runtime_session_open_journal_head")
            current = self.load_state()
            entries = self._transactions()
            index = self._snapshot_index(current, entries)
            if index is None:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "Terminal reconciliation Snapshot is not a journal prefix",
                )
            if open_head != "EMPTY" and not any(
                transaction.state_before.journal_head == open_head
                or transaction.state_after.journal_head == open_head
                for _, transaction in entries
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                    "Runtime Session OPEN head is outside the journal ancestry",
                )
            terminal = [
                transaction
                for _, transaction in entries
                if transaction.primary_effect == TRANSACTION_KILL
                and transaction.state_after.risk.kill_level == "EMERGENCY"
            ]
            if len(terminal) > 1:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                    "Atomic terminal journal is ambiguous",
                )
            if terminal:
                durable = entries[-1][1].state_after
                if terminal[0] != entries[-1][1]:
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                        "terminal KILL is not the journal tip",
                    )
                bound_suffix = (
                    f":WORKER-DEATH-PROOF:{proof_fingerprint}:{reason_code}"
                )
                if (
                    terminal[0].transaction_event_id != transaction_event_id
                    or terminal[0].transaction_timestamp_utc
                    != transaction_timestamp_utc
                    or terminal[0].causal_tick_id != causal_tick_id
                    or not terminal[0].control_authorization_reference.endswith(
                        bound_suffix
                    )
                    or terminal[0].effect_target_kill_level != "EMERGENCY"
                ):
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.JOURNAL_CONFLICT,
                        "existing terminal KILL identity differs",
                    )
                if current != durable:
                    _atomic_write_json(self.state_path, durable.to_record())
                return AtomicCommitResultV2(
                    state=durable,
                    journal_path=entries[-1][0],
                    newly_committed=False,
                    already_committed=True,
                    recovered_incomplete_commit=current != durable,
                )
            if index != len(entries):
                current = entries[-1][1].state_after
                _atomic_write_json(self.state_path, current.to_record())
            bound_reference = (
                f"{control_authorization_reference}:WORKER-DEATH-PROOF:"
                f"{proof_fingerprint}"
            )
            return self.commit_kill(
                transaction_event_id=transaction_event_id,
                transaction_timestamp_utc=transaction_timestamp_utc,
                causal_tick_id=causal_tick_id,
                target_kill_level="EMERGENCY",
                authorization_reference=bound_reference,
                reason_code=reason_code,
            )

    def migrate_v1_to_v2(
        self,
        *,
        source_state: AtomicPaperStateV1,
        source_loss_cluster: LossClusterStateV2,
        target_state_template: AtomicPaperStateV2,
        migration: AtomicV1ToV2MigrationArtifactV1,
        lifecycle_ledger: IU4LifecycleLedgerV1,
        simulate_interruption_after_prepare: bool = False,
        simulate_interruption_after_target: bool = False,
        simulate_interruption_before_prepare: bool = False,
        simulate_interruption_after_commit: bool = False,
        simulate_interruption_after_completion_claim: bool = False,
        simulate_interruption_before_commit: bool = False,
        reconcile_incomplete_migration: bool = False,
        completion_authorization_record_fingerprint: str = "NONE",
    ) -> AtomicMigrationResultV1:
        if not isinstance(source_state, AtomicPaperStateV1) or not isinstance(
            source_loss_cluster,
            LossClusterStateV2,
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.ATOMIC_SCHEMA_UNSUPPORTED,
                "migration requires Atomic V1 and LossClusterStateV2",
            )
        if source_state.state_fingerprint != migration.source_state_fingerprint:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source Atomic V1 fingerprint mismatch",
            )
        if source_loss_cluster.state_fingerprint != migration.source_loss_cluster_fingerprint:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source Loss Cluster fingerprint mismatch",
            )
        if not isinstance(source_state.position, PositionStateS2FlatV2):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                "migration rejects an OPEN Atomic V1 position",
            )
        source_path = Path(migration.source_state_path)
        if not source_path.is_file() or source_path.is_symlink():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                "migration source Atomic V1 path is missing or unsafe",
            )
        source_bytes = source_path.read_bytes()
        if hashlib.sha256(source_bytes).hexdigest() != migration.source_state_sha256:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source Atomic V1 byte checksum mismatch",
            )
        expected_source_bytes = (
            json.dumps(
                source_state.to_record(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            + "\n"
        ).encode("ascii")
        if source_bytes != expected_source_bytes:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source Atomic V1 bytes are not canonical",
            )
        if AtomicPaperStateV1.from_record(json.loads(source_bytes.decode("ascii"))) != source_state:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source bytes do not match supplied Atomic V1 State",
            )
        source_loss_path = Path(migration.source_loss_cluster_path)
        if not source_loss_path.is_file() or source_loss_path.is_symlink():
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                "migration source Loss Cluster path is missing or unsafe",
            )
        source_loss_bytes = source_loss_path.read_bytes()
        if (
            hashlib.sha256(source_loss_bytes).hexdigest()
            != migration.source_loss_cluster_sha256
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source Loss Cluster byte checksum mismatch",
            )
        expected_loss_bytes = (
            json.dumps(
                source_loss_cluster.to_record(),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
            )
            + "\n"
        ).encode("ascii")
        if source_loss_bytes != expected_loss_bytes:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source Loss Cluster bytes are not canonical",
            )
        if LossClusterStateV2.from_record(
            json.loads(source_loss_bytes.decode("ascii"))
        ) != source_loss_cluster:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration source bytes do not match supplied Loss Cluster State",
            )
        if (
            not isinstance(target_state_template.position, PositionStateS2FlatV2)
            or target_state_template.entry_quote is not None
            or target_state_template.transaction_sequence != 0
            or target_state_template.loss_cluster != source_loss_cluster
            or target_state_template.authority_manifest_id != migration.manifest_id
            or target_state_template.authority_manifest_fingerprint
            != migration.manifest_fingerprint
            or target_state_template.system_state_id
            != migration.target_system_state_id
            or target_state_template.position.state_fingerprint
            != migration.target_position_fingerprint
            or target_state_template.account.state_fingerprint
            != migration.target_account_fingerprint
            or target_state_template.throttle.state_fingerprint
            != migration.target_throttle_fingerprint
            or target_state_template.loss_cluster.state_fingerprint
            != migration.target_loss_cluster_fingerprint
            or target_state_template.progress_cursor.cursor_fingerprint
            != migration.target_progress_cursor_fingerprint
            or canonical_json_sha256(target_state_template.risk.business_payload())
            != migration.target_risk_business_fingerprint
            or target_state_template.state_owner_epoch
            != migration.target_state_owner_epoch
            or target_state_template.runtime_control_profile_id
            != migration.runtime_control_profile_id
            or target_state_template.runtime_control_fingerprint
            != migration.runtime_control_fingerprint
            or target_state_template.loss_cluster_policy_id
            != migration.loss_cluster_policy_id
            or target_state_template.loss_cluster_policy_fingerprint
            != migration.loss_cluster_policy_fingerprint
            or target_state_template.account.economics_profile_id
            != migration.economics_profile_id
            or target_state_template.account.economics_model_version
            != migration.economics_model_version
            or target_state_template.account.config_fingerprint
            != migration.config_fingerprint
            or target_state_template.throttle.policy_profile_id
            != migration.throttle_policy_profile_id
            or target_state_template.throttle.policy_model_version
            != migration.throttle_policy_model_version
            or target_state_template.throttle.policy_fingerprint
            != migration.throttle_policy_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                "migration target template is incomplete or contradictory",
            )
        target_business = target_state_template.business_payload()
        if (
            canonical_json_sha256(target_business)
            != migration.target_business_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration target business fingerprint mismatch",
            )
        generation = authority_generation_id(
            operation="ATOMIC_V1_TO_V2_MIGRATION",
            source_authority_generation_id=migration.source_authority_generation_id,
            source_authority_commit_anchor=migration.source_authority_commit_anchor,
            manifest_fingerprint=migration.manifest_fingerprint,
            approval_fingerprint=migration.approval_fingerprint,
            target_business_payload=target_business,
        )
        target_core = {
            "target_business_payload": target_business,
            "authority_generation_id": generation,
        }
        if (
            lifecycle_fingerprint(target_core)
            != migration.target_state_core_fingerprint
        ):
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration target core fingerprint mismatch",
            )
        ledger_view = lifecycle_ledger.view()
        ledger_records = lifecycle_ledger.records()
        prepare_event_id = f"{migration.migration_id}:PREPARE"
        commit_event_id = f"{migration.migration_id}:COMMIT"
        existing_prepare = next(
            (
                record
                for record in ledger_records
                if record.lifecycle_event_id == prepare_event_id
            ),
            None,
        )
        existing_commit = next(
            (
                record
                for record in ledger_records
                if record.lifecycle_event_id == commit_event_id
            ),
            None,
        )
        completion_record = None
        if completion_authorization_record_fingerprint != "NONE":
            completion_fingerprint = _sha256(
                completion_authorization_record_fingerprint,
                "completion_authorization_record_fingerprint",
            )
            completion_record = next(
                (
                    record
                    for record in ledger_records
                    if record.record_fingerprint == completion_fingerprint
                ),
                None,
            )
            if completion_record is None:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "completion authorization consumption record is missing",
                )
        owner_is_source = (
            ledger_view.owner_epoch == migration.previous_owner_epoch
            and migration.new_owner_epoch == ledger_view.owner_epoch + 1
        )
        owner_is_completed_target = (
            reconcile_incomplete_migration
            and existing_commit is not None
            and ledger_view.owner_epoch == migration.new_owner_epoch
        )
        if not owner_is_source and not owner_is_completed_target:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                "migration owner epoch does not match Lifecycle authority",
            )
        prepare_payload = {
            "operation": "ATOMIC_V1_TO_V2_MIGRATION",
            "source_state_schema": 1,
            "source_state_path": migration.source_state_path,
            "source_state_fingerprint": migration.source_state_fingerprint,
            "source_loss_cluster_path": migration.source_loss_cluster_path,
            "source_loss_cluster_fingerprint": migration.source_loss_cluster_fingerprint,
            "target_state_schema": 2,
            "target_state_path": migration.target_state_path,
            "target_business_payload": target_business,
            "target_state_core_fingerprint": lifecycle_fingerprint(target_core),
            "authority_generation_id": generation,
            "manifest_id": migration.manifest_id,
            "manifest_fingerprint": migration.manifest_fingerprint,
            "approval_id": migration.approval_id,
            "approval_fingerprint": migration.approval_fingerprint,
            "source_authority_generation_id": migration.source_authority_generation_id,
            "source_authority_commit_anchor": migration.source_authority_commit_anchor,
            "previous_owner_epoch": migration.previous_owner_epoch,
            "new_owner_epoch": migration.new_owner_epoch,
            "operator": migration.operator,
            "timestamp_utc": migration.migration_timestamp_utc,
        }
        if completion_record is not None and existing_prepare is None:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                "completion authorization consumption must follow the exact existing PREPARE",
            )
        if simulate_interruption_before_prepare:
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption before migration PREPARE"
            )
        if existing_prepare is not None:
            if (
                not reconcile_incomplete_migration
                or existing_prepare.record_type
                != "ATOMIC_V1_TO_V2_MIGRATION_PREPARE"
                or existing_prepare.payload != prepare_payload
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "open migration PREPARE requires exact explicit reconciliation",
                )
            completion_payload = (
                {} if completion_record is None else completion_record.payload
            )
            completion_valid = (
                completion_record is not None
                and completion_record.record_type == "RESTART_AUTH_CONSUME"
                and completion_payload.get("operation")
                == "COMPLETE_AUTHORITY_PREPARE"
                and completion_payload.get("completion_prepare_event_id")
                == prepare_event_id
                and completion_payload.get("completion_prepare_fingerprint")
                == existing_prepare.record_fingerprint
                and completion_payload.get("target_authority_generation_id")
                == generation
                and completion_payload.get("pre_state_fingerprint")
                == source_state.state_fingerprint
                and completion_payload.get("pre_journal_head") == "EMPTY"
                and completion_payload.get("source_authority_generation_id")
                == migration.source_authority_generation_id
                and completion_payload.get("source_authority_commit_anchor")
                == migration.source_authority_commit_anchor
                and completion_record.lifecycle_sequence
                > existing_prepare.lifecycle_sequence
                and completion_record.previous_record_fingerprint
                == completion_payload.get("pre_attempt_ledger_tip")
            )
            existing_commit_recovered = (
                existing_commit is not None
                and existing_commit.payload.get("completion_provenance")
                == "RECOVERED_AFTER_PREPARE"
            )
            if (existing_commit is None or existing_commit_recovered) and not completion_valid:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "open migration PREPARE requires consumed completion authorization",
                )
            if existing_commit is not None and not existing_commit_recovered:
                if completion_record is not None:
                    raise PaperAtomicCoordinatorError(
                        AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                        "DIRECT migration COMMIT cannot bind completion authorization",
                    )
            elif existing_commit is not None and (
                existing_commit.payload.get(
                    "completion_authorization_record_fingerprint"
                )
                != completion_record.record_fingerprint
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                    "completed migration readback used another authorization",
                )
            prepare = existing_prepare
        else:
            if ledger_view.open_authority_prepare_event_id:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "another Authority PREPARE is already open",
                )
            try:
                prepare = lifecycle_ledger.append(
                    record_type="ATOMIC_V1_TO_V2_MIGRATION_PREPARE",
                    lifecycle_event_id=prepare_event_id,
                    payload=prepare_payload,
                )
            except IU4LifecycleLedgerError as exc:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "migration PREPARE could not be committed",
                ) from exc
        materialization_record = None
        if completion_record is not None and existing_commit is None:
            if not ledger_records or ledger_records[-1] != completion_record:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "completion authorization is stale or its attempt already began",
                )
            completion_payload = completion_record.payload
            materialization_payload = {
                "operation": "COMPLETE_AUTHORITY_PREPARE",
                "migration_id": migration.migration_id,
                "prepare_record_fingerprint": prepare.record_fingerprint,
                "target_authority_generation_id": generation,
                "completion_authorization_id": completion_payload["authorization_id"],
                "completion_authorization_fingerprint": completion_payload[
                    "authorization_fingerprint"
                ],
                "completion_authorization_record_fingerprint": (
                    completion_record.record_fingerprint
                ),
                "completion_consumption_event_id": (
                    completion_record.lifecycle_event_id
                ),
                "completion_consumption_event_fingerprint": (
                    completion_record.record_fingerprint
                ),
                "completion_startup_attempt_id": completion_payload[
                    "startup_attempt_id"
                ],
                "completion_pre_attempt_ledger_tip": completion_payload[
                    "pre_attempt_ledger_tip"
                ],
                "operator": completion_payload["operator"],
                "timestamp_utc": completion_payload["consumption_timestamp_utc"],
            }
            try:
                materialization_record = lifecycle_ledger.append(
                    record_type="RECOVERY_MATERIALIZATION",
                    lifecycle_event_id=(
                        f"{migration.migration_id}:RECOVERY-MATERIALIZATION:"
                        f"{completion_payload['startup_attempt_id']}"
                    ),
                    payload=materialization_payload,
                )
            except IU4LifecycleLedgerError as exc:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "completion attempt could not be durably claimed",
                ) from exc
            if simulate_interruption_after_completion_claim:
                raise SimulatedAtomicTransactionInterruption(
                    "simulated interruption after completion attempt claim"
                )
        elif completion_record is not None:
            completion_payload = completion_record.payload
            expected_materialization_payload = {
                "operation": "COMPLETE_AUTHORITY_PREPARE",
                "migration_id": migration.migration_id,
                "prepare_record_fingerprint": prepare.record_fingerprint,
                "target_authority_generation_id": generation,
                "completion_authorization_id": completion_payload[
                    "authorization_id"
                ],
                "completion_authorization_fingerprint": completion_payload[
                    "authorization_fingerprint"
                ],
                "completion_authorization_record_fingerprint": (
                    completion_record.record_fingerprint
                ),
                "completion_consumption_event_id": (
                    completion_record.lifecycle_event_id
                ),
                "completion_consumption_event_fingerprint": (
                    completion_record.record_fingerprint
                ),
                "completion_startup_attempt_id": completion_payload[
                    "startup_attempt_id"
                ],
                "completion_pre_attempt_ledger_tip": completion_payload[
                    "pre_attempt_ledger_tip"
                ],
                "operator": completion_payload["operator"],
                "timestamp_utc": completion_payload["consumption_timestamp_utc"],
            }
            materialization_fingerprint = existing_commit.payload.get(
                "completion_materialization_record_fingerprint"
            )
            materialization_event_id = existing_commit.payload.get(
                "completion_materialization_event_id"
            )
            materialization_record = next(
                (
                    record
                    for record in ledger_records
                    if record.record_fingerprint == materialization_fingerprint
                ),
                None,
            )
            if (
                materialization_record is None
                or materialization_record.record_type != "RECOVERY_MATERIALIZATION"
                or materialization_record.lifecycle_event_id
                != materialization_event_id
                or materialization_record.lifecycle_event_id
                != (
                    f"{migration.migration_id}:RECOVERY-MATERIALIZATION:"
                    f"{completion_payload['startup_attempt_id']}"
                )
                or materialization_record.payload
                != expected_materialization_payload
                or materialization_record.previous_record_fingerprint
                != completion_record.record_fingerprint
                or existing_commit.previous_record_fingerprint
                != materialization_record.record_fingerprint
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                    "recovered migration COMMIT lacks its exact completion materialization",
                )
        if simulate_interruption_after_prepare:
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption after migration PREPARE"
            )
        risk = replace(
            target_state_template.risk,
            authority_generation_id=generation,
        )
        target_state = replace(
            target_state_template,
            authority_generation_id=generation,
            authority_prepare_record_fingerprint=prepare.record_fingerprint,
            risk=risk,
        )
        target_path = Path(migration.target_state_path)
        if target_path.exists():
            existing = AtomicPaperStateV2.from_record(
                _canonical_read_json_object(target_path)
            )
            if existing != target_state:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                    "migration target path contains another State",
                )
        else:
            _atomic_write_json(target_path, target_state.to_record())
        if source_path.read_bytes() != source_bytes:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration changed source Atomic V1 bytes",
            )
        if source_loss_path.read_bytes() != source_loss_bytes:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_ROOT_MISMATCH,
                "migration changed source Loss Cluster bytes",
            )
        if AtomicPaperStateV2.from_record(
            _canonical_read_json_object(target_path)
        ) != target_state:
            raise PaperAtomicCoordinatorError(
                AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                "migration target readback mismatch",
            )
        if simulate_interruption_after_target:
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption after migration target publication"
            )
        if simulate_interruption_before_commit:
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption before migration COMMIT"
            )
        if completion_record is None:
            completion_fields = {
                "completion_provenance": "DIRECT",
                "completion_authorization_id": "NONE",
                "completion_authorization_fingerprint": "NONE",
                "completion_authorization_record_fingerprint": "NONE",
                "completion_consumption_event_id": "NONE",
                "completion_consumption_event_fingerprint": "NONE",
                "completion_startup_attempt_id": "NONE",
                "completion_pre_attempt_ledger_tip": "NONE",
                "completion_materialization_event_id": "NONE",
                "completion_materialization_record_fingerprint": "NONE",
            }
        else:
            if materialization_record is None:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                    "recovered migration requires a durable completion materialization",
                )
            completion_payload = completion_record.payload
            completion_fields = {
                "completion_provenance": "RECOVERED_AFTER_PREPARE",
                "completion_authorization_id": completion_payload[
                    "authorization_id"
                ],
                "completion_authorization_fingerprint": completion_payload[
                    "authorization_fingerprint"
                ],
                "completion_authorization_record_fingerprint": (
                    completion_record.record_fingerprint
                ),
                "completion_consumption_event_id": (
                    completion_record.lifecycle_event_id
                ),
                "completion_consumption_event_fingerprint": (
                    completion_record.record_fingerprint
                ),
                "completion_startup_attempt_id": completion_payload[
                    "startup_attempt_id"
                ],
                "completion_pre_attempt_ledger_tip": completion_payload[
                    "pre_attempt_ledger_tip"
                ],
                "completion_materialization_event_id": (
                    materialization_record.lifecycle_event_id
                ),
                "completion_materialization_record_fingerprint": (
                    materialization_record.record_fingerprint
                ),
            }
        commit_payload = {
            "prepare_record_fingerprint": prepare.record_fingerprint,
            "authority_generation_id": generation,
            "new_owner_epoch": prepare_payload["new_owner_epoch"],
            "target_state_fingerprint": target_state.state_fingerprint,
            "target_state_core_fingerprint": prepare_payload["target_state_core_fingerprint"],
            "target_state_path": migration.target_state_path,
            "reconciliation_result": "PASS",
            **completion_fields,
            "operator": migration.operator,
            "timestamp_utc": migration.migration_timestamp_utc,
        }
        if existing_commit is not None:
            if (
                not reconcile_incomplete_migration
                or existing_commit.record_type
                != "ATOMIC_V1_TO_V2_MIGRATION_COMMIT"
                or existing_commit.payload != commit_payload
            ):
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.AUTHORITY_COMMIT_MISMATCH,
                    "existing migration COMMIT does not match explicit reconciliation",
                )
            commit = existing_commit
        else:
            try:
                commit = lifecycle_ledger.append(
                    record_type="ATOMIC_V1_TO_V2_MIGRATION_COMMIT",
                    lifecycle_event_id=commit_event_id,
                    payload=commit_payload,
                )
            except IU4LifecycleLedgerError as exc:
                raise PaperAtomicCoordinatorError(
                    AtomicCoordinatorReasonCode.LIFECYCLE_OPERATION_INCOMPLETE,
                    "migration COMMIT could not be committed",
                ) from exc
        if simulate_interruption_after_commit:
            raise SimulatedAtomicTransactionInterruption(
                "simulated interruption after migration COMMIT"
            )
        return AtomicMigrationResultV1(
            target_state=target_state,
            prepare_record_fingerprint=prepare.record_fingerprint,
            commit_record_fingerprint=commit.record_fingerprint,
        )


__all__ = [
    "ARTIFACT_ATOMIC_TRANSACTION",
    "AtomicCommitResult",
    "AtomicCommitResultV2",
    "AtomicCoordinatorReasonCode",
    "AtomicPaperStateV1",
    "AtomicPaperStateV2",
    "AtomicPaperTransactionV1",
    "AtomicPaperTransactionV2",
    "AtomicEntryDenialProvenanceV1",
    "AtomicEntryVetoCandidateV1",
    "AtomicProgressCursorV1",
    "AtomicReconciliationReport",
    "AtomicRecoveryResult",
    "AtomicRecoveryResultV2",
    "AtomicMigrationResultV1",
    "AtomicV1ToV2MigrationArtifactV1",
    "PaperAtomicCoordinator",
    "PaperAtomicCoordinatorV2",
    "PaperAtomicCoordinatorError",
    "PaperRiskStateS4V1",
    "S4KillTransitionV1",
    "SimulatedAtomicTransactionInterruption",
    "TRANSACTION_CLOSE",
    "TRANSACTION_ENTRY_VETO",
    "TRANSACTION_KILL",
    "TRANSACTION_OPEN",
    "TRANSACTION_PROGRESS",
]
