from __future__ import annotations

from typing import List

from tools.ssi.docs.document_model import ScientificDocument


REQUIRED_SECTION_TITLES = {
    "Purpose",
    "Final Principle",
}


def validate_document(document: ScientificDocument) -> List[str]:
    errors: List[str] = []
    errors.extend(document.validate())

    section_titles = [section.title.strip() for section in document.sections]
    normalized_titles = {title.lower() for title in section_titles}

    for required in REQUIRED_SECTION_TITLES:
        if required.lower() not in normalized_titles:
            errors.append(f"missing required section: {required}")

    if document.sections:
        first = document.sections[0].title.strip().lower()
        if first != "purpose":
            errors.append("first section must be: Purpose")

    for section in document.sections:
        if "todo" in section.body.lower():
            errors.append(f"section '{section.title}' contains TODO marker")

    return errors


def assert_valid_document(document: ScientificDocument) -> None:
    errors = validate_document(document)
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Document validation failed:\n{joined}")
