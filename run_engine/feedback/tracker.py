class FeedbackTracker:

    def __init__(self):
        self.last_action = None
        self.loss_streak = 0

    def record(self, decision, execution):

        action = decision.get("action")
        result = execution.get("status")

        self.last_action = action

        # simple heuristic (placeholder)
        if result in ["BUY_EXECUTED", "SELL_EXECUTED"]:
            self.loss_streak = 0
        else:
            self.loss_streak += 1

        return self.loss_streak