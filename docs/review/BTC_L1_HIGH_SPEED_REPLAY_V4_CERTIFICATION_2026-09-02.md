# BTC-L1 High-Speed Historical Replay V4 Certification

Date: 2026-09-02

Status: PASS

## Purpose

This document certifies the BTC-L1 High-Speed Historical Replay V4 path for
deterministic engineering replay of the exact frozen BTC-L1 golden reference.

It does not authorize replacement of the normal Paper or Live runtime path.
It does not constitute candidate selection, OOS evidence, holdout evidence,
or performance-based strategy selection.

## Frozen reference

- Golden commit: `a67b3da6661512d0e9177cc30badb3aa5fab5989`
- Canonical dataset logical ID: `BTC_L1_CANONICAL_V1`
- Canonical dataset SHA256: `530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f`
- Full canonical ticks: `4374557`
- Seed file: `seeds/5m/btcusdt_5m_timing_core_v2.csv`
- Seed SHA256: `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`
- Frozen replay runner: `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py`
- Frozen runner SHA256: `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292`
- Frozen runner is byte-identical to the runner used for the certified Full run: YES

## V4 optimization boundary

V4 changes no tracked golden strategy or core source file.

The certified replay adapter performs only these replay-specific optimizations:

1. Physical per-tick operational log output is suppressed.
2. The complete semantic event stream is still processed and hashed in order.
3. Per-tick S2/S4 disk persistence is suppressed during uninterrupted replay.
4. Final S2/S4 state is persisted once through the canonical persistence implementation.
5. The timing function is not optimized, cached, or replaced.

The timing path remains the original `live_l1.core.timing_5m.compute_5m_timing_vote`
implementation from the golden commit.

Earlier experimental prototypes that cached the complete timing vote are not certified
and must not be used as authoritative replay paths.

## Full-history certification result

- Ticks: `4374557`
- Runtime return code: `0`
- Runtime stderr: empty
- Semantic runtime events: `30621902`
- Semantic event SHA256: `ffa200c601dc6c2bdda0492909d6518573af6de0b621deb91ee3c9f46d7022e3`
- Golden semantic event SHA256: identical
- Semantic event stream parity: PASS
- Closed trades: `563`
- Normalized ordered trade SHA256: `46706ec9f6446eb5ceecf7782199a8a7fab8a7f91c318ce560f5daa83b98646c`
- Ordered trade sequence parity: PASS
- Final S2 semantic state parity: PASS
- Final S4 semantic state parity: PASS
- Loss-cluster semantic state parity: PASS
- Post-run reconciliation: PASS
- Per-tick canonical S2/S4 persistence calls suppressed: `4374557`
- Final canonical persistence calls: `1`
- Operational logger calls suppressed: `30621899`
- Operational logger calls retained: `3`
- Fast replay runtime artifacts: `6146901` bytes

## Runtime characterization

- Started UTC: `2026-09-02T05:11:36Z`
- Finished UTC: `2026-09-02T05:20:21Z`
- Elapsed time from UTC timestamps: `525` seconds
- Internal monotonic duration reported by runner: `577.871213` seconds

The two elapsed-time measurements differ. Both are preserved. Runtime performance
is characterization only and is not a parity or certification criterion.

## Certification interpretation

The Full V4 replay reproduced the Golden Full-A behavior across the complete canonical
2017-2025 BTC-L1 history with identical semantic event fingerprint, identical ordered
normalized trade sequence, identical semantic final states, and successful reconciliation.

Therefore V4 is certified as a high-speed historical replay path only for the frozen
configuration identified in this document.

## Mandatory recertification

This certification is invalidated and parity must be rerun if any of the following occurs:

1. Frozen runner SHA256 changes.
2. Golden reference commit changes.
3. Canonical dataset identity or SHA256 changes.
4. Seed identity or SHA256 changes.
5. Decision-relevant source code changes.
6. Decision-relevant runtime configuration changes.
7. Timing implementation or timing behavior changes.
8. Contradictory primary execution evidence is discovered.
9. Formal scientific review explicitly requires recertification.

## Prohibited interpretation

This certification must not be interpreted as:

- a Paper Trading readiness attestation,
- a Live Trading readiness attestation,
- an OOS result,
- a prospective holdout result,
- a candidate-selection result,
- permission to tune against the certified historical replay,
- permission to replace the normal production persistence guarantees.

## Evidence

Machine-readable evidence:

`docs/review/evidence/BTC_L1_HIGH_SPEED_REPLAY_V4_CERTIFICATION_2026-09-02.json`

Certification runner:

`live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py`
