class MA200Filter:
    def __init__(self, period=200):
        self.period = period
        self.closes = []

    def update(self, candle):
        self.closes.append(candle['close'])

    def should_buy(self, candle):
        self.update(candle)
        if len(self.closes) < self.period:
            return False
        ma200 = sum(self.closes[-self.period:]) / self.period
        return candle['close'] > ma200
