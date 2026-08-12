# Pre-IU-4 X1 100K SHADOW Observation Gate Evidence — 2026-08-12

## Status

**100,000-RECORD X1 SHADOW GATE DEFINED AND LOCALLY VERIFIED — RUN NOT STARTED**

The user approved continuation after the observation-writer branch integration
on 2026-08-12. This unit defines the next bounded gate; it does not execute the
observation.

## Gate contract

- execution host: X1 only;
- maximum/requested observations: exactly `100,000`;
- approximate market duration: `69.44` days of contiguous one-minute rows;
- observation mode: SHADOW;
- IU4 adapter scope: disposable sandbox only;
- bound atomic source: read-only;
- approved throttle profile remains required;
- evidence persistence: hash-chained append journal plus atomic checkpoint;
- final complete evidence: schema version 2 with bound journal identity;
- IU4 ENFORCED: disabled;
- Exchange: disabled;
- Live: disabled.

The hard implementation ceiling is raised only from `10,000` to `100,000`.
`100,000` is accepted only when explicitly configured and when
`requested_max_ticks <= configured_max_records`. `100,001` remains rejected
fail-closed.

## Resource and data-readiness evidence

- X1 free workspace storage at review: `951 GB`;
- previous 10K observation raw outputs:
  - final observation evidence: `11,505,376` bytes;
  - runtime log: `24,171,436` bytes;
  - captured stdout: `24,172,096` bytes;
- conservative projected 100K raw-output requirement: below `1 GB`;
- available/projected storage ratio: greater than `950:1`.

Local data availability is independently established by the preserved 200K
IU-3 run manifest:

- manifest SHA-256:
  `19b087a88be942af9d848e0e447dc67826320602fbb9008af599bcd166d3c037`;
- normalized rows: `200,000`;
- interval: `2017-08-17 04:00:00+00:00` through
  `2018-01-03 10:23:00+00:00`;
- normalized 200K slice SHA-256:
  `0b38752473c3082fc20c206ee35b0fd2f0f2e26a6b1426501bc74a667f5d4d6f`;
- immutable source CSV SHA-256:
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`.

The exact first 100,000 normalized rows must be rebuilt and hashed before a
run. This gate does not permit reuse of an unverified temporary input.

## Required run acceptance checks

Any separately authorized 100K run must validate:

1. `100,000/100,000 (100.00%)` exact ordered records;
2. unique source-intent IDs and exact observation sequence `1..100,000`;
3. checkpoint and journal counts, byte length, SHA-256, entry-chain head, and
   final evidence fingerprint;
4. zero source-state mutation and unchanged source manifest/fingerprint;
5. all position-before, action, and position-after parity flags;
6. every autonomous exit accounted as matching committed close or complete
   state-identical guard-divergence NOOP evidence;
7. approved throttle-profile identity and compliance;
8. final legacy and IU4 sandbox states;
9. runtime error/failure markers; and
10. input slice SHA-256 before and after execution.

Any mismatch stops fail-closed and is evidence, not a reason to weaken gates
or alter the input.

## Verification

```text
Focused observation-gate tests
16/16 passed

tests/live_l1
314/314 passed

tests/regression
170/170 passed

Unique full-suite total
484/484 passed
```

`py_compile` and `git diff --check` passed. The foreign untracked file
`scripts/build_rcc002_spec_bundle.py` was not read, modified, staged, or
committed.

## Next gate

After branch integration, the separately authorized next action is
`IU4-X1-100K-SHADOW-OBSERVATION FREIGEBEN`. That authorization may prepare the
exact input and run only this bounded X1 SHADOW observation. It does not
authorize Workstation execution, IU4 ENFORCED, Exchange, Live, or source-state
mutation.
