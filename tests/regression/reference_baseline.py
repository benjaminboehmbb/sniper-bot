"""TD005-IU-003: Reference Baseline Realization Unit.

Realizes TD005-SO-003's own establishment, governance, and reproducibility
behaviour for the authoritative reference-baseline record, per TD005-ID-004's
own freshly-established-baseline source-selection decision: the reference is
sourced from a freshly-established bootstrap capture (ReplaySession), never
a reconstruction from a historical commit.

State model (TD005-SO-003, unmodified, with the Specification's own V1.1
single-state clarification): Unestablished -> Capturing -> Established ->
Revising -> Established. (Established is reachable by two distinct
transitions; it is one state, not two.)

Forbidden: does not mutate the established record in place (TD005-AI-003);
does not accept a Failed bootstrap capture.

Traceability: TD005-SO-003; TD005-ARC-003; TD005-AD-002; TD005-AI-003,
TD005-AI-018; TD005-ID-004.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

from tests.regression.certification_boundary import CertificationBoundary
from tests.regression.corpus import CertifiedContractCorpus
from tests.regression.environment_identity import EnvironmentIdentity
from tests.regression.observation import ObservedSnapshot
from tests.regression.replay import ReplaySession


class ReferenceBaselineError(Exception):
    pass


class BootstrapRejectedError(ReferenceBaselineError):
    """Raised when a bootstrap capture reaching Failed is rejected (TD005-IU-003's
    own Forbidden interactions: never accepts a Failed bootstrap capture)."""


class NotEstablishedError(ReferenceBaselineError):
    """Raised when the reference baseline is consulted before Established."""


@dataclass(frozen=True)
class ReferenceBaselineRecord:
    """Immutable once established (TD005-AI-003: never mutated in place; a
    revision produces a new record via a fresh governance act)."""

    trajectory: Tuple[ObservedSnapshot, ...]
    environment_identity: EnvironmentIdentity
    source: str  # "freshly-established" (TD005-ID-004)
    governance_epoch: int
    revision_history: Tuple[str, ...] = field(default_factory=tuple)


class ReferenceBaselineAuthority:
    """TD005-IU-003's own realization: Unestablished -> Capturing ->
    Established -> Revising -> Established."""

    def __init__(self, corpus: CertifiedContractCorpus, boundary: CertificationBoundary) -> None:
        self._corpus = corpus
        self._boundary = boundary
        self._state = "Unestablished"
        self._record: Optional[ReferenceBaselineRecord] = None
        self._epoch = 0

    @property
    def state(self) -> str:
        return self._state

    @property
    def record(self) -> Optional[ReferenceBaselineRecord]:
        return self._record

    def establish(self, session: ReplaySession, observer, governance_note: str = "initial bootstrap") -> ReferenceBaselineRecord:
        """Establish the reference from a Captured bootstrap ReplaySession
        (TD005-SI-004: the specific execution intended as the reference must
        have reached Captured before this unit accepts it)."""
        self._state = "Capturing"

        if session.state != "Captured":
            self._state = "Unestablished"
            raise BootstrapRejectedError(
                f"bootstrap capture rejected: session state is {session.state!r}, "
                f"not Captured ({session.failure_reason})"
            )

        # Corpus/boundary must be available before a reference is accepted
        # (TD005-IU-003's own Dependencies on TD005-IU-001, TD005-IU-002).
        self._corpus.enumerate()
        self._boundary.evaluate("AC-001")

        trajectory = tuple(observer.observe(session))
        self._epoch += 1

        self._record = ReferenceBaselineRecord(
            trajectory=trajectory,
            environment_identity=session.identity,
            source="freshly-established",
            governance_epoch=self._epoch,
            revision_history=(governance_note,),
        )
        self._state = "Established"
        return self._record

    def revise(self, session: ReplaySession, observer, governance_note: str) -> ReferenceBaselineRecord:
        """A governed revision uses the identical bootstrap procedure as
        initial establishment, never a partial patch (TD005-ID-004's own
        Consequences)."""
        if self._state != "Established":
            raise NotEstablishedError("cannot revise a reference baseline that is not yet Established")

        self._state = "Revising"

        if session.state != "Captured":
            self._state = "Established"  # revert to the still-valid prior record
            raise BootstrapRejectedError(
                f"revision bootstrap capture rejected: session state is {session.state!r}, "
                f"not Captured ({session.failure_reason})"
            )

        trajectory = tuple(observer.observe(session))
        self._epoch += 1
        prior_history = self._record.revision_history if self._record else ()

        self._record = ReferenceBaselineRecord(
            trajectory=trajectory,
            environment_identity=session.identity,
            source="freshly-established",
            governance_epoch=self._epoch,
            revision_history=prior_history + (governance_note,),
        )
        self._state = "Established"
        return self._record

    def require_established(self) -> ReferenceBaselineRecord:
        if self._state != "Established" or self._record is None:
            raise NotEstablishedError(f"reference baseline is not Established (state={self._state!r})")
        return self._record
