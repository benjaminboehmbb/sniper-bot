class PositionEngine:

    def __init__(self):
        self.position = "FLAT"
        self.entry_price = 0.0

    def update_pre_trade(self, state):

        price = state.get("price", 0.0)
        if price is None:
            price = 0.0

        return {
            "position": self.position,
            "entry_price": self.entry_price,
            "last_price": price
        }

    def update_post_trade(self, execution, state):

        action = execution.get("action", "HOLD")
        price = state.get("price", 0.0)

        if price is None:
            price = 0.0

        if action == "BUY" and self.position == "FLAT":
            self.position = "LONG"
            self.entry_price = float(price)

        elif action == "SELL" and self.position == "FLAT":
            self.position = "SHORT"
            self.entry_price = float(price)

        elif action == "SELL" and self.position == "LONG":
            self.position = "FLAT"
            self.entry_price = 0.0

        elif action == "BUY" and self.position == "SHORT":
            self.position = "FLAT"
            self.entry_price = 0.0

        return {
            "position": self.position,
            "entry_price": self.entry_price,
            "last_price": price
        }