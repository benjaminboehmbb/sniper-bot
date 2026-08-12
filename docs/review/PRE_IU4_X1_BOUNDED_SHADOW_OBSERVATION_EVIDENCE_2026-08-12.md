# Pre-IU-4 X1 Bounded SHADOW Observation Evidence — 2026-08-12

## Status

**X1 BOUNDED PAPER SHADOW OBSERVATION PASSED — 1,000/1,000 (100.0%)**

The user explicitly approved
`IU4-X1-BOUNDED-SHADOW-OBSERVATION FREIGEBEN` on 2026-08-12.

The run executed the active PAPER loop and evaluated every fused intent through
the IU-4 adapter only in its disposable sandbox. The bound IU-4 source state
was read-only. IU4 ENFORCED, Exchange, and Live remained disabled.

## Immutable execution binding

- branch: `codex/iu4-x1-bounded-shadow-observation-2026-08-12`;
- Git commit: `90669fc0d6dd74ccf4fc5786d0a6555ed8400279`;
- execution host: `X1`;
- bounded records: `1,000` of the preserved `10,000`-record X1 slice;
- observed market interval: `2017-08-17 04:00:00+00:00` through
  `2017-08-17 20:39:00+00:00`;
- normalized market slice SHA-256 before and after:
  `9f83f5500ab0bc91de641146fdc5ad5910d2fdf6a7818227b29743e51b46fdba`;
- approved throttle profile SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`;
- approved throttle policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`;
- economics profile SHA-256:
  `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`.

## Result

- processed observations: `1,000/1,000`;
- unique ordered source-intent IDs: `1,000/1,000`;
- observation sequences and tick IDs: exact `1..1,000`;
- IU-4 outcomes: `3 COMMITTED`, `997 NOOP`;
- committed transitions: `2 OPEN_LONG`, `1 CLOSE_LONG`;
- autonomous exits: `1/1` correctly represented as `CLOSE_LONG`;
- autonomous-exit suppressions: `0`;
- position-before parity failures: `0`;
- action parity failures: `0`;
- position-after parity failures: `0`;
- runtime error markers: `0`;
- observation failure markers: `0`.

The bounded stop occurred while both legacy PAPER and the disposable IU-4
sandbox were `LONG`. This is exact parity at the explicit 1,000-tick boundary,
not an incomplete close or a Live position. The read-only IU-4 source remained
`FLAT` at transaction sequence `0`.

## Source immutability and safety boundary

- initial/current source-state fingerprint:
  `c5bd1ef08f39ae7a2d1e2d42c8cfe56abcb988d3114c1e5121b3dc25e79d0d42`;
- initial/current source transaction sequence: `0`;
- atomic source file SHA-256 before and after:
  `aee1e75533740dd3a024e55a7dbc4ec125dfdf59e726c64b38624d27cd44cbb2`;
- source reconciliation: passed;
- adapter execution scope: `DISPOSABLE_SANDBOX_ONLY`;
- source-state mutation allowed: `false`;
- Exchange enabled: `false`;
- Live enabled: `false`.

The older X1 replay input and atomic state were also re-hashed after the run and
remained unchanged:

- old normalized market slice:
  `9f83f5500ab0bc91de641146fdc5ad5910d2fdf6a7818227b29743e51b46fdba`;
- old atomic state:
  `120dcd57f5e0b3bacb2c95a0d7f37d8d6a15132fadd2ce7cae75b9c4c9316863`.

## Evidence identities

- observation evidence SHA-256:
  `730ae8e1c8ed26d446ae6d0e9f369b79bc57bfc3ec662a78bc7335ad1de6c65b`;
- observation evidence canonical fingerprint:
  `f4212ca054b7d300623613dc7a67ca5101fdac35db07879822a62c9e117547e6`;
- atomic-source byte-manifest fingerprint:
  `685a7d621e4b5197616d29b74e084789d8ae8d4604390bc082e10344ef04e3f2`;
- active runtime log SHA-256:
  `344a2ee538f13c284e8b942b46604ea122e758582e6b0259b8c020a00fb30036`.

The first launch attempt stopped before tick 1 because the isolated worktree's
empty legacy state directory had not yet been created. Its zero-record evidence
was preserved separately with SHA-256
`764df3dd2f298026ed620d1a8863c899b302216cb99826abefa1c49ca0cee55c`.
No source or atomic state changed during that fail-closed start.

## Scope boundary

This closes only the approved bounded X1 observation gate. It does not
authorize IU4 ENFORCED, Exchange, Live, a workstation run, or runtime mutation
of the bound source state.

## Next gate

Review the three committed transitions and then, under a separate approval,
extend the bounded X1 observation from `1,000/10,000` to the complete preserved
`10,000/10,000` X1 slice. The run must retain exact parity, source immutability,
and the current fail-closed gates.
