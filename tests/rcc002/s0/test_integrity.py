"""Unit tests for rcc002.s0.integrity."""

import tempfile
import unittest
from pathlib import Path

from rcc002.s0.integrity import (
    DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION,
    UnsupportedSourceFormatError,
    check_exists,
    check_header_present,
    check_nonempty,
    check_not_disallowed_format,
    check_provider_checksum,
    check_readable,
    check_spreadsheet_truncation_boundary,
    compute_source_byte_sha256,
    count_data_rows,
)


class TempFileTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def write_csv(self, name: str, header: str, data_rows: int) -> Path:
        path = self.tmp_path / name
        lines = [header] + [f"row{i}" for i in range(data_rows)]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


class ExistsReadableNonemptyTests(TempFileTestCase):
    def test_exists_true_for_existing_file(self) -> None:
        path = self.write_csv("a.csv", "header", 1)
        self.assertTrue(check_exists(path).passed)

    def test_exists_false_for_missing_file(self) -> None:
        self.assertFalse(check_exists(self.tmp_path / "missing.csv").passed)

    def test_readable_false_for_missing_file(self) -> None:
        result = check_readable(self.tmp_path / "missing.csv")
        self.assertFalse(result.passed)

    def test_nonempty_true_for_nonempty_file(self) -> None:
        path = self.write_csv("a.csv", "header", 1)
        self.assertTrue(check_nonempty(path).passed)

    def test_nonempty_false_for_empty_file(self) -> None:
        path = self.tmp_path / "empty.csv"
        path.write_text("", encoding="utf-8")
        self.assertFalse(check_nonempty(path).passed)

    def test_nonempty_false_for_missing_file(self) -> None:
        self.assertFalse(check_nonempty(self.tmp_path / "missing.csv").passed)


class DisallowedFormatTests(unittest.TestCase):
    def test_csv_is_allowed(self) -> None:
        self.assertTrue(check_not_disallowed_format(Path("a.csv")).passed)

    def test_xlsx_is_disallowed(self) -> None:
        self.assertFalse(check_not_disallowed_format(Path("a.xlsx")).passed)

    def test_xls_is_disallowed(self) -> None:
        self.assertFalse(check_not_disallowed_format(Path("a.xls")).passed)

    def test_ods_is_disallowed(self) -> None:
        self.assertFalse(check_not_disallowed_format(Path("a.ods")).passed)

    def test_disallowed_check_is_case_insensitive(self) -> None:
        self.assertFalse(check_not_disallowed_format(Path("a.XLSX")).passed)


class HeaderCheckTests(TempFileTestCase):
    def test_header_present_passes(self) -> None:
        path = self.write_csv("a.csv", "open_time,open,high,low,close,volume", 2)
        self.assertTrue(check_header_present(path, "csv").passed)

    def test_header_missing_on_empty_file_fails(self) -> None:
        path = self.tmp_path / "empty.csv"
        path.write_text("", encoding="utf-8")
        self.assertFalse(check_header_present(path, "csv").passed)

    def test_unsupported_format_raises_via_open_source_text(self) -> None:
        path = self.write_csv("a.csv", "header", 1)
        result = check_header_present(path, "parquet")
        self.assertFalse(result.passed)


class Sha256Tests(TempFileTestCase):
    def test_matches_hashlib_reference(self) -> None:
        import hashlib

        path = self.write_csv("a.csv", "header", 5)
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(compute_source_byte_sha256(path), expected)

    def test_deterministic_across_repeated_calls(self) -> None:
        path = self.write_csv("a.csv", "header", 5)
        self.assertEqual(
            compute_source_byte_sha256(path), compute_source_byte_sha256(path)
        )


class ProviderChecksumTests(unittest.TestCase):
    def test_passes_vacuously_when_no_provider_checksum(self) -> None:
        self.assertTrue(check_provider_checksum("abc", None).passed)

    def test_passes_when_matching(self) -> None:
        self.assertTrue(check_provider_checksum("abc", "abc").passed)

    def test_fails_when_mismatched(self) -> None:
        self.assertFalse(check_provider_checksum("abc", "def").passed)


class RowCountAndTruncationTests(TempFileTestCase):
    def test_count_data_rows_excludes_header(self) -> None:
        path = self.write_csv("a.csv", "header", 10)
        self.assertEqual(count_data_rows(path, "csv"), 10)

    def test_count_data_rows_zero_for_header_only(self) -> None:
        path = self.write_csv("a.csv", "header", 0)
        self.assertEqual(count_data_rows(path, "csv"), 0)

    def test_no_finding_below_boundary(self) -> None:
        self.assertIsNone(check_spreadsheet_truncation_boundary(1000))

    def test_finding_at_65535_boundary(self) -> None:
        finding = check_spreadsheet_truncation_boundary(65_535)
        self.assertIsNotNone(finding)
        assert finding is not None
        self.assertEqual(finding.reason_code, DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION)
        self.assertEqual(finding.severity, "ERROR")

    def test_finding_at_1048575_boundary(self) -> None:
        finding = check_spreadsheet_truncation_boundary(1_048_575)
        self.assertIsNotNone(finding)

    def test_finding_escalates_to_critical_when_upstream_has_more(self) -> None:
        finding = check_spreadsheet_truncation_boundary(
            65_535, upstream_has_more_rows_or_longer_range=True
        )
        assert finding is not None
        self.assertEqual(finding.severity, "CRITICAL")

    def test_severity_defaults_to_registry_value_without_upstream_evidence(self) -> None:
        # Per rcc002.reason_codes.REASON_CODE_SEVERITY (Data Validation
        # §16.3, DVSEV-001): DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION's
        # standard (non-escalated) severity is ERROR.
        finding = check_spreadsheet_truncation_boundary(65_535)
        assert finding is not None
        self.assertEqual(finding.severity, "ERROR")

    def test_no_finding_one_below_boundary(self) -> None:
        self.assertIsNone(check_spreadsheet_truncation_boundary(65_534))


if __name__ == "__main__":
    unittest.main()
