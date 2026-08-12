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

    def test_passed_gate_is_bound_to_started_loop(self) -> None:
        gate = self._passed_gate()
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


if __name__ == "__main__":
    unittest.main()
