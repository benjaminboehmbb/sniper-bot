import pandas as pd

dateipfad = "C:/btc_data/merged/price_data.csv"

df = pd.read_csv(dateipfad)

indicators = ["RSI", "MA200", "BB_upper", "BB_lower"]

print(f"Lade Daten aus: {dateipfad}\n")

for ind in indicators:
    if ind in df.columns:
        print(f"✔️ Spalte '{ind}' gefunden.")
    else:
        print(f"❌ Spalte '{ind}' fehlt.")
