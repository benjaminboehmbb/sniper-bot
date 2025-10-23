class CombinedStrategy:
    def __init__(self, filters):
        self.filters = filters

    def generate_signal(self, candle):
        buy_signals = [flt.should_buy(candle) for flt in self.filters]
        sell_signals = [getattr(flt, 'should_sell', lambda c: False)(candle) for flt in self.filters]

        if all(buy_signals):
            return 'buy'
        if any(sell_signals):
            return 'sell'
        return None
