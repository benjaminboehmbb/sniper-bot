"""The six registered S8 views (Data Pipeline Specification SS7.9,
Reproducibility and Manifest Specification SS8.7).

Every view's ordered field list is *derived*, not transcribed a second
time: it is the concatenation of ``FIELD_REGISTRY_GROUPS`` entries for the
view's allowed producer stages, in stage order (SS7.9.3 confirms this is
exactly the certified materialized ordering for all six views; a focused
test re-derives and byte-compares against the certified allowlists). This
avoids duplicating six ~232/534-entry field lists as separate normative
constants.

Only ``research-features``, ``backtest-inputs``, ``paper`` and ``live``
share the four-way-identical 232-field, S7-excluded allowlist; only
``label-research`` and ``audit`` share the 534-field, S7-included one
(SS7.9.4). ``audit`` is schema version ``2.0.0`` -- note that
``rcc002.constants.VIEW_SCHEMA_VERSION`` maps every ``ViewId`` including
``AUDIT`` to ``"1.0.0"``, which disagrees with the certified SS8.7 table
for audit; this module uses the certified version directly rather than
that top-level constant (see the S8 implementation report for this
finding). ``rcc002.constants.ViewId``/``VIEW_SCHEMA_ID`` are otherwise
reused unchanged.
"""

from __future__ import annotations

import dataclasses

from rcc002.constants import StageId, VIEW_SCHEMA_ID, ViewId, stage_schema_ref
from rcc002.s8.canonical import canonical_sha256
from rcc002.s8.field_registry import FIELD_LEAKAGE_CLASS, FIELD_OWNER_STAGE, FIELD_REGISTRY_GROUPS
from rcc002.s8.reason_codes import FieldRegistryError


# Stage order per Reproducibility and Manifest Specification SS8.7 / Data
# Pipeline Specification SS6.2. S8_EXPORT itself never appears as an
# "allowed producer stage" for a data view.
_BASE_STAGE_ORDER: tuple[str, ...] = (
    "S0_SOURCE",
    "S1_NORMALIZED",
    "S2_VALIDATED",
    "S3_INDICATORS",
    "S4_SIGNALS",
    "S5_REGIMES",
    "S6_GATES",
)
_LABEL_STAGE = "S7_LABELS"

# Certified allowlist hashes (SS8.7 table); independent literals, not
# derived from the computed hash below, so a golden test can prove the two
# agree instead of only ever agreeing with itself.
_NON_LABEL_ALLOWLIST_SHA256 = (
    "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"
)
_LABEL_ALLOWLIST_SHA256 = (
    "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"
)

# Canonical primary key (Data Pipeline Specification SS7.3/SS7.9.5): the
# certified single-provider, consolidated scope of all six registered S8
# views. Registered on every ``ViewDefinition`` as the schema-declared
# ``primary_key_fields`` (SS7.9.5 registry key) rather than assumed by
# reconciliation code.
_PRIMARY_KEY_FIELDS: tuple[str, ...] = (
    "market_type",
    "symbol",
    "interval",
    "open_time",
)

# SS7.9.5 registry key, identical for all six views.
_COMPATIBILITY_PROFILE_ID = "RCC002_VIEW_SCHEMA_COMPATIBILITY_V1"


def _group_fields(stage: str, leakage_class: str) -> tuple[str, ...]:
    for group in FIELD_REGISTRY_GROUPS:
        if (
            group["field_owner_stage"] == stage
            and group["leakage_class"] == leakage_class
        ):
            return group["fields"]
    raise FieldRegistryError(f"no registry group for {stage}/{leakage_class}")


def _point_in_time_fields(stage: str) -> tuple[str, ...]:
    return _group_fields(stage, "POINT_IN_TIME")


_NON_LABEL_FIELDS: tuple[str, ...] = tuple(
    field
    for stage in _BASE_STAGE_ORDER
    for field in _point_in_time_fields(stage)
)
_LABEL_FIELDS: tuple[str, ...] = _NON_LABEL_FIELDS + _group_fields(
    _LABEL_STAGE, "FUTURE_OUTCOME"
)


@dataclasses.dataclass(frozen=True, slots=True)
class ViewDefinition:
    view_id: ViewId
    schema_id: str
    schema_version: str
    allowed_producer_stages: tuple[str, ...]
    s7_allowed: bool
    fields: tuple[str, ...]
    allowlist_sha256: str
    primary_key_fields: tuple[str, ...] = _PRIMARY_KEY_FIELDS

    @property
    def schema_ref(self) -> str:
        return f"{self.schema_id}/{self.schema_version}"

    def field_contract(self) -> list[dict[str, object]]:
        """Ordered ``{field_name, field_owner_stage, leakage_class}`` list,
        byte-identical in name and order to :meth:`allowlist_preimage`'s
        ``fields`` (Data Pipeline Specification SS7.9.2/SS7.9.5)."""
        return [
            {
                "field_name": field,
                "field_owner_stage": FIELD_OWNER_STAGE[field],
                "leakage_class": FIELD_LEAKAGE_CLASS[field],
            }
            for field in self.fields
        ]

    def schema_fingerprint_preimage(self) -> dict[str, object]:
        """The exact eleven-key SS7.9.5 preimage: the ``views[]`` registry
        entry for this view (``registries/rcc002/views/
        s8_view_schema_fingerprint_profile.v1.json``), less
        ``schema_fingerprint_sha256`` itself (self-exclusion -- a value
        cannot be part of its own preimage)."""
        return {
            "view_id": self.view_id.value,
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "schema_ref": self.schema_ref,
            "allowed_producer_stages": list(self.allowed_producer_stages),
            "stage_schema_refs": [
                stage_schema_ref(StageId(stage))
                for stage in self.allowed_producer_stages
            ],
            "s7_eligible": self.s7_allowed,
            "field_contract": self.field_contract(),
            "primary_key_fields": list(self.primary_key_fields),
            "compatibility_profile_id": _COMPATIBILITY_PROFILE_ID,
            "allowlist_sha256": self.allowlist_sha256,
        }

    @property
    def schema_fingerprint_sha256(self) -> str:
        """The normative view schema fingerprint (Data Pipeline
        Specification SS7.9.5): RFC 8785/JCS canonicalization (via
        :func:`rcc002.s8.canonical.canonical_sha256`, the repository's
        certified RCC_JSON_CANONICALIZATION_V1 path) and SHA-256 of
        :meth:`schema_fingerprint_preimage`."""
        return canonical_sha256(self.schema_fingerprint_preimage())

    def allowlist_preimage(self) -> dict[str, object]:
        """RFC 8785/JCS preimage per Data Pipeline Specification SS7.9.2."""
        return {
            "allowed_producer_stages": list(self.allowed_producer_stages),
            "fields": self.field_contract(),
        }


def _build_view(
    view_id: ViewId,
    *,
    schema_version: str,
    s7_allowed: bool,
) -> ViewDefinition:
    stages = _BASE_STAGE_ORDER + ((_LABEL_STAGE,) if s7_allowed else ())
    fields = _LABEL_FIELDS if s7_allowed else _NON_LABEL_FIELDS
    expected_hash = _LABEL_ALLOWLIST_SHA256 if s7_allowed else _NON_LABEL_ALLOWLIST_SHA256
    definition = ViewDefinition(
        view_id=view_id,
        schema_id=VIEW_SCHEMA_ID[view_id],
        schema_version=schema_version,
        allowed_producer_stages=stages,
        s7_allowed=s7_allowed,
        fields=fields,
        allowlist_sha256=expected_hash,
    )
    computed_hash = canonical_sha256(definition.allowlist_preimage())
    if computed_hash != expected_hash:
        raise FieldRegistryError(
            f"{view_id.value} allowlist hash mismatch: "
            f"computed {computed_hash}, expected {expected_hash}"
        )
    return definition


# Canonical, ordered view registry (SS8.7: "DatasetManifest.views ist die
# kanonische, geordnete Registry-Momentaufnahme ... in exakt der oben
# angegebenen Reihenfolge").
VIEW_DEFINITIONS: dict[ViewId, ViewDefinition] = {
    ViewId.RESEARCH_FEATURES: _build_view(
        ViewId.RESEARCH_FEATURES, schema_version="1.0.0", s7_allowed=False
    ),
    ViewId.BACKTEST_INPUTS: _build_view(
        ViewId.BACKTEST_INPUTS, schema_version="1.0.0", s7_allowed=False
    ),
    ViewId.PAPER: _build_view(
        ViewId.PAPER, schema_version="1.0.0", s7_allowed=False
    ),
    ViewId.LIVE: _build_view(
        ViewId.LIVE, schema_version="1.0.0", s7_allowed=False
    ),
    ViewId.LABEL_RESEARCH: _build_view(
        ViewId.LABEL_RESEARCH, schema_version="1.0.0", s7_allowed=True
    ),
    ViewId.AUDIT: _build_view(
        ViewId.AUDIT, schema_version="2.0.0", s7_allowed=True
    ),
}

VIEW_ORDER: tuple[ViewId, ...] = (
    ViewId.RESEARCH_FEATURES,
    ViewId.BACKTEST_INPUTS,
    ViewId.PAPER,
    ViewId.LIVE,
    ViewId.LABEL_RESEARCH,
    ViewId.AUDIT,
)
if tuple(VIEW_DEFINITIONS) != VIEW_ORDER:
    raise FieldRegistryError("VIEW_DEFINITIONS is not in the certified order")

# Leakage-class-based prefix supplement (SS8.7: "Die zusaetzliche
# Praefixpruefung MUSS fwd_, label_ und barrier_ ablehnen, ersetzt aber
# nicht die stufenbasierte Pruefung."). Field owner stage/leakage class is
# the primary, authoritative check; this tuple is the additional,
# independent belt-and-braces textual check.
PROHIBITED_NON_LABEL_PREFIXES: tuple[str, ...] = ("fwd_", "label_", "barrier_")


def view_forbids_field_owner_stage(view_id: ViewId, owner_stage: str) -> bool:
    """True if ``owner_stage`` may never appear in ``view_id`` (SS8.7)."""
    definition = VIEW_DEFINITIONS[view_id]
    return not definition.s7_allowed and owner_stage == _LABEL_STAGE


__all__ = [
    "PROHIBITED_NON_LABEL_PREFIXES",
    "VIEW_DEFINITIONS",
    "VIEW_ORDER",
    "ViewDefinition",
    "view_forbids_field_owner_stage",
]
