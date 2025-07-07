import os
import requests
import zipfile
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = "C:/btc_data"
ZIP_DIR = os.path.join(DATA_DIR, "zips")
UNZIPPED_DIR = os.path.join(DATA_DIR, "unzipped")
INVALID_DIR = os.path.join(UNZIPPED_DIR, "invalid")
MERGED_FILE = os.path.join(DATA_DIR, "merged", "price_data.csv")

BASE_URL = "https://data.binance.vision/data/spot/monthly/klines/BTCUSDT/5m"

START_YEAR = 2017
START_MONTH = 8

END_YEAR = datetime.utcnow().year
END_MONTH = datetime.utcnow().month

def ensure_dirs():
    for d in [ZIP_DIR, UNZIPPED_DIR, INVALID_DIR, os.path.dirname(MERGED_FILE)]:
        os.makedirs(d, exist_ok=True)

def download_zip(year, month):
    filename = f"BTCUSDT-5m-{year}-{month:02d}.zip"
    url = f"{BASE_URL}/{year}-{month:02d}/{filename}"
    local_path = os.path.join(ZIP_DIR, filename)
    if os.path.exists(local_path):
        print(f"⬇️ Überspringe vorhandene Datei: {filename}")
        return True
    print(f"⬇️ Lade: {filename} ...")
    r = requests.get(url)
    if r.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(r.content)
        print(f"✅ Erfolgreich geladen: {filename}")
        return True
    else:
        print(f"❌ Nicht gefunden (Status {r.status_code}): {filename}")
        return False

def unzip_all():
    for file in os.listdir(ZIP_DIR):
        if file.endswith(".zip"):
            zip_path = os.path.join(ZIP_DIR, file)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(UNZIPPED_DIR)
            print(f"📦 Entpackt: {file}")

def validate_csv_files():
    print("Validiere CSV-Dateien...")
    valid_files = []
    for f in os.listdir(UNZIPPED_DIR):
        if not f.endswith(".csv"):
            continue
        if f == "invalid":
            continue
        file_path = os.path.join(UNZIPPED_DIR, f)
        try:
            df = pd.read_csv(file_path, header=None)
            # Binance CSV Format: open_time in ms in Spalte 0
            ts = df.iloc[0, 0]
            # Prüfe, ob Timestamp vernünftig (Unix Timestamp in ms, plausibler Bereich)
            if ts < 1000000000000 or ts > 1700000000000:  # ca. Jahre 2001 bis 2023+
                raise ValueError(f"Ungültiger Timestamp {ts}")
            valid_files.append(file_path)
        except Exception as e:
            print(f"⚠️ Datei {f} ist ungültig: {e}")
            # Verschiebe in invalid, lösche vorher, falls vorhanden
            dest_path = os.path.join(INVALID_DIR, f)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            os.rename(file_path, dest_path)
    return valid_files

def merge_csv_files():
    print("Führe CSV-Dateien zusammen...")
    all_files = [os.path.join(UNZIPPED_DIR, f) for f in os.listdir(UNZIPPED_DIR) if f.endswith(".csv")]
    df_list = []
    for file in all_files:
        try:
            df = pd.read_csv(file, header=None)
            df_list.append(df)
        except Exception as e:
            print(f"Fehler beim Lesen von {file}: {e}")
    if not df_list:
        print("Keine gültigen CSV-Dateien zum Zusammenführen gefunden!")
        return
    df_all = pd.concat(df_list, ignore_index=True)
    # Spalten benennen (Binance Klines)
    df_all.columns = ["open_time", "open", "high", "low", "close", "volume",
                      "close_time", "quote_asset_volume", "number_of_trades",
                      "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"]
    # Timestamp in datetime
    df_all["open_time"] = pd.to_datetime(df_all["open_time"], unit='ms', errors='coerce')
    df_all.dropna(subset=["open_time"], inplace=True)
    df_all.to_csv(MERGED_FILE, index=False)
    print(f"📦 Zusammengeführt: {len(df_all)} Zeilen → {MERGED_FILE}")

def main():
    ensure_dirs()
    # Download monatliche Daten von START bis jetzt
    current_year, current_month = START_YEAR, START_MONTH
    while (current_year < END_YEAR) or (current_year == END_YEAR and current_month <= END_MONTH):
        download_zip(current_year, current_month)
        # Increment month
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1
    unzip_all()
    valid_files = validate_csv_files()
    if not valid_files:
        print("Keine gültigen Dateien nach Validierung!")
        return
    merge_csv_files()
    print("Fertig.")

if __name__ == "__main__":
    main()
