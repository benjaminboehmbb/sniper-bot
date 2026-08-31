# Pre-IU4 I2 Lifecycle Ledger / Runtime Gate / Authorization V2 — Independent Read-Only File-Exact Rereview — 2026-08-20

## 1. Independent decision

The frozen I2 package is **ready** for independent acceptance.  The sole prior
finding, `I2-IR-B1`, is independently closed by a separate transparent
resolution and a one-path supplemental file-exact mandate decision.  The
collector, implementation, evidence and freeze remain byte-identical.

```text
REREVIEW_ID:IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-IMPLEMENTATION-INDEPENDENT-READONLY-FILE-EXACT-REREVIEW
REREVIEW_RESULT:READY
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I2_IR_B1_INDEPENDENTLY_CLOSED:YES
I2_IMPLEMENTATION_ACCEPTED:YES
I3_AUTHORIZED:NO
I3_ENTERED:NO
ADAPTER_V2_AUTHORIZED:NO
ATOMIC_V2_AUTHORIZED:NO
ENFORCED_LOOP_AUTHORIZED:NO
ENFORCED_ACTIVATION_AUTHORIZED:NO
EXCHANGE_AUTHORIZED:NO
LIVE_AUTHORIZED:NO
```

No acceptance credit was taken from the resolution or supplemental decision
alone.  Their exact constraints, the canonical and frozen collector bytes,
the complete Capability evidence, original preservation boundary and fresh
read-only test results were independently verified before this record was
created.

## 2. Repository and controlling identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
BRANCH:main
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_BEHIND_ORIGIN:0
MAIN_AHEAD_OF_ORIGIN:6
```

| Controlling artifact | SHA-256 | Lines / entries | Independent result |
|---|---|---:|---|
| original I2 file-exact mandate | `bbf2968cfc1de02edb54e1c6ed47951818f7fd6840b10b5d0b7c6ef652eb0517` | 311 | MATCH / collector historically absent |
| I2 implementation evidence | `950b5b2aa11f3163f0aa1f49f03528ce688de1a5c7506cd12b905dadc55bd516` | 1,215 | MATCH / final Section 12 |
| initial independent I2 review | `5655a1761ab65f29a7d91099e93342999af54468eac299ecd63b11d42e225dda` | 359 | MATCH / `NOT_READY`, `I2-IR-B1` |
| independent-review resolution | `fbaf549867ea70ef1214204851da52b530bbf47e80762bd37086cdedec86ba53` | 158 | MATCH / complete |
| supplemental collector mandate decision | `a69bced4751ebbd608b0ff081079f5021c5f57430ec93c478e6b0b90c6c76228` | 171 | MATCH / `AUTHORIZED` |
| Preservation package | `3af14ff2e270d7d3ca09c1279da7d64e6d720630d06a0c5f45b6786237782037` | 1,318 | MATCH / unique entries / gzip PASS |
| Freeze manifest | `ad154c0eda13470920878873ed170368cc8f4c43591400a07592a77b179d9e16` | 58 | MATCH |

The original mandate was not rewritten.  The resolution and supplemental
decision are separate artifacts and do not claim that the collector was
originally authorized.

## 3. Independent closure of I2-IR-B1

The supplemental decision recognizes exactly one existing identity:

```text
PATH:live_l1/tools/collect_terminal_lease_host_closure.py
CANONICAL_SHA256:78b40014aa5660b0ca976033d7e712e4d0103e12775822f6471937dc71836099
FREEZE_SHA256:78b40014aa5660b0ca976033d7e712e4d0103e12775822f6471937dc71836099
LINES:423
CANONICAL_FREEZE_BYTEIDENTICAL:YES
AUTHORIZED_PATH_COUNT:1
AUTHORIZED_OPERATION:RECOGNIZE_EXISTING_FROZEN_IDENTITY_FOR_I2_ACCEPTANCE_ONLY
EDIT_AUTHORIZED:NO
EXECUTION_AUTHORIZED:NO
EVIDENCE_REGENERATION_AUTHORIZED:NO
RETROACTIVE_ORIGINAL_AUTHORIZATION_CLAIM:NO
```

The rereview independently confirmed that the source is an exact host-closure
collector: it compiles the test-owned fixture, enforces 32 probes, drives the
irreversible Yama `0,2,3` sequence, controls QMP S3 suspend/wakeup, validates
the native/kernel records and create-new serializes or merges evidence.

The same collector SHA is serialized by all three preserved evidence objects:

| Evidence artifact | SHA-256 | Collector binding |
|---|---|---|
| `yama-evidence-v2.json` | `b69f865c9d027aa7bdc315505e66b6efcb3a6756eb1aebc77c78f48d0c418979` | exact match |
| `suspend-evidence.json` | `3cb00529931d9d06275aa14178a5eda104673574f2612b17dd7c890ba7381c09` | exact match |
| `host-closure-evidence.json` | `83f54a0d47a60df22f0e45395e59ae74c784f088033c1ba9dbf3f11cd5ebd491` | exact match |

No second supplemental source, test, fixture, helper, configuration,
manifest, launcher or VM-definition path is authorized or claimed.  The
effective implementation boundary is exactly the original Section-4 set plus
this one frozen collector identity.

Therefore the authority gap identified by `I2-IR-B1` is closed without an
implementation byte change and without falsifying the historical original
mandate.

## 4. Independent Capability reconstruction

The rereview reran the independent read-only checker against the unchanged
Preservation package.  It did not call the production validator or execute
the collector.

```text
INDEPENDENT_CHECKS:685_PASS
ARTIFACT_IDENTITIES:8_PASS
CAPABILITY_JSON_SHA256:7baa6b2885567ce0b07a7b863f96b3c18a97a178aefe6535a5da8b8446a153ac
CAPABILITY_V14:PASS
FOUNDATION_RESULT:PASS
CERTIFICATION_TRIALS:10000
STARTUP_PROBES:32
MISSING_MANDATORY_SCENARIOS:[]
REVISION21_CLAUSE_IDS_UNIQUE:97/97_PASS
REVISION21_ABSOLUTE_POINTERS:97/97_PASS
REVISION21_POINTER_VALUES:97/97_PASS
REVISION21_COMPARISONS:97/97_PASS
REVISION21_COVERAGE_PASS_BLOCKED:97/0
REVISION21_COVERAGE_FINGERPRINT:8c81ed8dd7ac03bbaaf93c4911156cec4fe6dadff5b0e6f1b380a27dd24a5cd3
REVISION21_MACRO_FAMILIES:8/8_PASS
REVISION21_MACRO_REMOVAL_AUTHORIZATION:AUTHORIZED
FULL_REVISION21_SATURATION_CLAIMED:true
CANDIDATE_PROFILE_FINGERPRINT:12ee335fc0afa07452d2fe28563baccf726142314613d9a9bac3870104349b88
```

Every serialized `actual` value equals its independently resolved Evidence
Pointer.  Every simple, path-rule, artifact-identity and specialized resource
comparison passes.  The canonical serialization of all 97 rows reproduces
the exact controlling coverage fingerprint.

## 5. Host and timestamp evidence

The rereview independently retained the initial review's record-level result:

```text
YAMA_MODE_ORDER:0,2,3
YAMA_PROBES:96/96_PASS
YAMA_OPEN_BLOCKED:96/96_PASS
YAMA_RUNTIME_SOCKET_CREATIONS:0
YAMA_SENDMSG_CALLS:0
SUSPEND_PHASE_POINTS:32/32_PASS
SUSPEND_SLEEP_STATE:deep
SUSPEND_QMP_AND_KERNEL_S3:32/32_PASS
SUSPEND_CLOCK:CLOCK_BOOTTIME
SUSPEND_FATAL_SIGNAL:SIGKILL
TIMESTAMP_SOURCE:bpf_ktime_get_boot_ns
TIMESTAMP_SCENARIOS:8/8
TIMESTAMP_TRIALS_PER_SCENARIO:10000/10000
TIMESTAMP_RECORDS:260000/260000_PASS
TIMESTAMP_MISSING:0
TIMESTAMP_DUPLICATE:0
TIMESTAMP_UNEXPECTED:0
TIMESTAMP_INVALID_IDENTITY:0
TIMESTAMP_NONMONOTONE_TRIALS:0
TIMESTAMP_MANIFEST_SHA256:32dc3140965e4edf393bed9b287fe817e2e79a7b0b961e556b7bcaa4bc0ad878
```

The collector and evidence were not executed, rewritten, normalized or
regenerated during the rereview.

## 6. Fresh read-only test execution

All commands used the repository `.venv`, synthetic or test-owned temporary
inputs and `PYTHONDONTWRITEBYTECODE=1`.

| Verification | Count | Result |
|---|---:|---|
| combined nine mandated focused I2 modules | 61 | PASS |
| complete `tests/live_l1` suite | 375 | PASS |
| complete regression suite | 170 | PASS |
| AST parse of collector, mode-neutral gate and Capability validator | 3 | PASS |
| `git diff --check` | n/a | PASS |

There were no failures, errors or skips and no repository-local bytecode
write.  Test success supports the technical result; the independent
file-exact closure above controls acceptance of the prior finding.

## 7. Implementation and preservation identity

All key final source identities remain those accepted by the initial review,
including:

| Path | SHA-256 | Result |
|---|---|---|
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | MATCH |
| `live_l1/core/terminal_persistence_worker.py` | `04df9a859bf1c00bc2f521163b597fc159dfefd81e05c9c2cebdffe0792cb86a` | MATCH |
| `live_l1/state/iu4_lifecycle_ledger.py` | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` | MATCH |
| `live_l1/native/terminal_lease_fault_fixture.c` | `88733165949d9f0fecb9f195c548beface25ab5ff88cacadac6eeaafd344f62b` | MATCH |
| `live_l1/native/terminal_runtime_socket_lsm_guard.bpf.c` | `6c666b673e12a5a59244ae777a02fe4c0ef94ec3109c5d0eba61838118b635d9` | MATCH |
| `live_l1/tools/validate_terminal_lease_capability.py` | `11215eb265ef0e342ac836fd4fe630cdc7fdbd65a28c982029f9576474d3e927` | MATCH |
| `tests/live_l1/test_terminal_lease_capability.py` | `4a20f0695fa82da129214dd74267363970649ad566b784b610de7e362bf85926` | MATCH |
| host-closure collector | `78b40014aa5660b0ca976033d7e712e4d0103e12775822f6471937dc71836099` | MATCH / supplemental authority |

All twelve original Section-5 read-only paths retain their exact required
hashes and line counts, including Adapter V1, Atomic Coordinator,
`paper_artifacts.py`, the active loop, execution and the accepted I1 test
boundary.

The freeze directory remains mode `0555`.  The package and manifest remain
mode `0444`; the directory still contains exactly those two files.  Their
hashes did not change during resolution, mandate creation or rereview.

## 8. Runtime and authorization boundary

The sole mode-neutral gate remains fail-closed for ENFORCED in I2:

```text
ENFORCED_PASSED:false
ADAPTER_EXECUTION_ENABLED:false
STATE_MUTATION_ENABLED:false
ENFORCED_LOOP_ENTERED:NO
ADAPTER_V2_INVOKED:NO
ATOMIC_V2_CREATED:NO
EXCHANGE_OR_LIVE_MUTATION:NO
```

The supplemental collector decision grants no Atomic V2, Adapter V2,
active-seam, loop, recovery, owner-handoff, activation, Exchange or Live
authority.  In particular, accepting I2 does not begin or authorize I3.

## 9. Findings

### BLOCKER

None.

### HIGH

None.

### MEDIUM

None.

### LOW

None.

The prior finding is independently closed:

- `I2-IR-B1`: PASS — the exact collector identity is now covered by a
  separate one-path supplemental mandate decision; canonical, frozen and all
  three serialized collector identities match, while the original scope gap
  remains transparently recorded.

## 10. Scope and rereview side effects

The resolution and mandate decision created governance records only.  The
rereview modified no implementation, test, configuration, freeze, evidence,
runtime state, R3/Workstation artifact, Research, Exchange or Live path.  It
did not execute the collector or regenerate evidence.

No Git stage, commit, fetch, push, cleanup or deletion occurred.  Foreign
artifacts and processes were not changed.  The excluded bundle script was not
read, executed, changed, staged or committed.

This uniquely named rereview record is the only canonical file created by the
substantive rereview.

## 11. Acceptance boundary and next step

This `READY` verdict accepts only I2 Lifecycle Ledger / Runtime Gate /
Authorization V2 at the original Section-4 scope plus the single exact
supplemental collector identity.  It does not authorize I3 Atomic
State/Transaction V2 or any later package.

The next eligible governance action is a separately requested and separately
reviewed file-exact mandate for I3.  No such mandate is created by this
rereview, and I3 must remain unstarted until that later authorization exists.

```text
NEXT_STEP:AWAIT_SEPARATE_I3_FILE_EXACT_MANDATE_AUTHORIZATION
```

## 12. Final verdict

```text
I2_FOUNDATION:PASS
I2_CAPABILITY_V14:PASS
I2_REVISION21_LEDGER:97/97_PASS
I2_YAMA_0_2_3:96/96_PASS
I2_REAL_SUSPEND_RESUME:32/32_PASS
I2_EXTERNAL_KERNEL_TIMESTAMPS:260000/260000_PASS
I2_TEST_SUITES:PASS
I2_PRESERVATION:PASS
I2_ENFORCED_NON_ENTRY:PASS
I2_ORIGINAL_SCOPE_HISTORY_PRESERVED:PASS
I2_SUPPLEMENTAL_COLLECTOR_SCOPE:PASS
I2_IR_B1:INDEPENDENTLY_CLOSED
I2_INDEPENDENT_ACCEPTANCE:READY
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
I3_AUTHORIZED:NO
I3_ENTERED:NO
NEXT_STEP:AWAIT_SEPARATE_I3_FILE_EXACT_MANDATE_AUTHORIZATION
```
