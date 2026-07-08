class Executor:

    DEFAULT_EXECUTION_QUANTITY = 1.0

    def execute(self, decision, position=None):

        action = decision.get("action", "HOLD")
        quantity = self._get_execution_quantity(decision)

        current_pos = "FLAT"
        if position:
            current_pos = position.get("position", "FLAT")

        if current_pos == "LONG" and action == "BUY":
            return {
                "action": "HOLD",
                "status": "NOOP",
                "quantity": 0.0,
            }

        if current_pos == "SHORT" and action == "SELL":
            return {
                "action": "HOLD",
                "status": "NOOP",
                "quantity": 0.0,
            }

        if action == "BUY":
            return {
                "action": action,
                "status": "BUY_EXECUTED",
                "quantity": quantity,
            }

        if action == "SELL":
            return {
                "action": action,
                "status": "SELL_EXECUTED",
                "quantity": quantity,
            }

        return {
            "action": "HOLD",
            "status": "NOOP",
            "quantity": 0.0,
        }

    def _get_execution_quantity(self, decision):
        raw_quantity = decision.get("quantity", self.DEFAULT_EXECUTION_QUANTITY)

        if raw_quantity is None:
            return 0.0

        try:
            return float(raw_quantity)
        except (TypeError, ValueError):
            return 0.0
