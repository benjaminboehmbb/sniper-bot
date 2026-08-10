#!/usr/bin/env python3
"""Inactive, fail-closed adapter from fused L1 intent to atomic Paper state.

The adapter is the only planned IU-4 bridge between BUY/SELL/HOLD intent and
Decimal Paper Execution Economics.  It never calls exchange or live-order
code, never writes a second economic state, and is deliberately not imported
by the active L1 loop.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

from live_l1.core.paper_economics import (
    EntryAuthorization,
    PaperEconomicsError,
    authorize_entry,
    settle_trade,
)
from live_l1.core.paper_entry_throttle import (
    AcceptedEntryEventV1,
    canonical_utc_timestamp,
)
from live_l1.state.paper_artifacts import (
    PositionStateS2FlatV2,
    PositionStateS2V2,
    TradeRecordV2,
    canonical_decimal,
)
from live_l1.state.paper_atomic_coordinator import (
    AtomicCommitResult,
    AtomicCoordinatorReasonCode,
    AtomicPaperStateV1,
    AtomicPaperTransactionV1,
    PaperAtomicCoordinator,
    PaperAtomicCoordinatorError,
    TRANSACTION_CLOSE,
    TRANSACTION_OPEN,
)


ACTION_NOOP = "NOOP"
ACTION_OPEN_LONG = "OPEN_LONG"
ACTION_OPEN_SHORT = "OPEN_SHORT"
ACTION_CLOSE_LONG = "CLOSE_LONG"
ACTION_CLOSE_SHORT = "CLOSE_SHORT"

STATUS_COMMITTED = "COMMITTED"
STATUS_NOOP = "NOOP"
STATUS_REJECTED = "REJECTED"


class IU4AdapterReasonCode:
    COMMITTED = "PEE_IU4_COMMITTED"
    ALREADY_COMMITTED = "PEE_IU4_ALREADY_COMMITTED"
    HOLD = "PEE_IU4_HOLD"
    ALREADY_POSITIONED = "PEE_IU4_ALREADY_POSITIONED"
    REQUEST_INVALID = "PEE_IU4_REQUEST_INVALID"
    STATE_MISMATCH = "PEE_IU4_STATE_MISMATCH"
    ENTRY_BLOCKED = "PEE_IU4_ENTRY_BLOCKED"
    TRANSACTION_CONFLICT = "PEE_IU4_TRANSACTION_CONFLICT"


class PaperIU4AdapterError(RuntimeError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


def _text(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise PaperIU4AdapterError(
            IU4AdapterReasonCode.REQUEST_INVALID,
            f"{field_name} must be a string",
        )
    result = value.strip()
    if not allow_empty and not result:
        raise PaperIU4AdapterError(
            IU4AdapterReasonCode.REQUEST_INVALID,
            f"{field_name} must not be empty",
        )
    return result


def _integer(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PaperIU4AdapterError(
            IU4AdapterReasonCode.REQUEST_INVALID,
            f"{field_name} must be a non-negative integer",
        )
    return value


def _positive_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise PaperIU4AdapterError(
            IU4AdapterReasonCode.REQUEST_INVALID,
            f"{field_name} must be Decimal, int, or a decimal string",
        )
    try:
        result = value if isinstance(value, Decimal) else Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise PaperIU4AdapterError(
            IU4AdapterReasonCode.REQUEST_INVALID,
            f"{field_name} is not a valid decimal",
        ) from exc
    if not result.is_finite() or result <= 0:
        raise PaperIU4AdapterError(
            IU4AdapterReasonCode.REQUEST_INVALID,
            f"{field_name} must be finite and greater than zero",
        )
    return result


def _sha256(value: object, field_name: str) -> str:
    result = _text(value, field_name).lower()
    if len(result) != 64 or any(character not in "0123456789abcdef" for character in result):
        raise PaperIU4AdapterError(
            IU4AdapterReasonCode.REQUEST_INVALID,
            f"{field_name} must be a lowercase SHA-256 digest",
        )
    return result


@dataclass(frozen=True)
class IU4AdapterRequestV1:
    schema_version: int
    request_id: str
    source_intent_id: str
    intent_final: str
    intent_reason_code: str
    expected_state_fingerprint: str
    target_system_state_id: str
    timestamp_utc: str
    tick_id: int
    reference_price: Decimal
    reference_stop_price: Decimal | None
    trade_id: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 1
        ):
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "IU4AdapterRequestV1 requires schema_version 1",
            )
        for name in ("source_intent_id", "intent_reason_code", "target_system_state_id"):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        intent = _text(self.intent_final, "intent_final").upper()
        if intent not in ("BUY", "SELL", "HOLD"):
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "intent_final must be BUY, SELL, or HOLD",
            )
        object.__setattr__(self, "intent_final", intent)
        object.__setattr__(
            self,
            "expected_state_fingerprint",
            _sha256(self.expected_state_fingerprint, "expected_state_fingerprint"),
        )
        try:
            timestamp = canonical_utc_timestamp(self.timestamp_utc, "timestamp_utc")
        except Exception as exc:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "timestamp_utc must be canonical UTC whole seconds",
            ) from exc
        object.__setattr__(self, "timestamp_utc", timestamp)
        object.__setattr__(self, "tick_id", _integer(self.tick_id, "tick_id"))
        object.__setattr__(
            self,
            "reference_price",
            _positive_decimal(self.reference_price, "reference_price"),
        )
        if self.reference_stop_price is not None:
            object.__setattr__(
                self,
                "reference_stop_price",
                _positive_decimal(self.reference_stop_price, "reference_stop_price"),
            )
        object.__setattr__(self, "trade_id", _text(self.trade_id, "trade_id", allow_empty=True))

        fingerprint = self.request_fingerprint
        expected_request_id = f"PEE-IU4-{fingerprint}"
        request_id = _text(self.request_id, "request_id", allow_empty=True)
        if request_id and request_id != expected_request_id:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "request_id does not match the canonical request fingerprint",
            )
        object.__setattr__(self, "request_id", expected_request_id)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_intent_id": self.source_intent_id,
            "intent_final": self.intent_final,
            "intent_reason_code": self.intent_reason_code,
            "expected_state_fingerprint": self.expected_state_fingerprint,
            "target_system_state_id": self.target_system_state_id,
            "timestamp_utc": self.timestamp_utc,
            "tick_id": self.tick_id,
            "reference_price": canonical_decimal(self.reference_price),
            "reference_stop_price": (
                None
                if self.reference_stop_price is None
                else canonical_decimal(self.reference_stop_price)
            ),
            "trade_id": self.trade_id,
        }

    @property
    def request_fingerprint(self) -> str:
        encoded = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_record(self) -> dict[str, Any]:
        return {"request_id": self.request_id, **self.canonical_payload()}

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "IU4AdapterRequestV1":
        expected_fields = set(cls.__dataclass_fields__)
        if set(record) != expected_fields:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "IU4 adapter request fields are missing or unknown",
            )
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})


@dataclass(frozen=True)
class IU4AdapterResultV1:
    schema_version: int
    status: str
    action: str
    reason_code: str
    request_id: str
    source_intent_id: str
    state: AtomicPaperStateV1
    transaction_event_id: str
    newly_committed: bool
    already_committed: bool
    recovered_incomplete_commit: bool


class PaperIU4Adapter:
    """Deterministic single-position adapter over PaperAtomicCoordinator."""

    def __init__(self, coordinator: PaperAtomicCoordinator) -> None:
        if not isinstance(coordinator, PaperAtomicCoordinator):
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "PaperIU4Adapter requires PaperAtomicCoordinator",
            )
        self.coordinator = coordinator

    @staticmethod
    def _action(position: str, intent: str) -> str:
        if position == "FLAT" and intent == "BUY":
            return ACTION_OPEN_LONG
        if position == "FLAT" and intent == "SELL":
            return ACTION_OPEN_SHORT
        if position == "LONG" and intent == "SELL":
            return ACTION_CLOSE_LONG
        if position == "SHORT" and intent == "BUY":
            return ACTION_CLOSE_SHORT
        return ACTION_NOOP

    @staticmethod
    def _result(
        request: IU4AdapterRequestV1,
        state: AtomicPaperStateV1,
        *,
        status: str,
        action: str,
        reason_code: str,
        commit: AtomicCommitResult | None = None,
    ) -> IU4AdapterResultV1:
        return IU4AdapterResultV1(
            schema_version=1,
            status=status,
            action=action,
            reason_code=reason_code,
            request_id=request.request_id,
            source_intent_id=request.source_intent_id,
            state=state if commit is None else commit.state,
            transaction_event_id="" if commit is None else request.request_id,
            newly_committed=False if commit is None else commit.newly_committed,
            already_committed=False if commit is None else commit.already_committed,
            recovered_incomplete_commit=(
                False if commit is None else commit.recovered_incomplete_commit
            ),
        )

    @staticmethod
    def _validate_trade_binding(
        request: IU4AdapterRequestV1,
        state: AtomicPaperStateV1,
        action: str,
    ) -> None:
        if action in (ACTION_OPEN_LONG, ACTION_OPEN_SHORT):
            if not request.trade_id or request.reference_stop_price is None:
                raise PaperIU4AdapterError(
                    IU4AdapterReasonCode.REQUEST_INVALID,
                    "OPEN requires trade_id and reference_stop_price",
                )
            return
        if request.reference_stop_price is not None:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "non-OPEN request must not contain reference_stop_price",
            )
        expected_trade_id = (
            "" if isinstance(state.position, PositionStateS2FlatV2) else state.position.trade_id
        )
        if request.trade_id != expected_trade_id:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.STATE_MISMATCH,
                "request trade_id does not match the current position",
            )
        if action == ACTION_NOOP and (
            request.target_system_state_id != state.position.system_state_id
        ):
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.STATE_MISMATCH,
                "NOOP cannot silently change system_state_id",
            )

    def _entry_authorization(
        self,
        request: IU4AdapterRequestV1,
        state: AtomicPaperStateV1,
        side: str,
    ) -> EntryAuthorization:
        assert request.reference_stop_price is not None
        return authorize_entry(
            side=side,  # type: ignore[arg-type]
            realized_equity_quote=state.account.realized_equity_quote,
            reference_entry_price=request.reference_price,
            reference_stop_price=request.reference_stop_price,
            config=self.coordinator.config,
        )

    def _commit_open(
        self,
        request: IU4AdapterRequestV1,
        state: AtomicPaperStateV1,
        action: str,
    ) -> IU4AdapterResultV1:
        entry_block_reasons = self.coordinator.evaluate_entry_block_reasons(
            entry_timestamp_utc=request.timestamp_utc,
        )
        if entry_block_reasons:
            return self._result(
                request,
                state,
                status=STATUS_REJECTED,
                action=action,
                reason_code=entry_block_reasons[0],
            )
        side = "LONG" if action == ACTION_OPEN_LONG else "SHORT"
        authorization = self._entry_authorization(request, state, side)
        if not authorization.allowed or authorization.quote is None:
            return self._result(
                request,
                state,
                status=STATUS_REJECTED,
                action=action,
                reason_code=authorization.reason_code,
            )
        quote = authorization.quote
        position = PositionStateS2V2(
            schema_version=2,
            system_state_id=request.target_system_state_id,
            symbol=state.position.symbol,
            position=side,
            side=side,
            trade_id=request.trade_id,
            reference_entry_price=quote.reference_entry_price,
            modeled_entry_fill_price=quote.modeled_entry_fill_price,
            quantity=quote.quantity,
            entry_notional_quote=quote.entry_notional_quote,
            entry_fee_quote=quote.entry_fee_quote,
            risk_budget_quote=quote.risk_budget_quote,
            modeled_stop_loss_quote=quote.modeled_stop_loss_quote,
            reference_stop_price=quote.reference_stop_price,
            entry_timestamp_utc=request.timestamp_utc,
            entry_tick_id=request.tick_id,
            economics_profile_id=quote.economics_profile_id,
            economics_model_version=quote.economics_model_version,
            config_fingerprint=quote.config_fingerprint,
        )
        event = AcceptedEntryEventV1(
            schema_version=1,
            entry_sequence=state.throttle.total_accepted_entry_count + 1,
            entry_event_id=request.request_id,
            previous_entry_event_id=state.throttle.last_entry_event_id,
            entry_timestamp_utc=request.timestamp_utc,
            policy_model_version=state.throttle.policy_model_version,
            policy_profile_id=state.throttle.policy_profile_id,
            policy_fingerprint=state.throttle.policy_fingerprint,
        )
        try:
            commit = self.coordinator.commit_open(
                position_after=position,
                accepted_entry_event=event,
                transition_tick_id=request.tick_id,
            )
        except PaperAtomicCoordinatorError as exc:
            if exc.reason_code == AtomicCoordinatorReasonCode.ENTRY_BLOCKED:
                return self._result(
                    request,
                    state,
                    status=STATUS_REJECTED,
                    action=action,
                    reason_code=IU4AdapterReasonCode.ENTRY_BLOCKED,
                )
            raise
        return self._result(
            request,
            commit.state,
            status=STATUS_COMMITTED,
            action=action,
            reason_code=(
                IU4AdapterReasonCode.ALREADY_COMMITTED
                if commit.already_committed
                else IU4AdapterReasonCode.COMMITTED
            ),
            commit=commit,
        )

    def _commit_close(
        self,
        request: IU4AdapterRequestV1,
        state: AtomicPaperStateV1,
        action: str,
    ) -> IU4AdapterResultV1:
        if not isinstance(state.position, PositionStateS2V2):
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.STATE_MISMATCH,
                "CLOSE requires an OPEN S2 V2 position",
            )
        authorization = authorize_entry(
            side=state.position.side,  # type: ignore[arg-type]
            realized_equity_quote=state.account.realized_equity_quote,
            reference_entry_price=state.position.reference_entry_price,
            reference_stop_price=state.position.reference_stop_price,
            config=self.coordinator.config,
        )
        if not authorization.allowed or authorization.quote is None:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.TRANSACTION_CONFLICT,
                "persisted OPEN economics cannot be reconstructed",
            )
        try:
            settlement = settle_trade(
                entry_quote=authorization.quote,
                reference_exit_price=request.reference_price,
                equity_before_quote=state.account.realized_equity_quote,
                peak_realized_equity_before_quote=state.account.peak_realized_equity_quote,
                config=self.coordinator.config,
            )
        except PaperEconomicsError as exc:
            raise PaperIU4AdapterError(exc.reason_code, exc.detail) from exc
        trade = TradeRecordV2.from_economics(
            trade_id=state.position.trade_id,
            settlement_sequence=state.account.closed_trade_count + 1,
            previous_settled_trade_id=state.account.last_settled_trade_id,
            settlement_event_id=request.request_id,
            settlement_utc_day=request.timestamp_utc[:10],
            system_state_id=request.target_system_state_id,
            symbol=state.position.symbol,
            quote_currency=state.account.quote_currency,
            entry_timestamp_utc=state.position.entry_timestamp_utc,
            exit_timestamp_utc=request.timestamp_utc,
            entry_tick_id=state.position.entry_tick_id,
            exit_tick_id=request.tick_id,
            exit_reason=request.intent_reason_code,
            entry_quote=authorization.quote,
            settlement=settlement,
        )
        flat = PositionStateS2FlatV2(
            schema_version=2,
            system_state_id=request.target_system_state_id,
            symbol=state.position.symbol,
            position="FLAT",
            side="",
            last_closed_trade_id=state.position.trade_id,
            economics_profile_id=state.position.economics_profile_id,
            economics_model_version=state.position.economics_model_version,
            config_fingerprint=state.position.config_fingerprint,
        )
        commit = self.coordinator.commit_close(position_after=flat, trade=trade)
        return self._result(
            request,
            commit.state,
            status=STATUS_COMMITTED,
            action=action,
            reason_code=(
                IU4AdapterReasonCode.ALREADY_COMMITTED
                if commit.already_committed
                else IU4AdapterReasonCode.COMMITTED
            ),
            commit=commit,
        )

    def _replay_existing(
        self,
        request: IU4AdapterRequestV1,
        transaction: AtomicPaperTransactionV1,
    ) -> IU4AdapterResultV1:
        before = transaction.state_before
        if request.expected_state_fingerprint != before.state_fingerprint:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.TRANSACTION_CONFLICT,
                "existing transaction does not match expected state",
            )
        action = self._action(before.position.position, request.intent_final)
        if transaction.transaction_type == TRANSACTION_OPEN:
            position = transaction.state_after.position
            event = transaction.accepted_entry_event
            if (
                action not in (ACTION_OPEN_LONG, ACTION_OPEN_SHORT)
                or not isinstance(position, PositionStateS2V2)
                or event is None
                or position.trade_id != request.trade_id
                or position.system_state_id != request.target_system_state_id
                or position.reference_entry_price != request.reference_price
                or position.reference_stop_price != request.reference_stop_price
                or transaction.transaction_timestamp_utc != request.timestamp_utc
                or transaction.transaction_tick_id != request.tick_id
            ):
                raise PaperIU4AdapterError(
                    IU4AdapterReasonCode.TRANSACTION_CONFLICT,
                    "existing OPEN does not match the IU-4 request",
                )
            commit = self.coordinator.commit_open(
                position_after=position,
                accepted_entry_event=event,
                transition_tick_id=transaction.transaction_tick_id,
            )
        elif transaction.transaction_type == TRANSACTION_CLOSE:
            trade = transaction.trade
            position = transaction.state_after.position
            if (
                action not in (ACTION_CLOSE_LONG, ACTION_CLOSE_SHORT)
                or trade is None
                or not isinstance(position, PositionStateS2FlatV2)
                or trade.trade_id != request.trade_id
                or trade.system_state_id != request.target_system_state_id
                or trade.reference_exit_price != request.reference_price
                or trade.exit_reason != request.intent_reason_code
                or transaction.transaction_timestamp_utc != request.timestamp_utc
                or transaction.transaction_tick_id != request.tick_id
            ):
                raise PaperIU4AdapterError(
                    IU4AdapterReasonCode.TRANSACTION_CONFLICT,
                    "existing CLOSE does not match the IU-4 request",
                )
            commit = self.coordinator.commit_close(position_after=position, trade=trade)
        else:
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.TRANSACTION_CONFLICT,
                "IU-4 request ID is already owned by a non-execution transaction",
            )
        return self._result(
            request,
            commit.state,
            status=STATUS_COMMITTED,
            action=action,
            reason_code=IU4AdapterReasonCode.ALREADY_COMMITTED,
            commit=commit,
        )

    def execute(self, request: IU4AdapterRequestV1) -> IU4AdapterResultV1:
        if not isinstance(request, IU4AdapterRequestV1):
            raise PaperIU4AdapterError(
                IU4AdapterReasonCode.REQUEST_INVALID,
                "execute requires IU4AdapterRequestV1",
            )
        existing = self.coordinator.transaction_by_event_id(request.request_id)
        if existing is not None:
            return self._replay_existing(request, existing)

        state = self.coordinator.load_state()
        if request.expected_state_fingerprint != state.state_fingerprint:
            return self._result(
                request,
                state,
                status=STATUS_REJECTED,
                action=ACTION_NOOP,
                reason_code=IU4AdapterReasonCode.STATE_MISMATCH,
            )
        action = self._action(state.position.position, request.intent_final)
        self._validate_trade_binding(request, state, action)
        if action == ACTION_NOOP:
            reason = (
                IU4AdapterReasonCode.HOLD
                if request.intent_final == "HOLD"
                else IU4AdapterReasonCode.ALREADY_POSITIONED
            )
            return self._result(
                request,
                state,
                status=STATUS_NOOP,
                action=action,
                reason_code=reason,
            )
        if action in (ACTION_OPEN_LONG, ACTION_OPEN_SHORT):
            return self._commit_open(request, state, action)
        return self._commit_close(request, state, action)


__all__ = [
    "ACTION_CLOSE_LONG",
    "ACTION_CLOSE_SHORT",
    "ACTION_NOOP",
    "ACTION_OPEN_LONG",
    "ACTION_OPEN_SHORT",
    "IU4AdapterReasonCode",
    "IU4AdapterRequestV1",
    "IU4AdapterResultV1",
    "PaperIU4Adapter",
    "PaperIU4AdapterError",
    "STATUS_COMMITTED",
    "STATUS_NOOP",
    "STATUS_REJECTED",
]
