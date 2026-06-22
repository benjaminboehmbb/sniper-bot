from __future__ import annotations

from dataclasses import dataclass, field

from tools.ssi.common.scientific_object import ScientificObject


@dataclass(frozen=True, slots=True)
class ScientificResultMetadata(ScientificObject):
    runtime_id: str
    input_path: str
    result_version: str
    conceptual_layer: str
    processing_layer: str
    source_dataset_type: str


@dataclass(frozen=True, slots=True)
class ScientificResult(ScientificObject):
    metadata: ScientificResultMetadata
    validation_status: str
    warnings: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def is_pass(self) -> bool:
        return self.validation_status == "PASS"

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0