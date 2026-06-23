from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from .result import DecisionEvidenceResult


class DecisionEvidenceRenderer:
    """
    Renders DecisionEvidenceResult into deterministic scientific artifacts.
    """

    def render(
        self,
        result: DecisionEvidenceResult,
    ) -> dict[str, Any]:
        """
        Render result as JSON and Markdown artifacts.
        """

        payload = asdict(result)

        return {
            "decision_evidence.json": json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            ),
            "decision_evidence_summary.md": self._render_summary(
                result
            ),
        }

    def _render_summary(
        self,
        result: DecisionEvidenceResult,
    ) -> str:
        """
        Render Markdown summary.
        """

        lines = [
            "# SSI Decision Evidence V1 Summary",
            "",
            "## Statistics",
            "",
            f"Total evidence: {result.statistics.total_evidence}",
            "",
            "## Evidence by Type",
            "",
        ]

        for evidence_type, count in sorted(
            result.statistics.evidence_by_type.items()
        ):
            lines.append(f"- {evidence_type}: {count}")

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