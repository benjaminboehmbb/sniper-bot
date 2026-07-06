class RiskEngine:

    def __init__(self):

        self.max_drawdown = 0.2
        self.max_exposure = 1.0
        self.min_exposure = 0.1

        self.last_equity = 100.0
        self.peak_equity = 100.0

    def check(self, state, position, regime):

        equity = state.get("equity", self.last_equity)

        if equity is None:
            equity = self.last_equity

        # update peak
        if equity > self.peak_equity:
            self.peak_equity = equity

        # drawdown calculation
        drawdown = self.peak_equity - equity

        # normalize drawdown ratio
        drawdown_ratio = 0.0
        if self.peak_equity > 0:
            drawdown_ratio = drawdown / self.peak_equity

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

        self.last_equity = equity

        return {
            "equity": equity,
            "peak_equity": self.peak_equity,
            "drawdown": drawdown,
            "drawdown_ratio": drawdown_ratio,
            "exposure": exposure
        }