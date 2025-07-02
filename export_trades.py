import pandas as pd
import matplotlib.pyplot as plt
from sim_trader import SimTrader
from pricefeed import CSVPriceFeed
from strategies.filters import RSIFilter

# === Konfiguration ===
data_path = "data"  # ACHTUNG: Nur Ordnername, keine einzelne Datei!
initial_capital = 10000
fee = 0.001
slippage = 0.0005

# === Daten laden ===
feed = CSVPriceFeed(data_path)
feed.load_data()
df = feed.data

# === Filter & Trader initialisieren ===
rsi_filter = RSIFilter(df)
signals = rsi_filter.get_signal()

trader = SimTrader(initial_balance=initial_capital, fee=fee, slippage=slippage)

# === Handelssimulation ===
for i in range(len(df)):
    candle = df.iloc[i]
    if signals[i]:
        trader.buy(candle)
    elif trader.position:
        trader.close_position(candle)

# === Trade-Historie exportieren ===
trades = pd.DataFrame(trader.get_history())
trades['timestamp'] = pd.to_datetime(trades['timestamp'], unit='ms')
csv_path = "trade_history.csv"
trades.to_csv(csv_path, index=False)
print(f"✅ Trade-Historie gespeichert als: {csv_path}")

# === Diagramm 1: Kontostand über Zeit ===
plt.figure(figsize=(10, 5))
plt.plot(trades['timestamp'], trades['balance'], label='Kontostand')
plt.title('Kontostand über Zeit')
plt.xlabel('Zeit')
plt.ylabel('USD')
plt.grid(True)
plt.tight_layout()
plt.show()

# === Diagramm 2: Aktionen zählen ===
plt.figure(figsize=(6, 4))
action_counts = trades['action'].value_counts()
action_counts.plot(kind='bar')
plt.title('Anzahl Trades nach Aktionstyp')
plt.xlabel('Aktion')
plt.ylabel('Anzahl')
plt.grid(True)
plt.tight_layout()
plt.show()
