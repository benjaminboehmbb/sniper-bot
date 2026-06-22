from __future__ import annotations

from pathlib import Path
from typing import List

from tools.ssi.docs.document_model import ScientificDocument


def _heading(level: int, title: str) -> str:
    if level < 1 or level > 6:
        raise ValueError(f"invalid heading level: {level}")
    return f"{'#' * level} {title.strip()}"


def render_markdown(document: ScientificDocument) -> str:
    errors = document.validate()
    if errors:
        joined = "\n".join(f"- {error}" for error in errors)
        raise ValueError(f"Invalid scientific document:\n{joined}")

    lines: List[str] = []

    lines.append(_heading(1, document.title))
    lines.append("")
    lines.append("Date:")
    lines.append(document.date)
    lines.append("")
    lines.append("Project:")
    lines.append(document.project)
    lines.append("")
    lines.append("Platform:")
    lines.append(document.platform)
    lines.append("")
    lines.append("Component:")
    lines.append(document.component)
    lines.append("")
    lines.append("Classification:")
    lines.append(document.classification)
    lines.append("")
    lines.append("Status:")
    lines.append(document.status)
    lines.append("")
    lines.append("Implementation Status:")
    lines.append(document.implementation_status)
    lines.append("")
    lines.append("Version:")
    lines.append(document.version)
    lines.append("")
    lines.append("---")
    lines.append("")

    if document.related_documents:
        lines.append("# Related Documents")
        lines.append("")
        for item in document.related_documents:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("---")
        lines.append("")

    for section in document.sections:
        lines.append(_heading(section.level, section.title))
        lines.append("")
        lines.append(section.body.strip())
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown(document: ScientificDocument, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(document), encoding="utf-8")
    return output_path
