from __future__ import annotations

from datetime import datetime, timezone

from tools.ssi.common.scientific_artifacts import (
    CSVArtifact,
    JSONArtifact,
    ScientificArtifacts,
    TextArtifact,
)
from tools.ssi.common.scientific_renderer import ScientificRenderer
from tools.ssi.knowledge.knowledge_extraction_result import KnowledgeExtractionResult


class KnowledgeExtractionRenderer(ScientificRenderer[KnowledgeExtractionResult]):
    def render(
        self,
        result: KnowledgeExtractionResult,
    ) -> ScientificArtifacts:
        return ScientificArtifacts(
            csv_artifacts=(
                _render_knowledge_items(result),
            ),
            text_artifacts=(
                _render_report(result),
            ),
            json_artifacts=(
                _render_manifest(result),
            ),
        )


def _format_float(value: float) -> str:
    return f"{value:.10f}"


def _render_knowledge_items(result: KnowledgeExtractionResult) -> CSVArtifact:
    rows = []

    for item in result.knowledge_items:
        rows.append([
            item.knowledge_id,
            item.knowledge_type,
            item.description,
            str(item.support_count),
            _format_float(item.support_ratio),
            _format_float(item.confidence),
            _format_float(item.scientific_score),
            item.runtime_id,
            item.knowledge_version,
            item.evidence_source,
            item.source_candidate_id,
            item.validation_status,
        ])

    return CSVArtifact(
        filename="knowledge_items_v1.csv",
        header=[
            "knowledge_id",
            "knowledge_type",
            "description",
            "support_count",
            "support_ratio",
            "confidence",
            "scientific_score",
            "runtime_id",
            "knowledge_version",
            "evidence_source",
            "source_candidate_id",
            "validation_status",
        ],
        rows=rows,
    )


def _render_report(result: KnowledgeExtractionResult) -> TextArtifact:
    m = result.metrics
    assert m is not None

    lines = [
        "# SSI KNOWLEDGE EXTRACTION V1 REPORT",
        "",
        f"Runtime ID: {result.metadata.runtime_id}",
        "",
        "## Summary",
        "",
        f"Knowledge candidates: {m.candidate_count}",
        f"Knowledge items: {m.knowledge_count}",
        f"Validation pass count: {m.validation_pass_count}",
        f"Validation fail count: {m.validation_fail_count}",
        "",
        "Validation:",
        result.validation_status,
        "",
        "## Knowledge Items",
        "",
    ]

    for item in result.knowledge_items:
        lines.extend([
            f"### {item.knowledge_type}",
            "",
            item.description,
            "",
            f"Support count: {item.support_count}",
            f"Support ratio: {_format_float(item.support_ratio)}",
            f"Confidence: {_format_float(item.confidence)}",
            f"Scientific score: {_format_float(item.scientific_score)}",
            "",
        ])

    lines.extend([
        "## Interpretation Boundary",
        "",
        "This report describes validated deterministic knowledge only.",
        "It does not generate rules, recommendations, optimization or execution decisions.",
    ])

    return TextArtifact(
        filename="knowledge_extraction_report.md",
        content="\n".join(lines),
    )


def _render_manifest(result: KnowledgeExtractionResult) -> JSONArtifact:
    m = result.metrics
    assert m is not None

    return JSONArtifact(
        filename="knowledge_extraction_manifest.json",
        content={
            "artifact_type": "knowledge_extraction_v1",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_id": result.metadata.runtime_id,
            "validation_status": result.validation_status,
            "candidate_count": m.candidate_count,
            "knowledge_count": m.knowledge_count,
            "validation_pass_count": m.validation_pass_count,
            "validation_fail_count": m.validation_fail_count,
        },
    )