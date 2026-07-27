"""Unit tests for rcc002.s3.state."""

import dataclasses
import unittest

from rcc002.s3.state import IndicatorStateSnapshot, compute_state_checksum, is_state_usable


def make_state(**overrides: object) -> IndicatorStateSnapshot:
    fields: dict[str, object] = dict(
        last_canonical_key=("spot", "BTCUSDT", "1m", 0),
        market_segment_id="m1",
        indicator_segment_id="i1",
        indicator_profile_id="RCC002_CANONICAL_INDICATORS_V1",
        indicator_profile_version="1.0.0",
        ema_states={"ema_close_50": 100.0},
        rsi_avg_gain=1.0,
        rsi_avg_loss=1.0,
        atr_state=2.0,
        obv_state=0.0,
        adx_tr_sum=10.0,
        adx_plus_dm_sum=5.0,
        adx_minus_dm_sum=5.0,
        adx_state=20.0,
        previous_ohlc={"close": 100.0, "high": 101.0, "low": 99.0},
        warmup_buffers={},
        warmup_counters={},
    )
    fields.update(overrides)
    return IndicatorStateSnapshot(**fields)  # type: ignore[arg-type]


class ChecksumTests(unittest.TestCase):
    def test_deterministic(self) -> None:
        state = make_state()
        self.assertEqual(compute_state_checksum(state), compute_state_checksum(state))

    def test_distinct_for_distinct_state(self) -> None:
        a = make_state()
        b = make_state(rsi_avg_gain=2.0)
        self.assertNotEqual(compute_state_checksum(a), compute_state_checksum(b))

    def test_with_checksum_is_self_consistent(self) -> None:
        state = make_state().with_checksum()
        self.assertEqual(state.checksum, compute_state_checksum(dataclasses.replace(state, checksum="")))


class IsStateUsableTests(unittest.TestCase):
    def test_usable_when_all_checks_pass(self) -> None:
        state = make_state().with_checksum()
        self.assertTrue(
            is_state_usable(
                state,
                expected_parent_build_id="build-1",
                actual_parent_build_id="build-1",
                next_canonical_key=("spot", "BTCUSDT", "1m", 60_000),
                key_directly_follows=True,
            )
        )

    def test_unusable_on_build_id_mismatch(self) -> None:
        state = make_state().with_checksum()
        self.assertFalse(
            is_state_usable(
                state,
                expected_parent_build_id="build-1",
                actual_parent_build_id="build-2",
                next_canonical_key=("spot", "BTCUSDT", "1m", 60_000),
                key_directly_follows=True,
            )
        )

    def test_unusable_when_key_does_not_directly_follow(self) -> None:
        state = make_state().with_checksum()
        self.assertFalse(
            is_state_usable(
                state,
                expected_parent_build_id="build-1",
                actual_parent_build_id="build-1",
                next_canonical_key=("spot", "BTCUSDT", "1m", 120_000),
                key_directly_follows=False,
            )
        )

    def test_unusable_on_checksum_tamper(self) -> None:
        state = make_state().with_checksum()
        tampered = dataclasses.replace(state, rsi_avg_gain=999.0)
        self.assertFalse(
            is_state_usable(
                tampered,
                expected_parent_build_id="build-1",
                actual_parent_build_id="build-1",
                next_canonical_key=("spot", "BTCUSDT", "1m", 60_000),
                key_directly_follows=True,
            )
        )


if __name__ == "__main__":
    unittest.main()
