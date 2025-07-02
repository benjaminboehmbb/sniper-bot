import pandas as pd
from filters import rsi_filter, macd_filter, ma200_filter, bollinger_filter

class SimTrader:
    def __init__(self, df, filters):
        self.df = df.copy()
        self.initial_balance = 10000
        self.balance = self.initial_balance
        self.position = None
        self.entry_price = None
        self.trades = []
        
        # Mapping von Filternamen (Strings) auf Funktionen aus filters.py
        filter_map = {
            "RSI": rsi_filter,
            "MACD": macd_filter,
            "MA200": ma200_filter,
            "Bollinger": bollinger_filter,
        }
        
        # Ersetze String-Namen durch Filterfunktionen
        self.filters = [filter_map[f] for f in filters]

    def _apply_filters(self, df):
        for f in self.filters:
            df = f(df)
        return df

    def run(self):
        df = self._apply_filters(self.df)
        for i, row in df.iterrows():
            if self.position is None and row.get("entry_signal"):
                self.position = "LONG"
                self.entry_price = row["close"]
                self.entry_time = row["timestamp"]
            elif self.position == "LONG" and row.get("exit_signal"):
                exit_price = row["close"]
                profit = (exit_price - self.entry_price) / self.entry_price * self.balance
                self.balance += profit
                self.trades.append({
                    "entry_time": self.entry_time,
                    "exit_time": row["timestamp"],
                    "entry_price": self.entry_price,
                    "exit_price": exit_price,
                    "profit": profit
                })
                self.position = None
                self.entry_price = None

    def get_trade_history(self):
        return self.trades

    def get_total_return(self):
        return (self.balance - self.initial_balance) / self.initial_balance * 100
