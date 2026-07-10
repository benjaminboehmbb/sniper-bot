class CanonicalState:

    VALID_RUNTIME_STATUS_VALUES = (
        "INITIALIZING",
        "RUNNING",
        "PAUSED",
        "STOPPING",
        "STOPPED",
        "ERROR",
    )

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

            "regime": "UNKNOWN",

            "strategy_selection": None,

            "execution_decision": None,

            "performance_metrics": None,

            "runtime_status": None
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

    def update_strategy_selection(self, weights):

        self.state["strategy_selection"] = weights

    def update_execution_decision(self, decision):

        self.state["execution_decision"] = decision

    def update_performance_metrics(self, performance_metrics):

        self.state["performance_metrics"] = performance_metrics

    def update_runtime_status(self, runtime_status):

        if runtime_status not in self.VALID_RUNTIME_STATUS_VALUES:
            raise ValueError(f"Invalid runtime_status: {runtime_status!r}")

        self.state["runtime_status"] = runtime_status

    def get(self):

        return self.state

    def reset(self):

        self.__init__()