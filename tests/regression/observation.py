"""TD005-IU-008 (Observable Surface Classification) and TD005-IU-009
(Non-Interference Observation) Realization Units.

TD005-IU-009 is the exclusive component permitted to read active Run Engine
state directly (TD005-AD-013, TD005-II-004); every other unit consumes state
exclusively through its own exposed ObservedSnapshot (TD005-II-011). It
never reads run_engine internals directly - it consumes the already-returned,
Tick-Complete dict a Captured ReplaySession produced (replay.py), which is
itself the certified boundary (RunLoop.step()'s own return value, after all
twelve ADR-010 stages have run) - and deep-copies it so no downstream
consumer, however implemented, could measurably affect a later tick even by
accident (TD005-SI-007: no measurable behavioural difference from
observation).

TD005-IU-008 classifies each enumerated observable field into exactly one of
four categories, before any Comparison-domain unit consumes it (TD005-SI-008).

State models (both unmodified): TD005-SO-006 (Unclassified -> Classified);
TD005-SO-007 (Idle -> Reading -> Exposed -> Idle).

Traceability: TD005-SO-006; TD005-ARC-004; TD005-AI-002. TD005-SO-007;
TD005-ARC-005; TD005-AI-002; TD005-AD-013; TD005-II-011.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Tuple

from tests.regression.replay import ReplaySession, TrajectoryNotAvailableError


class ObservableCategory(Enum):
    CERTIFIED_EXTERNAL_OUTPUT = "certified_external_output"
    CERTIFIED_INTERNAL_INVARIANT = "certified_internal_invariant"
    IMPLEMENTATION_DETAIL = "implementation_detail"
    INCIDENTAL_INTERMEDIATE_VALUE = "incidental_intermediate_value"


# The four-category classification map. Every field this suite's own
# observation boundary can see is classified exactly once (TD005-SI-008).
# Two field families exist in RunLoop.step()'s own return dict: its
# fourteen top-level keys, and the fifteen CanonicalState fields nested
# under its own "state" key. Nested fields are keyed here as "state.<field>"
# to avoid colliding with a top-level key of the same underlying concept
# (for example, top-level "regime" versus nested "state.regime", which are
# in fact the same value published twice - AC-002 Unique Information
# Ownership concerns the canonical *write* path, not this suite's own
# read-side convenience duplication).
CLASSIFICATION: Dict[str, ObservableCategory] = {
    # --- Top-level RunLoop.step() return keys ---
    "tick": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "regime": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "position": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "risk": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "pnl": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "equity": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "performance": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    # Certified per FR-016 (Executor Action-to-Status Mapping).
    "execution": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    # Certified per FR-007 through FR-010, FR-017 (lifecycle event integrity,
    # runtime failure handling).
    "trade_event": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    # decision (confidence-bearing internal decision) and strategy_weights are
    # not named by any certified AC/FR as a comparison target in their own
    # right; they are internal tuning/decision state that feeds the certified
    # Executor status (above), not themselves a contract.
    "decision": ObservableCategory.IMPLEMENTATION_DETAIL,
    "strategy_weights": ObservableCategory.IMPLEMENTATION_DETAIL,
    # Auxiliary values RunLoop.step()'s own return dict includes beyond
    # CanonicalState itself, for debugging/observability - not part of the
    # AC-001 Canonical Runtime Ownership boundary.
    "active_trade": ObservableCategory.INCIDENTAL_INTERMEDIATE_VALUE,
    "lifecycle_position": ObservableCategory.INCIDENTAL_INTERMEDIATE_VALUE,
    # The wrapping "state" key's own nested CanonicalState snapshot is
    # certified field-by-field below; the wrapping key itself is an
    # incidental intermediate value, not a second independent contract.
    "state": ObservableCategory.INCIDENTAL_INTERMEDIATE_VALUE,
    # --- Nested CanonicalState fields (run_engine/core/canonical_state.py,
    #     independently re-confirmed), certified by AC-001/002/004/005/006/
    #     007/008/009 and FR-001 through FR-017. ---
    "state.tick": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.price": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.position": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.equity": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.peak_equity": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.pnl": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.realized_pnl_cumulative": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.drawdown": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.drawdown_ratio": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.risk_allocation_factor": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.regime": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.runtime_status": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.performance_metrics": ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT,
    "state.strategy_selection": ObservableCategory.IMPLEMENTATION_DETAIL,
    "state.execution_decision": ObservableCategory.IMPLEMENTATION_DETAIL,
}

COMPARISON_DOMAIN = frozenset(
    {
        field
        for field, category in CLASSIFICATION.items()
        if category
        in (ObservableCategory.CERTIFIED_EXTERNAL_OUTPUT, ObservableCategory.CERTIFIED_INTERNAL_INVARIANT)
    }
)


class ClassificationError(Exception):
    pass


class ObservableSurfaceClassifier:
    """TD005-IU-008's own realization: Unclassified -> Classified."""

    def __init__(self) -> None:
        self._state = "Unclassified"

    @property
    def state(self) -> str:
        return self._state

    def classify_all(self) -> Dict[str, ObservableCategory]:
        self._state = "Classified"
        return dict(CLASSIFICATION)

    def category_of(self, field_name: str) -> ObservableCategory:
        if self._state == "Unclassified":
            self.classify_all()
        if field_name not in CLASSIFICATION:
            raise ClassificationError(f"{field_name!r} is not a classified observable field")
        return CLASSIFICATION[field_name]

    def in_comparison_domain(self, field_name: str) -> bool:
        return field_name in COMPARISON_DOMAIN


@dataclass(frozen=True)
class ObservedSnapshot:
    tick_index: int
    data: Dict[str, Any]  # deep-copied, immutable-in-practice


class NonInterferenceObserver:
    """TD005-IU-009's own realization: Idle -> Reading -> Exposed -> Idle,
    repeating per tick."""

    def __init__(self) -> None:
        self._state = "Idle"

    @property
    def state(self) -> str:
        return self._state

    def observe(self, session: ReplaySession) -> Tuple[ObservedSnapshot, ...]:
        """Expose the Captured session's own trajectory as a tuple of
        immutable ObservedSnapshot records, one per tick. Raises
        TrajectoryNotAvailableError for a session that never reached
        Captured (TD005-SI-006)."""
        raw_trajectory = session.captured_trajectory()  # raises if not Captured

        snapshots = []
        for index, raw in enumerate(raw_trajectory):
            self._state = "Reading"
            # Deep-copy at the observation boundary: this act itself never
            # mutates, delays, or measurably alters Run Engine state or
            # timing (TD005-SI-007), since it operates only on the already-
            # returned Tick-Complete dict, after RunLoop.step() has fully
            # completed for that tick.
            snapshot = ObservedSnapshot(tick_index=index, data=copy.deepcopy(raw))
            self._state = "Exposed"
            snapshots.append(snapshot)
            self._state = "Idle"

        return tuple(snapshots)
