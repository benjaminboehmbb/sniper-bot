"""Versioned `source_row_id` canonicalization.

Data Pipeline §7.2: "`source_row_id` identifiziert die normalisierte Zeile
innerhalb des `source_snapshot_id` deterministisch. Seine Vorabbildung und
Kanonisierungsregel müssen versioniert sein." Data Validation §7.1:
"`source_row_id` muss deterministisch als UTF-8-String erzeugt werden. Eine
parallele typabhängige Darstellung als Integer ist unzulässig."

Unlike `source_snapshot_id` (a cross-cutting Reproducibility identity — see
rcc002/IMPLEMENTATION_BLOCKERS.md), `source_row_id` is not listed among
Reproducibility §5.1's "Erforderliche IDs" — it is S1's own stage-local row
identifier. The specification requires it to be deterministic, string-typed,
and governed by a *versioned* rule, but explicitly leaves the concrete rule
to be defined and versioned by the implementation (the same pattern already
used for the S0/S1 legacy-alias migration profiles). This module defines and
versions exactly one such rule.
"""

from __future__ import annotations

SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID = "RCC002_S1_SOURCE_ROW_ID_V1"

# Zero-padding width for the row-index component. Chosen generously (20
# digits comfortably exceeds any realistic single-source row count) so that
# lexicographic string ordering matches numeric ordering, which is useful
# for diagnostics; the specification does not require this property, but it
# does not forbid it either, and no canonical field name or type is
# affected by it (`source_row_id` remains an opaque UTF-8 string).
_ROW_INDEX_WIDTH = 20


def compute_source_row_id(source_snapshot_id: str, original_row_index: int) -> str:
    """Deterministically derive `source_row_id` for one original source row.

    `original_row_index` MUST be the row's zero-based position in the
    *original, pre-sort* source file order (Data Validation §8.5: "die
    ursprüngliche Reihenfolge über `source_row_id` erhalten bleibt"), not
    its position after any deterministic S1 re-sort.
    """
    if original_row_index < 0:
        raise ValueError("original_row_index must be non-negative")
    return (
        f"{SOURCE_ROW_ID_CANONICALIZATION_PROFILE_ID}:"
        f"{source_snapshot_id}:"
        f"{original_row_index:0{_ROW_INDEX_WIDTH}d}"
    )
