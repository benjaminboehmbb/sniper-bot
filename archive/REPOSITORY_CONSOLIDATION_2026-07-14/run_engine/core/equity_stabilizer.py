import math


class EquityStabilizer:

    def __init__(self):

        self.alpha = 0.05          # smoothing factor
        self.vol_window = []
        self.max_window = 100

        self.smoothed_return = 0.0
        self.last_equity = 100.0

    def update(self, equity, raw_pnl):

        if equity is None:
            equity = self.last_equity

        # raw return
        if self.last_equity != 0:
            raw_return = raw_pnl / self.last_equity
        else:
            raw_return = 0.0

        # update volatility window
        self.vol_window.append(raw_return)

        if len(self.vol_window) > self.max_window:
            self.vol_window.pop(0)

        # compute volatility
        vol = self._std(self.vol_window)

        # avoid division by zero
        vol = max(vol, 1e-6)

        # normalized return (vol-adjusted)
        normalized_return = raw_return / vol

        # exponential smoothing
        self.smoothed_return = (
            self.alpha * normalized_return +
            (1 - self.alpha) * self.smoothed_return
        )

        # stabilized equity update
        stabilized_equity = self.last_equity * (1.0 + self.smoothed_return)

        # safety clamp (prevents runaway explosion)
        max_step = 0.02  # max 2% per tick

        step_return = (stabilized_equity - self.last_equity) / self.last_equity
        step_return = max(-max_step, min(max_step, step_return))

        stabilized_equity = self.last_equity * (1.0 + step_return)

        self.last_equity = stabilized_equity

        return stabilized_equity

    def _std(self, values):

        if len(values) < 2:
            return 1.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)

        return math.sqrt(variance)