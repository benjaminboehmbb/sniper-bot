"""Unit tests for rcc002.constants (Implementation Step 1: foundation).

Asserts that the transcribed stage list and schema identifiers match the
certified RCC-002 specification bundle exactly: correct stage count and
order, correct schema ID strings, correct versions, and no duplicates.
"""

import unittest

from rcc002 import constants


class StageIdTests(unittest.TestCase):
    def test_exactly_nine_stages(self) -> None:
        self.assertEqual(len(constants.StageId), 9)

    def test_canonical_stage_order(self) -> None:
        self.assertEqual(
            [stage.value for stage in constants.StageId],
            [
                "S0_SOURCE",
                "S1_NORMALIZED",
                "S2_VALIDATED",
                "S3_INDICATORS",
                "S4_SIGNALS",
                "S5_REGIMES",
                "S6_GATES",
                "S7_LABELS",
                "S8_EXPORT",
            ],
        )


class StageSchemaTests(unittest.TestCase):
    def test_eight_stage_schemas_s8_excluded(self) -> None:
        # S8_EXPORT has no stage schema of its own; only per-view schemas
        # (Data Pipeline §7.9).
        self.assertEqual(len(constants.STAGE_SCHEMA_ID), 8)
        self.assertNotIn(constants.StageId.S8_EXPORT, constants.STAGE_SCHEMA_ID)

    def test_schema_ids_match_specification(self) -> None:
        expected = {
            constants.StageId.S0_SOURCE: "rcc002.stage.s0-source",
            constants.StageId.S1_NORMALIZED: "rcc002.stage.s1-normalized",
            constants.StageId.S2_VALIDATED: "rcc002.stage.s2-validated",
            constants.StageId.S3_INDICATORS: "rcc002.stage.s3-indicators",
            constants.StageId.S4_SIGNALS: "rcc002.stage.s4-signals",
            constants.StageId.S5_REGIMES: "rcc002.stage.s5-regimes",
            constants.StageId.S6_GATES: "rcc002.stage.s6-gates",
            constants.StageId.S7_LABELS: "rcc002.stage.s7-labels",
        }
        self.assertEqual(constants.STAGE_SCHEMA_ID, expected)

    def test_schema_refs_are_versioned_1_0_0(self) -> None:
        for stage in constants.STAGE_SCHEMA_ID:
            self.assertEqual(constants.stage_schema_ref(stage).split("/")[-1], "1.0.0")
            self.assertTrue(
                constants.stage_schema_ref(stage).startswith(
                    constants.STAGE_SCHEMA_ID[stage] + "/"
                )
            )

    def test_no_duplicate_stage_schema_ids(self) -> None:
        ids = list(constants.STAGE_SCHEMA_ID.values())
        self.assertEqual(len(ids), len(set(ids)))


class StateSchemaTests(unittest.TestCase):
    def test_state_schemas_only_for_s3_and_s5(self) -> None:
        self.assertEqual(
            set(constants.STATE_SCHEMA_ID.keys()),
            {constants.StageId.S3_INDICATORS, constants.StageId.S5_REGIMES},
        )

    def test_state_schema_ids_match_specification(self) -> None:
        self.assertEqual(
            constants.STATE_SCHEMA_ID[constants.StageId.S3_INDICATORS],
            "rcc002.state.s3-indicators",
        )
        self.assertEqual(
            constants.STATE_SCHEMA_ID[constants.StageId.S5_REGIMES],
            "rcc002.state.s5-regimes",
        )

    def test_state_schema_refs_are_versioned_1_0_0(self) -> None:
        for stage in constants.STATE_SCHEMA_ID:
            self.assertTrue(constants.state_schema_ref(stage).endswith("/1.0.0"))


class ViewIdTests(unittest.TestCase):
    def test_exactly_six_views(self) -> None:
        self.assertEqual(len(constants.ViewId), 6)

    def test_view_schema_ids_match_specification(self) -> None:
        expected = {
            constants.ViewId.RESEARCH_FEATURES: "rcc002.view.research-features",
            constants.ViewId.BACKTEST_INPUTS: "rcc002.view.backtest-inputs",
            constants.ViewId.PAPER: "rcc002.view.paper",
            constants.ViewId.LIVE: "rcc002.view.live",
            constants.ViewId.LABEL_RESEARCH: "rcc002.view.label-research",
            constants.ViewId.AUDIT: "rcc002.view.audit",
        }
        self.assertEqual(constants.VIEW_SCHEMA_ID, expected)

    def test_view_schema_refs_are_versioned_1_0_0(self) -> None:
        for view in constants.VIEW_SCHEMA_ID:
            self.assertTrue(constants.view_schema_ref(view).endswith("/1.0.0"))

    def test_no_duplicate_view_schema_ids(self) -> None:
        ids = list(constants.VIEW_SCHEMA_ID.values())
        self.assertEqual(len(ids), len(set(ids)))


class PackageIdentityTests(unittest.TestCase):
    def test_certified_bundle_hash_recorded(self) -> None:
        import rcc002

        self.assertEqual(
            rcc002.CERTIFIED_BUNDLE_SHA256,
            "8a6ab7d732e02727199e704313c38959161c3929441fddce34b4ee4f2586d9ee",
        )

    def test_certified_bundle_hash_matches_working_tree(self) -> None:
        import hashlib
        from pathlib import Path

        import rcc002

        repo_root = Path(__file__).resolve().parents[2]
        bundle_path = repo_root / rcc002.CERTIFIED_BUNDLE_PATH
        actual_sha256 = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
        self.assertEqual(actual_sha256, rcc002.CERTIFIED_BUNDLE_SHA256)

    def test_certified_manifest_hash_matches_working_tree(self) -> None:
        import hashlib
        from pathlib import Path

        import rcc002

        repo_root = Path(__file__).resolve().parents[2]
        manifest_path = repo_root / rcc002.CERTIFIED_MANIFEST_PATH
        actual_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        self.assertEqual(actual_sha256, rcc002.CERTIFIED_MANIFEST_SHA256)


if __name__ == "__main__":
    unittest.main()
