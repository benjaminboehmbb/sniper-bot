class StrategySelector:

    def __init__(self):
        self.last_weights = {
            "BUY": 1.0,
            "SELL": 1.0,
            "HOLD": 1.0
        }

    def select_weights(self, regime: str):
        if regime == "TREND_UP":
            weights = {"BUY": 1.2, "SELL": 0.8, "HOLD": 1.0}
        elif regime == "TREND_DOWN":
            weights = {"BUY": 0.8, "SELL": 1.2, "HOLD": 1.0}
        elif regime == "CHOP":
            weights = {"BUY": 0.9, "SELL": 0.9, "HOLD": 1.2}
        elif regime == "HIGH_VOLATILITY":
            weights = {"BUY": 0.7, "SELL": 0.7, "HOLD": 1.6}
        else:
            weights = {"BUY": 1.0, "SELL": 1.0, "HOLD": 1.0}

        self.last_weights = weights
        return weights

    # WICHTIG: das ist der missing link
    def apply(self, decision: dict, regime: str):
        weights = self.select_weights(regime)

        bias = decision.get("bias", {"BUY": 0.33, "SELL": 0.33, "HOLD": 0.34})

        # simple policy modulation
        adjusted = {
            k: bias.get(k, 0.33) * weights.get(k, 1.0)
            for k in ["BUY", "SELL", "HOLD"]
        }

        total = sum(adjusted.values()) or 1.0
        normalized = {k: v / total for k, v in adjusted.items()}

        decision["bias"] = normalized
        decision["strategy_weights"] = weights

        return decision