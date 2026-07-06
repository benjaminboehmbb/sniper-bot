class StrategyMemory:

    def __init__(self):

        self.history = []

        self.stats = {
            "TREND_UP": {"BUY": 0, "SELL": 0, "HOLD": 0},
            "TREND_DOWN": {"BUY": 0, "SELL": 0, "HOLD": 0},
            "CHOP": {"BUY": 0, "SELL": 0, "HOLD": 0},
            "HIGH_VOLATILITY": {"BUY": 0, "SELL": 0, "HOLD": 0},
        }

    def record(self, regime, decision, execution):

        action = decision.get("action")
        status = execution.get("status")

        reward = self._compute_reward(status)

        self.history.append({
            "regime": regime,
            "action": action,
            "reward": reward
        })

        if regime in self.stats:
            self.stats[regime][action] += reward

    def _compute_reward(self, status):

        if status in ["BUY_EXECUTED", "SELL_EXECUTED"]:
            return 1

        return -1

    def get_bias_adjustment(self, regime):

        if regime not in self.stats:
            return {}

        s = self.stats[regime]

        total = sum(abs(v) for v in s.values()) + 1e-9

        return {
            k: v / total for k, v in s.items()
        }