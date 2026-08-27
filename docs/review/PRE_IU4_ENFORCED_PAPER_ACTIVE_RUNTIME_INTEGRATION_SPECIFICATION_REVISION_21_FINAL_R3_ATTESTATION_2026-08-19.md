# Pre-IU4 Enforced Paper Active Runtime Integration Specification Revision 21 — Final R3 Attestation — 2026-08-19

## 1. Final decision

The terminal R3 artifact bound by the Revision 21 handoff passed the frozen
postrun validator in its sole governed execution. This record binds the
complete terminal result to the exact code, input, profile, evidence,
specification, rereview, handoff, and validator identities below.

```text
FINAL_R3_RESULT: PASS
REVISION: 21
VALIDATOR_EXECUTION_COUNT: 1
VALIDATOR_EXIT_CODE: 0
VALIDATOR_RESULT: PASS
VALIDATOR_RETRY_AUTHORIZED: NO
R3_FINAL_ATTESTATION_BOUND: YES
SPECIFICATION_IMPLEMENTATION_READY: YES
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

Observed terminally at `2026-08-19T07:55:22Z`.

## 2. Governance-chain identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
REVISION_21_SPECIFICATION:docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
REVISION_21_SPECIFICATION_SHA256:ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0
REVISION_21_SPECIFICATION_LINES:4605
REVISION_21_REREVIEW:docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md
REVISION_21_REREVIEW_SHA256:6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c
REVISION_21_REREVIEW_LINES:752
REVISION_21_REREVIEW_VERDICT:READY
REVISION_21_REREVIEW_FINDINGS_BLOCKER_HIGH_MEDIUM_LOW:0/0/0/0
TERMINAL_R3_HANDOFF:docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_TERMINAL_R3_HANDOFF_2026-08-19.md
TERMINAL_R3_HANDOFF_SHA256:0aecf831429076a7b732ca6de2482ba02384792919c3f76a3232c1ef27863b2e
TERMINAL_R3_HANDOFF_LINES:140
TERMINAL_R3_HANDOFF_RESULT:COMPLETE
```

## 3. Code and execution identity

```text
CANONICAL_HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
WORKSTATION_WORKTREE:/home/workstation/worktrees/sniper-bot/iu4-workstation-full-history-shadow-c7ce045-20260817
WORKSTATION_WORKTREE_HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
WORKSTATION_WORKTREE_STATUS:CLEAN
EXECUTION_HOST:WORKSTATION
SCHEDULER_TASK:Codex-IU4-Workstation-Full-History-Shadow-C7CE045-20260817
SCHEDULER_FINAL_STATUS:READY
SCHEDULER_FINAL_RESULT:0
R3_PROCESS_ACTIVE_AT_HANDOFF:NO
LAUNCHER:/home/workstation/runs/sniper-bot/launchers/launch_iu4_full_history_shadow_c7ce045_atomic-c7f188_live-state-r3_20260817.sh
LAUNCHER_SHA256:871434f69fc5c9308da5e57a854b20c6e07da19f05554dc37089fe5b8decbc72
PROCESS_EXIT_CODE:0
STDERR_SIZE_BYTES:0
```

## 4. Frozen validator identity and one-shot execution

```text
VALIDATOR_PATH:/home/benja/projects/sniper-bot/live_l1/tools/validate_iu4_shadow_observation.py
VALIDATOR_SHA256:a87497a249d837ea0d8f8f4612561576e915419f9100dcb256554900f9c5c0f0
VALIDATOR_LINES:947
VALIDATOR_EXECUTION_TRANSPORT:X1_EXACT_BYTES_OVER_SSH_STDIN
WORKSTATION_VALIDATOR_FILE_CREATED:NO
VALIDATOR_EXECUTION_SEQUENCE:1_OF_1
VALIDATOR_EXIT_CODE:0
VALIDATOR_RESULT:PASS
```

The validator performed read-only streaming validation of the evidence and
its evidence-bound sibling journal. It detected no input change during either
read. No preliminary run, retry, resume, or second terminal-artifact
invocation occurred.

## 5. Evidence identity and validator result

```text
OUTPUTROOT:/home/workstation/runs/sniper-bot/pee_iu4_workstation_full_history_shadow_observation_1042658_c7ce045_atomic-c7f188_live-state-r3_20260817
EVIDENCE_PATH:/home/workstation/runs/sniper-bot/pee_iu4_workstation_full_history_shadow_observation_1042658_c7ce045_atomic-c7f188_live-state-r3_20260817/iu4_shadow_observation_evidence.json
EVIDENCE_SHA256:15158db36ba2634cb7563e0c2096cc24bfd09dcb3b8b3df47862654fc3286767
EVIDENCE_FINGERPRINT:b4a1c300019e7e87e53db01e479aecb041910aed0d5150794cae63276adf7cc6
JOURNAL_PATH:/home/workstation/runs/sniper-bot/pee_iu4_workstation_full_history_shadow_observation_1042658_c7ce045_atomic-c7f188_live-state-r3_20260817/iu4_shadow_observation_evidence.json.records.jsonl
JOURNAL_SHA256:9bf229c53228171baf02b7b3403459eda9c838bece700f34465a1d2db3353a31
JOURNAL_SIZE_BYTES:1498872502
LAST_JOURNAL_ENTRY_SHA256:dc95551cf499f54bfefd7b7fe8b5d28bff50af880085179abc2d1bb2e9d50bef
RECORD_COUNT:1042658
UNIQUE_SOURCE_INTENT_IDS:1042658
UNIQUE_IU4_REQUEST_IDS:1042658
FINAL_LEGACY_POSITION:FLAT
FINAL_IU4_POSITION:FLAT
```

Validator counts:

| Class | Value |
| --- | ---: |
| status `COMMITTED` | 222 |
| status `NOOP` | 1,042,436 |
| status `REJECTED` | 0 |
| action `OPEN_LONG` | 111 |
| action `CLOSE_LONG` | 111 |
| action `OPEN_SHORT` | 0 |
| action `CLOSE_SHORT` | 0 |
| action `NOOP` | 1,042,436 |
| autonomous exits | 111 |
| loss-cluster vetoes | 286 |

The action counts sum to the exact record count. The 111 opens and 111 closes
are balanced, and both final positions are `FLAT`.

## 6. Immutable input identity

```text
RAW_SOURCE_SHA256:2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104
NORMALIZED_MARKET_SHA256:902d10b1d7678777bd23140ff459b9c5eaa9ef7d968bab7ab6e09926bfbfba8a
ATOMIC_STATE_SHA256:c7f188c44497b6d4339b24fe8e239d2f3611681d8ac784dc871568e3b1b567b1
COORDINATOR_ID:IU4-WORKSTATION-REPLAY-BTCUSDT-24eda737081c1b3d
RUNTIME_STATE_S2_SHA256:92c65ec3e379d9ee6b008f4887f2f0da73d24838220b9d94920d0903f3f803f8
RUNTIME_STATE_S2_LINES:1042658
RUNTIME_STATE_S4_SHA256:315301fc790fbc368c605418e88dc044240d53e769bcbba026fa638906fcbe2f
RUNTIME_STATE_S4_LINES:1042658
```

The recorded pre-run and post-run hashes for immutable source, normalized
market data, atomic state, seed, economics, throttle profile, and requirements
are identical.

## 7. Profile and policy identity

```text
OPERATIONAL_PROFILE:PAPER
IU4_MODE:SHADOW
THROTTLE_PROFILE_ID:PEE_RATE_OBSERVED_BOUNDARY_001
THROTTLE_MODEL_VERSION:PEE_RATE_V1
THROTTLE_POLICY_FINGERPRINT:ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada
THROTTLE_PROFILE_SHA256:b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7
ECONOMICS_SHA256:f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86
SEED_5M_SHA256:6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5
```

## 8. Safety identity

```text
SOURCE_STATE_MUTATION_ALLOWED:false
IU4_ENFORCED:false
EXCHANGE:false
LIVE:false
RUN_RETRY_AUTHORIZED:NO
VALIDATOR_RETRY_AUTHORIZED:NO
```

This PASS is an offline PAPER/SHADOW R3 result. It does not authorize IU4
ENFORCED, Exchange connectivity, live trading, source-state mutation, a new
Workstation run, or a validator rerun.

## 9. Completion and next step

The exact Revision 21 governance chain is now terminally complete through
final R3 `PASS`. The specification is implementation-ready but this record is
not an implementation mandate.

The only next authorized governance action is to create a separate,
explicit, file-exact mandate for **I1 Characterization / Pure Control
Extraction**. That mandate must enumerate every authorized file and preserve
all Revision 21 non-activation boundaries. No I1 code change may precede it.

```text
R3_TERMINAL_HANDOFF:PASS
FROZEN_POSTRUN_VALIDATOR:PASS
FINAL_IDENTITY_BINDING:PASS
FINAL_R3_ATTESTATION:PASS
NEXT_GOVERNANCE_ACTION:IU4-I1-CHARACTERIZATION-PURE-CONTROL-EXTRACTION-FILE-EXACT-MANDATE
```
