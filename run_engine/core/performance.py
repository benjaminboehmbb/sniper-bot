class PerformanceEngine:

    REALIZED_EVENT_TYPES = {"PARTIAL_CLOSE", "TRADE_CLOSED"}

    def __init__(self):
        self.stats = {}
        self._history = []

    def update(self, decision, pnl, regime, trade_event):

        event_type = getattr(trade_event, "event_type", None)

        if event_type not in self.REALIZED_EVENT_TYPES:
            return self._stats_snapshot()

        side = getattr(trade_event, "side", None)

        if side not in self.stats:
            self.stats[side] = {
                'pnl': 0.0,
                'trades': 0,
                'winrate': 0.0
            }

        self.stats[side]['trades'] += 1

        trades = self.stats[side]['trades']
        wins = 1 if pnl > 0 else 0

        self.stats[side]['pnl'] = (
            self.stats[side]['pnl'] * (trades - 1) + pnl
        ) / trades

        self.stats[side]['winrate'] = (
            (self.stats[side]['winrate'] * (trades - 1) + wins)
            / trades
        )

        self._history.append({
            'trade_id': getattr(trade_event, "trade_id", None),
            'event_type': event_type,
            'side': side,
            'pnl': pnl,
            'win': bool(wins),
            'tick': getattr(trade_event, "tick", None),
        })

        return self._stats_snapshot()

    def _stats_snapshot(self):
        return {side: dict(inner) for side, inner in self.stats.items()}

    def get_history(self):
        return [dict(record) for record in self._history]
