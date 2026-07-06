class Executor:

    def execute(self, decision, position=None):

        action = decision.get("action", "HOLD")

        current_pos = "FLAT"
        if position:
            current_pos = position.get("position", "FLAT")

        if current_pos == "LONG" and action == "BUY":
            return {
                "action": "HOLD",
                "status": "NOOP"
            }

        if current_pos == "SHORT" and action == "SELL":
            return {
                "action": "HOLD",
                "status": "NOOP"
            }

        if action == "BUY":
            return {
                "action": action,
                "status": "BUY_EXECUTED"
            }

        if action == "SELL":
            return {
                "action": action,
                "status": "SELL_EXECUTED"
            }

        return {
            "action": "HOLD",
            "status": "NOOP"
        }
