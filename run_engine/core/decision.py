class DecisionEngine:

    def __init__(self):
        pass

    def decide(self, state):

        # USE ONLY REAL PRICE FROM STATE

        price = state.get("price", None)

        if price is None:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "regime": "UNKNOWN"
            }

        # SIMPLE DETERMINISTIC SIGNAL (NO RANDOM)

        if price % 2 == 0:
            action = "BUY"
            confidence = 0.55
        else:
            action = "SELL"
            confidence = 0.55

        return {
            "action": action,
            "confidence": confidence,
            "regime": state.get("regime", "CHOP")
        }