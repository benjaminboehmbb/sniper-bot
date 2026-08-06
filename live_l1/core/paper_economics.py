#!/usr/bin/env python3
"""Pure and deterministic execution-economics calculations for paper trading.

This module deliberately has no file, environment, clock, network, logging, or
runtime-state access.  It does not decide whether a strategy wants a trade.  It
only validates explicit economic inputs and calculates fills, fees, position
size, entry authorization, and settlement values.

All externally supplied numeric values must be ``Decimal``, ``int``, or decimal
strings.  Floats are rejected at the boundary so that binary floating-point
artifacts cannot silently enter account calculations.  Monetary calculations
remain exact ``Decimal`` values in IU-1; the only rounding performed here is
the mandatory downward rounding of quantity to ``quantity_step``.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from typing import Literal, Mapping, Optional


Side = Literal["LONG", "SHORT"]
FillPhase = Literal["ENTRY", "EXIT"]

ZERO = Decimal("0")
ONE = Decimal("1")
TEN_THOUSAND = Decimal("10000")


class ReasonCode:
    """Stable machine-readable reason codes owned by the economics core."""

    AUTHORIZED = "PEE_AUTHORIZED"
    CONFIG_INVALID = "PEE_CONFIG_INVALID"
    INPUT_INVALID = "PEE_INPUT_INVALID"
    INPUT_FLOAT_NOT_ALLOWED = "PEE_INPUT_FLOAT_NOT_ALLOWED"
    SIDE_INVALID = "PEE_SIDE_INVALID"
    PHASE_INVALID = "PEE_PHASE_INVALID"
    STOP_DIRECTION_INVALID = "PEE_STOP_DIRECTION_INVALID"
    QUANTITY_ZERO = "PEE_QUANTITY_ZERO"
    QUANTITY_BELOW_MIN = "PEE_QUANTITY_BELOW_MIN"
    NOTIONAL_BELOW_MIN = "PEE_NOTIONAL_BELOW_MIN"
    RISK_LIMIT_EXCEEDED = "PEE_RISK_LIMIT_EXCEEDED"
    NOTIONAL_LIMIT_EXCEEDED = "PEE_NOTIONAL_LIMIT_EXCEEDED"
    CONFIG_FINGERPRINT_MISMATCH = "PEE_CONFIG_FINGERPRINT_MISMATCH"


class PaperEconomicsError(ValueError):
    """Validation error carrying a stable machine-readable reason code."""

    def __init__(self, reason_code: str, message: str) -> None:
        self.reason_code = reason_code
        self.detail = message
        super().__init__(f"{reason_code}: {message}")


def _decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise PaperEconomicsError(
            ReasonCode.INPUT_FLOAT_NOT_ALLOWED,
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
            raise PaperEconomicsError(
                ReasonCode.INPUT_INVALID,
                f"{field_name} is not a valid decimal",
            ) from exc
    else:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            f"{field_name} must be Decimal, int, or a decimal string",
        )

    if not result.is_finite():
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            f"{field_name} must be finite",
        )
    if result == ZERO:
        return ZERO
    return result


def _positive(value: object, field_name: str) -> Decimal:
    result = _decimal(value, field_name)
    if result <= ZERO:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            f"{field_name} must be greater than zero",
        )
    return result


def _non_negative(value: object, field_name: str) -> Decimal:
    result = _decimal(value, field_name)
    if result < ZERO:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            f"{field_name} must not be negative",
        )
    return result


def _rate_at_most_one(
    value: object,
    field_name: str,
    *,
    allow_zero: bool,
) -> Decimal:
    result = _decimal(value, field_name)
    lower_ok = result >= ZERO if allow_zero else result > ZERO
    if not lower_ok or result > ONE:
        relation = "between zero and one" if allow_zero else "greater than zero and at most one"
        raise PaperEconomicsError(
            ReasonCode.CONFIG_INVALID,
            f"{field_name} must be {relation}",
        )
    return result


def _non_empty_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PaperEconomicsError(
            ReasonCode.CONFIG_INVALID,
            f"{field_name} must be a non-empty string",
        )
    return value.strip()


def _canonical_decimal(value: Decimal) -> str:
    if value == ZERO:
        return "0"
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _validate_side(side: object) -> Side:
    if side not in ("LONG", "SHORT"):
        raise PaperEconomicsError(
            ReasonCode.SIDE_INVALID,
            "side must be exactly LONG or SHORT",
        )
    return side


@dataclass(frozen=True)
class PaperEconomicsConfig:
    """Explicit, versioned economics profile without production defaults."""

    schema_version: int
    economics_model_version: str
    economics_profile_id: str
    quote_currency: str
    starting_equity_quote: Decimal
    risk_per_trade_rate: Decimal
    max_position_notional_rate: Decimal
    entry_fee_rate: Decimal
    exit_fee_rate: Decimal
    entry_slippage_bps: Decimal
    exit_slippage_bps: Decimal
    quantity_step: Decimal
    min_quantity: Decimal
    min_notional_quote: Decimal
    max_daily_loss_rate: Decimal
    max_daily_fee_rate: Decimal
    max_realized_drawdown_rate: Decimal

    def __post_init__(self) -> None:
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int):
            raise PaperEconomicsError(
                ReasonCode.CONFIG_INVALID,
                "schema_version must be an integer",
            )
        if self.schema_version != 1:
            raise PaperEconomicsError(
                ReasonCode.CONFIG_INVALID,
                "IU-1 supports PaperEconomicsConfig schema_version 1 only",
            )

        object.__setattr__(
            self,
            "economics_model_version",
            _non_empty_text(self.economics_model_version, "economics_model_version"),
        )
        object.__setattr__(
            self,
            "economics_profile_id",
            _non_empty_text(self.economics_profile_id, "economics_profile_id"),
        )
        quote_currency = _non_empty_text(self.quote_currency, "quote_currency").upper()
        object.__setattr__(self, "quote_currency", quote_currency)

        object.__setattr__(
            self,
            "starting_equity_quote",
            _positive(self.starting_equity_quote, "starting_equity_quote"),
        )
        object.__setattr__(
            self,
            "risk_per_trade_rate",
            _rate_at_most_one(
                self.risk_per_trade_rate,
                "risk_per_trade_rate",
                allow_zero=False,
            ),
        )
        object.__setattr__(
            self,
            "max_position_notional_rate",
            _rate_at_most_one(
                self.max_position_notional_rate,
                "max_position_notional_rate",
                allow_zero=False,
            ),
        )
        object.__setattr__(
            self,
            "entry_fee_rate",
            _rate_at_most_one(self.entry_fee_rate, "entry_fee_rate", allow_zero=True),
        )
        object.__setattr__(
            self,
            "exit_fee_rate",
            _rate_at_most_one(self.exit_fee_rate, "exit_fee_rate", allow_zero=True),
        )

        entry_slippage = _non_negative(self.entry_slippage_bps, "entry_slippage_bps")
        exit_slippage = _non_negative(self.exit_slippage_bps, "exit_slippage_bps")
        if entry_slippage >= TEN_THOUSAND or exit_slippage >= TEN_THOUSAND:
            raise PaperEconomicsError(
                ReasonCode.CONFIG_INVALID,
                "slippage must be less than 10000 basis points",
            )
        object.__setattr__(self, "entry_slippage_bps", entry_slippage)
        object.__setattr__(self, "exit_slippage_bps", exit_slippage)

        object.__setattr__(
            self,
            "quantity_step",
            _positive(self.quantity_step, "quantity_step"),
        )
        object.__setattr__(
            self,
            "min_quantity",
            _non_negative(self.min_quantity, "min_quantity"),
        )
        object.__setattr__(
            self,
            "min_notional_quote",
            _non_negative(self.min_notional_quote, "min_notional_quote"),
        )
        object.__setattr__(
            self,
            "max_daily_loss_rate",
            _rate_at_most_one(
                self.max_daily_loss_rate,
                "max_daily_loss_rate",
                allow_zero=False,
            ),
        )
        object.__setattr__(
            self,
            "max_daily_fee_rate",
            _rate_at_most_one(
                self.max_daily_fee_rate,
                "max_daily_fee_rate",
                allow_zero=False,
            ),
        )
        object.__setattr__(
            self,
            "max_realized_drawdown_rate",
            _rate_at_most_one(
                self.max_realized_drawdown_rate,
                "max_realized_drawdown_rate",
                allow_zero=False,
            ),
        )

    def canonical_payload(self) -> Mapping[str, object]:
        """Return the semantic profile payload used for stable identity."""

        return {
            "schema_version": self.schema_version,
            "economics_model_version": self.economics_model_version,
            "economics_profile_id": self.economics_profile_id,
            "quote_currency": self.quote_currency,
            "starting_equity_quote": _canonical_decimal(self.starting_equity_quote),
            "risk_per_trade_rate": _canonical_decimal(self.risk_per_trade_rate),
            "max_position_notional_rate": _canonical_decimal(self.max_position_notional_rate),
            "entry_fee_rate": _canonical_decimal(self.entry_fee_rate),
            "exit_fee_rate": _canonical_decimal(self.exit_fee_rate),
            "entry_slippage_bps": _canonical_decimal(self.entry_slippage_bps),
            "exit_slippage_bps": _canonical_decimal(self.exit_slippage_bps),
            "quantity_step": _canonical_decimal(self.quantity_step),
            "min_quantity": _canonical_decimal(self.min_quantity),
            "min_notional_quote": _canonical_decimal(self.min_notional_quote),
            "max_daily_loss_rate": _canonical_decimal(self.max_daily_loss_rate),
            "max_daily_fee_rate": _canonical_decimal(self.max_daily_fee_rate),
            "max_realized_drawdown_rate": _canonical_decimal(
                self.max_realized_drawdown_rate
            ),
        }

    @property
    def config_fingerprint(self) -> str:
        canonical = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class EntryEconomicsQuote:
    side: Side
    reference_entry_price: Decimal
    reference_stop_price: Decimal
    modeled_entry_fill_price: Decimal
    modeled_stop_fill_price: Decimal
    realized_equity_quote: Decimal
    risk_budget_quote: Decimal
    modeled_stop_loss_per_unit_quote: Decimal
    risk_quantity: Decimal
    notional_cap_quote: Decimal
    notional_cap_quantity: Decimal
    raw_quantity: Decimal
    quantity_step: Decimal
    quantity: Decimal
    entry_notional_quote: Decimal
    entry_fee_quote: Decimal
    expected_stop_notional_quote: Decimal
    expected_stop_fee_quote: Decimal
    modeled_stop_loss_quote: Decimal
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str


@dataclass(frozen=True)
class EntryAuthorization:
    allowed: bool
    reason_code: str
    findings: tuple[str, ...]
    quantity: Decimal
    quote: Optional[EntryEconomicsQuote]


@dataclass(frozen=True)
class TradeSettlement:
    side: Side
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
    economics_profile_id: str
    economics_model_version: str
    config_fingerprint: str


def model_fill_price(
    *,
    side: Side,
    phase: FillPhase,
    reference_price: object,
    slippage_bps: object,
) -> Decimal:
    """Apply deterministic adverse slippage for the side and fill phase."""

    validated_side = _validate_side(side)
    if phase not in ("ENTRY", "EXIT"):
        raise PaperEconomicsError(
            ReasonCode.PHASE_INVALID,
            "phase must be exactly ENTRY or EXIT",
        )
    price = _positive(reference_price, "reference_price")
    bps = _non_negative(slippage_bps, "slippage_bps")
    if bps >= TEN_THOUSAND:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            "slippage_bps must be less than 10000",
        )
    rate = bps / TEN_THOUSAND

    adverse_up = (validated_side == "LONG" and phase == "ENTRY") or (
        validated_side == "SHORT" and phase == "EXIT"
    )
    multiplier = ONE + rate if adverse_up else ONE - rate
    return price * multiplier


def calculate_fee_quote(*, notional_quote: object, fee_rate: object) -> Decimal:
    """Calculate a non-negative fee from absolute executed notional."""

    notional = _non_negative(notional_quote, "notional_quote")
    rate = _non_negative(fee_rate, "fee_rate")
    if rate > ONE:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            "fee_rate must be at most one",
        )
    return abs(notional) * rate


def floor_quantity_to_step(*, quantity: object, quantity_step: object) -> Decimal:
    """Round a non-negative quantity down to an explicit exchange step."""

    value = _non_negative(quantity, "quantity")
    step = _positive(quantity_step, "quantity_step")
    steps = (value / step).to_integral_value(rounding=ROUND_FLOOR)
    result = steps * step
    return ZERO if result == ZERO else result


def _build_entry_quote(
    *,
    side: Side,
    realized_equity_quote: object,
    reference_entry_price: object,
    reference_stop_price: object,
    config: PaperEconomicsConfig,
) -> EntryEconomicsQuote:
    validated_side = _validate_side(side)
    equity = _positive(realized_equity_quote, "realized_equity_quote")
    entry_reference = _positive(reference_entry_price, "reference_entry_price")
    stop_reference = _positive(reference_stop_price, "reference_stop_price")

    valid_stop_direction = (
        validated_side == "LONG" and stop_reference < entry_reference
    ) or (validated_side == "SHORT" and stop_reference > entry_reference)
    if not valid_stop_direction:
        raise PaperEconomicsError(
            ReasonCode.STOP_DIRECTION_INVALID,
            "LONG stop must be below entry and SHORT stop must be above entry",
        )

    entry_fill = model_fill_price(
        side=validated_side,
        phase="ENTRY",
        reference_price=entry_reference,
        slippage_bps=config.entry_slippage_bps,
    )
    stop_fill = model_fill_price(
        side=validated_side,
        phase="EXIT",
        reference_price=stop_reference,
        slippage_bps=config.exit_slippage_bps,
    )

    price_loss_per_unit = (
        entry_fill - stop_fill
        if validated_side == "LONG"
        else stop_fill - entry_fill
    )
    entry_fee_per_unit = entry_fill * config.entry_fee_rate
    stop_fee_per_unit = stop_fill * config.exit_fee_rate
    modeled_loss_per_unit = (
        price_loss_per_unit + entry_fee_per_unit + stop_fee_per_unit
    )
    if modeled_loss_per_unit <= ZERO:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            "modeled stop loss per unit must be greater than zero",
        )

    risk_budget = equity * config.risk_per_trade_rate
    risk_quantity = risk_budget / modeled_loss_per_unit
    notional_cap = equity * config.max_position_notional_rate
    notional_cap_quantity = notional_cap / entry_fill
    raw_quantity = min(risk_quantity, notional_cap_quantity)
    quantity = floor_quantity_to_step(
        quantity=raw_quantity,
        quantity_step=config.quantity_step,
    )

    entry_notional = quantity * entry_fill
    entry_fee = calculate_fee_quote(
        notional_quote=entry_notional,
        fee_rate=config.entry_fee_rate,
    )
    expected_stop_notional = quantity * stop_fill
    expected_stop_fee = calculate_fee_quote(
        notional_quote=expected_stop_notional,
        fee_rate=config.exit_fee_rate,
    )
    modeled_stop_loss = quantity * modeled_loss_per_unit

    return EntryEconomicsQuote(
        side=validated_side,
        reference_entry_price=entry_reference,
        reference_stop_price=stop_reference,
        modeled_entry_fill_price=entry_fill,
        modeled_stop_fill_price=stop_fill,
        realized_equity_quote=equity,
        risk_budget_quote=risk_budget,
        modeled_stop_loss_per_unit_quote=modeled_loss_per_unit,
        risk_quantity=risk_quantity,
        notional_cap_quote=notional_cap,
        notional_cap_quantity=notional_cap_quantity,
        raw_quantity=raw_quantity,
        quantity_step=config.quantity_step,
        quantity=quantity,
        entry_notional_quote=entry_notional,
        entry_fee_quote=entry_fee,
        expected_stop_notional_quote=expected_stop_notional,
        expected_stop_fee_quote=expected_stop_fee,
        modeled_stop_loss_quote=modeled_stop_loss,
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


def authorize_entry(
    *,
    side: Side,
    realized_equity_quote: object,
    reference_entry_price: object,
    reference_stop_price: object,
    config: PaperEconomicsConfig,
) -> EntryAuthorization:
    """Calculate quantity and return an explicit allow/reject decision."""

    try:
        quote = _build_entry_quote(
            side=side,
            realized_equity_quote=realized_equity_quote,
            reference_entry_price=reference_entry_price,
            reference_stop_price=reference_stop_price,
            config=config,
        )
    except PaperEconomicsError as exc:
        return EntryAuthorization(
            allowed=False,
            reason_code=exc.reason_code,
            findings=(exc.detail,),
            quantity=ZERO,
            quote=None,
        )

    if quote.quantity <= ZERO:
        return EntryAuthorization(
            allowed=False,
            reason_code=ReasonCode.QUANTITY_ZERO,
            findings=("quantity is zero after downward step rounding",),
            quantity=ZERO,
            quote=quote,
        )
    if quote.quantity < config.min_quantity:
        return EntryAuthorization(
            allowed=False,
            reason_code=ReasonCode.QUANTITY_BELOW_MIN,
            findings=("quantity is below min_quantity",),
            quantity=quote.quantity,
            quote=quote,
        )
    if quote.entry_notional_quote < config.min_notional_quote:
        return EntryAuthorization(
            allowed=False,
            reason_code=ReasonCode.NOTIONAL_BELOW_MIN,
            findings=("entry notional is below min_notional_quote",),
            quantity=quote.quantity,
            quote=quote,
        )
    if quote.modeled_stop_loss_quote > quote.risk_budget_quote:
        return EntryAuthorization(
            allowed=False,
            reason_code=ReasonCode.RISK_LIMIT_EXCEEDED,
            findings=("rounded quantity exceeds risk budget",),
            quantity=quote.quantity,
            quote=quote,
        )
    if quote.entry_notional_quote > quote.notional_cap_quote:
        return EntryAuthorization(
            allowed=False,
            reason_code=ReasonCode.NOTIONAL_LIMIT_EXCEEDED,
            findings=("rounded quantity exceeds notional cap",),
            quantity=quote.quantity,
            quote=quote,
        )

    return EntryAuthorization(
        allowed=True,
        reason_code=ReasonCode.AUTHORIZED,
        findings=(),
        quantity=quote.quantity,
        quote=quote,
    )


def settle_trade(
    *,
    entry_quote: EntryEconomicsQuote,
    reference_exit_price: object,
    equity_before_quote: object,
    peak_realized_equity_before_quote: object,
    config: PaperEconomicsConfig,
) -> TradeSettlement:
    """Settle an authorized entry quote against one reference exit price."""

    if entry_quote.config_fingerprint != config.config_fingerprint:
        raise PaperEconomicsError(
            ReasonCode.CONFIG_FINGERPRINT_MISMATCH,
            "entry quote and settlement config fingerprints differ",
        )
    if entry_quote.quantity <= ZERO:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            "entry quote quantity must be greater than zero",
        )

    exit_reference = _positive(reference_exit_price, "reference_exit_price")
    equity_before = _positive(equity_before_quote, "equity_before_quote")
    peak_before = _positive(
        peak_realized_equity_before_quote,
        "peak_realized_equity_before_quote",
    )
    if peak_before < equity_before:
        raise PaperEconomicsError(
            ReasonCode.INPUT_INVALID,
            "peak realized equity before settlement cannot be below current equity",
        )

    exit_fill = model_fill_price(
        side=entry_quote.side,
        phase="EXIT",
        reference_price=exit_reference,
        slippage_bps=config.exit_slippage_bps,
    )
    exit_notional = entry_quote.quantity * exit_fill
    exit_fee = calculate_fee_quote(
        notional_quote=exit_notional,
        fee_rate=config.exit_fee_rate,
    )
    total_fees = entry_quote.entry_fee_quote + exit_fee

    if entry_quote.side == "LONG":
        reference_pnl = entry_quote.quantity * (
            exit_reference - entry_quote.reference_entry_price
        )
        execution_gross_pnl = entry_quote.quantity * (
            exit_fill - entry_quote.modeled_entry_fill_price
        )
    else:
        reference_pnl = entry_quote.quantity * (
            entry_quote.reference_entry_price - exit_reference
        )
        execution_gross_pnl = entry_quote.quantity * (
            entry_quote.modeled_entry_fill_price - exit_fill
        )

    slippage_cost = reference_pnl - execution_gross_pnl
    net_pnl = execution_gross_pnl - total_fees
    equity_after = equity_before + net_pnl
    peak_after = max(peak_before, equity_after)
    drawdown = peak_after - equity_after

    return TradeSettlement(
        side=entry_quote.side,
        quantity=entry_quote.quantity,
        reference_entry_price=entry_quote.reference_entry_price,
        reference_exit_price=exit_reference,
        modeled_entry_fill_price=entry_quote.modeled_entry_fill_price,
        modeled_exit_fill_price=exit_fill,
        entry_notional_quote=entry_quote.entry_notional_quote,
        exit_notional_quote=exit_notional,
        entry_fee_quote=entry_quote.entry_fee_quote,
        exit_fee_quote=exit_fee,
        total_fees_quote=total_fees,
        reference_pnl_quote=reference_pnl,
        execution_gross_pnl_quote=execution_gross_pnl,
        slippage_cost_quote=slippage_cost,
        net_pnl_quote=net_pnl,
        net_return_on_entry_notional=net_pnl / entry_quote.entry_notional_quote,
        net_return_on_equity_before=net_pnl / equity_before,
        equity_before_quote=equity_before,
        equity_after_quote=equity_after,
        peak_realized_equity_after_quote=peak_after,
        realized_drawdown_quote=drawdown,
        realized_drawdown_rate=drawdown / peak_after,
        economics_profile_id=config.economics_profile_id,
        economics_model_version=config.economics_model_version,
        config_fingerprint=config.config_fingerprint,
    )


__all__ = [
    "EntryAuthorization",
    "EntryEconomicsQuote",
    "PaperEconomicsConfig",
    "PaperEconomicsError",
    "ReasonCode",
    "TradeSettlement",
    "authorize_entry",
    "calculate_fee_quote",
    "floor_quantity_to_step",
    "model_fill_price",
    "settle_trade",
]
