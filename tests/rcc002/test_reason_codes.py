"""Unit tests for rcc002.reason_codes (central severity registry)."""

import unittest

from rcc002.reason_codes import (
    QUALITY_RULE_VERSION,
    REASON_CODE_PRIORITY_PROFILE_ID,
    REASON_CODE_SEVERITY,
    Severity,
    derive_quality_status,
    sort_reason_codes,
)

# The exact 32 codes registered in Data Validation §16.2 / §16.3.
ALL_32_CODES = {
    "DV_FILE_MISSING",
    "DV_FILE_EMPTY",
    "DV_FILE_CORRUPT",
    "DV_CHECKSUM_MISMATCH",
    "DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION",
    "DV_SCHEMA_REQUIRED_COLUMN_MISSING",
    "DV_SCHEMA_UNEXPECTED_COLUMN",
    "DV_PARSE_TIMESTAMP_FAILED",
    "DV_PARSE_NUMERIC_FAILED",
    "DV_TIME_NOT_UTC",
    "DV_TIME_MISALIGNED",
    "DV_TIME_OUT_OF_RANGE",
    "DV_DUPLICATE_IDENTICAL_COLLAPSED",
    "DV_DUPLICATE_CONFLICT",
    "DV_SOURCE_CONFLICT_RESOLVED",
    "DV_GAP_DETECTED",
    "DV_GAP_UNEXPLAINED",
    "DV_TIME_GAP_SEGMENT_STARTED",
    "DV_NUMERIC_NONFINITE",
    "DV_OHLC_INVARIANT_FAILED",
    "DV_VOLUME_NEGATIVE",
    "DV_VOLUME_ZERO_OBSERVED",
    "DV_ANOMALY_EXTREME_CANDLE_RETURN",
    "DV_ANOMALY_EXTREME_HIGH_LOW_RANGE",
    "DV_ANOMALY_EXTREME_VOLUME",
    "DV_ANOMALY_ZERO_VOLUME_CLUSTER",
    "DV_ANOMALY_REPEATED_IDENTICAL_OHLC",
    "DV_ANOMALY_PARTITION_BOUNDARY_JUMP",
    "DV_SYNTHETIC_ROW_NONCANONICAL",
    "DV_APPROVED_WARNING_ACTIVE",
    "DV_ROW_RECONCILIATION_FAILED",
    "DV_SCHEMA_FINGERPRINT_MISMATCH",
}


class RegistryCompletenessTests(unittest.TestCase):
    def test_exactly_32_codes_registered(self) -> None:
        self.assertEqual(len(REASON_CODE_SEVERITY), 32)

    def test_registered_set_matches_certified_16_2_list_exactly(self) -> None:
        self.assertEqual(set(REASON_CODE_SEVERITY), ALL_32_CODES)

    def test_every_code_has_a_severity_value(self) -> None:
        for code, severity in REASON_CODE_SEVERITY.items():
            self.assertIsInstance(severity, Severity, msg=code)


class SpotCheckExplicitSeveritiesTests(unittest.TestCase):
    """The 6 codes with a severity already explicit somewhere else in Data
    Validation before DVSEV-001 (§7.2, §10.2, §12.1, §12.2, §14.1, §6.3)."""

    def test_duplicate_conflict_is_critical(self) -> None:
        self.assertEqual(REASON_CODE_SEVERITY["DV_DUPLICATE_CONFLICT"], Severity.CRITICAL)

    def test_ohlc_invariant_failed_is_critical(self) -> None:
        self.assertEqual(REASON_CODE_SEVERITY["DV_OHLC_INVARIANT_FAILED"], Severity.CRITICAL)

    def test_volume_negative_is_critical(self) -> None:
        self.assertEqual(REASON_CODE_SEVERITY["DV_VOLUME_NEGATIVE"], Severity.CRITICAL)

    def test_parse_numeric_failed_is_critical(self) -> None:
        self.assertEqual(REASON_CODE_SEVERITY["DV_PARSE_NUMERIC_FAILED"], Severity.CRITICAL)

    def test_parse_timestamp_failed_is_critical(self) -> None:
        self.assertEqual(REASON_CODE_SEVERITY["DV_PARSE_TIMESTAMP_FAILED"], Severity.CRITICAL)

    def test_file_suspected_row_limit_truncation_default_is_error(self) -> None:
        self.assertEqual(
            REASON_CODE_SEVERITY["DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION"], Severity.ERROR
        )


class SeverityOrderingTests(unittest.TestCase):
    def test_ascending_strength_order(self) -> None:
        self.assertLess(Severity.INFO, Severity.WARN)
        self.assertLess(Severity.WARN, Severity.ERROR)
        self.assertLess(Severity.ERROR, Severity.CRITICAL)


class SortReasonCodesTests(unittest.TestCase):
    def test_severity_descending_primary_order(self) -> None:
        result = sort_reason_codes(
            ["DV_GAP_DETECTED", "DV_DUPLICATE_CONFLICT", "DV_APPROVED_WARNING_ACTIVE"]
        )
        # CRITICAL (DUPLICATE_CONFLICT) first, then WARN (GAP_DETECTED), then INFO
        self.assertEqual(
            result,
            ["DV_DUPLICATE_CONFLICT", "DV_GAP_DETECTED", "DV_APPROVED_WARNING_ACTIVE"],
        )

    def test_alphabetic_tiebreak_within_same_severity(self) -> None:
        # Both CRITICAL: DV_CHECKSUM_MISMATCH < DV_FILE_CORRUPT alphabetically
        result = sort_reason_codes(["DV_FILE_CORRUPT", "DV_CHECKSUM_MISMATCH"])
        self.assertEqual(result, ["DV_CHECKSUM_MISMATCH", "DV_FILE_CORRUPT"])

    def test_order_independent_of_input_order(self) -> None:
        codes = ["DV_VOLUME_ZERO_OBSERVED", "DV_VOLUME_NEGATIVE", "DV_GAP_DETECTED"]
        self.assertEqual(sort_reason_codes(codes), sort_reason_codes(list(reversed(codes))))

    def test_empty_input_yields_empty_output(self) -> None:
        self.assertEqual(sort_reason_codes([]), [])

    def test_profile_id_is_a_nonempty_versioned_string(self) -> None:
        self.assertTrue(REASON_CODE_PRIORITY_PROFILE_ID)
        self.assertIn("V1", REASON_CODE_PRIORITY_PROFILE_ID)


class DeriveQualityStatusTests(unittest.TestCase):
    def test_no_active_codes_is_pass(self) -> None:
        self.assertEqual(derive_quality_status([]), "PASS")

    def test_only_info_codes_is_pass(self) -> None:
        self.assertEqual(
            derive_quality_status(["DV_DUPLICATE_IDENTICAL_COLLAPSED", "DV_APPROVED_WARNING_ACTIVE"]),
            "PASS",
        )

    def test_highest_warn_yields_warn(self) -> None:
        self.assertEqual(
            derive_quality_status(["DV_APPROVED_WARNING_ACTIVE", "DV_GAP_DETECTED"]), "WARN"
        )

    def test_highest_error_yields_error(self) -> None:
        self.assertEqual(
            derive_quality_status(["DV_GAP_DETECTED", "DV_TIME_OUT_OF_RANGE"]), "ERROR"
        )

    def test_highest_critical_yields_critical(self) -> None:
        self.assertEqual(
            derive_quality_status(
                ["DV_TIME_OUT_OF_RANGE", "DV_OHLC_INVARIANT_FAILED", "DV_GAP_DETECTED"]
            ),
            "CRITICAL",
        )


class QualityRuleVersionTests(unittest.TestCase):
    def test_is_a_nonempty_versioned_string(self) -> None:
        self.assertTrue(QUALITY_RULE_VERSION)
        self.assertIn("V1", QUALITY_RULE_VERSION)
        self.assertTrue(QUALITY_RULE_VERSION.startswith("RCC002_"))


if __name__ == "__main__":
    unittest.main()
