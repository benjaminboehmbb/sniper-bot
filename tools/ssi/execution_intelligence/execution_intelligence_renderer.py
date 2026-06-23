from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from .execution_intelligence_result import ExecutionIntelligenceResult


class ExecutionIntelligenceRenderer:
    """
    Renders ExecutionIntelligenceResult into deterministic scientific artifacts.
    """

    def render(
        self,
        result: ExecutionIntelligenceResult,
    ) -> dict[str, Any]:
        """
        Render ExecutionIntelligenceResult as JSON and Markdown artifacts.
        """

        payload = asdict(result)

        return {
            "execution_intelligence.json": json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            ),
            "execution_intelligence_summary.md": self._render_summary(
                result
            ),
        }

    def _render_summary(
        self,
        result: ExecutionIntelligenceResult,
    ) -> str:
        """
        Render Markdown summary.
        """

        lines = [
            "# SSI Execution Intelligence V1 Summary",
            "",
            "## Statistics",
            "",
            f"Total intents: {result.statistics.total_intents}",
            "",
            "## Intents by Status",
            "",
        ]

        for status, count in sorted(
            result.statistics.intents_by_status.items()
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