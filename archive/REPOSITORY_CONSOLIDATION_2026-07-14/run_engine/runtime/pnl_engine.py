class PnLEngine:

    def __init__(self):
        self.last_price = None
        self.last_position = None

    def compute_reward(self, decision, execution, price):

        action = decision.get("action")

        reward = 0.0

        # initialize
        if self.last_price is None:
            self.last_price = price
            self.last_position = action
            return 0.0

        price_change = price - self.last_price

        # position logic (simplified proxy)
        if self.last_position == "BUY":
            reward = price_change

        elif self.last_position == "SELL":
            reward = -price_change

        else:
            reward = 0.0

        # execution penalty
        if execution.get("status") == "NOOP":
            reward -= 0.01

        # update state
        self.last_price = price
        self.last_position = action

        return reward