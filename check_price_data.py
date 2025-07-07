import pandas as pd

FILE_PATH = "C:/btc_data/merged/price_data.csv"

def main():
    print(f"Lade Daten aus: {FILE_PATH}")
    df = pd.read_csv(FILE_PATH)

    print("\nSpalten:")
    print(df.columns.tolist())

    print("\nErste 5 Zeilen:")
    print(df.head())

    print("\nLetzte 5 Zeilen:")
    print(df.tail())

    print("\nDatentypen:")
    print(df.dtypes)

    print("\nAnzahl Zeilen:", len(df))

    # Check auf fehlende Werte
    missing = df.isnull().sum()
    print("\nFehlende Werte je Spalte:")
    print(missing[missing > 0])

    # Prüfe auf Duplikate bzgl. Zeitstempel
    if "open_time" in df.columns:
        duplicates = df.duplicated(subset=["open_time"]).sum()
        print(f"\nAnzahl doppelter Zeitstempel: {duplicates}")

    # Check auf Zeitstempel-Reihenfolge
    if "open_time" in df.columns:
        if not df["open_time"].is_monotonic_increasing:
            print("\nWarnung: Zeitstempel sind nicht streng aufsteigend sortiert!")
        else:
            print("\nZeitstempel sind korrekt sortiert.")

if __name__ == "__main__":
    main()
