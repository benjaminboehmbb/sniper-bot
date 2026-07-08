from run_engine.core.state import StateEngine
from run_engine.core.regime import RegimeClassifier
from run_engine.core.strategy import StrategySelector
from run_engine.core.position import PositionEngine
from run_engine.core.risk import RiskEngine
from run_engine.core.execution import Executor
from run_engine.core.performance import PerformanceEngine
from run_engine.core.pnl import PnLEngine
from run_engine.core.trade_lifecycle import TradeLifecycleEngine
from run_engine.core.canonical_state import CanonicalState
from run_engine.core.canonical_enforcer import CanonicalEnforcer


class RunLoop:

    def __init__(self):

        self.state_engine = StateEngine()
        self.regime_classifier = RegimeClassifier()
        self.strategy_selector = StrategySelector()
        self.position_engine = PositionEngine()
        self.trade_lifecycle_engine = TradeLifecycleEngine()
        self.risk_engine = RiskEngine()
        self.execution_engine = Executor()
        self.pnl_engine = PnLEngine()
        self.performance_engine = PerformanceEngine()

        self.cstate = CanonicalState()
        self.enforcer = CanonicalEnforcer(self.cstate)

    def step(self, tick):

        state = self.state_engine.update(tick)

        runtime_tick = state.get("tick") if isinstance(state, dict) else None
        price = state.get("price") if isinstance(state, dict) else None

        self.cstate.update_tick(runtime_tick, price)

        regime = self.regime_classifier.classify(state)
        self.cstate.update_regime(regime)

        position_pre = self.position_engine.update_pre_trade(state)

        weights = self.strategy_selector.select(state, regime, position_pre)

        decision = self.strategy_selector.decide(state, regime, weights)

        execution = self.execution_engine.execute(decision, position_pre)

        trade_event = self.trade_lifecycle_engine.on_execution(execution, state)

        lifecycle_position = self.trade_lifecycle_engine.current_position()

        position = self.position_engine.update_post_trade(
            execution,
            state,
            lifecycle_position,
        )
        self.enforcer.apply_position(position)

        pnl = self.pnl_engine.update(trade_event, execution)
        self.enforcer.apply_pnl(pnl)

        equity = self.cstate.get()["equity"] + pnl
        self.enforcer.apply_equity(equity)

        canonical_state = self.cstate.get()

        risk = self.risk_engine.check(canonical_state, position, regime)
        self.enforcer.apply_risk(risk if isinstance(risk, dict) else {})

        performance = self.performance_engine.update(decision, pnl, regime)

        return {
            "tick": runtime_tick,
            "state": self.cstate.get(),
            "regime": regime,
            "decision": decision,
            "execution": execution,
            "trade_event": trade_event,
            "lifecycle_position": lifecycle_position,
            "active_trade": self.trade_lifecycle_engine.get_active_trade(),
            "position": position,
            "risk": risk,
            "pnl": pnl,
            "equity": equity,
            "performance": performance,
            "strategy_weights": weights,
        }


if __name__ == "__main__":

    engine = RunLoop()
    tick = 0

    while True:

        tick_data = {
            "tick": tick,
            "price": 30000 + (tick % 100),
        }

        result = engine.step(tick_data)
        print(result)

        tick += 1
