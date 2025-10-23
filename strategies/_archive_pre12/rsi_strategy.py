import pandas as pd

class RSIStrategy:
    """
    Einfache RSI-basierte Strategie:
    - Kaufe, wenn RSI < 30
    - Verkaufe, wenn RSI > 70
    """

    def __init__(self, period=14):
        self.period = period
        self.prices = []

    def generate_signal(self, candle):
        close = candle['close']
        self.prices.append(close)

        if len(self.prices) < self.period + 1:
            return None  # nicht genug Daten

        rsi = self._calculate_rsi()

        if rsi < 30:
            return 'buy'
        elif rsi > 70:
            return 'sell'
        else:
            return None

    def _calculate_rsi(self):
        prices = pd.Series(self.prices[-(self.period+1):])
        delta = prices.diff().dropna()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.mean()
        avg_loss = loss.mean()

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
