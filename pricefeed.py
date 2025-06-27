import pandas as pd

class CSVPriceFeed:
    def __init__(self, file_path=None, folder_path=None, pattern=None, datetime_col='timestamp', time_format='ms', df=None):
        if df is not None:
            self.df = df.copy()
        elif file_path:
            self.df = pd.read_csv(file_path)
            if datetime_col not in self.df.columns:
                raise ValueError(f"{file_path} enthält keine Spalte '{datetime_col}'.")
            self.df[datetime_col] = pd.to_datetime(self.df[datetime_col], unit=time_format)
        elif folder_path and pattern:
            import os, glob
            files = sorted(glob.glob(os.path.join(folder_path, pattern)))
            if not files:
                raise FileNotFoundError(f"Keine Dateien unter {folder_path} mit Pattern {pattern}")
            all_dfs = []
            for f in files:
                df_f = pd.read_csv(f, header=None)
                df_f.columns = [
                    'timestamp', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
                ]
                df_f['timestamp'] = pd.to_datetime(df_f['timestamp'], unit='ms')
                all_dfs.append(df_f[['timestamp', 'open', 'high', 'low', 'close', 'volume']])
            self.df = pd.concat(all_dfs).sort_values('timestamp').reset_index(drop=True)
        else:
            raise ValueError("Bitte entweder 'df', 'file_path' oder ('folder_path' + 'pattern') angeben.")

        self.df = self.df.sort_values('timestamp').reset_index(drop=True)
        self.data = self.df  # Alias für Kompatibilität
        self.pointer = 0

    def get_next_candle(self):
        if self.pointer < len(self.df):
            row = self.df.iloc[self.pointer]
            self.pointer += 1
            return {
                'timestamp': row['timestamp'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']),
            }
        else:
            return None

    def get_next(self):
        return self.get_next_candle()

    def has_next(self):
        return self.pointer < len(self.df)

    def reset(self):
        self.pointer = 0
