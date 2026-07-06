# run_engine/core/trade_lifecycle.py

from dataclasses import dataclass, field
from typing import Optional, Dict, List


@dataclass
class Trade:
    trade_id: int
    side: str                  # LONG / SHORT
    entry_price: float
    entry_tick: int

    exit_price: Optional[float] = None
    exit_tick: Optional[int] = None

    status: str = "OPEN"       # OPEN / CLOSED
    realized_pnl: float = 0.0


class TradeLifecycleEngine:

    def __init__(self):
        self.trades: List[Trade] = []
        self.active_trade: Optional[Trade] = None
        self._id = 0

    def on_execution(self, execution: Dict, state: Dict):

        action = execution.get("action")

        price = state["price"]
        tick = state["tick"]

        # -----------------------
        # OPEN TRADE
        # -----------------------
        if action == "BUY" and self.active_trade is None:
            self._id += 1

            self.active_trade = Trade(
                trade_id=self._id,
                side="LONG",
                entry_price=price,
                entry_tick=tick
            )

            self.trades.append(self.active_trade)
            return self.active_trade

        # -----------------------
        # CLOSE TRADE
        # -----------------------
        if action == "SELL" and self.active_trade is not None:

            trade = self.active_trade

            trade.exit_price = price
            trade.exit_tick = tick
            trade.status = "CLOSED"

            trade.realized_pnl = trade.exit_price - trade.entry_price

            self.active_trade = None

            return trade

        return None

    def get_active_trade(self):
        return self.active_trade

    def get_all_trades(self):
        return self.trades

    def realized_pnl(self):
        return sum(t.realized_pnl for t in self.trades if t.status == "CLOSED")