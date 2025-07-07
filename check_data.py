import pandas as pd

def main():
    # Datei laden
    filepath = "C:/btc_data/merged/price_data.csv"
    print(f"Lade Daten aus: {filepath}")
    df = pd.read_csv(filepath)
    
    # Überblick über Daten
    print("\n--- Übersicht der Spalten ---")
    print(df.columns.tolist())
    
    print("\n--- Datentypen der Spalten ---")
    print(df.dtypes)
    
    print("\n--- Erste 5 Zeilen ---")
    print(df.head())
    
    print("\n--- Fehlende Werte je Spalte ---")
    print(df.isnull().sum())
    
    # Prüfen, ob Zeitspalte vorhanden ist und Datentyp konvertieren
    if "open_time" in df.columns:
        print("\nKonvertiere 'open_time' in datetime...")
        df["open_time"] = pd.to_datetime(df["open_time"], errors="coerce")
        print(df["open_time"].head())
    else:
        print("Spalte 'open_time' nicht gefunden!")

if __name__ == "__main__":
    main()
