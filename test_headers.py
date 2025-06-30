import pandas as pd

df = pd.read_csv("data/BTCUSDT-5m-SINGLE.csv")
print("Spaltenüberschriften:", list(df.columns))
print("Erste Zeile:")
print(df.iloc[0])
