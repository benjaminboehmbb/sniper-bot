from pricefeed import CSVPriceFeed
from strategies.filters.rsi_filter import RSIFilter
from strategies.filters.ma200_filter import MA200Filter
from strategies.filters.macd_filter import MACDFilter
from strategies.filters.bollinger_filter import BollingerFilter

# === 1. Preisdaten laden ===
feed = CSVPriceFeed("data")
feed.load_data()
df = feed.data

# === 2. Alle Filter vorbereiten ===
rsi_filter = RSIFilter(df, lower=30, upper=70)
ma200_filter = MA200Filter(df)
macd_filter = MACDFilter(df)
bollinger_filter = BollingerFilter(df)

# === 3. Kombinierte Filterprüfung ===
print("Zulässige Zeitpunkte (RSI UND MA200 UND MACD UND Bollinger stimmen überein):")
for i in range(len(df)):
    if (
        rsi_filter.is_allowed(i)
        and ma200_filter.is_allowed(i)
        and macd_filter.is_allowed(i)
        and bollinger_filter.is_allowed(i)
    ):
        timestamp = df.loc[i, "timestamp"]
        close = df.loc[i, "close"]
        print(f"{timestamp} → close={close:.2f}")
