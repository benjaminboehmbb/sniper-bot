from __future__ import annotations

from pathlib import Path
from typing import Dict

from tools.ssi.docs.document_model import DocumentSection, ScientificDocument, build_document
from tools.ssi.docs.document_validator import assert_valid_document
from tools.ssi.docs.markdown_writer import write_markdown


OUTPUT_DIR = Path("docs/ssi/generated")


def build_test_document() -> ScientificDocument:
    return build_document(
        title="SSI GENERATED DOCUMENT TEST",
        date="2026-06-22",
        project="Sniper-Bot",
        platform="State Space Intelligence",
        component="SSI Documentation System",
        classification="Generated Documentation Test",
        status="TEST",
        implementation_status="TEST",
        version="1.0",
        sections=[
            DocumentSection(
                title="Purpose",
                body=(
                    "This generated document validates the end-to-end SSI "
                    "documentation generation pipeline."
                ),
            ),
            DocumentSection(
                title="Validation Scope",
                body=(
                    "This test verifies document model construction, document "
                    "validation, Markdown rendering, and deterministic file output."
                ),
            ),
            DocumentSection(
                title="Final Principle",
                body=(
                    "SSI documentation must be generated, validated, reproducible, "
                    "and traceable."
                ),
            ),
        ],
        related_documents=[
            "SSI_DOCUMENTATION_SYSTEM_V1.md",
        ],
    )


def generate_all() -> Dict[str, Path]:
    documents = {
        "ssi_generated_document_test": build_test_document(),
    }

    outputs: Dict[str, Path] = {}

    for name, document in documents.items():
        assert_valid_document(document)
        output_path = OUTPUT_DIR / f"{name}.md"
        outputs[name] = write_markdown(document, output_path)

    return outputs


def main() -> int:
    outputs = generate_all()

    for name, path in outputs.items():
        print(f"GENERATED {name}: {path}")

    print("SSI_DOC_GENERATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
