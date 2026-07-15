class ExecutionAdapter:

    def execute(self, decision):

        action = decision.get("action")

        if action == "BUY":
            print("EXEC BUY")
            return {"status": "BUY_EXECUTED"}

        if action == "SELL":
            print("EXEC SELL")
            return {"status": "SELL_EXECUTED"}

        return {"status": "NOOP"}