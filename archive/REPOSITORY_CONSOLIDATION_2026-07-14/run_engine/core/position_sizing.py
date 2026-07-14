class PositionSizingEngine:

    def __init__(self):

        self.base_size = 1.0

    def size(self, state, decision, risk):

        equity = state.get("equity", 100.0)

        confidence = decision.get("confidence", 0.5)
        action = decision.get("action", "HOLD")

        exposure = risk.get("exposure", 1.0)

        # no trade if HOLD
        if action == "HOLD":
            return 0.0

        # base scaling from equity
        equity_scale = equity / 100.0

        # confidence scaling (very important)
        confidence_scale = max(0.0, min(1.0, confidence))

        # regime penalty / boost
        regime = state.get("regime", "CHOP")

        if regime == "CHOP":
            regime_scale = 0.5
        elif regime == "TREND":
            regime_scale = 1.2
        elif regime == "VOLATILE":
            regime_scale = 0.3
        else:
            regime_scale = 1.0

        # final position size
        size = (
            self.base_size
            * equity_scale
            * confidence_scale
            * regime_scale
            * exposure
        )

        # clamp
        size = max(0.0, min(1.0, size))

        return size