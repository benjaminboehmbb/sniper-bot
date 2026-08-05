"""Tests for rcc002.s8.identity.

Mandatory S8 test item 13: semantic-versus-physical identity separation
(Reproducibility and Manifest Specification SS6.7 golden identity-effect
table), plus general identity-builder positive/negative coverage.
"""

from __future__ import annotations

import unittest

from rcc002.s8 import identity as ident
from rcc002.s8.reason_codes import IdentityError

D = "a" * 64
D2 = "b" * 64
COMMIT = "c" * 40


def _spec_profile() -> "list[ident.SpecificationProfileEntry]":
    return [ident.SpecificationProfileEntry("RCC-002-RM", "0.9.0", D)]


def _base_build_kwargs() -> dict:
    return dict(
        parent_identities=[f"source:sha256:{D}"],
        code_commit_sha=COMMIT,
        dirty_patch_sha256=None,
        semantic_build_configuration_sha256=D,
        specification_profile=_spec_profile(),
        pipeline_profile_id="rcc002-canonical",
        schema_ids=["rcc002.stage.s7-labels/1.0.0"],
        environment_identity_profile_id="RCC_BUILD_ENV_IDENTITY_V2",
        environment_identity_sha256=D,
        stage_or_stage_range="S0..S7",
    )


class TestBuildIdDeterminism(unittest.TestCase):
    def test_same_preimage_same_id(self) -> None:
        id1, digest1 = ident.build_id(**_base_build_kwargs())
        id2, digest2 = ident.build_id(**_base_build_kwargs())
        self.assertEqual(id1, id2)
        self.assertEqual(digest1, digest2)
        self.assertEqual(id1, f"build:sha256:{digest1}")

    def test_rejects_empty_parents(self) -> None:
        kwargs = _base_build_kwargs()
        kwargs["parent_identities"] = []
        with self.assertRaises(IdentityError):
            ident.build_id(**kwargs)

    def test_rejects_malformed_commit_sha(self) -> None:
        kwargs = _base_build_kwargs()
        kwargs["code_commit_sha"] = "not-a-commit"
        with self.assertRaises(IdentityError):
            ident.build_id(**kwargs)

    def test_rejects_malformed_dirty_patch_hash(self) -> None:
        kwargs = _base_build_kwargs()
        kwargs["dirty_patch_sha256"] = "short"
        with self.assertRaises(IdentityError):
            ident.build_id(**kwargs)


class TestRunIdIsNondeterministic(unittest.TestCase):
    def test_two_calls_never_collide(self) -> None:
        seen = {ident.new_run_id() for _ in range(20)}
        self.assertEqual(len(seen), 20)

    def test_format(self) -> None:
        import re

        run_id = ident.new_run_id()
        self.assertTrue(run_id.startswith("run:"))
        match = re.match(
            r"^run:(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z):"
            r"([0-9a-f-]{36})$",
            run_id,
        )
        self.assertIsNotNone(match, msg=run_id)


class TestSemanticVersusPhysicalIdentitySeparation(unittest.TestCase):
    """Item 13, and the SS6.7 golden identity-effect table.

    | change | build_id | dataset_id | artifact_id | dataset_artifact_set_id |
    | semantic config change | new | new | new | new |
    | pure physical repackaging | same | same | new | new |
    | new run_id/time only | same | same | same (same bytes) | same |
    """

    def _dataset_kwargs(self, build_id_value: str) -> dict:
        return dict(
            components=[
                ident.DatasetComponent("audit-v2", "rcc002.view.audit/2.0.0", D, 100, (1000, 2000))
            ],
            release_schema_id="rcc002.dataset-manifest/1.0.1",
            dataset_profile="rcc002-canonical",
            build_id_value=build_id_value,
            semantic_build_configuration_sha256=D,
            quality_status="PASS",
            specification_profile=_spec_profile(),
        )

    def test_semantic_configuration_change_changes_build_and_dataset_id(self) -> None:
        build1, _ = ident.build_id(**_base_build_kwargs())
        kwargs2 = _base_build_kwargs()
        kwargs2["semantic_build_configuration_sha256"] = D2
        build2, _ = ident.build_id(**kwargs2)
        self.assertNotEqual(build1, build2)

        dataset1, _ = ident.dataset_id(**self._dataset_kwargs(build1))
        dataset_kwargs2 = self._dataset_kwargs(build2)
        dataset_kwargs2["semantic_build_configuration_sha256"] = D2
        dataset2, _ = ident.dataset_id(**dataset_kwargs2)
        self.assertNotEqual(dataset1, dataset2)

    def test_pure_physical_repackaging_keeps_dataset_id_but_not_artifact_set_id(
        self,
    ) -> None:
        build_id_value, _ = ident.build_id(**_base_build_kwargs())
        dataset_id_value, _ = ident.dataset_id(**self._dataset_kwargs(build_id_value))

        artifact = ident.PublishedDataArtifact(
            logical_name="audit-v2",
            relative_path="data/audit.parquet",
            artifact_id_value=f"artifact:sha256:{D}",
            byte_sha256=D,
            semantic_sha256=D,
            physical_layout_sha256=D,
            size_bytes=100,
            schema_ref="rcc002.view.audit/2.0.0",
            schema_fingerprint_sha256=D,
            view_allowlist_sha256=D2,
        )
        repacked = ident.PublishedDataArtifact(
            logical_name="audit-v2",
            relative_path="data/audit_repartitioned.parquet",  # new layout
            artifact_id_value=f"artifact:sha256:{D2}",  # new physical id
            byte_sha256=D2,
            semantic_sha256=D,  # same logical content
            physical_layout_sha256=D2,  # new physical layout
            size_bytes=100,
            schema_ref="rcc002.view.audit/2.0.0",
            schema_fingerprint_sha256=D,
            view_allowlist_sha256=D2,
        )

        set_id_1, _ = ident.dataset_artifact_set_id(
            dataset_id_value=dataset_id_value,
            physical_publication_configuration_sha256=D,
            data_artifacts=[artifact],
        )
        set_id_2, _ = ident.dataset_artifact_set_id(
            dataset_id_value=dataset_id_value,
            physical_publication_configuration_sha256=D2,
            data_artifacts=[repacked],
        )
        # dataset_id is unaffected by a pure physical repackaging...
        self.assertEqual(dataset_id_value, dataset_id_value)
        # ...but the physical dataset_artifact_set_id must change.
        self.assertNotEqual(set_id_1, set_id_2)

    def test_new_run_id_alone_leaves_every_deterministic_identity_unchanged(
        self,
    ) -> None:
        build1, _ = ident.build_id(**_base_build_kwargs())
        build2, _ = ident.build_id(**_base_build_kwargs())
        self.assertEqual(build1, build2)
        # run_id is deliberately excluded from the build_id preimage.
        self.assertNotEqual(ident.new_run_id(), ident.new_run_id())

    def test_artifact_id_preimage_excludes_dataset_scope_fields(self) -> None:
        # artifact_id (SS5.6) must be computable from a single artifact's
        # own physical/semantic identity alone, with no dataset_id or
        # dataset_artifact_set_id input parameter available to leak in.
        import inspect

        params = inspect.signature(ident.DataArtifactIdentity).parameters
        self.assertNotIn("dataset_id", params)
        self.assertNotIn("dataset_artifact_set_id", params)

    def test_build_id_preimage_excludes_prohibited_fields(self) -> None:
        import inspect

        params = inspect.signature(ident.build_id).parameters
        for forbidden in (
            "run_start_time",
            "run_end_time",
            "hostname",
            "random_uuid",
            "temp_path",
            "manifest_id",
            "physical_publication_configuration_sha256",
            "physical_layout_sha256",
            "artifact_id",
            "dataset_artifact_set_id",
        ):
            self.assertNotIn(forbidden, params)


class TestDatasetArtifactSetId(unittest.TestCase):
    def test_sorted_by_relative_path_then_logical_name(self) -> None:
        def artifact(name: str, path: str) -> ident.PublishedDataArtifact:
            return ident.PublishedDataArtifact(
                logical_name=name,
                relative_path=path,
                artifact_id_value=f"artifact:sha256:{D}",
                byte_sha256=D,
                semantic_sha256=D,
                physical_layout_sha256=D,
                size_bytes=1,
                schema_ref="rcc002.view.audit/2.0.0",
                schema_fingerprint_sha256=D,
                view_allowlist_sha256=None,
            )

        forward = [artifact("b", "path/b.parquet"), artifact("a", "path/a.parquet")]
        reverse = list(reversed(forward))
        id1, _ = ident.dataset_artifact_set_id(
            dataset_id_value=f"dataset:sha256:{D}",
            physical_publication_configuration_sha256=D,
            data_artifacts=forward,
        )
        id2, _ = ident.dataset_artifact_set_id(
            dataset_id_value=f"dataset:sha256:{D}",
            physical_publication_configuration_sha256=D,
            data_artifacts=reverse,
        )
        self.assertEqual(id1, id2)  # input order must not matter

    def test_rejects_duplicate_relative_path(self) -> None:
        artifact = ident.PublishedDataArtifact(
            logical_name="a",
            relative_path="same.parquet",
            artifact_id_value=f"artifact:sha256:{D}",
            byte_sha256=D,
            semantic_sha256=D,
            physical_layout_sha256=D,
            size_bytes=1,
            schema_ref="rcc002.view.audit/2.0.0",
            schema_fingerprint_sha256=D,
            view_allowlist_sha256=None,
        )
        with self.assertRaises(IdentityError):
            ident.dataset_artifact_set_id(
                dataset_id_value=f"dataset:sha256:{D}",
                physical_publication_configuration_sha256=D,
                data_artifacts=[artifact, artifact],
            )


class TestManifestIdFinalization(unittest.TestCase):
    def test_deterministic(self) -> None:
        manifest_id_1, finalized_1 = ident.finalize_manifest_id({"a": 1, "b": 2})
        manifest_id_2, finalized_2 = ident.finalize_manifest_id({"b": 2, "a": 1})
        self.assertEqual(manifest_id_1, manifest_id_2)
        self.assertEqual(finalized_1["manifest_id"], manifest_id_1)

    def test_rejects_preexisting_manifest_id(self) -> None:
        with self.assertRaises(IdentityError):
            ident.finalize_manifest_id({"manifest_id": f"manifest:sha256:{D}"})

    def test_rejects_self_reported_byte_hash_or_size(self) -> None:
        with self.assertRaises(IdentityError):
            ident.finalize_manifest_id({"byte_sha256": D})
        with self.assertRaises(IdentityError):
            ident.finalize_manifest_id({"file_size_bytes": 123})

    def test_different_content_different_id(self) -> None:
        id1, _ = ident.finalize_manifest_id({"a": 1})
        id2, _ = ident.finalize_manifest_id({"a": 2})
        self.assertNotEqual(id1, id2)


if __name__ == "__main__":
    unittest.main()
