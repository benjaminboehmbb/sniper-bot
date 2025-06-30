from pricefeed import CSVPriceFeed

def main():
    try:
        print("🔍 Lade Feed...")
        feed = CSVPriceFeed(
            folder_path="data",
            pattern="BTCUSDT-5m-SINGLE.csv",  # oder BTCUSDT-5m-MERGED.csv, wenn du nur 1 Datei nutzen willst
            datetime_col='timestamp',
            time_format='ms'
        )

        print("✅ Feed geladen. Zeige erste 5 Kerzen:")
        for _ in range(5):
            candle = feed.get_next_candle()
            if candle:
                print(f"{candle['timestamp']} | Open: {candle['open']} | High: {candle['high']} | Low: {candle['low']} | Close: {candle['close']} | Volume: {candle['volume']}")
            else:
                print("❌ Weniger als 5 Kerzen verfügbar.")
                break

    except Exception as e:
        print(f"❌ Fehler beim Laden oder Lesen des Feeds:\n{e}")

if __name__ == "__main__":
    main()
