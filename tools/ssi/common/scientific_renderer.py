from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from tools.ssi.common.scientific_artifacts import ScientificArtifacts
from tools.ssi.common.scientific_result import ScientificResult


ResultT = TypeVar("ResultT", bound=ScientificResult)


class ScientificRenderer(ABC, Generic[ResultT]):
    """
    Abstract base class for deterministic rendering of SSI scientific results.

    A renderer converts a ScientificResult into ScientificArtifacts.

    A renderer must never:

    - write files
    - modify results
    - perform scientific analysis
    - execute trading decisions

    It only transforms scientific results into renderable artifacts.
    """

    @abstractmethod
    def render(self, result: ResultT) -> ScientificArtifacts:
        """
        Render a scientific result into scientific artifacts.
        """
        raise NotImplementedError