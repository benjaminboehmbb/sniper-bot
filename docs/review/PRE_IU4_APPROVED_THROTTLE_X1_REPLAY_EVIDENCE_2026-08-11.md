# Pre-IU-4 Approved Throttle X1 Replay Evidence — 2026-08-11

## Status

**OFFLINE X1 SHADOW REPLAY PASSED; RUNTIME NOT ACTIVATED**

The user explicitly approved
`IU4-APPROVED-THROTTLE-REPLAY FREIGEBEN` on 2026-08-11.

This gate authorizes only offline replay use of the approved throttle profile.
IU4 ENFORCED, Exchange, and Live remain disabled.

## Implemented boundary

`run_paper_iu4_x1_replay_dataset.py` now accepts exactly one of:

- the existing calibration-only observation policy; or
- `--approved-throttle-policy-json` for an approved but non-activated profile.

The approved path fails closed before output creation when:

- both or neither policy inputs are provided;
- artifact fields are missing or unknown;
- approval or calibration binding is invalid;
- `runtime_activated`, IU4 ENFORCED, Exchange, or Live authority is true;
- the policy model or canonical fingerprint differs;
- any binding hash is malformed.

The run manifest records the approval ID, profile/model identity, file hash,
canonical policy fingerprint, and calibration binding. The startup gate remains
SHADOW and receives no ENFORCED authorization.

## Approved policy binding

- Profile ID: `PEE_RATE_OBSERVED_BOUNDARY_001`
- Model version: `PEE_RATE_V1`
- Profile file SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`
- Policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`
- Calibration report SHA-256:
  `c7ecc33ff559ab8c57b15928bc0ad0f98a466bd15130ac9f30f763918454afe8`
- Calibration decision replay SHA-256:
  `65f47adaace62a9d9073bc28695d58b09bd7c943f3df94b23f2c67f70ea8114b`

## X1 action smoke replay

The final replay is bound to repository commit
`4463556fc4c538d8400cf6fe80156fcdcdf01a1c` and a six-tick synthetic,
offline-only forced-intent source. It deliberately exercises one accepted
entry, its exit, and two attempted re-entries inside the approved three-hour
cooldown.

- Requested / processed steps: `6 / 6`
- Committed: `2` (`OPEN_LONG`, then `CLOSE_LONG`)
- NOOP: `2`
- Rejected entries: `2`
- Both rejection reasons: `PEE_RATE_REENTRY_COOLDOWN`
- Exit permission: `true` for every step
- Continuation blocked: `false`
- Guard divergence: `0`
- Final position: `FLAT`
- Pipeline chain checks: `16 / 16` true
- IU4 ENFORCED / Exchange / Live: `false / false / false`

Outcome sequence:

1. `NOOP` — HOLD, FLAT;
2. `OPEN_LONG` — COMMITTED, LONG;
3. `CLOSE_LONG` — COMMITTED, FLAT;
4. `OPEN_LONG` — REJECTED by re-entry cooldown, FLAT;
5. `NOOP` — HOLD, FLAT;
6. `OPEN_SHORT` — REJECTED by re-entry cooldown, FLAT.

## Artifact identities

- Source CSV SHA-256:
  `54be8d285237650b05d7cb5e4ce8e32a2d7f936a095d024d7f4c62b24c455abe`
- Run manifest SHA-256:
  `4afb133d23b2aa8c9ae60d26fe738ab78732caece200c077374a28a2eaf73a56`
- Run manifest fingerprint:
  `16f822d96134b7bd3e05c9c52bc5cdc81a0233711238d14642e6f5a5a7f88bb2`
- Replay JSONL SHA-256:
  `734880e5b92546be1b0d4ec49f9134e444009f012633b94bffffa941c150c8bc`
- Replay-input manifest SHA-256:
  `c33c2106ab15e784b09bf1989111a9ab352ed76a7553cdc5f4a67917bb8b0d13`
- Replay evidence SHA-256:
  `9518d352879ab23668dd4dd22b2c2b6edb54d22213f58bf7eb28b0825d337928`
- Pipeline receipt SHA-256:
  `2872e9ee01e6aa59b0fa6277416fc5b4dc1a83203374c8ea47d54f6cba8de8c1`

## Repeat-run assessment

Two independent action-smoke generations produced the same ordered policy
decisions, counts, locks, and 16 chain checks. Their canonical semantic summary
SHA-256 was identical:
`e3d1e3b82b187c8225bdbec0204195da525e8fa8bbefd7141bdeecd389c62bd4`.

Fresh IU3 source generation is not byte-identical because the existing live
loop writes wall-clock audit timestamps, output paths, and new
system-state/intent IDs. Therefore independently regenerated whole-file hashes
differ. This is an upstream source-generation property, not a throttle-policy
decision divergence. The next workstation gate must reuse the already
hash-pinned full-history replay input instead of regenerating IU3 source logs.

## Verification

```text
.venv/bin/python -m unittest \
  tests.live_l1.test_run_paper_iu4_x1_replay_dataset
Ran 15 tests — OK

.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
Ran 281 tests — OK

.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
Ran 170 tests — OK
```

`py_compile`, CLI argument validation, JSON validation, and `git diff --check`
passed. Runtime implementation commit: `02d90c8`. Action-replay regression test
commit: `4463556`.

## Next gate

Run the exact approved profile on the workstation against the preserved,
hash-pinned full-history replay input. This requires a fresh approved-policy
atomic source and must remain IU4 SHADOW with Exchange and Live disabled.
