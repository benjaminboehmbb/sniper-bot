# Pre-IU-4 X1 Replay Restart Fault-Injection Evidence — 2026-08-09

## Status

**TRUNCATED RESTART SNAPSHOT DETECTED; CONTINUATION FAILED CLOSED**

Branch: `codex/pre-iu4-x1-replay-restart-fault-2026-08-09`

Fault-injection contract commit: `f20660f5e46f9546f004d224cf30817758f48371`

IU-4 ENFORCED, Exchange, Live, and the Workstation remained locked and unused.

## Controlled fault

The X1 replay requested 10,000 steps and an isolated restart after step 5,050.
At that boundary, and only inside the disposable IU-4 sandbox, the atomic
snapshot was replaced with deliberately truncated JSON and durably flushed.
The source coordinator, source log, dataset, repository state, and all runtime
artifacts outside the temporary sandbox were never modified by the injection.

Expected success criteria for this negative test were:

- detect the corrupted snapshot during reconstruction;
- report the exact atomic failure reason;
- execute no step after the restart boundary;
- publish immutable negative evidence without treating the sandbox as valid;
- prove the real source remains byte-identical;
- keep IU-4 ENFORCED, Exchange, and Live disabled.

## X1 result

- requested replay steps: 10,000;
- processed replay steps: 5,050;
- restart position: LONG;
- restart transaction sequence: 15;
- committed before fault: 15 (`8 OPEN_LONG`, `7 CLOSE_LONG`);
- NOOP before fault: 5,035;
- rejected outcomes: 0;
- injected fault: `SNAPSHOT_TRUNCATED`;
- detected reason: `PEE_ATOMIC_JSON_INVALID`;
- snapshot SHA-256 before fault:
  `4dc23cce261ee2e0d12a5cc652ee1c8978e6153e102c8b9378b3086f60311629`;
- snapshot SHA-256 after fault:
  `3f95f51e9b8717f4b3bf975963a890c5f8f60a444922815bd17642b0c95682ff`;
- restart state restored: false;
- continuation blocked: true;
- last outcome index: 5,050;
- no outcome with index 5,051 or higher exists;
- source state unchanged: true;
- all pipeline chain checks passed for the expected blocked-fault mode.

The result is intentionally not a completed 10,000-step replay. Passing means
the inconsistency was detected and processing stopped exactly at the boundary.

## Whole-file hashes

- IU-3 manifest:
  `21dd0548ba1c8246f7c258eaa642543893e5070f1a6f1316a273e4c90e84004f`;
- L1 source log:
  `95bd74f0483cc3f6bf10665016293acffd72e629472a264707e97f2edb7ef66c`;
- replay JSONL:
  `f52a4740144fbb4ca85ed3fd258f097ebd0dba91d8c4fafee849154199b6940d`;
- replay input manifest:
  `b53f770cb145a4d593e83364a0cf8085b8b3f09c9cbbd913e75c0f73a22e6231`;
- negative replay evidence:
  `d411adbe2d23fa5543ff3a9d4e2184c86d504d20b85b2095b0235b15f016d755`;
- pipeline receipt:
  `ccb0389e179da513f31f7cc80e9cc365e625ecd28609ef0715db422f140a05e7`;
- top-level run manifest:
  `519e847b048f450dc86aa36571c937aad90d6c914a72ab2dbedf31828868889a`.

All canonical fingerprints, the requested/processed step counts, the missing
step 5,051, the changed sandbox hash, and unchanged source state independently
revalidated.

## Verification

```text
Focused restart/fault/replay tests
Ran 37 tests — OK

tests/live_l1 full suite
Ran 255 tests — OK

tests/regression full suite
Ran 170 tests — OK
```

Bytecode compilation and `git diff --check` passed. The unrelated untracked
`scripts/build_rcc002_spec_bundle.py` remained untouched.

## Scope boundary and next gate

This proves detection and fail-closed blocking for one deliberately truncated
restart snapshot. It does not authorize automated repair, IU-4 ENFORCED,
Exchange, Live, or an operational throttle policy.

Next gate when the Workstation is available:
`IU4-WORKSTATION-FULL-HISTORY-REPLAY FREIGEBEN`.
