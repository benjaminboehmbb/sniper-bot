import pandas as pd

class RSIFilter:
    def __init__(self, period=14, threshold=30):
        self.period = period
        self.threshold = threshold
        self.prices = []

    def update(self, candle):
        self.prices.append(candle['close'])
        if len(self.prices) < self.period + 1:
            return None
        return self._calculate_rsi()

    def should_buy(self, candle):
        rsi = self.update(candle)
        return rsi is not None and rsi < self.threshold

    def should_sell(self, candle):
        rsi = self.update(candle)
        return rsi is not None and rsi > 70  # fixe Ausstiegsregel

    def _calculate_rsi(self):
        prices = pd.Series(self.prices[-(self.period + 1):])
        delta = prices.diff().dropna()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.mean()
        avg_loss = loss.mean()
        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
