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
from dataclasses import dataclass
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
    PaperAccountState,
    PaperArtifactError,
    PositionArtifactV2,
    PositionStateS2FlatV2,
    PositionStateS2V2,
    TradeRecordV2,
    apply_trade_to_account,
    canonical_json_sha256,
    evaluate_account_entry_guard,
    parse_position_artifact,
)


ARTIFACT_ATOMIC_TRANSACTION = "paper_atomic_transaction"
TRANSACTION_OPEN = "OPEN"
TRANSACTION_CLOSE = "CLOSE"
TRANSACTION_KILL = "KILL"
KILL_LEVELS = frozenset({"NONE", "SOFT", "HARD", "EMERGENCY"})
POSITION_OPEN_REASON = "PEE_S4_POSITION_OPEN"


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


class PaperAtomicCoordinatorError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


class SimulatedAtomicTransactionInterruption(RuntimeError):
    """Test-only interruption after a durable coordinator journal write."""


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
        account_decision = evaluate_account_entry_guard(account, self.config)
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


__all__ = [
    "ARTIFACT_ATOMIC_TRANSACTION",
    "AtomicCommitResult",
    "AtomicCoordinatorReasonCode",
    "AtomicPaperStateV1",
    "AtomicPaperTransactionV1",
    "AtomicReconciliationReport",
    "AtomicRecoveryResult",
    "PaperAtomicCoordinator",
    "PaperAtomicCoordinatorError",
    "PaperRiskStateS4V1",
    "S4KillTransitionV1",
    "SimulatedAtomicTransactionInterruption",
    "TRANSACTION_CLOSE",
    "TRANSACTION_KILL",
    "TRANSACTION_OPEN",
]
