class StrategySelector:

    def __init__(self):

        self.weights = {
            "BUY": 1.0,
            "SELL": 1.0,
            "HOLD": 1.0
        }

        self.last_action = None
        self.cooldown = 0
        self.cooldown_limit = 3

    # ----------------------------

    def select(self, state, regime, position=None):

        base = self._regime_bias(regime)

        scores = {}

        for k in self.weights:
            scores[k] = base[k] * self.weights[k]

        current_pos = position.get("position", "FLAT") if position else "FLAT"

        if current_pos == "LONG":
            scores["BUY"] *= 0.01

        if current_pos == "SHORT":
            scores["SELL"] *= 0.01

        total = sum(scores.values()) + 1e-9

        for k in scores:
            scores[k] /= total

        return scores

    # ----------------------------

    def decide(self, state, regime, weights):

        if self.cooldown > 0:
            self.cooldown -= 1
            return {
                "action": "HOLD",
                "confidence": 1.0,
                "regime": regime
            }

        action = max(weights, key=weights.get)
        confidence = float(weights[action])

        if self.last_action is not None:

            if action != self.last_action:

                if confidence < 0.60:
                    action = self.last_action
                    confidence = weights[action]

        if action != self.last_action:
            self.cooldown = self.cooldown_limit

        self.last_action = action

        return {
            "action": action,
            "confidence": confidence,
            "regime": regime
        }

    # ----------------------------

    def update(self, decision, pnl, regime):

        action = decision["action"]

        if action in ["BUY", "SELL"]:
            self.weights[action] += 0.01
        else:
            self.weights["HOLD"] += 0.005

        for k in self.weights:
            self.weights[k] = max(0.3, self.weights[k])
            self.weights[k] = min(3.0, self.weights[k])

        total = sum(self.weights.values())

        for k in self.weights:
            self.weights[k] /= total

    # ----------------------------

    def _regime_bias(self, regime):

        if regime == "TREND_UP":
            return {"BUY": 1.3, "SELL": 0.7, "HOLD": 1.0}

        if regime == "TREND_DOWN":
            return {"BUY": 0.7, "SELL": 1.3, "HOLD": 1.0}

        if regime == "CHOP":
            return {"BUY": 1.0, "SELL": 1.0, "HOLD": 0.9}

        if regime == "HIGH_VOLATILITY":
            return {"BUY": 0.8, "SELL": 0.8, "HOLD": 1.2}

        return {"BUY": 1.0, "SELL": 1.0, "HOLD": 1.0}