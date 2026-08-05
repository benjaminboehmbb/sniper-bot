"""Tests for rcc002.s8.views.

Mandatory S8 test items 1 (232/534 field order and allowlist hashes) and 3
(rejection of every S7 field from non-label views, verified structurally
here; behaviourally in test_projection.py). Also covers the RCC-002-S8-
TRACK2-IAD-001 F-002 correction: the normative SS7.9.5 view schema
fingerprint construction.
"""

from __future__ import annotations

import copy
import unittest

from rcc002.constants import ViewId
from rcc002.s8.canonical import canonical_sha256
from rcc002.s8.field_registry import FIELD_OWNER_STAGE
from rcc002.s8.views import (
    PROHIBITED_NON_LABEL_PREFIXES,
    VIEW_DEFINITIONS,
    VIEW_ORDER,
    view_forbids_field_owner_stage,
)

NON_LABEL_VIEWS = (
    ViewId.RESEARCH_FEATURES,
    ViewId.BACKTEST_INPUTS,
    ViewId.PAPER,
    ViewId.LIVE,
)
LABEL_VIEWS = (ViewId.LABEL_RESEARCH, ViewId.AUDIT)

CERTIFIED_NON_LABEL_HASH = (
    "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"
)
CERTIFIED_LABEL_HASH = (
    "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"
)


class TestFieldCountsAndHashes(unittest.TestCase):
    def test_non_label_views_have_232_fields(self) -> None:
        for view_id in NON_LABEL_VIEWS:
            with self.subTest(view=view_id.value):
                self.assertEqual(len(VIEW_DEFINITIONS[view_id].fields), 232)

    def test_label_views_have_534_fields(self) -> None:
        for view_id in LABEL_VIEWS:
            with self.subTest(view=view_id.value):
                self.assertEqual(len(VIEW_DEFINITIONS[view_id].fields), 534)

    def test_non_label_views_share_certified_hash(self) -> None:
        for view_id in NON_LABEL_VIEWS:
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    VIEW_DEFINITIONS[view_id].allowlist_sha256,
                    CERTIFIED_NON_LABEL_HASH,
                )

    def test_label_views_share_certified_hash(self) -> None:
        for view_id in LABEL_VIEWS:
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    VIEW_DEFINITIONS[view_id].allowlist_sha256,
                    CERTIFIED_LABEL_HASH,
                )

    def test_four_non_label_views_share_byte_identical_field_order(self) -> None:
        reference = VIEW_DEFINITIONS[ViewId.RESEARCH_FEATURES].fields
        for view_id in NON_LABEL_VIEWS[1:]:
            with self.subTest(view=view_id.value):
                self.assertEqual(VIEW_DEFINITIONS[view_id].fields, reference)

    def test_label_research_and_audit_share_byte_identical_field_order(self) -> None:
        self.assertEqual(
            VIEW_DEFINITIONS[ViewId.LABEL_RESEARCH].fields,
            VIEW_DEFINITIONS[ViewId.AUDIT].fields,
        )

    def test_label_view_fields_extend_non_label_prefix(self) -> None:
        prefix = VIEW_DEFINITIONS[ViewId.RESEARCH_FEATURES].fields
        full = VIEW_DEFINITIONS[ViewId.LABEL_RESEARCH].fields
        self.assertEqual(full[: len(prefix)], prefix)

    def test_audit_is_schema_version_2_0_0(self) -> None:
        # Certified in RM SS8.7; note rcc002.constants.VIEW_SCHEMA_VERSION
        # incorrectly maps every view including audit to "1.0.0" -- see the
        # implementation report finding. This module must not inherit that
        # bug.
        self.assertEqual(VIEW_DEFINITIONS[ViewId.AUDIT].schema_version, "2.0.0")
        self.assertEqual(
            VIEW_DEFINITIONS[ViewId.AUDIT].schema_ref, "rcc002.view.audit/2.0.0"
        )

    def test_view_registry_order_is_certified_order(self) -> None:
        self.assertEqual(
            VIEW_ORDER,
            (
                ViewId.RESEARCH_FEATURES,
                ViewId.BACKTEST_INPUTS,
                ViewId.PAPER,
                ViewId.LIVE,
                ViewId.LABEL_RESEARCH,
                ViewId.AUDIT,
            ),
        )

    def test_every_view_field_is_sorted_unique_within_itself(self) -> None:
        for view_id in VIEW_ORDER:
            fields = VIEW_DEFINITIONS[view_id].fields
            with self.subTest(view=view_id.value):
                self.assertEqual(len(set(fields)), len(fields))


class TestNonLabelViewsExcludeS7(unittest.TestCase):
    """Item 3: no field owned by S7_LABELS may appear in a non-label view."""

    def test_no_s7_owned_field_in_any_non_label_view(self) -> None:
        for view_id in NON_LABEL_VIEWS:
            for field in VIEW_DEFINITIONS[view_id].fields:
                with self.subTest(view=view_id.value, field=field):
                    self.assertNotEqual(FIELD_OWNER_STAGE[field], "S7_LABELS")

    def test_no_future_outcome_leakage_class_in_any_non_label_view(self) -> None:
        from rcc002.s8.field_registry import FIELD_LEAKAGE_CLASS

        for view_id in NON_LABEL_VIEWS:
            for field in VIEW_DEFINITIONS[view_id].fields:
                with self.subTest(view=view_id.value, field=field):
                    self.assertNotEqual(
                        FIELD_LEAKAGE_CLASS[field], "FUTURE_OUTCOME"
                    )

    def test_every_registered_s7_field_individually_forbidden_in_non_label_views(
        self,
    ) -> None:
        s7_fields = [
            field
            for field, stage in FIELD_OWNER_STAGE.items()
            if stage == "S7_LABELS"
        ]
        self.assertEqual(len(s7_fields), 302)
        for view_id in NON_LABEL_VIEWS:
            for field in s7_fields:
                with self.subTest(view=view_id.value, field=field):
                    self.assertTrue(
                        view_forbids_field_owner_stage(view_id, "S7_LABELS")
                    )

    def test_label_views_permit_s7_owner_stage(self) -> None:
        for view_id in LABEL_VIEWS:
            with self.subTest(view=view_id.value):
                self.assertFalse(
                    view_forbids_field_owner_stage(view_id, "S7_LABELS")
                )


class TestProhibitedPrefixes(unittest.TestCase):
    """Item 4: fwd_/label_/barrier_ prefix rejection surface."""

    def test_prefix_tuple_is_exact(self) -> None:
        self.assertEqual(
            PROHIBITED_NON_LABEL_PREFIXES, ("fwd_", "label_", "barrier_")
        )

    def test_prefix_check_alone_would_not_catch_every_s7_field(self) -> None:
        # SS7.9.3/SS8.7: the prefix check supplements, but does not
        # replace, the stage-based check. Some S7 metadata fields (for
        # example ``horizon_registry_id``, ``cost_profile_id``) carry
        # none of the three prohibited prefixes despite being S7-owned --
        # proving the stage-based registry check is load-bearing and the
        # prefix check is only a belt-and-braces supplement.
        s7_fields = [
            field
            for field, stage in FIELD_OWNER_STAGE.items()
            if stage == "S7_LABELS"
        ]
        unprefixed = [
            field
            for field in s7_fields
            if not field.startswith(PROHIBITED_NON_LABEL_PREFIXES)
        ]
        self.assertIn("horizon_registry_id", unprefixed)
        self.assertIn("cost_profile_id", unprefixed)
        self.assertGreater(len(unprefixed), 0)

    def test_no_non_label_view_field_has_a_prohibited_prefix(self) -> None:
        for view_id in NON_LABEL_VIEWS:
            for field in VIEW_DEFINITIONS[view_id].fields:
                with self.subTest(view=view_id.value, field=field):
                    self.assertFalse(
                        field.startswith(PROHIBITED_NON_LABEL_PREFIXES)
                    )


class TestSchemaFingerprintSS795(unittest.TestCase):
    """F-002: the normative SS7.9.5 view schema fingerprint construction.

    Golden values are transcribed verbatim from Data Pipeline Specification
    0.9.0 SS7.9.5's "Sechs literale schema_fingerprint_sha256-Werte" table
    (and cross-checked against the certified registry artifact
    ``registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json``)
    -- they are plain string literals, never produced by calling
    ``schema_fingerprint_sha256`` itself.
    """

    GOLDEN_SCHEMA_FINGERPRINT_SHA256 = {
        "rcc002.view.research-features/1.0.0": (
            "1e2bd4af73e8cc508a5a21966245fc3db9f0b0c2c71de60d7e4add713a969459"
        ),
        "rcc002.view.backtest-inputs/1.0.0": (
            "28892062a428a93fba75428729c63a72bc0b44a6d39687ba953c106a78ffeb2d"
        ),
        "rcc002.view.paper/1.0.0": (
            "901aa6b4b3f67d96d087c2a917494566f7d8779fb520e71c49fb2dac47c4c50c"
        ),
        "rcc002.view.live/1.0.0": (
            "49966dcc82cae5e9b2c4f1a80a5f0523ef856637f247b939aca296c495491ebe"
        ),
        "rcc002.view.label-research/1.0.0": (
            "97becbeee9575bce31e3a8c215f5dd0a549c469abe38174d96967999ffce206a"
        ),
        "rcc002.view.audit/2.0.0": (
            "6995e0cb3e2e624e34a4f842fc888115bc75bd28c84826759ce42391bb869397"
        ),
    }

    # SS7.9.5: exactly eleven keys, the twelve-key registry entry less
    # `schema_fingerprint_sha256` itself.
    PREIMAGE_KEYS = (
        "view_id",
        "schema_id",
        "schema_version",
        "schema_ref",
        "allowed_producer_stages",
        "stage_schema_refs",
        "s7_eligible",
        "field_contract",
        "primary_key_fields",
        "compatibility_profile_id",
        "allowlist_sha256",
    )

    def test_golden_vectors(self) -> None:
        for view_id in VIEW_ORDER:
            definition = VIEW_DEFINITIONS[view_id]
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    definition.schema_fingerprint_sha256,
                    self.GOLDEN_SCHEMA_FINGERPRINT_SHA256[definition.schema_ref],
                )

    def test_golden_vectors_cover_every_registered_view(self) -> None:
        self.assertEqual(
            {VIEW_DEFINITIONS[v].schema_ref for v in VIEW_ORDER},
            set(self.GOLDEN_SCHEMA_FINGERPRINT_SHA256),
        )

    def test_preimage_has_exactly_the_normative_eleven_keys(self) -> None:
        for view_id in VIEW_ORDER:
            with self.subTest(view=view_id.value):
                preimage = VIEW_DEFINITIONS[view_id].schema_fingerprint_preimage()
                self.assertEqual(tuple(preimage), self.PREIMAGE_KEYS)

    def test_preimage_excludes_schema_fingerprint_sha256_itself(self) -> None:
        preimage = VIEW_DEFINITIONS[ViewId.AUDIT].schema_fingerprint_preimage()
        self.assertNotIn("schema_fingerprint_sha256", preimage)

    def test_preimage_hash_matches_canonical_sha256_of_the_preimage(self) -> None:
        # Confirms the repository's conformant RCC_JSON_CANONICALIZATION_V1
        # path (rcc002.s8.canonical.canonical_sha256, reused from
        # rcc002.s0.source_identity.canonical_json_bytes) is what is used,
        # rather than a competing canonicalization implementation.
        for view_id in VIEW_ORDER:
            definition = VIEW_DEFINITIONS[view_id]
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    definition.schema_fingerprint_sha256,
                    canonical_sha256(definition.schema_fingerprint_preimage()),
                )

    def test_stage_schema_refs_parallel_allowed_producer_stages(self) -> None:
        research = VIEW_DEFINITIONS[ViewId.RESEARCH_FEATURES]
        preimage = research.schema_fingerprint_preimage()
        self.assertEqual(
            preimage["stage_schema_refs"],
            [
                "rcc002.stage.s0-source/1.0.0",
                "rcc002.stage.s1-normalized/1.0.0",
                "rcc002.stage.s2-validated/1.0.0",
                "rcc002.stage.s3-indicators/1.0.0",
                "rcc002.stage.s4-signals/1.0.0",
                "rcc002.stage.s5-regimes/1.0.0",
                "rcc002.stage.s6-gates/1.0.0",
            ],
        )
        label_research = VIEW_DEFINITIONS[ViewId.LABEL_RESEARCH]
        self.assertEqual(
            label_research.schema_fingerprint_preimage()["stage_schema_refs"][-1],
            "rcc002.stage.s7-labels/1.0.0",
        )

    def test_field_contract_is_byte_identical_to_allowlist_preimage_fields(
        self,
    ) -> None:
        for view_id in VIEW_ORDER:
            definition = VIEW_DEFINITIONS[view_id]
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    definition.schema_fingerprint_preimage()["field_contract"],
                    definition.allowlist_preimage()["fields"],
                )

    def test_primary_key_fields_is_the_certified_consolidated_key(self) -> None:
        for view_id in VIEW_ORDER:
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    VIEW_DEFINITIONS[view_id].primary_key_fields,
                    ("market_type", "symbol", "interval", "open_time"),
                )

    def test_negative_research_features_and_label_research_diverge(self) -> None:
        # SS7.9.5 "Negative-evidence case": these two views differ only in
        # allowed_producer_stages/stage_schema_refs/s7_eligible/
        # field_contract/allowlist_sha256; their fingerprints must differ.
        self.assertNotEqual(
            VIEW_DEFINITIONS[ViewId.RESEARCH_FEATURES].schema_fingerprint_sha256,
            VIEW_DEFINITIONS[ViewId.LABEL_RESEARCH].schema_fingerprint_sha256,
        )

    def test_negative_label_research_and_audit_diverge(self) -> None:
        # These two differ only in schema_id/schema_version/schema_ref
        # (identical allowlist_sha256, identical field_contract).
        self.assertNotEqual(
            VIEW_DEFINITIONS[ViewId.LABEL_RESEARCH].schema_fingerprint_sha256,
            VIEW_DEFINITIONS[ViewId.AUDIT].schema_fingerprint_sha256,
        )

    def test_negative_mutating_any_single_preimage_key_changes_the_hash(
        self,
    ) -> None:
        base = VIEW_DEFINITIONS[ViewId.RESEARCH_FEATURES]
        base_preimage = base.schema_fingerprint_preimage()
        base_hash = canonical_sha256(base_preimage)
        self.assertEqual(base_hash, base.schema_fingerprint_sha256)

        mutations = {
            "view_id": "backtest-inputs",
            "schema_id": "rcc002.view.other",
            "schema_version": "9.9.9",
            "schema_ref": "rcc002.view.other/9.9.9",
            "allowed_producer_stages": list(base_preimage["allowed_producer_stages"])
            + ["S7_LABELS"],
            "stage_schema_refs": list(base_preimage["stage_schema_refs"])
            + ["rcc002.stage.s7-labels/1.0.0"],
            "s7_eligible": not base_preimage["s7_eligible"],
            "field_contract": base_preimage["field_contract"][:-1],
            "primary_key_fields": ["provider", *base_preimage["primary_key_fields"]],
            "compatibility_profile_id": "OTHER_PROFILE",
            "allowlist_sha256": "0" * 64,
        }
        for key, mutated_value in mutations.items():
            with self.subTest(key=key):
                mutated = copy.deepcopy(base_preimage)
                mutated[key] = mutated_value
                self.assertNotEqual(canonical_sha256(mutated), base_hash)


if __name__ == "__main__":
    unittest.main()
