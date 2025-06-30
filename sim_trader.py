class SimTrader:
    """
    Einfache Simulation eines Trading-Bots mit Long-only-Strategien.
    Arbeitet mit einem PriceFeed und einer Strategie.
    """

    def __init__(self, price_feed, strategy, starting_balance=10000):
        self.feed = price_feed
        self.strategy = strategy
        self.balance = starting_balance
        self.position = None  # {'entry_price': ..., 'timestamp': ...}
        self.trades = []

    def run(self):
        """
        Führt die Simulation aus, indem Kerzen vom Feed geholt und an die Strategie weitergegeben werden.
        """
        while self.feed.has_next():
            candle = self.feed.get_next()
            if candle is None:
                break

            signal = self.strategy.generate_signal(candle)

            # Kaufsignal
            if signal == 'buy' and self.position is None:
                self._buy(candle)

            # Verkaufssignal
            elif signal == 'sell' and self.position is not None:
                self._sell(candle)

        # Schließe offene Position am Ende
        if self.position is not None:
            self._sell(self.feed.data.iloc[-1].to_dict())

    def _buy(self, candle):
        amount = self.balance / candle['close']
        self.position = {
            'entry_price': candle['close'],
            'timestamp': candle['timestamp'],
            'amount': amount
        }
        self.balance = 0  # alles investiert

    def _sell(self, candle):
        exit_price = candle['close']
        proceeds = self.position['amount'] * exit_price
        pnl = proceeds - (self.position['amount'] * self.position['entry_price'])

        trade = {
            'entry_time': self.position['timestamp'],
            'exit_time': candle['timestamp'],
            'entry_price': self.position['entry_price'],
            'exit_price': exit_price,
            'pnl': pnl
        }

        self.trades.append(trade)
        self.balance = proceeds
        self.position = None

    def get_balance(self):
        """Aktueller Kontostand (Cash + ggf. offene Position)."""
        if self.position:
            current_price = self.feed.data.iloc[self.feed.pointer - 1]['close']
            return self.position['amount'] * current_price
        return self.balance

    def get_trades(self):
        """Gibt die Liste der abgeschlossenen Trades zurück."""
        return self.trades
