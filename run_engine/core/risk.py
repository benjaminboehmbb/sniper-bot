class RiskEngine:
    """
    Risk Ownership (P2-04).

    Authoritative Owner of Risk Policy Configuration: max_drawdown, max_exposure,
    min_exposure, and the CHOP/TREND/VOLATILE regime-dampening multipliers applied
    in check(). Risk Policy Configuration is a fixed, non-evolving declaration, not
    computed runtime state, and is deliberately never published to CanonicalState
    (P2-04-AD-002). It has no Computational Authority distinct from its
    Authoritative Owner, since it is a declared value, not a computed one
    (P2-04-AD-002).

    Computational Authority for risk_allocation_factor, the value check() returns
    under the key "exposure" (unrenamed per P2-02A-AD-007) and CanonicalState
    stores under "risk_allocation_factor". CanonicalState, not RiskEngine, is the
    Authoritative Owner of risk_allocation_factor; RiskEngine only computes it
    (P2-04-AD-004, P2-04-AD-005).

    Stateless beyond the three Risk Policy Configuration attributes set in
    __init__: no instance attribute is ever added or mutated after __init__
    completes, and check() persists no value across calls (P2-04-AD-012).
    check() is a pure, deterministic function of its three parameters: identical
    inputs produce functionally identical outputs, independent of call history,
    wall-clock time, or any other non-explicit input (P2-04-AD-011).

    No reset() method exists or is required: since Risk Policy Configuration is
    never mutated after __init__, a fresh RiskEngine() instantiation already
    re-establishes it identically, and no state exists that a reset could need to
    restore (P2-04-AD-015).
    """

    def __init__(self):

        self.max_drawdown = 0.2
        self.max_exposure = 1.0
        self.min_exposure = 0.1

    def check(self, state, position, regime):
        """
        Compute Drawdown, Drawdown Ratio, and risk_allocation_factor for the
        current tick.

        Strictly read-only: neither state nor position is ever mutated by this
        method, and Equity, Peak Equity, and Position (including Position-derived
        Exposure) are never cached or republished under an owning name
        (P2-04-AD-008, P2-04-AD-013). Reads canonical Equity and Peak Equity from
        state, and Position-derived Exposure from position.
        """
        # Read-only; deliberately not incorporated into the formula below.
        # Functional non-incorporation is a recorded architecture decision
        # (P2-04-AD-007), not an omission; reactivating functional use requires
        # an Architecture Evolution Review.
        position_exposure = position.get("exposure", 0.0)

        equity = state.get("equity", 0.0)

        if equity is None:
            equity = 0.0

        peak_equity = state.get("peak_equity", 0.0)

        if peak_equity is None:
            peak_equity = 0.0

        # drawdown calculation
        drawdown = peak_equity - equity

        # normalize drawdown ratio
        drawdown_ratio = 0.0
        if peak_equity > 0:
            drawdown_ratio = drawdown / peak_equity

        # exposure control
        # Risk-limiting formula retained in its current structural shape
        # (P2-04-AD-009); no revision pending. Inputs are drawdown_ratio and
        # regime only; TD-006's remaining risk-formula half is closed by this
        # retention decision together with P2-04-AD-002 (P2-04-AD-010).
        exposure = self.max_exposure

        if drawdown_ratio > self.max_drawdown:
            exposure = self.min_exposure

        # regime dampening
        if regime == "CHOP":
            exposure *= 0.7

        if regime == "TREND":
            exposure *= 1.0

        if regime == "VOLATILE":
            exposure *= 0.5

        # clamp
        exposure = max(self.min_exposure, min(self.max_exposure, exposure))

        return {
            "equity": equity,
            "peak_equity": peak_equity,
            "drawdown": drawdown,
            "drawdown_ratio": drawdown_ratio,
            "exposure": exposure
        }