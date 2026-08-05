"""Tests for rcc002.s8.artifact_class."""

from __future__ import annotations

import unittest

from rcc002.s8 import artifact_class as ac
from rcc002.s8.reason_codes import ArtifactClassificationError


class TestClassifyPath(unittest.TestCase):
    def test_exact_path_rule(self) -> None:
        self.assertEqual(ac.classify_path("SHA256SUMS"), "RELEASE_LEDGER")

    def test_prefix_rules(self) -> None:
        cases = {
            "docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md": "SCHEMA_ARTIFACT",
            "registries/rcc002/release/release_artifact_class_registry.v1.json": "SCHEMA_ARTIFACT",
            "schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json": "SCHEMA_ARTIFACT",
            "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/complete-valid.json": "SCHEMA_ARTIFACT",
            "scripts/rcc002/verify_s8rr003_normative_ledger.py": "SCHEMA_ARTIFACT",
            "docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_RR004_2026-08-01.md": "REVIEW_ARTIFACT",
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(ac.classify_path(path), expected)

    def test_unmatched_path_fails_closed(self) -> None:
        with self.assertRaises(ArtifactClassificationError):
            ac.classify_path("data/rcc002/audit.parquet")

    def test_empty_path_rejected(self) -> None:
        with self.assertRaises(ArtifactClassificationError):
            ac.classify_path("")

    def test_leading_dot_slash_normalized(self) -> None:
        self.assertEqual(ac.classify_path("./SHA256SUMS"), "RELEASE_LEDGER")


class TestClassMetadata(unittest.TestCase):
    def test_all_five_classes_present(self) -> None:
        self.assertEqual(
            ac.ARTIFACT_CLASSES,
            frozenset(
                {
                    "DATA_ARTIFACT",
                    "SCHEMA_ARTIFACT",
                    "CONTROL_MANIFEST",
                    "REVIEW_ARTIFACT",
                    "RELEASE_LEDGER",
                }
            ),
        )

    def test_enters_dataset_artifact_set_id(self) -> None:
        self.assertTrue(ac.enters_dataset_artifact_set_id("DATA_ARTIFACT"))
        self.assertFalse(ac.enters_dataset_artifact_set_id("SCHEMA_ARTIFACT"))
        self.assertFalse(ac.enters_dataset_artifact_set_id("RELEASE_LEDGER"))

    def test_unregistered_class_rejected(self) -> None:
        with self.assertRaises(ArtifactClassificationError):
            ac.enters_dataset_artifact_set_id("NOT_A_CLASS")
        with self.assertRaises(ArtifactClassificationError):
            ac.dataset_manifest_placement("NOT_A_CLASS")

    def test_dataset_manifest_placement_known_for_every_class(self) -> None:
        for artifact_class in ac.ARTIFACT_CLASSES:
            with self.subTest(artifact_class=artifact_class):
                self.assertIsInstance(
                    ac.dataset_manifest_placement(artifact_class), str
                )


if __name__ == "__main__":
    unittest.main()
