import pandas as pd

# Pfad zu deiner CSV-Datei
dateipfad = "C:/btc_data/merged/price_data.csv"

# CSV einlesen, open_time direkt als datetime interpretieren
df = pd.read_csv(dateipfad, parse_dates=["open_time"])

# Ausgabe der ersten 5 Werte aus 'open_time'
print("Erste 5 Werte in open_time:")
print(df["open_time"].head())

# Prüfen, ob es fehlgeschlagene Konvertierungen gibt
fehlerhafte_zeiten = df[df["open_time"].isna()]
print(f"Anzahl fehlerhafte open_time-Werte: {len(fehlerhafte_zeiten)}")
if len(fehlerhafte_zeiten) > 0:
    print("Fehlerhafte Zeitwerte gefunden:")
    print(fehlerhafte_zeiten)
else:
    print("Alle open_time-Werte wurden korrekt konvertiert.")
