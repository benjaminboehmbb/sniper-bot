"""Unit tests for rcc002.s0.manifest."""

import dataclasses
import json
import unittest
from pathlib import Path

from rcc002.s0.manifest import (
    CoverageReconciliation,
    ConflictingLegacyAliasError,
    LegacySourceManifest,
    ManifestProducer,
    SourceManifest,
    migrate_legacy_aliases,
)
from rcc002.s0.profiles import (
    ArchivePeriod,
    SourceProfileError,
    TimestampUnit,
)
from rcc002.s0.source_identity import (
    SourceFileIdentity,
    build_source_snapshot,
)

VALID_SHA256 = "a" * 64
SOURCE_IDENTITY_FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures/rcc002/source/source_identity_golden.v1.json"
)


def make_manifest(**overrides: object) -> LegacySourceManifest:
    fields: dict[str, object] = dict(
        source_snapshot_id="source:sha256:" + VALID_SHA256,
        provider="binance",
        market_type="spot",
        symbol="BTCUSDT",
        interval="1m",
        retrieved_at_utc=1_700_000_000_000,
        source_file_name="BTCUSDT-1m-2024-01.csv",
        source_byte_sha256=VALID_SHA256,
        source_format="csv",
        source_location="https://data.binance.vision/",
    )
    fields.update(overrides)
    return LegacySourceManifest(**fields)  # type: ignore[arg-type]


class SourceManifestConstructionTests(unittest.TestCase):
    def test_valid_manifest_constructs(self) -> None:
        manifest = make_manifest()
        self.assertEqual(manifest.provider, "binance")
        self.assertIsNone(manifest.source_revision)
        self.assertIsNone(manifest.license_or_terms_ref)

    def test_nullable_fields_accept_none_explicitly(self) -> None:
        manifest = make_manifest(source_revision=None, license_or_terms_ref=None)
        self.assertIsNone(manifest.source_revision)

    def test_nullable_fields_accept_value(self) -> None:
        manifest = make_manifest(
            source_revision="rev-42", license_or_terms_ref="https://example/terms"
        )
        self.assertEqual(manifest.source_revision, "rev-42")

    def test_is_frozen(self) -> None:
        manifest = make_manifest()
        with self.assertRaises(Exception):
            manifest.provider = "other"  # type: ignore[misc]

    def test_registered_provider_is_forbidden_on_legacy_manifest(self) -> None:
        with self.assertRaises(SourceProfileError) as context:
            make_manifest(provider="BINANCE_VISION")
        self.assertEqual(
            context.exception.reason_code,
            "RCC_SOURCE_REGISTERED_PROVIDER_LEGACY_PATH_FORBIDDEN",
        )

    def test_registered_provider_guard_is_case_insensitive(self) -> None:
        with self.assertRaises(SourceProfileError):
            make_manifest(provider="binance_vision")


class SourceManifestRequiredFieldTests(unittest.TestCase):
    def test_empty_provider_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_manifest(provider="")

    def test_empty_symbol_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_manifest(symbol="")

    def test_empty_source_file_name_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_manifest(source_file_name="")


class SourceManifestFormatValidationTests(unittest.TestCase):
    def test_sha256_must_be_64_lowercase_hex(self) -> None:
        with self.assertRaises(ValueError):
            make_manifest(source_byte_sha256="A" * 64)  # uppercase rejected

    def test_sha256_wrong_length_rejected(self) -> None:
        with self.assertRaises(ValueError):
            make_manifest(source_byte_sha256="abc123")

    def test_retrieved_at_utc_must_be_int(self) -> None:
        with self.assertRaises(ValueError):
            make_manifest(retrieved_at_utc="1700000000000")  # type: ignore[arg-type]

    def test_retrieved_at_utc_rejects_bool(self) -> None:
        # bool is a subclass of int in Python; explicitly excluded.
        with self.assertRaises(ValueError):
            make_manifest(retrieved_at_utc=True)  # type: ignore[arg-type]


def make_registered_snapshot():
    source = SourceFileIdentity(
        provider_relative_name=(
            "data/spot/daily/klines/BTCUSDT/1m/"
            "BTCUSDT-1m-2024-12-31.zip"
        ),
        byte_sha256="b" * 64,
        provider_checksum_sha256="b" * 64,
        size_bytes=100,
        csv_member_name="BTCUSDT-1m-2024-12-31.csv",
        source_file_ordinal=0,
        archive_period=ArchivePeriod(
            archive_family="DAILY",
            period_token="2024-12-31",
            period_start_utc="2024-12-31T00:00:00Z",
            period_end_utc="2025-01-01T00:00:00Z",
        ),
        record_count=1,
        min_open_time_utc_ms=1_735_603_200_000,
        max_close_time_utc_ms=1_735_603_259_999,
        timestamp_unit=TimestampUnit.MILLISECOND,
    )
    return build_source_snapshot((source,))


def make_two_file_registered_snapshot():
    first_period = ArchivePeriod(
        archive_family="DAILY",
        period_token="2024-12-30",
        period_start_utc="2024-12-30T00:00:00Z",
        period_end_utc="2024-12-31T00:00:00Z",
    )
    second_period = ArchivePeriod(
        archive_family="DAILY",
        period_token="2024-12-31",
        period_start_utc="2024-12-31T00:00:00Z",
        period_end_utc="2025-01-01T00:00:00Z",
    )
    first = SourceFileIdentity(
        provider_relative_name=(
            "data/spot/daily/klines/BTCUSDT/1m/"
            "BTCUSDT-1m-2024-12-30.zip"
        ),
        byte_sha256="a" * 64,
        provider_checksum_sha256="a" * 64,
        size_bytes=100,
        csv_member_name="BTCUSDT-1m-2024-12-30.csv",
        source_file_ordinal=0,
        archive_period=first_period,
        record_count=1,
        min_open_time_utc_ms=1_735_516_800_000,
        max_close_time_utc_ms=1_735_516_859_999,
        timestamp_unit=TimestampUnit.MILLISECOND,
    )
    second = SourceFileIdentity(
        provider_relative_name=(
            "data/spot/daily/klines/BTCUSDT/1m/"
            "BTCUSDT-1m-2024-12-31.zip"
        ),
        byte_sha256="b" * 64,
        provider_checksum_sha256="b" * 64,
        size_bytes=100,
        csv_member_name="BTCUSDT-1m-2024-12-31.csv",
        source_file_ordinal=1,
        archive_period=second_period,
        record_count=1,
        min_open_time_utc_ms=1_735_603_200_000,
        max_close_time_utc_ms=1_735_603_259_999,
        timestamp_unit=TimestampUnit.MILLISECOND,
    )
    return build_source_snapshot((first, second))


def make_registered_manifest() -> SourceManifest:
    return SourceManifest.from_snapshot(
        make_registered_snapshot(),
        manifest_id="manifest:sha256:" + "c" * 64,
        created_at_utc="2026-07-30T18:00:00Z",
        producer=ManifestProducer(
            component="RCC002_S0_SOURCE_INGEST",
            version="1.0.0",
        ),
        status="candidate",
        retrieved_at_utc="2026-07-30T17:00:00Z",
        coverage_reconciliation=CoverageReconciliation(status="PASS"),
    )


class RegisteredSourceManifestTests(unittest.TestCase):
    def test_materializes_exact_schema_fields(self) -> None:
        manifest = make_registered_manifest()
        payload = manifest.as_dict()
        schema_path = (
            Path(__file__).parents[3]
            / "schemas/rcc002/manifests/source-manifest/"
            / "1.0.0.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(set(payload), set(schema["required"]))
        self.assertEqual(
            payload["source_snapshot_id"],
            make_registered_snapshot().source_snapshot_id,
        )
        json.dumps(payload, allow_nan=False)

    def test_identity_mismatch_is_rejected(self) -> None:
        manifest = make_registered_manifest()
        with self.assertRaises(ValueError):
            dataclasses.replace(
                manifest,
                source_snapshot_preimage_sha256="d" * 64,
            )

    def test_noncanonical_source_file_order_is_rejected(self) -> None:
        fixture = json.loads(
            SOURCE_IDENTITY_FIXTURE_PATH.read_text(encoding="utf-8")
        )
        case = next(
            item
            for item in fixture["negative_cases"]
            if item["case_id"] == "noncanonical_source_file_order"
        )
        snapshot = make_two_file_registered_snapshot()
        manifest = SourceManifest.from_snapshot(
            snapshot,
            manifest_id="manifest:sha256:" + "c" * 64,
            created_at_utc="2026-07-30T18:00:00Z",
            producer=ManifestProducer(
                component="RCC002_S0_SOURCE_INGEST",
                version="1.0.0",
            ),
            status="candidate",
            retrieved_at_utc="2026-07-30T17:00:00Z",
            coverage_reconciliation=CoverageReconciliation(status="PASS"),
        )
        with self.assertRaises(SourceProfileError) as context:
            dataclasses.replace(
                manifest,
                source_files=tuple(reversed(manifest.source_files)),
            )
        self.assertEqual(
            context.exception.reason_code,
            case["expected_error"],
        )

    def test_noncanonical_constant_is_rejected(self) -> None:
        manifest = make_registered_manifest()
        with self.assertRaises(ValueError):
            dataclasses.replace(manifest, provider="BINANCE")

    def test_pass_reconciliation_rejects_exceptions(self) -> None:
        with self.assertRaises(ValueError):
            CoverageReconciliation(
                status="PASS",
                exceptions=("unexpected overlap",),
            )

    def test_empty_license_reference_is_rejected(self) -> None:
        manifest = make_registered_manifest()
        with self.assertRaises(ValueError):
            dataclasses.replace(manifest, license_or_terms_ref="")


class LegacyAliasMigrationTests(unittest.TestCase):
    def test_migrates_source_provider(self) -> None:
        result = migrate_legacy_aliases({"source_provider": "binance"})
        self.assertEqual(result, {"provider": "binance"})
        self.assertNotIn("source_provider", result)

    def test_migrates_source_retrieved_at_utc(self) -> None:
        result = migrate_legacy_aliases({"source_retrieved_at_utc": 123})
        self.assertEqual(result, {"retrieved_at_utc": 123})
        self.assertNotIn("source_retrieved_at_utc", result)

    def test_migrates_both_aliases_together(self) -> None:
        result = migrate_legacy_aliases(
            {"source_provider": "binance", "source_retrieved_at_utc": 123, "symbol": "BTCUSDT"}
        )
        self.assertEqual(
            result, {"provider": "binance", "retrieved_at_utc": 123, "symbol": "BTCUSDT"}
        )

    def test_non_aliased_keys_pass_through_unchanged(self) -> None:
        result = migrate_legacy_aliases({"symbol": "BTCUSDT"})
        self.assertEqual(result, {"symbol": "BTCUSDT"})

    def test_already_canonical_input_is_a_no_op(self) -> None:
        result = migrate_legacy_aliases({"provider": "binance"})
        self.assertEqual(result, {"provider": "binance"})

    def test_conflicting_legacy_and_canonical_keys_raise(self) -> None:
        with self.assertRaises(ConflictingLegacyAliasError):
            migrate_legacy_aliases({"source_provider": "binance", "provider": "coinbase"})

    def test_reverse_mapping_is_not_applied(self) -> None:
        # 'provider' must never be renamed back to 'source_provider'.
        result = migrate_legacy_aliases({"provider": "binance"})
        self.assertNotIn("source_provider", result)


if __name__ == "__main__":
    unittest.main()
