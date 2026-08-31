# Pre-IU4 I2 Lifecycle Ledger / Runtime Gate / Authorization V2 — Independent Read-Only File-Exact Review Resolution — 2026-08-20

## 1. Resolution decision

The single finding from the independent I2 file-exact review is resolved by
a separate supplemental file-exact mandate decision for the already frozen
host-closure collector identity.  No implementation file is changed by this
resolution.

```text
RESOLUTION_ID:IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REVIEW-RESOLUTION
RESOLUTION_RESULT:COMPLETE
I2_IR_B1_STATUS:RESOLVED_BY_SEPARATE_SUPPLEMENTAL_MANDATE_DECISION
BLOCKER_OPEN:0
HIGH_OPEN:0
MEDIUM_OPEN:0
LOW_OPEN:0
I2_INDEPENDENT_ACCEPTANCE_PENDING:YES
I3_AUTHORIZED:NO
I3_ENTERED:NO
ENFORCED_LOOP_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

This is a governance-side resolution record.  It does not independently
accept or self-certify I2.  Only a fresh independent read-only file-exact
rereview of the resolution, supplemental mandate, unchanged implementation
and unchanged freeze may accept I2.

## 2. Canonical and controlling identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_DIVERGENCE_BEHIND_AHEAD:0/6
```

| Controlling artifact | SHA-256 | Lines | Result |
|---|---|---:|---|
| I2 file-exact mandate | `bbf2968cfc1de02edb54e1c6ed47951818f7fd6840b10b5d0b7c6ef652eb0517` | 311 | unchanged / original Section-4 ceiling |
| I2 implementation evidence | `950b5b2aa11f3163f0aa1f49f03528ce688de1a5c7506cd12b905dadc55bd516` | 1,215 | unchanged / final Section 12 |
| independent I2 review | `5655a1761ab65f29a7d91099e93342999af54468eac299ecd63b11d42e225dda` | 359 | `NOT_READY`, `I2-IR-B1` |
| Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 entries | unchanged |
| Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 58 | unchanged |

## 3. Finding resolved

### I2-IR-B1 — Evidence-producing source path outside original Section 4

The review correctly found that:

```text
PATH:live_l1/tools/collect_terminal_lease_host_closure.py
SHA256:78b40014aa5660b0ca976033d7e712e4d0103e12775822f6471937dc71836099
LINES:423
ORIGINAL_I2_SECTION4_LISTED:NO
I2_EVIDENCE_DEPENDENCY:YES
PRESERVED_IN_FREEZE:YES
```

The collector is not incidental.  It compiles the test-owned native fixture,
collects the Yama 0/2/3 records, controls QMP suspend/wakeup, validates the
guest and kernel records and merges the strict host-closure evidence consumed
by the final Capability-V14 run.

The original mandate remains historically accurate: it did not authorize
this path.  This resolution does not rewrite that history and does not claim
that the collector was originally within Section 4.

The finding is closed through a separate, explicit supplemental file-exact
mandate decision with the following required properties:

1. it adds exactly this one existing path and exact frozen identity to the
   effective I2 acceptance boundary;
2. it grants no authority to edit, regenerate or replace the collector;
3. it grants no additional source, test, documentation, fixture,
   configuration or evidence path;
4. it binds the collector only to disposable-host Yama/S3 evidence
   acquisition and merge validation;
5. it preserves the complete original Section-5 read-only boundary;
6. it explicitly records that the authority is supplemental and does not
   create a false claim of original authorization; and
7. it leaves I3, I4, I5, ENFORCED entry, activation, Exchange and Live
   unauthorized.

## 4. No implementation correction

The technical implementation and evidence require no byte change.  The
independent review already reconstructed:

```text
CAPABILITY_V14:PASS
REVISION21_COVERAGE:97/97_PASS
YAMA_0_2_3:96/96_PASS
REAL_SUSPEND_RESUME:32/32_PASS
EXTERNAL_KERNEL_TIMESTAMPS:260000/260000_PASS
FOCUSED_TESTS:61/61_PASS
LIVE_L1_TESTS:375/375_PASS
REGRESSION_TESTS:170/170_PASS
```

Changing the collector or regenerating the frozen evidence would create a new
technical identity and is outside this resolution.  The exact collector SHA,
all three host-closure evidence hashes, Capability JSON hash, coverage
fingerprint and Preservation package hash remain controlling.

## 5. Effective scope after the separate decision

The effective I2 file-exact acceptance scope is the union of:

1. every original Section-4 path in the I2 file-exact mandate; and
2. exactly `live_l1/tools/collect_terminal_lease_host_closure.py` at SHA-256
   `78b40014aa5660b0ca976033d7e712e4d0103e12775822f6471937dc71836099`,
   423 lines, once the separate supplemental decision is filed.

The union does not authorize any additional path.  Governance records created
for the resolution, mandate decision and rereview are review-chain artifacts,
not I2 runtime implementation files.

## 6. Preservation and non-authorizations

The freeze remains unchanged and read-only.  The twelve original Section-5
preservation identities remain controlling.  Adapter V1, Atomic Coordinator,
the active loop, execution, I1, state, production journals, Workstation/R3,
Research, GS, RCC002, Exchange and Live are not changed or reinterpreted.

No Git stage, commit, fetch, push, cleanup or deletion is authorized or
performed.  Foreign artifacts remain untouched.  The excluded bundle script
is not read, executed, changed, staged or committed.

## 7. Completion gate and next step

```text
I2_IR_B1_RESOLUTION:PASS
COLLECTOR_TECHNICAL_IDENTITY_UNCHANGED:PASS
COLLECTOR_ORIGINAL_SECTION4_AUTHORIZATION_CLAIM:NO
SUPPLEMENTAL_FILE_EXACT_DECISION_REQUIRED:YES
I2_SELF_CERTIFIED:NO
I2_INDEPENDENT_ACCEPTANCE_PENDING:YES
I3_AUTHORIZED:NO
RESOLUTION_RESULT:COMPLETE
```

The exact next governance step is:

```text
IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-COLLECTOR-SUPPLEMENTAL-FILE-EXACT-MANDATE-DECISION
```

After that decision is filed, a fresh independent read-only file-exact
rereview must verify the decision, this resolution, the exact collector,
unchanged freeze, preserved Capability evidence, original scope and all
non-authorizations.  Only that rereview may issue `READY` for I2.
