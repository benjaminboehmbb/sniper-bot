import pandas as pd

class RSIFilter:
    def __init__(self, df, period=14, lower=30, upper=70):
        self.df = df.copy()
        self.period = period
        self.lower = lower
        self.upper = upper
        self.rsi = self.compute_rsi()

    def compute_rsi(self):
        delta = self.df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=self.period).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=self.period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def get_signal(self):
        signal = (self.rsi > self.lower) & (self.rsi < self.upper)
        return signal.fillna(False)


