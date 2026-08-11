# Pre-IU-4 Replay Input Builder Evidence — 2026-08-09

## Status

**IMPLEMENTED AND LOCALLY VERIFIED; ISOLATED SHADOW INPUT ONLY**

Branch: `codex/pre-iu4-replay-input-builder-2026-08-09`

IU-4 ENFORCED, Exchange, and Live remain locked. The builder is not imported
by the active L1 loop or any startup path.

## Source contract

`build_iu4_replay_input_from_l1_log()` reads an existing regular,
non-symlink structured L1 log. It parses the established key/value format and
joins exactly one `L2 market_snapshot` with exactly one `L3 intent_fused` for
each `(system_state_id, source tick)` pair.

The active loop receives one additive observability field:
`market_snapshot.reference_price_text`. This is the existing canonical Decimal
carrier created directly from the market CSV. No decision, guard, execution,
state, timing, or Exchange/Live behavior is changed. The builder explicitly
rejects the legacy float `price` as an economic authority.

The source boundary fails closed on malformed lines, invalid categories,
missing pairs, duplicate pairs, invalid ticks, missing intent identity/reason,
invalid intent, absent/noncanonical/nonpositive Decimal price text, duplicate
intent IDs, or non-monotone market timestamps.

## Deterministic transformation

For every joined pair the builder creates one strict
`IU4ShadowIntentStepV1`:

- replay ticks are normalized to the strict sequence `1..N`, including across
  L1 process restarts where source tick IDs restart;
- the canonical market timestamp and Decimal price are preserved;
- the fused intent ID, reason code, and system-state identity remain bound;
- BUY/SELL candidate stops are calculated with the explicit Decimal stop rate
  and the same 50-digit, half-even arithmetic contract used by PEE SHADOW;
- candidate trade IDs are SHA-256 content-addressed;
- HOLD contains neither a stop nor a trade ID.

The SHADOW harness binds each generic intent candidate to the exact current
sandbox state. It selects the candidate stop/trade ID only for an actual OPEN,
uses the current trade ID for CLOSE, and preserves the current state identity
for NOOP. Therefore an economically rejected entry cannot corrupt or terminate
the remaining replay sequence.

## Artifacts and immutability

The builder writes two immutable no-clobber artifacts:

1. canonical strict replay JSONL;
2. a canonical manifest binding source log SHA-256/size/statistics, explicit
   stop rate and price authority, replay SHA-256/size/count, time bounds, and
   normalized tick bounds.

The manifest has its own canonical fingerprint. Byte-identical reruns are
idempotent without inode or modification-time changes. Different existing
artifacts, symlinks, path collisions, invalid directories, and source mutation
fail closed; no artifact is overwritten.

## Verification

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest \
  tests.live_l1.test_paper_iu4_replay_input \
  tests.live_l1.test_paper_iu4_replay_evidence \
  tests.live_l1.test_paper_iu4_shadow_harness \
  tests.live_l1.test_paper_economics_shadow_runtime

Ran 35 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/live_l1 -p 'test_*.py'

Ran 235 tests — OK
```

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover \
  -s tests/regression -p 'test_*.py'

Ran 170 tests — OK
```

`git diff --check` and bytecode compilation passed.

## Scope boundary

This unit converts a completed L1 log into replay input. It does not run L1,
create or mutate atomic Paper state, activate IU-4, change the accepted PEE
profile, or send Exchange/Live orders. An explicit pipeline smoke test must
still prove the complete local chain: L1 log → replay JSONL/manifest → isolated
SHADOW harness → immutable replay evidence.
