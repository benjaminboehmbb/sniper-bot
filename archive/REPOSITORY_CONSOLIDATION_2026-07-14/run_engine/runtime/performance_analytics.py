from collections import defaultdict


class PerformanceAnalytics:

    def __init__(self):

        # regime -> action -> metrics
        self.data = defaultdict(lambda: defaultdict(lambda: {
            "pnl": 0.0,
            "trades": 0,
            "wins": 0,
            "losses": 0
        }))

    def record(self, regime, action, pnl):

        bucket = self.data[regime][action]

        bucket["pnl"] += pnl
        bucket["trades"] += 1

        if pnl > 0:
            bucket["wins"] += 1
        else:
            bucket["losses"] += 1

    def get_metrics(self, regime):

        result = {}

        for action, m in self.data[regime].items():

            trades = m["trades"]
            pnl = m["pnl"]

            winrate = m["wins"] / trades if trades > 0 else 0.0

            result[action] = {
                "pnl": pnl,
                "trades": trades,
                "winrate": winrate
            }

        return result

    def get_global_summary(self):

        summary = {}

        for regime in self.data:

            summary[regime] = self.get_metrics(regime)

        return summary