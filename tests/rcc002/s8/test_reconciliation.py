"""Tests for rcc002.s8.reconciliation.

Mandatory S8 test items 5 (S8_rows == S7_rows and exact row identity/order
preservation) and 6 (missing, duplicate, merged, reordered, and modified
row detection). Also covers the RCC-002-S8-TRACK2-IAD-001 F-004 correction:
schema-derived (not hardcoded provider-first) primary-key behavior.
"""

from __future__ import annotations

import dataclasses
import unittest

from rcc002.constants import ViewId
from rcc002.s7.compute import compute_labels
from rcc002.s8.projection import project_view
from rcc002.s8.reason_codes import RowReconciliationError
from rcc002.s8.reconciliation import (
    CONSOLIDATED_PRIMARY_KEY_FIELDS,
    PRIMARY_KEY_FIELDS,
    PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS,
    primary_key_fields_for_view,
    reconcile_row_identity,
    reconcile_view_artifact,
    resolve_primary_key_fields,
    row_identity_key,
)
from rcc002.s8.views import VIEW_DEFINITIONS
from tests.rcc002.s7._helpers import make_s6_rows


def _s7_rows(count: int = 5):
    s6_rows = make_s6_rows(tuple(100.0 + i for i in range(count)))
    return compute_labels(s6_rows, output_row_count=count).rows


class TestRowIdentityKey(unittest.TestCase):
    def test_key_shape_consolidated_default(self) -> None:
        row = _s7_rows(1)[0]
        key = row_identity_key(row)
        self.assertEqual(
            key,
            (row.market_type, row.symbol, row.interval, row.open_time),
        )

    def test_key_shape_provider_specific(self) -> None:
        row = _s7_rows(1)[0]
        key = row_identity_key(
            row, primary_key_fields=PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS
        )
        self.assertEqual(
            key,
            (row.provider, row.market_type, row.symbol, row.interval, row.open_time),
        )


class TestResolvePrimaryKeyFields(unittest.TestCase):
    """F-004: schema-derived primary-key resolution, not a hardcoded
    provider-first assumption."""

    def test_consolidated_schema_accepted_unchanged(self) -> None:
        self.assertEqual(
            resolve_primary_key_fields(
                ("market_type", "symbol", "interval", "open_time")
            ),
            CONSOLIDATED_PRIMARY_KEY_FIELDS,
        )

    def test_provider_specific_schema_accepted_unchanged(self) -> None:
        self.assertEqual(
            resolve_primary_key_fields(
                ("provider", "market_type", "symbol", "interval", "open_time")
            ),
            PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS,
        )

    def test_default_is_consolidated(self) -> None:
        self.assertEqual(PRIMARY_KEY_FIELDS, CONSOLIDATED_PRIMARY_KEY_FIELDS)

    def test_negative_empty_definition_rejected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            resolve_primary_key_fields(())

    def test_negative_duplicate_field_rejected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            resolve_primary_key_fields(
                ("market_type", "market_type", "symbol", "interval", "open_time")
            )

    def test_negative_unknown_field_rejected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            resolve_primary_key_fields(
                ("market_type", "symbol", "interval", "open_time", "close")
            )

    def test_negative_missing_required_field_rejected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            resolve_primary_key_fields(("market_type", "symbol", "interval"))

    def test_negative_consolidated_fields_out_of_order_rejected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            resolve_primary_key_fields(
                ("symbol", "market_type", "interval", "open_time")
            )

    def test_negative_provider_not_leading_rejected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            resolve_primary_key_fields(
                ("market_type", "provider", "symbol", "interval", "open_time")
            )

    def test_negative_provider_specific_fields_out_of_order_rejected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            resolve_primary_key_fields(
                ("provider", "symbol", "market_type", "interval", "open_time")
            )


class TestPrimaryKeyFieldsForView(unittest.TestCase):
    def test_every_registered_view_resolves_to_the_consolidated_key(self) -> None:
        for view_id in ViewId:
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    primary_key_fields_for_view(view_id),
                    CONSOLIDATED_PRIMARY_KEY_FIELDS,
                )

    def test_matches_the_view_definitions_declared_primary_key(self) -> None:
        for view_id in ViewId:
            with self.subTest(view=view_id.value):
                self.assertEqual(
                    primary_key_fields_for_view(view_id),
                    resolve_primary_key_fields(
                        VIEW_DEFINITIONS[view_id].primary_key_fields
                    ),
                )


class TestItem5ExactPreservation(unittest.TestCase):
    def test_identical_rows_pass(self) -> None:
        rows = _s7_rows(5)
        reconcile_row_identity(rows, rows)

    def test_row_count_mismatch_rejected(self) -> None:
        rows = _s7_rows(5)
        with self.assertRaises(RowReconciliationError):
            reconcile_row_identity(rows, rows[:-1])

    def test_view_artifact_matches_fresh_reprojection(self) -> None:
        rows = _s7_rows(5)
        for view_id in ViewId:
            with self.subTest(view=view_id.value):
                artifact = [project_view(view_id, row) for row in rows]
                reconcile_view_artifact(view_id, rows, artifact)


class TestItem6MutationDetection(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = _s7_rows(5)
        self.artifact = [
            project_view(ViewId.RESEARCH_FEATURES, row) for row in self.rows
        ]

    def test_missing_row_detected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            reconcile_row_identity(self.rows, self.rows[1:])
        with self.assertRaises(RowReconciliationError):
            reconcile_view_artifact(
                ViewId.RESEARCH_FEATURES, self.rows, self.artifact[1:]
            )

    def test_duplicate_row_detected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            reconcile_row_identity(self.rows, list(self.rows) + [self.rows[0]])
        with self.assertRaises(RowReconciliationError):
            reconcile_view_artifact(
                ViewId.RESEARCH_FEATURES,
                self.rows,
                self.artifact + [self.artifact[0]],
            )

    def test_merged_row_detected_as_row_count_shortfall(self) -> None:
        # A "merge" of two S7 rows into one S8 row always manifests as a
        # row-count shortfall against S7_rows plus a missing canonical
        # key -- exactly what reconciliation must catch.
        merged_artifact = self.artifact[:-2] + [self.artifact[-1]]
        with self.assertRaises(RowReconciliationError):
            reconcile_view_artifact(
                ViewId.RESEARCH_FEATURES, self.rows, merged_artifact
            )

    def test_reordered_rows_detected(self) -> None:
        with self.assertRaises(RowReconciliationError):
            reconcile_row_identity(self.rows, list(reversed(self.rows)))
        with self.assertRaises(RowReconciliationError):
            reconcile_view_artifact(
                ViewId.RESEARCH_FEATURES, self.rows, list(reversed(self.artifact))
            )

    def test_modified_row_value_detected(self) -> None:
        tampered = [dict(row) for row in self.artifact]
        tampered[2] = dict(tampered[2])
        tampered[2]["close"] = tampered[2]["close"] + 1000.0
        with self.assertRaises(RowReconciliationError):
            reconcile_view_artifact(ViewId.RESEARCH_FEATURES, self.rows, tampered)

    def test_modified_row_object_detected_via_row_identity(self) -> None:
        tampered_rows = list(self.rows)
        tampered_rows[0] = dataclasses.replace(tampered_rows[0], close=999999.0)
        # Row identity (primary key only) is unaffected by a non-key value
        # change -- this is expected and correct; full value preservation
        # is proven via reconcile_view_artifact, not reconcile_row_identity.
        reconcile_row_identity(self.rows, tampered_rows)
        tampered_artifact = [
            project_view(ViewId.RESEARCH_FEATURES, row) for row in tampered_rows
        ]
        with self.assertRaises(RowReconciliationError):
            reconcile_view_artifact(
                ViewId.RESEARCH_FEATURES, self.rows, tampered_artifact
            )

    def test_duplicate_primary_key_in_s7_input_itself_fails_closed(self) -> None:
        rows_with_duplicate_key = list(self.rows) + [
            dataclasses.replace(self.rows[0], close=self.rows[0].close + 1.0)
        ]
        with self.assertRaises(RowReconciliationError):
            reconcile_row_identity(rows_with_duplicate_key, rows_with_duplicate_key)

    def test_non_dict_artifact_row_rejected(self) -> None:
        broken = list(self.artifact)
        broken[0] = ["not", "a", "dict"]  # type: ignore[list-item]
        with self.assertRaises(RowReconciliationError):
            reconcile_view_artifact(ViewId.RESEARCH_FEATURES, self.rows, broken)


class TestProviderSpecificReconciliation(unittest.TestCase):
    """F-004: provider-specific (not-yet-consolidated) datasets are
    supported by explicitly passing the provider-specific schema key,
    distinct from the consolidated default used by
    :func:`reconcile_view_artifact`."""

    def test_rows_distinguished_only_by_provider_pass_under_provider_specific_key(
        self,
    ) -> None:
        rows = _s7_rows(2)
        other_provider_row = dataclasses.replace(rows[1], provider="other-provider")
        provider_specific_rows = [rows[0], other_provider_row]
        reconcile_row_identity(
            provider_specific_rows,
            provider_specific_rows,
            primary_key_fields=PROVIDER_SPECIFIC_PRIMARY_KEY_FIELDS,
        )

    def test_rows_distinguished_only_by_provider_collide_under_consolidated_key(
        self,
    ) -> None:
        # Without `provider` in the key, two rows that otherwise share
        # (market_type, symbol, interval, open_time) collide -- proving the
        # consolidated key is genuinely enforced, not silently widened.
        rows = _s7_rows(1)
        other_provider_row = dataclasses.replace(rows[0], provider="other-provider")
        colliding_rows = [rows[0], other_provider_row]
        with self.assertRaises(RowReconciliationError):
            reconcile_row_identity(colliding_rows, colliding_rows)


if __name__ == "__main__":
    unittest.main()
