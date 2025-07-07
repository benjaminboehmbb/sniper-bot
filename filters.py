import pandas as pd

def rsi_filter(df, threshold=30):
    # Signal 1, wenn RSI unter threshold, sonst 0
    return (df["RSI"] < threshold).astype(int)

def ma200_filter(df):
    # Signal 1, wenn Schlusskurs über MA200, sonst 0
    return (df["close"] > df["MA200"]).astype(int)

def bollinger_filter(df):
    # Signal 1, wenn Schlusskurs unter unteres Bollinger Band, sonst 0
    return (df["close"] < df["BB_lower"]).astype(int)

def macd_filter(df):
    # Signal 1, wenn MACD über Signal-Linie (vereinfachte Annahme hier)
    return (df["MACD"] > df["MACD_signal"]).astype(int)

def apply_filters(df, filter_funcs, weights):
    """
    Kombiniert mehrere Filter mit Gewichtung.
    filter_funcs: Liste von Funktionen (df -> Series mit 0/1)
    weights: Liste von Gewichtungen (float zwischen 0 und 1)
    """
    assert len(filter_funcs) == len(weights), "Filter und Gewichtungen müssen gleich lang sein"
    
    combined_signal = pd.Series(0.0, index=df.index)
    for f, w in zip(filter_funcs, weights):
        combined_signal += f(df) * w
    # Normalisieren auf max 1
    max_signal = combined_signal.max()
    if max_signal > 1:
        combined_signal /= max_signal
    return combined_signal





