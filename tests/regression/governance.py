"""TD005-IU-020 (Governance Sequence Conformance) and TD005-IU-023
(Executor Namespace Boundary) Realization Units.

Both are static markers, consuming no runtime information (TD005-SO-019 /
TD005-SO-022, unmodified state models: Conformant / Excluded).

TD005-IU-023 explicitly records that this suite does not own, extend, or
duplicate Repository Consolidation's own Executor-namespace-uniqueness
protection (RC-AD-004); this suite's own scope.py (TD005-IU-022) re-derives
the active/inactive module partition for regression-coverage purposes only,
never as an Executor-namespace uniqueness check.

Traceability: TD005-SO-019; TD005-ARC-019; TD005-DEP-033. TD005-SO-022;
TD005-ARC-021; TD005-AI-012; TD005-SI-021; TD005-AD-009.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConformanceRecord:
    state: str
    statement: str


GOVERNANCE_CONFORMANCE = ConformanceRecord(
    state="Conformant",
    statement=(
        "This suite implements exactly the accepted TD-005 FRA V1.1, SDA V1.1, "
        "CGA V1.1, Architecture V1.1, Specification V1.1, and Implementation "
        "Specification V1.1. No baseline was redesigned during coding; every "
        "code-level mechanism decision (tolerance constants, evidence schema, "
        "persistence format, coverage concept, classification procedure, "
        "execution-time budget deferral) is documented at its own point of "
        "definition and in the TD-005 Implementation Report, citing the "
        "Implementation Specification's own registry entry it resolves."
    ),
)


@dataclass(frozen=True)
class ExclusionRecord:
    state: str
    statement: str


EXECUTOR_NAMESPACE_EXCLUSION = ExclusionRecord(
    state="Excluded",
    statement=(
        "This suite does not own, extend, or duplicate Repository "
        "Consolidation's own Executor-namespace-uniqueness protection "
        "(RC-AD-004). tests/regression/scope.py's own AST-based import "
        "closure re-derives the active/inactive module partition for "
        "regression-coverage purposes only; it performs no namespace-"
        "collision check and asserts no exclusive-ownership property over "
        "run_engine/core/execution/executor.py beyond confirming it is "
        "reachable from run_engine.main, a fact Repository Consolidation's "
        "own already-certified mechanism independently and separately "
        "protects."
    ),
)


def conformant() -> bool:
    return GOVERNANCE_CONFORMANCE.state == "Conformant"


def executor_namespace_excluded() -> bool:
    return EXECUTOR_NAMESPACE_EXCLUSION.state == "Excluded"
