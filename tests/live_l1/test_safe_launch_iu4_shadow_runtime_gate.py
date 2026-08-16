#!/usr/bin/env python3

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from live_l1.core.paper_iu4_shadow_runtime_gate import (
    IU4ShadowRuntimeGateError,
    IU4ShadowRuntimeGateReasonCode,
)
from live_l1.core.paper_iu4_shadow_observation_gate import (
    IU4ShadowObservationError,
    IU4ShadowObservationReasonCode,
)
from live_l1.tools import safe_launch


class SafeLaunchIU4ShadowRuntimeGateTests(unittest.TestCase):
    @staticmethod
    def _passed_gate():
        return SimpleNamespace(
            mode="SHADOW",
            shadow_enabled=True,
            decision=SimpleNamespace(
                adapter_execution_enabled=False,
                state_mutation_allowed=False,
            ),
        )

    @staticmethod
    def _seed_path(override: str | None = None) -> str:
        if override is None:
            return "seeds/5m/btcusdt_5m_timing_core_v2.csv"
        return override

    @staticmethod
    def _market_path(override: str | None = None) -> str:
        if override is None:
            return "data/l1_paper_short_gate_test.csv"
        return override

    def test_passed_gate_is_bound_to_started_loop(self) -> None:
        gate = self._passed_gate()
        observation_gate = SimpleNamespace(
            enabled=True,
            max_records=1,
            observer=SimpleNamespace(close=lambda: None),
        )
        profile = {
            "profile": "PAPER",
            "startup_validation_required": True,
            "reconciliation_required": True,
        }
        startup = SimpleNamespace(passed=True, issues=[])
        environment = {
            "L1_STARTUP_RECOVERY": "1",
            "L1_STARTUP_RECONCILIATION_GATE": "1",
        }
        with (
            patch.object(safe_launch, "profile_summary", return_value=profile),
            patch.object(safe_launch, "validate_startup", return_value=startup),
            patch.object(safe_launch, "run_reconciliation", return_value=[]),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_runtime_gate",
                return_value=gate,
            ),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_observation_gate",
                return_value=observation_gate,
            ),
            patch.object(
                safe_launch,
                "run_l1_loop_step1234567",
                return_value=0,
            ) as run_loop,
            patch.dict(safe_launch.os.environ, environment, clear=True),
            patch("sys.argv", ["safe_launch.py", "--max-ticks", "1"]),
            redirect_stdout(io.StringIO()),
        ):
            result = safe_launch.main()

        self.assertEqual(result, 0)
        self.assertIs(
            run_loop.call_args.kwargs["iu4_shadow_runtime_gate"],
            gate,
        )
        self.assertIs(
            run_loop.call_args.kwargs["iu4_shadow_observation_gate"],
            observation_gate,
        )

    def test_passed_gate_validation_and_runtime_inputs_share_exact_seed_and_market_defaults(self) -> None:
        gate = self._passed_gate()
        observation_gate = SimpleNamespace(
            enabled=True,
            max_records=1,
            observer=SimpleNamespace(close=lambda: None),
        )
        profile = {
            "profile": "PAPER",
            "startup_validation_required": True,
            "reconciliation_required": True,
        }
        startup = SimpleNamespace(passed=True, issues=[])
        environment = {
            "L1_STARTUP_RECOVERY": "1",
            "L1_STARTUP_RECONCILIATION_GATE": "1",
        }
        captured = {}

        def _capture_startup(
            *,
            repo_root,
            market_csv_path: str,
            seeds_5m_csv: str,
            require_wsl: bool,
        ) -> SimpleNamespace:
            captured["market_csv_path"] = market_csv_path
            captured["seeds_5m_csv"] = seeds_5m_csv
            return startup

        with (
            patch.object(safe_launch, "profile_summary", return_value=profile),
            patch.object(safe_launch, "validate_startup", side_effect=_capture_startup),
            patch.object(safe_launch, "run_reconciliation", return_value=[]),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_runtime_gate",
                return_value=gate,
            ),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_observation_gate",
                return_value=observation_gate,
            ),
            patch.object(
                safe_launch,
                "run_l1_loop_step1234567",
                return_value=0,
            ) as run_loop,
            patch.dict(safe_launch.os.environ, environment, clear=True),
            patch("sys.argv", ["safe_launch.py", "--max-ticks", "1"]),
        ):
            result = safe_launch.main()

        expected_seed = self._seed_path()
        expected_market = self._market_path()
        self.assertEqual(result, 0)
        self.assertEqual(captured["market_csv_path"], expected_market)
        self.assertEqual(captured["seeds_5m_csv"], expected_seed)
        self.assertNotEqual(
            captured["seeds_5m_csv"],
            "seeds/5m/btcusdt_5m_long_timing_core_v1.csv",
        )
        self.assertEqual(run_loop.call_args.kwargs["market_csv_path"], expected_market)
        self.assertEqual(run_loop.call_args.kwargs["seeds_5m_csv"], expected_seed)
        self.assertEqual(run_loop.call_args.kwargs["market_csv_path"], captured["market_csv_path"])
        self.assertEqual(run_loop.call_args.kwargs["seeds_5m_csv"], captured["seeds_5m_csv"])

    def test_passed_gate_cli_overrides_reach_runtime_unchanged(self) -> None:
        gate = self._passed_gate()
        observation_gate = SimpleNamespace(
            enabled=True,
            max_records=1,
            observer=SimpleNamespace(close=lambda: None),
        )
        profile = {
            "profile": "PAPER",
            "startup_validation_required": True,
            "reconciliation_required": True,
        }
        startup = SimpleNamespace(passed=True, issues=[])
        environment = {
            "L1_STARTUP_RECOVERY": "1",
            "L1_STARTUP_RECONCILIATION_GATE": "1",
        }
        captured = {}

        def _capture_startup(
            *,
            repo_root,
            market_csv_path: str,
            seeds_5m_csv: str,
            require_wsl: bool,
        ) -> SimpleNamespace:
            captured["market_csv_path"] = market_csv_path
            captured["seeds_5m_csv"] = seeds_5m_csv
            return startup

        market_override = "data/override_market_for_safe_launch.csv"
        seed_override = "seeds/5m/override_seed_path.csv"

        with (
            patch.object(safe_launch, "profile_summary", return_value=profile),
            patch.object(safe_launch, "validate_startup", side_effect=_capture_startup),
            patch.object(safe_launch, "run_reconciliation", return_value=[]),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_runtime_gate",
                return_value=gate,
            ),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_observation_gate",
                return_value=observation_gate,
            ),
            patch.object(
                safe_launch,
                "run_l1_loop_step1234567",
                return_value=0,
            ) as run_loop,
            patch.dict(safe_launch.os.environ, environment, clear=True),
            patch(
                "sys.argv",
                [
                    "safe_launch.py",
                    "--max-ticks",
                    "1",
                    "--market-csv-path",
                    market_override,
                    "--seeds-5m-csv",
                    seed_override,
                ],
            ),
        ):
            result = safe_launch.main()

        self.assertEqual(result, 0)
        self.assertEqual(captured["market_csv_path"], market_override)
        self.assertEqual(captured["seeds_5m_csv"], seed_override)
        self.assertEqual(run_loop.call_args.kwargs["market_csv_path"], market_override)
        self.assertEqual(run_loop.call_args.kwargs["seeds_5m_csv"], seed_override)

    def test_denied_gate_stops_before_loop(self) -> None:
        profile = {
            "profile": "PAPER",
            "startup_validation_required": True,
            "reconciliation_required": True,
        }
        startup = SimpleNamespace(passed=True, issues=[])
        environment = {
            "L1_STARTUP_RECOVERY": "1",
            "L1_STARTUP_RECONCILIATION_GATE": "1",
        }
        denied = IU4ShadowRuntimeGateError(
            IU4ShadowRuntimeGateReasonCode.GATE_DENIED,
            "test denial",
        )
        output = io.StringIO()
        with (
            patch.object(safe_launch, "profile_summary", return_value=profile),
            patch.object(safe_launch, "validate_startup", return_value=startup),
            patch.object(safe_launch, "run_reconciliation", return_value=[]),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_runtime_gate",
                side_effect=denied,
            ),
            patch.object(safe_launch, "run_l1_loop_step1234567") as run_loop,
            patch.dict(safe_launch.os.environ, environment, clear=True),
            patch("sys.argv", ["safe_launch.py", "--max-ticks", "1"]),
            redirect_stdout(output),
        ):
            result = safe_launch.main()

        self.assertEqual(result, 1)
        run_loop.assert_not_called()
        self.assertIn("FAILED_STEP: iu4_shadow_runtime_gate", output.getvalue())

    def test_denied_observation_gate_stops_before_loop(self) -> None:
        profile = {
            "profile": "PAPER",
            "startup_validation_required": True,
            "reconciliation_required": True,
        }
        startup = SimpleNamespace(passed=True, issues=[])
        environment = {
            "L1_STARTUP_RECOVERY": "1",
            "L1_STARTUP_RECONCILIATION_GATE": "1",
        }
        denied = IU4ShadowObservationError(
            IU4ShadowObservationReasonCode.CONFIG_INVALID,
            "test denial",
        )
        output = io.StringIO()
        with (
            patch.object(safe_launch, "profile_summary", return_value=profile),
            patch.object(safe_launch, "validate_startup", return_value=startup),
            patch.object(safe_launch, "run_reconciliation", return_value=[]),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_runtime_gate",
                return_value=self._passed_gate(),
            ),
            patch.object(
                safe_launch,
                "evaluate_iu4_shadow_observation_gate",
                side_effect=denied,
            ),
            patch.object(safe_launch, "run_l1_loop_step1234567") as run_loop,
            patch.dict(safe_launch.os.environ, environment, clear=True),
            patch("sys.argv", ["safe_launch.py", "--max-ticks", "1"]),
            redirect_stdout(output),
        ):
            result = safe_launch.main()

        self.assertEqual(result, 1)
        run_loop.assert_not_called()
        self.assertIn("FAILED_STEP: iu4_shadow_observation_gate", output.getvalue())


if __name__ == "__main__":
    unittest.main()
