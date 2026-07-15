"""TD005-IU-022: Active/Deferred Scope Boundary Realization Unit.

Realizes TD005-SO-021's own scope-stability and drift-sensitivity behaviour,
per TD005-ID-015's own re-derivation method: a fresh, static, AST-based
import-closure walk from run_engine.main, re-run at the start of every
Replay Session and Observation act, never via a cached or hand-maintained
list (TD005-SI-020, TD005-II-008: static analysis only, never dynamic
import execution that could itself alter Run Engine state).

State model (TD005-SO-021, unmodified): Stable -> Drift-Detected -> Re-Confirmed.

Traceability: TD005-SO-021; TD005-ARC-020; TD005-AI-011; TD005-ID-014, TD005-ID-015.
"""

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from typing import FrozenSet, List, Optional

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# RETAIN-Deferred-Scope modules under ADR-012 (Repository Consolidation
# Architecture RC-AD-005) - independently re-confirmed inactive at every
# stage of this governance chain, most recently in the Implementation
# Specification's own Section 5.
RETAIN_DEFERRED_SCOPE: FrozenSet[str] = frozenset(
    {
        "run_engine/core/config.py",
        "run_engine/runtime/recovery.py",
        "run_engine/runtime/snapshot.py",
        "run_engine/runtime/state_memory.py",
    }
)


@dataclass(frozen=True)
class ScopePartition:
    active: FrozenSet[str]
    inactive: FrozenSet[str]


def _resolve_module(mod: str) -> Optional[str]:
    parts = mod.split(".")
    if parts[0] != "run_engine":
        return None
    candidate = os.path.join(*parts) + ".py"
    if os.path.isfile(os.path.join(REPO_ROOT, candidate)):
        return candidate.replace(os.sep, "/")
    candidate_init = os.path.join(*parts, "__init__.py")
    if os.path.isfile(os.path.join(REPO_ROOT, candidate_init)):
        return candidate_init.replace(os.sep, "/")
    return None


def _imports_of(rel_path: str) -> List[str]:
    """Static AST parse only; never imports or executes the module (TD005-II-008)."""
    full_path = os.path.join(REPO_ROOT, rel_path)
    with open(full_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=full_path)

    mods: List[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                pkg_parts = rel_path.split("/")[:-1]
                up = node.level - 1
                if up > 0:
                    pkg_parts = pkg_parts[:-up] if up <= len(pkg_parts) else []
                base = ".".join(pkg_parts)
                full = (base + "." + node.module) if (base and node.module) else (node.module or base)
                if full:
                    mods.append(full)
            elif node.module:
                mods.append(node.module)
    return mods


def derive_scope_partition() -> ScopePartition:
    """Fresh static AST-based import closure from run_engine.main (TD005-ID-015)."""
    visited: set = set()
    queue = ["run_engine/main.py"]
    while queue:
        current = queue.pop()
        if current in visited:
            continue
        visited.add(current)
        for mod in _imports_of(current):
            resolved = _resolve_module(mod)
            if resolved and resolved not in visited:
                queue.append(resolved)

    all_files: set = set()
    for root, _dirs, files in os.walk(os.path.join(REPO_ROOT, "run_engine")):
        for fn in files:
            if fn.endswith(".py"):
                rel = os.path.relpath(os.path.join(root, fn), REPO_ROOT).replace(os.sep, "/")
                all_files.add(rel)

    inactive = all_files - visited
    return ScopePartition(active=frozenset(visited), inactive=frozenset(inactive))


class ScopeBoundary:
    """TD005-IU-022's own realization: Stable -> Drift-Detected -> Re-Confirmed."""

    def __init__(self, partition_provider=derive_scope_partition) -> None:
        # partition_provider defaults to the real static AST-based re-derivation;
        # tests may substitute a stub to exercise the Drift-Detected transition
        # without altering the repository (TD005-II-008 remains satisfied by
        # the default, production provider).
        self._provider = partition_provider
        self._state = "Stable"
        self._partition: Optional[ScopePartition] = None

    @property
    def state(self) -> str:
        return self._state

    @property
    def partition(self) -> Optional[ScopePartition]:
        return self._partition

    def confirm(self) -> ScopePartition:
        """Re-evaluate the scope boundary; called at the start of every session
        (TD005-SI-020), never assumed unchanged from a prior evaluation.

        Stable is the steady state for as long as the partition does not
        change between confirmations; Drift-Detected -> Re-Confirmed is only
        reached when an actual partition change is observed (TD005-SO-021's
        own state model: Illegal: Drift-Detected -> Stable without an
        intervening Re-Confirmed)."""
        fresh = self._provider()

        if self._partition is not None and fresh.active != self._partition.active:
            self._state = "Drift-Detected"
            self._partition = fresh
            self._state = "Re-Confirmed"
        else:
            self._partition = fresh
            if self._state == "Drift-Detected":
                self._state = "Re-Confirmed"
            # else: remains Stable (or Re-Confirmed, once already reached).

        return self._partition

    def is_active(self, rel_path: str) -> bool:
        if self._partition is None:
            self.confirm()
        return rel_path in self._partition.active

    def uncovered_active_modules(self, covered: FrozenSet[str]) -> FrozenSet[str]:
        """Active modules not present in a given coverage set (TD005-IU-018 support)."""
        if self._partition is None:
            self.confirm()
        return frozenset(self._partition.active) - frozenset(covered)
