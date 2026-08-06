from __future__ import annotations

import unittest

from live_l1.core.paper_economics import ReasonCode
from live_l1.core.paper_economics_shadow import (
    MODE_INVALID,
    MODE_OFF,
    MODE_SHADOW,
    SHADOW_CONFIG_MISSING,
    SHADOW_MODE_INVALID,
    add_legacy_execution_outcome,
    load_shadow_settings,
    observe_shadow_entry_candidate,
)


def shadow_environment(**overrides: str) -> dict[str, str]:
    values = {
        "PEE_MODE": "SHADOW",
        "PEE_SCHEMA_VERSION": "1",
        "PEE_ECONOMICS_MODEL_VERSION": "PEE_V1",
        "PEE_ECONOMICS_PROFILE_ID": "TEST_ONLY_CONSERVATIVE",
        "PEE_QUOTE_CURRENCY": "USDT",
        "PEE_STARTING_EQUITY_QUOTE": "10000",
        "PEE_RISK_PER_TRADE_RATE": "0.01",
        "PEE_MAX_POSITION_NOTIONAL_RATE": "0.05",
        "PEE_ENTRY_FEE_RATE": "0.0005",
        "PEE_EXIT_FEE_RATE": "0.0005",
        "PEE_ENTRY_SLIPPAGE_BPS": "2",
        "PEE_EXIT_SLIPPAGE_BPS": "2",
        "PEE_QUANTITY_STEP": "0.001",
        "PEE_MIN_QUANTITY": "0.001",
        "PEE_MIN_NOTIONAL_QUOTE": "5",
        "PEE_MAX_DAILY_LOSS_RATE": "0.03",
        "PEE_MAX_DAILY_FEE_RATE": "0.01",
        "PEE_MAX_REALIZED_DRAWDOWN_RATE": "0.10",
        "PEE_REFERENCE_STOP_RATE": "0.015",
    }
    values.update(overrides)
    return values


def observe(settings, **overrides: object):
    values: dict[str, object] = {
        "settings": settings,
        "current_position": "FLAT",
        "intent_final": "BUY",
        "reference_entry_price": "100",
        "tick_id": 10,
        "snapshot_id": "SNAP-10",
        "timestamp_utc": "2026-08-06T10:00:00Z",
        "intent_id": "INTENT-10",
    }
    values.update(overrides)
    return observe_shadow_entry_candidate(**values)


class ShadowSettingsTests(unittest.TestCase):
    def test_off_is_default_and_requires_no_profile(self) -> None:
        settings = load_shadow_settings({})

        self.assertEqual(settings.mode, MODE_OFF)
        self.assertFalse(settings.ready)
        self.assertIsNone(observe(settings))

    def test_invalid_mode_is_explicit_and_fail_closed(self) -> None:
        settings = load_shadow_settings({"PEE_MODE": "ENFORCED"})
        observation = observe(settings)

        self.assertEqual(settings.mode, MODE_INVALID)
        self.assertEqual(settings.reason_code, SHADOW_MODE_INVALID)
        self.assertIsNotNone(observation)
        self.assertFalse(observation.allowed)
        self.assertEqual(observation.reason_code, SHADOW_MODE_INVALID)

    def test_shadow_requires_every_numeric_and_identity_field(self) -> None:
        environment = shadow_environment()
        del environment["PEE_EXIT_FEE_RATE"]
        settings = load_shadow_settings(environment)
        observation = observe(settings)

        self.assertEqual(settings.mode, MODE_SHADOW)
        self.assertFalse(settings.ready)
        self.assertEqual(settings.reason_code, SHADOW_CONFIG_MISSING)
        self.assertIn("PEE_EXIT_FEE_RATE", settings.detail)
        self.assertIsNotNone(observation)
        self.assertEqual(observation.reason_code, SHADOW_CONFIG_MISSING)

    def test_valid_profile_has_stable_identity(self) -> None:
        first = load_shadow_settings(shadow_environment())
        second = load_shadow_settings(shadow_environment())

        self.assertTrue(first.ready)
        self.assertEqual(first.reason_code, ReasonCode.AUTHORIZED)
        self.assertIsNotNone(first.config)
        self.assertEqual(
            first.config.config_fingerprint,
            second.config.config_fingerprint,
        )


class ShadowObservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = load_shadow_settings(shadow_environment())

    def test_only_flat_buy_or_sell_is_an_entry_candidate(self) -> None:
        cases = (
            {"current_position": "LONG", "intent_final": "SELL"},
            {"current_position": "SHORT", "intent_final": "BUY"},
            {"current_position": "FLAT", "intent_final": "HOLD"},
        )
        for case in cases:
            with self.subTest(case=case):
                self.assertIsNone(observe(self.settings, **case))

    def test_long_and_short_candidates_receive_adverse_stop_and_quote(self) -> None:
        long_observation = observe(self.settings, intent_final="BUY")
        short_observation = observe(self.settings, intent_final="SELL")

        self.assertIsNotNone(long_observation)
        self.assertIsNotNone(short_observation)
        self.assertTrue(long_observation.allowed)
        self.assertTrue(short_observation.allowed)
        self.assertEqual(long_observation.side, "LONG")
        self.assertEqual(short_observation.side, "SHORT")
        self.assertEqual(long_observation.reference_stop_price, "98.5")
        self.assertEqual(short_observation.reference_stop_price, "101.5")
        self.assertNotEqual(long_observation.hypothetical_quantity, "1")
        self.assertNotEqual(short_observation.hypothetical_quantity, "1")

    def test_observation_contains_profile_model_and_fingerprint(self) -> None:
        observation = observe(self.settings)
        self.assertIsNotNone(observation)
        fields = observation.to_log_fields()

        self.assertEqual(fields["shadow_only"], 1)
        self.assertEqual(fields["economics_profile_id"], "TEST_ONLY_CONSERVATIVE")
        self.assertEqual(fields["economics_model_version"], "PEE_V1")
        self.assertEqual(len(fields["config_fingerprint"]), 64)
        self.assertEqual(fields["pee_reason_code"], ReasonCode.AUTHORIZED)

    def test_same_candidate_is_deterministic(self) -> None:
        first = observe(self.settings)
        second = observe(self.settings)

        self.assertEqual(first, second)
        self.assertEqual(len(first.observation_id), 64)

    def test_bad_market_price_becomes_rejection_not_exception(self) -> None:
        observation = observe(self.settings, reference_entry_price="not-a-price")

        self.assertIsNotNone(observation)
        self.assertFalse(observation.allowed)
        self.assertEqual(observation.hypothetical_quantity, "0")

    def test_minimum_notional_rejection_is_visible(self) -> None:
        settings = load_shadow_settings(
            shadow_environment(PEE_MIN_NOTIONAL_QUOTE="1000000")
        )
        observation = observe(settings)

        self.assertIsNotNone(observation)
        self.assertFalse(observation.allowed)
        self.assertEqual(observation.reason_code, ReasonCode.NOTIONAL_BELOW_MIN)

    def test_legacy_outcome_reports_shadow_divergence_without_control_output(self) -> None:
        rejected_settings = load_shadow_settings(
            shadow_environment(PEE_MIN_NOTIONAL_QUOTE="1000000")
        )
        observation = observe(rejected_settings)
        self.assertIsNotNone(observation)

        fields = add_legacy_execution_outcome(
            observation,
            legacy_action="OPEN_LONG",
            legacy_executed=True,
            legacy_position_before="FLAT",
            legacy_position_after="LONG",
        )

        self.assertEqual(fields["legacy_executed"], 1)
        self.assertEqual(
            fields["parity_code"],
            "PEE_SHADOW_LEGACY_EXECUTED_PEE_REJECTED",
        )
        self.assertNotIn("allow_execution", fields)
        self.assertNotIn("position_size", fields)


if __name__ == "__main__":
    unittest.main()
