import pandas as pd

class MA200Filter:
    def __init__(self, df):
        self.df = df.copy()
        self.ma200 = self.df['close'].rolling(window=200).mean()

    def get_signal(self):
        signal = self.df['close'] > self.ma200
        return signal.fillna(False)


