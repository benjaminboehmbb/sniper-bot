# Pre-IU-4 X1 100K SHADOW Retest Evidence — 2026-08-13

## Status

**PASSED — 100,000/100,000 RECORDS WITH ZERO PARITY FAILURES**

The user explicitly approved `IU4-X1-100K-SHADOW-RETEST FREIGEBEN` after the
loss-cluster parity repair was integrated into `main`.

The bounded X1 PAPER SHADOW retest completed with process exit code `0`, an
empty stderr, a complete hash-chained evidence journal, and exact Legacy/IU-4
action and position parity for all 100,000 records. IU4 ENFORCED, Exchange,
Live, and source-state mutation remained disabled.

## Immutable execution binding

- execution host: `X1`;
- repository commit: `6d6795c9d8c1392fa7a409ea00163280e15fe444`;
- started UTC: `2026-08-13T14:46:14.009600644Z`;
- finished UTC: `2026-08-13T15:35:47.333279579Z`;
- process exit code: `0`;
- observed records: `100,000/100,000`;
- market interval: `2017-08-17 04:00:00+00:00` through
  `2017-10-25 21:38:00+00:00`;
- normalized market SHA-256 before and after:
  `e6921180523900e824f7a8a1f0d995fafb203d1e7c30301763e385ee81be23c6`;
- atomic source SHA-256 before and after:
  `93f37fd2785caa909a864e21b1ff21644527e204b533ebc123650982b9736fd2`;
- source byte-manifest fingerprint:
  `b38fcb9c3c36032d81480cd15922f0b86ffca6d9b251a431007ad9bcf8bca61c`;
- source initial/current state fingerprint:
  `aeb4c5bddabdfd4baca92b23437c7fba2cd24567a92945f0ad41306606816512`;
- source initial/current transaction sequence: `0`;
- 5-minute seed SHA-256:
  `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`;
- economics profile SHA-256:
  `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`;
- approved throttle profile SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`;
- launcher SHA-256:
  `74e46f6f0b877173f40e05e14a9d3ca3cb7a810f75b8fdefa5a27783969c9c37`.

## Evidence integrity

- final evidence schema: `2`;
- exact observation sequences: `1..100,000`;
- exact tick IDs: `1..100,000`;
- unique source-intent IDs: `100,000/100,000`;
- unique IU-4 request IDs: `100,000/100,000`;
- final evidence SHA-256:
  `62e096cdd0a44aca63e75f1c759d30608f1b23eeaff8ea1c6286c3e3cdd46921`;
- final evidence canonical fingerprint:
  `b93dbe680ce1edf860a1076636bd8f64ff9dfd3e1bf8e9ca08492d14633adac0`;
- journal SHA-256:
  `0236c42b80643e6bcc9e8ef26382aab9ce6548b73f9e1c2369b58a8fed4b0f5f`;
- journal byte length: `143,283,957`;
- journal records: `100,000`;
- final journal chain head:
  `ab0ec7b7b256630f345973d425e7ee4ef19afa959ebe203f3856e0f5ba9eff27`;
- canonical journal failures: `0`;
- journal-chain failures: `0`;
- journal/final-record mismatches: `0`;
- launcher stdout SHA-256:
  `3dcc5131a670e40ddf6efd48e43631ac24bfe8f9c7d4f76523fdb6d550c2d679`;
- launcher stderr SHA-256 (empty):
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- runtime error, traceback, or observation-failure markers: `0`.

## Behavioral result

- IU-4 outcomes: `40 COMMITTED`, `99,960 NOOP`;
- committed transitions: `20 OPEN_LONG`, `20 CLOSE_LONG`;
- autonomous exits: `20/20` position-matched and committed;
- autonomous-exit suppressions: `0`;
- position-before parity failures: `0`;
- action parity failures: `0`;
- position-after parity failures: `0`;
- final Legacy position: `FLAT`;
- final IU-4 sandbox position: `FLAT`;
- final IU-4 sandbox transaction sequence: `40`.

## Loss-cluster parity result

The two causal events from the failed run are corrected exactly:

- observation `13,219`: source `BUY`, observed `HOLD`, Legacy `NOOP`, IU-4
  `NOOP`, Legacy/IU-4 `FLAT -> FLAT`, all parity flags true;
- observation `92,748`: source `BUY`, observed `HOLD`, Legacy `NOOP`, IU-4
  `NOOP`, Legacy/IU-4 `FLAT -> FLAT`, all parity flags true.

The corrected state trajectory exposes `43` total legitimate
`LOSS_CLUSTER_GATE_BLOCKED_ENTRY` attempts, not only the two causal events.
All 43 are source `BUY`, observed `HOLD`, state-exact `FLAT -> FLAT`, and fully
parity-equal. This larger count is expected after the repair: in the failed
run, the two erroneous IU-4 LONG states hid later blocked-entry opportunities
from IU-4. No acceptance criterion is weakened or reclassified.

## Safety boundary

- operational profile: `PAPER`;
- observation mode: `SHADOW`;
- adapter execution scope: `DISPOSABLE_SANDBOX_ONLY`;
- source-state mutation allowed: `false`;
- IU4 ENFORCED: `false`;
- Exchange enabled: `false`;
- Live enabled: `false`.

## Scope and next gate

This evidence closes only the approved X1 100K SHADOW retest. It does not
authorize IU4 ENFORCED, Exchange, Live, source-state mutation, a workstation
run, or branch integration.

The next separately approved action is branch integration of this evidence,
followed by definition of the next bounded IU-4 gate.
