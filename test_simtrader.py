import pandas as pd
from simtrader_csv_core import SimTrader
import filters

def main():
    # Daten laden (mit Indikatoren)
    df = pd.read_csv("C:/btc_data/merged/price_data.csv")
    
    # Indikatoren müssen vorhanden sein (RSI, MA200, BB_lower etc.)
    # Filterfunktionen
    filter_funcs = [
        filters.rsi_filter,
        filters.ma200_filter,
        filters.bollinger_filter,
        # filters.macd_filter,  # falls MACD Indikatoren vorhanden
    ]
    
    # Gewichtungen zu den Filtern (Summe sollte idealerweise <= 1)
    weights = [0.4, 0.4, 0.2]
    
    # SimTrader initialisieren mit Filter-Signal
    # Wichtig: SimTrader in deiner Version muss `filters` als Liste von (func, weight) akzeptieren
    # Falls noch nicht: kannst du stattdessen einen Wrapper schreiben, der apply_filters aus filters.py aufruft.
    
    # Variante 1: Wir erstellen die Kombi-Signale vorab:
    combined_signal = filters.apply_filters(df, filter_funcs, weights)
    # Füge combined_signal als Spalte in df ein
    df["combined_signal"] = combined_signal
    
    # SimTrader starten
    trader = SimTrader(df)
    trader.run(signal_column="combined_signal")
    
    print(f"Trades gespeichert unter: {trader.export_results()}")
    print(f"Endkapital: ${trader.get_balance():.2f}")

if __name__ == "__main__":
    main()

