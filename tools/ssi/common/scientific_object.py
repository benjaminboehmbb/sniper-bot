from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ScientificObject:
    """
    Base class for immutable scientific SSI objects.

    This class intentionally contains no behavior.
    It marks objects that represent scientific meaning,
    not implementation convenience.
    """

    pass


class HasDeterministicId(Protocol):
    """
    Protocol for SSI objects that expose a deterministic identity.
    """

    def deterministic_id(self) -> str:
        ...