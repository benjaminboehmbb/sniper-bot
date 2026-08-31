"""Non-authoritative tests for the isolated I6 paper artifact contracts.

Classification: NONAUTHORITATIVE_P2B_PATH_A_TEST_CLOSURE_CANDIDATE.
This module grants no test, evidence, acceptance, publication, execution,
live, or exchange authority.
"""

import unittest
from dataclasses import fields
from decimal import Decimal

from live_l1.core.paper_economics import EntryEconomicsQuote
from live_l1.state.paper_artifacts import (
    EntryEconomicsQuoteArtifactV1,
    LegacyArtifact,
    PaperArtifactError,
    PaperRiskStateS4V2,
)


CLASSIFICATION = "NONAUTHORITATIVE_P2B_PATH_A_TEST_CLOSURE_CANDIDATE"
D = Decimal
H1, H2, H3 = "1" * 64, "2" * 64, "3" * 64
H4, H5, H6 = "4" * 64, "5" * 64, "6" * 64
H7, H8, H9 = "7" * 64, "8" * 64, "9" * 64

ENTRY_FIELDS = {
    "schema_version", "side", "reference_entry_price", "reference_stop_price",
    "modeled_entry_fill_price", "modeled_stop_fill_price",
    "realized_equity_quote", "risk_budget_quote",
    "modeled_stop_loss_per_unit_quote", "risk_quantity",
    "notional_cap_quote", "notional_cap_quantity", "raw_quantity",
    "quantity_step", "quantity", "entry_notional_quote", "entry_fee_quote",
    "expected_stop_notional_quote", "expected_stop_fee_quote",
    "modeled_stop_loss_quote", "economics_profile_id",
    "economics_model_version", "config_fingerprint",
}

RISK_FIELDS = {
    "schema_version", "system_state_id", "kill_level", "cooldown_until_utc",
    "trades_today", "loss_today", "anomaly_counter", "trades_6h",
    "last_trade_timestamp_utc", "entry_allowed", "exit_evaluation_allowed",
    "runtime_directive", "reason_codes", "position_fingerprint",
    "account_fingerprint", "throttle_fingerprint",
    "loss_cluster_fingerprint", "progress_cursor_fingerprint",
    "runtime_control_profile_id", "runtime_control_fingerprint",
    "loss_cluster_policy_id", "loss_cluster_policy_fingerprint",
    "economics_profile_id", "economics_model_version", "config_fingerprint",
    "throttle_policy_profile_id", "throttle_policy_model_version",
    "throttle_policy_fingerprint", "authority_generation_id",
    "transaction_sequence", "journal_head", "last_transaction_event_id",
    "last_transaction_timestamp_utc", "last_transaction_tick_id",
}


def make_quote(**changes):
    values = {
        "side": "LONG",
        "reference_entry_price": D("100"),
        "reference_stop_price": D("90"),
        "modeled_entry_fill_price": D("101"),
        "modeled_stop_fill_price": D("89"),
        "realized_equity_quote": D("10000"),
        "risk_budget_quote": D("100"),
        "modeled_stop_loss_per_unit_quote": D("12"),
        "risk_quantity": D("8"),
        "notional_cap_quote": D("5000"),
        "notional_cap_quantity": D("49"),
        "raw_quantity": D("8"),
        "quantity_step": D("0.1"),
        "quantity": D("8"),
        "entry_notional_quote": D("808"),
        "entry_fee_quote": D("0.808"),
        "expected_stop_notional_quote": D("712"),
        "expected_stop_fee_quote": D("0.712"),
        "modeled_stop_loss_quote": D("96"),
        "economics_profile_id": "PEE-I6",
        "economics_model_version": "v2",
        "config_fingerprint": H1,
    }
    values.update(changes)
    return EntryEconomicsQuote(**values)


def make_entry(**changes):
    return EntryEconomicsQuoteArtifactV1.from_quote(make_quote(**changes))


def make_risk(**changes):
    values = {
        "schema_version": 2,
        "system_state_id": "S4-I6",
        "kill_level": "NONE",
        "cooldown_until_utc": "2026-08-31T10:00:00+02:00",
        "trades_today": 2,
        "loss_today": D("0"),
        "anomaly_counter": 0,
        "trades_6h": 2,
        "last_trade_timestamp_utc": "2026-08-31T07:30:00Z",
        "entry_allowed": True,
        "exit_evaluation_allowed": True,
        "runtime_directive": "CONTINUE",
        "reason_codes": (),
        "position_fingerprint": H1,
        "account_fingerprint": H2,
        "throttle_fingerprint": H3,
        "loss_cluster_fingerprint": H4,
        "progress_cursor_fingerprint": H5,
        "runtime_control_profile_id": "RC-I6",
        "runtime_control_fingerprint": H6,
        "loss_cluster_policy_id": "LC-I6",
        "loss_cluster_policy_fingerprint": H7,
        "economics_profile_id": "PEE-I6",
        "economics_model_version": "v2",
        "config_fingerprint": H8,
        "throttle_policy_profile_id": "TH-I6",
        "throttle_policy_model_version": "v2",
        "throttle_policy_fingerprint": H9,
        "authority_generation_id": "AUTH-I6",
        "transaction_sequence": 0,
        "journal_head": "EMPTY",
        "last_transaction_event_id": "",
        "last_transaction_timestamp_utc": "",
        "last_transaction_tick_id": 0,
    }
    values.update(changes)
    return PaperRiskStateS4V2(**values)


class EntryEconomicsQuoteArtifactV1Tests(unittest.TestCase):
    def test_complete_fields_quote_roundtrip_and_canonical_values(self):
        artifact = make_entry()
        self.assertEqual({item.name for item in fields(artifact)}, ENTRY_FIELDS)
        # The current exact quote schema has no UTC member; do not invent one.
        self.assertFalse(any(name.endswith("_utc") for name in ENTRY_FIELDS))
        self.assertEqual(artifact.to_quote(), make_quote())
        self.assertEqual(
            EntryEconomicsQuoteArtifactV1.from_quote(artifact.to_quote()),
            artifact,
        )
        self.assertEqual(artifact.entry_notional_quote, D("808"))
        self.assertEqual(artifact.modeled_stop_loss_quote, D("96"))
        self.assertEqual(artifact.config_fingerprint, H1)

    def test_record_roundtrip_canonicality_and_fingerprints(self):
        artifact = make_entry()
        record = artifact.to_record()
        self.assertEqual(record["artifact_type"], "entry_economics_quote")
        self.assertEqual(record["quantity"], "8")
        self.assertEqual(record["quantity_step"], "0.1")
        self.assertEqual(record["entry_fee_quote"], "0.808")
        self.assertEqual(len(record["quote_fingerprint"]), 64)
        self.assertEqual(record["quote_fingerprint"], record["quote_fingerprint"].lower())
        rebuilt = EntryEconomicsQuoteArtifactV1.from_record(record)
        self.assertEqual(rebuilt, artifact)
        self.assertEqual(rebuilt.to_record(), record)
        self.assertEqual(make_entry().quote_fingerprint, artifact.quote_fingerprint)
        self.assertNotEqual(
            make_entry(economics_profile_id="PEE-I6-OTHER").quote_fingerprint,
            artifact.quote_fingerprint,
        )

    def test_wrong_primitives_and_broken_identities_are_rejected(self):
        artifact = make_entry()
        values = {item.name: getattr(artifact, item.name) for item in fields(artifact)}
        for name, value in (
            ("schema_version", True),
            ("quantity", True),
            ("quantity", 8.0),
            ("side", 1),
            ("config_fingerprint", "g" * 64),
        ):
            candidate = dict(values)
            candidate[name] = value
            with self.subTest(name=name, value=value):
                with self.assertRaises(PaperArtifactError):
                    EntryEconomicsQuoteArtifactV1(**candidate)
        for changes in (
            {"reference_stop_price": D("100")},
            {"entry_notional_quote": D("807")},
            {"modeled_stop_loss_quote": D("95")},
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(PaperArtifactError):
                    make_entry(**changes)

    def test_incomplete_unknown_tampered_noncanonical_records_are_rejected(self):
        record = make_entry().to_record()
        candidates = []
        item = dict(record)
        item.pop("quantity")
        candidates.append(item)
        item = dict(record)
        item["unknown"] = "blocked"
        candidates.append(item)
        for name, value in (
            ("artifact_type", "other"),
            ("quote_fingerprint", H2),
            ("quantity", "8.0"),
            ("config_fingerprint", "A" * 64),
        ):
            item = dict(record)
            item[name] = value
            candidates.append(item)
        for candidate in candidates:
            with self.subTest(keys=tuple(sorted(candidate))):
                with self.assertRaises(PaperArtifactError):
                    EntryEconomicsQuoteArtifactV1.from_record(candidate)

    def test_existing_legacy_artifact_remains_distinct_and_unchanged(self):
        raw = {"schema_version": 1, "position": "FLAT"}
        legacy = LegacyArtifact("s2_position", 1, raw)
        self.assertIsNot(EntryEconomicsQuoteArtifactV1, LegacyArtifact)
        self.assertIsNot(PaperRiskStateS4V2, LegacyArtifact)
        self.assertEqual(legacy.raw_record, raw)
        self.assertFalse(legacy.economics_complete)
        self.assertFalse(legacy.entry_allowed)
        self.assertTrue(legacy.exit_allowed)


class PaperRiskStateS4V2Tests(unittest.TestCase):
    def test_complete_fields_utc_decimal_and_provenance_bindings(self):
        state = make_risk()
        self.assertEqual({item.name for item in fields(state)}, RISK_FIELDS)
        self.assertEqual(state.cooldown_until_utc, "2026-08-31T08:00:00Z")
        self.assertEqual(state.last_trade_timestamp_utc, "2026-08-31T07:30:00Z")
        self.assertEqual(state.loss_today, D("0"))
        expected = {
            "position_fingerprint": H1,
            "account_fingerprint": H2,
            "throttle_fingerprint": H3,
            "loss_cluster_fingerprint": H4,
            "progress_cursor_fingerprint": H5,
            "runtime_control_fingerprint": H6,
            "loss_cluster_policy_fingerprint": H7,
            "config_fingerprint": H8,
            "throttle_policy_fingerprint": H9,
            "authority_generation_id": "AUTH-I6",
        }
        for name, value in expected.items():
            self.assertEqual(getattr(state, name), value)

    def test_business_canonical_record_and_fingerprint_roundtrips(self):
        state = make_risk()
        canonical = state.canonical_payload()
        business = state.business_payload()
        record = state.to_record()
        self.assertEqual(set(canonical), RISK_FIELDS)
        self.assertEqual(canonical["loss_today"], "0")
        self.assertEqual(record["state_fingerprint"], state.state_fingerprint)
        self.assertEqual(PaperRiskStateS4V2.from_record(record), state)
        self.assertEqual(PaperRiskStateS4V2.from_record(record).to_record(), record)
        for omitted in (
            "authority_generation_id", "transaction_sequence", "journal_head",
            "last_transaction_event_id", "last_transaction_timestamp_utc",
            "last_transaction_tick_id",
        ):
            self.assertNotIn(omitted, business)
        self.assertEqual(make_risk().state_fingerprint, state.state_fingerprint)
        self.assertNotEqual(
            make_risk(anomaly_counter=1).state_fingerprint,
            state.state_fingerprint,
        )

    def test_strict_primitives_utc_hashes_and_capabilities(self):
        invalid = (
            {"schema_version": True},
            {"trades_today": True},
            {"loss_today": True},
            {"loss_today": 0.0},
            {"entry_allowed": 1},
            {"cooldown_until_utc": "2026-08-31T08:00:00.1Z"},
            {"position_fingerprint": "bad"},
            {"kill_level": "HARD"},
            {"entry_allowed": False},
            {
                "kill_level": "SOFT", "entry_allowed": False,
                "reason_codes": ("PAUSED", "PAUSED"),
            },
            {"transaction_sequence": 1, "journal_head": H1},
        )
        for changes in invalid:
            with self.subTest(changes=changes):
                with self.assertRaises(PaperArtifactError):
                    make_risk(**changes)

    def test_noncanonical_missing_unknown_contradictory_records_are_rejected(self):
        record = make_risk().to_record()
        candidates = []
        item = dict(record)
        item.pop("progress_cursor_fingerprint")
        candidates.append(item)
        item = dict(record)
        item["unknown"] = 1
        candidates.append(item)
        for name, value in (
            ("loss_today", "0.0"),
            ("cooldown_until_utc", "2026-08-31T08:00:00+00:00"),
            ("state_fingerprint", H1),
        ):
            item = dict(record)
            item[name] = value
            candidates.append(item)
        for candidate in candidates:
            with self.subTest(keys=tuple(sorted(candidate))):
                with self.assertRaises(PaperArtifactError):
                    PaperRiskStateS4V2.from_record(candidate)
