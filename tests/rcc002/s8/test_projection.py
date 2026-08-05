"""Tests for rcc002.s8.projection.

Mandatory S8 test items 3 (rejection of every S7 field from non-label
views) and 4 (fwd_/label_/barrier_ prefix rejection), exercised against
the live rejection code path (not only structurally, as in
test_views.py).
"""

from __future__ import annotations

import unittest
from unittest import mock

from rcc002.constants import ViewId
from rcc002.s7.compute import compute_labels
from rcc002.s8 import field_registry, projection
from rcc002.s8.reason_codes import FieldRegistryError, ViewProjectionError
from rcc002.s8.views import VIEW_DEFINITIONS
from tests.rcc002.s7._helpers import make_s6_rows


def _s7_rows(count: int = 5):
    s6_rows = make_s6_rows(tuple(100.0 + i for i in range(count)))
    return compute_labels(s6_rows, output_row_count=count).rows


class TestFlattenRow(unittest.TestCase):
    def test_flatten_includes_every_view_registered_field(self) -> None:
        row = _s7_rows(1)[0]
        flat = projection.flatten_row(row)
        for field in field_registry.FIELD_OWNER_STAGE:
            if field_registry.FIELD_LEAKAGE_CLASS[field] in (
                "POINT_IN_TIME",
                "FUTURE_OUTCOME",
            ):
                with self.subTest(field=field):
                    self.assertIn(field, flat)

    def test_flatten_rejects_non_s7row(self) -> None:
        with self.assertRaises(ViewProjectionError):
            projection.flatten_row({"not": "a row"})  # type: ignore[arg-type]


class TestProjectViewPositive(unittest.TestCase):
    def test_each_view_projects_exact_certified_field_count(self) -> None:
        row = _s7_rows(1)[0]
        for view_id, definition in VIEW_DEFINITIONS.items():
            with self.subTest(view=view_id.value):
                projected = projection.project_view(view_id, row)
                self.assertEqual(tuple(projected), definition.fields)

    def test_project_rows_preserves_order_and_count(self) -> None:
        rows = _s7_rows(4)
        projected = projection.project_rows(ViewId.PAPER, rows)
        self.assertEqual(len(projected), 4)
        expected_keys = [
            (r.provider, r.market_type, r.symbol, r.interval, r.open_time)
            for r in rows
        ]
        actual_keys = [
            (p["provider"], p["market_type"], p["symbol"], p["interval"], p["open_time"])
            for p in projected
        ]
        self.assertEqual(actual_keys, expected_keys)

    def test_flattened_reuse_matches_fresh_flatten(self) -> None:
        row = _s7_rows(1)[0]
        flat = projection.flatten_row(row)
        with_reuse = projection.project_view(ViewId.AUDIT, row, flattened=flat)
        without_reuse = projection.project_view(ViewId.AUDIT, row)
        self.assertEqual(with_reuse, without_reuse)


class TestNonLabelViewsRejectS7Fields(unittest.TestCase):
    """Item 3, behavioural: inject each registered S7 field and require
    rejection, for every one of the four non-label views."""

    NON_LABEL_VIEWS = (
        ViewId.RESEARCH_FEATURES,
        ViewId.BACKTEST_INPUTS,
        ViewId.PAPER,
        ViewId.LIVE,
    )

    def test_every_s7_field_individually_rejected_from_every_non_label_view(
        self,
    ) -> None:
        s7_fields = [
            field
            for field, stage in field_registry.FIELD_OWNER_STAGE.items()
            if stage == "S7_LABELS"
        ]
        self.assertEqual(len(s7_fields), 302)
        for view_id in self.NON_LABEL_VIEWS:
            for field in s7_fields:
                with self.subTest(view=view_id.value, field=field):
                    with self.assertRaises(ViewProjectionError):
                        projection._reject_field_for_view(view_id, field)

    def test_label_views_accept_s7_fields(self) -> None:
        for view_id in (ViewId.LABEL_RESEARCH, ViewId.AUDIT):
            for field in ("fwd_cc_valid_h001", "label_profile_id"):
                with self.subTest(view=view_id.value, field=field):
                    projection._reject_field_for_view(view_id, field)  # no raise


class TestPrefixRejection(unittest.TestCase):
    """Item 4: fwd_/label_/barrier_ prefix rejection, including a case
    where only the prefix check (not the stage check) would fire, proving
    the two gates are genuinely independent."""

    def test_real_registered_field_rejected_by_both_gates(self) -> None:
        # A real, certified S7 field: rejected by stage AND prefix.
        with self.assertRaises(ViewProjectionError):
            projection._reject_field_for_view(
                ViewId.RESEARCH_FEATURES, "barrier_valid_h001"
            )

    def test_prefix_gate_fires_independently_of_stage_gate(self) -> None:
        # Simulate a mis-registered field: prefixed like a label field but
        # (hypothetically) misclassified under a non-S7 owner stage. The
        # prefix check must still reject it -- proving it is not a no-op
        # that merely restates the stage check.
        with mock.patch.dict(
            field_registry.FIELD_OWNER_STAGE, {"fwd_mis_registered": "S3_INDICATORS"}
        ), mock.patch.dict(
            field_registry.FIELD_LEAKAGE_CLASS,
            {"fwd_mis_registered": "POINT_IN_TIME"},
        ):
            # The stage-based gate alone would accept this (S3 is allowed
            # in non-label views); confirm that, then confirm the prefix
            # gate still rejects it end to end.
            self.assertFalse(
                projection.view_forbids_field_owner_stage(
                    ViewId.RESEARCH_FEATURES, "S3_INDICATORS"
                )
            )
            with self.assertRaises(ViewProjectionError):
                projection._reject_field_for_view(
                    ViewId.RESEARCH_FEATURES, "fwd_mis_registered"
                )

    def test_unregistered_field_fails_closed_before_prefix_check(self) -> None:
        with self.assertRaises(FieldRegistryError):
            projection._reject_field_for_view(
                ViewId.RESEARCH_FEATURES, "totally_unregistered_field"
            )


if __name__ == "__main__":
    unittest.main()
