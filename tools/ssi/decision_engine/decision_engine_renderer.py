from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from .decision_engine_result import DecisionResult


class DecisionEngineRenderer:
    """
    Renders DecisionResult into deterministic scientific artifacts.
    """

    def render(
        self,
        result: DecisionResult,
    ) -> dict[str, Any]:
        """
        Render DecisionResult as JSON and Markdown artifacts.
        """

        payload = asdict(result)

        return {
            "decision_engine.json": json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            ),
            "decision_engine_summary.md": self._render_summary(
                result
            ),
        }

    def _render_summary(
        self,
        result: DecisionResult,
    ) -> str:
        """
        Render Markdown summary.
        """

        lines = [
            "# SSI Decision Engine V1 Summary",
            "",
            "## Statistics",
            "",
            f"Total decisions: {result.statistics.total_decisions}",
            "",
            "## Decisions by Status",
            "",
        ]

        for status, count in sorted(
            result.statistics.decisions_by_status.items()
        ):
            lines.append(f"- {status}: {count}")

        lines.extend(
            [
                "",
                "## Validation Summary",
                "",
            ]
        )

        for key, value in sorted(
            result.validation_summary.items()
        ):
            lines.append(f"- {key}: {value}")

        return "\n".join(lines) + "\n"