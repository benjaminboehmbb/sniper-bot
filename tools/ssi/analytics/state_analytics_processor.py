from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.ssi.analytics.load_tsv import load_tsv_rows, require_columns
from tools.ssi.analytics.state_analytics_result import (
    StateAnalyticsResult,
    build_state_analytics_metadata,
)
from tools.ssi.analytics.state_key import REQUIRED_STATE_KEY_COLUMNS
from tools.ssi.analytics.state_space_summary import summarize_state_space
from tools.ssi.common.scientific_object import ScientificObject
from tools.ssi.common.scientific_processor import ScientificProcessor


@dataclass(frozen=True, slots=True)
class StateAnalyticsInput(ScientificObject):
    input_path: Path
    runtime_id: str


class StateAnalyticsProcessor(
    ScientificProcessor[StateAnalyticsInput, StateAnalyticsResult]
):
    def validate_input(self, input_object: StateAnalyticsInput) -> None:
        if input_object.runtime_id.strip() == "":
            raise ValueError("runtime_id must not be empty")

        if not input_object.input_path.exists():
            raise ValueError(f"input_path does not exist: {input_object.input_path}")

        if not input_object.input_path.is_file():
            raise ValueError(f"input_path is not a file: {input_object.input_path}")

        if input_object.input_path.stat().st_size <= 0:
            raise ValueError(f"input_path is empty: {input_object.input_path}")

    def process(self, input_object: StateAnalyticsInput) -> StateAnalyticsResult:
        self.validate_input(input_object)

        rows, header = load_tsv_rows(input_object.input_path)
        require_columns(header, REQUIRED_STATE_KEY_COLUMNS)

        summary = summarize_state_space(rows, header)

        return StateAnalyticsResult(
            metadata=build_state_analytics_metadata(
                runtime_id=input_object.runtime_id,
                input_path=str(input_object.input_path),
            ),
            validation_status="PASS",
            summary=summary,
        )