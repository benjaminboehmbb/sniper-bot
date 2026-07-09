class PerformanceEngine:

    def __init__(self):
        self.stats = {}

    def update(self, decision, pnl, regime, trade_event):

        if getattr(trade_event, "event_type", None) == "RUNTIME_FAILURE_EVENT":
            return self.stats

        action = decision.get('action', 'HOLD')

        if action not in self.stats:
            self.stats[action] = {
                'pnl': 0.0,
                'trades': 0,
                'winrate': 0.0
            }

        self.stats[action]['trades'] += 1

        trades = self.stats[action]['trades']
        wins = 1 if pnl > 0 else 0

        self.stats[action]['pnl'] = (
            self.stats[action]['pnl'] * (trades - 1) + pnl
        ) / trades

        self.stats[action]['winrate'] = (
            (self.stats[action]['winrate'] * (trades - 1) + wins)
            / trades
        )

        return self.stats
