from pricefeed import CSVPriceFeed
from sim_trader import SimTrader

# Filter importieren
from strategies.filters.rsi_filter import RSIFilter
from strategies.filters.ma200_filter import MA200Filter
from strategies.filters.bollinger_filter import BollingerFilter
from strategies.combined_strategy import CombinedStrategy

# Feed laden
feed = CSVPriceFeed("data/BTCUSDT_5min_clean.csv", datetime_col='timestamp', time_format='ms')

# Filter definieren
rsi = RSIFilter(period=14, threshold=30)
ma200 = MA200Filter()
bb = BollingerFilter()

# Kombinierte Strategie
strategy = CombinedStrategy(filters=[rsi, ma200, bb])

# Trader starten
trader = SimTrader(price_feed=feed, strategy=strategy)
trader.run()

# Ergebnisse anzeigen
trades = trader.get_trades()
for t in trades:
    print(f"{t['entry_time']} → {t['exit_time']} | Buy: {t['entry_price']} → Sell: {t['exit_price']} | PnL: {t['pnl']:.2f}")
print(f"\nFinaler Kontostand: {trader.get_balance():.2f} USDT")
