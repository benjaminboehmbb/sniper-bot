class StrategyWeightEvolution:

    def __init__(self):

        self.weights = {
            "TREND_UP": {
                "BUY": 1.0,
                "SELL": 1.0,
                "HOLD": 1.0
            },
            "TREND_DOWN": {
                "BUY": 1.0,
                "SELL": 1.0,
                "HOLD": 1.0
            },
            "CHOP": {
                "BUY": 1.0,
                "SELL": 1.0,
                "HOLD": 1.0
            },
            "HIGH_VOLATILITY": {
                "BUY": 1.0,
                "SELL": 1.0,
                "HOLD": 1.0
            }
        }

    def update(self, regime, action, reward):

        if regime not in self.weights:
            return

        if action not in self.weights[regime]:
            return

        # multiplicative update (stable learning signal)
        lr = 0.05

        if reward > 0:
            self.weights[regime][action] *= (1 + lr)
        else:
            self.weights[regime][action] *= (1 - lr)

    def get_weights(self, regime):

        return self.weights.get(regime, {
            "BUY": 1.0,
            "SELL": 1.0,
            "HOLD": 1.0
        })