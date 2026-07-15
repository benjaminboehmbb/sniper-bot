"""TD005-IU-019: Long-Duration-Validation Integration Realization Unit.

Realizes TD005-SO-018's own single-invocation-contract behaviour across all
six Long-Duration-Validation stages, per TD005-ID-013's own pre-run
application decision: the invocation contract is applied before each stage
begins, never after, and is identical in every observable respect across
all six stages (TD005-SI-019, TD005-II-009: no stage-specific variant).

The concrete execution-time budget remains explicitly deferred to empirical
calibration once this suite is run against real Long-Duration-Validation
durations (TD005-ID-013's own Consequences); this unit records that the
budget is not yet set, rather than inventing a number.

State model (TD005-SO-018, unmodified): Not-Invoked -> Invoked ->
Stage-Complete -> Invoked (next stage, identical contract).

Traceability: TD005-SO-018; TD005-ARC-018; TD005-SI-019; TD005-ID-013.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Tuple

from tests.regression.orchestrator import InvocationResult, RegressionPipelineOrchestrator
from tests.regression.replay import ControlledConditionManifest

# The six mandatory Long-Duration-Validation stages (Implementation Baseline,
# independently re-confirmed): Functional smoke, 1-hour, 6-hour, 24-hour,
# 7-day, 30-day.
LDV_STAGES: Tuple[str, ...] = (
    "functional_smoke",
    "1_hour",
    "6_hour",
    "24_hour",
    "7_day",
    "30_day",
)


class LDVIntegrationError(Exception):
    pass


class StageSpecificVariantError(LDVIntegrationError):
    """Raised if two invocation contracts, captured for different stages,
    are found to differ (TD005-SI-019's own violation)."""


@dataclass(frozen=True)
class InvocationContract:
    """Identical in every observable respect across all six stages: the
    manifest-construction callable and the evaluated_contract_id."""

    manifest_factory_repr: str
    evaluated_contract_id: str

    # execution_time_budget_seconds is explicitly None: not yet set,
    # correctly deferred to empirical calibration (TD005-ID-013).
    execution_time_budget_seconds = None


@dataclass
class LDVIntegration:
    """TD005-IU-019's own realization: Not-Invoked -> Invoked ->
    Stage-Complete -> Invoked."""

    orchestrator: RegressionPipelineOrchestrator
    manifest_factory: Callable[[], ControlledConditionManifest]
    evaluated_contract_id: str = "AC-001"

    state: str = field(default="Not-Invoked", init=False)
    _stage_index: int = field(default=0, init=False)
    _contracts_used: List[InvocationContract] = field(default_factory=list, init=False)
    _evidence_continuity: List[str] = field(default_factory=list, init=False)

    def _current_contract(self) -> InvocationContract:
        return InvocationContract(
            manifest_factory_repr=repr(self.manifest_factory),
            evaluated_contract_id=self.evaluated_contract_id,
        )

    def run_stage(self, stage_name: str) -> InvocationResult:
        if stage_name not in LDV_STAGES:
            raise LDVIntegrationError(f"{stage_name!r} is not one of the six mandatory LDV stages")

        self.state = "Invoked"

        # Pre-run application: the contract is applied before the stage's
        # own regression check begins, using the identical contract every
        # other stage uses.
        contract = self._current_contract()
        if self._contracts_used and contract != self._contracts_used[0]:
            raise StageSpecificVariantError(
                f"invocation contract for {stage_name!r} differs from the contract used "
                f"for {LDV_STAGES[0]!r}"
            )
        self._contracts_used.append(contract)

        manifest = self.manifest_factory()
        result = self.orchestrator.invoke(manifest, session_id=f"ldv-{stage_name}", evaluated_contract_id=self.evaluated_contract_id)

        if result.evidence_path:
            self._evidence_continuity.append(result.evidence_path)

        self.state = "Stage-Complete"
        self._stage_index += 1
        return result

    def run_all_stages(self) -> List[InvocationResult]:
        return [self.run_stage(stage) for stage in LDV_STAGES]

    def contract_is_identical_across_stages(self) -> bool:
        if len(self._contracts_used) < 2:
            return True
        first = self._contracts_used[0]
        return all(c == first for c in self._contracts_used[1:])

    def evidence_continuity_chain(self) -> Tuple[str, ...]:
        return tuple(self._evidence_continuity)
