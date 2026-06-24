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
        Render result as JSON and Markdown artifacts.
        """

        payload = asdict(result)

        return {
            "decision_engine.json": json.dumps(
                payload,
                indent=2,
                sort_keys=True,
            ),
            "decision_engine_summary.md": self._render_summary(result),
        }

    def _render_summary(
        self,
        result: DecisionResult,
    ) -> str:
        """
        Render Markdown summary.
        """

        lines = [
            "# SSI Decision Engine / Scientific Reasoning Engine V1 Summary",
            "",
            "## Statistics",
            "",
            f"Total decisions: {result.statistics.total_decisions}",
            "",
            "## Decisions by Status",
            "",
        ]

        for status, count in sorted(result.statistics.decisions_by_status.items()):
            lines.append(f"- {status}: {count}")

        lines.extend(
            [
                "",
                "## Scientific Decisions",
                "",
            ]
        )

        for decision in result.decisions:
            lines.extend(
                [
                    f"### {decision.decision_id}",
                    "",
                    f"Decision status: {decision.decision_status}",
                    f"Scientific recommendation: {decision.scientific_recommendation}",
                    f"Evidence sufficiency: {decision.evidence_sufficiency}",
                    f"Evidence consistency: {decision.evidence_consistency}",
                    f"Evidence completeness: {decision.evidence_completeness}",
                    f"Scientific confidence: {decision.scientific_confidence}",
                    f"Supporting evidence count: {decision.supporting_evidence_count}",
                    "",
                    "Reasoning summary:",
                    "",
                    decision.reasoning_summary,
                    "",
                    "Findings:",
                    "",
                ]
            )

            for finding in decision.findings:
                lines.append(f"- {finding}")

            lines.extend(
                [
                    "",
                    "Limitations:",
                    "",
                ]
            )

            for limitation in decision.limitations:
                lines.append(f"- {limitation}")

            lines.extend(
                [
                    "",
                    "Explanation:",
                    "",
                    decision.explanation,
                    "",
                ]
            )

        lines.extend(
            [
                "## Validation Summary",
                "",
            ]
        )

        for key, value in sorted(result.validation_summary.items()):
            lines.append(f"- {key}: {value}")

        return "\n".join(lines) + "\n"
