class Safety:

    def __init__(self):
        self.loss_streak = 0
        self.max_loss_streak = 5

    def update(self, loss_streak):
        self.loss_streak = loss_streak

    def allow(self, decision):

        if decision.get("confidence", 0) < 0.5:
            return False

        if self.loss_streak >= self.max_loss_streak:
            return False

        if decision.get("action") not in ["BUY", "SELL", "HOLD"]:
            return False

        return True