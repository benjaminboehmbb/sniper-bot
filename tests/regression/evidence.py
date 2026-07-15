"""TD005-IU-015 (Regression Evidence Composition) and TD005-IU-016 (Evidence
Persistence and Continuity) Realization Units.

TD005-ID-011's own nine-field schema (eight required, one conditional):
affected tick; affected stage or component; expected value; actual value;
input provenance; initial-state provenance; certified-contract ID;
execution-environment identity; plus a reasoned unavailability marker,
usable only in place of any of the first eight when the outcome-producing
condition itself renders that element structurally unobtainable
(TD005-II-014).

TD005-ID-012's own append-only, governed-location, atomic-write persistence
design: the persist operation is atomic (write-then-rename); an interrupted
persist leaves the record Unpersisted, never Persisted-and-Altered
(TD005-IU-016's own Failure behaviour).

State models (both unmodified): TD005-SO-016 (Not-Composed -> Composing ->
Composed); TD005-SO-017 (Unpersisted -> Persisted -> Retained -> Expired).

Traceability: TD005-SO-016/017; TD005-ARC-013/014; TD005-AI-005,
TD005-AI-015, TD005-AI-017; TD005-SD-004; TD005-ID-011, TD005-ID-012,
TD005-ID-014.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict

# TD005-ID-014's own designated location: a new subdirectory of the already-
# existing, currently-empty tests/ convention, distinct from tests/ssi/.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
EVIDENCE_DIR = os.path.join(REPO_ROOT, "tests", "regression", "data", "evidence")

REQUIRED_ELEMENTS = (
    "affected_tick",
    "affected_stage_or_component",
    "expected_value",
    "actual_value",
    "input_provenance",
    "initial_state_provenance",
    "certified_contract_id",
    "execution_environment_identity",
)


class EvidenceError(Exception):
    pass


class IncompleteEvidenceError(EvidenceError):
    pass


class InterruptedPersistError(EvidenceError):
    """Raised (in tests only) to simulate a persist operation interrupted
    before completion, so the atomic-write guarantee can be exercised."""


@dataclass
class UnavailabilityMarker:
    """TD005-II-014: names the specific upstream condition that prevented a
    determinate value; a generic or unexplained marker does not satisfy
    this element."""

    reason: str

    def __post_init__(self) -> None:
        if not self.reason or not self.reason.strip():
            raise IncompleteEvidenceError(
                "a reasoned unavailability marker must name the specific upstream "
                "condition; a bare/empty marker does not satisfy this element"
            )


@dataclass
class EvidenceRecord:
    """Not-Composed -> Composing -> Composed. Immutable once Composed
    (TD005-AI-005, TD005-SI-017): no field is ever reassigned in place after
    compose() completes; a correction produces a new, separate record."""

    state: str = field(default="Not-Composed")
    elements: Dict[str, Any] = field(default_factory=dict)
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))


class EvidenceComposer:
    """TD005-IU-015's own realization."""

    def compose(self, **elements: Any) -> EvidenceRecord:
        """Compose one complete evidence record. Every required element must
        be present, either as a determinate value or an UnavailabilityMarker
        instance (TD005-SI-016's own accommodation)."""
        record = EvidenceRecord(state="Composing")

        missing = [name for name in REQUIRED_ELEMENTS if name not in elements]
        if missing:
            raise IncompleteEvidenceError(
                f"evidence record missing required elements (no value and no "
                f"reasoned unavailability marker): {missing}"
            )

        for name in REQUIRED_ELEMENTS:
            value = elements[name]
            if value is None:
                raise IncompleteEvidenceError(
                    f"element {name!r} is a bare omission (None); a reasoned "
                    f"UnavailabilityMarker or a determinate value is required"
                )
            record.elements[name] = value

        record.state = "Composed"
        return record


def _serialize(value: Any) -> Any:
    if isinstance(value, UnavailabilityMarker):
        return {"__unavailable__": True, "reason": value.reason}
    if hasattr(value, "__dataclass_fields__"):
        import dataclasses

        return {k: _serialize(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(v) for v in value]
    return value


class EvidencePersistence:
    """TD005-IU-016's own realization: Unpersisted -> Persisted -> Retained
    -> Expired. Append-only, governed-location (TD005-ID-014), atomic write
    (TD005-ID-012)."""

    def __init__(self, directory: str = EVIDENCE_DIR) -> None:
        self._directory = directory

    def persist(self, record: EvidenceRecord, *, simulate_interruption: bool = False) -> str:
        """Persist a Composed record atomically. Returns the persisted
        record's own path. If simulate_interruption is True (test use only),
        the write is deliberately abandoned before the atomic rename, and
        the record SHALL remain absent from the persisted store (never a
        partially-written file)."""
        if record.state != "Composed":
            raise EvidenceError(f"cannot persist a record in state {record.state!r}; must be Composed")

        os.makedirs(self._directory, exist_ok=True)
        final_path = os.path.join(self._directory, f"{record.record_id}.json")
        payload = json.dumps(
            {"record_id": record.record_id, "elements": _serialize(record.elements)},
            indent=2,
            sort_keys=True,
            default=str,
        )

        # Atomic write: write to a temp file in the same directory, then
        # os.replace (atomic on POSIX and Windows) to the final path. If
        # interrupted before the replace, the final path never exists -
        # never a partially-written state observable to any consumer.
        fd, tmp_path = tempfile.mkstemp(dir=self._directory, prefix=".tmp-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(payload)

            if simulate_interruption:
                raise InterruptedPersistError("persist operation interrupted before completion (test simulation)")

            os.replace(tmp_path, final_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

        return final_path

    def is_persisted(self, record: EvidenceRecord) -> bool:
        final_path = os.path.join(self._directory, f"{record.record_id}.json")
        return os.path.isfile(final_path)

    def load(self, record_id: str) -> Dict[str, Any]:
        final_path = os.path.join(self._directory, f"{record_id}.json")
        with open(final_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def retained_across(self, record: EvidenceRecord, stage_transitions: int) -> bool:
        """Cross-stage continuity: a persisted record remains retrievable,
        unaltered, across every subsequent Long-Duration-Validation stage
        transition (TD005-SI-018's own retrieve-unaltered guarantee)."""
        if not self.is_persisted(record):
            return False
        before = self.load(record.record_id)
        for _ in range(stage_transitions):
            after = self.load(record.record_id)
            if after != before:
                return False
        return True
