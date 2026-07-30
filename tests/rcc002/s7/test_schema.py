"""Exact S7 field expansion, type registry, and leakage tests."""

from __future__ import annotations

import dataclasses
import unittest

from rcc002.s7.compute import compute_labels
from rcc002.s7.constants import (
    HORIZONS,
    HORIZON_LOCAL_FIELDS,
    LABEL_EXTENSION_FIELDS,
    LABEL_METADATA_FIELDS,
    LABEL_SCHEMA_FINGERPRINT_SHA256,
    S7_FIELD_REGISTRY,
    SEMANTIC_BUILD_CONFIGURATION_SHA256,
    BarrierOutcome,
)
from rcc002.s7.leakage import assert_no_s7_fields
from rcc002.s7.schema import flatten_s7_extension
from tests.rcc002.s7._helpers import make_s6_rows


class TestSchemaRegistry(unittest.TestCase):
    def test_exact_field_count_and_order(self) -> None:
        self.assertEqual(len(LABEL_METADATA_FIELDS), 14)
        self.assertEqual(len(HORIZON_LOCAL_FIELDS), 48)
        self.assertEqual(len(LABEL_EXTENSION_FIELDS), 302)
        self.assertEqual(tuple(S7_FIELD_REGISTRY), LABEL_EXTENSION_FIELDS)
        self.assertEqual(
            LABEL_EXTENSION_FIELDS[:14], LABEL_METADATA_FIELDS
        )
        self.assertEqual(
            LABEL_EXTENSION_FIELDS[14],
            "label_horizon_bars_h001",
        )
        self.assertEqual(
            LABEL_EXTENSION_FIELDS[-1],
            "barrier_short_first_hit_time_tp050_sl020_h1440",
        )

    def test_registry_metadata_is_fail_closed(self) -> None:
        for definition in S7_FIELD_REGISTRY.values():
            self.assertEqual(definition.field_owner_stage, "S7_LABELS")
            self.assertEqual(definition.leakage_class, "FUTURE_OUTCOME")
            self.assertFalse(definition.live_allowed)
            self.assertFalse(definition.paper_allowed)
            self.assertFalse(definition.backtest_input_allowed)
            self.assertFalse(definition.research_feature_allowed)
            self.assertTrue(definition.label_research_allowed)

    def test_fingerprints_are_sha256(self) -> None:
        for value in (
            LABEL_SCHEMA_FINGERPRINT_SHA256,
            SEMANTIC_BUILD_CONFIGURATION_SHA256,
        ):
            self.assertEqual(len(value), 64)
            int(value, 16)

    def test_flattened_output_has_exact_expansion(self) -> None:
        row = compute_labels(
            make_s6_rows((100.0, 101.0)),
            output_row_count=1,
        ).rows[0]
        flattened = flatten_s7_extension(row)
        self.assertEqual(tuple(flattened), LABEL_EXTENSION_FIELDS)
        self.assertEqual(len(row.horizons), len(HORIZONS))

    def test_timeout_requires_null_hit_bar_and_time(self) -> None:
        labels = compute_labels(
            make_s6_rows((100.0, 100.0)),
            output_row_count=1,
        ).rows[0].horizons["H001"]
        self.assertIs(
            labels.barrier_long_outcome_tp050_sl020,
            BarrierOutcome.TIMEOUT,
        )
        with self.assertRaises(ValueError):
            dataclasses.replace(
                labels,
                barrier_long_first_hit_bar_tp050_sl020=1,
                barrier_long_first_hit_time_tp050_sl020=123,
            )

    def test_hit_requires_non_null_hit_bar_and_time(self) -> None:
        labels = compute_labels(
            make_s6_rows(
                (100.0, 105.0),
                opens=(100.0, 100.0),
                highs=(100.0, 105.0),
                lows=(100.0, 99.0),
            ),
            output_row_count=1,
        ).rows[0].horizons["H001"]
        self.assertIs(
            labels.barrier_long_outcome_tp050_sl020,
            BarrierOutcome.TP_FIRST,
        )
        with self.assertRaises(ValueError):
            dataclasses.replace(
                labels,
                barrier_long_first_hit_bar_tp050_sl020=None,
                barrier_long_first_hit_time_tp050_sl020=None,
            )


class TestLeakageGuard(unittest.TestCase):
    def test_every_registered_s7_field_is_rejected(self) -> None:
        for field_name in S7_FIELD_REGISTRY:
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValueError):
                    assert_no_s7_fields(
                        (field_name,),
                        field_owners={field_name: "S7_LABELS"},
                        positive_allowlist=frozenset({field_name}),
                    )

    def test_prefix_and_ownerless_fields_are_rejected(self) -> None:
        cases = (
            ("fwd_unregistered", "S6_GATES"),
            ("label_unregistered", "S6_GATES"),
            ("barrier_unregistered", "S6_GATES"),
        )
        for field_name, owner in cases:
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValueError):
                    assert_no_s7_fields(
                        (field_name,),
                        field_owners={field_name: owner},
                        positive_allowlist=frozenset({field_name}),
                    )
        with self.assertRaises(ValueError):
            assert_no_s7_fields(
                ("close",),
                field_owners={},
                positive_allowlist=frozenset({"close"}),
            )

    def test_known_upstream_allowlisted_field_passes(self) -> None:
        assert_no_s7_fields(
            ("close",),
            field_owners={"close": "S1_NORMALIZED"},
            positive_allowlist=frozenset({"close"}),
        )


if __name__ == "__main__":
    unittest.main()
