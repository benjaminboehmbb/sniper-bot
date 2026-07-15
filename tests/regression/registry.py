"""TD005-IU-021: Specification Extension Point Registry Realization Unit.

Enumerates, by name, every code-level mechanism decision this suite's own
Implementation resolves (extending the Implementation Specification's own
fifteen TD005-ID-xxx design-level decisions with concrete, code-level
choices), and every mechanism decision still open, attached to its own
owning module. No further mechanism choice is made without being recorded
here (TD005-SI-022, TD005-II-012).

Traceability: TD005-SO-020; TD005-ARC-022; TD005-SI-022.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class RegistryEntry:
    owning_module: str
    mechanism: str
    resolution: str
    deterministic: bool
    repository_local: bool


# Resolved code-level mechanism decisions (this suite's own "Remaining
# mechanism decisions", each satisfying the Implementation Specification,
# deterministic, repository-local, documented, and covered by tests).
RESOLVED: Tuple[RegistryEntry, ...] = (
    RegistryEntry(
        owning_module="tests/regression/replay.py",
        mechanism="Controlled-Condition Manifest representation",
        resolution="A frozen dataclass with five named fields (TD005-ID-005); "
                   "only tick_sequence is variable, since the active RunLoop "
                   "exposes no injection point for the other four.",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/environment_identity.py",
        mechanism="Execution-environment identity representation",
        resolution="A frozen dataclass capturing sys.version, "
                   "platform.python_implementation(), numpy.__version__, "
                   "pandas.__version__ at capture time.",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/observation.py",
        mechanism="Trajectory representation",
        resolution="An ordered tuple of ObservedSnapshot(tick_index, data) "
                   "records, ordered by tick_index (TD005-ID-007), never by "
                   "wall-clock timestamp.",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/comparison.py",
        mechanism="Numeric tolerance values",
        resolution="Combined relative-and-absolute bound (TD005-ID-008): "
                   "ABSOLUTE_TOLERANCE=1e-6, RELATIVE_TOLERANCE=1e-9.",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/evidence.py",
        mechanism="Evidence persistence format",
        resolution="JSON, one file per record, named by record_id, under "
                   "tests/regression/data/evidence/ (TD005-ID-014's own "
                   "designated location).",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/evidence.py",
        mechanism="Evidence persistence atomicity technique",
        resolution="Write-then-rename: tempfile.mkstemp in the same "
                   "directory, then os.replace (atomic on POSIX and "
                   "Windows) to the final path.",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/coverage.py",
        mechanism="Coverage concept",
        resolution="Three-part: module coverage, lifecycle-event-type "
                   "coverage, Functional-Requirement-citation coverage "
                   "(TD005-ID-010); no aggregate percentage computed.",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/classification.py",
        mechanism="Concrete classification procedure",
        resolution="Ordered four-step short-circuiting sequence "
                   "(TD005-ID-009), implemented as RegressionClassifier.classify().",
        deterministic=True,
        repository_local=True,
    ),
    RegistryEntry(
        owning_module="tests/regression/replay.py",
        mechanism="Replay Session execution-time budget",
        resolution="DEFAULT_BOUNDED_DURATION_SECONDS = 300.0, a conservative "
                   "ceiling for a bounded, finite, I/O-free tick sequence "
                   "(distinct from the LDV-level budget below, still open).",
        deterministic=True,
        repository_local=True,
    ),
)

# Still-open mechanism decisions: explicitly named, not silently invented.
STILL_OPEN: Tuple[str, ...] = (
    "Long-Duration-Validation execution-time budget (ldv_integration.py): "
    "no accepted-baseline requirement names a number; requires empirical "
    "calibration against real 1-hour/6-hour/24-hour/7-day/30-day runs, "
    "which this suite has not yet performed.",
    "Evidence retention/expiry policy (evidence.py): no accepted-baseline "
    "requirement mandates one; EvidencePersistence currently retains every "
    "persisted record indefinitely (Retained, never Expired).",
)


def all_resolved_mechanisms() -> Tuple[str, ...]:
    return tuple(entry.mechanism for entry in RESOLVED)


def is_registered(mechanism: str) -> bool:
    return mechanism in all_resolved_mechanisms() or mechanism in STILL_OPEN
