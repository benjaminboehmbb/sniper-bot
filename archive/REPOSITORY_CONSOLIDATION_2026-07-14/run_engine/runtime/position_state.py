class PositionState:

    def __init__(self):

        self.position = "FLAT"
        self.entry_price = None
        self.last_price = None

    def update(self, action, price):

        reward = 0.0

        # initialize price tracking
        self.last_price = price

        # -------------------------
        # ENTRY LOGIC
        # -------------------------
        if self.position == "FLAT":

            if action == "BUY":
                self.position = "LONG"
                self.entry_price = price

            elif action == "SELL":
                self.position = "SHORT"
                self.entry_price = price

            return reward

        # -------------------------
        # LONG POSITION
        # -------------------------
        if self.position == "LONG":

            reward = price - self.entry_price

            if action == "SELL":
                # close long
                self.position = "FLAT"
                self.entry_price = None

            return reward

        # -------------------------
        # SHORT POSITION
        # -------------------------
        if self.position == "SHORT":

            reward = self.entry_price - price

            if action == "BUY":
                # close short
                self.position = "FLAT"
                self.entry_price = None

            return reward

        return reward

    def get_state(self):

        return {
            "position": self.position,
            "entry_price": self.entry_price,
            "last_price": self.last_price
        }