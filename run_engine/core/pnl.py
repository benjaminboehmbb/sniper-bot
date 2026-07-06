# run_engine/core/pnl.py

from typing import Optional, Dict, Any


class PnLEngine:

    def __init__(self):
        # keine laufende Equity-Logik mehr hier
        self.last_realized_pnl = 0.0

    def update(self, trade_event: Optional[Any], execution: Dict) -> float:

        """
        REALIZED PnL ONLY:
        - nur wenn ein Trade geschlossen wird
        - keine Tick-basierte Berechnung
        - keine unrealized PnL Aggregation
        """

        if trade_event is None:
            return 0.0

        # TradeLifecycleEngine liefert Trade-Objekt
        if hasattr(trade_event, "status") and trade_event.status == "CLOSED":

            pnl = getattr(trade_event, "realized_pnl", 0.0)

            self.last_realized_pnl = pnl

            return pnl

        return 0.0

    def get_last_realized_pnl(self) -> float:
        return self.last_realized_pnl