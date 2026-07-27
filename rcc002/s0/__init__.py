"""S0_SOURCE — raw source artifacts and the source_manifest.

Per RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md §7.1: S0 consists of
two separate normative objects — unmodified source artifacts, and exactly
one associated source_manifest. Source bytes are never modified. This
subpackage implements the source_manifest model and the file-level ingestion
mechanics (integrity checks, legacy alias migration); it never parses source
bytes into row-level canonical schema (that is S1's responsibility, per
Data Validation §6.1: "Nur VERIFIED darf regulär in S1 eingehen.").
"""
