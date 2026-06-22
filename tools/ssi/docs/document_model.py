from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class DocumentSection:
    title: str
    body: str
    level: int = 1

    def validate(self) -> List[str]:
        errors: List[str] = []

        if not self.title.strip():
            errors.append("section title is empty")

        if not self.body.strip():
            errors.append(f"section '{self.title}' body is empty")

        if self.level < 1 or self.level > 6:
            errors.append(f"section '{self.title}' has invalid heading level: {self.level}")

        return errors


@dataclass(frozen=True)
class ScientificDocument:
    title: str
    date: str
    project: str
    platform: str
    component: str
    classification: str
    status: str
    implementation_status: str
    version: str
    sections: List[DocumentSection] = field(default_factory=list)
    related_documents: Optional[List[str]] = None

    def validate(self) -> List[str]:
        errors: List[str] = []

        required_fields = {
            "title": self.title,
            "date": self.date,
            "project": self.project,
            "platform": self.platform,
            "component": self.component,
            "classification": self.classification,
            "status": self.status,
            "implementation_status": self.implementation_status,
            "version": self.version,
        }

        for name, value in required_fields.items():
            if not str(value).strip():
                errors.append(f"missing required document field: {name}")

        if not self.sections:
            errors.append("document has no sections")

        seen_titles = set()
        for section in self.sections:
            normalized = section.title.strip().lower()
            if normalized in seen_titles:
                errors.append(f"duplicate section title: {section.title}")
            seen_titles.add(normalized)
            errors.extend(section.validate())

        return errors


def build_document(
    *,
    title: str,
    date: str,
    project: str,
    platform: str,
    component: str,
    classification: str,
    status: str,
    implementation_status: str,
    version: str,
    sections: List[DocumentSection],
    related_documents: Optional[List[str]] = None,
) -> ScientificDocument:
    document = ScientificDocument(
        title=title,
        date=date,
        project=project,
        platform=platform,
        component=component,
        classification=classification,
        status=status,
        implementation_status=implementation_status,
        version=version,
        sections=sections,
        related_documents=related_documents,
    )

    errors = document.validate()
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Invalid scientific document:\n{joined}")

    return document
