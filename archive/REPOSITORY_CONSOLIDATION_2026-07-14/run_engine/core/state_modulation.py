import random

class StateModulator:

    def __init__(self):
        self.base_bias = {
            "BUY": 0.33,
            "SELL": 0.33,
            "HOLD": 0.34
        }

    def analyze(self, state):

        market = state.get("market", "unknown")

        # simple synthetic market signal (placeholder)
        volatility = random.random()
        trend = random.random()

        return {
            "volatility": volatility,
            "trend": trend
        }

    def modulate(self, state, base_bias):

        signals = self.analyze(state)

        trend = signals["trend"]
        volatility = signals["volatility"]

        bias = base_bias.copy()

        # Trend effect
        if trend > 0.6:
            bias["BUY"] += 0.2
            bias["SELL"] -= 0.1

        elif trend < 0.4:
            bias["SELL"] += 0.2
            bias["BUY"] -= 0.1

        # Volatility effect
        if volatility > 0.7:
            bias["HOLD"] += 0.2

        # normalize
        total = sum(bias.values())
        for k in bias:
            bias[k] = max(0.01, bias[k] / total)

        return bias