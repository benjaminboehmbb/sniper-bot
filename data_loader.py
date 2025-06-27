import pandas as pd
import os

def load_combined_data(folder="data", pattern="BTCUSDT-5m-*.csv", datetime_col='timestamp', time_format='ms'):
    import glob

    all_files = glob.glob(os.path.join(folder, pattern))
    if not all_files:
        raise FileNotFoundError(f"Keine CSV-Dateien im Ordner {folder} mit Pattern '{pattern}' gefunden.")

    dfs = []
    for file in all_files:
        df = pd.read_csv(file, header=None)
        df.columns = [
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
        ]

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        dfs.append(df[['timestamp', 'open', 'high', 'low', 'close', 'volume']])  # nur relevante Spalten

    combined = pd.concat(dfs)
    combined = combined.sort_values(by='timestamp').reset_index(drop=True)
    return combined
