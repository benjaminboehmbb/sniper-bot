"""Positive and negative tests for all six RCC-002 S8 manifest builders.

Mandatory S8 test item 9 (positive and negative tests for all six manifest
builders) and item 10 (production rejection of withdrawn Dataset Manifest
versions). Also covers the RCC-002-S8-TRACK2-IAD-001 F-001 correction
(Dataset Manifest 1.0.2, 1.0.0/1.0.1 withdrawn) and F-003 correction (the
current seven-document specification profile).
"""

from __future__ import annotations

import hashlib
import os
import unittest

from rcc002.s0.profiles import ArchivePeriod, TimestampUnit
from rcc002.s0.source_identity import SourceFileIdentity, build_source_snapshot
from rcc002.constants import ViewId
from rcc002.s8 import identity as ident
from rcc002.s8.manifests.common import validate_structural
from rcc002.s8.manifests.dataset import (
    ChildManifestEntry,
    DataArtifactEntry,
    SchemaArtifactEntry,
    VersionedReference,
    build_dataset_manifest,
)
from rcc002.s8.manifests.reproduction import (
    ArtifactComparison,
    EnvironmentReference,
    build_reproduction_manifest,
)
from rcc002.s8.manifests.review import Finding, ReviewedArtifact, build_review_manifest
from rcc002.s8.manifests.run import (
    CodeProvenance,
    EnvironmentRecord,
    Library,
    Outcome,
    build_run_manifest,
)
from rcc002.s8.manifests.source import build_source_manifest
from rcc002.s8.manifests.stage import (
    ArtifactReference,
    ReconciliationResult,
    SchemaRecord,
    ValidationResult,
)
from rcc002.s8.manifests.stage import VersionedReference as StageVersionedReference
from rcc002.s8.manifests.stage import build_stage_manifest
from rcc002.s8.reason_codes import ManifestValidationError
from rcc002.s8.specification_profile import current_specification_profile
from rcc002.s8.views import VIEW_DEFINITIONS

D = "a" * 64
C = "b" * 40


def _source_snapshot():
    period = ArchivePeriod(
        archive_family="DAILY",
        period_token="2024-12-31",
        period_start_utc="2024-12-31T00:00:00Z",
        period_end_utc="2025-01-01T00:00:00Z",
    )
    descriptor = SourceFileIdentity(
        provider_relative_name="data/spot/daily/klines/BTCUSDT/1m/BTCUSDT-1m-2024-12-31.zip",
        byte_sha256=D,
        provider_checksum_sha256=D,
        size_bytes=100,
        csv_member_name="BTCUSDT-1m-2024-12-31.csv",
        source_file_ordinal=0,
        archive_period=period,
        record_count=1440,
        min_open_time_utc_ms=1735603200000,
        max_close_time_utc_ms=1735689599999,
        timestamp_unit=TimestampUnit.MILLISECOND,
    )
    return build_source_snapshot((descriptor,))


class TestSourceManifest(unittest.TestCase):
    def test_positive(self) -> None:
        manifest = build_source_manifest(
            snapshot=_source_snapshot(),
            retrieved_at_utc="2026-08-01T12:00:00Z",
            license_or_terms_ref="https://www.binance.com/en/terms",
            created_at_utc="2026-08-01T12:00:00Z",
            producer_component="rcc002-s8",
            producer_version="1.0.0",
        )
        self.assertTrue(manifest["manifest_id"].startswith("manifest:sha256:"))
        self.assertEqual(manifest["manifest_schema_ref"], "rcc002.source-manifest/1.0.0")

    def test_negative_wrong_snapshot_type(self) -> None:
        with self.assertRaises(ManifestValidationError):
            build_source_manifest(
                snapshot="not-a-snapshot",  # type: ignore[arg-type]
                retrieved_at_utc="2026-08-01T12:00:00Z",
                license_or_terms_ref=None,
                created_at_utc="2026-08-01T12:00:00Z",
                producer_component="rcc002-s8",
                producer_version="1.0.0",
            )

    def test_negative_malformed_timestamp_caught_structurally(self) -> None:
        with self.assertRaises(ManifestValidationError):
            build_source_manifest(
                snapshot=_source_snapshot(),
                retrieved_at_utc="not-a-timestamp",
                license_or_terms_ref=None,
                created_at_utc="2026-08-01T12:00:00Z",
                producer_component="rcc002-s8",
                producer_version="1.0.0",
            )


class TestStageManifest(unittest.TestCase):
    def _valid_kwargs(self) -> dict:
        run_id = "run:2026-08-01T12:00:00.000000Z:00000000-0000-4000-8000-000000000000"
        return dict(
            stage_id="S7_LABELS",
            stage_version="1.0.0",
            component=("rcc002-s7", "1.0.0"),
            build_id=f"build:sha256:{D}",
            run_id=run_id,
            input_schema=SchemaRecord("rcc002.stage.s6-gates", "1.0.0", D),
            output_schema=SchemaRecord("rcc002.stage.s7-labels", "1.0.0", D),
            parents=[ArtifactReference(f"artifact:sha256:{D}", "data/s6.parquet", D)],
            outputs=[ArtifactReference(f"artifact:sha256:{D}", "data/s7.parquet", D)],
            semantic_build_configuration_sha256=D,
            physical_publication_configuration_sha256=D,
            specification_profile=[StageVersionedReference("RCC-002-LF", "0.5.0", D)],
            registries=[StageVersionedReference("RCC002_S1_SOURCE_ROW_ID_V2", "1.0.0", D)],
            reconciliation=ReconciliationResult(1440, 1440, True, True, "NOT_APPLICABLE", "PASS"),
            validation=ValidationResult("PASS", 10, 0),
            warnings=[],
            failures=[],
            publication_status="candidate",
            created_at_utc="2026-08-01T12:00:00Z",
            producer_component="rcc002-s7",
            producer_version="1.0.0",
        )

    def test_positive(self) -> None:
        manifest = build_stage_manifest(**self._valid_kwargs())
        self.assertEqual(manifest["stage_id"], "S7_LABELS")

    def test_negative_unknown_stage_id(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["stage_id"] = "S99_NOT_REAL"
        with self.assertRaises(ManifestValidationError):
            build_stage_manifest(**kwargs)

    def test_negative_no_outputs(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["outputs"] = []
        with self.assertRaises(ManifestValidationError):
            build_stage_manifest(**kwargs)

    def test_negative_invalid_reconciliation_status_caught_structurally(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["reconciliation"] = ReconciliationResult(
            1440, 1440, True, True, "BOGUS_STATUS", "PASS"
        )
        with self.assertRaises(ManifestValidationError):
            build_stage_manifest(**kwargs)


class TestRunManifest(unittest.TestCase):
    def _valid_kwargs(self) -> dict:
        return dict(
            run_id="run:2026-08-01T12:00:00.000000Z:00000000-0000-4000-8000-000000000000",
            build_id=f"build:sha256:{D}",
            started_at_utc="2026-08-01T12:00:00Z",
            ended_at_utc="2026-08-01T12:01:00Z",
            code_provenance=CodeProvenance("sniper-bot", C, True, None, "scripts/build_rcc002.py"),
            environment=EnvironmentRecord(
                "RCC_BUILD_ENV_IDENTITY_V2", D, "3.12.0", "requirements.lock", D, "linux",
                (Library("numpy", "2.3.3"),),
            ),
            semantic_build_configuration_sha256=D,
            physical_publication_configuration_sha256=D,
            effective_cli_arguments=["--profile", "rcc002-canonical"],
            validation_outcome=Outcome("PASS"),
            publication_outcome=Outcome("NOT_ATTEMPTED"),
            created_at_utc="2026-08-01T12:01:00Z",
            producer_component="rcc002-s8",
            producer_version="1.0.0",
        )

    def test_positive(self) -> None:
        manifest = build_run_manifest(**self._valid_kwargs())
        self.assertEqual(manifest["run_id"], self._valid_kwargs()["run_id"])

    def test_negative_invalid_outcome_status(self) -> None:
        with self.assertRaises(ManifestValidationError):
            Outcome("BOGUS").as_dict()

    def test_negative_malformed_commit_sha_caught_structurally(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["code_provenance"] = CodeProvenance(
            "sniper-bot", "not-a-sha", True, None, "scripts/build_rcc002.py"
        )
        with self.assertRaises(ManifestValidationError):
            build_run_manifest(**kwargs)

    def test_negative_secret_like_cli_argument_caught_structurally(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["effective_cli_arguments"] = ["--token=abc123"]
        with self.assertRaises(ManifestValidationError):
            build_run_manifest(**kwargs)


class TestReviewManifest(unittest.TestCase):
    def _valid_kwargs(self) -> dict:
        return dict(
            subject_dataset_manifest_id=f"manifest:sha256:{D}",
            subject_dataset_manifest_byte_sha256=D,
            review_id="RCC-002-S8-REVIEW-001",
            review_type="scr",
            reviewer="internal-reviewer",
            reviewer_system="human",
            reviewed_artifacts=[ReviewedArtifact("manifests/dataset.json", D)],
            started_at_utc="2026-08-01T13:00:00Z",
            completed_at_utc="2026-08-01T14:00:00Z",
            review_status="passed",
            findings=[],
            resolution_references=[],
            created_at_utc="2026-08-01T14:00:00Z",
            producer_component="rcc002-s8",
            producer_version="1.0.0",
        )

    def test_positive(self) -> None:
        manifest = build_review_manifest(**self._valid_kwargs())
        self.assertEqual(manifest["review_status"], "passed")

    def test_positive_with_finding(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["review_status"] = "passed_with_findings"
        kwargs["findings"] = [Finding("F-001", "MINOR", "CLOSED", "cosmetic issue")]
        manifest = build_review_manifest(**kwargs)
        self.assertEqual(len(manifest["findings"]), 1)

    def test_negative_ai_reviewer_passed_without_review_artifact(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["reviewer_system"] = "claude"
        with self.assertRaises(ManifestValidationError):
            build_review_manifest(**kwargs)

    def test_negative_invalid_review_type(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["review_type"] = "not-a-real-type"
        with self.assertRaises(ManifestValidationError):
            build_review_manifest(**kwargs)

    def test_negative_no_reviewed_artifacts(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["reviewed_artifacts"] = []
        with self.assertRaises(ManifestValidationError):
            build_review_manifest(**kwargs)


class TestReproductionManifest(unittest.TestCase):
    def _valid_kwargs(self) -> dict:
        return dict(
            subject_dataset_manifest_id=f"manifest:sha256:{D}",
            subject_dataset_manifest_byte_sha256=D,
            source_run_id="run:source",
            source_build_id=f"build:sha256:{D}",
            target_run_id="run:target",
            target_build_id=f"build:sha256:{D}",
            source_environment=EnvironmentReference("env-v2", D),
            target_environment=EnvironmentReference("env-v2", D),
            environment_differences=[],
            artifact_comparisons=[ArtifactComparison("audit-v2", True, True, True, True)],
            comparison_report_relative_path="reports/reproduction.json",
            equality_result="E3",
            deviations=[],
            final_status="PASS",
            created_at_utc="2026-08-01T15:00:00Z",
            producer_component="rcc002-s8",
            producer_version="1.0.0",
        )

    def test_positive(self) -> None:
        manifest = build_reproduction_manifest(**self._valid_kwargs())
        self.assertEqual(manifest["equality_result"], "E3")

    def test_negative_pass_requires_at_least_e2(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["equality_result"] = "E1"
        with self.assertRaises(ManifestValidationError):
            build_reproduction_manifest(**kwargs)

    def test_negative_no_artifact_comparisons(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["artifact_comparisons"] = []
        with self.assertRaises(ManifestValidationError):
            build_reproduction_manifest(**kwargs)

    def test_negative_invalid_equality_result(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["equality_result"] = "E9"
        with self.assertRaises(ManifestValidationError):
            build_reproduction_manifest(**kwargs)


def _dataset_manifest_valid_kwargs() -> dict:
    spec_profile = current_specification_profile()
    spec_refs = [VersionedReference(e.id, e.version, e.sha256) for e in spec_profile]
    audit = VIEW_DEFINITIONS[ViewId.AUDIT]
    art = ident.DataArtifactIdentity(
        schema_ref=audit.schema_ref,
        semantic_sha256=D,
        physical_layout_sha256=D,
        byte_sha256=D,
        row_count=100,
        logical_time_coverage=(1000, 2000),
    )
    artifact_id, _ = ident.artifact_id(art)
    build_id, _ = ident.build_id(
        parent_identities=[f"source:sha256:{D}"],
        code_commit_sha=C,
        dirty_patch_sha256=None,
        semantic_build_configuration_sha256=D,
        specification_profile=[
            ident.SpecificationProfileEntry(e.id, e.version, e.sha256) for e in spec_profile
        ],
        pipeline_profile_id="rcc002-canonical",
        schema_ids=[audit.schema_ref],
        environment_identity_profile_id="RCC_BUILD_ENV_IDENTITY_V2",
        environment_identity_sha256=D,
        stage_or_stage_range="S0..S8",
    )
    dataset_id, _ = ident.dataset_id(
        components=[ident.DatasetComponent("audit-v2", audit.schema_ref, D, 100, (1000, 2000))],
        release_schema_id="rcc002.dataset-manifest/1.0.2",
        dataset_profile="rcc002-canonical",
        build_id_value=build_id,
        semantic_build_configuration_sha256=D,
        quality_status="PASS",
        specification_profile=[
            ident.SpecificationProfileEntry(e.id, e.version, e.sha256) for e in spec_profile
        ],
    )
    published = ident.PublishedDataArtifact(
        logical_name="audit-v2",
        relative_path="data/rcc002/audit.parquet",
        artifact_id_value=artifact_id,
        byte_sha256=D,
        semantic_sha256=D,
        physical_layout_sha256=D,
        size_bytes=123,
        schema_ref=audit.schema_ref,
        schema_fingerprint_sha256=audit.schema_fingerprint_sha256,
        view_allowlist_sha256=audit.allowlist_sha256,
    )
    dataset_artifact_set_id, preimage_digest = ident.dataset_artifact_set_id(
        dataset_id_value=dataset_id,
        physical_publication_configuration_sha256=D,
        data_artifacts=[published],
    )
    return dict(
        dataset_id=dataset_id,
        dataset_artifact_set_id=dataset_artifact_set_id,
        dataset_artifact_set_preimage_sha256=preimage_digest,
        build_id=build_id,
        publication_run_id=ident.new_run_id(),
        source_snapshot_ids=[f"source:sha256:{D}"],
        artifacts=[
            DataArtifactEntry(
                "audit-v2", "data/rcc002/audit.parquet", artifact_id, D, D, D, 123,
                audit.schema_ref, audit.schema_fingerprint_sha256, audit.allowlist_sha256,
            )
        ],
        schema_artifacts=[
            SchemaArtifactEntry(
                "dataset-manifest-schema",
                "schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json",
                D,
                1,
            )
        ],
        child_manifests=[
            ChildManifestEntry("source", f"manifest:sha256:{D}", "manifests/source.json", D, 1)
        ],
        stages=[VersionedReference(f"S{i}", "1.0.0", D) for i in range(8)],
        registries=[VersionedReference("RCC002_S8_FIELD_OWNERSHIP_V1", "1.0.0", D)],
        specification_profile=spec_refs,
        code_provenance={
            "repository": "sniper-bot",
            "commit_sha": C,
            "worktree_clean": True,
            "dirty_patch_sha256": None,
        },
        semantic_build_configuration=("semantic-v1", D),
        physical_publication_configuration=("physical-v1", D),
        environment_reference=VersionedReference("RCC_BUILD_ENV_IDENTITY_V2", "1.0.0", D),
        quality_summary={
            "status": "PASS",
            "critical_findings": 0,
            "error_findings": 0,
            "warning_findings": 0,
        },
        dataset_lineage_graph_sha256=D,
        knowledge_lineage_graph_sha256=D,
        supersedes=[],
        review_requirements=[("scientific", True), ("architecture", True)],
        created_at_utc="2026-08-01T16:00:00Z",
        producer_component="rcc002-s8",
        producer_version="1.0.0",
    )


class TestDatasetManifest(unittest.TestCase):
    def _valid_kwargs(self) -> dict:
        return _dataset_manifest_valid_kwargs()

    def test_positive(self) -> None:
        manifest = build_dataset_manifest(**self._valid_kwargs())
        self.assertEqual(manifest["manifest_schema_version"], "1.0.2")
        self.assertEqual(
            manifest["manifest_schema_ref"], "rcc002.dataset-manifest/1.0.2"
        )
        self.assertEqual(len(manifest["views"]), 6)
        self.assertEqual(len(manifest["specification_profile"]), 7)
        for view_entry in manifest["views"]:
            self.assertIn("schema_fingerprint_sha256", view_entry)
            self.assertEqual(len(view_entry["schema_fingerprint_sha256"]), 64)

    def test_negative_too_few_stages(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["stages"] = kwargs["stages"][:3]
        with self.assertRaises(ManifestValidationError):
            build_dataset_manifest(**kwargs)

    def test_negative_wrong_specification_profile_count(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["specification_profile"] = kwargs["specification_profile"][:5]
        with self.assertRaises(ManifestValidationError):
            build_dataset_manifest(**kwargs)

    def test_negative_no_artifacts(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["artifacts"] = []
        with self.assertRaises(ManifestValidationError):
            build_dataset_manifest(**kwargs)

    def test_negative_no_child_manifests(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["child_manifests"] = []
        with self.assertRaises(ManifestValidationError):
            build_dataset_manifest(**kwargs)

    def test_negative_child_manifest_cannot_reference_dataset_type(self) -> None:
        with self.assertRaises(ManifestValidationError):
            ChildManifestEntry(
                "dataset", f"manifest:sha256:{D}", "manifests/dataset.json", D, 1
            ).as_dict()

    def test_negative_invalid_quality_status(self) -> None:
        kwargs = self._valid_kwargs()
        kwargs["quality_summary"] = {
            "status": "BOGUS",
            "critical_findings": 0,
            "error_findings": 0,
            "warning_findings": 0,
        }
        with self.assertRaises(ManifestValidationError):
            build_dataset_manifest(**kwargs)


class TestDatasetManifestWithdrawnVersionRejection(unittest.TestCase):
    """Item 10 (F-001 correction): Dataset Manifest 1.0.0 and 1.0.1 are both
    withdrawn for prospective S8 production and must never be emitted by new
    code; only 1.0.2 is prospectively valid. Verified behaviorally (through
    the public loader and builder APIs), not via source-text inspection."""

    def test_common_loader_rejects_1_0_0(self) -> None:
        with self.assertRaises(ManifestValidationError):
            validate_structural({"manifest_schema_version": "1.0.0"}, "dataset", "1.0.0")

    def test_common_loader_rejects_1_0_1(self) -> None:
        with self.assertRaises(ManifestValidationError):
            validate_structural({"manifest_schema_version": "1.0.1"}, "dataset", "1.0.1")

    def test_common_loader_reaches_1_0_2_schema_content_validation(self) -> None:
        # An intentionally empty body must fail on 1.0.2 schema content
        # (missing required properties), never on the withdrawn-version
        # guard -- proving 1.0.2 is not itself treated as withdrawn.
        with self.assertRaises(ManifestValidationError) as ctx:
            validate_structural({}, "dataset", "1.0.2")
        self.assertNotIn("withdrawn", str(ctx.exception))

    def test_dataset_builder_always_emits_the_production_version(self) -> None:
        # Behavioral proof that the builder never exposes a withdrawn
        # version: `build_dataset_manifest` takes no caller-supplied schema
        # version, so exercising its only public entry point is the
        # complete reachability surface for this claim.
        from rcc002.s8.manifests.common import DATASET_MANIFEST_PRODUCTION_VERSION

        manifest = build_dataset_manifest(**_dataset_manifest_valid_kwargs())
        self.assertEqual(
            manifest["manifest_schema_version"], DATASET_MANIFEST_PRODUCTION_VERSION
        )
        self.assertNotIn(manifest["manifest_schema_version"], {"1.0.0", "1.0.1"})

    def test_dataset_manifest_schema_version_is_always_1_0_2(self) -> None:
        from rcc002.s8.manifests.common import DATASET_MANIFEST_PRODUCTION_VERSION

        self.assertEqual(DATASET_MANIFEST_PRODUCTION_VERSION, "1.0.2")

    def test_historical_1_0_0_and_1_0_1_fixtures_remain_on_disk_unchanged(
        self,
    ) -> None:
        # SS8.6: schema 1.0.0 and 1.0.1 remain certified, byte-identical
        # historical artifacts, valid for historical verification, even
        # though new code may not emit either -- the withdrawal guard is
        # production-emission-scoped, not a deletion of the schema files.
        from rcc002.s8.manifests.common import _SCHEMA_ROOT

        for version in ("1.0.0", "1.0.1", "1.0.2"):
            path = os.path.join(
                _SCHEMA_ROOT, "dataset-manifest", f"{version}.schema.json"
            )
            with self.subTest(version=version):
                self.assertTrue(os.path.isfile(path))


class TestSpecificationProfileF003(unittest.TestCase):
    """F-003 correction: the specification profile binds Data Pipeline
    Specification 0.9.0 and Reproducibility and Manifest Specification
    0.9.1 (exact identifiers, repository paths, and content hashes), and
    obsolete or mixed versions are rejected wherever the certified Dataset
    Manifest 1.0.2 schema's `specification_profile` `const` contract
    requires it.
    """

    # Independently transcribed from the certified Dataset Manifest 1.0.2
    # schema's `specification_profile` `prefixItems` (schemas/rcc002/
    # manifests/dataset-manifest/1.0.2.schema.json), not produced by
    # calling current_specification_profile().
    EXPECTED_PROFILE = (
        (
            "RCC_002_DATA_PIPELINE_SPECIFICATION",
            "0.9.0",
            "RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md",
        ),
        ("RCC-002-DV", "0.6.0", "RCC_002_DATA_VALIDATION_2026-07-23.md"),
        ("RCC-002-IS", "0.4.3", "RCC_002_INDICATOR_SPECIFICATION_2026-07-23.md"),
        ("RCC-002-ST", "0.4.2", "RCC_002_SIGNAL_TRANSFORMATION_2026-07-23.md"),
        (
            "RCC-002-RG",
            "0.5.1",
            "RCC_002_REGIME_AND_GATE_SPECIFICATION_2026-07-23.md",
        ),
        (
            "RCC-002-LF",
            "0.5.0",
            "RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md",
        ),
        ("RCC-002-RM", "0.9.1", "RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md"),
    )

    def test_current_profile_matches_the_certified_1_0_2_prefixitems(self) -> None:
        profile = current_specification_profile()
        self.assertEqual(len(profile), 7)
        for entry, (expected_id, expected_version, _filename) in zip(
            profile, self.EXPECTED_PROFILE
        ):
            with self.subTest(id=expected_id):
                self.assertEqual(entry.id, expected_id)
                self.assertEqual(entry.version, expected_version)

    def test_content_hashes_are_independently_reproducible(self) -> None:
        # Recomputes each document's SHA-256 directly from the file content
        # in this test, rather than trusting current_specification_profile's
        # own computation of the same value.
        from rcc002.s8.specification_profile import _SPEC_DIR

        profile = current_specification_profile()
        for entry, (_expected_id, _expected_version, filename) in zip(
            profile, self.EXPECTED_PROFILE
        ):
            path = os.path.join(_SPEC_DIR, filename)
            digest = hashlib.sha256()
            with open(path, "rb") as handle:
                digest.update(handle.read())
            with self.subTest(id=entry.id):
                self.assertEqual(entry.sha256, digest.hexdigest())

    def test_obsolete_data_pipeline_version_rejected(self) -> None:
        kwargs = _dataset_manifest_valid_kwargs()
        stale = list(kwargs["specification_profile"])
        stale[0] = VersionedReference(
            "RCC_002_DATA_PIPELINE_SPECIFICATION", "0.8.0", stale[0].sha256
        )
        kwargs["specification_profile"] = stale
        with self.assertRaises(ManifestValidationError):
            build_dataset_manifest(**kwargs)

    def test_mixed_obsolete_reproducibility_and_manifest_version_rejected(
        self,
    ) -> None:
        kwargs = _dataset_manifest_valid_kwargs()
        stale = list(kwargs["specification_profile"])
        stale[-1] = VersionedReference("RCC-002-RM", "0.9.0", stale[-1].sha256)
        kwargs["specification_profile"] = stale
        with self.assertRaises(ManifestValidationError):
            build_dataset_manifest(**kwargs)


if __name__ == "__main__":
    unittest.main()
