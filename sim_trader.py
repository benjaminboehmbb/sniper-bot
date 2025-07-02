class SimTrader:
    def __init__(self, initial_balance=10000.0, fee=0.001, slippage=0.0005):
        self.balance = initial_balance
        self.fee = fee
        self.slippage = slippage
        self.position = None  # None, "long", "short"
        self.entry_price = None
        self.num_trades = 0
        self.history = []

    def buy(self, candle):
        if self.position == "long":
            return
        self.close_position(candle, "close-before-buy")
        price = candle['close'] * (1 + self.slippage)
        self.position = "long"
        self.entry_price = price
        self.num_trades += 1
        self._log_trade(candle, "buy", price)

    def sell(self, candle):
        if self.position == "short":
            return
        self.close_position(candle, "close-before-sell")
        price = candle['close'] * (1 - self.slippage)
        self.position = "short"
        self.entry_price = price
        self.num_trades += 1
        self._log_trade(candle, "sell", price)

    def close_position(self, candle, reason="close"):
        if self.position is None:
            return
        price = candle['close']
        if self.position == "long":
            profit = (price - self.entry_price) * (1 - self.fee)
        else:  # short
            profit = (self.entry_price - price) * (1 - self.fee)
        self.balance += profit
        self._log_trade(candle, reason, price)
        self.position = None
        self.entry_price = None

    def _log_trade(self, candle, action, price):
        self.history.append({
            "timestamp": candle["timestamp"],
            "price": price,
            "action": action,
            "position": self.position,
            "balance": round(self.balance, 2)
        })

    def get_history(self):
        return self.history




