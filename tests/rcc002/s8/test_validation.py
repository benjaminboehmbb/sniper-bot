"""Tests for rcc002.s8.validation.

Mandatory S8 test items 11 (secret, absolute-path, missing-parent, and
lineage-cycle rejection) and 12 (artifact-inventory and byte/semantic-hash
reconciliation).
"""

from __future__ import annotations

import hashlib
import unittest

from rcc002.s8.reason_codes import ManifestValidationError
from rcc002.s8.validation import (
    reconcile_artifact_inventory,
    reconcile_semantic_hash,
    require_acyclic,
    require_parents_exist,
    require_portable_relative_path,
    scan_for_secrets,
)


class TestSecretRejection(unittest.TestCase):
    def test_clean_structure_passes(self) -> None:
        scan_for_secrets({"a": 1, "nested": {"b": ["x", "y", 2, None, True]}})

    def test_secret_like_value_rejected(self) -> None:
        for bad in (
            "my password is x",
            "SECRET=abc",
            "auth token: abc",
            "PRIVATE_KEY-----BEGIN",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ManifestValidationError):
                    scan_for_secrets({"field": bad})

    def test_secret_like_key_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            scan_for_secrets({"api_secret": "harmless-looking-value"})

    def test_secret_deep_in_nested_structure_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            scan_for_secrets({"a": {"b": [{"c": "d"}, {"token": "xyz"}]}})


class TestAbsolutePathRejection(unittest.TestCase):
    def test_relative_path_accepted(self) -> None:
        require_portable_relative_path("data/rcc002/audit.parquet")

    def test_absolute_unix_path_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_portable_relative_path("/etc/passwd")

    def test_windows_drive_path_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_portable_relative_path("C:\\Windows\\System32")

    def test_backslash_path_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_portable_relative_path("data\\audit.parquet")

    def test_parent_traversal_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_portable_relative_path("data/../../etc/passwd")

    def test_empty_path_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_portable_relative_path("")


class TestMissingParentRejection(unittest.TestCase):
    def test_all_parents_known_passes(self) -> None:
        require_parents_exist(["a", "b"], {"a", "b", "c"}, context="stage")

    def test_missing_parent_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_parents_exist(["a", "ghost"], {"a"}, context="stage")

    def test_all_parents_missing_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_parents_exist(["x", "y"], set(), context="stage")


class TestLineageCycleRejection(unittest.TestCase):
    def test_acyclic_dag_passes(self) -> None:
        require_acyclic(
            ["s0", "s1", "s2", "audit"],
            [("s0", "s1"), ("s1", "s2"), ("s2", "audit")],
        )

    def test_direct_cycle_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_acyclic(["a", "b"], [("a", "b"), ("b", "a")])

    def test_indirect_cycle_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_acyclic(
                ["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]
            )

    def test_self_loop_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_acyclic(["a"], [("a", "a")])

    def test_dangling_edge_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_acyclic(["a"], [("a", "ghost")])

    def test_diamond_shaped_dag_passes(self) -> None:
        # Two paths converging on the same descendant is not a cycle.
        require_acyclic(
            ["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
        )

    def test_disconnected_components_all_checked(self) -> None:
        with self.assertRaises(ManifestValidationError):
            require_acyclic(
                ["a", "b", "x", "y"], [("a", "b"), ("x", "y"), ("y", "x")]
            )


class TestArtifactInventoryReconciliation(unittest.TestCase):
    """Item 12: byte and semantic hash reconciliation."""

    def test_matching_bytes_and_size_pass(self) -> None:
        content = b"hello rcc002"
        digest = hashlib.sha256(content).hexdigest()
        entries = [
            {"relative_path": "x.txt", "byte_sha256": digest, "size_bytes": len(content)}
        ]
        reconcile_artifact_inventory(entries, lambda _p: content)

    def test_byte_hash_mismatch_rejected(self) -> None:
        entries = [{"relative_path": "x.txt", "byte_sha256": "a" * 64, "size_bytes": 5}]
        with self.assertRaises(ManifestValidationError):
            reconcile_artifact_inventory(entries, lambda _p: b"hello")

    def test_size_mismatch_rejected(self) -> None:
        content = b"hello"
        digest = hashlib.sha256(content).hexdigest()
        entries = [{"relative_path": "x.txt", "byte_sha256": digest, "size_bytes": 999}]
        with self.assertRaises(ManifestValidationError):
            reconcile_artifact_inventory(entries, lambda _p: content)

    def test_malformed_declared_digest_rejected(self) -> None:
        entries = [{"relative_path": "x.txt", "byte_sha256": "not-hex", "size_bytes": 1}]
        with self.assertRaises(ManifestValidationError):
            reconcile_artifact_inventory(entries, lambda _p: b"x")

    def test_unsafe_relative_path_rejected_before_resolution(self) -> None:
        entries = [{"relative_path": "/etc/passwd", "byte_sha256": "a" * 64}]
        with self.assertRaises(ManifestValidationError):
            reconcile_artifact_inventory(entries, lambda _p: b"unused")

    def test_semantic_hash_match(self) -> None:
        reconcile_semantic_hash(
            declared_semantic_sha256="a" * 64,
            recomputed_semantic_sha256="a" * 64,
            context="audit-v2",
        )

    def test_semantic_hash_mismatch_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            reconcile_semantic_hash(
                declared_semantic_sha256="a" * 64,
                recomputed_semantic_sha256="b" * 64,
                context="audit-v2",
            )

    def test_malformed_declared_semantic_hash_rejected(self) -> None:
        with self.assertRaises(ManifestValidationError):
            reconcile_semantic_hash(
                declared_semantic_sha256="not-hex",
                recomputed_semantic_sha256="a" * 64,
                context="audit-v2",
            )


if __name__ == "__main__":
    unittest.main()
