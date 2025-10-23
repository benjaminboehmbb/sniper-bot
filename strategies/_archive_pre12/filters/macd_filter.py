import pandas as pd

class MACDFilter:
    def __init__(self, df, short_window=12, long_window=26, signal_window=9):
        self.df = df.copy()
        self.short_window = short_window
        self.long_window = long_window
        self.signal_window = signal_window
        self._calculate_macd()

    def _calculate_macd(self):
        self.df['ema_short'] = self.df['close'].ewm(span=self.short_window, adjust=False).mean()
        self.df['ema_long'] = self.df['close'].ewm(span=self.long_window, adjust=False).mean()
        self.df['macd'] = self.df['ema_short'] - self.df['ema_long']
        self.df['signal_line'] = self.df['macd'].ewm(span=self.signal_window, adjust=False).mean()

    def get_signal(self):
        signal = self.df['macd'] > self.df['signal_line']
        return signal.fillna(False)


