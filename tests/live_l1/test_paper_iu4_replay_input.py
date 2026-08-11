#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from live_l1.tools.paper_iu4_replay_evidence import load_iu4_replay_jsonl
from live_l1.tools.paper_iu4_replay_input import (
    IU4ReplayInputBuilderError,
    IU4ReplayInputBuilderReasonCode,
    build_iu4_replay_input_from_l1_log,
)


class PaperIU4ReplayInputBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.mkdtemp(prefix="pee-iu4-input-")
        self.root = Path(self.temporary_directory)
        self.source = self.root / "l1.log"
        self.output = self.root / "replay.jsonl"
        self.manifest = self.root / "replay.manifest.json"

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary_directory, ignore_errors=True)

    @staticmethod
    def _market(
        *,
        sequence: int,
        state: str,
        tick: int,
        timestamp: str,
        price_text: str,
        include_price_text: bool = True,
    ) -> str:
        fields = [
            f"timestamp_utc=2026-08-09T09:00:{sequence:02d}Z",
            f"seq={sequence}",
            "category=L2",
            "event=market_snapshot",
            "severity=INFO",
            f"system_state_id={state}",
            "price=100.0",
        ]
        if include_price_text:
            fields.append(f"reference_price_text={price_text}")
        fields.extend((f"tick={tick}", f"timestamp_utc={timestamp}"))
        return " ".join(fields)

    @staticmethod
    def _intent(
        *,
        sequence: int,
        state: str,
        tick: int,
        intent: str,
        intent_id: str,
        reason: str = "FUSED_TEST",
    ) -> str:
        return " ".join(
            (
                f"timestamp_utc=2026-08-09T09:01:{sequence:02d}Z",
                f"seq={sequence}",
                "category=L3",
                "event=intent_fused",
                "severity=INFO",
                f"system_state_id={state}",
                f"intent_id={intent_id}",
                f"intent_final={intent}",
                f"reason_code={reason}",
                f"tick={tick}",
            )
        )

    @staticmethod
    def _execution(
        *,
        sequence: int,
        state: str,
        tick: int,
        intent_id: str,
        action: str,
        executed: int,
        reason: str,
    ) -> str:
        return " ".join(
            (
                f"timestamp_utc=2026-08-09T09:02:{sequence:02d}Z",
                f"seq={sequence}",
                "category=L5",
                "event=execution",
                "severity=INFO",
                f"system_state_id={state}",
                f"intent_id={intent_id}",
                f"action={action}",
                f"executed={executed}",
                f"reason={reason}",
                f"tick={tick}",
            )
        )

    def _valid_source(self) -> bytes:
        lines = (
            self._market(
                sequence=1,
                state="STATE-A",
                tick=40,
                timestamp="2026-08-09T10:00:00Z",
                price_text="100.1234567890123456789",
            ),
            self._intent(
                sequence=2,
                state="STATE-A",
                tick=40,
                intent="BUY",
                intent_id="INTENT-1",
            ),
            self._market(
                sequence=3,
                state="STATE-A",
                tick=41,
                timestamp="2026-08-09T10:01:00Z",
                price_text="101",
            ),
            self._intent(
                sequence=4,
                state="STATE-A",
                tick=41,
                intent="HOLD",
                intent_id="INTENT-2",
                reason="HOLD_RAW",
            ),
            self._market(
                sequence=1,
                state="STATE-B",
                tick=1,
                timestamp="2026-08-09T10:02:00Z",
                price_text="102",
            ),
            self._intent(
                sequence=2,
                state="STATE-B",
                tick=1,
                intent="SELL",
                intent_id="INTENT-3",
                reason="EXIT_LONG",
            ),
        )
        return ("\n".join(lines) + "\n").encode("utf-8")

    def _build(self):
        return build_iu4_replay_input_from_l1_log(
            source_path=self.source,
            output_path=self.output,
            manifest_path=self.manifest,
            reference_stop_rate="0.015",
        )

    def test_builds_strict_replay_with_exact_decimal_and_restart_normalization(self) -> None:
        source_bytes = self._valid_source()
        self.source.write_bytes(source_bytes)

        result = self._build()
        replay = load_iu4_replay_jsonl(self.output)

        self.assertTrue(result.replay.newly_written)
        self.assertTrue(result.manifest_newly_written)
        self.assertEqual(self.source.read_bytes(), source_bytes)
        self.assertEqual(result.source_sha256, hashlib.sha256(source_bytes).hexdigest())
        self.assertEqual(result.parsed_event_count, 6)
        self.assertEqual(result.market_event_count, 3)
        self.assertEqual(result.intent_event_count, 3)
        self.assertEqual([step.tick_id for step in replay.steps], [1, 2, 3])
        self.assertEqual(
            replay.steps[0].to_record()["reference_price"],
            "100.1234567890123456789",
        )
        self.assertEqual(
            replay.steps[0].to_record()["reference_stop_price"],
            "98.6216049371771604937165",
        )
        self.assertIsNone(replay.steps[1].reference_stop_price)
        self.assertEqual(replay.steps[1].trade_id, "")
        self.assertEqual(replay.steps[2].to_record()["reference_stop_price"], "103.53")
        self.assertTrue(replay.steps[0].trade_id.startswith("PEE-IU4-TRADE-"))
        self.assertNotEqual(replay.steps[0].trade_id, replay.steps[2].trade_id)

    def test_manifest_binds_source_builder_and_replay_hashes(self) -> None:
        source_bytes = self._valid_source()
        self.source.write_bytes(source_bytes)
        result = self._build()
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))

        fingerprint = manifest.pop("manifest_fingerprint")
        canonical = json.dumps(
            manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
        self.assertEqual(fingerprint, hashlib.sha256(canonical).hexdigest())
        self.assertEqual(manifest["source"]["sha256"], result.source_sha256)
        self.assertEqual(
            manifest["replay"]["sha256"],
            hashlib.sha256(self.output.read_bytes()).hexdigest(),
        )
        self.assertEqual(manifest["builder"]["reference_stop_rate"], "0.015")
        self.assertEqual(
            manifest["builder"]["price_authority"],
            "market_snapshot.reference_price_text",
        )

    def test_autonomous_close_execution_overrides_only_its_joined_hold(self) -> None:
        lines = (
            self._market(
                sequence=1,
                state="STATE-A",
                tick=1,
                timestamp="2026-08-09T10:00:00Z",
                price_text="100",
            ),
            self._intent(
                sequence=2,
                state="STATE-A",
                tick=1,
                intent="BUY",
                intent_id="INTENT-1",
            ),
            self._execution(
                sequence=3,
                state="STATE-A",
                tick=1,
                intent_id="INTENT-1",
                action="OPEN_LONG",
                executed=1,
                reason="BUY_FROM_FLAT",
            ),
            self._market(
                sequence=4,
                state="STATE-A",
                tick=2,
                timestamp="2026-08-09T10:01:00Z",
                price_text="101",
            ),
            self._intent(
                sequence=5,
                state="STATE-A",
                tick=2,
                intent="HOLD",
                intent_id="INTENT-2",
                reason="HOLD_RAW",
            ),
            self._execution(
                sequence=6,
                state="STATE-A",
                tick=2,
                intent_id="INTENT-2",
                action="NOOP",
                executed=0,
                reason="HOLD_NO_EXECUTION",
            ),
            self._market(
                sequence=7,
                state="STATE-A",
                tick=3,
                timestamp="2026-08-09T10:02:00Z",
                price_text="102",
            ),
            self._intent(
                sequence=8,
                state="STATE-A",
                tick=3,
                intent="HOLD",
                intent_id="INTENT-3",
                reason="HOLD_RAW",
            ),
            self._execution(
                sequence=9,
                state="STATE-A",
                tick=3,
                intent_id="INTENT-3",
                action="CLOSE_LONG",
                executed=1,
                reason="LONG_TIME_STOP_HIT",
            ),
        )
        self.source.write_text("\n".join(lines) + "\n", encoding="utf-8")

        result = self._build()
        replay = load_iu4_replay_jsonl(self.output)
        manifest = json.loads(self.manifest.read_text(encoding="utf-8"))

        self.assertEqual(result.execution_event_count, 3)
        self.assertEqual(result.executed_exit_event_count, 1)
        self.assertEqual(result.autonomous_exit_event_count, 1)
        self.assertEqual(
            [step.intent_final for step in replay.steps],
            ["BUY", "HOLD", "SELL"],
        )
        self.assertEqual(replay.steps[1].source_event_kind, "INTENT")
        autonomous = replay.steps[2]
        self.assertEqual(autonomous.schema_version, 2)
        self.assertEqual(
            autonomous.source_event_kind,
            "AUTONOMOUS_EXIT_EXECUTION",
        )
        self.assertEqual(autonomous.source_intent_final, "HOLD")
        self.assertEqual(autonomous.source_execution_action, "CLOSE_LONG")
        self.assertEqual(autonomous.source_execution_sequence, 9)
        self.assertEqual(autonomous.intent_reason_code, "LONG_TIME_STOP_HIT")
        self.assertIsNone(autonomous.reference_stop_price)
        self.assertEqual(autonomous.trade_id, "")
        self.assertEqual(manifest["schema_version"], 2)
        self.assertEqual(manifest["source"]["autonomous_exit_event_count"], 1)

    def test_mismatched_autonomous_execution_fails_closed(self) -> None:
        lines = (
            self._market(
                sequence=1,
                state="STATE-A",
                tick=1,
                timestamp="2026-08-09T10:00:00Z",
                price_text="100",
            ),
            self._intent(
                sequence=2,
                state="STATE-A",
                tick=1,
                intent="HOLD",
                intent_id="INTENT-1",
            ),
            self._execution(
                sequence=3,
                state="STATE-A",
                tick=1,
                intent_id="FOREIGN-INTENT",
                action="CLOSE_LONG",
                executed=1,
                reason="LONG_TIME_STOP_HIT",
            ),
        )
        self.source.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with self.assertRaises(IU4ReplayInputBuilderError) as caught:
            self._build()
        self.assertEqual(
            caught.exception.reason_code,
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
        )
        self.assertFalse(self.output.exists())

    def test_identical_build_is_idempotent_without_rewrite(self) -> None:
        self.source.write_bytes(self._valid_source())
        first = self._build()
        replay_stat = self.output.stat()
        manifest_stat = self.manifest.stat()
        second = self._build()

        self.assertTrue(first.replay.newly_written)
        self.assertTrue(second.replay.already_exists)
        self.assertTrue(second.manifest_already_exists)
        self.assertEqual(self.output.stat().st_ino, replay_stat.st_ino)
        self.assertEqual(self.output.stat().st_mtime_ns, replay_stat.st_mtime_ns)
        self.assertEqual(self.manifest.stat().st_ino, manifest_stat.st_ino)
        self.assertEqual(self.manifest.stat().st_mtime_ns, manifest_stat.st_mtime_ns)

    def test_float_price_is_never_used_as_decimal_authority(self) -> None:
        self.source.write_text(
            self._market(
                sequence=1,
                state="STATE-A",
                tick=1,
                timestamp="2026-08-09T10:00:00Z",
                price_text="",
                include_price_text=False,
            )
            + "\n"
            + self._intent(
                sequence=2,
                state="STATE-A",
                tick=1,
                intent="BUY",
                intent_id="INTENT-1",
            )
            + "\n",
            encoding="utf-8",
        )

        with self.assertRaises(IU4ReplayInputBuilderError) as caught:
            self._build()
        self.assertEqual(
            caught.exception.reason_code,
            IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
        )
        self.assertFalse(self.output.exists())

    def test_malformed_duplicate_and_unpaired_events_fail_closed(self) -> None:
        cases = {
            "malformed": "not-a-structured-log-line\n",
            "unpaired": self._market(
                sequence=1,
                state="STATE-A",
                tick=1,
                timestamp="2026-08-09T10:00:00Z",
                price_text="100",
            )
            + "\n",
            "duplicate": "\n".join(
                (
                    self._market(
                        sequence=1,
                        state="STATE-A",
                        tick=1,
                        timestamp="2026-08-09T10:00:00Z",
                        price_text="100",
                    ),
                    self._market(
                        sequence=2,
                        state="STATE-A",
                        tick=1,
                        timestamp="2026-08-09T10:00:00Z",
                        price_text="100",
                    ),
                )
            )
            + "\n",
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                self.source.write_text(text, encoding="utf-8")
                with self.assertRaises(IU4ReplayInputBuilderError):
                    self._build()
                self.assertFalse(self.output.exists())

    def test_timestamp_regression_and_duplicate_intent_ids_fail_before_publish(self) -> None:
        base = self._valid_source().decode("utf-8").splitlines()
        cases = (
            base[:4]
            + [
                self._market(
                    sequence=5,
                    state="STATE-A",
                    tick=42,
                    timestamp="2026-08-09T09:59:00Z",
                    price_text="102",
                ),
                self._intent(
                    sequence=6,
                    state="STATE-A",
                    tick=42,
                    intent="SELL",
                    intent_id="INTENT-3",
                ),
            ],
            [*base[:3], self._intent(
                sequence=4,
                state="STATE-A",
                tick=41,
                intent="HOLD",
                intent_id="INTENT-1",
            )],
        )
        for index, lines in enumerate(cases):
            with self.subTest(index=index):
                self.source.write_text("\n".join(lines) + "\n", encoding="utf-8")
                with self.assertRaises(IU4ReplayInputBuilderError) as caught:
                    self._build()
                self.assertEqual(
                    caught.exception.reason_code,
                    IU4ReplayInputBuilderReasonCode.EVENT_INVALID,
                )
                self.assertFalse(self.output.exists())

    def test_invalid_config_paths_and_conflicts_are_rejected(self) -> None:
        self.source.write_bytes(self._valid_source())
        for rate in ("", "0", "1", "NaN", "0.1x"):
            with self.subTest(rate=rate):
                with self.assertRaises(IU4ReplayInputBuilderError):
                    build_iu4_replay_input_from_l1_log(
                        source_path=self.source,
                        output_path=self.output,
                        manifest_path=self.manifest,
                        reference_stop_rate=rate,
                    )
        with self.assertRaises(IU4ReplayInputBuilderError):
            build_iu4_replay_input_from_l1_log(
                source_path=self.source,
                output_path=self.source,
                manifest_path=self.manifest,
                reference_stop_rate="0.015",
            )

        replay_link = self.root / "replay-link.jsonl"
        replay_link.symlink_to(self.root / "missing.jsonl")
        with self.assertRaises(IU4ReplayInputBuilderError) as linked:
            build_iu4_replay_input_from_l1_log(
                source_path=self.source,
                output_path=replay_link,
                manifest_path=self.manifest,
                reference_stop_rate="0.015",
            )
        self.assertEqual(
            linked.exception.reason_code,
            IU4ReplayInputBuilderReasonCode.OUTPUT_INVALID,
        )

        self.output.write_bytes(b"foreign\n")
        before = self.output.read_bytes()
        with self.assertRaises(IU4ReplayInputBuilderError) as conflict:
            self._build()
        self.assertEqual(
            conflict.exception.reason_code,
            IU4ReplayInputBuilderReasonCode.OUTPUT_CONFLICT,
        )
        self.assertEqual(self.output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
