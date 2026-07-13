class RiskEngine:

    def __init__(self):

        self.max_drawdown = 0.2
        self.max_exposure = 1.0
        self.min_exposure = 0.1

    def check(self, state, position, regime):
        position_exposure = position.get("exposure", 0.0)

        equity = state.get("equity", 0.0)

        if equity is None:
            equity = 0.0

        peak_equity = state.get("peak_equity", 0.0)

        if peak_equity is None:
            peak_equity = 0.0

        # drawdown calculation
        drawdown = peak_equity - equity

        # normalize drawdown ratio
        drawdown_ratio = 0.0
        if peak_equity > 0:
            drawdown_ratio = drawdown / peak_equity

        # exposure control
        exposure = self.max_exposure

        if drawdown_ratio > self.max_drawdown:
            exposure = self.min_exposure

        # regime dampening
        if regime == "CHOP":
            exposure *= 0.7

        if regime == "TREND":
            exposure *= 1.0

        if regime == "VOLATILE":
            exposure *= 0.5

        # clamp
        exposure = max(self.min_exposure, min(self.max_exposure, exposure))

        return {
            "equity": equity,
            "peak_equity": peak_equity,
            "drawdown": drawdown,
            "drawdown_ratio": drawdown_ratio,
            "exposure": exposure
        }