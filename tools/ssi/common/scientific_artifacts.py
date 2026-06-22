from __future__ import annotations

from dataclasses import dataclass, field

from tools.ssi.common.scientific_object import ScientificObject


@dataclass(frozen=True, slots=True)
class CSVArtifact(ScientificObject):
    filename: str
    header: list[str]
    rows: list[list[str]]


@dataclass(frozen=True, slots=True)
class TextArtifact(ScientificObject):
    filename: str
    content: str


@dataclass(frozen=True, slots=True)
class JSONArtifact(ScientificObject):
    filename: str
    content: dict


@dataclass(frozen=True, slots=True)
class ScientificArtifacts(ScientificObject):
    csv_artifacts: tuple[CSVArtifact, ...] = field(default_factory=tuple)
    text_artifacts: tuple[TextArtifact, ...] = field(default_factory=tuple)
    json_artifacts: tuple[JSONArtifact, ...] = field(default_factory=tuple)

    def total_count(self) -> int:
        return (
            len(self.csv_artifacts)
            + len(self.text_artifacts)
            + len(self.json_artifacts)
        )