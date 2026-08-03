"""Mutation tests for the REV9 normative-ledger verifier.

The production authority is independently asserted as:

    145 certified baseline entries
    + 43 additions
    - 0 removals
    = 188 successor entries

Two baseline replacements are count-neutral.
"""

import hashlib
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
    "verify_s8candbcp_rev2_normative_ledger.py",
)

_spec = importlib.util.spec_from_file_location(
    "verify_s8candbcp_rev2_normative_ledger",
    _MODULE_PATH,
)
verifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verifier)


EXPECTED_SCOPE_ID = (
    "RCC002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1"
)
EXPECTED_CORRECTION_ID = "RCC-002-S8-CAND-BCP-001-REV9"
EXPECTED_LEDGER_PATH = "SHA256SUMS"
EXPECTED_BASELINE = 145
EXPECTED_ADDED = 43
EXPECTED_REMOVED = 0
EXPECTED_REPLACED = 2
EXPECTED_SUCCESSOR = 188
EXPECTED_PROTECTED_BUILDER = "scripts/build_rcc002_spec_bundle.py"

_DIGEST_A = "a" * 64
_DIGEST_B = "b" * 64
_DIGEST_C = "c" * 64
_DIGEST_D = "d" * 64


class TestProductionAuthority(unittest.TestCase):
    def test_independent_arithmetic_balances(self):
        self.assertEqual(
            EXPECTED_BASELINE + EXPECTED_ADDED - EXPECTED_REMOVED,
            EXPECTED_SUCCESSOR,
        )
        self.assertEqual(EXPECTED_REPLACED, 2)

    def test_verifier_authority_matches_independent_authority(self):
        self.assertEqual(verifier.SCOPE_ID, EXPECTED_SCOPE_ID)
        self.assertEqual(
            verifier.CORRECTION_ID,
            EXPECTED_CORRECTION_ID,
        )
        self.assertEqual(verifier.LEDGER_PATH, EXPECTED_LEDGER_PATH)
        self.assertEqual(
            verifier.EXPECTED_BASELINE,
            EXPECTED_BASELINE,
        )
        self.assertEqual(verifier.EXPECTED_ADDED, EXPECTED_ADDED)
        self.assertEqual(
            verifier.EXPECTED_REMOVED,
            EXPECTED_REMOVED,
        )
        self.assertEqual(
            verifier.EXPECTED_REPLACED,
            EXPECTED_REPLACED,
        )
        self.assertEqual(
            verifier.EXPECTED_SUCCESSOR,
            EXPECTED_SUCCESSOR,
        )
        self.assertEqual(
            verifier.PROTECTED_BUILDER_PATH,
            EXPECTED_PROTECTED_BUILDER,
        )


class _SyntheticScaleMixin:
    """Patch only numerical production constants to a four-entry scale."""

    _PATCHED = (
        "EXPECTED_BASELINE",
        "EXPECTED_ADDED",
        "EXPECTED_REMOVED",
        "EXPECTED_REPLACED",
        "EXPECTED_SUCCESSOR",
    )

    def setUp(self):
        self._saved = {
            name: getattr(verifier, name)
            for name in self._PATCHED
        }

        verifier.EXPECTED_BASELINE = 3
        verifier.EXPECTED_ADDED = 1
        verifier.EXPECTED_REMOVED = 0
        verifier.EXPECTED_REPLACED = 1
        verifier.EXPECTED_SUCCESSOR = 4

    def tearDown(self):
        for name, value in self._saved.items():
            setattr(verifier, name, value)

    @staticmethod
    def _baseline():
        return [
            ("alpha.txt", _DIGEST_A),
            ("beta.txt", _DIGEST_B),
            ("gamma.txt", _DIGEST_C),
        ]

    @staticmethod
    def _successor_map():
        return {
            "alpha.txt": _DIGEST_A,
            "beta.txt": _DIGEST_B,
            "delta.txt": _DIGEST_A,
            "gamma.txt": _DIGEST_D,
        }

    @classmethod
    def _scope_paths(cls):
        return sorted(cls._successor_map())


class TestLedgerArithmetic(
    _SyntheticScaleMixin,
    unittest.TestCase,
):
    def test_positive_control_passes(self):
        verifier.verify_arithmetic(
            self._baseline(),
            self._scope_paths(),
            self._successor_map(),
        )

    def test_missing_successor_entry_rejected(self):
        successor = self._successor_map()
        del successor["delta.txt"]

        with self.assertRaises(verifier.LedgerVerificationError):
            verifier.verify_arithmetic(
                self._baseline(),
                self._scope_paths(),
                successor,
            )

    def test_extra_successor_entry_rejected(self):
        successor = self._successor_map()
        successor["epsilon.txt"] = _DIGEST_A

        with self.assertRaises(verifier.LedgerVerificationError):
            verifier.verify_arithmetic(
                self._baseline(),
                self._scope_paths(),
                successor,
            )

    def test_unexpected_removal_rejected(self):
        successor = self._successor_map()
        del successor["beta.txt"]
        successor["epsilon.txt"] = _DIGEST_A

        with self.assertRaises(verifier.LedgerVerificationError):
            verifier.verify_arithmetic(
                self._baseline(),
                sorted(successor),
                successor,
            )

    def test_missing_replacement_rejected(self):
        successor = self._successor_map()
        successor["gamma.txt"] = _DIGEST_C

        with self.assertRaises(verifier.LedgerVerificationError):
            verifier.verify_arithmetic(
                self._baseline(),
                self._scope_paths(),
                successor,
            )

    def test_scope_membership_mismatch_rejected(self):
        scope = self._scope_paths()[:-1]

        with self.assertRaises(verifier.LedgerVerificationError):
            verifier.verify_arithmetic(
                self._baseline(),
                scope,
                self._successor_map(),
            )

    def test_forged_expected_addition_count_rejected(self):
        verifier.EXPECTED_ADDED = 99

        with self.assertRaises(verifier.LedgerVerificationError):
            verifier.verify_arithmetic(
                self._baseline(),
                self._scope_paths(),
                self._successor_map(),
            )


class TestParseLedgerLines(unittest.TestCase):
    def test_valid_lines_are_parsed(self):
        text = (
            f"{_DIGEST_A}  ./alpha.txt\n"
            f"{_DIGEST_B}  ./beta.txt\n"
        )

        self.assertEqual(
            verifier._parse_ledger_lines(text),
            [
                ("./alpha.txt", _DIGEST_A),
                ("./beta.txt", _DIGEST_B),
            ],
        )

    def test_malformed_line_rejected(self):
        with self.assertRaises(verifier.LedgerVerificationError):
            verifier._parse_ledger_lines("missing-path\n")

    def test_short_digest_rejected(self):
        with self.assertRaises(verifier.LedgerVerificationError):
            verifier._parse_ledger_lines("abc  ./alpha.txt\n")

    def test_uppercase_digest_rejected(self):
        with self.assertRaises(verifier.LedgerVerificationError):
            verifier._parse_ledger_lines(
                f"{'A' * 64}  ./alpha.txt\n"
            )

    def test_duplicate_paths_remain_detectable(self):
        text = (
            f"{_DIGEST_A}  ./alpha.txt\n"
            f"{_DIGEST_B}  ./alpha.txt\n"
        )
        entries = verifier._parse_ledger_lines(text)
        paths = [path for path, _digest in entries]

        self.assertNotEqual(len(paths), len(set(paths)))


class TestScopeManifest(
    _SyntheticScaleMixin,
    unittest.TestCase,
):
    def _document(self):
        return {
            "scope_schema_version": "1",
            "scope_id": EXPECTED_SCOPE_ID,
            "correction_id": EXPECTED_CORRECTION_ID,
            "ledger_path": EXPECTED_LEDGER_PATH,
            "path_ordering": (
                "LC_ALL=C lexical order, "
                "repository-relative POSIX paths, ./-prefixed"
            ),
            "baseline_entry_count": 3,
            "added_entry_count": 1,
            "removed_entry_count": 0,
            "replaced_entry_count": 1,
            "successor_entry_count": 4,
            "self_entry_excluded": True,
            "entries": [
                "./alpha.txt",
                "./beta.txt",
                "./delta.txt",
                "./gamma.txt",
            ],
        }

    def _verify(self, document):
        with tempfile.TemporaryDirectory() as temporary_root:
            manifest_path = os.path.join(
                temporary_root,
                verifier.SCOPE_MANIFEST_PATH,
            )
            os.makedirs(
                os.path.dirname(manifest_path),
                exist_ok=True,
            )

            with open(
                manifest_path,
                "w",
                encoding="ascii",
                newline="\n",
            ) as handle:
                json.dump(document, handle)
                handle.write("\n")

            with mock.patch.object(
                verifier,
                "REPO_ROOT",
                temporary_root,
            ):
                return verifier.load_scope_manifest()

    def test_positive_control_passes(self):
        self.assertEqual(
            self._verify(self._document()),
            [
                "./alpha.txt",
                "./beta.txt",
                "./delta.txt",
                "./gamma.txt",
            ],
        )

    def test_wrong_scope_id_rejected(self):
        document = self._document()
        document["scope_id"] = "OTHER_SCOPE"

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_wrong_correction_id_rejected(self):
        document = self._document()
        document["correction_id"] = (
            "RCC-002-S8-CAND-BCP-001-REV5"
        )

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_wrong_ledger_path_rejected(self):
        document = self._document()
        document["ledger_path"] = "OTHER_LEDGER"

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_false_self_exclusion_rejected(self):
        document = self._document()
        document["self_entry_excluded"] = False

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_wrong_baseline_count_rejected(self):
        document = self._document()
        document["baseline_entry_count"] = 99

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_wrong_added_count_rejected(self):
        document = self._document()
        document["added_entry_count"] = 99

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_wrong_successor_count_rejected(self):
        document = self._document()
        document["successor_entry_count"] = 99

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_entry_count_mismatch_rejected(self):
        document = self._document()
        document["entries"] = document["entries"][:-1]

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_reordered_entries_rejected(self):
        document = self._document()
        document["entries"][0], document["entries"][1] = (
            document["entries"][1],
            document["entries"][0],
        )

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_duplicate_entry_rejected(self):
        document = self._document()
        document["entries"][-1] = document["entries"][-2]

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_ledger_self_entry_rejected(self):
        document = self._document()
        document["entries"][0] = "./SHA256SUMS"
        document["entries"] = sorted(document["entries"])

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)

    def test_protected_builder_entry_rejected(self):
        document = self._document()
        document["entries"][0] = (
            "./scripts/build_rcc002_spec_bundle.py"
        )
        document["entries"] = sorted(document["entries"])

        with self.assertRaises(verifier.LedgerVerificationError):
            self._verify(document)


class TestSuccessorLedger(
    _SyntheticScaleMixin,
    unittest.TestCase,
):
    def _load(self, entries):
        with tempfile.TemporaryDirectory() as temporary_root:
            ledger_path = os.path.join(
                temporary_root,
                EXPECTED_LEDGER_PATH,
            )

            with open(
                ledger_path,
                "w",
                encoding="ascii",
                newline="\n",
            ) as handle:
                for path, digest in entries:
                    handle.write(f"{digest}  {path}\n")

            with mock.patch.object(
                verifier,
                "REPO_ROOT",
                temporary_root,
            ):
                return verifier.load_successor_ledger()

    def _entries(self):
        return [
            ("./alpha.txt", _DIGEST_A),
            ("./beta.txt", _DIGEST_B),
            ("./delta.txt", _DIGEST_A),
            ("./gamma.txt", _DIGEST_D),
        ]

    def test_positive_control_passes(self):
        self.assertEqual(
            self._load(self._entries()),
            dict(self._entries()),
        )

    def test_duplicate_path_rejected(self):
        entries = self._entries()
        entries[-1] = ("./delta.txt", _DIGEST_D)

        with self.assertRaises(verifier.LedgerVerificationError):
            self._load(entries)

    def test_reordered_paths_rejected(self):
        entries = self._entries()
        entries[0], entries[1] = entries[1], entries[0]

        with self.assertRaises(verifier.LedgerVerificationError):
            self._load(entries)

    def test_ledger_self_entry_rejected(self):
        entries = self._entries()
        entries[0] = ("SHA256SUMS", _DIGEST_A)
        entries.sort()

        with self.assertRaises(verifier.LedgerVerificationError):
            self._load(entries)

    def test_protected_builder_entry_rejected(self):
        entries = self._entries()
        entries[0] = (
            "scripts/build_rcc002_spec_bundle.py",
            _DIGEST_A,
        )
        entries.sort()

        with self.assertRaises(verifier.LedgerVerificationError):
            self._load(entries)


class TestHashVerification(unittest.TestCase):
    def test_matching_hashes_pass(self):
        with tempfile.TemporaryDirectory() as temporary_root:
            content = b"alpha\n"
            path = os.path.join(temporary_root, "alpha.txt")

            with open(path, "wb") as handle:
                handle.write(content)

            successor = {
                "alpha.txt": hashlib.sha256(content).hexdigest(),
            }

            with mock.patch.object(
                verifier,
                "REPO_ROOT",
                temporary_root,
            ):
                verifier.verify_hashes(successor)

    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_root:
            path = os.path.join(temporary_root, "alpha.txt")

            with open(path, "wb") as handle:
                handle.write(b"alpha\n")

            with mock.patch.object(
                verifier,
                "REPO_ROOT",
                temporary_root,
            ):
                with self.assertRaises(
                    verifier.LedgerVerificationError
                ):
                    verifier.verify_hashes(
                        {"alpha.txt": _DIGEST_A}
                    )

    def test_missing_ledgered_file_rejected(self):
        with tempfile.TemporaryDirectory() as temporary_root:
            with mock.patch.object(
                verifier,
                "REPO_ROOT",
                temporary_root,
            ):
                with self.assertRaises(
                    verifier.LedgerVerificationError
                ):
                    verifier.verify_hashes(
                        {"missing.txt": _DIGEST_A}
                    )


if __name__ == "__main__":
    unittest.main()
