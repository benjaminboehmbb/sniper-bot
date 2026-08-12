# Pre-IU-4 X1 100K SHADOW Observation Evidence — 2026-08-12

## Status

**EXECUTION COMPLETED — ACCEPTANCE FAILED CLOSED ON LEGACY LOSS-CLUSTER DIVERGENCE**

The user explicitly approved
`IU4-X1-100K-SHADOW-OBSERVATION FREIGEBEN` on 2026-08-12.

The bounded X1 PAPER SHADOW loop completed all `100,000/100,000` observations
with process exit code `0` and no runtime error output. The acceptance gate is
nevertheless **not passed**: two Legacy entries were correctly blocked by the
existing loss-cluster gate while the disposable IU-4 sandbox opened LONG.
The resulting position divergence remained visible through the end of the
bounded input. This is preserved as fail-closed evidence and is not relabelled
as a successful parity run.

IU4 ENFORCED, Exchange, and Live remained disabled. The bound IU-4 source state
remained read-only.

## Immutable execution binding

- execution host: `X1`;
- repository commit: `1c070996438e5adb8dc8441ad91333c8eaf19bf3`;
- started UTC: `2026-08-12T13:11:17.438799181Z`;
- finished UTC: `2026-08-12T14:39:02.814885195Z`;
- process exit code: `0`;
- bounded records: `100,000/100,000`;
- observed market interval: `2017-08-17 04:00:00+00:00` through
  `2017-10-25 21:38:00+00:00`;
- normalized market slice SHA-256 before and after:
  `e6921180523900e824f7a8a1f0d995fafb203d1e7c30301763e385ee81be23c6`;
- atomic source SHA-256 before and after:
  `93f37fd2785caa909a864e21b1ff21644527e204b533ebc123650982b9736fd2`;
- approved throttle profile SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`;
- approved throttle policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`;
- economics profile SHA-256:
  `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`;
- 5-minute seed SHA-256:
  `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`;
- launcher SHA-256:
  `d8dcdfd10a23cab4c8322d3da5536b77004d83a2eadd7bd8cc518c7fea561cb2`.

## Evidence integrity

- final evidence schema: `2`;
- evidence record count: `100,000`;
- unique source-intent IDs: `100,000/100,000`;
- unique IU-4 request IDs: `100,000/100,000`;
- observation sequences: exact `1..100,000`;
- tick IDs: exact `1..100,000`;
- final evidence SHA-256:
  `52de9b473da4e3659d261b16c8144ec3f836bd24470cf64da3dcfb017c2360a1`;
- final evidence canonical fingerprint:
  `4912ced11ff05d22183f234de15f2b44bb3d88f133987eb4a377666032aa5661`;
- journal SHA-256:
  `db7cc96dca407c4206dd9d3486c540c61fb7f17fea77e4d2ee80c9ccf48aee6c`;
- journal byte length: `143,405,133`;
- journal records: `100,000`;
- final journal chain head:
  `adb405ad951bddd830bab50aa35ebdaa2885143b62197602bd8a750b878a2bca`;
- journal canonical-encoding failures: `0`;
- journal chain failures: `0`;
- journal/final-record mismatches: `0`;
- source byte-manifest fingerprint:
  `b38fcb9c3c36032d81480cd15922f0b86ffca6d9b251a431007ad9bcf8bca61c`;
- launcher stderr SHA-256 (empty):
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`;
- launcher stdout SHA-256:
  `12470c978605d6f4a4099fa3f6e39535d6d3f5058a5f9f480c0d2ef8ad7199dd`;
- runtime error markers: `0`;
- observation failure markers: `0`.

The evidence and journal are internally complete and hash-valid. Process
success therefore proves completion and evidence integrity only; it does not
override the failed behavioral acceptance checks below.

## Behavioral result

- IU-4 outcomes: `41 COMMITTED`, `99,959 NOOP`;
- IU-4 transitions: `21 OPEN_LONG`, `20 CLOSE_LONG`;
- autonomous exits: `20/20` position-matched and committed;
- autonomous-exit suppressions: `0`;
- position-before parity failures: `60,306`;
- action parity failures: `3`;
- position-after parity failures: `60,307`;
- final Legacy position: `FLAT`;
- final IU-4 sandbox position: `LONG`;
- final IU-4 sandbox transaction sequence: `41`.

The three action divergences are:

1. observation `13,219`, `2017-08-26 08:18:00+00:00`, source intent
   `IN-12f755020839`: Legacy `NOOP / LOSS_CLUSTER_GATE_BLOCKED_ENTRY`, IU-4
   `OPEN_LONG`;
2. observation `66,273`, `2017-10-02 11:31:00+00:00`, source intent
   `IN-3b3e04668574`: Legacy `OPEN_LONG`, IU-4 `NOOP` because its sandbox was
   already LONG from divergence 1;
3. observation `92,748`, `2017-10-20 20:46:00+00:00`, source intent
   `IN-76bce3845b60`: Legacy `NOOP / LOSS_CLUSTER_GATE_BLOCKED_ENTRY`, IU-4
   `OPEN_LONG`.

Position divergence intervals are:

- position-before: `13,220..66,273` and `92,749..100,000`;
- position-after: `13,219..66,272` and `92,748..100,000`.

The first divergence is later closed by the common autonomous LONG time stop,
which restores position parity after observation `66,273`. The second
divergence remains open when the bounded input ends.

## Root-cause boundary

The established Legacy execution path owns a persistent loss-cluster entry
gate and emitted `LOSS_CLUSTER_GATE_BLOCKED_ENTRY` at the two causal points.
The current IU-4 adapter contract maps the fused BUY intent and its own atomic
risk/throttle state, but it does not receive or represent this Legacy
loss-cluster veto. The discrepancy is therefore a missing cross-runtime guard
contract, not corrupted evidence, altered input, an autonomous-exit mismatch,
or a reason to weaken parity.

No runtime implementation is changed by this evidence unit. Any correction
requires a separately approved, governance-consistent contract decision for
how the established loss-cluster veto is bound into IU-4 observation and later
execution.

## Source immutability and safety boundary

- initial/current source-state fingerprint:
  `aeb4c5bddabdfd4baca92b23437c7fba2cd24567a92945f0ad41306606816512`;
- initial/current source transaction sequence: `0`;
- adapter execution scope: `DISPOSABLE_SANDBOX_ONLY`;
- source-state mutation allowed: `false`;
- observation mode: `SHADOW`;
- IU4 ENFORCED: `false`;
- Exchange enabled: `false`;
- Live enabled: `false`.

## Scope boundary and next gate

This commit records the completed but behaviorally failed 100K observation.
It does not approve IU4 ENFORCED, Exchange, Live, source-state mutation, or a
repeat run.

The next gate is a focused `LOSS_CLUSTER` parity-contract decision and repair.
It must retain fail-closed behavior, use the established Legacy gate as the
behavioral authority, add targeted divergence tests, run the complete Live-L1
and regression suites, and receive separate authorization before any new
100K observation.
