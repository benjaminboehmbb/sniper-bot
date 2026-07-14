class RegimeExecutionGate:

    def __init__(self):

        # harte Trade-Filter pro Regime
        self.rules = {
            "UNKNOWN": {
                "allow_trade": True,
                "max_position_multiplier": 0.5
            },
            "CHOP": {
                "allow_trade": True,
                "max_position_multiplier": 0.3
            },
            "HIGH_VOLATILITY": {
                "allow_trade": True,
                "max_position_multiplier": 0.6
            },
            "TREND_UP": {
                "allow_trade": True,
                "max_position_multiplier": 1.2
            },
            "TREND_DOWN": {
                "allow_trade": True,
                "max_position_multiplier": 1.2
            }
        }

        self.last_block_reason = None

    def evaluate(self, regime: str, base_position_size: float):

        rule = self.rules.get(regime, self.rules["UNKNOWN"])

        if not rule["allow_trade"]:
            self.last_block_reason = regime
            return {
                "allowed": False,
                "position_size": 0.0,
                "reason": "REGIME_BLOCKED"
            }

        adjusted_size = base_position_size * rule["max_position_multiplier"]

        return {
            "allowed": True,
            "position_size": adjusted_size,
            "reason": "OK",
            "regime": regime
        }