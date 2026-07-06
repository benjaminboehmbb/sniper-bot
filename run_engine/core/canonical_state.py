class CanonicalState:

    def __init__(self):

        self.state = {
            "tick": None,

            "price": None,

            "position": {
                "position": "FLAT",
                "entry_price": None,
                "last_price": None
            },

            "equity": 100.0,

            "peak_equity": 100.0,

            "pnl": 0.0,

            "drawdown": 0.0,

            "drawdown_ratio": 0.0,

            "exposure": 1.0,

            "regime": "UNKNOWN"
        }

    def update_tick(self, tick, price):

        self.state["tick"] = tick
        self.state["price"] = price

    def update_position(self, position):

        self.state["position"] = position

    def update_equity(self, equity):

        self.state["equity"] = equity

        if equity > self.state["peak_equity"]:
            self.state["peak_equity"] = equity

    def update_pnl(self, pnl):

        self.state["pnl"] = pnl

    def update_risk(self, risk_dict):

        self.state["drawdown"] = risk_dict.get("drawdown", 0.0)
        self.state["drawdown_ratio"] = risk_dict.get("drawdown_ratio", 0.0)
        self.state["exposure"] = risk_dict.get("exposure", 1.0)

    def update_regime(self, regime):

        self.state["regime"] = regime

    def get(self):

        return self.state

    def reset(self):

        self.__init__()