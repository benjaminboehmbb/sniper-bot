class CanonicalEnforcer:

    def __init__(self, canonical_state):

        self.cs = canonical_state

    def apply_position(self, position):

        if position is None:
            return self.cs.get()["position"]

        self.cs.update_position(position)
        return self.cs.get()["position"]

    def apply_pnl(self, pnl):

        if pnl is None:
            return self.cs.get()["pnl"]

        self.cs.update_pnl(pnl)
        return self.cs.get()["pnl"]

    def apply_equity(self, equity):

        if equity is None:
            return self.cs.get()["equity"]

        self.cs.update_equity(equity)
        return self.cs.get()["equity"]

    def apply_risk(self, risk):

        if risk is None:
            return self.cs.get()

        self.cs.update_risk(risk)
        return self.cs.get()