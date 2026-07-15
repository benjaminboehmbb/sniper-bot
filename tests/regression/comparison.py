"""TD005-IU-010 (Behavioural Equivalence Definition), TD005-IU-011
(Trajectory Comparison), TD005-IU-012 (Numeric and Categorical Comparison),
TD005-IU-013 (Object-Identity-Independent Comparison) Realization Units.

Traceability: TD005-SO-008/010/011/012; TD005-ARC-006/007/008/009;
TD005-AI-004, TD005-AI-007; TD005-SI-009, TD005-SI-011, TD005-SI-012;
TD005-ID-007, TD005-ID-008.
"""

from __future__ import annotations

import dataclasses
import math
from dataclasses import dataclass, field
from typing import Any, List, Tuple

from tests.regression.observation import COMPARISON_DOMAIN, ObservedSnapshot

# --- TD005-IU-012: Numeric and Categorical Comparison -----------------------

# TD005-ID-008's own combined relative-and-absolute tolerance policy shape.
# The concrete constants are a conservative, documented, code-level choice
# (Remaining mechanism decisions: numeric tolerance values), deterministic
# and repository-local, covered by tests. Chosen generously relative to
# float64 precision so only a genuine behavioural difference trips it.
ABSOLUTE_TOLERANCE = 1e-6
RELATIVE_TOLERANCE = 1e-9

# Leaf field names, drawn from run_engine/core/trade_lifecycle.py's own
# LifecycleEvent, run_engine/core/position.py's own snapshot, run_engine/core/
# risk.py's own check() return, run_engine/core/execution/executor.py's own
# execute() return, and run_engine/core/performance.py's own stats - every
# leaf name this suite's own trajectories can produce is categorized here
# (TD005-SI-011: never left uncategorized).
EXACT_EQUALITY_FIELDS = frozenset(
    {
        "event_type", "position", "side", "action", "status", "regime",
        "runtime_status", "trade_id", "tick", "reason", "trades",
    }
)
TOLERANCE_BOUNDED_FIELDS = frozenset(
    {
        "price", "entry_price", "prior_quantity", "execution_quantity",
        "resulting_quantity", "quantity_delta", "closed_quantity",
        "remaining_quantity", "quantity", "last_price", "exposure",
        "equity", "peak_equity", "pnl", "realized_pnl_cumulative",
        "drawdown", "drawdown_ratio", "risk_allocation_factor", "winrate",
        "confidence",
    }
)


class ComparisonError(Exception):
    pass


class UncategorizedFieldError(ComparisonError):
    pass


class NumericCategoricalComparator:
    """TD005-IU-012's own realization: Undefined -> Defined -> Applied."""

    def __init__(self) -> None:
        self._state = "Defined"  # category structure is fixed at construction

    @property
    def state(self) -> str:
        return self._state

    def category_of(self, field_name: str) -> str:
        if field_name in EXACT_EQUALITY_FIELDS:
            return "exact_equality"
        if field_name in TOLERANCE_BOUNDED_FIELDS:
            return "tolerance_bounded"
        raise UncategorizedFieldError(f"{field_name!r} has no assigned comparison category")

    def compare_leaf(self, field_name: str, reference_value: Any, candidate_value: Any) -> bool:
        """Applies the identical tolerance policy to reference and candidate
        (TD005-II-007: never an asymmetric one)."""
        self._state = "Applied"
        category = self.category_of(field_name)

        if category == "exact_equality":
            return reference_value == candidate_value

        # tolerance_bounded: combined relative-and-absolute bound.
        if reference_value is None or candidate_value is None:
            return reference_value == candidate_value
        try:
            a = float(reference_value)
            b = float(candidate_value)
        except (TypeError, ValueError):
            return reference_value == candidate_value

        if not (math.isfinite(a) and math.isfinite(b)):
            return a == b or (math.isnan(a) and math.isnan(b))

        diff = abs(a - b)
        if diff <= ABSOLUTE_TOLERANCE:
            return True
        return diff <= RELATIVE_TOLERANCE * max(abs(a), abs(b))


# --- TD005-IU-013: Object-Identity-Independent Comparison --------------------

class ObjectIdentityIndependentComparator:
    """TD005-IU-013's own realization: Undefined -> Defined -> Applied."""

    def __init__(self) -> None:
        self._state = "Defined"

    @property
    def state(self) -> str:
        return self._state

    def structurally_equal(self, a: Any, b: Any) -> bool:
        """Structural value equality only; object identity is irrelevant to
        every comparison outcome (TD005-SI-012). Deliberately never uses
        `is` as a comparison criterion."""
        self._state = "Applied"
        return self._deep_equal(a, b)

    def _deep_equal(self, a: Any, b: Any) -> bool:
        if dataclasses.is_dataclass(a) and dataclasses.is_dataclass(b):
            return self._deep_equal(dataclasses.asdict(a), dataclasses.asdict(b))
        if isinstance(a, dict) and isinstance(b, dict):
            if set(a.keys()) != set(b.keys()):
                return False
            return all(self._deep_equal(a[k], b[k]) for k in a)
        if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
            if len(a) != len(b):
                return False
            return all(self._deep_equal(x, y) for x, y in zip(a, b))
        return a == b


# --- TD005-IU-010: Behavioural Equivalence Definition ------------------------

@dataclass
class LeafDifference:
    path: str
    reference_value: Any
    candidate_value: Any


@dataclass
class ComparisonResult:
    equivalent: bool
    differences: List[LeafDifference] = field(default_factory=list)


class BehaviouralEquivalenceDefinition:
    """TD005-IU-010's own realization: Undefined -> Defined -> Applied.
    Composes trajectory equivalence (IU-011, held by TrajectoryComparator)
    and value-level equivalence (IU-012, IU-013) into one internally
    consistent definition (TD005-AI-007: never byte, source, or
    implementation identity)."""

    def __init__(self) -> None:
        self._numeric = NumericCategoricalComparator()
        self._identity_independent = ObjectIdentityIndependentComparator()
        self._state = "Defined"

    @property
    def state(self) -> str:
        return self._state

    def compare_value(self, path: str, reference_value: Any, candidate_value: Any) -> List[LeafDifference]:
        """Recursively compares two observed values leaf by leaf, applying
        TD005-IU-012's own category rule at every leaf and TD005-IU-013's own
        structural-equality rule at every container level."""
        self._state = "Applied"

        if dataclasses.is_dataclass(reference_value) and dataclasses.is_dataclass(candidate_value):
            return self.compare_value(path, dataclasses.asdict(reference_value), dataclasses.asdict(candidate_value))

        if isinstance(reference_value, dict) and isinstance(candidate_value, dict):
            differences: List[LeafDifference] = []
            keys = set(reference_value.keys()) | set(candidate_value.keys())
            for key in sorted(keys, key=str):
                if key not in reference_value or key not in candidate_value:
                    differences.append(LeafDifference(f"{path}.{key}", reference_value.get(key), candidate_value.get(key)))
                    continue
                differences.extend(self.compare_value(f"{path}.{key}", reference_value[key], candidate_value[key]))
            return differences

        if reference_value is None and candidate_value is None:
            return []

        leaf_name = path.rsplit(".", 1)[-1]
        try:
            equal = self._numeric.compare_leaf(leaf_name, reference_value, candidate_value)
        except UncategorizedFieldError:
            # No categorization exists for this leaf: fall back to structural
            # value equality (TD005-IU-013), never object identity, and
            # never silently drop the comparison.
            equal = self._identity_independent.structurally_equal(reference_value, candidate_value)

        if equal:
            return []
        return [LeafDifference(path, reference_value, candidate_value)]


# --- TD005-IU-011: Trajectory Comparison -------------------------------------

class TrajectoryComparator:
    """TD005-IU-011's own realization: Undefined -> Defined -> Applied."""

    def __init__(self, equivalence: BehaviouralEquivalenceDefinition) -> None:
        self._equivalence = equivalence
        self._state = "Defined"

    @property
    def state(self) -> str:
        return self._state

    def compare(
        self,
        reference_trajectory: Tuple[ObservedSnapshot, ...],
        candidate_trajectory: Tuple[ObservedSnapshot, ...],
    ) -> ComparisonResult:
        """Evaluates across the complete captured trajectory using logical-
        order (tick-index) semantics only, never wall-clock timing
        (TD005-SI-010); only fields within the comparison domain
        (TD005-SO-006's own certified-output/internal-invariant categories)
        are ever compared."""
        self._state = "Applied"

        differences: List[LeafDifference] = []

        if len(reference_trajectory) != len(candidate_trajectory):
            differences.append(
                LeafDifference("trajectory.length", len(reference_trajectory), len(candidate_trajectory))
            )
            return ComparisonResult(equivalent=False, differences=differences)

        for ref_snapshot, cand_snapshot in zip(reference_trajectory, candidate_trajectory):
            # Logical order: paired strictly by tick_index, never wall-clock.
            if ref_snapshot.tick_index != cand_snapshot.tick_index:
                differences.append(
                    LeafDifference("trajectory.tick_index", ref_snapshot.tick_index, cand_snapshot.tick_index)
                )
                continue

            for field_name in sorted(COMPARISON_DOMAIN):
                ref_value = ref_snapshot.data.get(field_name)
                cand_value = cand_snapshot.data.get(field_name)
                path = f"tick[{ref_snapshot.tick_index}].{field_name}"
                differences.extend(self._equivalence.compare_value(path, ref_value, cand_value))

        return ComparisonResult(equivalent=(len(differences) == 0), differences=differences)
