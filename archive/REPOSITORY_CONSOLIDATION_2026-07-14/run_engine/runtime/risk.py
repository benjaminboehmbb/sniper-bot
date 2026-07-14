class RiskLayer:

    def __init__(self):

        self.max_exposure = 3.0
        self.current_exposure = 0.0

        self.max_drawdown = 50.0
        self.peak_equity = 100.0
        self.equity = 100.0

    def update_equity(self, pnl):

        self.equity += pnl

        if self.equity > self.peak_equity:
            self.peak_equity = self.equity

    def drawdown(self):

        return self.peak_equity - self.equity

    def allow_trade(self, position_size):

        if self.drawdown() > self.max_drawdown:
            return False

        return True

    def apply_trade(self, position_size):

        self.current_exposure += position_size

        if self.current_exposure > self.max_exposure:
            self.current_exposure = self.max_exposure

    def release_exposure(self, position_size):

        self.current_exposure -= position_size

        if self.current_exposure < 0:
            self.current_exposure = 0

    def get_state(self):

        return {
            "equity": self.equity,
            "peak_equity": self.peak_equity,
            "drawdown": self.drawdown(),
            "exposure": self.current_exposure
        }