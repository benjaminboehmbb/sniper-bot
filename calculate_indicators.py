import pandas as pd
import numpy as np

def calculate_rsi(df, length=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=length).mean()
    avg_loss = loss.rolling(window=length).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df, fast=12, slow=26, signal=9):
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    return macd, macd_signal

def calculate_bollinger_bands(df, length=20, std_dev=2):
    sma = df['close'].rolling(window=length).mean()
    rstd = df['close'].rolling(window=length).std()
    upper_band = sma + std_dev * rstd
    lower_band = sma - std_dev * rstd
    return upper_band, lower_band

def calculate_ma200(df):
    return df['close'].rolling(window=200).mean()

def main():
    df = pd.read_csv("C:/btc_data/merged/price_data.csv", parse_dates=['open_time'])
    
    df['RSI'] = calculate_rsi(df)
    df['MACD'], df['MACD_signal'] = calculate_macd(df)
    df['BB_upper'], df['BB_lower'] = calculate_bollinger_bands(df)
    df['MA200'] = calculate_ma200(df)
    
    df.to_csv("C:/btc_data/merged/price_data.csv", index=False)
    print("Indikatoren berechnet und CSV aktualisiert.")

if __name__ == "__main__":
    main()


