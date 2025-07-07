import pandas as pd
import os

class SimTrader:
    def __init__(self, df, filters=None, initial_balance=10000):
        self.df = df.copy()
        self.filters = filters if filters is not None else []
        self.balance = initial_balance
        self.position = None  # 'LONG' oder None
        self.trades = []

    def run(self):
        # Wende Filter an, erwarte Spalte 'entry_signal' und 'exit_signal' als bool
        for f in self.filters:
            self.df = f(self.df)

        for idx, row in self.df.iterrows():
            if self.position is None and row.get('entry_signal', False):
                # Einstieg Long
                self.position = {
                    'entry_idx': idx,
                    'entry_price': row['close'],
                    'entry_time': row['open_time']
                }
            elif self.position is not None and row.get('exit_signal', False):
                # Ausstieg Long
                entry_price = self.position['entry_price']
                exit_price = row['close']
                profit = (exit_price - entry_price) / entry_price
                self.trades.append({
                    'entry_idx': self.position['entry_idx'],
                    'entry_price': entry_price,
                    'entry_time': self.position['entry_time'],
                    'exit_idx': idx,
                    'exit_price': exit_price,
                    'exit_time': row['open_time'],
                    'profit': profit
                })
                self.balance *= (1 + profit)
                self.position = None

    def export_trades(self, filename='results/trades.csv'):
        if not os.path.exists('results'):
            os.makedirs('results')
        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filename, index=False)
        print(f"✅ {len(self.trades)} Trades gespeichert unter {filename}")

    def get_final_balance(self):
        return self.balance

def sample_entry_exit_signals(df):
    """
    Beispiel-Filter-Funktion:
    Long Entry wenn RSI < 30
    Exit wenn RSI > 70
    (Vorausgesetzt RSI-Spalte ist vorhanden)
    """
    df['entry_signal'] = df['RSI'] < 30
    df['exit_signal'] = df['RSI'] > 70
    return df

def main():
    filepath = 'C:/btc_data/merged/price_data.csv'
    print(f"📥 Lade Kursdaten aus: {filepath}")
    df = pd.read_csv(filepath)

    # Datumsspalte korrekt parsen, auch mit Millisekunden
    df['open_time'] = pd.to_datetime(df['open_time'], errors='coerce')
    if df['open_time'].isnull().any():
        print("⚠️ Warnung: Einige 'open_time'-Werte konnten nicht konvertiert werden.")

    # Beispielindikator (hier müsste vorher 'RSI' berechnet sein)
    if 'RSI' not in df.columns:
        print("⚠️ RSI-Spalte fehlt! Bitte zuerst Indikatoren berechnen.")
        return

    # Beispiel: Nur Zeilen mit gültigem RSI verwenden
    df = df.dropna(subset=['RSI'])

    trader = SimTrader(df, filters=[sample_entry_exit_signals], initial_balance=10000)
    trader.run()
    trader.export_trades()
    final_balance = trader.get_final_balance()
    print(f"📈 Endkapital: ${final_balance:.2f} (Start: $10000.00)")

if __name__ == "__main__":
    main()


