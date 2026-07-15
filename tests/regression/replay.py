"""TD005-IU-006: Replay Session Realization Unit.

Realizes TD005-SO-004's own controlled-condition execution behaviour, using
TD005-ID-005's own Controlled-Condition Manifest concept.

Honest limitation, evidence-grounded (Section 5 re-verification of
run_engine/core/loop.py: RunLoop.__init__ takes no parameters and always
constructs fresh StateEngine/RegimeClassifier/PositionEngine/
TradeLifecycleEngine/RiskEngine/Executor/PnLEngine/PerformanceEngine
instances): the active Run Engine currently exposes no injection point for
a non-default initial Position, lifecycle history, regime/strategy state,
or configuration. Per this suite's own repository-safety constraint (do not
modify active run_engine/ runtime semantics), the manifest's own
initial-state fields are validated against the one value RunLoop actually
supports (its own fresh-construction default) rather than silently ignored;
only the tick sequence is a genuinely controllable input today. This is
recorded, not silently assumed (TD005-SI-005's own "complete controlled-
condition specification" is satisfied by a manifest whose non-tick-sequence
fields are explicit, not merely absent).

State model (TD005-SO-004, unmodified): Not-Started -> Configuring ->
Executing -> Captured / Failed.

Traceability: TD005-SO-004; TD005-ARC-011; TD005-AD-003; TD005-ID-005.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from tests.regression.environment_identity import EnvironmentIdentity, capture as capture_identity

# TD005-ID-013 / TD005-II-017 conservative, documented, code-level execution-time
# budget for a single Replay Session (distinct from the Long-Duration-Validation
# execution-time budget, still explicitly deferred, ldv_integration.py). Chosen
# conservatively: replay of a bounded, finite tick sequence against a
# single-threaded, deterministic engine with no I/O is expected to complete in
# well under one second per hundred ticks; 300 seconds is a generous ceiling
# that only trips on a genuine hang.
DEFAULT_BOUNDED_DURATION_SECONDS = 300.0


class ManifestError(Exception):
    """Base class for Controlled-Condition Manifest validation errors."""


class IncompleteManifestError(ManifestError):
    pass


class UnsupportedManifestError(ManifestError):
    pass


class TrajectoryNotAvailableError(Exception):
    """Raised when a Failed or not-yet-Captured session's trajectory is requested."""


@dataclass(frozen=True)
class ControlledConditionManifest:
    """TD005-ID-005's own five named fields."""

    tick_sequence: Tuple[Dict[str, Any], ...]
    initial_position: str = "FLAT"
    lifecycle_history: Tuple[Any, ...] = ()
    regime_strategy_state: str = "fresh"
    configuration: str = "default"

    def validate(self) -> None:
        if not self.tick_sequence:
            raise IncompleteManifestError("tick_sequence must be non-empty")
        if self.initial_position != "FLAT":
            raise UnsupportedManifestError(
                "initial_position != 'FLAT' is not supported: the active RunLoop "
                "exposes no injection point for a non-default initial Position"
            )
        if self.lifecycle_history != ():
            raise UnsupportedManifestError(
                "non-empty lifecycle_history is not supported: the active RunLoop "
                "exposes no injection point for prior lifecycle history"
            )
        if self.regime_strategy_state != "fresh":
            raise UnsupportedManifestError(
                "regime_strategy_state != 'fresh' is not supported: the active "
                "RunLoop always constructs a fresh RegimeClassifier/StrategySelector"
            )
        if self.configuration != "default":
            raise UnsupportedManifestError(
                "configuration != 'default' is not supported: RiskEngine's own "
                "policy configuration is fixed at construction with no override point"
            )


@dataclass
class ReplaySession:
    """TD005-IU-006's own realization: Not-Started -> Configuring -> Executing
    -> Captured / Failed."""

    manifest: ControlledConditionManifest
    bounded_duration_seconds: float = DEFAULT_BOUNDED_DURATION_SECONDS
    state: str = field(default="Not-Started", init=False)
    identity: Optional[EnvironmentIdentity] = field(default=None, init=False)
    failure_reason: Optional[str] = field(default=None, init=False)
    _trajectory: List[Dict[str, Any]] = field(default_factory=list, init=False)

    def run(self, session_id: str) -> "ReplaySession":
        self.state = "Configuring"
        try:
            self.manifest.validate()
        except ManifestError as exc:
            self.state = "Failed"
            self.failure_reason = f"incomplete controlled-condition specification: {exc}"
            return self

        self.state = "Executing"
        self.identity = capture_identity(session_id)

        # Local import: the active Run Engine's own runtime entry point is
        # touched only here, never at module import time, and never through
        # any path other than this unit driving RunLoop.step() (TD005-CON-002,
        # TD005-II-005: no alternative execution path).
        from run_engine.core.loop import RunLoop

        engine = RunLoop()
        start_time = time.monotonic()

        for tick_data in self.manifest.tick_sequence:
            if (time.monotonic() - start_time) > self.bounded_duration_seconds:
                self.state = "Failed"
                self.failure_reason = "bounded duration exceeded (TD005-SI-005, TD005-II-017)"
                self._trajectory = []
                return self

            # Pass a copy: this unit never lets the Run Engine observe or
            # retain a reference to manifest-owned data structures.
            try:
                result = engine.step(dict(tick_data))
            except Exception as exc:  # noqa: BLE001 - an unhandled condition is itself the Failed trigger
                self.state = "Failed"
                self.failure_reason = f"unhandled condition: {exc!r}"
                self._trajectory = []
                return self

            self._trajectory.append(result)

        self.state = "Captured"
        return self

    def captured_trajectory(self) -> Tuple[Dict[str, Any], ...]:
        """A Failed session's trajectory is never usable downstream (TD005-SI-006)."""
        if self.state != "Captured":
            raise TrajectoryNotAvailableError(
                f"trajectory not available: session state is {self.state!r}, not Captured"
            )
        return tuple(self._trajectory)
