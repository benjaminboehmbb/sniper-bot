"""TD005-IU-004: Behavioural Vocabulary Realization Unit.

Realizes TD005-SO-009's own stability requirement for the terminology every
other Implementation Unit's own design is stated in (Architecture Baseline's
Ownership Terminology section; ADR-009's Scientific Definitions).

State model (unmodified from TD005-SO-009): Established -> Revised.
This module is Established; no revision has occurred.

Traceability: TD005-SO-009; TD005-ARC-010; TD005-AI-001.
"""

from __future__ import annotations

from typing import FrozenSet, Mapping


class VocabularyError(Exception):
    """Raised when a term is used outside its own established meaning."""


# The authoritative term set (TD005-SO-009's own Outputs field). Each entry
# names a term this suite's own design language relies on; no Implementation
# Unit in this suite introduces a new term without adding it here first
# (TD005-IU-004's own Forbidden interactions).
TERMS: Mapping[str, str] = {
    "Position": "The active trade's own side/quantity/entry-price state, FLAT "
                 "when no trade is open.",
    "Side": "LONG or SHORT; the only two non-FLAT Position values.",
    "Scale-In": "A lifecycle transition that increases the active trade's own "
                "quantity without closing it (SCALE_IN event).",
    "Partial Close": "A lifecycle transition that decreases the active trade's "
                      "own quantity, realizing PnL, without terminating it "
                      "(PARTIAL_CLOSE event).",
    "Full Close": "A lifecycle transition that terminates the active trade "
                  "exactly once (TRADE_CLOSED event).",
    "Tick-Complete": "The state returned by RunLoop.step() after all twelve "
                      "stages of ADR-010's own Stage Ordering have run for "
                      "that tick.",
    "Canonical Working State": "The CanonicalState instance's own current "
                                "field values at any point within a tick, "
                                "prior to Tick-Complete.",
    "Authoritative Owner": "The single component whose own update_* method "
                            "is the sole write path for a given canonical "
                            "field.",
    "Computational Authority": "The component that computes a value, "
                                "distinct from the component that owns "
                                "(publishes) it.",
    "Runtime Failure Event": "A RUNTIME_FAILURE_EVENT lifecycle event, "
                              "generated when a requested transition is "
                              "rejected; canonical state is never mutated "
                              "by a rejected transition.",
}

# Lifecycle event vocabulary (run_engine/core/trade_lifecycle.py, independently
# re-confirmed). Every event this suite observes is one of these five.
LIFECYCLE_EVENT_TYPES: FrozenSet[str] = frozenset(
    {"TRADE_OPENED", "SCALE_IN", "PARTIAL_CLOSE", "TRADE_CLOSED", "RUNTIME_FAILURE_EVENT"}
)

# Position Side vocabulary (run_engine/core/position.py).
SIDE_VALUES: FrozenSet[str] = frozenset({"LONG", "SHORT"})

# Position vocabulary (includes FLAT, unlike SIDE_VALUES).
POSITION_VALUES: FrozenSet[str] = frozenset({"FLAT", "LONG", "SHORT"})

# Executor status vocabulary (run_engine/core/execution/executor.py).
EXECUTOR_STATUS_VALUES: FrozenSet[str] = frozenset(
    {"BUY_EXECUTED", "SELL_EXECUTED", "NOOP"}
)

# The twelve CanonicalState update_* methods (run_engine/core/canonical_state.py,
# independently re-confirmed), each the sole write path for its own field(s).
CANONICAL_UPDATE_METHODS: FrozenSet[str] = frozenset(
    {
        "update_tick",
        "update_position",
        "update_equity",
        "update_peak_equity",
        "update_pnl",
        "update_realized_pnl_cumulative",
        "update_risk",
        "update_regime",
        "update_strategy_selection",
        "update_execution_decision",
        "update_performance_metrics",
        "update_runtime_status",
    }
)

# The complete set of CanonicalState field names (run_engine/core/canonical_state.py
# CanonicalState.__init__, independently re-confirmed).
CANONICAL_STATE_FIELDS: FrozenSet[str] = frozenset(
    {
        "tick",
        "price",
        "position",
        "equity",
        "peak_equity",
        "pnl",
        "realized_pnl_cumulative",
        "drawdown",
        "drawdown_ratio",
        "risk_allocation_factor",
        "regime",
        "strategy_selection",
        "execution_decision",
        "performance_metrics",
        "runtime_status",
    }
)


def define(term: str) -> str:
    """Return the authoritative definition of a term, or raise VocabularyError."""
    if term not in TERMS:
        raise VocabularyError(f"{term!r} is not an established Behavioural Vocabulary term")
    return TERMS[term]


def is_established(term: str) -> bool:
    return term in TERMS
