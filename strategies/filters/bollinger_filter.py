import pandas as pd

class BollingerFilter:
    def __init__(self, period=20, std_dev=2):
        self.period = period
        self.std_dev = std_dev
        self.closes = []

    def update(self, candle):
        self.closes.append(candle['close'])

    def should_buy(self, candle):
        self.update(candle)
        if len(self.closes) < self.period:
            return False
        series = pd.Series(self.closes[-self.period:])
        lower_band = series.mean() - self.std_dev * series.std()
        return candle['close'] <= lower_band
