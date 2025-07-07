import pandas as pd

def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # RSI
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # MA200
    df['MA200'] = df['close'].rolling(window=200).mean()

    # Bollinger Bands
    ma20 = df['close'].rolling(window=20).mean()
    std20 = df['close'].rolling(window=20).std()
    df['BB_upper'] = ma20 + (2 * std20)
    df['BB_lower'] = ma20 - (2 * std20)

    return df


