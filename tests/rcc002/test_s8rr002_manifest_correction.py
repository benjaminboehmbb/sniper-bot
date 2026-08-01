"""Focused tests for the RCC-002 S8RR002-BCP-001-REV2 blocker-correction candidate.

Independently proves closure of S8-RR2-B01 (Dataset Manifest view inventory)
and S8-RR2-B02 (Dataset Manifest specification profile) per
docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md
Section 5.7, without relying on the mechanical verifier's own report.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

try:
    import jsonschema  # noqa: F401

    HAVE_JSONSCHEMA = True
except ImportError:  # pragma: no cover - exercised only without the review dependency
    HAVE_JSONSCHEMA = False


def _load_verifier_module():
    spec = importlib.util.spec_from_file_location(
        "rcc002_s8rr002_verifier",
        REPO / "scripts/rcc002/verify_s8rr002_artifacts.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(
    HAVE_JSONSCHEMA, "review-only dependency jsonschema==4.26.0 is not installed"
)
class S8RR002ManifestCorrectionTests(unittest.TestCase):
    RM_PATH = REPO / "docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md"
    DP_PATH = REPO / "docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md"
    SCHEMA_PATH = REPO / "schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json"
    FIXTURE_ROOT = REPO / "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1"
    NEGATIVE_ROOT = FIXTURE_ROOT / "negative"
    STAGE_SCHEMA_PATH = REPO / "schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json"

    ZERO_DIGEST = "0" * 64

    EXPECTED_VIEW_IDENTITY = [
        ("rcc002.view.research-features", "1.0.0",
         "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
        ("rcc002.view.backtest-inputs", "1.0.0",
         "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
        ("rcc002.view.paper", "1.0.0",
         "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
        ("rcc002.view.live", "1.0.0",
         "2f2fd811b5ed8754ad8b02ee2222d885d7da3e7551ecbd5cf65fe38831c0806e"),
        ("rcc002.view.label-research", "1.0.0",
         "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"),
        ("rcc002.view.audit", "2.0.0",
         "0e223d60ed4139f73194f1cb3b886a8eface9229183ad522a093e966827518cc"),
    ]

    EXPECTED_SPEC_IDS_VERSIONS = [
        ("RCC_002_DATA_PIPELINE_SPECIFICATION", "0.8.0"),
        ("RCC-002-DV", "0.6.0"),
        ("RCC-002-IS", "0.4.3"),
        ("RCC-002-ST", "0.4.2"),
        ("RCC-002-RG", "0.5.1"),
        ("RCC-002-LF", "0.5.0"),
        ("RCC-002-RM", "0.9.0"),
    ]

    EXPECTED_NON_SELF_HASHES = [
        "0e060d30b75082b74eb5211b1d378837aa7872d86f62e5e162586e2a2cc37fad",
        "459c4a99a266b420d52a69f2fb1a6b36a99529e999842bc8271f3336c444bb31",
        "0d8ad604cce88daa56193ee054f4d28237d60135a67cebbde883d2c00d18539d",
        "b3de8b4b7c69c30fd811edbeceb246b1b981d7d561c54b585535e72ca0fd8c74",
        "37ee84f1ddd86c0765e9c4df3b57aa5907472ba481f54181e8f8d6dccf354cdc",
        "526665966c83c8fc7254c663474fe08ee721125ae6cdcd88e5a4f5b80af5882f",
    ]

    EXPECTED_IMMUTABLE_HASHES = {
        "schemas/rcc002/manifests/dataset-manifest/1.0.0.schema.json":
            "4462193667777f268119ea253adefb63972dc91b7c8769f14d9cce169543c523",
        "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/minimal-valid.json":
            "1766958549c83bcb1fb808fc1334fe8c11ef0fb17618095296b38ccc8e653002",
        "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/complete-valid.json":
            "1766958549c83bcb1fb808fc1334fe8c11ef0fb17618095296b38ccc8e653002",
        "schemas/rcc002/manifests/stage-manifest/1.0.0.schema.json":
            "12f3e4a39dd0647681867bcd05ead249460dd2882b5b4a74d89620477f8e4c10",
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.verifier = _load_verifier_module()
        cls.rm_text = cls.RM_PATH.read_text(encoding="utf-8")
        cls.dp_text = cls.DP_PATH.read_text(encoding="utf-8")
        cls.schema = json.loads(cls.SCHEMA_PATH.read_text(encoding="utf-8"))

    # -- exact six-view order, identity and hashes --------------------------

    def test_data_pipeline_declares_exact_six_view_order(self) -> None:
        views = self.verifier.extract_data_pipeline_view_contracts(self.dp_text)
        actual = [(v["schema_id"], v["schema_version"], v["allowlist_sha256"]) for v in views]
        self.assertEqual(actual, self.EXPECTED_VIEW_IDENTITY)

    def test_rm_view_registry_matches_data_pipeline_exactly(self) -> None:
        rows = self.verifier.extract_rm_view_registry(self.rm_text)
        actual = [(row[0], row[1], row[3]) for row in rows]
        self.assertEqual(actual, self.EXPECTED_VIEW_IDENTITY)

    # -- exact seven-document order, identity, versions and hashes ----------

    def test_rm_specification_profile_exact_seven_order(self) -> None:
        rows = self.verifier.extract_rm_specification_profile(self.rm_text)
        self.assertEqual(rows, self.EXPECTED_SPEC_IDS_VERSIONS)

    def test_non_self_specification_hashes_are_literal_and_match_disk(self) -> None:
        for (doc_id, version, expected_sha, filename) in zip(
            (d for d, _v in self.EXPECTED_SPEC_IDS_VERSIONS[:6]),
            (v for _d, v in self.EXPECTED_SPEC_IDS_VERSIONS[:6]),
            self.EXPECTED_NON_SELF_HASHES,
            (
                "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
                "RCC_002_DATA_VALIDATION_2026-07-23.md",
                "RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md",
                "RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md",
                "RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md",
                "RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md",
            ),
        ):
            path = REPO / "docs/specifications" / filename
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual, expected_sha, f"{doc_id}/{version}")

    # -- RM 0.9.0 exposes only Dataset Manifest 1.0.1 for prospective S8 ----

    def test_rm_declares_dataset_manifest_1_0_1_and_withdraws_1_0_0(self) -> None:
        normalized = " ".join(self.rm_text.split())
        self.assertIn(
            "Dataset Manifest | `rcc002.dataset-manifest` | `1.0.1` | "
            "`rcc002.dataset-manifest/1.0.1` |",
            normalized,
        )
        self.assertIn(
            "ist für prospektive S8-Produktion zurückgezogen: neuer Code DARF "
            "Dataset Manifest `1.0.0` NICHT ausgeben.",
            normalized,
        )
        self.assertIn("Version `0.9.0`", self.rm_text)

    # -- Dataset Manifest 1.0.1 accepts every positive fixture --------------

    def test_dataset_manifest_1_0_1_accepts_every_positive_fixture(self) -> None:
        from jsonschema import Draft202012Validator

        Draft202012Validator.check_schema(self.schema)
        validator = Draft202012Validator(self.schema)
        positive = sorted(self.FIXTURE_ROOT.glob("*-valid.json"))
        self.assertEqual(len(positive), 2)
        for path in positive:
            payload = json.loads(path.read_text(encoding="utf-8"))
            errors = list(validator.iter_errors(payload))
            self.assertEqual(errors, [], f"{path.name} unexpectedly rejected: {errors}")

    def test_positive_fixtures_are_distinct_payloads(self) -> None:
        hashes = {
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.FIXTURE_ROOT.glob("*-valid.json")
        }
        self.assertEqual(len(hashes), 2)

    # -- every negative fixture is rejected for its declared reason ---------

    def test_every_negative_fixture_rejected_and_ledger_complete(self) -> None:
        from jsonschema import Draft202012Validator

        validator = Draft202012Validator(self.schema)
        ledger = json.loads((self.NEGATIVE_ROOT / "CASE_LEDGER.json").read_text(encoding="utf-8"))
        cases = ledger["cases"]
        negative_files = sorted(
            p.name for p in self.NEGATIVE_ROOT.glob("*.json") if p.name != "CASE_LEDGER.json"
        )
        self.assertEqual(len(negative_files), 21)
        self.assertEqual(sorted(cases), negative_files)
        for name in negative_files:
            payload = json.loads((self.NEGATIVE_ROOT / name).read_text(encoding="utf-8"))
            errors = list(validator.iter_errors(payload))
            self.assertTrue(errors, f"{name} was unexpectedly accepted")

    def test_semantic_negative_fixtures_isolate_declared_dimension(self) -> None:
        baseline = json.loads((self.FIXTURE_ROOT / "minimal-valid.json").read_text(encoding="utf-8"))
        ledger = json.loads((self.NEGATIVE_ROOT / "CASE_LEDGER.json").read_text(encoding="utf-8"))
        self.verifier.verify_semantic_negative_isolation(baseline, ledger)

    # -- the verifier uses only the committed scope manifest -----------------

    def test_verifier_scope_manifest_is_used_and_free_of_unscoped_traversal(self) -> None:
        source = (REPO / "scripts/rcc002/verify_s8rr002_artifacts.py").read_text(encoding="utf-8")
        self.assertIn(
            'SCOPE_PATH = REPO / "docs/review/evidence/'
            'RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json"',
            source,
        )
        self.assertIn("load_scope()", source)
        for forbidden in ("rglob(", "os.walk(", "subprocess", "glob.glob(", "check_output("):
            self.assertNotIn(forbidden, source)

    def test_scope_manifest_loads_and_declares_findings(self) -> None:
        scope = self.verifier.load_scope()
        self.assertEqual(scope["scope_schema_version"], "1")
        self.assertEqual(sorted(scope["findings_in_scope"]), ["S8-RR2-B01", "S8-RR2-B02"])

    # -- the verifier does not merely count fixture files --------------------

    def test_verifier_performs_structural_and_semantic_reconciliation(self) -> None:
        source = (REPO / "scripts/rcc002/verify_s8rr002_artifacts.py").read_text(encoding="utf-8")
        self.assertIn("iter_errors", source)
        self.assertIn("verify_semantic_negative_isolation", source)
        self.assertIn("verify_positive_fixture_contract", source)
        self.assertNotRegex(source, r"assert len\(positive\) ==")

    def test_verifier_end_to_end_passes(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            exit_code = self.verifier.main()
        self.assertEqual(exit_code, 0)
        report = json.loads(buf.getvalue())
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["positive_fixture_files"], 2)
        self.assertEqual(report["positive_fixture_distinct_payloads"], 2)
        self.assertEqual(report["negative_fixtures_verified"], 21)

    # -- Section 24 vs. fixtures: identical except RM self-hash placeholder --

    def test_section_24_matches_fixture_contract_except_self_hash_placeholder(self) -> None:
        example = self.verifier.extract_section_24_example(self.rm_text)
        fixture = json.loads((self.FIXTURE_ROOT / "minimal-valid.json").read_text(encoding="utf-8"))

        self.assertEqual(example["views"], fixture["views"])

        example_ids_versions = [(e["id"], e["version"]) for e in example["specification_profile"]]
        fixture_ids_versions = [(f["id"], f["version"]) for f in fixture["specification_profile"]]
        self.assertEqual(example_ids_versions, fixture_ids_versions)

        for e_entry, f_entry in zip(
            example["specification_profile"][:6], fixture["specification_profile"][:6]
        ):
            self.assertEqual(e_entry["sha256"], f_entry["sha256"])

        self.assertEqual(example["specification_profile"][6]["sha256"], self.ZERO_DIGEST)
        self.assertNotEqual(fixture["specification_profile"][6]["sha256"], self.ZERO_DIGEST)
        self.assertEqual(len(fixture["specification_profile"][6]["sha256"]), 64)

    # -- old 1.0.0 files remain byte-identical -------------------------------

    def test_dataset_manifest_1_0_0_and_stage_manifest_1_0_0_byte_identical(self) -> None:
        for rel_path, expected in self.EXPECTED_IMMUTABLE_HASHES.items():
            actual = hashlib.sha256((REPO / rel_path).read_bytes()).hexdigest()
            self.assertEqual(actual, expected, rel_path)

    # -- Stage Manifest specification_profile untouched and distinct --------

    def test_stage_manifest_specification_profile_is_generic_and_untouched(self) -> None:
        stage_schema = json.loads(self.STAGE_SCHEMA_PATH.read_text(encoding="utf-8"))
        spec_profile_schema = stage_schema["properties"]["specification_profile"]
        self.assertNotIn("prefixItems", spec_profile_schema)
        self.assertEqual(spec_profile_schema.get("minItems"), 1)
        self.assertNotIn("maxItems", spec_profile_schema)


@unittest.skipUnless(
    HAVE_JSONSCHEMA, "review-only dependency jsonschema==4.26.0 is not installed"
)
class S8RR002ScopeMutationTests(unittest.TestCase):
    """Mutation tests for Finding S8RR002-CAND-ARCH-001.

    Every mutation here operates on an in-memory deep copy of the real,
    committed scope dict, or on isolated temporary directories/files. No
    repository artifact is ever written to. Each test proves that the
    repaired verifier fails closed for exactly the class of scope defect
    the original finding identified as silently accepted.
    """

    SCOPE_PATH = REPO / "docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json"

    @classmethod
    def setUpClass(cls) -> None:
        cls.real_scope = json.loads(cls.SCOPE_PATH.read_text(encoding="utf-8"))

    def _mutated_scope(self) -> dict:
        return copy.deepcopy(self.real_scope)

    def _fresh_verifier(self):
        return _load_verifier_module()

    # 1. one removed required immutable-input entry ------------------------

    def test_removed_immutable_input_entry_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        scope["immutable_reference_inputs"] = scope["immutable_reference_inputs"][1:]
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 2. one removed required candidate-output entry ------------------------

    def test_removed_candidate_output_entry_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        scope["correction_candidate_outputs"] = scope["correction_candidate_outputs"][:-1]
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 3. an undeclared extra fixture or candidate path -----------------------

    def test_undeclared_extra_fixture_file_on_disk_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        with tempfile.TemporaryDirectory() as tmp_fixture, tempfile.TemporaryDirectory() as tmp_negative:
            fixture_root = Path(tmp_fixture)
            negative_root = Path(tmp_negative)
            (fixture_root / "sneaky-undeclared.json").write_text("{}", encoding="utf-8")
            verifier.FIXTURE_ROOT = fixture_root
            verifier.NEGATIVE_ROOT = negative_root
            with self.assertRaises(verifier.VerificationError):
                verifier.verify_no_undeclared_fixture_files(scope)

    def test_undeclared_extra_candidate_path_in_scope_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        scope["correction_candidate_outputs"] = sorted(
            scope["correction_candidate_outputs"] + ["docs/specifications/RCC_002_DATA_VALIDATION_2026-07-23.md"]
        )
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 4. a duplicate within one category -------------------------------------

    def test_duplicate_within_one_category_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        scope["correction_candidate_outputs"] = scope["correction_candidate_outputs"] + [
            scope["correction_candidate_outputs"][-1]
        ]
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 5. a duplicate across categories ---------------------------------------

    def test_duplicate_across_categories_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        shared = scope["correction_candidate_outputs"][0]
        scope["immutable_reference_inputs"] = sorted(scope["immutable_reference_inputs"] + [shared])
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 6. an absolute path -----------------------------------------------------

    def test_absolute_path_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        mutated = list(scope["correction_candidate_outputs"])
        mutated[0] = "/etc/passwd"
        scope["correction_candidate_outputs"] = sorted(mutated)
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 7. a parent-traversal path ----------------------------------------------

    def test_parent_traversal_path_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        mutated = list(scope["correction_candidate_outputs"])
        mutated[0] = "tests/fixtures/../../../etc/passwd"
        scope["correction_candidate_outputs"] = sorted(mutated)
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 8. a required path placed in the wrong category -------------------------

    def test_required_path_in_wrong_category_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        moved = "requirements-rcc002-review.txt"
        self.assertIn(moved, scope["correction_candidate_outputs"])
        scope["correction_candidate_outputs"] = [
            p for p in scope["correction_candidate_outputs"] if p != moved
        ]
        scope["immutable_reference_inputs"] = sorted(scope["immutable_reference_inputs"] + [moved])
        with self.assertRaises(verifier.VerificationError):
            verifier.validate_scope(scope)

    # 9. incorrect scope metadata ----------------------------------------------

    def test_incorrect_scope_metadata_is_rejected(self) -> None:
        verifier = self._fresh_verifier()
        for field, bad_value in (
            ("scope_schema_version", "2"),
            ("scope_id", "WRONG_SCOPE_ID"),
            ("correction_id", "RCC-002-WRONG-ID"),
            ("consumed_by", "scripts/rcc002/some_other_script.py"),
            ("path_ordering", "arbitrary order"),
            ("findings_in_scope", ["S8-RR2-B01"]),
        ):
            with self.subTest(field=field):
                scope = self._mutated_scope()
                scope[field] = bad_value
                with self.assertRaises(verifier.VerificationError):
                    verifier.validate_scope(scope)

    # 10. an incomplete candidate SHA-256 inventory ----------------------------

    def test_incomplete_candidate_inventory_never_reaches_pass(self) -> None:
        """The exact mutation used by the ChatGPT independent review.

        Removes tests/fixtures/.../negative/wrong-schema-identity.json from
        correction_candidate_outputs while leaving the fixture file itself on
        disk untouched, then proves the full verifier rejects the mutated
        scope rather than emitting a PASS with a shrunken inventory.
        """
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        target = (
            "tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/"
            "negative/wrong-schema-identity.json"
        )
        self.assertIn(target, scope["correction_candidate_outputs"])
        scope["correction_candidate_outputs"] = [
            p for p in scope["correction_candidate_outputs"] if p != target
        ]

        real_fixture_path = REPO / target
        self.assertTrue(real_fixture_path.is_file(), "fixture must remain on disk")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_scope_path = Path(tmp_dir) / "mutated_scope.json"
            tmp_scope_path.write_text(json.dumps(scope), encoding="utf-8")
            verifier.SCOPE_PATH = tmp_scope_path

            buf = io.StringIO()
            with self.assertRaises(verifier.VerificationError):
                with redirect_stdout(buf):
                    verifier.main()
            self.assertEqual(buf.getvalue(), "", "no PASS report may be printed for a rejected scope")

        # the fixture file itself was never touched by this test
        self.assertTrue(real_fixture_path.is_file())

    # -- positive control: the unmutated real scope still passes ------------

    def test_unmutated_scope_validates_and_yields_exactly_30_candidate_outputs(self) -> None:
        verifier = self._fresh_verifier()
        scope = self._mutated_scope()
        verifier.validate_scope(scope)  # must not raise
        self.assertEqual(len(scope["correction_candidate_outputs"]), 30)
        self.assertEqual(len(scope["immutable_reference_inputs"]), 11)


if __name__ == "__main__":
    unittest.main()
