"""RCC-002 S8_EXPORT: consumer view projection, manifest, and publication
package.

Authorized implementation boundary (S8 Implementation Readiness Review
RR-004 SS9): exact projections for the six registered views; S7 row/key/
order/value/count reconciliation; stage- and prefix-based leakage
rejection; canonicalization and deterministic identity builders; Source,
Stage, Run, Dataset, Review, and Reproduction Manifest builders;
structural and semantic manifest validation; Dataset Manifest output
restricted to 1.0.1; artifact inventory, parent, and lineage validation;
temporary/failed/quarantined/candidate state handling; atomic publication
mechanics; and release-ledger generation.

This package never generates or publishes a real dataset and never
performs live or paper production execution; ``rcc002.s8.publication``
only ever writes under an explicit, caller-supplied directory (a sandbox
in tests), never a hardcoded or default repository path.
"""

from __future__ import annotations

from rcc002.s8.field_registry import FIELD_LEAKAGE_CLASS, FIELD_OWNER_STAGE, FIELD_REGISTRY_SHA256
from rcc002.s8.projection import flatten_row, project_rows, project_view
from rcc002.s8.reconciliation import reconcile_row_identity, reconcile_view_artifact
from rcc002.s8.views import VIEW_DEFINITIONS, VIEW_ORDER, ViewDefinition

__all__ = [
    "FIELD_LEAKAGE_CLASS",
    "FIELD_OWNER_STAGE",
    "FIELD_REGISTRY_SHA256",
    "VIEW_DEFINITIONS",
    "VIEW_ORDER",
    "ViewDefinition",
    "flatten_row",
    "project_rows",
    "project_view",
    "reconcile_row_identity",
    "reconcile_view_artifact",
]
