from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

QUANTITY_EPSILON = 1e-9


@dataclass(frozen=True)
class LifecycleEvent:
    event_type: str
    trade_id: Optional[int]
    side: Optional[str]
    price: float
    tick: int
    entry_price: float = 0.0
    prior_quantity: float = 0.0
    execution_quantity: float = 0.0
    resulting_quantity: float = 0.0
    quantity_delta: float = 0.0
    closed_quantity: float = 0.0
    remaining_quantity: float = 0.0
    reason: str = ""


@dataclass
class Trade:
    trade_id: int
    side: str
    entry_price: float
    entry_tick: int
    quantity: float = 1.0

    exit_price: Optional[float] = None
    exit_tick: Optional[int] = None

    status: str = "OPEN"
    events: List[LifecycleEvent] = field(default_factory=list)


class TradeLifecycleEngine:
    def __init__(self):
        self.trades: List[Trade] = []
        self.active_trade: Optional[Trade] = None
        self._id = 0
        self.failure_events: List[LifecycleEvent] = []

    def on_execution(self, execution: Dict[str, Any], state: Dict[str, Any]) -> Optional[LifecycleEvent]:
        action = execution.get("action", "HOLD")
        price = self._safe_float(state.get("price", 0.0))
        tick = self._safe_int(state.get("tick", 0))
        quantity = self._safe_float(execution.get("quantity", 0.0))

        if action != "HOLD" and not self._validate_execution_quantity(quantity):
            return self._failure_event(
                action=action,
                price=price,
                tick=tick,
                reason="INVALID_EXECUTION_QUANTITY",
            )

        if action == "HOLD":
            return None

        if action == "BUY":
            return self._handle_buy(price, tick, quantity)

        if action == "SELL":
            return self._handle_sell(price, tick, quantity)

        return self._failure_event(
            action=action,
            price=price,
            tick=tick,
            reason="UNSUPPORTED_EXECUTION_ACTION",
        )

    def get_active_trade(self) -> Optional[Trade]:
        return self.active_trade

    def get_all_trades(self) -> List[Trade]:
        return list(self.trades)

    def get_failure_events(self) -> List[LifecycleEvent]:
        return list(self.failure_events)

    def current_position(self) -> Dict[str, Any]:
        if self.active_trade is None:
            return {
                "position": "FLAT",
                "side": None,
                "entry_price": 0.0,
                "quantity": 0.0,
            }

        return {
            "position": self.active_trade.side,
            "side": self.active_trade.side,
            "entry_price": self.active_trade.entry_price,
            "quantity": self.active_trade.quantity,
        }

    def _handle_buy(self, price: float, tick: int, quantity: float) -> LifecycleEvent:
        if self.active_trade is None:
            return self._open_trade(side="LONG", price=price, tick=tick, quantity=quantity)

        if self.active_trade.side == "SHORT":
            return self._close_trade(price=price, tick=tick, quantity=quantity)

        return self._failure_event(
            action="BUY",
            price=price,
            tick=tick,
            reason="BUY_WHILE_LONG_OPEN",
        )

    def _handle_sell(self, price: float, tick: int, quantity: float) -> LifecycleEvent:
        if self.active_trade is None:
            return self._open_trade(side="SHORT", price=price, tick=tick, quantity=quantity)

        if self.active_trade.side == "LONG":
            return self._close_trade(price=price, tick=tick, quantity=quantity)

        return self._failure_event(
            action="SELL",
            price=price,
            tick=tick,
            reason="SELL_WHILE_SHORT_OPEN",
        )

    def _open_trade(self, side: str, price: float, tick: int, quantity: float) -> LifecycleEvent:
        self._id += 1

        trade = Trade(
            trade_id=self._id,
            side=side,
            entry_price=price,
            entry_tick=tick,
            quantity=quantity,
        )

        event = LifecycleEvent(
            event_type="TRADE_OPENED",
            trade_id=trade.trade_id,
            side=side,
            price=price,
            tick=tick,
            entry_price=price,
            prior_quantity=0.0,
            execution_quantity=trade.quantity,
            resulting_quantity=trade.quantity,
            quantity_delta=trade.quantity,
            closed_quantity=0.0,
            remaining_quantity=trade.quantity,
        )

        trade.events.append(event)
        self.trades.append(trade)
        self.active_trade = trade

        return event

    def _close_trade(self, price: float, tick: int, quantity: float) -> LifecycleEvent:
        if self.active_trade is None:
            return self._failure_event(
                action="CLOSE",
                price=price,
                tick=tick,
                reason="NO_ACTIVE_TRADE",
            )

        trade = self.active_trade

        trade.exit_price = price
        trade.exit_tick = tick
        trade.status = "CLOSED"

        event = LifecycleEvent(
            event_type="TRADE_CLOSED",
            trade_id=trade.trade_id,
            side=trade.side,
            price=price,
            tick=tick,
            entry_price=trade.entry_price,
            prior_quantity=trade.quantity,
            execution_quantity=quantity,
            resulting_quantity=0.0,
            quantity_delta=-trade.quantity,
            closed_quantity=trade.quantity,
            remaining_quantity=0.0,
        )

        trade.events.append(event)
        self.active_trade = None

        return event

    def _failure_event(self, action: str, price: float, tick: int, reason: str) -> LifecycleEvent:
        active_quantity = self.active_trade.quantity if self.active_trade else 0.0

        event = LifecycleEvent(
            event_type="RUNTIME_FAILURE_EVENT",
            trade_id=self.active_trade.trade_id if self.active_trade else None,
            side=self.active_trade.side if self.active_trade else None,
            price=price,
            tick=tick,
            entry_price=self.active_trade.entry_price if self.active_trade else 0.0,
            prior_quantity=active_quantity,
            execution_quantity=0.0,
            resulting_quantity=active_quantity,
            quantity_delta=0.0,
            closed_quantity=0.0,
            remaining_quantity=active_quantity,
            reason=f"{reason}:{action}",
        )

        self.failure_events.append(event)

        if self.active_trade is not None:
            self.active_trade.events.append(event)

        return event

    def _validate_execution_quantity(self, quantity: float) -> bool:
        return quantity > QUANTITY_EPSILON

    @staticmethod
    def _safe_float(value: Any) -> float:
        if value is None:
            return 0.0
        return float(value)

    @staticmethod
    def _safe_int(value: Any) -> int:
        if value is None:
            return 0
        return int(value)
