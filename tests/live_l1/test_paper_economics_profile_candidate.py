from __future__ import annotations

import unittest
from pathlib import Path

from live_l1.core.paper_economics_shadow import MODE_SHADOW
from live_l1.tools.paper_economics_shadow_sidecar import load_settings_json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = (
    PROJECT_ROOT
    / "config"
    / "pee"
    / "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json"
)
EXPECTED_FINGERPRINT = (
    "ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1"
)


class PaperEconomicsProfileCandidateTests(unittest.TestCase):
    def test_candidate_is_valid_shadow_only_configuration(self) -> None:
        settings = load_settings_json(PROFILE_PATH)

        self.assertEqual(settings.mode, MODE_SHADOW)
        self.assertTrue(settings.ready)
        self.assertIsNotNone(settings.config)
        self.assertEqual(
            settings.config.economics_profile_id,
            "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001",
        )
        self.assertEqual(settings.config.quote_currency, "USDT")
        self.assertEqual(settings.config.config_fingerprint, EXPECTED_FINGERPRINT)

    def test_candidate_preserves_conservative_caps(self) -> None:
        settings = load_settings_json(PROFILE_PATH)
        config = settings.config
        self.assertIsNotNone(config)

        self.assertEqual(str(config.risk_per_trade_rate), "0.0025")
        self.assertEqual(str(config.max_position_notional_rate), "0.10")
        self.assertEqual(str(config.max_daily_loss_rate), "0.01")
        self.assertEqual(str(config.max_realized_drawdown_rate), "0.05")


if __name__ == "__main__":
    unittest.main()
