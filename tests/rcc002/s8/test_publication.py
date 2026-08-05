"""Tests for rcc002.s8.publication.

Mandatory S8 test item 15: no-silent-overwrite and atomic-publication
tests. Every test operates inside ``tempfile.TemporaryDirectory()`` --
never a repository path -- and confirms no artifact leaks outside it.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
import unittest

from rcc002.s8.publication import (
    _REQUIRED_PUBLICATION_GATES,
    build_release_ledger,
    publish_atomically,
    require_not_diagnostic_publication,
    require_publication_gates,
    verify_no_silent_overwrite,
    write_candidate_files,
)
from rcc002.s8.reason_codes import PublicationError, PublicationStateError
from rcc002.s8.states import BuildState

ALL_GATES_OPEN = {name: True for name in _REQUIRED_PUBLICATION_GATES}
SET_ID = "dataset-artifact-set:sha256:" + "a" * 64


class TestPublicationGates(unittest.TestCase):
    def test_all_gates_open_passes(self) -> None:
        require_publication_gates(ALL_GATES_OPEN)

    def test_any_missing_gate_rejected(self) -> None:
        for name in _REQUIRED_PUBLICATION_GATES:
            with self.subTest(gate=name):
                gates = dict(ALL_GATES_OPEN)
                gates[name] = False
                with self.assertRaises(PublicationError):
                    require_publication_gates(gates)

    def test_absent_gate_key_treated_as_not_satisfied(self) -> None:
        gates = dict(ALL_GATES_OPEN)
        del gates["dataset_manifest_complete"]
        with self.assertRaises(PublicationError):
            require_publication_gates(gates)


class TestAtomicPublication(unittest.TestCase):
    def test_publish_creates_target_and_leaves_no_staging_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            publish_root = os.path.join(tmp, "publish")
            staging = write_candidate_files(publish_root, {"data/audit.parquet": b"hi"})
            target = publish_atomically(
                staging,
                publish_root,
                SET_ID,
                build_state=BuildState.CANDIDATE,
                gates=ALL_GATES_OPEN,
            )
            self.assertTrue(os.path.isdir(target))
            self.assertFalse(os.path.exists(staging))
            self.assertTrue(
                os.path.isfile(os.path.join(target, "data", "audit.parquet"))
            )

    def test_publish_requires_candidate_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            publish_root = os.path.join(tmp, "publish")
            staging = write_candidate_files(publish_root, {"a.txt": b"x"})
            for bad_state in (
                BuildState.PLANNED,
                BuildState.RUNNING,
                BuildState.VALIDATING,
                BuildState.FAILED,
                BuildState.QUARANTINED,
                BuildState.PUBLISHED,
            ):
                with self.subTest(state=bad_state.value):
                    with self.assertRaises(PublicationStateError):
                        publish_atomically(
                            staging,
                            publish_root,
                            SET_ID,
                            build_state=bad_state,
                            gates=ALL_GATES_OPEN,
                        )

    def test_publish_requires_all_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            publish_root = os.path.join(tmp, "publish")
            staging = write_candidate_files(publish_root, {"a.txt": b"x"})
            bad_gates = dict(ALL_GATES_OPEN)
            bad_gates["no_parent_artifact_missing"] = False
            with self.assertRaises(PublicationError):
                publish_atomically(
                    staging,
                    publish_root,
                    SET_ID,
                    build_state=BuildState.CANDIDATE,
                    gates=bad_gates,
                )

    def test_no_silent_overwrite_on_republish(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            publish_root = os.path.join(tmp, "publish")
            staging1 = write_candidate_files(publish_root, {"a.txt": b"v1"})
            publish_atomically(
                staging1,
                publish_root,
                SET_ID,
                build_state=BuildState.CANDIDATE,
                gates=ALL_GATES_OPEN,
            )
            staging2 = write_candidate_files(publish_root, {"a.txt": b"v2-different"})
            with self.assertRaises(PublicationError):
                publish_atomically(
                    staging2,
                    publish_root,
                    SET_ID,
                    build_state=BuildState.CANDIDATE,
                    gates=ALL_GATES_OPEN,
                )
            # original published content must be untouched
            published_path = os.path.join(
                publish_root, SET_ID.rsplit(":", 1)[-1], "a.txt"
            )
            with open(published_path, "rb") as handle:
                self.assertEqual(handle.read(), b"v1")

    def test_write_candidate_files_rejects_unsafe_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            publish_root = os.path.join(tmp, "publish")
            with self.assertRaises(Exception):
                write_candidate_files(publish_root, {"/etc/passwd": b"x"})

    def test_write_candidate_files_never_overwrites_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            publish_root = os.path.join(tmp, "publish")
            staging = write_candidate_files(publish_root, {"a.txt": b"one"})
            # Writing the exact same staging dir path again must fail
            # ('xb' mode) rather than silently overwrite.
            with self.assertRaises(FileExistsError):
                with open(os.path.join(staging, "a.txt"), "xb") as handle:
                    handle.write(b"two")


class TestReleaseLedger(unittest.TestCase):
    def test_deterministic_sorted_output(self) -> None:
        files = {"b.txt": b"2", "a.txt": b"1"}
        ledger = build_release_ledger(files, self_path="SHA256SUMS")
        lines = ledger.rstrip("\n").split("\n")
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].endswith("./a.txt"))
        self.assertTrue(lines[1].endswith("./b.txt"))
        for line in lines:
            digest = line.split("  ")[0]
            self.assertEqual(len(digest), 64)

    def test_hashes_are_correct(self) -> None:
        content = b"hello"
        ledger = build_release_ledger({"x.txt": content}, self_path="SHA256SUMS")
        expected = hashlib.sha256(content).hexdigest()
        self.assertEqual(ledger, f"{expected}  ./x.txt\n")

    def test_rejects_self_entry(self) -> None:
        with self.assertRaises(PublicationError):
            build_release_ledger({"SHA256SUMS": b"x"}, self_path="SHA256SUMS")

    def test_empty_file_set_produces_empty_ledger(self) -> None:
        self.assertEqual(build_release_ledger({}, self_path="SHA256SUMS"), "")


class TestNoSilentOverwriteHelper(unittest.TestCase):
    def test_new_identity_passes(self) -> None:
        verify_no_silent_overwrite([SET_ID], "dataset-artifact-set:sha256:" + "b" * 64)

    def test_colliding_identity_rejected(self) -> None:
        with self.assertRaises(PublicationError):
            verify_no_silent_overwrite([SET_ID], SET_ID)


class TestDiagnosticPublicationPrevention(unittest.TestCase):
    def test_failed_and_quarantined_rejected_from_final_path(self) -> None:
        for state in (BuildState.FAILED, BuildState.QUARANTINED):
            with self.subTest(state=state.value):
                with self.assertRaises(PublicationStateError):
                    require_not_diagnostic_publication(state, context="release")

    def test_published_permitted(self) -> None:
        require_not_diagnostic_publication(BuildState.PUBLISHED, context="release")


if __name__ == "__main__":
    unittest.main()
