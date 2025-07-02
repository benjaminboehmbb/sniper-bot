import pandas as pd
import os

# Pfad zum ersten CSV-Datensatz
file = os.path.join("data", os.listdir("data")[0])  # Passe "data" ggf. an

df = pd.read_csv(file)
print("Spaltenüberschriften:", df.columns.tolist())
