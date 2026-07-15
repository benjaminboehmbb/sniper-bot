"""TD005-IU-002: Certification Boundary Realization Unit.

Realizes TD005-SO-002's own certification-status determination behaviour,
per TD005-ID-003's own three contract-type category structure: ADR-sourced,
AC-sourced, Certified-Unit-Finding-sourced.

State model (TD005-SO-002, unmodified): Undefined -> Defined -> Revised.

Forbidden: does not itself classify a deviation as regression or
non-regression outside its own recorded boundary (TD005-AI-008); that is
exclusively TD005-IU-014's own role (classification.py).

Traceability: TD005-SO-002; TD005-ARC-002; TD005-ID-003.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from tests.regression.corpus import CertifiedContractCorpus

BOUNDARY_RULE_VERSION = "TD005-CB-V1"

# The three contract-type categories (TD005-ID-003).
CONTRACT_CATEGORIES: Tuple[str, ...] = ("ADR", "AC", "CERTIFIED_UNIT")


@dataclass(frozen=True)
class CertificationDetermination:
    contract_id: str
    certified: bool
    boundary_rule_version: str
    category: str = ""


class CertificationBoundary:
    """TD005-IU-002's own realization: Undefined -> Defined -> Revised."""

    def __init__(self, corpus: CertifiedContractCorpus) -> None:
        self._corpus = corpus
        self._state = "Undefined"
        self._rule_version = BOUNDARY_RULE_VERSION
        self._history: Dict[str, CertificationDetermination] = {}

    @property
    def state(self) -> str:
        return self._state

    def define(self) -> None:
        """Establish the rule for the first time (Undefined -> Defined)."""
        self._corpus.enumerate()
        self._state = "Defined"

    def revise(self, new_version: str) -> None:
        """A governed revision changes the rule (Defined/Revised -> Revised)."""
        if self._state == "Undefined":
            raise RuntimeError("cannot revise an Undefined boundary; call define() first")
        self._rule_version = new_version
        self._state = "Revised"

    def evaluate(self, contract_id: str) -> CertificationDetermination:
        """Apply exactly one boundary-rule version; identical inputs yield
        identical determinations (TD005-SO-002 Postconditions)."""
        if self._state == "Undefined":
            self.define()

        is_member = self._corpus.membership(contract_id)
        category = ""
        if is_member:
            category = self._corpus.get(contract_id).category

        determination = CertificationDetermination(
            contract_id=contract_id,
            certified=is_member,
            boundary_rule_version=self._rule_version,
            category=category,
        )
        self._history[contract_id] = determination
        return determination

    def determination_history(self) -> Dict[str, CertificationDetermination]:
        return dict(self._history)
