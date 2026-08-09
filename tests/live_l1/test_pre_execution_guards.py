from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from live_l1.core import loop
from live_l1.core.execution import ExecutionDecision
from live_l1.tools.paper_economics_shadow_sidecar import parse_l1_log_line


def _state(*, kill_level: str = "NONE") -> SimpleNamespace:
    return SimpleNamespace(
        s2_position=SimpleNamespace(
            position="FLAT",
            side="",
            entry_price=None,
            entry_timestamp_utc="",
        ),
        s4_risk=SimpleNamespace(kill_level=kill_level),
    )


def _config(*, gate_mode: str = "auto") -> SimpleNamespace:
    return SimpleNamespace(gate_mode=gate_mode)


class PreExecutionGuardTests(unittest.TestCase):
    def _assert_blocked(
        self,
        *,
        gate_mode: str,
        kill_level: str,
        expected_guard_reason: str,
        expected_execution_reason: str,
        expected_kill_level: str,
    ) -> None:
        state = _state(kill_level=kill_level)

        with mock.patch.object(loop, "apply_paper_execution") as execution:
            decision, guard_reason, kill_level_new = (
                loop._apply_guarded_paper_execution(
                    cfg=_config(gate_mode=gate_mode),
                    state=state,
                    intent_final="BUY",
                    price=100000.0,
                    timestamp_utc="2026-08-09T10:00:00Z",
                )
            )

        execution.assert_not_called()
        self.assertEqual(guard_reason, expected_guard_reason)
        self.assertEqual(kill_level_new, expected_kill_level)
        self.assertEqual(state.s4_risk.kill_level, expected_kill_level)
        self.assertEqual(
            decision,
            ExecutionDecision(
                action="NOOP",
                executed=False,
                position_before="FLAT",
                position_after="FLAT",
                side_after="",
                entry_price=None,
                entry_timestamp_utc="",
                reason=expected_execution_reason,
            ),
        )

    def test_closed_gate_blocks_before_execution(self) -> None:
        self._assert_blocked(
            gate_mode="closed",
            kill_level="NONE",
            expected_guard_reason="guard_gate_closed",
            expected_execution_reason="GUARD_GATE_CLOSED",
            expected_kill_level="HARD",
        )

    def test_hard_kill_level_blocks_before_execution(self) -> None:
        self._assert_blocked(
            gate_mode="auto",
            kill_level="HARD",
            expected_guard_reason="guard_kill_level_block:HARD",
            expected_execution_reason="GUARD_KILL_LEVEL_HARD",
            expected_kill_level="HARD",
        )

    def test_emergency_kill_level_blocks_before_execution(self) -> None:
        self._assert_blocked(
            gate_mode="open",
            kill_level="EMERGENCY",
            expected_guard_reason="guard_kill_level_block:EMERGENCY",
            expected_execution_reason="GUARD_KILL_LEVEL_EMERGENCY",
            expected_kill_level="EMERGENCY",
        )

    def test_allowed_guard_calls_existing_execution_path_once(self) -> None:
        state = _state(kill_level="NONE")
        expected = ExecutionDecision(
            action="OPEN_LONG",
            executed=True,
            position_before="FLAT",
            position_after="LONG",
            side_after="long",
            entry_price=100000.0,
            entry_timestamp_utc="2026-08-09T10:00:00Z",
            reason="BUY_FROM_FLAT",
        )

        with mock.patch.object(
            loop,
            "apply_paper_execution",
            return_value=expected,
        ) as execution:
            decision, guard_reason, kill_level_new = (
                loop._apply_guarded_paper_execution(
                    cfg=_config(gate_mode="auto"),
                    state=state,
                    intent_final="BUY",
                    price=100000.0,
                    timestamp_utc="2026-08-09T10:00:00Z",
                )
            )

        execution.assert_called_once_with(
            state=state,
            intent_final="BUY",
            price=100000.0,
            timestamp_utc="2026-08-09T10:00:00Z",
            position_size=1.0,
        )
        self.assertIs(decision, expected)
        self.assertEqual(guard_reason, "guard_ok")
        self.assertEqual(kill_level_new, "NONE")

    def test_closed_gate_preserves_existing_position_exit_path(self) -> None:
        state = _state(kill_level="NONE")
        state.s2_position.position = "LONG"
        state.s2_position.side = "long"
        expected = ExecutionDecision(
            action="CLOSE_LONG",
            executed=True,
            position_before="LONG",
            position_after="FLAT",
            side_after="",
            entry_price=None,
            entry_timestamp_utc="",
            reason="SELL_CLOSES_LONG",
        )

        with mock.patch.object(
            loop,
            "apply_paper_execution",
            return_value=expected,
        ) as execution:
            decision, guard_reason, kill_level_new = (
                loop._apply_guarded_paper_execution(
                    cfg=_config(gate_mode="closed"),
                    state=state,
                    intent_final="SELL",
                    price=100000.0,
                    timestamp_utc="2026-08-09T10:00:00Z",
                )
            )

        execution.assert_called_once_with(
            state=state,
            intent_final="SELL",
            price=100000.0,
            timestamp_utc="2026-08-09T10:00:00Z",
            position_size=1.0,
        )
        self.assertIs(decision, expected)
        self.assertEqual(guard_reason, "guard_gate_closed")
        self.assertEqual(kill_level_new, "HARD")

    def test_closed_gate_blocks_forced_entry_in_active_loop(self) -> None:
        with tempfile.TemporaryDirectory(prefix="l1-guard-closed-") as root_text:
            root = Path(root_text)
            (root / "data").mkdir()
            (root / "seeds" / "5m").mkdir(parents=True)
            (root / "live_state").mkdir()
            (root / "live_logs").mkdir()
            (root / "data" / "market.csv").write_text(
                "timestamp_utc,open,high,low,close,volume,allow_long,allow_short,regime_v2\n"
                "2026-08-09T10:00:00Z,100000,100000,100000,100000,1,1,1,0\n",
                encoding="utf-8",
            )
            (root / "seeds" / "5m" / "seeds.csv").write_text(
                "seed_id,comb_json,direction\n",
                encoding="utf-8",
            )
            log_path = root / "live_logs" / "l1.log"
            environment = {
                "L1_LOG_PATH": str(log_path),
                "L1_MARKET_CSV_PATH": "data/market.csv",
                "SEEDS_5M_CSV": "seeds/5m/seeds.csv",
                "L1_DECISION_TICK_SECONDS": "0",
                "L1_REQUIRE_WSL": "0",
                "L1_GATE_MODE": "closed",
                "L1_TEST_FORCE_INTENTS": "1",
                "L1_TEST_FORCE_BUY_EVERY": "1",
                "L1_TEST_FORCE_SELL_EVERY": "0",
                "L1_AUDIT_LOG_PATH": str(root / "live_logs" / "execution.jsonl"),
                "L1_TRADE_LOG_PATH": str(root / "live_logs" / "trades.jsonl"),
                "L1_LOSS_CLUSTER_STATE_PATH": str(
                    root / "live_state" / "loss_cluster.json"
                ),
                "PEE_MODE": "OFF",
            }

            with mock.patch.dict(os.environ, environment, clear=True):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = loop.run_l1_loop_step1234567(str(root), max_ticks=1)

            self.assertEqual(result, 0)
            events = [
                parse_l1_log_line(line, number)
                for number, line in enumerate(
                    log_path.read_text(encoding="utf-8").splitlines(),
                    start=1,
                )
            ]
            execution = next(event for event in events if event.event == "execution")
            guard = next(
                event for event in events if event.event == "guard_blocked_execution"
            )
            position = json.loads(
                (root / "live_state" / "s2_position.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )
            risk = json.loads(
                (root / "live_state" / "s4_risk.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )

            self.assertEqual(execution.fields["action"], "NOOP")
            self.assertEqual(execution.fields["executed"], "0")
            self.assertEqual(execution.fields["reason"], "GUARD_GATE_CLOSED")
            self.assertEqual(guard.fields["guard_reason"], "guard_gate_closed")
            self.assertEqual(position["position"], "FLAT")
            self.assertEqual(risk["kill_level"], "HARD")


if __name__ == "__main__":
    unittest.main()
