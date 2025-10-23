import pandas as pd

class BollingerFilter:
    def __init__(self, df, window=20, num_std=2):
        self.df = df.copy()
        self.window = window
        self.num_std = num_std
        self._calculate_bands()

    def _calculate_bands(self):
        self.df['ma'] = self.df['close'].rolling(window=self.window).mean()
        self.df['std'] = self.df['close'].rolling(window=self.window).std()
        self.df['upper_band'] = self.df['ma'] + (self.df['std'] * self.num_std)
        self.df['lower_band'] = self.df['ma'] - (self.df['std'] * self.num_std)

    def get_signal(self):
        signal = (self.df['close'] > self.df['lower_band']) & (self.df['close'] < self.df['upper_band'])
        return signal.fillna(False)


