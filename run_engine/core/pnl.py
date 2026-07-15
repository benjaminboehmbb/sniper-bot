from typing import Any, Optional


class PnLEngine:

    def __init__(self):
        self.last_realized_pnl = 0.0

    def update(
        self,
        trade_event: Optional[Any],
        entry_basis: float,
    ) -> float:
        """
        Computes realized PnL exclusively from lifecycle facts.
        """

        if trade_event is None:
            return 0.0

        event_type = getattr(trade_event, "event_type", None)

        if event_type not in {"TRADE_CLOSED", "PARTIAL_CLOSE"}:
            return 0.0

        side = getattr(trade_event, "side", None)
        entry_price = float(entry_basis)
        exit_price = float(getattr(trade_event, "price", 0.0))
        quantity = float(getattr(trade_event, "closed_quantity", 0.0))

        if side == "LONG":
            pnl = (exit_price - entry_price) * quantity
        elif side == "SHORT":
            pnl = (entry_price - exit_price) * quantity
        else:
            pnl = 0.0

        self.last_realized_pnl = pnl

        return pnl

    def compute_equity(
        self,
        trade_event: Optional[Any],
        event_pnl: float,
        prior_cumulative_pnl: float,
        prior_equity: float,
        prior_peak_equity: float,
    ) -> dict:
        """
        Computes Realized PnL (cumulative), Equity, and Peak Equity from
        the prior canonical values and the current tick's event-PnL.
        """

        event_type = getattr(trade_event, "event_type", None)

        if event_type == "RUNTIME_FAILURE_EVENT":
            return {
                "realized_pnl_cumulative": prior_cumulative_pnl,
                "equity": prior_equity,
                "peak_equity": prior_peak_equity,
            }

        new_cumulative_pnl = prior_cumulative_pnl + event_pnl
        new_equity = prior_equity + event_pnl
        new_peak_equity = max(prior_peak_equity, new_equity)

        return {
            "realized_pnl_cumulative": new_cumulative_pnl,
            "equity": new_equity,
            "peak_equity": new_peak_equity,
        }

    def get_last_realized_pnl(self) -> float:
        return self.last_realized_pnl
