# indicators.py
import pandas as pd

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["ma200"] = df["close"].rolling(window=200).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()

    # Bollinger Bands
    sma20 = df["close"].rolling(window=20).mean()
    std20 = df["close"].rolling(window=20).std()
    df["bb_upper"] = sma20 + (2 * std20)
    df["bb_lower"] = sma20 - (2 * std20)

    return df


