"""Focused mutation tests for the RCC-002 S8-RR-003 normative ledger verifier.

Exercises the pure verifier functions in
scripts/rcc002/verify_s8rr003_normative_ledger.py against in-memory
mutations and isolated temporary directories. No repository file is
ever modified by this module.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
import warnings

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VERIFIER_PATH = os.path.join(REPO_ROOT, "scripts", "rcc002", "verify_s8rr003_normative_ledger.py")

_spec = importlib.util.spec_from_file_location("verify_s8rr003_normative_ledger", VERIFIER_PATH)
verifier = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verifier)

V = verifier.VerificationError


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def build_ledger_bytes(entries):
    """entries: list of (digest, relpath-without-./-prefix)."""
    lines = ["%s  ./%s" % (digest, path) for digest, path in entries]
    return ("\n".join(lines) + "\n").encode("ascii")


def valid_current_entries():
    """(digest, path) pairs, in the exact expected sorted order, with
    deterministic fake digests (not real file contents)."""
    return [(sha256_hex(p.encode("ascii")), p) for p in verifier.CURRENT_LEDGER_PATHS]


def valid_historical_entries():
    entries = [(sha256_hex(p.encode("ascii")), p) for p in verifier.HISTORICAL_NORMATIVE_PATHS]
    # Force the historically-correct (stale) RM digest onto the RM path.
    entries = [
        (verifier.STALE_RM_SHA256, p) if p == verifier.CURRENT_RM_PATH else (d, p)
        for d, p in entries
    ]
    return entries


def valid_scope_doc():
    return {
        "scope_schema_version": verifier.SCOPE_SCHEMA_VERSION,
        "scope_id": verifier.SCOPE_ID,
        "correction_id": verifier.CORRECTION_ID,
        "finding_in_scope": verifier.FINDING_IN_SCOPE,
        "ledger_path": verifier.LEDGER_PATH,
        "historical_ledger_sha256": verifier.HISTORICAL_LEDGER_SHA256,
        "path_ordering": verifier.PATH_ORDERING,
        "entry_format": verifier.ENTRY_FORMAT,
        "expected_current_entry_count": verifier.EXPECTED_CURRENT_ENTRY_COUNT,
        "consumed_by": verifier.CONSUMED_BY,
        "historical_normative_paths": list(verifier.HISTORICAL_NORMATIVE_PATHS),
        "s8rr002_correction_outputs": list(verifier.S8RR002_CORRECTION_OUTPUTS),
        "s8rr003_lifecycle_outputs": list(verifier.S8RR003_LIFECYCLE_OUTPUTS),
        "current_ledger_paths": list(verifier.CURRENT_LEDGER_PATHS),
    }


class Case01ValidPositiveControl(unittest.TestCase):
    """Case 1: valid unmodified 110/30/6/145 positive control -- full
    integration run against the real (read-only) repository state."""

    def test_full_repo_state_passes(self):
        result = verifier.run_verification(REPO_ROOT)
        self.assertEqual(result["result"], "PASS")
        self.assertEqual(result["historical_entry_count"], 110)
        self.assertEqual(result["s8rr002_output_count"], 30)
        self.assertEqual(result["s8rr003_output_count"], 6)
        self.assertEqual(result["current_ledger_entry_count"], 145)
        self.assertEqual(result["verified_entry_count"], 145)
        self.assertEqual(result["historical_ledger_sha256"], verifier.HISTORICAL_LEDGER_SHA256)
        self.assertEqual(result["current_rm_sha256"], verifier.CURRENT_RM_SHA256)

    def test_scope_arithmetic_in_memory(self):
        self.assertEqual(len(verifier.HISTORICAL_NORMATIVE_PATHS), 110)
        self.assertEqual(len(verifier.S8RR002_CORRECTION_OUTPUTS), 30)
        self.assertEqual(len(verifier.S8RR003_LIFECYCLE_OUTPUTS), 6)
        self.assertEqual(len(verifier.CURRENT_LEDGER_PATHS), 145)
        derived = verifier.derive_union(
            verifier.HISTORICAL_NORMATIVE_PATHS,
            verifier.S8RR002_CORRECTION_OUTPUTS,
            verifier.S8RR003_LIFECYCLE_OUTPUTS,
        )
        self.assertEqual(derived, list(verifier.CURRENT_LEDGER_PATHS))


class ScopeCategoryMutations(unittest.TestCase):
    """Cases 2-10: category equality, ordering, and metadata gates."""

    def test_case02_missing_historical_path(self):
        mutated = list(verifier.HISTORICAL_NORMATIVE_PATHS)[1:]
        with self.assertRaises(V):
            verifier.require_exact_ordered_equality(
                mutated, verifier.HISTORICAL_NORMATIVE_PATHS, "historical_normative_paths"
            )

    def test_case03_missing_s8rr002_output(self):
        mutated = list(verifier.S8RR002_CORRECTION_OUTPUTS)[1:]
        with self.assertRaises(V):
            verifier.require_exact_ordered_equality(
                mutated, verifier.S8RR002_CORRECTION_OUTPUTS, "s8rr002_correction_outputs"
            )

    def test_case04_missing_s8rr003_output(self):
        mutated = list(verifier.S8RR003_LIFECYCLE_OUTPUTS)[1:]
        with self.assertRaises(V):
            verifier.require_exact_ordered_equality(
                mutated, verifier.S8RR003_LIFECYCLE_OUTPUTS, "s8rr003_lifecycle_outputs"
            )

    def test_case05_extra_current_ledger_path(self):
        mutated = list(verifier.CURRENT_LEDGER_PATHS) + ["docs/EXTRA_NOT_IN_SCOPE.md"]
        doc = valid_scope_doc()
        doc["current_ledger_paths"] = sorted(mutated)
        with self.assertRaises(V):
            verifier.validate_scope_categories(doc)

    def test_case06_duplicate_within_category(self):
        mutated = list(verifier.S8RR002_CORRECTION_OUTPUTS)
        mutated.append(mutated[0])
        with self.assertRaises(V):
            verifier.require_sorted_unique(mutated, "s8rr002_correction_outputs")

    def test_case07_invalid_overlap_across_categories(self):
        bogus_shared_path = next(
            p for p in verifier.S8RR002_CORRECTION_OUTPUTS if p != verifier.EXPECTED_OVERLAP_PATH
        )
        mutated_historical = list(verifier.HISTORICAL_NORMATIVE_PATHS) + [bogus_shared_path]
        overlap = verifier.compute_overlap(mutated_historical, verifier.S8RR002_CORRECTION_OUTPUTS)
        self.assertNotEqual(overlap, {verifier.EXPECTED_OVERLAP_PATH})
        with self.assertRaises(V):
            verifier.require_single_expected_overlap(
                overlap, verifier.EXPECTED_OVERLAP_PATH, "overlap_a_b"
            )

    def test_case08_reordered_category(self):
        doc = valid_scope_doc()
        reordered = list(reversed(doc["s8rr003_lifecycle_outputs"]))
        self.assertEqual(set(reordered), set(verifier.S8RR003_LIFECYCLE_OUTPUTS))
        self.assertNotEqual(reordered, list(verifier.S8RR003_LIFECYCLE_OUTPUTS))
        doc["s8rr003_lifecycle_outputs"] = reordered
        with self.assertRaises(V):
            verifier.validate_scope_categories(doc)

    def test_case09_reordered_current_union(self):
        doc = valid_scope_doc()
        reordered = list(reversed(doc["current_ledger_paths"]))
        doc["current_ledger_paths"] = reordered
        with self.assertRaises(V):
            verifier.validate_scope_categories(doc)

    def test_case10_incorrect_scope_metadata(self):
        doc = valid_scope_doc()
        doc["finding_in_scope"] = "S8-RR3-B99"
        with self.assertRaises(V):
            verifier.validate_scope_metadata(doc)


class UnsafePathMutations(unittest.TestCase):
    """Cases 11-13: unsafe relative-path rejection."""

    def test_case11_absolute_path(self):
        with self.assertRaises(V):
            verifier.validate_safe_relpath("/etc/passwd", "test")

    def test_case12_parent_traversal(self):
        with self.assertRaises(V):
            verifier.validate_safe_relpath("docs/../../etc/passwd", "test")

    def test_case13_backslash_path(self):
        with self.assertRaises(V):
            verifier.validate_safe_relpath("docs\\evil.txt", "test")


class LedgerStructureMutations(unittest.TestCase):
    """Cases 14-19, 26-29: SHA256SUMS grammar and structural gates."""

    def test_case14_root_ledger_self_entry(self):
        entries = valid_current_entries()[:3]
        entries.append((sha256_hex(b"x"), "SHA256SUMS"))
        data = build_ledger_bytes(entries)
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(data, label="current_ledger")

    def test_case15_missing_ledger_entry(self):
        entries = valid_current_entries()[:-1]
        data = build_ledger_bytes(entries)
        parsed = verifier.parse_ledger_bytes(data, label="current_ledger")
        paths = [p for _, p in parsed]
        with self.assertRaises(V):
            verifier.require_exact_ordered_equality(
                paths, verifier.CURRENT_LEDGER_PATHS, "current_ledger_paths"
            )

    def test_case16_extra_ledger_entry(self):
        entries = valid_current_entries()
        entries.append((sha256_hex(b"extra"), "docs/EXTRA_NOT_IN_SCOPE.md"))
        entries.sort(key=lambda e: e[1])
        data = build_ledger_bytes(entries)
        parsed = verifier.parse_ledger_bytes(data, label="current_ledger")
        paths = [p for _, p in parsed]
        with self.assertRaises(V):
            verifier.require_exact_ordered_equality(
                paths, verifier.CURRENT_LEDGER_PATHS, "current_ledger_paths"
            )

    def test_case17_duplicate_ledger_entry(self):
        entries = valid_current_entries()
        entries.insert(1, entries[0])
        data = build_ledger_bytes(entries)
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(data, label="current_ledger")

    def test_case18_reordered_ledger_entry(self):
        entries = valid_current_entries()
        entries[0], entries[-1] = entries[-1], entries[0]
        data = build_ledger_bytes(entries)
        parsed = verifier.parse_ledger_bytes(data, label="current_ledger")
        paths = [p for _, p in parsed]
        with self.assertRaises(V):
            verifier.require_exact_ordered_equality(
                paths, verifier.CURRENT_LEDGER_PATHS, "current_ledger_paths"
            )

    def test_case19_malformed_digest_or_separator(self):
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(b"deadbeef  ./docs/short-digest.md\n", label="current_ledger")
        good_digest = sha256_hex(b"y")
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(
                ("%s ./docs/single-space.md\n" % good_digest).encode("ascii"), label="current_ledger"
            )

    def test_case26_crlf_line_endings(self):
        entries = valid_current_entries()[:2]
        data = build_ledger_bytes(entries).replace(b"\n", b"\r\n")
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(data, label="current_ledger")

    def test_case27_missing_final_newline(self):
        entries = valid_current_entries()[:2]
        data = build_ledger_bytes(entries)[:-1]
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(data, label="current_ledger")

    def test_case28_multiple_final_newlines(self):
        entries = valid_current_entries()[:2]
        data = build_ledger_bytes(entries) + b"\n"
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(data, label="current_ledger")

    def test_case29_non_ascii_byte(self):
        entries = valid_current_entries()[:2]
        data = build_ledger_bytes(entries)
        data = data.replace(b"docs", b"d\xc3\xa9cs", 1)
        with self.assertRaises(V):
            verifier.parse_ledger_bytes(data, label="current_ledger")


class FilesystemMutations(unittest.TestCase):
    """Cases 20-25: target-file and evidence-copy gates, via isolated
    temporary directories only -- the real repository is never touched."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="rcc002_s8rr003_test_")
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def _write(self, relpath, content_bytes):
        abspath = os.path.join(self.tmpdir, relpath)
        os.makedirs(os.path.dirname(abspath), exist_ok=True)
        with open(abspath, "wb") as f:
            f.write(content_bytes)
        return abspath

    def test_case20_missing_target_file(self):
        entries = [(sha256_hex(b"a"), "some/present.txt")]
        self._write("some/present.txt", b"a")
        entries.append((sha256_hex(b"b"), "some/absent.txt"))  # never written
        with self.assertRaises(V):
            verifier.validate_target_files(self.tmpdir, entries)

    def test_case21_symlink_target(self):
        real_path = self._write("some/real.txt", b"content")
        link_path = os.path.join(self.tmpdir, "some/linked.txt")
        os.symlink(real_path, link_path)
        entries = [(sha256_hex(b"content"), "some/linked.txt")]
        with self.assertRaises(V):
            verifier.validate_target_files(self.tmpdir, entries)

    def test_case22_wrong_target_digest(self):
        self._write("some/file.txt", b"actual-content")
        entries = [(sha256_hex(b"declared-different-content"), "some/file.txt")]
        with self.assertRaises(V):
            verifier.validate_target_files(self.tmpdir, entries)

    def test_case23_stale_rm_digest_missing_from_historical_ledger(self):
        entries = valid_historical_entries()
        # Tamper: historical copy now carries the *current* certified digest
        # instead of the stale one it must preserve as evidence.
        entries = [
            (verifier.CURRENT_RM_SHA256, p) if p == verifier.CURRENT_RM_PATH else (d, p)
            for d, p in entries
        ]
        with self.assertRaises(V):
            verifier.require_digest_for_path(
                entries, verifier.CURRENT_RM_PATH, verifier.STALE_RM_SHA256, "historical_evidence_stale_rm"
            )

    def test_case24_altered_historical_evidence_bytes(self):
        original = build_ledger_bytes(valid_historical_entries())
        altered = original[:-2] + b"0\n"  # flip trailing content
        self.assertNotEqual(sha256_hex(altered), sha256_hex(original))
        with self.assertRaises(V):
            verifier.require_exact_bytes_hash(altered, sha256_hex(original), "historical_evidence")

    def test_case25_protected_builder_path_injection(self):
        for category_name, category in (
            ("historical", verifier.HISTORICAL_NORMATIVE_PATHS),
            ("s8rr002", verifier.S8RR002_CORRECTION_OUTPUTS),
            ("s8rr003", verifier.S8RR003_LIFECYCLE_OUTPUTS),
        ):
            mutated = list(category) + [verifier.PROTECTED_BUILDER_PATH]
            with self.assertRaises(V):
                verifier.require_protected_builder_absent(mutated, category_name)

        entries = valid_current_entries()
        entries.append((sha256_hex(b"builder"), verifier.PROTECTED_BUILDER_PATH))
        entries.sort(key=lambda e: e[1])
        data = build_ledger_bytes(entries)
        parsed = verifier.parse_ledger_bytes(data, label="current_ledger")
        paths = [p for _, p in parsed]
        with self.assertRaises(V):
            verifier.require_protected_builder_absent(paths, "current_ledger")


def write_scope_manifest(path, doc):
    text = json.dumps(doc, indent=2, ensure_ascii=True) + "\n"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        f.write(text)
    return text.encode("ascii")


class ScopeMetadataContractMutations(unittest.TestCase):
    """Closure tests for S8RR003-CAND-ARCH-001: exact scope-metadata contract."""

    def test_unexpected_additional_metadata_key(self):
        doc = valid_scope_doc()
        doc["extra_note"] = "not part of the approved 14-key contract"
        with self.assertRaises(V) as ctx:
            verifier.require_exact_top_level_keys(doc, "scope")
        self.assertEqual(ctx.exception.invariant, "scope_extra_top_level_keys")

    def test_rogue_additional_metadata_key_with_valid_sha256(self):
        doc = valid_scope_doc()
        rogue_hash = sha256_hex(b"rogue-file-content")
        doc["unauthorized_file_sha256"] = rogue_hash
        # Rejected as an out-of-contract key regardless of its content...
        with self.assertRaises(V) as ctx:
            verifier.require_exact_top_level_keys(doc, "scope")
        self.assertEqual(ctx.exception.invariant, "scope_extra_top_level_keys")
        # ...and independently rejected by the single-hash-authority proof,
        # which does not rely on the key-count gate alone (defense in depth).
        with self.assertRaises(V) as ctx2:
            verifier.require_single_hash_authority(doc, "scope")
        self.assertEqual(ctx2.exception.invariant, "scope_unauthorized_hash_value")

    def test_missing_required_metadata_key(self):
        doc = valid_scope_doc()
        del doc["consumed_by"]
        with self.assertRaises(V) as ctx:
            verifier.require_exact_top_level_keys(doc, "scope")
        self.assertEqual(ctx.exception.invariant, "scope_missing_top_level_keys")

    def test_wrong_metadata_value_type(self):
        doc = valid_scope_doc()
        doc["expected_current_entry_count"] = "145"  # str instead of int
        with self.assertRaises(V) as ctx:
            verifier.validate_scope_metadata(doc)
        self.assertEqual(ctx.exception.invariant, "scope_metadata_wrong_type_expected_current_entry_count")

    def test_non_object_json_root(self):
        tmpdir = tempfile.mkdtemp(prefix="rcc002_s8rr003_test_")
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=True)
        manifest_path = os.path.join(tmpdir, verifier.SCOPE_MANIFEST_PATH)
        os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
        with open(manifest_path, "w", newline="\n") as f:
            f.write("[]\n")
        with self.assertRaises(V) as ctx:
            verifier.load_scope_manifest(tmpdir)
        self.assertEqual(ctx.exception.invariant, "scope_manifest_non_object_root")

    def test_non_list_immutable_reference_category(self):
        doc = valid_scope_doc()
        doc["historical_normative_paths"] = "not-a-list"
        with self.assertRaises(V) as ctx:
            verifier.validate_scope_categories(doc)
        self.assertEqual(ctx.exception.invariant, "scope_category_not_list_historical_normative_paths")

    def test_non_list_candidate_output_category(self):
        doc = valid_scope_doc()
        doc["s8rr002_correction_outputs"] = {"not": "a list"}
        with self.assertRaises(V) as ctx:
            verifier.validate_scope_categories(doc)
        self.assertEqual(ctx.exception.invariant, "scope_category_not_list_s8rr002_correction_outputs")

    def test_non_list_lifecycle_output_category(self):
        doc = valid_scope_doc()
        doc["s8rr003_lifecycle_outputs"] = 6
        with self.assertRaises(V) as ctx:
            verifier.validate_scope_categories(doc)
        self.assertEqual(ctx.exception.invariant, "scope_category_not_list_s8rr003_lifecycle_outputs")

    def test_non_list_current_ledger_category(self):
        doc = valid_scope_doc()
        doc["current_ledger_paths"] = None
        with self.assertRaises(V) as ctx:
            verifier.validate_scope_categories(doc)
        self.assertEqual(ctx.exception.invariant, "scope_category_not_list_current_ledger_paths")

    def test_co_mutated_scope_and_root_ledger_digest_full_chain_rejection(self):
        """Even when the root ledger's recorded digest for the scope manifest
        is updated to match the rogue-keyed scope bytes exactly (i.e. the
        target-hash gate alone would see a fully self-consistent pair), the
        complete verification chain must still reject the scope contract
        violation -- and must do so before ever reaching target hashing."""
        tmpdir = tempfile.mkdtemp(prefix="rcc002_s8rr003_test_")
        self.addCleanup(shutil.rmtree, tmpdir, ignore_errors=True)

        doc = valid_scope_doc()
        doc["unauthorized_file_sha256"] = sha256_hex(b"rogue-file-content")
        manifest_path = os.path.join(tmpdir, verifier.SCOPE_MANIFEST_PATH)
        manifest_bytes = write_scope_manifest(manifest_path, doc)
        co_mutated_digest = sha256_hex(manifest_bytes)

        ledger_path = os.path.join(tmpdir, verifier.LEDGER_PATH)
        with open(ledger_path, "wb") as f:
            f.write(("%s  ./%s\n" % (co_mutated_digest, verifier.SCOPE_MANIFEST_PATH)).encode("ascii"))

        with self.assertRaises(V) as ctx:
            verifier.run_verification(tmpdir)
        self.assertEqual(ctx.exception.invariant, "scope_extra_top_level_keys")


class ResourceHandlingRegression(unittest.TestCase):
    """Closure test for S8RR003-CAND-IMPL-001: no unclosed binary reads."""

    def test_no_resource_warning_on_successful_run(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error", ResourceWarning)
            result = verifier.run_verification(REPO_ROOT)
        self.assertEqual(result["result"], "PASS")


if __name__ == "__main__":
    unittest.main()
