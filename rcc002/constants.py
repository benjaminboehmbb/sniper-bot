"""Canonical RCC-002 stage list and schema identifiers.

Transcribed verbatim from the certified RCC-002 specification bundle
(docs/review/RCC_002_AIR4_MIN01_CORRECTED_FULL_SPEC_BUNDLE_2026-07-27.md,
SHA-256 39314fd6b6c186c3bc27932c701a36d1456f8f0a6009518617e6af592cea139a):
RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md §6 (Kanonischer Datenfluss)
for the stage list, and the family-wide `rcc002.stage.*` / `rcc002.state.*` /
`rcc002.view.*` schema-ID references for the schema identifiers.

Pure constants only. No business logic, no I/O.
"""

from __future__ import annotations

import enum


class StageId(enum.Enum):
    """Canonical RCC-002 stage list, in canonical order (Data Pipeline §6).

    Enum member declaration order is the canonical stage order; Python enums
    preserve declaration order, so `list(StageId)` yields the same sequence
    documented in Data Pipeline §6.
    """

    S0_SOURCE = "S0_SOURCE"
    S1_NORMALIZED = "S1_NORMALIZED"
    S2_VALIDATED = "S2_VALIDATED"
    S3_INDICATORS = "S3_INDICATORS"
    S4_SIGNALS = "S4_SIGNALS"
    S5_REGIMES = "S5_REGIMES"
    S6_GATES = "S6_GATES"
    S7_LABELS = "S7_LABELS"
    S8_EXPORT = "S8_EXPORT"


# Stage schema IDs and versions. S8_EXPORT has no stage schema of its own;
# it is defined exclusively via the per-view schemas in VIEW_SCHEMA_ID below
# (Data Pipeline §7.9: "S8 verwendet ausschließlich die nachfolgende
# versionsgebundene Registry ... Jede View ist eine positive, fail-closed
# Feld-Allowlist.").
STAGE_SCHEMA_ID: dict[StageId, str] = {
    StageId.S0_SOURCE: "rcc002.stage.s0-source",
    StageId.S1_NORMALIZED: "rcc002.stage.s1-normalized",
    StageId.S2_VALIDATED: "rcc002.stage.s2-validated",
    StageId.S3_INDICATORS: "rcc002.stage.s3-indicators",
    StageId.S4_SIGNALS: "rcc002.stage.s4-signals",
    StageId.S5_REGIMES: "rcc002.stage.s5-regimes",
    StageId.S6_GATES: "rcc002.stage.s6-gates",
    StageId.S7_LABELS: "rcc002.stage.s7-labels",
}

STAGE_SCHEMA_VERSION: dict[StageId, str] = {
    stage: "1.0.0" for stage in STAGE_SCHEMA_ID
}


def stage_schema_ref(stage: StageId) -> str:
    """Return the fully-qualified '<schema_id>/<version>' schema reference."""
    return f"{STAGE_SCHEMA_ID[stage]}/{STAGE_SCHEMA_VERSION[stage]}"


# Recursive-indicator / regime state-snapshot schemas. Only S3 (Indicator,
# recursive indicators such as EMA/RSI/ATR/ADX/MACD) and S5 (Regime, causal
# persistence of regime_effective) define a state-snapshot schema.
STATE_SCHEMA_ID: dict[StageId, str] = {
    StageId.S3_INDICATORS: "rcc002.state.s3-indicators",
    StageId.S5_REGIMES: "rcc002.state.s5-regimes",
}

STATE_SCHEMA_VERSION: dict[StageId, str] = {
    stage: "1.0.0" for stage in STATE_SCHEMA_ID
}


def state_schema_ref(stage: StageId) -> str:
    """Return the fully-qualified '<schema_id>/<version>' state-schema reference."""
    return f"{STATE_SCHEMA_ID[stage]}/{STATE_SCHEMA_VERSION[stage]}"


class ViewId(enum.Enum):
    """Canonical S8 view identifiers (Data Pipeline §7.9)."""

    RESEARCH_FEATURES = "research-features"
    BACKTEST_INPUTS = "backtest-inputs"
    PAPER = "paper"
    LIVE = "live"
    LABEL_RESEARCH = "label-research"
    AUDIT = "audit"


VIEW_SCHEMA_ID: dict[ViewId, str] = {
    ViewId.RESEARCH_FEATURES: "rcc002.view.research-features",
    ViewId.BACKTEST_INPUTS: "rcc002.view.backtest-inputs",
    ViewId.PAPER: "rcc002.view.paper",
    ViewId.LIVE: "rcc002.view.live",
    ViewId.LABEL_RESEARCH: "rcc002.view.label-research",
    ViewId.AUDIT: "rcc002.view.audit",
}

VIEW_SCHEMA_VERSION: dict[ViewId, str] = {
    view: "1.0.0" for view in VIEW_SCHEMA_ID
}


def view_schema_ref(view: ViewId) -> str:
    """Return the fully-qualified '<schema_id>/<version>' view-schema reference."""
    return f"{VIEW_SCHEMA_ID[view]}/{VIEW_SCHEMA_VERSION[view]}"
