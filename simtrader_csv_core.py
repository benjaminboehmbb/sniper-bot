import pandas as pd

class SimTrader:
    def __init__(self, df, initial_balance=10000):
        """
        df: DataFrame mit Kursdaten und Indikatoren (inkl. Signalspalte)
        initial_balance: Startkapital in USD
        """
        self.df = df.copy()
        self.balance = initial_balance
        self.position = 0  # Menge BTC im Bestand
        self.trades = []  # Liste für Trade-Daten
        self.initial_balance = initial_balance

    def run(self, signal_column="combined_signal", threshold_entry=0.7, threshold_exit=0.3):
        """
        signal_column: Name der Spalte mit Signalwerten [0..1]
        threshold_entry: Signal ab dem ein Kauf ausgelöst wird
        threshold_exit: Signal unter dem verkauft wird
        """
        for i, row in self.df.iterrows():
            signal = row.get(signal_column, 0)

            # Kaufbedingung: keine Position, Signal hoch genug
            if self.position == 0 and signal >= threshold_entry:
                # Kaufe BTC mit gesamtem Kapital
                btc_amount = self.balance / row["close"]
                self.position = btc_amount
                self.balance = 0
                self.trades.append({
                    "entry_idx": i,
                    "entry_price": row["close"],
                    "entry_time": row["open_time"],
                    "exit_idx": None,
                    "exit_price": None,
                    "exit_time": None,
                    "profit": None,
                })

            # Verkaufbedingung: Position gehalten, Signal zu schwach
            elif self.position > 0 and signal <= threshold_exit:
                btc_amount = self.position
                sell_price = row["close"]
                self.balance = btc_amount * sell_price
                self.position = 0

                # Trade schließen
                last_trade = self.trades[-1]
                last_trade["exit_idx"] = i
                last_trade["exit_price"] = sell_price
                last_trade["exit_time"] = row["open_time"]
                last_trade["profit"] = (sell_price - last_trade["entry_price"]) / last_trade["entry_price"]

        # Am Ende Position schließen (wenn noch offen)
        if self.position > 0:
            last_row = self.df.iloc[-1]
            sell_price = last_row["close"]
            self.balance = self.position * sell_price
            self.position = 0

            last_trade = self.trades[-1]
            if last_trade["exit_idx"] is None:
                last_trade["exit_idx"] = self.df.index[-1]
                last_trade["exit_price"] = sell_price
                last_trade["exit_time"] = last_row["open_time"]
                last_trade["profit"] = (sell_price - last_trade["entry_price"]) / last_trade["entry_price"]

    def export_results(self, filename="results/trades.csv"):
        df_trades = pd.DataFrame(self.trades)
        df_trades.to_csv(filename, index=False)
        return filename

    def get_balance(self):
        return self.balance

    def get_trade_history(self):
        return pd.DataFrame(self.trades)





