from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from tools.ssi.common.scientific_artifacts import ScientificArtifacts


class ScientificPersistence(ABC):
    """
    Abstract base class for deterministic persistence of SSI scientific artifacts.
    """

    @abstractmethod
    def persist(
        self,
        artifacts: ScientificArtifacts,
        output_dir: Path,
    ) -> list[Path]:
        pass