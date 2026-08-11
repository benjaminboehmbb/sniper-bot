#!/usr/bin/env python3
"""Versioned, strict data contracts for Paper Execution Economics.

The active L1 runtime does not import this module yet.  IU-2 keeps schema
evolution isolated so legacy S2 and trade records remain readable without
silently receiving V2 semantics.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Context, Decimal, InvalidOperation, ROUND_HALF_EVEN
from typing import Any, Mapping, Union

from live_l1.core.paper_economics import (
    EntryEconomicsQuote,
    PaperEconomicsConfig,
    TradeSettlement,
)


ZERO = Decimal("0")
ONE = Decimal("1")
DECIMAL_CONTEXT = Context(
    prec=50,
    rounding=ROUND_HALF_EVEN,
    Emin=-999999,
    Emax=999999,
)

ARTIFACT_S2_POSITION = "s2_position"
ARTIFACT_PAPER_ACCOUNT = "paper_account"
ARTIFACT_TRADE = "paper_trade"
ARTIFACT_SETTLEMENT = "paper_settlement"

SUPPORTED_ARTIFACT_SCHEMA_VERSIONS: Mapping[str, frozenset[int]] = {
    ARTIFACT_S2_POSITION: frozenset({0, 1, 2}),
    ARTIFACT_PAPER_ACCOUNT: frozenset({1}),
    ARTIFACT_TRADE: frozenset({0, 1, 2}),
    ARTIFACT_SETTLEMENT: frozenset({1}),
}


class ArtifactReasonCode:
    SCHEMA_MALFORMED = "PEE_SCHEMA_MALFORMED"
    SCHEMA_UNSUPPORTED = "PEE_SCHEMA_UNSUPPORTED"
    ARTIFACT_INVALID = "PEE_SCHEMA_ARTIFACT_INVALID"
    LEGACY_ECONOMICS_INCOMPLETE = "PEE_SCHEMA_LEGACY_ECONOMICS_INCOMPLETE"
    CONFIG_MISMATCH = "PEE_RECONCILIATION_CONFIG_MISMATCH"
    ACCOUNT_MISMATCH = "PEE_RECONCILIATION_ACCOUNT_MISMATCH"
    SEQUENCE_MISMATCH = "PEE_RECONCILIATION_SEQUENCE_MISMATCH"


class AccountGuardReasonCode:
    EQUITY_NON_POSITIVE = "PEE_ACCOUNT_EQUITY_NON_POSITIVE"
    ACCOUNT_DAY_REGRESSION = "PEE_ACCOUNT_DAY_REGRESSION"
    DAILY_LOSS_LIMIT = "PEE_RISK_DAILY_LOSS_LIMIT"
    REALIZED_DRAWDOWN_LIMIT = "PEE_RISK_REALIZED_DRAWDOWN_LIMIT"
    DAILY_FEE_LIMIT = "PEE_COST_DAILY_FEE_LIMIT"


class PaperArtifactError(ValueError):
    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


def _text(value: object, field_name: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be a string",
        )
    result = value.strip()
    if not allow_empty and not result:
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must not be empty",
        )
    return result


def _integer(value: object, field_name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be an integer >= {minimum}",
        )
    return value


def _decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be Decimal, int, or a decimal string",
        )
    if isinstance(value, Decimal):
        result = value
    elif isinstance(value, int):
        result = Decimal(value)
    elif isinstance(value, str):
        try:
            result = Decimal(value.strip())
        except (InvalidOperation, ValueError) as exc:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                f"{field_name} is not a valid decimal",
            ) from exc
    else:
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be Decimal, int, or a decimal string",
        )
    if not result.is_finite():
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be finite",
        )
    return ZERO if result == ZERO else result


def _positive_decimal(value: object, field_name: str) -> Decimal:
    result = _decimal(value, field_name)
    if result <= ZERO:
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be greater than zero",
        )
    return result


def _non_negative_decimal(value: object, field_name: str) -> Decimal:
    result = _decimal(value, field_name)
    if result < ZERO:
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must not be negative",
        )
    return result


def _dadd(left: Decimal, right: Decimal) -> Decimal:
    return DECIMAL_CONTEXT.add(left, right)


def _dsub(left: Decimal, right: Decimal) -> Decimal:
    return DECIMAL_CONTEXT.subtract(left, right)


def _dmul(left: Decimal, right: Decimal) -> Decimal:
    return DECIMAL_CONTEXT.multiply(left, right)


def _utc_timestamp_seconds(value: object, field_name: str) -> str:
    text = _text(value, field_name)
    try:
        parsed = datetime.fromisoformat(
            text[:-1] + "+00:00" if text.endswith("Z") else text
        )
    except ValueError as exc:
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be an ISO-8601 timestamp",
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.microsecond:
        raise PaperArtifactError(
            ArtifactReasonCode.ARTIFACT_INVALID,
            f"{field_name} must be timezone-aware with whole-second resolution",
        )
    return parsed.astimezone(timezone.utc).isoformat(timespec="seconds").replace(
        "+00:00",
        "Z",
    )


def _ddiv(left: Decimal, right: Decimal) -> Decimal:
    return DECIMAL_CONTEXT.divide(left, right)


def canonical_decimal(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    result = format(value, "f")
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    return result


def canonical_json_sha256(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def artifact_schema_version(
    record: Mapping[str, Any],
    artifact_type: str,
) -> int:
    if artifact_type not in SUPPORTED_ARTIFACT_SCHEMA_VERSIONS:
        raise PaperArtifactError(
            ArtifactReasonCode.SCHEMA_UNSUPPORTED,
            f"unknown artifact type {artifact_type!r}",
        )
    if "schema_version" not in record:
        version = 0
    else:
        raw = record.get("schema_version")
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise PaperArtifactError(
                ArtifactReasonCode.SCHEMA_MALFORMED,
                f"{artifact_type} schema_version must be an integer",
            )
        version = raw
    if version not in SUPPORTED_ARTIFACT_SCHEMA_VERSIONS[artifact_type]:
        raise PaperArtifactError(
            ArtifactReasonCode.SCHEMA_UNSUPPORTED,
            f"unsupported {artifact_type} schema_version {version}",
        )
    return version


@dataclass(frozen=True)
class LegacyArtifact:
    artifact_type: str
    schema_version: int
    raw_record: Mapping[str, Any]
    economics_complete: bool = False
    entry_allowed: bool = False
    exit_allowed: bool = True
    reason_code: str = ArtifactReasonCode.LEGACY_ECONOMICS_INCOMPLETE


@dataclass(frozen=True)
class PositionStateS2V2:
    schema_version: int
    system_state_id: str
    symbol: str
    position: str
    side: str
    trade_id: str
    reference_entry_price: Decimal
    modeled_entry_fill_price: Decimal
    quantity: Decimal
    entry_notional_quote: Decimal
    entry_fee_quote: Decimal
    risk_budget_quote: Decimal
    modeled_stop_loss_quote: Decimal
    reference_stop_price: Decimal
    entry_timestamp_utc: str
    entry_tick_id: int
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 2
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.SCHEMA_UNSUPPORTED,
                "PositionStateS2V2 requires schema_version 2",
            )
        position = _text(self.position, "position").upper()
        if position not in ("LONG", "SHORT"):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "S2 V2 economics position must be LONG or SHORT",
            )
        side = _text(self.side, "side").upper()
        if side != position:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "side must equal position",
            )
        object.__setattr__(self, "position", position)
        object.__setattr__(self, "side", side)

        for name in (
            "system_state_id",
            "symbol",
            "trade_id",
            "economics_profile_id",
            "economics_model_version",
            "config_fingerprint",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(
            self,
            "entry_timestamp_utc",
            _utc_timestamp_seconds(self.entry_timestamp_utc, "entry_timestamp_utc"),
        )
        object.__setattr__(self, "entry_tick_id", _integer(self.entry_tick_id, "entry_tick_id"))
        for name in (
            "reference_entry_price",
            "modeled_entry_fill_price",
            "quantity",
            "entry_notional_quote",
            "reference_stop_price",
        ):
            object.__setattr__(self, name, _positive_decimal(getattr(self, name), name))
        for name in ("entry_fee_quote", "risk_budget_quote", "modeled_stop_loss_quote"):
            object.__setattr__(
                self,
                name,
                _non_negative_decimal(getattr(self, name), name),
            )

        valid_stop = (
            position == "LONG" and self.reference_stop_price < self.reference_entry_price
        ) or (
            position == "SHORT" and self.reference_stop_price > self.reference_entry_price
        )
        if not valid_stop:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "reference stop direction is invalid for the position",
            )
        valid_entry_fill = (
            position == "LONG"
            and self.modeled_entry_fill_price >= self.reference_entry_price
        ) or (
            position == "SHORT"
            and self.modeled_entry_fill_price <= self.reference_entry_price
        )
        if not valid_entry_fill:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "modeled entry fill is favorable relative to the reference price",
            )
        if self.entry_notional_quote != _dmul(
            self.quantity,
            self.modeled_entry_fill_price,
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "entry notional identity is invalid",
            )
        if self.modeled_stop_loss_quote > self.risk_budget_quote:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "modeled stop loss exceeds the risk budget",
            )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "system_state_id": self.system_state_id,
            "symbol": self.symbol,
            "position": self.position,
            "side": self.side,
            "trade_id": self.trade_id,
            "reference_entry_price": canonical_decimal(self.reference_entry_price),
            "modeled_entry_fill_price": canonical_decimal(self.modeled_entry_fill_price),
            "quantity": canonical_decimal(self.quantity),
            "entry_notional_quote": canonical_decimal(self.entry_notional_quote),
            "entry_fee_quote": canonical_decimal(self.entry_fee_quote),
            "risk_budget_quote": canonical_decimal(self.risk_budget_quote),
            "modeled_stop_loss_quote": canonical_decimal(self.modeled_stop_loss_quote),
            "reference_stop_price": canonical_decimal(self.reference_stop_price),
            "entry_timestamp_utc": self.entry_timestamp_utc,
            "entry_tick_id": self.entry_tick_id,
            "economics_profile_id": self.economics_profile_id,
            "economics_model_version": self.economics_model_version,
            "config_fingerprint": self.config_fingerprint,
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PositionStateS2V2":
        artifact_schema_version(record, ARTIFACT_S2_POSITION)
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})

    @property
    def state_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class PositionStateS2FlatV2:
    schema_version: int
    system_state_id: str
    symbol: str
    position: str
    side: str
    last_closed_trade_id: str
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.schema_version, bool)
            or not isinstance(self.schema_version, int)
            or self.schema_version != 2
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.SCHEMA_UNSUPPORTED,
                "PositionStateS2FlatV2 requires schema_version 2",
            )
        position = _text(self.position, "position").upper()
        if position != "FLAT":
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "S2 V2 flat position must be FLAT",
            )
        side = _text(self.side, "side", allow_empty=True).upper()
        if side != "":
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "S2 V2 flat position must have an empty side",
            )
        object.__setattr__(self, "position", position)
        object.__setattr__(self, "side", side)
        for name in (
            "system_state_id",
            "symbol",
            "economics_profile_id",
            "economics_model_version",
            "config_fingerprint",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(
            self,
            "last_closed_trade_id",
            _text(
                self.last_closed_trade_id,
                "last_closed_trade_id",
                allow_empty=True,
            ),
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema_version": 2,
            "system_state_id": self.system_state_id,
            "symbol": self.symbol,
            "position": self.position,
            "side": self.side,
            "last_closed_trade_id": self.last_closed_trade_id,
            "economics_profile_id": self.economics_profile_id,
            "economics_model_version": self.economics_model_version,
            "config_fingerprint": self.config_fingerprint,
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PositionStateS2FlatV2":
        artifact_schema_version(record, ARTIFACT_S2_POSITION)
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})

    @property
    def state_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class TradeRecordV2:
    schema_version: int
    trade_id: str
    settlement_sequence: int
    previous_settled_trade_id: str
    settlement_event_id: str
    settlement_utc_day: str
    system_state_id: str
    symbol: str
    quote_currency: str
    side: str
    quantity: Decimal
    reference_entry_price: Decimal
    reference_exit_price: Decimal
    modeled_entry_fill_price: Decimal
    modeled_exit_fill_price: Decimal
    entry_notional_quote: Decimal
    exit_notional_quote: Decimal
    entry_fee_quote: Decimal
    exit_fee_quote: Decimal
    total_fees_quote: Decimal
    reference_pnl_quote: Decimal
    execution_gross_pnl_quote: Decimal
    slippage_cost_quote: Decimal
    net_pnl_quote: Decimal
    net_return_on_entry_notional: Decimal
    net_return_on_equity_before: Decimal
    equity_before_quote: Decimal
    equity_after_quote: Decimal
    peak_realized_equity_after_quote: Decimal
    realized_drawdown_quote: Decimal
    realized_drawdown_rate: Decimal
    risk_budget_quote: Decimal
    modeled_stop_loss_quote: Decimal
    entry_timestamp_utc: str
    exit_timestamp_utc: str
    entry_tick_id: int
    exit_tick_id: int
    exit_reason: str
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str
    economics_complete: bool

    def __post_init__(self) -> None:
        if self.schema_version != 2:
            raise PaperArtifactError(
                ArtifactReasonCode.SCHEMA_UNSUPPORTED,
                "TradeRecordV2 requires schema_version 2",
            )
        for name in (
            "trade_id",
            "settlement_event_id",
            "settlement_utc_day",
            "system_state_id",
            "symbol",
            "quote_currency",
            "entry_timestamp_utc",
            "exit_timestamp_utc",
            "exit_reason",
            "economics_profile_id",
            "economics_model_version",
            "config_fingerprint",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        object.__setattr__(
            self,
            "previous_settled_trade_id",
            _text(self.previous_settled_trade_id, "previous_settled_trade_id", allow_empty=True),
        )
        if len(self.settlement_utc_day) != 10:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "settlement_utc_day must use YYYY-MM-DD",
            )
        side = _text(self.side, "side").upper()
        if side not in ("LONG", "SHORT"):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "trade side must be LONG or SHORT",
            )
        object.__setattr__(self, "side", side)
        object.__setattr__(
            self,
            "settlement_sequence",
            _integer(self.settlement_sequence, "settlement_sequence", minimum=1),
        )
        object.__setattr__(self, "entry_tick_id", _integer(self.entry_tick_id, "entry_tick_id"))
        object.__setattr__(self, "exit_tick_id", _integer(self.exit_tick_id, "exit_tick_id"))
        if self.exit_tick_id < self.entry_tick_id:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "exit_tick_id must not precede entry_tick_id",
            )
        if self.economics_complete is not True:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "TradeRecordV2 requires economics_complete=true",
            )

        positive_fields = (
            "quantity",
            "reference_entry_price",
            "reference_exit_price",
            "modeled_entry_fill_price",
            "modeled_exit_fill_price",
            "entry_notional_quote",
            "exit_notional_quote",
            "equity_before_quote",
            "peak_realized_equity_after_quote",
        )
        for name in positive_fields:
            object.__setattr__(self, name, _positive_decimal(getattr(self, name), name))
        non_negative_fields = (
            "entry_fee_quote",
            "exit_fee_quote",
            "total_fees_quote",
            "slippage_cost_quote",
            "realized_drawdown_quote",
            "realized_drawdown_rate",
            "risk_budget_quote",
            "modeled_stop_loss_quote",
        )
        for name in non_negative_fields:
            object.__setattr__(
                self,
                name,
                _non_negative_decimal(getattr(self, name), name),
            )
        signed_fields = (
            "reference_pnl_quote",
            "execution_gross_pnl_quote",
            "net_pnl_quote",
            "net_return_on_entry_notional",
            "net_return_on_equity_before",
            "equity_after_quote",
        )
        for name in signed_fields:
            object.__setattr__(self, name, _decimal(getattr(self, name), name))

        if self.total_fees_quote != _dadd(self.entry_fee_quote, self.exit_fee_quote):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "total fees do not equal entry plus exit fees",
            )
        if self.net_pnl_quote != _dsub(
            self.execution_gross_pnl_quote,
            self.total_fees_quote,
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "net PnL identity is invalid",
            )
        if self.slippage_cost_quote != _dsub(
            self.reference_pnl_quote,
            self.execution_gross_pnl_quote,
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "slippage cost identity is invalid",
            )
        if self.equity_after_quote != _dadd(self.equity_before_quote, self.net_pnl_quote):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "equity settlement identity is invalid",
            )
        if self.realized_drawdown_quote != _dsub(
            self.peak_realized_equity_after_quote,
            self.equity_after_quote,
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "realized drawdown identity is invalid",
            )

    @classmethod
    def from_economics(
        cls,
        *,
        trade_id: str,
        settlement_sequence: int,
        previous_settled_trade_id: str,
        settlement_event_id: str,
        settlement_utc_day: str,
        system_state_id: str,
        symbol: str,
        quote_currency: str,
        entry_timestamp_utc: str,
        exit_timestamp_utc: str,
        entry_tick_id: int,
        exit_tick_id: int,
        exit_reason: str,
        entry_quote: EntryEconomicsQuote,
        settlement: TradeSettlement,
    ) -> "TradeRecordV2":
        if entry_quote.config_fingerprint != settlement.config_fingerprint:
            raise PaperArtifactError(
                ArtifactReasonCode.CONFIG_MISMATCH,
                "entry quote and settlement fingerprints differ",
            )
        return cls(
            schema_version=2,
            trade_id=trade_id,
            settlement_sequence=settlement_sequence,
            previous_settled_trade_id=previous_settled_trade_id,
            settlement_event_id=settlement_event_id,
            settlement_utc_day=settlement_utc_day,
            system_state_id=system_state_id,
            symbol=symbol,
            quote_currency=quote_currency,
            side=settlement.side,
            quantity=settlement.quantity,
            reference_entry_price=settlement.reference_entry_price,
            reference_exit_price=settlement.reference_exit_price,
            modeled_entry_fill_price=settlement.modeled_entry_fill_price,
            modeled_exit_fill_price=settlement.modeled_exit_fill_price,
            entry_notional_quote=settlement.entry_notional_quote,
            exit_notional_quote=settlement.exit_notional_quote,
            entry_fee_quote=settlement.entry_fee_quote,
            exit_fee_quote=settlement.exit_fee_quote,
            total_fees_quote=settlement.total_fees_quote,
            reference_pnl_quote=settlement.reference_pnl_quote,
            execution_gross_pnl_quote=settlement.execution_gross_pnl_quote,
            slippage_cost_quote=settlement.slippage_cost_quote,
            net_pnl_quote=settlement.net_pnl_quote,
            net_return_on_entry_notional=settlement.net_return_on_entry_notional,
            net_return_on_equity_before=settlement.net_return_on_equity_before,
            equity_before_quote=settlement.equity_before_quote,
            equity_after_quote=settlement.equity_after_quote,
            peak_realized_equity_after_quote=settlement.peak_realized_equity_after_quote,
            realized_drawdown_quote=settlement.realized_drawdown_quote,
            realized_drawdown_rate=settlement.realized_drawdown_rate,
            risk_budget_quote=entry_quote.risk_budget_quote,
            modeled_stop_loss_quote=entry_quote.modeled_stop_loss_quote,
            entry_timestamp_utc=entry_timestamp_utc,
            exit_timestamp_utc=exit_timestamp_utc,
            entry_tick_id=entry_tick_id,
            exit_tick_id=exit_tick_id,
            exit_reason=exit_reason,
            economics_profile_id=settlement.economics_profile_id,
            economics_model_version=settlement.economics_model_version,
            config_fingerprint=settlement.config_fingerprint,
            economics_complete=True,
        )

    def to_record(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            result[name] = canonical_decimal(value) if isinstance(value, Decimal) else value
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "TradeRecordV2":
        artifact_schema_version(record, ARTIFACT_TRADE)
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})

    @property
    def record_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class PaperAccountState:
    schema_version: int
    account_id: str
    quote_currency: str
    starting_equity_quote: Decimal
    realized_equity_quote: Decimal
    cumulative_net_pnl_quote: Decimal
    peak_realized_equity_quote: Decimal
    realized_drawdown_quote: Decimal
    realized_drawdown_rate: Decimal
    utc_day: str
    daily_net_pnl_quote: Decimal
    daily_fees_quote: Decimal
    closed_trade_count: int
    last_settled_trade_id: str
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str
    last_update_event_id: str

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise PaperArtifactError(
                ArtifactReasonCode.SCHEMA_UNSUPPORTED,
                "PaperAccountState requires schema_version 1",
            )
        for name in (
            "account_id",
            "quote_currency",
            "utc_day",
            "economics_profile_id",
            "economics_model_version",
            "config_fingerprint",
        ):
            object.__setattr__(self, name, _text(getattr(self, name), name))
        for name in ("last_settled_trade_id", "last_update_event_id"):
            object.__setattr__(
                self,
                name,
                _text(getattr(self, name), name, allow_empty=True),
            )
        if len(self.utc_day) != 10:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "utc_day must use YYYY-MM-DD",
            )
        object.__setattr__(
            self,
            "closed_trade_count",
            _integer(self.closed_trade_count, "closed_trade_count"),
        )
        object.__setattr__(
            self,
            "starting_equity_quote",
            _positive_decimal(self.starting_equity_quote, "starting_equity_quote"),
        )
        object.__setattr__(
            self,
            "peak_realized_equity_quote",
            _positive_decimal(
                self.peak_realized_equity_quote,
                "peak_realized_equity_quote",
            ),
        )
        for name in (
            "realized_equity_quote",
            "cumulative_net_pnl_quote",
            "daily_net_pnl_quote",
        ):
            object.__setattr__(self, name, _decimal(getattr(self, name), name))
        for name in ("realized_drawdown_quote", "realized_drawdown_rate", "daily_fees_quote"):
            object.__setattr__(
                self,
                name,
                _non_negative_decimal(getattr(self, name), name),
            )

        if self.realized_equity_quote != _dadd(
            self.starting_equity_quote,
            self.cumulative_net_pnl_quote,
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "account realized-equity identity is invalid",
            )
        if self.peak_realized_equity_quote < max(
            self.starting_equity_quote,
            self.realized_equity_quote,
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "peak realized equity is below an observed equity",
            )
        if self.realized_drawdown_quote != _dsub(
            self.peak_realized_equity_quote,
            self.realized_equity_quote,
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "account drawdown identity is invalid",
            )
        expected_drawdown_rate = _ddiv(
            self.realized_drawdown_quote,
            self.peak_realized_equity_quote,
        )
        if self.realized_drawdown_rate != expected_drawdown_rate:
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "account drawdown-rate identity is invalid",
            )
        if self.closed_trade_count == 0 and (
            self.last_settled_trade_id or self.last_update_event_id
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "empty account cannot reference a settlement",
            )
        if self.closed_trade_count > 0 and not (
            self.last_settled_trade_id and self.last_update_event_id
        ):
            raise PaperArtifactError(
                ArtifactReasonCode.ARTIFACT_INVALID,
                "non-empty account must reference its last settlement",
            )

    @classmethod
    def initial(
        cls,
        *,
        account_id: str,
        quote_currency: str,
        starting_equity_quote: Decimal,
        utc_day: str,
        economics_profile_id: str,
        economics_model_version: str,
        config_fingerprint: str,
    ) -> "PaperAccountState":
        equity = _positive_decimal(starting_equity_quote, "starting_equity_quote")
        return cls(
            schema_version=1,
            account_id=account_id,
            quote_currency=quote_currency,
            starting_equity_quote=equity,
            realized_equity_quote=equity,
            cumulative_net_pnl_quote=ZERO,
            peak_realized_equity_quote=equity,
            realized_drawdown_quote=ZERO,
            realized_drawdown_rate=ZERO,
            utc_day=utc_day,
            daily_net_pnl_quote=ZERO,
            daily_fees_quote=ZERO,
            closed_trade_count=0,
            last_settled_trade_id="",
            economics_profile_id=economics_profile_id,
            economics_model_version=economics_model_version,
            config_fingerprint=config_fingerprint,
            last_update_event_id="",
        )

    def to_record(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for name in self.__dataclass_fields__:
            value = getattr(self, name)
            result[name] = canonical_decimal(value) if isinstance(value, Decimal) else value
        return result

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "PaperAccountState":
        artifact_schema_version(record, ARTIFACT_PAPER_ACCOUNT)
        return cls(**{name: record.get(name) for name in cls.__dataclass_fields__})

    @property
    def state_fingerprint(self) -> str:
        return canonical_json_sha256(self.to_record())


@dataclass(frozen=True)
class AccountEntryGuardDecision:
    entry_allowed: bool
    exit_allowed: bool
    reason_codes: tuple[str, ...]
    day_start_equity_quote: Decimal
    daily_loss_rate: Decimal
    daily_fee_rate: Decimal


def evaluate_account_entry_guard(
    account: PaperAccountState,
    config: PaperEconomicsConfig,
    *,
    entry_timestamp_utc: str | None = None,
) -> AccountEntryGuardDecision:
    """Evaluate account limits without ever blocking an exit."""

    if (
        account.quote_currency != config.quote_currency
        or account.economics_profile_id != config.economics_profile_id
        or account.economics_model_version != config.economics_model_version
        or account.config_fingerprint != config.config_fingerprint
    ):
        return AccountEntryGuardDecision(
            entry_allowed=False,
            exit_allowed=True,
            reason_codes=(ArtifactReasonCode.CONFIG_MISMATCH,),
            day_start_equity_quote=ZERO,
            daily_loss_rate=ZERO,
            daily_fee_rate=ZERO,
        )

    candidate_day = account.utc_day
    if entry_timestamp_utc is not None:
        candidate_day = _utc_timestamp_seconds(
            entry_timestamp_utc,
            "entry_timestamp_utc",
        )[:10]
    if candidate_day < account.utc_day:
        return AccountEntryGuardDecision(
            entry_allowed=False,
            exit_allowed=True,
            reason_codes=(AccountGuardReasonCode.ACCOUNT_DAY_REGRESSION,),
            day_start_equity_quote=account.realized_equity_quote,
            daily_loss_rate=ZERO,
            daily_fee_rate=ZERO,
        )
    same_day = candidate_day == account.utc_day
    daily_net_pnl = account.daily_net_pnl_quote if same_day else ZERO
    daily_fees = account.daily_fees_quote if same_day else ZERO
    day_start_equity = _dsub(
        account.realized_equity_quote,
        daily_net_pnl,
    )
    if account.realized_equity_quote <= ZERO or day_start_equity <= ZERO:
        return AccountEntryGuardDecision(
            entry_allowed=False,
            exit_allowed=True,
            reason_codes=(AccountGuardReasonCode.EQUITY_NON_POSITIVE,),
            day_start_equity_quote=day_start_equity,
            daily_loss_rate=ZERO,
            daily_fee_rate=ZERO,
        )

    daily_loss = max(ZERO, -daily_net_pnl)
    daily_loss_rate = _ddiv(daily_loss, day_start_equity)
    daily_fee_rate = _ddiv(daily_fees, day_start_equity)
    reasons: list[str] = []

    if daily_loss_rate >= config.max_daily_loss_rate:
        reasons.append(AccountGuardReasonCode.DAILY_LOSS_LIMIT)
    if account.realized_drawdown_rate >= config.max_realized_drawdown_rate:
        reasons.append(AccountGuardReasonCode.REALIZED_DRAWDOWN_LIMIT)
    if daily_fee_rate >= config.max_daily_fee_rate:
        reasons.append(AccountGuardReasonCode.DAILY_FEE_LIMIT)

    return AccountEntryGuardDecision(
        entry_allowed=not reasons,
        exit_allowed=True,
        reason_codes=tuple(reasons),
        day_start_equity_quote=day_start_equity,
        daily_loss_rate=daily_loss_rate,
        daily_fee_rate=daily_fee_rate,
    )


def apply_trade_to_account(
    account: PaperAccountState,
    trade: TradeRecordV2,
) -> PaperAccountState:
    if (
        account.quote_currency != trade.quote_currency
        or account.economics_profile_id != trade.economics_profile_id
        or account.economics_model_version != trade.economics_model_version
        or account.config_fingerprint != trade.config_fingerprint
    ):
        raise PaperArtifactError(
            ArtifactReasonCode.CONFIG_MISMATCH,
            "trade identity does not match paper account identity",
        )
    expected_sequence = account.closed_trade_count + 1
    if trade.settlement_sequence != expected_sequence:
        raise PaperArtifactError(
            ArtifactReasonCode.SEQUENCE_MISMATCH,
            f"expected settlement sequence {expected_sequence}",
        )
    if trade.previous_settled_trade_id != account.last_settled_trade_id:
        raise PaperArtifactError(
            ArtifactReasonCode.SEQUENCE_MISMATCH,
            "previous settled trade id does not match account",
        )
    if trade.equity_before_quote != account.realized_equity_quote:
        raise PaperArtifactError(
            ArtifactReasonCode.ACCOUNT_MISMATCH,
            "trade equity_before does not match realized account equity",
        )

    cumulative_pnl = _dadd(account.cumulative_net_pnl_quote, trade.net_pnl_quote)
    realized_equity = _dadd(account.starting_equity_quote, cumulative_pnl)
    peak_equity = max(account.peak_realized_equity_quote, realized_equity)
    drawdown = _dsub(peak_equity, realized_equity)
    drawdown_rate = _ddiv(drawdown, peak_equity)

    if trade.equity_after_quote != realized_equity:
        raise PaperArtifactError(
            ArtifactReasonCode.ACCOUNT_MISMATCH,
            "trade equity_after does not match derived account equity",
        )
    if trade.peak_realized_equity_after_quote != peak_equity:
        raise PaperArtifactError(
            ArtifactReasonCode.ACCOUNT_MISMATCH,
            "trade peak equity does not match derived account peak",
        )
    if trade.realized_drawdown_quote != drawdown:
        raise PaperArtifactError(
            ArtifactReasonCode.ACCOUNT_MISMATCH,
            "trade drawdown does not match derived account drawdown",
        )

    same_day = trade.settlement_utc_day == account.utc_day
    daily_pnl = (
        _dadd(account.daily_net_pnl_quote, trade.net_pnl_quote)
        if same_day
        else trade.net_pnl_quote
    )
    daily_fees = (
        _dadd(account.daily_fees_quote, trade.total_fees_quote)
        if same_day
        else trade.total_fees_quote
    )

    return PaperAccountState(
        schema_version=1,
        account_id=account.account_id,
        quote_currency=account.quote_currency,
        starting_equity_quote=account.starting_equity_quote,
        realized_equity_quote=realized_equity,
        cumulative_net_pnl_quote=cumulative_pnl,
        peak_realized_equity_quote=peak_equity,
        realized_drawdown_quote=drawdown,
        realized_drawdown_rate=drawdown_rate,
        utc_day=trade.settlement_utc_day,
        daily_net_pnl_quote=daily_pnl,
        daily_fees_quote=daily_fees,
        closed_trade_count=trade.settlement_sequence,
        last_settled_trade_id=trade.trade_id,
        economics_profile_id=account.economics_profile_id,
        economics_model_version=account.economics_model_version,
        config_fingerprint=account.config_fingerprint,
        last_update_event_id=trade.settlement_event_id,
    )


PositionArtifactV2 = Union[PositionStateS2FlatV2, PositionStateS2V2]
PositionArtifact = Union[PositionStateS2FlatV2, PositionStateS2V2, LegacyArtifact]
TradeArtifact = Union[TradeRecordV2, LegacyArtifact]


def parse_position_artifact(record: Mapping[str, Any]) -> PositionArtifact:
    version = artifact_schema_version(record, ARTIFACT_S2_POSITION)
    if version in (0, 1):
        return LegacyArtifact(
            artifact_type=ARTIFACT_S2_POSITION,
            schema_version=version,
            raw_record=dict(record),
        )
    position = str(record.get("position", "")).strip().upper()
    if position == "FLAT":
        return PositionStateS2FlatV2.from_record(record)
    if position in ("LONG", "SHORT"):
        return PositionStateS2V2.from_record(record)
    raise PaperArtifactError(
        ArtifactReasonCode.ARTIFACT_INVALID,
        "S2 V2 position must be FLAT, LONG, or SHORT",
    )


def parse_trade_artifact(record: Mapping[str, Any]) -> TradeArtifact:
    version = artifact_schema_version(record, ARTIFACT_TRADE)
    if version in (0, 1):
        return LegacyArtifact(
            artifact_type=ARTIFACT_TRADE,
            schema_version=version,
            raw_record=dict(record),
        )
    return TradeRecordV2.from_record(record)


__all__ = [
    "AccountEntryGuardDecision",
    "AccountGuardReasonCode",
    "ARTIFACT_PAPER_ACCOUNT",
    "ARTIFACT_S2_POSITION",
    "ARTIFACT_SETTLEMENT",
    "ARTIFACT_TRADE",
    "ArtifactReasonCode",
    "LegacyArtifact",
    "PaperAccountState",
    "PaperArtifactError",
    "PositionArtifactV2",
    "PositionStateS2FlatV2",
    "PositionStateS2V2",
    "SUPPORTED_ARTIFACT_SCHEMA_VERSIONS",
    "TradeRecordV2",
    "apply_trade_to_account",
    "artifact_schema_version",
    "canonical_json_sha256",
    "evaluate_account_entry_guard",
    "parse_position_artifact",
    "parse_trade_artifact",
]
