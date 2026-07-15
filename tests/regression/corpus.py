"""TD005-IU-001: Certified Contract Corpus Realization Unit.

Realizes TD005-SO-001's own enumeration, membership-determination, and
drift-detection behaviour. Implements TD005-ID-002's own Governance Citation
Manifest concept: an ordered listing of the certified-contract corpus's own
primary-evidence sources, re-derivable on demand by re-checking each cited
source still exists (TD005-SI-002: never an unverifiable cached view).

State model (TD005-SO-001, unmodified): Uninitialized -> Enumerated ->
Drift-Detected -> Re-Enumerated.

Forbidden: does not read active Run Engine runtime state; does not perform
classification (TD005-IU-001's own Forbidden interactions).

Traceability: TD005-SO-001; TD005-ARC-001; TD005-ID-002.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Tuple

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@dataclass(frozen=True)
class CorpusEntry:
    """One certified-contract corpus entry: a citable primary-evidence source."""

    contract_id: str
    category: str  # "ADR" | "AC" | "CERTIFIED_UNIT"
    source_path: str
    description: str


def _p(*parts: str) -> str:
    return os.path.join(REPO_ROOT, *parts)


# The corpus enumeration itself. Every entry cites a primary-evidence source
# independently re-confirmed to exist (Section 5 of the Implementation
# Specification). This is the manifest content; re-derivation means
# re-checking every cited path still exists (see CertifiedContractCorpus.enumerate).
_MANIFEST: Tuple[CorpusEntry, ...] = (
    CorpusEntry("ADR-009", "ADR", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Lifecycle Transition Table and Scientific Definitions"),
    CorpusEntry("ADR-010", "ADR", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Deterministic Runtime Execution Ordering (twelve-stage sequence)"),
    CorpusEntry("ADR-011", "ADR", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Runtime Failure Handling"),
    CorpusEntry("AC-001", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Canonical Runtime Ownership"),
    CorpusEntry("AC-002", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Unique Information Ownership"),
    CorpusEntry("AC-004", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Lifecycle Integrity"),
    CorpusEntry("AC-005", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Financial Integrity"),
    CorpusEntry("AC-006", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Canonical Runtime State (single authoritative representation)"),
    CorpusEntry("AC-007", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Risk Evaluation determinism and non-ownership"),
    CorpusEntry("AC-008", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Performance Evaluation gated on completed lifecycle outcomes"),
    CorpusEntry("AC-009", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Tick Completion uniqueness"),
    CorpusEntry("AC-010", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Information Flow non-reconstruction"),
    CorpusEntry("AC-012", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Deterministic Behaviour"),
    CorpusEntry("AC-014", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Lifecycle Semantics distinctness of Scale-In/Partial-Close/Full-Close"),
    CorpusEntry("AC-015", "AC", _p("docs", "architecture", "RUN_ENGINE_ARCHITECTURE_BASELINE_V1_2026-07-06.md"),
                "Runtime Failure Handling"),
    CorpusEntry("P2-02A", "CERTIFIED_UNIT",
                _p("docs", "architecture", "certification", "P2_02A_FINAL_CERTIFICATION_V1_2026-07-10.md"),
                "Position Ownership - Final Certification"),
    CorpusEntry("P2-03", "CERTIFIED_UNIT",
                _p("docs", "architecture", "certification", "P2_03_FINAL_CERTIFICATION_V1_2026-07-11.md"),
                "Financial Ownership - Final Certification"),
    CorpusEntry("P2-04", "CERTIFIED_UNIT",
                _p("docs", "architecture", "certification", "P2_04_FINAL_CERTIFICATION_V1_2026-07-13.md"),
                "Risk Ownership - Final Certification"),
    CorpusEntry("P3-01", "CERTIFIED_UNIT",
                _p("docs", "architecture", "certification", "P3_01_FINAL_CERTIFICATION_V1_2026-07-13.md"),
                "Deterministic Execution Ordering - Final Certification"),
    CorpusEntry("P3-02", "CERTIFIED_UNIT",
                _p("docs", "architecture", "certification", "P3_02_FINAL_CERTIFICATION_V1_2026-07-13.md"),
                "Information Flow Validation - Final Certification"),
    CorpusEntry("P3-03", "CERTIFIED_UNIT",
                _p("docs", "architecture", "certification", "P3_03_FINAL_CERTIFICATION_V1_2026-07-13.md"),
                "Performance Validation - Final Certification"),
    CorpusEntry("REPOSITORY_CONSOLIDATION", "CERTIFIED_UNIT",
                _p("docs", "architecture", "certification", "REPOSITORY_CONSOLIDATION_FINAL_CERTIFICATION_V1_2026-07-14.md"),
                "Repository Consolidation - Final Certification"),
)


@dataclass
class DriftReport:
    missing: List[str] = field(default_factory=list)

    @property
    def drifted(self) -> bool:
        return len(self.missing) > 0


class CertifiedContractCorpus:
    """TD005-IU-001's own realization: Uninitialized -> Enumerated -> Drift-Detected -> Re-Enumerated."""

    def __init__(self) -> None:
        self._state = "Uninitialized"
        self._enumeration: Tuple[CorpusEntry, ...] = ()

    @property
    def state(self) -> str:
        return self._state

    def enumerate(self) -> Tuple[CorpusEntry, ...]:
        """Re-derive the enumeration from primary evidence (TD005-SI-002)."""
        for entry in _MANIFEST:
            if not os.path.isfile(entry.source_path):
                self._state = "Drift-Detected"
                return self._enumeration if self._enumeration else ()
        self._enumeration = _MANIFEST
        self._state = "Enumerated" if self._state == "Uninitialized" else "Re-Enumerated"
        return self._enumeration

    def check_drift(self) -> DriftReport:
        """Report any cited source that no longer exists (drift/ambiguity signal)."""
        missing = [e.contract_id for e in _MANIFEST if not os.path.isfile(e.source_path)]
        report = DriftReport(missing=missing)
        if report.drifted:
            self._state = "Drift-Detected"
        return report

    def membership(self, contract_id: str) -> bool:
        """Determinate membership/exclusion for any candidate (TD005-SO-001 Postconditions)."""
        if self._state == "Uninitialized":
            self.enumerate()
        return any(e.contract_id == contract_id for e in self._enumeration)

    def get(self, contract_id: str) -> CorpusEntry:
        for e in self._enumeration or self.enumerate():
            if e.contract_id == contract_id:
                return e
        raise KeyError(f"{contract_id!r} is not a corpus member")

    def all_ids(self) -> Tuple[str, ...]:
        entries = self._enumeration or self.enumerate()
        return tuple(e.contract_id for e in entries)
