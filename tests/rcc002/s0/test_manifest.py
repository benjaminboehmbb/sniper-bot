"""Unit tests for rcc002.s0.manifest."""

import unittest

from rcc002.s0.manifest import (
    ConflictingLegacyAliasError,
    SourceManifest,
    migrate_legacy_aliases,
)

VALID_SHA256 = "a" * 64


def make_manifest(**overrides: object) -> SourceManifest:
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
    return SourceManifest(**fields)  # type: ignore[arg-type]


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
