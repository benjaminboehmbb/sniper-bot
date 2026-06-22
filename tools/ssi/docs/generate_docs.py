from __future__ import annotations

from pathlib import Path
from typing import Dict

from tools.ssi.docs.document_model import DocumentSection, ScientificDocument, build_document
from tools.ssi.docs.document_validator import assert_valid_document
from tools.ssi.docs.markdown_writer import write_markdown


OUTPUT_DIR = Path("docs/ssi/generated")


def build_tsv_interface_specification() -> ScientificDocument:
    return build_document(
        title="TSV INTERFACE SPECIFICATION V1",
        date="2026-06-22",
        project="Sniper-Bot",
        platform="State Space Intelligence (SSI)",
        component="TSV Interface",
        classification="Scientific Interface Contract",
        status="SPECIFICATION ONLY",
        implementation_status="NOT IMPLEMENTED",
        version="1.0",
        sections=[
            DocumentSection(
                title="Purpose",
                body=(
                    "This document defines the formal interface contract between "
                    "the TSV Builder and every downstream SSI module. The purpose "
                    "of the interface is to ensure that every SSI component consumes "
                    "exactly the same canonical state representation. The interface "
                    "prevents schema drift, hidden assumptions, duplicated parsing "
                    "logic, incompatible TSV versions, and inconsistent scientific "
                    "interpretation."
                ),
            ),
            DocumentSection(
                title="Core Principle",
                body=(
                    "Runtime lifecycle data shall never be consumed directly by "
                    "downstream SSI modules. The only accepted scientific "
                    "representation is the Trade State Vector (TSV). TSV is "
                    "therefore the canonical internal language of the entire SSI "
                    "platform."
                ),
            ),
            DocumentSection(
                title="Scope",
                body=(
                    "The interface begins immediately after TSV generation. The "
                    "interface does not define how TSV is generated. Generation is "
                    "specified by the TSV Builder Specification. The interface "
                    "defines only the contract between producer and consumer."
                ),
            ),
            DocumentSection(
                title="Producer",
                body=(
                    "The only authorized producer of TSV datasets is the TSV "
                    "Builder. No other SSI component may generate canonical TSV "
                    "datasets."
                ),
            ),
            DocumentSection(
                title="Consumers",
                body=(
                    "Expected consumers include State Space Builder, Trajectory "
                    "Analysis, Transition Graph Analysis, State Clustering, Basin "
                    "Analysis, Forecasting, Knowledge Extraction, and Governance. "
                    "Every consumer must validate the interface before processing."
                ),
            ),
            DocumentSection(
                title="Required Files",
                body=(
                    "Every valid TSV package shall contain tsv_dataset_v1.csv, "
                    "tsv_dataset_v1.parquet, tsv_dataset_v1_manifest.json, and "
                    "tsv_dataset_v1_summary.md. CSV is intended for inspection. "
                    "Parquet is intended for computation. Manifest is authoritative "
                    "metadata. Summary is human-readable documentation."
                ),
            ),
            DocumentSection(
                title="Required Schema",
                body=(
                    "Every TSV record must contain tsv_id, tsv_version, runtime_id, "
                    "trade_id, snapshot_id, timestamp_utc, tick, side, progress, "
                    "compatibility, stability, confidence, source_file, "
                    "source_row_index, created_at_utc, generator_name, and "
                    "generator_version. Missing required fields invalidate the dataset."
                ),
            ),
            DocumentSection(
                title="Dimension Contract",
                body=(
                    "The four canonical TSV dimensions are Progress, Compatibility, "
                    "Stability, and Confidence. Each dimension shall satisfy "
                    "0.0 <= value <= 1.0. Higher values always indicate stronger or "
                    "healthier state quality. Dimension semantics shall never be "
                    "reversed."
                ),
            ),
            DocumentSection(
                title="Version Contract",
                body=(
                    "Every TSV dataset declares exactly one TSV version. Consumers "
                    "must explicitly list supported versions. Unsupported versions "
                    "must generate a hard validation failure. Silent compatibility "
                    "assumptions are forbidden."
                ),
            ),
            DocumentSection(
                title="Provenance Contract",
                body=(
                    "Every TSV record must be traceable back to its originating "
                    "lifecycle snapshot. Required provenance includes runtime_id, "
                    "trade_id, snapshot_id, timestamp_utc, source_file, "
                    "source_row_index, generator_name, generator_version, and "
                    "tsv_version."
                ),
            ),
            DocumentSection(
                title="Manifest Contract",
                body=(
                    "Every TSV dataset must contain a manifest including runtime_id, "
                    "source files, trade count, snapshot count, TSV count, TSV "
                    "version, generator version, creation timestamp, validation "
                    "status, warnings, errors, input hashes, and output hashes. "
                    "The manifest is the scientific fingerprint of the dataset."
                ),
            ),
            DocumentSection(
                title="Determinism",
                body=(
                    "The interface assumes deterministic generation. Identical inputs "
                    "must always produce identical TSV datasets. No randomness is "
                    "permitted."
                ),
            ),
            DocumentSection(
                title="No-Lookahead Contract",
                body=(
                    "The TSV dataset may contain only information available at or "
                    "before the represented snapshot. Future information is forbidden. "
                    "Outcome labels may exist only as explicitly separated offline "
                    "evaluation fields."
                ),
            ),
            DocumentSection(
                title="Validation Contract",
                body=(
                    "Consumers must validate schema, required fields, version, "
                    "provenance, manifest, identifier uniqueness, and dimension "
                    "bounds. Processing invalid datasets is forbidden."
                ),
            ),
            DocumentSection(
                title="Consumer Responsibilities",
                body=(
                    "Consumers shall validate before processing, preserve provenance, "
                    "reference the consumed manifest, and document produced outputs. "
                    "Consumers shall not reinterpret TSV semantics, modify TSV values, "
                    "silently repair datasets, or bypass validation."
                ),
            ),
            DocumentSection(
                title="Interface Evolution",
                body=(
                    "Breaking interface changes require a new interface version, "
                    "compatibility statement, migration documentation, and affected "
                    "module list. Backward compatibility must never be assumed."
                ),
            ),
            DocumentSection(
                title="Scientific Traceability",
                body=(
                    "Every scientific conclusion shall remain traceable through "
                    "Finding -> Module Output -> TSV Dataset -> TSV Manifest -> "
                    "Lifecycle Snapshot -> Runtime Archive. The traceability chain "
                    "must remain complete."
                ),
            ),
            DocumentSection(
                title="Final Principle",
                body=(
                    "The TSV Interface is the canonical contract of the State Space "
                    "Intelligence Platform. Every SSI component speaks TSV. Every SSI "
                    "dataset is validated through this interface. Every scientific "
                    "conclusion shall remain reproducible through this contract."
                ),
            ),
        ],
        related_documents=[
            "SSI_PLATFORM_BLUEPRINT_V1_2026-06-22.md",
            "TSV_DATA_MODEL_V1_2026-06-22.md",
            "TSV_BUILDER_SPECIFICATION_V1_2026-06-22.md",
        ],
    )


def generate_all() -> Dict[str, Path]:
    documents = {
        "TSV_INTERFACE_SPECIFICATION_V1_2026-06-22": build_tsv_interface_specification(),
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
