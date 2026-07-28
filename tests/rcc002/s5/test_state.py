"""Checkpoint-state tests for RCC-002 S5."""

from __future__ import annotations

import dataclasses
import json
import unittest

from rcc002.s5.constants import (
    REGIME_STATE_SCHEMA_REF,
    RegimeState,
)
from rcc002.s5.state import (
    compute_state_hash,
    make_state_snapshot,
)


def _snapshot():
    return make_state_snapshot(
        parent_build_id="build-1",
        market_type="spot",
        symbol="BTCUSDT",
        interval="1m",
        last_open_time=60_000,
        market_segment_id="market-1",
        indicator_segment_id="indicator-1",
        sma200_context_state=(99.0, 100.0),
        regime_effective=RegimeState.BULL,
        regime_candidate=RegimeState.BEAR,
        regime_candidate_count=2,
    )


class TestStateSnapshot(unittest.TestCase):
    def test_snapshot_has_checksum(self) -> None:
        snapshot = _snapshot()
        self.assertEqual(len(snapshot.state_payload_sha256), 64)
        self.assertEqual(
            snapshot.state_payload_sha256,
            compute_state_hash(snapshot),
        )

    def test_hash_is_lowercase_hex(self) -> None:
        checksum = _snapshot().state_payload_sha256
        self.assertEqual(checksum, checksum.lower())
        int(checksum, 16)

    def test_state_schema_ref(self) -> None:
        self.assertEqual(
            _snapshot().state_schema_ref, REGIME_STATE_SCHEMA_REF
        )

    def test_hash_changes_with_payload(self) -> None:
        first = _snapshot()
        second = make_state_snapshot(
            parent_build_id="build-2",
            market_type=first.market_type,
            symbol=first.symbol,
            interval=first.interval,
            last_open_time=first.last_open_time,
            market_segment_id=first.market_segment_id,
            indicator_segment_id=first.indicator_segment_id,
            sma200_context_state=first.sma200_context_state,
            regime_effective=first.regime_effective,
            regime_candidate=first.regime_candidate,
            regime_candidate_count=first.regime_candidate_count,
        )
        self.assertNotEqual(
            first.state_payload_sha256,
            second.state_payload_sha256,
        )

    def test_context_is_immutable_tuple(self) -> None:
        self.assertIsInstance(_snapshot().sma200_context_state, tuple)

    def test_context_over_1440_rejected(self) -> None:
        snapshot = _snapshot()
        with self.assertRaises(ValueError):
            dataclasses.replace(
                snapshot,
                sma200_context_state=(1.0,) * 1_441,
            )

    def test_nonfinite_context_rejected(self) -> None:
        snapshot = _snapshot()
        with self.assertRaises(ValueError):
            dataclasses.replace(
                snapshot,
                sma200_context_state=(float("nan"),),
            )

    def test_candidate_count_above_three_not_persistable(self) -> None:
        snapshot = _snapshot()
        with self.assertRaises(ValueError):
            dataclasses.replace(
                snapshot,
                regime_candidate_count=4,
            )

    def test_wrong_checksum_rejected(self) -> None:
        snapshot = _snapshot()
        with self.assertRaises(ValueError):
            dataclasses.replace(
                snapshot, state_payload_sha256="0" * 64
            )

    def test_hash_matches_independent_canonical_json(self) -> None:
        snapshot = _snapshot()
        payload = {
            field.name: getattr(snapshot, field.name)
            for field in dataclasses.fields(snapshot)
            if field.name != "state_payload_sha256"
        }
        payload["regime_effective"] = snapshot.regime_effective.value
        payload["regime_candidate"] = snapshot.regime_candidate.value
        payload["sma200_context_state"] = list(
            snapshot.sma200_context_state
        )
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        import hashlib
        expected = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
        self.assertEqual(snapshot.state_payload_sha256, expected)


if __name__ == "__main__":
    unittest.main()
