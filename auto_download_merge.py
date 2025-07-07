import os
import requests
import zipfile
import pandas as pd
from datetime import datetime

# Ordnerstruktur anpassen
BASE_DIR = "C:/btc_data"
RAW_DIR = os.path.join(BASE_DIR, "raw")         # Rohdaten ZIP
UNZIP_DIR = os.path.join(BASE_DIR, "unzipped")  # Entpackte CSVs
MERGED_DIR = os.path.join(BASE_DIR, "merged")   # Zusammengeführt

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(UNZIP_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)

START_DATE = datetime(2017, 8, 1)
END_DATE = datetime.now()

SYMBOL = "BTCUSDT"
INTERVAL = "5m"

BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"

def month_year_iter(start_month, start_year, end_month, end_year):
    ym_start = 12*start_year + start_month - 1
    ym_end = 12*end_year + end_month - 1
    for ym in range(ym_start, ym_end + 1):
        y, m = divmod(ym, 12)
        yield y, m + 1

def download_zip_for_month(year, month):
    filename = f"{SYMBOL}-{INTERVAL}-{year}-{month:02d}.zip"
    url = f"{BASE_URL}/{SYMBOL}/{INTERVAL}/{filename}"
    local_path = os.path.join(RAW_DIR, filename)

    if os.path.exists(local_path):
        print(f"✅ Bereits vorhanden: {filename}")
        return local_path

    print(f"⬇️ Lade: {filename} ...")
    resp = requests.get(url)
    if resp.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(resp.content)
        print(f"✅ Erfolgreich geladen: {filename}")
        return local_path
    else:
        print(f"❌ Nicht gefunden (Status {resp.status_code}): {filename}")
        return None

def unzip_file(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(UNZIP_DIR)

def merge_csv_files():
    all_files = [os.path.join(UNZIP_DIR, f) for f in os.listdir(UNZIP_DIR) if f.endswith(".csv")]
    dfs = []
    for file in all_files:
        try:
            df = pd.read_csv(file, header=None)
            dfs.append(df)
        except Exception as e:
            print(f"⚠️ Fehler beim Einlesen {file}: {e}")
    if not dfs:
        print("Keine CSV-Dateien zum Zusammenführen gefunden.")
        return
    df_all = pd.concat(dfs, ignore_index=True)
    # Spalten benennen entsprechend Binance Klines
    df_all.columns = [
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_base", "taker_buy_quote", "ignore"
    ]
    # Timestamp in datetime umwandeln (open_time ms)
    df_all["open_time"] = pd.to_datetime(df_all["open_time"], unit="ms")
    df_all.sort_values("open_time", inplace=True)
    merged_path = os.path.join(MERGED_DIR, "price_data.csv")
    df_all.to_csv(merged_path, index=False)
    print(f"📦 Zusammengeführt: {len(df_all)} Zeilen → {merged_path}")

def main():
    print(f"Starte Download und Verarbeitung von {SYMBOL} {INTERVAL} Daten...")

    for year, month in month_year_iter(START_DATE.month, START_DATE.year, END_DATE.month, END_DATE.year):
        zip_path = download_zip_for_month(year, month)
        if zip_path:
            unzip_file(zip_path)

    merge_csv_files()
    print("Fertig.")

if __name__ == "__main__":
    main()
