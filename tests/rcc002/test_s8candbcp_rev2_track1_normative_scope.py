"""Mutation tests for the REV9 Track 1 normative-scope verifier.

This module independently hardcodes the exact 46-path authority for
RCC-002-S8-CAND-BCP-001-REV9. It does not import the verifier's constants to
define its expected counts, correction identity, or entry inventory.
"""

import importlib.util
import json
import os
import tempfile
import unittest
from unittest import mock


_REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
_MODULE_PATH = os.path.join(
    _REPO_ROOT,
    "scripts",
    "rcc002",
    "verify_s8candbcp_rev2_track1_normative_scope.py",
)

_spec = importlib.util.spec_from_file_location(
    "verify_s8candbcp_rev2_track1_normative_scope",
    _MODULE_PATH,
)
verifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verifier)


EXPECTED_SCOPE_ID = "RCC002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1"
EXPECTED_CORRECTION_ID = "RCC-002-S8-CAND-BCP-001-REV9"
EXPECTED_TOTAL = 46
EXPECTED_MODIFIED = 4
EXPECTED_NEW = 42
EXPECTED_FINDINGS = (
    "S8-CAND-B02",
    "S8-CAND-BCP-REV4-ARCH-001",
    "S8-CAND-BCP-REV4-DOC-001",
)
EXPECTED_PATH_ORDERING = (
    "LC_ALL=C lexical order, repository-relative POSIX paths"
)
PROTECTED_BUILDER_PATH = "scripts/build_rcc002_spec_bundle.py"

EXPECTED_ENTRIES = (
    ("CLAUDE.md", "MODIFIED"),
    ("SHA256SUMS", "MODIFIED"),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_GATE_SCOPE_V1.json",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_"
        "2026-08-01.txt",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_"
        "0_8_0_CERTIFIED_COPY_2026-08-02.txt",
        "NEW",
    ),
    (
        "docs/review/evidence/"
        "RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_"
        "0_9_0_CERTIFIED_COPY_2026-08-02.txt",
        "NEW",
    ),
    (
        "docs/specifications/"
        "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
        "MODIFIED",
    ),
    (
        "docs/specifications/"
        "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md",
        "MODIFIED",
    ),
    (
        "registries/rcc002/views/"
        "s8_view_schema_fingerprint_profile.v1.json",
        "NEW",
    ),
    (
        "schemas/rcc002/manifests/dataset-manifest/"
        "1.0.2.schema.json",
        "NEW",
    ),
    ("scripts/rcc002/run_s8candbcp_gate.py", "NEW"),
    ("scripts/rcc002/verify_s8candbcp_gate_scope.py", "NEW"),
    (
        "scripts/rcc002/"
        "verify_s8candbcp_rev2_normative_ledger.py",
        "NEW",
    ),
    (
        "scripts/rcc002/"
        "verify_s8candbcp_rev2_track1_normative_scope.py",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/complete-valid.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/minimal-valid.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/CASE_LEDGER.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/absolute-path.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/duplicate-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/duplicate-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/extra-property.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/invalid-id.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/invalid-timestamp.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/missing-required-field.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/missing-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/missing-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/path-traversal.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/reordered-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/reordered-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/secret-like-field.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/secret-like-value.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/stale-specification-version.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/unknown-specification.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/unknown-view.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-schema-identity.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-schema-version.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-type-nullability.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-view-allowlist-hash.json",
        "NEW",
    ),
    (
        "tests/fixtures/rcc002/manifests/dataset-manifest/"
        "1.0.2/negative/wrong-view-fingerprint-hash.json",
        "NEW",
    ),
    ("tests/rcc002/test_s8candbcp_gate_scope.py", "NEW"),
    (
        "tests/rcc002/"
        "test_s8candbcp_rev2_normative_ledger.py",
        "NEW",
    ),
    (
        "tests/rcc002/"
        "test_s8candbcp_rev2_track1_normative_scope.py",
        "NEW",
    ),
    (
        "tests/rcc002/"
        "test_s8rr002_manifest_correction_historical_replay.py",
        "NEW",
    ),
    (
        "tests/rcc002/"
        "test_s8rr003_normative_ledger_historical_replay.py",
        "NEW",
    ),
)


def _entries():
    return list(EXPECTED_ENTRIES)


def _manifest_document():
    return {
        "scope_schema_version": "1",
        "scope_id": EXPECTED_SCOPE_ID,
        "correction_id": EXPECTED_CORRECTION_ID,
        "findings_in_scope": list(EXPECTED_FINDINGS),
        "path_ordering": EXPECTED_PATH_ORDERING,
        "total_entries": EXPECTED_TOTAL,
        "modified_entries": EXPECTED_MODIFIED,
        "new_entries": EXPECTED_NEW,
        "entries": [
            {"path": path, "category": category}
            for path, category in EXPECTED_ENTRIES
        ],
    }


class TestIndependentAuthority(unittest.TestCase):
    def test_test_authority_is_complete_and_sorted(self):
        paths = [path for path, _category in EXPECTED_ENTRIES]

        self.assertEqual(len(EXPECTED_ENTRIES), EXPECTED_TOTAL)
        self.assertEqual(len(set(paths)), EXPECTED_TOTAL)
        self.assertEqual(paths, sorted(paths))
        self.assertEqual(
            sum(
                category == "MODIFIED"
                for _path, category in EXPECTED_ENTRIES
            ),
            EXPECTED_MODIFIED,
        )
        self.assertEqual(
            sum(
                category == "NEW"
                for _path, category in EXPECTED_ENTRIES
            ),
            EXPECTED_NEW,
        )
        self.assertNotIn(PROTECTED_BUILDER_PATH, paths)

    def test_verifier_authority_equals_independent_test_authority(self):
        self.assertEqual(verifier.SCOPE_ID, EXPECTED_SCOPE_ID)
        self.assertEqual(verifier.CORRECTION_ID, EXPECTED_CORRECTION_ID)
        self.assertEqual(verifier.EXPECTED_TOTAL, EXPECTED_TOTAL)
        self.assertEqual(verifier.EXPECTED_MODIFIED, EXPECTED_MODIFIED)
        self.assertEqual(verifier.EXPECTED_NEW, EXPECTED_NEW)
        self.assertEqual(verifier.EXPECTED_FINDINGS, EXPECTED_FINDINGS)
        self.assertEqual(verifier.EXPECTED_ENTRIES, EXPECTED_ENTRIES)

    def test_positive_control_unchanged_scope_passes(self):
        verifier.verify(_entries(), source_label="test")


class TestEntryMutations(unittest.TestCase):
    def test_missing_entry_rejected(self):
        mutated = _entries()[:-1]

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_extra_entry_rejected(self):
        mutated = _entries()
        mutated.append(("zzz-undeclared-extra-file.txt", "NEW"))

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_duplicate_entry_rejected(self):
        mutated = _entries()
        mutated.append(mutated[0])

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_reordered_entry_rejected(self):
        mutated = _entries()
        mutated[0], mutated[1] = mutated[1], mutated[0]

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_miscategorized_entry_rejected(self):
        mutated = _entries()
        path, category = mutated[0]
        flipped = "MODIFIED" if category == "NEW" else "NEW"
        mutated[0] = (path, flipped)

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_same_count_path_substitution_rejected(self):
        mutated = _entries()
        _path, category = mutated[-1]
        mutated[-1] = ("tests/rcc002/zz_same_count_substitute.py", category)

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_absolute_path_rejected(self):
        mutated = _entries()
        mutated[0] = ("/etc/passwd", mutated[0][1])

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_parent_traversal_path_rejected(self):
        mutated = _entries()
        mutated[0] = ("../../etc/passwd", mutated[0][1])

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_backslash_path_rejected(self):
        mutated = _entries()
        mutated[0] = ("tests\\rcc002\\unsafe.py", mutated[0][1])

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_control_character_path_rejected(self):
        mutated = _entries()
        mutated[0] = ("tests/rcc002/bad\x01path.py", mutated[0][1])

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")

    def test_protected_builder_path_rejected(self):
        mutated = _entries()
        mutated[0] = (PROTECTED_BUILDER_PATH, mutated[0][1])

        with self.assertRaises(verifier.ScopeVerificationError):
            verifier.verify(mutated, source_label="test")


class TestManifestMutations(unittest.TestCase):
    def _verify_manifest(self, document):
        with tempfile.TemporaryDirectory() as temporary_root:
            manifest_path = os.path.join(temporary_root, "scope.json")

            with open(
                manifest_path,
                "w",
                encoding="ascii",
                newline="\n",
            ) as handle:
                json.dump(document, handle)
                handle.write("\n")

            with mock.patch.object(verifier, "REPO_ROOT", temporary_root):
                verifier.verify_scope_manifest_file("scope.json")

    def test_valid_manifest_passes(self):
        self._verify_manifest(_manifest_document())

    def test_wrong_scope_id_rejected(self):
        document = _manifest_document()
        document["scope_id"] = "SOME_OTHER_SCOPE_ID"

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_wrong_correction_id_rejected(self):
        document = _manifest_document()
        document["correction_id"] = "RCC-002-S8-CAND-BCP-001-REV5"

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_wrong_total_count_rejected(self):
        document = _manifest_document()
        document["total_entries"] = EXPECTED_TOTAL - 1

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_wrong_modified_count_rejected(self):
        document = _manifest_document()
        document["modified_entries"] = EXPECTED_MODIFIED - 1

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_wrong_new_count_rejected(self):
        document = _manifest_document()
        document["new_entries"] = EXPECTED_NEW - 1

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_wrong_findings_rejected(self):
        document = _manifest_document()
        document["findings_in_scope"] = ["UNDECLARED-FINDING"]

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_wrong_path_ordering_rejected(self):
        document = _manifest_document()
        document["path_ordering"] = "unspecified"

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_extra_top_level_key_rejected(self):
        document = _manifest_document()
        document["undeclared"] = True

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)

    def test_entry_extra_key_rejected(self):
        document = _manifest_document()
        document["entries"][0]["undeclared"] = True

        with self.assertRaises(verifier.ScopeVerificationError):
            self._verify_manifest(document)


if __name__ == "__main__":
    unittest.main()
