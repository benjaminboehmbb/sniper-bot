from __future__ import annotations

from collections import Counter
from typing import Any

from tools.ssi.decision_evidence.decision_evidence_result import (
    DecisionEvidenceResult,
)

from .decision_engine_models import (
    DecisionStatistics,
    ScientificDecision,
)


class DecisionValidator:
    """
    Validates DecisionEvidenceResult and generates deterministic
    ScientificDecision objects with explicit scientific reasoning.
    """

    _REQUIRED_EVIDENCE_TYPES = {
        "RepeatedStateEvidence",
        "NonRepeatedStateEvidence",
        "ForecastEvidence",
        "BehaviourEvidence",
    }

    def validate(
        self,
        evidence_result: DecisionEvidenceResult,
    ) -> tuple[list[ScientificDecision], DecisionStatistics]:
        self._validate_input(evidence_result)

        evidence_items = self._collect_evidence(evidence_result)
        evidence_sufficiency = self._assess_sufficiency(evidence_items)
        evidence_consistency = self._assess_consistency(evidence_items)
        evidence_completeness = self._assess_completeness(evidence_items)
        scientific_confidence = self._assess_confidence(evidence_items)

        findings = self._build_findings(
            evidence_items,
            evidence_sufficiency,
            evidence_consistency,
            evidence_completeness,
            scientific_confidence,
        )

        limitations = self._build_limitations(
            evidence_items,
            evidence_sufficiency,
            evidence_consistency,
            evidence_completeness,
            scientific_confidence,
        )

        scientific_recommendation = self._generate_recommendation(
            evidence_sufficiency,
            evidence_consistency,
            evidence_completeness,
            scientific_confidence,
        )

        decisions = self._build_decisions(
            evidence_result=evidence_result,
            evidence_items=evidence_items,
            evidence_sufficiency=evidence_sufficiency,
            evidence_consistency=evidence_consistency,
            evidence_completeness=evidence_completeness,
            scientific_confidence=scientific_confidence,
            scientific_recommendation=scientific_recommendation,
            findings=findings,
            limitations=limitations,
        )

        statistics = self._build_statistics(decisions)

        return decisions, statistics

    def _validate_input(self, evidence_result: DecisionEvidenceResult) -> None:
        if evidence_result is None:
            raise ValueError("evidence_result must not be None.")

        if evidence_result.evidence is None:
            raise ValueError("evidence must not be None.")

        evidence_ids: set[str] = set()

        for evidence in evidence_result.evidence:
            if evidence.evidence_id.strip() == "":
                raise ValueError("evidence_id must not be empty.")

            if evidence.evidence_id in evidence_ids:
                raise ValueError(
                    f"duplicate evidence_id: {evidence.evidence_id}"
                )

            evidence_ids.add(evidence.evidence_id)

    def _collect_evidence(self, evidence_result: DecisionEvidenceResult) -> list[Any]:
        return list(evidence_result.evidence)

    def _assess_sufficiency(self, evidence_items: list[Any]) -> str:
        if not evidence_items:
            return "INSUFFICIENT"

        valid_items = [
            item
            for item in evidence_items
            if item.metadata.get("validation_status", "UNKNOWN") == "PASS"
        ]

        if not valid_items:
            return "INSUFFICIENT"

        return "SUFFICIENT"

    def _assess_consistency(self, evidence_items: list[Any]) -> str:
        if not evidence_items:
            return "CONSISTENT"

        validation_statuses = {
            item.metadata.get("validation_status", "UNKNOWN")
            for item in evidence_items
        }

        if validation_statuses == {"PASS"}:
            return "CONSISTENT"

        if "PASS" in validation_statuses:
            return "PARTIALLY_CONSISTENT"

        return "CONTRADICTORY"

    def _assess_completeness(self, evidence_items: list[Any]) -> str:
        if not evidence_items:
            return "INCOMPLETE"

        evidence_types = {item.evidence_type for item in evidence_items}
        missing_types = self._REQUIRED_EVIDENCE_TYPES - evidence_types

        if not missing_types:
            return "COMPLETE"

        if evidence_types:
            return "PARTIAL"

        return "INCOMPLETE"

    def _assess_confidence(self, evidence_items: list[Any]) -> str:
        if not evidence_items:
            return "LOW"

        scores: list[float] = []

        for item in evidence_items:
            metadata = item.metadata
            scores.append(float(metadata.get("support_ratio", 0.0)))
            scores.append(float(metadata.get("confidence", 0.0)))
            scores.append(float(metadata.get("scientific_score", 0.0)))

        mean_score = sum(scores) / len(scores)

        if mean_score >= 0.75:
            return "HIGH"

        if mean_score >= 0.40:
            return "MEDIUM"

        return "LOW"

    def _build_findings(
        self,
        evidence_items: list[Any],
        evidence_sufficiency: str,
        evidence_consistency: str,
        evidence_completeness: str,
        scientific_confidence: str,
    ) -> list[str]:
        evidence_types = sorted({item.evidence_type for item in evidence_items})

        evidence_types_text = ", ".join(evidence_types)
        if not evidence_types_text:
            evidence_types_text = "none"

        return [
            f"Evidence items evaluated: {len(evidence_items)}.",
            f"Evidence types present: {evidence_types_text}.",
            f"Evidence sufficiency assessment: {evidence_sufficiency}.",
            f"Evidence consistency assessment: {evidence_consistency}.",
            f"Evidence completeness assessment: {evidence_completeness}.",
            f"Scientific confidence assessment: {scientific_confidence}.",
        ]

    def _build_limitations(
        self,
        evidence_items: list[Any],
        evidence_sufficiency: str,
        evidence_consistency: str,
        evidence_completeness: str,
        scientific_confidence: str,
    ) -> list[str]:
        limitations: list[str] = []

        if evidence_sufficiency == "INSUFFICIENT":
            limitations.append("Available evidence is insufficient.")

        if evidence_consistency != "CONSISTENT":
            limitations.append(
                "Evidence consistency is limited or contradictory."
            )

        if evidence_completeness != "COMPLETE":
            present_types = {item.evidence_type for item in evidence_items}
            missing_types = sorted(self._REQUIRED_EVIDENCE_TYPES - present_types)

            missing_text = ", ".join(missing_types)
            if not missing_text:
                missing_text = "none"

            limitations.append(f"Missing evidence types: {missing_text}.")

        if scientific_confidence == "LOW":
            limitations.append(
                "Scientific confidence is low under deterministic V1 rules."
            )

        if not limitations:
            limitations.append("No deterministic V1 limitations detected.")

        return limitations

    def _generate_recommendation(
        self,
        evidence_sufficiency: str,
        evidence_consistency: str,
        evidence_completeness: str,
        scientific_confidence: str,
    ) -> str:
        if evidence_sufficiency == "INSUFFICIENT":
            return "INSUFFICIENT_EVIDENCE"

        if evidence_consistency == "CONTRADICTORY":
            return "CONTRADICTORY"

        if evidence_completeness == "COMPLETE" and scientific_confidence == "HIGH":
            return "STRONGLY_SUPPORTED"

        if scientific_confidence in {"HIGH", "MEDIUM"}:
            return "WEAKLY_SUPPORTED"

        return "REVIEW_REQUIRED"

    def _build_decisions(
        self,
        evidence_result: DecisionEvidenceResult,
        evidence_items: list[Any],
        evidence_sufficiency: str,
        evidence_consistency: str,
        evidence_completeness: str,
        scientific_confidence: str,
        scientific_recommendation: str,
        findings: list[str],
        limitations: list[str],
    ) -> list[ScientificDecision]:
        evidence_ids = [evidence.evidence_id for evidence in evidence_items]

        decision_status = self._map_recommendation_to_status(
            scientific_recommendation
        )

        reasoning_summary = self._build_reasoning_summary(
            scientific_recommendation=scientific_recommendation,
            decision_status=decision_status,
        )

        metadata: dict[str, Any] = {
            "source_evidence_count": len(evidence_ids),
            "source_validation_status": evidence_result.validation_summary.get(
                "status",
                "UNKNOWN",
            ),
            "evidence_types": sorted(
                {item.evidence_type for item in evidence_items}
            ),
            "reasoning_version": "scientific_reasoning_engine_v1",
        }

        return [
            ScientificDecision(
                decision_id="DECISION-SRE-V1-001",
                decision_status=decision_status,
                evidence_ids=evidence_ids,
                explanation=reasoning_summary,
                supporting_evidence_count=len(evidence_ids),
                evidence_sufficiency=evidence_sufficiency,
                evidence_consistency=evidence_consistency,
                evidence_completeness=evidence_completeness,
                scientific_confidence=scientific_confidence,
                scientific_recommendation=scientific_recommendation,
                findings=findings,
                limitations=limitations,
                reasoning_summary=reasoning_summary,
                metadata=metadata,
            )
        ]

    def _map_recommendation_to_status(
        self,
        scientific_recommendation: str,
    ) -> str:
        if scientific_recommendation in {
            "STRONGLY_SUPPORTED",
            "WEAKLY_SUPPORTED",
        }:
            return "SUPPORTED"

        if scientific_recommendation == "CONTRADICTORY":
            return "NOT_SUPPORTED"

        return "UNDECIDED"

    def _build_reasoning_summary(
        self,
        scientific_recommendation: str,
        decision_status: str,
    ) -> str:
        return (
            "Scientific reasoning produced recommendation "
            f"{scientific_recommendation} and decision status "
            f"{decision_status}."
        )

    def _build_statistics(
        self,
        decisions: list[ScientificDecision],
    ) -> DecisionStatistics:
        counter = Counter(decision.decision_status for decision in decisions)

        return DecisionStatistics(
            total_decisions=len(decisions),
            decisions_by_status=dict(counter),
        )
