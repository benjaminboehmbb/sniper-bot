from pricefeed import CSVPriceFeed

# Ordnerpfad zu deinen CSV-Dateien (anpassen falls nötig)
feed = CSVPriceFeed("data/")
feed.load_data()

# Zeige jede Kerze (z. B. Timestamp und Schlusskurs)
while True:
    candle = feed.get_next()
    if candle is None:
        break
    print(candle['timestamp'], candle['close'])
