"""TD005-IU-017 (Contract-to-Requirement Coverage) and TD005-IU-018 (Module
and State-Transition Coverage) Realization Units.

TD005-ID-010's own three-part coverage concept: module coverage (every
active module reached by at least one comparison), state-transition
coverage (every lifecycle transition exercised at least once), and
Functional-Requirement-citation coverage (every FR exercised) - with no
percentage-based aggregate metric computed (TD005-AI-014).

Both realization units are advisory-only: no coverage report gates, blocks,
or alters a classification result already reached (TD005-II-015).

State models (both unmodified): Not-Computed -> Computed -> Stale ->
Recomputed.

Traceability: TD005-SO-014/015; TD005-ARC-015/016; TD005-AI-014;
TD005-ID-010.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, Set

from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.scope import ScopeBoundary
from tests.regression.vocabulary import LIFECYCLE_EVENT_TYPES

ALL_FR_IDS: FrozenSet[str] = frozenset(f"TD005-FR-{i:03d}" for i in range(1, 23))


@dataclass
class ContractCoverageReport:
    uncovered_contracts: FrozenSet[str] = field(default_factory=frozenset)
    uncovered_requirements: FrozenSet[str] = field(default_factory=frozenset)

    @property
    def complete(self) -> bool:
        return not self.uncovered_contracts and not self.uncovered_requirements


class ContractRequirementCoverage:
    """TD005-IU-017's own realization: Not-Computed -> Computed -> Stale ->
    Recomputed."""

    def __init__(self, corpus: CertifiedContractCorpus) -> None:
        self._corpus = corpus
        self._state = "Not-Computed"
        self._exercised_contracts: Set[str] = set()
        self._exercised_requirements: Set[str] = set()
        self._report: ContractCoverageReport = ContractCoverageReport()
        self._last_corpus_ids: FrozenSet[str] = frozenset()

    @property
    def state(self) -> str:
        return self._state

    def record_contract_exercised(self, contract_id: str) -> None:
        self._exercised_contracts.add(contract_id)
        if self._state == "Computed":
            self._state = "Stale"

    def record_requirement_exercised(self, fr_id: str) -> None:
        self._exercised_requirements.add(fr_id)
        if self._state == "Computed":
            self._state = "Stale"

    def compute(self) -> ContractCoverageReport:
        self._corpus.enumerate()
        all_contracts = frozenset(self._corpus.all_ids())
        uncovered_contracts = all_contracts - frozenset(self._exercised_contracts)
        uncovered_requirements = ALL_FR_IDS - frozenset(self._exercised_requirements)

        self._report = ContractCoverageReport(
            uncovered_contracts=uncovered_contracts,
            uncovered_requirements=uncovered_requirements,
        )
        self._last_corpus_ids = all_contracts
        self._state = "Recomputed" if self._state == "Stale" else "Computed"
        return self._report

    def is_stale(self) -> bool:
        if self._state != "Computed" and self._state != "Recomputed":
            return False
        return frozenset(self._corpus.all_ids()) != self._last_corpus_ids


@dataclass
class ModuleCoverageReport:
    uncovered_modules: FrozenSet[str] = field(default_factory=frozenset)
    uncovered_event_types: FrozenSet[str] = field(default_factory=frozenset)

    @property
    def complete(self) -> bool:
        return not self.uncovered_modules and not self.uncovered_event_types


class ModuleStateTransitionCoverage:
    """TD005-IU-018's own realization: Not-Computed -> Computed -> Stale ->
    Recomputed. Cross-layer dependency on TD005-IU-022 (Scope Boundary),
    Layer 6 depending on Layer 9 - already justified by TD005-SO-021's own
    drift-trigger relationship (Section 9 of the Implementation
    Specification)."""

    def __init__(self, scope: ScopeBoundary) -> None:
        self._scope = scope
        self._state = "Not-Computed"
        self._exercised_modules: Set[str] = set()
        self._exercised_event_types: Set[str] = set()
        self._report: ModuleCoverageReport = ModuleCoverageReport()
        self._last_active_set: FrozenSet[str] = frozenset()

    @property
    def state(self) -> str:
        return self._state

    def record_module_exercised(self, module_path: str) -> None:
        self._exercised_modules.add(module_path)
        if self._state == "Computed":
            self._state = "Stale"

    def record_event_type_exercised(self, event_type: str) -> None:
        self._exercised_event_types.add(event_type)
        if self._state == "Computed":
            self._state = "Stale"

    def on_scope_drift(self) -> None:
        """TD005-IU-022 signals this unit to recompute on drift."""
        if self._state == "Computed":
            self._state = "Stale"

    def compute(self) -> ModuleCoverageReport:
        partition = self._scope.confirm()
        uncovered_modules = frozenset(partition.active) - frozenset(self._exercised_modules)
        uncovered_events = LIFECYCLE_EVENT_TYPES - frozenset(self._exercised_event_types)

        self._report = ModuleCoverageReport(
            uncovered_modules=uncovered_modules,
            uncovered_event_types=uncovered_events,
        )
        self._last_active_set = frozenset(partition.active)
        self._state = "Recomputed" if self._state == "Stale" else "Computed"
        return self._report
