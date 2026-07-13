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

    def apply_realized_pnl_cumulative(self, realized_pnl_cumulative):

        if realized_pnl_cumulative is None:
            return self.cs.get()["realized_pnl_cumulative"]

        self.cs.update_realized_pnl_cumulative(realized_pnl_cumulative)
        return self.cs.get()["realized_pnl_cumulative"]

    def apply_equity(self, equity):

        if equity is None:
            return self.cs.get()["equity"]

        self.cs.update_equity(equity)
        return self.cs.get()["equity"]

    def apply_peak_equity(self, peak_equity):

        if peak_equity is None:
            return self.cs.get()["peak_equity"]

        self.cs.update_peak_equity(peak_equity)
        return self.cs.get()["peak_equity"]

    def apply_risk(self, risk):

        if risk is None:
            return self.cs.get()

        self.cs.update_risk(risk)
        return self.cs.get()

    def apply_strategy_selection(self, weights):

        if weights is None:
            return self.cs.get()["strategy_selection"]

        self.cs.update_strategy_selection(weights)
        return self.cs.get()["strategy_selection"]

    def apply_execution_decision(self, decision):

        if decision is None:
            return self.cs.get()["execution_decision"]

        self.cs.update_execution_decision(decision)
        return self.cs.get()["execution_decision"]

    def apply_performance_metrics(self, performance_metrics):

        if performance_metrics is None:
            return self.cs.get()["performance_metrics"]

        self.cs.update_performance_metrics(performance_metrics)
        return self.cs.get()["performance_metrics"]

    def apply_runtime_status(self, runtime_status):

        if runtime_status is None:
            return self.cs.get()["runtime_status"]

        self.cs.update_runtime_status(runtime_status)
        return self.cs.get()["runtime_status"]

    def apply_regime(self, regime):

        if regime is None:
            return self.cs.get()["regime"]

        self.cs.update_regime(regime)
        return self.cs.get()["regime"]