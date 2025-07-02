import pandas as pd
import numpy as np

def rsi_filter(df, period=14, lower=30, upper=70):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['rsi'] = rsi

    df['entry_signal'] = df['rsi'] < lower
    df['exit_signal'] = df['rsi'] > upper
    return df

def macd_filter(df, fast=12, slow=26, signal=9):
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    df['macd'] = macd
    df['signal_line'] = signal_line

    df['entry_signal'] = (macd > signal_line) & (macd.shift(1) <= signal_line.shift(1))
    df['exit_signal'] = (macd < signal_line) & (macd.shift(1) >= signal_line.shift(1))
    return df

def ma200_filter(df):
    df['ma200'] = df['close'].rolling(window=200).mean()

    df['entry_signal'] = df['close'] > df['ma200']
    df['exit_signal'] = df['close'] < df['ma200']
    return df

def bollinger_filter(df, window=20, std_dev=2):
    rolling_mean = df['close'].rolling(window).mean()
    rolling_std = df['close'].rolling(window).std()
    df['bollinger_upper'] = rolling_mean + std_dev * rolling_std
    df['bollinger_lower'] = rolling_mean - std_dev * rolling_std

    df['entry_signal'] = df['close'] > df['bollinger_upper']
    df['exit_signal'] = df['close'] < df['bollinger_lower']
    return df

def apply_filters(df, filters):
    """
    Wendet mehrere Filter nacheinander an und kombiniert die Entry- und Exit-Signale logisch (AND).
    """
    df = df.copy()
    df['entry_signal'] = True
    df['exit_signal'] = True

    filter_map = {
        "RSI": rsi_filter,
        "MACD": macd_filter,
        "MA200": ma200_filter,
        "Bollinger": bollinger_filter,
    }

    for f in filters:
        df = filter_map[f](df)
        df['entry_signal'] = df['entry_signal'] & df['entry_signal']
        df['exit_signal'] = df['exit_signal'] & df['exit_signal']

    return df


