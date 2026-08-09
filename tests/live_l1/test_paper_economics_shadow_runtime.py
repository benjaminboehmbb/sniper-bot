from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from live_l1.core import loop
from live_l1.core.paper_economics_shadow import MODE_OFF
from live_l1.core.paper_economics_shadow import SHADOW_REFERENCE_PRICE_MISSING
from live_l1.core.paper_economics_shadow_runtime import (
    SHADOW_PARITY_UNKNOWN,
    SHADOW_RUNTIME_ERROR,
    build_runtime_shadow_log_fields,
    load_runtime_shadow_settings,
    observe_runtime_shadow,
    shadow_startup_log_fields,
)
from live_l1.tools.paper_economics_shadow_sidecar import parse_l1_log_line


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


def accepted_environment() -> dict[str, str]:
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("accepted profile must be a JSON object")
    return {str(key): str(value) for key, value in payload.items()}


def candidate_attempt(settings):
    return observe_runtime_shadow(
        settings=settings,
        current_position="FLAT",
        intent_final="BUY",
        reference_entry_price="100000",
        tick_id=7,
        snapshot_id="SNAP-7",
        timestamp_utc="2026-08-06T10:00:00Z",
        intent_id="INTENT-7",
    )


class RecordingLogger:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[dict[str, object]] = []

    def log(self, **kwargs: object) -> None:
        self.calls.append(dict(kwargs))
        if self.fail:
            raise RuntimeError("simulated shadow log failure")


class RuntimeShadowBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.settings = load_runtime_shadow_settings(accepted_environment())
        self.assertTrue(self.settings.ready)

    def test_startup_fields_pin_the_accepted_profile_identity(self) -> None:
        fields = shadow_startup_log_fields(self.settings)

        self.assertEqual(fields["pee_shadow_mode"], "SHADOW")
        self.assertEqual(fields["pee_shadow_ready"], 1)
        self.assertEqual(
            fields["pee_economics_profile_id"],
            "PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001",
        )
        self.assertEqual(fields["pee_economics_model_version"], "PEE_V1")
        self.assertEqual(fields["pee_config_fingerprint"], EXPECTED_FINGERPRINT)

    def test_candidate_audit_contains_quote_identity_and_legacy_outcome(self) -> None:
        attempt = candidate_attempt(self.settings)
        fields = build_runtime_shadow_log_fields(
            attempt,
            settings=self.settings,
            legacy_action="OPEN_LONG",
            legacy_executed=True,
            legacy_position_before="FLAT",
            legacy_position_after="LONG",
        )

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual(fields["shadow_only"], 1)
        self.assertEqual(fields["legacy_action"], "OPEN_LONG")
        self.assertEqual(fields["legacy_executed"], 1)
        self.assertEqual(
            fields["parity_code"],
            "PEE_SHADOW_LEGACY_EXECUTED_PEE_ALLOWED",
        )
        self.assertEqual(fields["config_fingerprint"], EXPECTED_FINGERPRINT)
        self.assertEqual(fields["economics_model_version"], "PEE_V1")
        self.assertNotIn("allow_execution", fields)
        self.assertNotIn("position_size", fields)

    def test_off_and_non_candidate_paths_emit_no_shadow_dataset(self) -> None:
        off_settings = load_runtime_shadow_settings({})
        self.assertEqual(off_settings.mode, MODE_OFF)
        self.assertEqual(shadow_startup_log_fields(off_settings), {})
        off_attempt = candidate_attempt(off_settings)
        non_candidate = observe_runtime_shadow(
            settings=self.settings,
            current_position="LONG",
            intent_final="SELL",
            reference_entry_price="100000",
            tick_id=8,
            snapshot_id="SNAP-8",
            timestamp_utc="2026-08-06T10:01:00Z",
            intent_id="INTENT-8",
        )

        for attempt, settings in (
            (off_attempt, off_settings),
            (non_candidate, self.settings),
        ):
            fields = build_runtime_shadow_log_fields(
                attempt,
                settings=settings,
                legacy_action="NOOP",
                legacy_executed=False,
                legacy_position_before="FLAT",
                legacy_position_after="FLAT",
            )
            self.assertIsNone(fields)

    def test_unexpected_observation_error_becomes_audit_not_control(self) -> None:
        with mock.patch(
            "live_l1.core.paper_economics_shadow_runtime.observe_shadow_entry_candidate",
            side_effect=RuntimeError("simulated calculation failure"),
        ):
            attempt = candidate_attempt(self.settings)

        fields = build_runtime_shadow_log_fields(
            attempt,
            settings=self.settings,
            legacy_action="OPEN_LONG",
            legacy_executed=True,
            legacy_position_before="FLAT",
            legacy_position_after="LONG",
        )

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual(fields["pee_reason_code"], SHADOW_RUNTIME_ERROR)
        self.assertEqual(fields["parity_code"], SHADOW_PARITY_UNKNOWN)
        self.assertEqual(fields["legacy_executed"], 1)
        self.assertEqual(fields["config_fingerprint"], EXPECTED_FINGERPRINT)

    def test_missing_canonical_price_is_logged_fail_closed_without_control(self) -> None:
        attempt = observe_runtime_shadow(
            settings=self.settings,
            current_position="FLAT",
            intent_final="BUY",
            reference_entry_price="",
            tick_id=11,
            snapshot_id="SNAP-11",
            timestamp_utc="2026-08-06T10:03:00Z",
            intent_id="INTENT-11",
        )
        fields = build_runtime_shadow_log_fields(
            attempt,
            settings=self.settings,
            legacy_action="OPEN_LONG",
            legacy_executed=True,
            legacy_position_before="FLAT",
            legacy_position_after="LONG",
        )

        self.assertIsNotNone(fields)
        assert fields is not None
        self.assertEqual(fields["pee_allowed"], 0)
        self.assertEqual(
            fields["pee_reason_code"],
            SHADOW_REFERENCE_PRICE_MISSING,
        )
        self.assertEqual(fields["config_fingerprint"], EXPECTED_FINGERPRINT)
        self.assertEqual(
            fields["parity_code"],
            "PEE_SHADOW_LEGACY_EXECUTED_PEE_REJECTED",
        )
        self.assertEqual(fields["legacy_executed"], 1)
        self.assertNotIn("allow_execution", fields)

    def test_active_loop_passes_exact_canonical_carrier_to_shadow(self) -> None:
        exact_price = "12345.678901234567890123456789"
        with tempfile.TemporaryDirectory(prefix="pee-canonical-boundary-") as root_text:
            root = Path(root_text)
            (root / "data").mkdir()
            (root / "seeds" / "5m").mkdir(parents=True)
            (root / "live_state").mkdir()
            (root / "live_logs").mkdir()
            (root / "data" / "market.csv").write_text(
                "timestamp_utc,open,high,low,close,volume\n"
                f"2026-08-06T10:00:00Z,{exact_price},{exact_price},"
                f"{exact_price},{exact_price},1\n",
                encoding="utf-8",
            )
            (root / "seeds" / "5m" / "seeds.csv").write_text(
                "seed_id,comb_json,direction\n",
                encoding="utf-8",
            )
            environment = {
                "L1_LOG_PATH": str(root / "live_logs" / "l1.log"),
                "L1_MARKET_CSV_PATH": "data/market.csv",
                "SEEDS_5M_CSV": "seeds/5m/seeds.csv",
                "L1_DECISION_TICK_SECONDS": "0",
                "L1_REQUIRE_WSL": "0",
                "L1_TEST_FORCE_INTENTS": "1",
                "L1_TEST_FORCE_BUY_EVERY": "1",
                "L1_TEST_FORCE_WARMUP_TICKS": "0",
                "L1_AUDIT_LOG_PATH": str(root / "live_logs" / "execution.jsonl"),
                "L1_TRADE_LOG_PATH": str(root / "live_logs" / "trades.jsonl"),
                "L1_LOSS_CLUSTER_STATE_PATH": str(
                    root / "live_state" / "loss_cluster.json"
                ),
                **accepted_environment(),
            }

            with mock.patch.dict(os.environ, environment, clear=True):
                with mock.patch.object(
                    loop,
                    "_observe_pee_shadow_fail_safe",
                    return_value=None,
                ) as shadow_observer:
                    with contextlib.redirect_stdout(io.StringIO()):
                        result = loop.run_l1_loop_step1234567(
                            str(root),
                            max_ticks=1,
                        )

        self.assertEqual(result, 0)
        self.assertEqual(shadow_observer.call_count, 1)
        self.assertEqual(
            shadow_observer.call_args.kwargs["reference_entry_price"],
            exact_price,
        )

    def test_loop_boundary_swallows_shadow_calculation_and_logging_failures(self) -> None:
        with mock.patch.object(
            loop,
            "observe_runtime_shadow",
            side_effect=RuntimeError("simulated bridge failure"),
        ):
            attempt = loop._observe_pee_shadow_fail_safe(
                settings=self.settings,
                current_position="FLAT",
                intent_final="BUY",
                reference_entry_price="100000",
                tick_id=9,
                snapshot_id="SNAP-9",
                timestamp_utc="2026-08-06T10:02:00Z",
                intent_id="INTENT-9",
            )
        self.assertIsNone(attempt)

        logger = RecordingLogger(fail=True)
        loop._log_pee_shadow_fail_safe(
            log=logger,
            attempt=candidate_attempt(self.settings),
            settings=self.settings,
            system_state_id="STATE-9",
            intent_id="INTENT-9",
            legacy_action="OPEN_LONG",
            legacy_executed=True,
            legacy_position_before="FLAT",
            legacy_position_after="LONG",
        )
        self.assertEqual(len(logger.calls), 1)

    def test_active_loop_off_and_shadow_preserve_identical_legacy_path(self) -> None:
        def run_once(root: Path, pee_environment: dict[str, str]):
            (root / "data").mkdir(parents=True)
            (root / "seeds" / "5m").mkdir(parents=True)
            (root / "live_state").mkdir()
            (root / "live_logs").mkdir()
            market_path = root / "data" / "market.csv"
            market_path.write_text(
                "timestamp_utc,open,high,low,close,volume,allow_long,allow_short,regime_v2\n"
                "2026-08-06T10:00:00Z,100000,100000,100000,100000,1,1,1,0\n"
                "2026-08-06T10:01:00Z,100100,100100,100100,100100,1,1,1,0\n",
                encoding="utf-8",
            )
            seed_path = root / "seeds" / "5m" / "seeds.csv"
            seed_path.write_text("seed_id,comb_json,direction\n", encoding="utf-8")
            log_path = root / "live_logs" / "l1.log"
            environment = {
                "L1_LOG_PATH": str(log_path),
                "L1_MARKET_CSV_PATH": "data/market.csv",
                "SEEDS_5M_CSV": "seeds/5m/seeds.csv",
                "L1_DECISION_TICK_SECONDS": "0",
                "L1_REQUIRE_WSL": "0",
                "L1_TEST_FORCE_INTENTS": "1",
                "L1_TEST_FORCE_BUY_EVERY": "1",
                "L1_TEST_FORCE_SELL_EVERY": "2",
                "L1_TEST_FORCE_WARMUP_TICKS": "0",
                "L1_AUDIT_LOG_PATH": str(root / "live_logs" / "execution.jsonl"),
                "L1_TRADE_LOG_PATH": str(root / "live_logs" / "trades.jsonl"),
                "L1_LOSS_CLUSTER_STATE_PATH": str(
                    root / "live_state" / "loss_cluster.json"
                ),
            }
            environment.update(pee_environment)

            with mock.patch.dict(os.environ, environment, clear=True):
                with contextlib.redirect_stdout(io.StringIO()):
                    result = loop.run_l1_loop_step1234567(str(root), max_ticks=2)
            self.assertEqual(result, 0)

            events = [
                parse_l1_log_line(line, number)
                for number, line in enumerate(
                    log_path.read_text(encoding="utf-8").splitlines(),
                    start=1,
                )
            ]
            state_record = json.loads(
                (root / "live_state" / "s2_position.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )
            risk_record = json.loads(
                (root / "live_state" / "s4_risk.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()[-1]
            )
            return events, state_record, risk_record

        with tempfile.TemporaryDirectory(prefix="pee-loop-off-") as off_root_text:
            off_events, off_state, off_risk = run_once(
                Path(off_root_text),
                {"PEE_MODE": "OFF"},
            )
        with tempfile.TemporaryDirectory(prefix="pee-loop-shadow-") as shadow_root_text:
            shadow_events, shadow_state, shadow_risk = run_once(
                Path(shadow_root_text),
                accepted_environment(),
            )

        off_legacy_path = [
            (event.category, event.event)
            for event in off_events
            if event.category != "PEE"
        ]
        shadow_legacy_path = [
            (event.category, event.event)
            for event in shadow_events
            if event.category != "PEE"
        ]
        self.assertEqual(shadow_legacy_path, off_legacy_path)

        state_fields = (
            "position",
            "side",
            "size",
            "position_size",
            "entry_price",
            "entry_timestamp_utc",
            "last_snapshot_id",
            "last_timestamp_utc",
            "last_tick_id",
        )
        self.assertEqual(
            {name: shadow_state[name] for name in state_fields},
            {name: off_state[name] for name in state_fields},
        )
        risk_fields = (
            "kill_level",
            "cooldown_until_utc",
            "trades_6h",
            "trades_today",
            "last_trade_timestamp_utc",
        )
        self.assertEqual(
            {name: shadow_risk[name] for name in risk_fields},
            {name: off_risk[name] for name in risk_fields},
        )

        off_intents = [event for event in off_events if event.event == "intent_fused"]
        shadow_intents = [
            event for event in shadow_events if event.event == "intent_fused"
        ]
        intent_fields = (
            "intent_1m_raw",
            "intent_final",
            "reason_code",
            "current_position",
            "test_forced_intent",
        )
        self.assertEqual(
            [
                {name: event.fields[name] for name in intent_fields}
                for event in shadow_intents
            ],
            [
                {name: event.fields[name] for name in intent_fields}
                for event in off_intents
            ],
        )

        off_executions = [event for event in off_events if event.event == "execution"]
        shadow_executions = [
            event for event in shadow_events if event.event == "execution"
        ]
        execution_fields = (
            "action",
            "executed",
            "position_before",
            "position_after",
            "side_after",
            "entry_price",
            "entry_timestamp_utc",
            "reason",
        )
        self.assertEqual(
            [
                {name: event.fields[name] for name in execution_fields}
                for event in shadow_executions
            ],
            [
                {name: event.fields[name] for name in execution_fields}
                for event in off_executions
            ],
        )
        self.assertEqual(
            [event.fields["action"] for event in shadow_executions],
            ["OPEN_LONG", "CLOSE_LONG"],
        )

        self.assertFalse(any(event.category == "PEE" for event in off_events))
        shadow_audits = [event for event in shadow_events if event.category == "PEE"]
        self.assertEqual(len(shadow_audits), 1)
        self.assertEqual(
            shadow_audits[0].fields["config_fingerprint"],
            EXPECTED_FINGERPRINT,
        )

    def test_restart_uses_new_system_state_id_and_resumes_next_snapshot(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pee-loop-restart-") as root_text:
            root = Path(root_text)
            (root / "data").mkdir()
            (root / "seeds" / "5m").mkdir(parents=True)
            (root / "live_state").mkdir()
            (root / "live_logs").mkdir()
            (root / "data" / "market.csv").write_text(
                "timestamp_utc,open,high,low,close,volume\n"
                "2026-08-06T10:00:00Z,100000,100000,100000,100000,1\n"
                "2026-08-06T10:01:00Z,100100,100100,100100,100100,1\n",
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
                "L1_AUDIT_LOG_PATH": str(root / "live_logs" / "execution.jsonl"),
                "L1_TRADE_LOG_PATH": str(root / "live_logs" / "trades.jsonl"),
                "L1_LOSS_CLUSTER_STATE_PATH": str(
                    root / "live_state" / "loss_cluster.json"
                ),
                **accepted_environment(),
            }

            with mock.patch.dict(os.environ, environment, clear=True):
                with contextlib.redirect_stdout(io.StringIO()):
                    first_rc = loop.run_l1_loop_step1234567(
                        str(root),
                        max_ticks=1,
                    )
                    second_rc = loop.run_l1_loop_step1234567(
                        str(root),
                        max_ticks=1,
                    )

            self.assertEqual((first_rc, second_rc), (0, 0))
            events = [
                parse_l1_log_line(line, number)
                for number, line in enumerate(
                    log_path.read_text(encoding="utf-8").splitlines(),
                    start=1,
                )
            ]
            starts = [event for event in events if event.event == "system_start"]
            markets = [event for event in events if event.event == "market_snapshot"]

            self.assertEqual(len(starts), 2)
            self.assertNotEqual(starts[0].system_state_id, starts[1].system_state_id)
            self.assertEqual(starts[0].fields["resume_after_snapshot_id"], "")
            self.assertEqual(
                starts[1].fields["resume_after_snapshot_id"],
                "CSV-00000001",
            )
            self.assertEqual(
                [event.fields["snapshot_id"] for event in markets],
                ["CSV-00000001", "CSV-00000002"],
            )


if __name__ == "__main__":
    unittest.main()
