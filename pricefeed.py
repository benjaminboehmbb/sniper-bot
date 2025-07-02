import os
import pandas as pd
from datetime import datetime

class CSVPriceFeed:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.data = None
        self.index = 0

    def load_data(self):
        all_files = sorted([
            os.path.join(self.folder_path, f)
            for f in os.listdir(self.folder_path)
            if f.endswith(".csv")
        ])

        df_list = []
        for file in all_files:
            df = pd.read_csv(file, header=None)

            # Binance 5min-Kline-Struktur: [0] open time, [1] open, [2] high, [3] low, [4] close, [5] volume, ...
            df.columns = [
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ]

            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df_list.append(df)

        self.data = pd.concat(df_list, ignore_index=True)

        # Umwandeln von timestamp in datetime
        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'], unit='ms')
        self.data = self.data.sort_values('timestamp').reset_index(drop=True)

    def get_next(self):
        if self.index >= len(self.data):
            return None
        row = self.data.iloc[self.index]
        self.index += 1
        return row

    def reset(self):
        self.index = 0
