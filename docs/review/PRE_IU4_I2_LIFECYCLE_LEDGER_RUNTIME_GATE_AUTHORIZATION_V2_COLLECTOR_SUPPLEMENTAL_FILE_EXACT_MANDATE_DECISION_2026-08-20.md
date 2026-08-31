# Pre-IU4 I2 Lifecycle Ledger / Runtime Gate / Authorization V2 — Collector Supplemental File-Exact Mandate Decision — 2026-08-20

## 1. Mandate decision

This decision grants a supplemental file-exact I2 acceptance mandate for one
already existing and frozen host-closure collector identity.  It closes the
authority gap identified as `I2-IR-B1` without changing implementation or
regenerating evidence.

```text
MANDATE_DECISION_ID:IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-COLLECTOR-SUPPLEMENTAL-FILE-EXACT-MANDATE-DECISION
MANDATE_DECISION_RESULT:AUTHORIZED
IMPLEMENTATION_PACKAGE:I2_ONLY
AUTHORITY_KIND:SUPPLEMENTAL_FILE_EXACT_ACCEPTANCE_BOUNDARY
AUTHORIZED_PATH_COUNT:1
EXISTING_FROZEN_IDENTITY_RECOGNIZED:YES
COLLECTOR_EDIT_AUTHORIZED:NO
COLLECTOR_EXECUTION_AUTHORIZED:NO
EVIDENCE_REGENERATION_AUTHORIZED:NO
RETROACTIVE_ORIGINAL_SECTION4_AUTHORIZATION_CLAIM:NO
I2_INDEPENDENT_ACCEPTANCE_PENDING:YES
I3_AUTHORIZED:NO
I3_ENTERED:NO
ADAPTER_V2_AUTHORIZED:NO
ATOMIC_V2_AUTHORIZED:NO
ENFORCED_LOOP_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

The historical original mandate remains unchanged and historically accurate.
This decision does not assert that the collector was authorized before it was
created or used.  It separately recognizes the exact frozen identity for the
purpose of resolving the current I2 acceptance boundary.

## 2. Canonical and controlling identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_DIVERGENCE_BEHIND_AHEAD:0/6
```

| Controlling artifact | SHA-256 | Lines / entries | Result |
|---|---|---:|---|
| original I2 file-exact mandate | `bbf2968cfc1de02edb54e1c6ed47951818f7fd6840b10b5d0b7c6ef652eb0517` | 311 | unchanged; collector absent |
| I2 implementation evidence | `950b5b2aa11f3163f0aa1f49f03528ce688de1a5c7506cd12b905dadc55bd516` | 1,215 | unchanged |
| independent I2 review | `5655a1761ab65f29a7d91099e93342999af54468eac299ecd63b11d42e225dda` | 359 | `NOT_READY`, `I2-IR-B1` |
| independent-review resolution | `fbaf549867ea70ef1214204851da52b530bbf47e80762bd37086cdedec86ba53` | 158 | complete; separate mandate required |
| Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 | unchanged |
| Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 58 | unchanged |

## 3. Exact supplemental file authority

Exactly one path and identity is recognized:

| Path | SHA-256 | Lines | Authorized purpose | Authorized operation |
|---|---|---:|---|---|
| `live_l1/tools/collect_terminal_lease_host_closure.py` | `78b40014aa5660b0ca976033d7e712e4d0103e12775822f6471937dc71836099` | 423 | disposable-host Yama 0/2/3 collection, QMP ACPI-S3 suspend/resume collection, strict partial-evidence validation and merge | recognize existing frozen identity for I2 acceptance only |

No modification, execution, replacement, rename, move, generated variant or
additional consumer of this path is authorized.  A byte, line-count or path
change invalidates this decision and requires a new file-exact mandate before
any further acceptance review.

## 4. Exact evidence binding

The collector identity is already bound by the frozen evidence chain:

| Evidence artifact | SHA-256 | Binding |
|---|---|---|
| `yama-evidence-v2.json` | `b69f865c9d027aa7bdc315505e66b6efcb3a6756eb1aebc77c78f48d0c418979` | serializes collector, guest, fixture and 96 Yama records |
| `suspend-evidence.json` | `3cb00529931d9d06275aa14178a5eda104673574f2612b17dd7c890ba7381c09` | serializes collector, guest, fixture and 32 S3 records |
| `host-closure-evidence.json` | `83f54a0d47a60df22f0e45395e59ae74c784f088033c1ba9dbf3f11cd5ebd491` | strict merged identity consumed by Capability V14 |
| `terminal_lease_capability_v14.json` | `7baa6b2885567ce0b07a7b863f96b3c18a97a178aefe6535a5da8b8446a153ac` | final 97/97 Capability result |
| external timestamp manifest | `32dc3140965e4edf393bed9b287fe817e2e79a7b0b961e556b7bcaa4bc0ad878` | 260,000/260,000 external kernel records |

The Preservation package contains the exact collector bytes and all evidence
artifacts above.  This decision grants no authority to regenerate, normalize,
rewrite or replace them.

## 5. Effective file-exact boundary

For the pending I2 rereview only, the effective file-exact implementation
boundary is:

```text
EFFECTIVE_I2_SCOPE = ORIGINAL_I2_MANDATE_SECTION_4
                   + live_l1/tools/collect_terminal_lease_host_closure.py
```

The addition is exact and singular.  Governance documents created to record
the review, resolution, this decision and the rereview remain governance
records rather than I2 runtime implementation paths.

No other current untracked or tracked path receives authority.  In
particular, this decision does not authorize a new collector test, helper,
manifest, configuration, launcher, VM definition, QEMU artifact or host
script.

## 6. Required rereview checks

The fresh independent read-only file-exact rereview must, at minimum:

1. verify this decision and the resolution as separate immutable records;
2. rehash the canonical collector and its copy inside the Preservation
   package and require both identities to match this decision;
3. verify that the three host-closure evidence objects serialize the same
   collector identity and remain bound to the final Capability JSON;
4. reverify the 97/97 coverage fingerprint, host-closure counts and complete
   external timestamp manifest without executing the collector;
5. verify the original Section-5 preservation hashes and unchanged freeze;
6. confirm that no second supplemental implementation path exists;
7. confirm ENFORCED non-entry and every I3/I4/I5/Exchange/Live
   non-authorization; and
8. issue an independent `READY` or `NOT_READY` record without modifying
   implementation, freeze or evidence.

## 7. Invalidation and fail-closed conditions

The rereview must return `NOT_READY` if any of the following occurs:

- collector path, SHA-256 or line count differs;
- collector bytes in the Preservation package differ from the canonical
  collector;
- a host-closure artifact, Capability JSON, timestamp manifest, coverage
  fingerprint, freeze hash or original preservation identity differs;
- another implementation path is claimed under this decision;
- the collector is executed or evidence is regenerated during the rereview;
- Git, foreign artifacts, runtime state, Exchange or Live is mutated; or
- I3 is started or treated as authorized.

## 8. Preservation and prohibited scope

The original mandate Sections 5, 8, 13 and 14 otherwise remain fully
controlling.  This decision does not authorize Adapter V2, Atomic V2, S4V2,
Entry Quote, Progress/Loss migration, loop or execution wiring, Genesis,
recovery, owner handoff, ENFORCED entry, activation, Exchange or Live.

It does not authorize Git staging, commit, fetch, push, cleanup or deletion.
Foreign artifacts remain untouched.  The excluded bundle script remains
unread, unexecuted and unchanged.

## 9. Decision gate and next step

```text
SUPPLEMENTAL_PATHS:1/1_AUTHORIZED
COLLECTOR_IDENTITY_EXACT:PASS
COLLECTOR_BYTES_MUTABLE:NO
COLLECTOR_EXECUTION_AUTHORIZED:NO
EVIDENCE_REGENERATION_AUTHORIZED:NO
ORIGINAL_MANDATE_REWRITTEN:NO
ORIGINAL_SCOPE_GAP_ACKNOWLEDGED:YES
I2_SELF_CERTIFIED:NO
I2_INDEPENDENT_ACCEPTANCE_PENDING:YES
I3_AUTHORIZED:NO
MANDATE_DECISION_RESULT:AUTHORIZED
```

The exact next governance step is:

```text
IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW
```

Only that fresh rereview may accept I2.  Even a `READY` I2 rereview does not
itself authorize I3; I3 still requires a separate, later file-exact mandate.
