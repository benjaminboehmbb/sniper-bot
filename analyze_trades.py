# analyze_trades.py
import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "strategy_results.csv"  # Dateiname ggf. anpassen

# CSV einlesen (ohne parse_dates)
df = pd.read_csv(CSV_PATH)

# Spaltennamen bereinigen (Whitespace entfernen)
df.columns = [c.strip() for c in df.columns]

# Grundlegende Statistik anzeigen
print("\nStatistische Auswertung der Strategien:")
print(df.describe())

# Beste und schlechteste Strategie anzeigen
best = df.loc[df["Endkapital ($)"].idxmax()]
worst = df.loc[df["Endkapital ($)"].idxmin()]

print("\nBeste Strategie:")
print(best)

print("\nSchlechteste Strategie:")
print(worst)

# Visualisierung: Endkapital je Filter-Kombination
plt.figure(figsize=(12, 6))
df_sorted = df.sort_values("Endkapital ($)", ascending=True)
plt.barh(df_sorted["Filter-Kombination"], df_sorted["Endkapital ($)"])
plt.xlabel("Endkapital ($)")
plt.title("Strategie-Ergebnis je Filter-Kombination")
plt.tight_layout()
plt.show()

