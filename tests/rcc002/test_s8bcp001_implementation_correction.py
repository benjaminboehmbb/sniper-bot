"""Cross-stage conformance tests for S8BCP-001 Revision 2 implementation."""

from __future__ import annotations

import dataclasses
import unittest

from rcc002.s3.constants import INDICATOR_SCHEMA_REF
from rcc002.s3.schema import S3Row
from rcc002.s1.schema import S1Row
from rcc002.s2.schema import S2Row
from rcc002.s4.schema import S4Row
from rcc002.s5.schema import S5Row
from rcc002.s6.schema import S6Row
from rcc002.s7.schema import S7Row
from rcc002.s4.compute import compute_signals
from rcc002.s4.constants import COMPONENT_VERSION as S4_COMPONENT_VERSION
from rcc002.s5.constants import COMPONENT_VERSION as S5_COMPONENT_VERSION
from rcc002.s6.constants import COMPONENT_VERSION as S6_COMPONENT_VERSION
from rcc002.s7.compute import compute_labels
from rcc002.s7.constants import (
    COMPONENT_VERSION as S7_COMPONENT_VERSION,
    LABEL_SCHEMA_FINGERPRINT_SHA256,
    SEMANTIC_BUILD_CONFIGURATION_SHA256,
)
from tests.rcc002.s4.test_compute import _make_row
from tests.rcc002.s6._helpers import valid_s5_row
from tests.rcc002.s7._helpers import make_s6_rows


class IndicatorSchemaRefConformanceTests(unittest.TestCase):
    def test_source_coordinates_propagate_through_s1_to_s7(self) -> None:
        for row_type in (
            S1Row,
            S2Row,
            S3Row,
            S4Row,
            S5Row,
            S6Row,
            S7Row,
        ):
            names = tuple(
                field.name for field in dataclasses.fields(row_type)
            )
            snapshot_index = names.index("source_snapshot_id")
            self.assertEqual(
                names[snapshot_index : snapshot_index + 4],
                (
                    "source_snapshot_id",
                    "source_row_id",
                    "source_file_ordinal",
                    "original_record_index",
                ),
            )

    def test_s3_field_order_matches_normative_contract(self) -> None:
        names = tuple(field.name for field in dataclasses.fields(S3Row))
        version_index = names.index("indicator_schema_version")
        self.assertEqual(
            names[version_index : version_index + 3],
            (
                "indicator_schema_version",
                "indicator_schema_ref",
                "indicator_segment_id",
            ),
        )

    def test_s3_to_s4_preserves_exact_ref(self) -> None:
        source = _make_row(0)
        output = compute_signals((source,)).rows[0]
        self.assertEqual(source.indicator_schema_ref, INDICATOR_SCHEMA_REF)
        self.assertEqual(output.indicator_schema_ref, INDICATOR_SCHEMA_REF)

    def test_s5_to_s7_preserves_exact_ref(self) -> None:
        s5 = valid_s5_row()
        s6_rows = make_s6_rows((100.0, 101.0))
        s7 = compute_labels(s6_rows, output_row_count=1).rows[0]
        self.assertEqual(s5.indicator_schema_ref, INDICATOR_SCHEMA_REF)
        for row in (*s6_rows, s7):
            self.assertEqual(
                row.indicator_schema_ref,
                INDICATOR_SCHEMA_REF,
            )


class PatchVersionAndFingerprintTests(unittest.TestCase):
    def test_downstream_component_patch_versions(self) -> None:
        self.assertEqual(
            (
                S4_COMPONENT_VERSION,
                S5_COMPONENT_VERSION,
                S6_COMPONENT_VERSION,
                S7_COMPONENT_VERSION,
            ),
            ("0.3.1", "0.4.1", "0.4.1", "0.3.1"),
        )

    def test_recomputed_s7_identities_are_exact(self) -> None:
        self.assertEqual(
            LABEL_SCHEMA_FINGERPRINT_SHA256,
            "6fb2bcdeae2070f054fcf298693382b668ed267017f4e0f72be87615a3827bce",
        )
        self.assertEqual(
            SEMANTIC_BUILD_CONFIGURATION_SHA256,
            "8ca946ee9725e6f767ff498c7d41362181f52457de7f5494a48a4b32b0806905",
        )


if __name__ == "__main__":
    unittest.main()
