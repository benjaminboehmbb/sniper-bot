import pandas as pd

class MACDFilter:
    """
    Gibt 'buy'-Signal, wenn MACD-Linie die Signal-Linie von unten nach oben kreuzt.
    Kein 'sell'-Signal enthalten (zur optionalen Erweiterung).
    """
    def __init__(self, fast=12, slow=26, signal=9):
        self.fast = fast
        self.slow = slow
        self.signal = signal
        self.closes = []
        self.prev_macd = None
        self.prev_signal = None

    def update(self, candle):
        self.closes.append(candle['close'])

        if len(self.closes) < self.slow + self.signal:
            return None, None, False  # ❗ Rückgabe auf 3 Werte erweitert

        series = pd.Series(self.closes)
        ema_fast = series.ewm(span=self.fast).mean()
        ema_slow = series.ewm(span=self.slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.signal).mean()

        macd_now = macd_line.iloc[-1]
        signal_now = signal_line.iloc[-1]

        macd_cross = (
            self.prev_macd is not None and
            self.prev_signal is not None and
            self.prev_macd < self.prev_signal and
            macd_now > signal_now
        )

        self.prev_macd = macd_now
        self.prev_signal = signal_now

        return macd_line, signal_line, macd_cross

    def should_buy(self, candle):
        _, _, macd_cross = self.update(candle)
        return macd_cross

    def should_sell(self, candle):
        return False  # optional später erweiterbar
