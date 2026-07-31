"""Unit tests for rcc002.s0.ingest."""

import tempfile
import unittest
from pathlib import Path

from rcc002.s0.integrity import SourceFileState
from rcc002.s0.ingest import ingest_source
from rcc002.s0.profiles import SourceProfileError

VALID_SNAPSHOT_ID = "source:sha256:" + "a" * 64


class IngestSourceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def write_csv(self, name: str, data_rows: int) -> Path:
        path = self.tmp_path / name
        lines = ["open_time,open,high,low,close,volume"] + [
            f"{i},1,1,1,1,1" for i in range(data_rows)
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def ingest(self, path: Path, **overrides: object):
        kwargs: dict[str, object] = dict(
            source_snapshot_id=VALID_SNAPSHOT_ID,
            provider="binance",
            market_type="spot",
            symbol="BTCUSDT",
            interval="1m",
            retrieved_at_utc=1_700_000_000_000,
            source_format="csv",
            source_location="https://data.binance.vision/",
        )
        kwargs.update(overrides)
        return ingest_source(path, **kwargs)  # type: ignore[arg-type]


class MissingFileTests(IngestSourceTestCase):
    def test_missing_file_yields_missing_state(self) -> None:
        result = self.ingest(self.tmp_path / "does-not-exist.csv")
        self.assertEqual(result.state, SourceFileState.MISSING)
        self.assertIsNone(result.manifest)

    def test_missing_file_checks_recorded(self) -> None:
        result = self.ingest(self.tmp_path / "does-not-exist.csv")
        self.assertFalse(result.checks[0].passed)


class RegisteredProviderBoundaryTests(IngestSourceTestCase):
    def test_registered_provider_is_rejected_before_file_access(self) -> None:
        with self.assertRaises(SourceProfileError) as context:
            self.ingest(
                self.tmp_path / "does-not-exist.csv",
                provider="BINANCE_VISION",
            )
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_REGISTERED_PROVIDER_LEGACY_PATH_FORBIDDEN",
        )

    def test_registered_provider_cannot_enter_through_legacy_alias(self) -> None:
        path = self.write_csv("BTCUSDT-1m.csv", 1)
        with self.assertRaises(SourceProfileError):
            self.ingest(
                path,
                raw_metadata={"source_provider": "BINANCE_VISION"},
            )


class EmptyFileTests(IngestSourceTestCase):
    def test_empty_file_yields_corrupt_state(self) -> None:
        path = self.tmp_path / "empty.csv"
        path.write_text("", encoding="utf-8")
        result = self.ingest(path)
        self.assertEqual(result.state, SourceFileState.CORRUPT)
        self.assertIsNone(result.manifest)


class DisallowedFormatTests(IngestSourceTestCase):
    def test_xlsx_extension_yields_corrupt_state(self) -> None:
        path = self.tmp_path / "a.xlsx"
        path.write_text("something", encoding="utf-8")
        result = self.ingest(path)
        self.assertEqual(result.state, SourceFileState.CORRUPT)


class VerifiedFileTests(IngestSourceTestCase):
    def test_valid_file_yields_verified_state_and_manifest(self) -> None:
        path = self.write_csv("BTCUSDT-1m.csv", 100)
        result = self.ingest(path)
        self.assertEqual(result.state, SourceFileState.VERIFIED)
        self.assertIsNotNone(result.manifest)
        assert result.manifest is not None
        self.assertEqual(result.manifest.provider, "binance")
        self.assertEqual(result.manifest.source_file_name, "BTCUSDT-1m.csv")
        self.assertEqual(result.manifest.source_snapshot_id, VALID_SNAPSHOT_ID)

    def test_manifest_byte_hash_matches_actual_file(self) -> None:
        import hashlib

        path = self.write_csv("BTCUSDT-1m.csv", 10)
        result = self.ingest(path)
        assert result.manifest is not None
        expected = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(result.manifest.source_byte_sha256, expected)

    def test_no_truncation_finding_for_normal_row_count(self) -> None:
        path = self.write_csv("BTCUSDT-1m.csv", 100)
        result = self.ingest(path)
        self.assertIsNone(result.truncation_finding)


class ChecksumMismatchTests(IngestSourceTestCase):
    def test_provider_checksum_mismatch_yields_checksum_mismatch_state(self) -> None:
        path = self.write_csv("BTCUSDT-1m.csv", 10)
        result = self.ingest(path, provider_sha256="0" * 64)
        self.assertEqual(result.state, SourceFileState.CHECKSUM_MISMATCH)
        self.assertIsNone(result.manifest)

    def test_provider_checksum_match_yields_verified_state(self) -> None:
        import hashlib

        path = self.write_csv("BTCUSDT-1m.csv", 10)
        actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        result = self.ingest(path, provider_sha256=actual_sha256)
        self.assertEqual(result.state, SourceFileState.VERIFIED)


class TruncationBoundaryTests(IngestSourceTestCase):
    def test_65535_row_file_produces_truncation_finding(self) -> None:
        path = self.write_csv("BTCUSDT-1m.csv", 65_535)
        result = self.ingest(path)
        self.assertEqual(result.state, SourceFileState.VERIFIED)
        self.assertIsNotNone(result.truncation_finding)
        assert result.truncation_finding is not None
        self.assertEqual(
            result.truncation_finding.reason_code,
            "DV_FILE_SUSPECTED_ROW_LIMIT_TRUNCATION",
        )

    def test_truncation_escalates_to_critical_when_flagged(self) -> None:
        path = self.write_csv("BTCUSDT-1m.csv", 65_535)
        result = self.ingest(path, upstream_has_more_rows_or_longer_range=True)
        assert result.truncation_finding is not None
        self.assertEqual(result.truncation_finding.severity, "CRITICAL")


class LegacyAliasMetadataTests(IngestSourceTestCase):
    def test_raw_metadata_legacy_aliases_are_migrated(self) -> None:
        path = self.write_csv("BTCUSDT-1m.csv", 10)
        result = self.ingest(
            path,
            raw_metadata={"source_provider": "coinbase", "source_retrieved_at_utc": 42},
        )
        assert result.manifest is not None
        self.assertEqual(result.manifest.provider, "coinbase")
        self.assertEqual(result.manifest.retrieved_at_utc, 42)


if __name__ == "__main__":
    unittest.main()
