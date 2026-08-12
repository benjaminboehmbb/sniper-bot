# Pre-IU-4 X1 Full-10K SHADOW Observation Evidence — 2026-08-12

## Status

**X1 FULL-10K PAPER SHADOW OBSERVATION PASSED — 10,000/10,000 (100.0%)**

The user explicitly approved
`IU4-X1-FULL-10K-SHADOW-OBSERVATION FREIGEBEN` on 2026-08-12.

The active PAPER loop evaluated every fused intent through the IU-4 adapter
only inside its disposable sandbox. The bound IU-4 source state remained
read-only. IU4 ENFORCED, Exchange, and Live remained disabled.

## Immutable execution binding

- branch: `codex/iu4-x1-full-10k-shadow-observation-2026-08-12`;
- Git commit: `b35bac1acdb8127f62951aaa481b7a056bb48ee5`;
- execution host: `X1`;
- bounded records: `10,000/10,000`;
- observed market interval: `2017-08-17 04:00:00+00:00` through
  `2017-08-24 02:39:00+00:00`;
- normalized market slice SHA-256 before and after:
  `9f83f5500ab0bc91de641146fdc5ad5910d2fdf6a7818227b29743e51b46fdba`;
- approved throttle profile SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`;
- approved throttle policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`;
- economics profile SHA-256:
  `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`.

## Result

- processed observations: `10,000/10,000`;
- unique ordered source-intent IDs: `10,000/10,000`;
- observation sequences and tick IDs: exact `1..10,000`;
- IU-4 outcomes: `18 COMMITTED`, `9,982 NOOP`;
- committed transitions: `9 OPEN_LONG`, `9 CLOSE_LONG`;
- autonomous exits: `9/9` matched the required open position and committed as
  `CLOSE_LONG`;
- autonomous-exit suppressions: `0`;
- position-before parity failures: `0`;
- action parity failures: `0`;
- position-after parity failures: `0`;
- final legacy position: `FLAT`;
- final IU-4 sandbox position: `FLAT`;
- final IU-4 sandbox transaction sequence: `18`;
- runtime error markers: `0`;
- observation failure markers: `0`.

## Source immutability and safety boundary

- initial/current source-state fingerprint:
  `aeb4c5bddabdfd4baca92b23437c7fba2cd24567a92945f0ad41306606816512`;
- initial/current source transaction sequence: `0`;
- atomic source file SHA-256 before and after:
  `93f37fd2785caa909a864e21b1ff21644527e204b533ebc123650982b9736fd2`;
- source reconciliation: passed;
- adapter execution scope: `DISPOSABLE_SANDBOX_ONLY`;
- source-state mutation allowed: `false`;
- Exchange enabled: `false`;
- Live enabled: `false`.

The older preserved X1 input and atomic state were re-hashed after execution
and remained unchanged:

- old normalized market slice:
  `9f83f5500ab0bc91de641146fdc5ad5910d2fdf6a7818227b29743e51b46fdba`;
- old atomic state:
  `120dcd57f5e0b3bacb2c95a0d7f37d8d6a15132fadd2ce7cae75b9c4c9316863`.

## Evidence identities

- observation evidence SHA-256:
  `aae4299709c1c52a853f574bf0931614e0d316d8d393758d3959b6f5f4f6f4f0`;
- observation evidence canonical fingerprint:
  `d0253a180fd30a4e7a51e4ccc379933ddb476448668f7bee1a8dadc85d16ade9`;
- atomic-source byte-manifest fingerprint:
  `b38fcb9c3c36032d81480cd15922f0b86ffca6d9b251a431007ad9bcf8bca61c`;
- active runtime log SHA-256:
  `5a92a12614954ff7ce2ad55af1dcb4f3ae401c03069242ff88e6f671172a29c9`;
- launcher stdout SHA-256:
  `8c6992ad3fad89cf8195de3ca9ac16fcfa53e0219826cd8e320a869bc903e03b`;
- launcher stderr SHA-256 (empty):
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Scope boundary

This closes only the approved complete `10,000`-tick X1 observation. It does
not authorize IU4 ENFORCED, Exchange, Live, a workstation active observation,
or mutation of the bound IU-4 source state.

## Next gate

Review the exact 18 committed transitions and the zero-divergence result, then
define the next bounded observation gate. Any workstation active observation
or longer-duration PAPER observation requires separate approval and must retain
the same fail-closed, read-only, and no-Exchange/no-Live boundary.
