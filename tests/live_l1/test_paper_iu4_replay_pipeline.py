#!/usr/bin/env python3

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from live_l1.core import loop
from live_l1.core.paper_entry_throttle import PaperEntryThrottleState
from live_l1.core.paper_iu4_startup_gate import (
    IU4StartupModeRequestV1,
    MODE_SHADOW,
    evaluate_iu4_startup_gate,
)
from live_l1.state.paper_artifacts import PaperAccountState, PositionStateS2FlatV2
from live_l1.state.paper_atomic_coordinator import PaperAtomicCoordinator
from live_l1.tools.paper_iu4_replay_input import IU4ReplayInputBuilderError
from live_l1.tools.paper_iu4_replay_pipeline import (
    IU4ReplayPipelineError,
    IU4ReplayPipelineReasonCode,
    run_iu4_replay_pipeline_smoke,
)
from tests.live_l1.test_paper_economics_shadow_runtime import accepted_environment
from tests.live_l1.test_paper_iu4_adapter import make_config, make_policy


COMMIT_SHA = "a" * 40


class PaperIU4ReplayPipelineSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-iu4-pipeline-")
        self.root = Path(self.temporary_directory)
        self.l1_root = self.root / "l1"
        self.artifacts = self.root / "artifacts"
        self.atomic_root = self.root / "atomic-source"
        self.artifacts.mkdir()
        self._generate_real_l1_log()

        self.config = make_config()
        self.policy = make_policy()
        self.coordinator = PaperAtomicCoordinator(
            self.atomic_root,
            self.config,
            self.policy,
            coordinator_id="IU4-PIPELINE-BTCUSDT",
            symbol="BTCUSDT",
        )
        self.coordinator.initialize(
            position=PositionStateS2FlatV2(
                schema_version=2,
                system_state_id="SYSTEM-0",
                symbol="BTCUSDT",
                position="FLAT",
                side="",
                last_closed_trade_id="",
                economics_profile_id=self.config.economics_profile_id,
                economics_model_version=self.config.economics_model_version,
                config_fingerprint=self.config.config_fingerprint,
            ),
            account=PaperAccountState.initial(
                account_id="PAPER-IU4-PIPELINE",
                quote_currency=self.config.quote_currency,
                starting_equity_quote=self.config.starting_equity_quote,
                utc_day="2026-08-09",
                economics_profile_id=self.config.economics_profile_id,
                economics_model_version=self.config.economics_model_version,
                config_fingerprint=self.config.config_fingerprint,
            ),
            throttle=PaperEntryThrottleState.initial(
                self.policy,
                utc_day="2026-08-09",
            ),
        )
        request = IU4StartupModeRequestV1(
            schema_version=1,
            mode=MODE_SHADOW,
            startup_timestamp_utc="2026-08-09T09:00:00Z",
            operational_profile="PAPER",
            startup_recovery_enabled=False,
            reconciliation_gate_enabled=True,
            repository_commit_sha=COMMIT_SHA,
            expected_coordinator_id=self.coordinator.coordinator_id,
            expected_symbol=self.coordinator.symbol,
            expected_economics_profile_id=self.config.economics_profile_id,
            expected_economics_model_version=self.config.economics_model_version,
            expected_economics_config_fingerprint=self.config.config_fingerprint,
            expected_throttle_policy_profile_id=self.policy.policy_profile_id,
            expected_throttle_policy_model_version=self.policy.policy_model_version,
            expected_throttle_policy_fingerprint=self.policy.policy_fingerprint,
            authorization=None,
        )
        self.gate = evaluate_iu4_startup_gate(
            request,
            self.coordinator,
            running_repository_commit_sha=COMMIT_SHA,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    def _generate_real_l1_log(self) -> None:
        (self.l1_root / "data").mkdir(parents=True)
        (self.l1_root / "seeds" / "5m").mkdir(parents=True)
        (self.l1_root / "live_state").mkdir()
        (self.l1_root / "live_logs").mkdir()
        (self.l1_root / "data" / "market.csv").write_text(
            "timestamp_utc,open,high,low,close,volume,allow_long,allow_short,regime_v2\n"
            "2026-08-09T10:00:00Z,100,100,100,100,1,1,1,0\n"
            "2026-08-09T10:01:00Z,110,110,110,110,1,1,1,0\n"
            "2026-08-09T10:02:00Z,105,105,105,105,1,1,1,0\n",
            encoding="utf-8",
        )
        (self.l1_root / "seeds" / "5m" / "seeds.csv").write_text(
            "seed_id,comb_json,direction\n",
            encoding="utf-8",
        )
        environment = {
            "L1_LOG_PATH": str(self.l1_root / "live_logs" / "l1.log"),
            "L1_MARKET_CSV_PATH": "data/market.csv",
            "SEEDS_5M_CSV": "seeds/5m/seeds.csv",
            "L1_DECISION_TICK_SECONDS": "0",
            "L1_REQUIRE_WSL": "0",
            "L1_TEST_FORCE_INTENTS": "1",
            "L1_TEST_FORCE_BUY_EVERY": "1",
            "L1_TEST_FORCE_SELL_EVERY": "2",
            "L1_TEST_FORCE_WARMUP_TICKS": "0",
            "L1_AUDIT_LOG_PATH": str(self.l1_root / "live_logs" / "execution.jsonl"),
            "L1_TRADE_LOG_PATH": str(self.l1_root / "live_logs" / "trades.jsonl"),
            "L1_LOSS_CLUSTER_STATE_PATH": str(
                self.l1_root / "live_state" / "loss_cluster.json"
            ),
            **accepted_environment(),
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            with contextlib.redirect_stdout(io.StringIO()):
                result = loop.run_l1_loop_step1234567(
                    str(self.l1_root),
                    max_ticks=3,
                )
        if result != 0:
            raise AssertionError(f"real L1 smoke fixture failed with {result}")
        self.source_log = self.l1_root / "live_logs" / "l1.log"

    def _pipeline_arguments(self) -> dict[str, object]:
        return {
            "source_log_path": self.source_log,
            "replay_output_path": self.artifacts / "replay.jsonl",
            "replay_manifest_path": self.artifacts / "replay.manifest.json",
            "replay_evidence_path": self.artifacts / "replay.evidence.json",
            "pipeline_receipt_path": self.artifacts / "pipeline.receipt.json",
            "source_coordinator": self.coordinator,
            "shadow_gate_decision": self.gate,
            "reference_stop_rate": "0.015",
            "replay_id": "IU4-X1-PIPELINE-SMOKE-20260809",
            "generated_at_utc": "2026-08-09T15:00:00Z",
        }

    def _source_bytes(self) -> dict[str, bytes]:
        paths = [self.coordinator.state_path]
        paths.extend(sorted(self.coordinator.transaction_directory.glob("*.json")))
        return {
            path.relative_to(self.atomic_root).as_posix(): path.read_bytes()
            for path in paths
        }

    def test_real_l1_log_reaches_complete_shadow_evidence_chain(self) -> None:
        before_log = self.source_log.read_bytes()
        before_atomic = self._source_bytes()
        result = run_iu4_replay_pipeline_smoke(**self._pipeline_arguments())

        self.assertTrue(result.receipt_newly_written)
        self.assertEqual(self.source_log.read_bytes(), before_log)
        self.assertEqual(self._source_bytes(), before_atomic)
        evidence = json.loads(
            (self.artifacts / "replay.evidence.json").read_text(encoding="utf-8")
        )
        self.assertEqual(evidence["validation"]["step_count"], 3)
        self.assertEqual(evidence["validation"]["committed_step_count"], 3)
        self.assertEqual(evidence["validation"]["simulated_transaction_count"], 3)
        self.assertEqual(
            [outcome["action"] for outcome in evidence["outcomes"]],
            ["OPEN_LONG", "CLOSE_LONG", "OPEN_LONG"],
        )
        self.assertEqual(self.coordinator.load_state().position.position, "FLAT")

    def test_receipt_binds_every_hash_and_keeps_all_activation_flags_false(self) -> None:
        result = run_iu4_replay_pipeline_smoke(**self._pipeline_arguments())
        receipt_path = self.artifacts / "pipeline.receipt.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        fingerprint = receipt.pop("receipt_fingerprint")
        canonical = json.dumps(
            receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")

        self.assertEqual(fingerprint, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(
            result.receipt_sha256,
            hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        )
        self.assertTrue(all(receipt["chain_checks"].values()))
        self.assertFalse(receipt["iu4_enforced_enabled"])
        self.assertFalse(receipt["exchange_enabled"])
        self.assertFalse(receipt["live_enabled"])
        for name in ("replay", "input_manifest", "evidence"):
            artifact = receipt["artifacts"][name]
            path = self.artifacts / artifact["logical_name"]
            self.assertEqual(artifact["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_identical_pipeline_rerun_is_fully_idempotent(self) -> None:
        arguments = self._pipeline_arguments()
        first = run_iu4_replay_pipeline_smoke(**arguments)
        paths = tuple(
            self.artifacts / name
            for name in (
                "replay.jsonl",
                "replay.manifest.json",
                "replay.evidence.json",
                "pipeline.receipt.json",
            )
        )
        stats = {path: path.stat() for path in paths}
        second = run_iu4_replay_pipeline_smoke(**arguments)

        self.assertTrue(first.receipt_newly_written)
        self.assertTrue(second.input_build.replay.already_exists)
        self.assertTrue(second.input_build.manifest_already_exists)
        self.assertTrue(second.evidence_export.already_exists)
        self.assertTrue(second.receipt_already_exists)
        for path in paths:
            self.assertEqual(path.stat().st_ino, stats[path].st_ino)
            self.assertEqual(path.stat().st_mtime_ns, stats[path].st_mtime_ns)

    def test_unsafe_paths_and_conflicting_artifact_fail_closed(self) -> None:
        arguments = self._pipeline_arguments()
        arguments["pipeline_receipt_path"] = self.atomic_root / "unsafe.json"
        with self.assertRaises(IU4ReplayPipelineError) as unsafe:
            run_iu4_replay_pipeline_smoke(**arguments)
        self.assertEqual(
            unsafe.exception.reason_code,
            IU4ReplayPipelineReasonCode.OUTPUT_INVALID,
        )
        self.assertEqual(self.coordinator.load_state().transaction_sequence, 0)

        arguments = self._pipeline_arguments()
        arguments["replay_manifest_path"] = arguments["replay_output_path"]
        with self.assertRaises(IU4ReplayPipelineError):
            run_iu4_replay_pipeline_smoke(**arguments)

        foreign = self.artifacts / "replay.jsonl"
        foreign.write_bytes(b"foreign\n")
        before = foreign.read_bytes()
        with self.assertRaises(IU4ReplayInputBuilderError):
            run_iu4_replay_pipeline_smoke(**self._pipeline_arguments())
        self.assertEqual(foreign.read_bytes(), before)
        self.assertEqual(self.coordinator.load_state().transaction_sequence, 0)


if __name__ == "__main__":
    unittest.main()
