from typing import Any, Dict, Optional


class PnLEngine:

    def __init__(self):
        self.last_realized_pnl = 0.0

    def update(
        self,
        trade_event: Optional[Any],
        execution: Dict[str, Any],
    ) -> float:
        """
        Computes realized PnL exclusively from lifecycle facts.
        """

        if trade_event is None:
            return 0.0

        if getattr(trade_event, "event_type", None) != "TRADE_CLOSED":
            return 0.0

        side = getattr(trade_event, "side", None)
        entry_price = float(getattr(trade_event, "entry_price", 0.0))
        exit_price = float(getattr(trade_event, "price", 0.0))
        quantity = float(getattr(trade_event, "quantity", 1.0))

        if side == "LONG":
            pnl = (exit_price - entry_price) * quantity
        elif side == "SHORT":
            pnl = (entry_price - exit_price) * quantity
        else:
            pnl = 0.0

        self.last_realized_pnl = pnl

        return pnl

    def get_last_realized_pnl(self) -> float:
        return self.last_realized_pnl
