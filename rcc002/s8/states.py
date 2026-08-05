"""S8 build/publication state model (Reproducibility and Manifest
Specification SS14.1).

The nine states and their meanings are transcribed verbatim from SS14.1.
The specification does not tabulate an explicit transition graph; the
``ALLOWED_TRANSITIONS`` table below is this implementation's disciplined,
disclosed formalization of SS14.1's state meanings and SS14.4's explicit
rule ("Teilergebnisse ... MUESSEN ... als failed oder quarantined markiert
werden und DUERFEN NICHT unter einem finalen Veroeffentlichungspfad
erscheinen") -- the same kind of self-defined, versioned,
implementation-owned technical profile already used elsewhere in this
package for an open specification parameter (see
``rcc002.reason_codes`` for the precedent). It is not a resolution of any
open governance-level decision.
"""

from __future__ import annotations

import enum

from rcc002.s8.reason_codes import PublicationStateError


class BuildState(str, enum.Enum):
    PLANNED = "planned"
    RUNNING = "running"
    VALIDATING = "validating"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    CANDIDATE = "candidate"
    PUBLISHED = "published"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


# failed/quarantined are terminal for *this* build: SS14.4 permits keeping
# them only for diagnostics, never on a path towards final publication.
# superseded/withdrawn are terminal post-publication end states (SS14.3).
ALLOWED_TRANSITIONS: dict[BuildState, frozenset[BuildState]] = {
    BuildState.PLANNED: frozenset({BuildState.RUNNING, BuildState.FAILED}),
    BuildState.RUNNING: frozenset({BuildState.VALIDATING, BuildState.FAILED}),
    BuildState.VALIDATING: frozenset(
        {BuildState.CANDIDATE, BuildState.FAILED, BuildState.QUARANTINED}
    ),
    BuildState.CANDIDATE: frozenset(
        {BuildState.PUBLISHED, BuildState.QUARANTINED, BuildState.FAILED}
    ),
    BuildState.FAILED: frozenset(),
    BuildState.QUARANTINED: frozenset(),
    BuildState.PUBLISHED: frozenset({BuildState.SUPERSEDED, BuildState.WITHDRAWN}),
    BuildState.SUPERSEDED: frozenset(),
    BuildState.WITHDRAWN: frozenset(),
}

# SS14.4: a partial/diagnostic-only result must be one of exactly these.
DIAGNOSTIC_ONLY_STATES = frozenset({BuildState.FAILED, BuildState.QUARANTINED})

# SS14.2: only a fully checked candidate may be atomically published.
PUBLISHABLE_STATES = frozenset({BuildState.CANDIDATE})

# States whose artifacts may legitimately be referenced under a final
# publication path.
PUBLICATION_PATH_STATES = frozenset(
    {BuildState.PUBLISHED, BuildState.SUPERSEDED, BuildState.WITHDRAWN}
)


def _coerce(value: "BuildState | str") -> BuildState:
    if isinstance(value, BuildState):
        return value
    try:
        return BuildState(value)
    except ValueError as exc:
        raise PublicationStateError(f"unknown build state: {value!r}") from exc


def validate_transition(
    current: "BuildState | str", target: "BuildState | str"
) -> None:
    """Raise :class:`PublicationStateError` for any non-permitted edge."""
    current_state = _coerce(current)
    target_state = _coerce(target)
    if target_state not in ALLOWED_TRANSITIONS[current_state]:
        raise PublicationStateError(
            f"illegal state transition: {current_state.value} -> "
            f"{target_state.value}"
        )


def require_publishable(state: "BuildState | str") -> BuildState:
    """Raise unless ``state`` may be atomically published (SS14.2)."""
    resolved = _coerce(state)
    if resolved not in PUBLISHABLE_STATES:
        raise PublicationStateError(
            f"state {resolved.value!r} is not publishable; only "
            f"{sorted(s.value for s in PUBLISHABLE_STATES)} may publish"
        )
    return resolved


def require_not_diagnostic_only(state: "BuildState | str", *, context: str) -> None:
    """Raise if ``state`` is failed/quarantined and therefore forbidden on
    a final publication path (SS14.4)."""
    resolved = _coerce(state)
    if resolved in DIAGNOSTIC_ONLY_STATES:
        raise PublicationStateError(
            f"{context}: state {resolved.value!r} may not appear under a "
            f"final publication path"
        )


def is_terminal(state: "BuildState | str") -> bool:
    return not ALLOWED_TRANSITIONS[_coerce(state)]


__all__ = [
    "ALLOWED_TRANSITIONS",
    "DIAGNOSTIC_ONLY_STATES",
    "PUBLICATION_PATH_STATES",
    "PUBLISHABLE_STATES",
    "BuildState",
    "is_terminal",
    "require_not_diagnostic_only",
    "require_publishable",
    "validate_transition",
]
