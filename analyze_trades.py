import pandas as pd

def main():
    filename = 'results/trades.csv'
    print(f"Lade Daten aus: {filename}")

    # Zuerst ohne parse_dates laden, um Spaltennamen zu prüfen
    df = pd.read_csv(filename)
    print("\nSpaltennamen in trades.csv:", df.columns.tolist())

    # Prüfen, ob die erwarteten Zeit-Spalten existieren und diese dann konvertieren
    time_cols = []
    for col in ['entry_time', 'exit_time']:
        if col in df.columns:
            time_cols.append(col)

    if time_cols:
        df = pd.read_csv(filename, parse_dates=time_cols)
    else:
        print("Warnung: Zeit-Spalten 'entry_time' und/oder 'exit_time' nicht gefunden!")

    print("\nErste 5 Zeilen der Daten:")
    print(df.head())

    print("\nStatistische Übersicht:")
    print(f"Anzahl Trades: {len(df)}")
    if 'profit' in df.columns:
        wins = df[df['profit'] > 0]
        losses = df[df['profit'] <= 0]
        print(f"Gewinn-Trades: {len(wins)}")
        print(f"Verlust-Trades: {len(losses)}")
        print(f"Durchschnittlicher Profit pro Trade: {df['profit'].mean():.4f}")
    else:
        print("Spalte 'profit' nicht gefunden, keine Gewinn/Verlust-Statistik möglich.")

if __name__ == "__main__":
    main()



