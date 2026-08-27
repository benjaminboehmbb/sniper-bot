# Pre-IU4 Enforced Paper Active Runtime Integration Specification Revision 21 — Terminal R3 Handoff — 2026-08-19

## 1. Decision

This record performs the terminal R3 handoff for the exact Revision 21
specification identity accepted by its independent read-only rereview.

```text
HANDOFF_RESULT: COMPLETE
REVISION: 21
ONE_SHOT_VALIDATOR_ELIGIBLE: YES
ONE_SHOT_VALIDATOR_EXECUTION_COUNT_AT_HANDOFF: 0
FINAL_R3_ATTESTATION_BOUND: NO
IMPLEMENTATION_AUTHORIZED: NO
ENFORCED_ACTIVATION_AUTHORIZED: NO
EXCHANGE_AUTHORIZED: NO
LIVE_AUTHORIZED: NO
```

The handoff authorizes exactly one read-only execution of the frozen postrun
validator against the terminal artifact named below. It does not authorize a
run start, retry, resume, runtime mutation, scheduler mutation, Workstation
file creation, implementation, activation, Exchange, or Live.

## 2. Repository and specification identity

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
SPECIFICATION_PATH:docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
SPECIFICATION_SHA256:ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0
SPECIFICATION_LINES:4605
REREVIEW_PATH:docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md
REREVIEW_SHA256:6618955e67bf9e11798c103eb7d01823dc2ece4c39a66575dbb668c4162c0c7c
REREVIEW_LINES:752
REREVIEW_VERDICT:READY
REREVIEW_FINDINGS_BLOCKER_HIGH_MEDIUM_LOW:0/0/0/0
```

## 3. Frozen validator identity

The validator is the existing untracked, frozen X1 artifact. It remains
unchanged and is not copied to or persisted on the Workstation. Its exact
bytes are supplied as standard input to the Workstation Python interpreter.

```text
VALIDATOR_PATH:/home/benja/projects/sniper-bot/live_l1/tools/validate_iu4_shadow_observation.py
VALIDATOR_SHA256:a87497a249d837ea0d8f8f4612561576e915419f9100dcb256554900f9c5c0f0
VALIDATOR_LINES:947
VALIDATOR_TEST_PATH:/home/benja/projects/sniper-bot/tests/live_l1/test_validate_iu4_shadow_observation.py
VALIDATOR_TEST_SHA256:e72439919c29a9a50cf6bcbfff0b18f95910ba28348d85a079326b2ab6731ba5
VALIDATOR_TEST_LINES:396
```

No synthetic test or preliminary invocation against the terminal artifact is
part of this handoff. The next invocation is the sole governed execution.

## 4. Terminal R3 execution identity

```text
EXECUTION_HOST:WORKSTATION
SCHEDULER_TASK:Codex-IU4-Workstation-Full-History-Shadow-C7CE045-20260817
SCHEDULER_STATUS:READY
SCHEDULER_LAST_RESULT:0
WORKTREE:/home/workstation/worktrees/sniper-bot/iu4-workstation-full-history-shadow-c7ce045-20260817
WORKTREE_HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
WORKTREE_STATUS:CLEAN
R3_PROCESS_ACTIVE:NO
LAUNCHER:/home/workstation/runs/sniper-bot/launchers/launch_iu4_full_history_shadow_c7ce045_atomic-c7f188_live-state-r3_20260817.sh
LAUNCHER_SHA256:871434f69fc5c9308da5e57a854b20c6e07da19f05554dc37089fe5b8decbc72
OUTPUTROOT:/home/workstation/runs/sniper-bot/pee_iu4_workstation_full_history_shadow_observation_1042658_c7ce045_atomic-c7f188_live-state-r3_20260817
STARTED_UTC:2026-08-17T14:28:49.674478438Z
FINISHED_UTC:2026-08-18T11:44:07.587241387Z
PROCESS_EXIT_CODE:0
STDERR_SIZE_BYTES:0
```

## 5. Terminal artifact identity

```text
EVIDENCE_PATH:/home/workstation/runs/sniper-bot/pee_iu4_workstation_full_history_shadow_observation_1042658_c7ce045_atomic-c7f188_live-state-r3_20260817/iu4_shadow_observation_evidence.json
EXPECTED_EVIDENCE_SHA256:15158db36ba2634cb7563e0c2096cc24bfd09dcb3b8b3df47862654fc3286767
JOURNAL_PATH:/home/workstation/runs/sniper-bot/pee_iu4_workstation_full_history_shadow_observation_1042658_c7ce045_atomic-c7f188_live-state-r3_20260817/iu4_shadow_observation_evidence.json.records.jsonl
EXPECTED_JOURNAL_SHA256:9bf229c53228171baf02b7b3403459eda9c838bece700f34465a1d2db3353a31
EXPECTED_LAST_JOURNAL_ENTRY_SHA256:dc95551cf499f54bfefd7b7fe8b5d28bff50af880085179abc2d1bb2e9d50bef
EXPECTED_RECORD_COUNT:1042658
EXPECTED_EVIDENCE_FINGERPRINT:b4a1c300019e7e87e53db01e479aecb041910aed0d5150794cae63276adf7cc6
```

## 6. Input, policy, and runtime-state binding

The final pre-/post-run hash files are identical for all immutable inputs.

```text
MARKET_SHA256:902d10b1d7678777bd23140ff459b9c5eaa9ef7d968bab7ab6e09926bfbfba8a
RAW_SOURCE_SHA256:2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104
ATOMIC_STATE_SHA256:c7f188c44497b6d4339b24fe8e239d2f3611681d8ac784dc871568e3b1b567b1
COORDINATOR_ID:IU4-WORKSTATION-REPLAY-BTCUSDT-24eda737081c1b3d
THROTTLE_PROFILE_ID:PEE_RATE_OBSERVED_BOUNDARY_001
THROTTLE_MODEL_VERSION:PEE_RATE_V1
THROTTLE_POLICY_FINGERPRINT:ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada
THROTTLE_PROFILE_SHA256:b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7
ECONOMICS_SHA256:f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86
SEED_5M_SHA256:6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5
RUNTIME_STATE_S2_SHA256:92c65ec3e379d9ee6b008f4887f2f0da73d24838220b9d94920d0903f3f803f8
RUNTIME_STATE_S4_SHA256:315301fc790fbc368c605418e88dc044240d53e769bcbba026fa638906fcbe2f
```

## 7. Safety binding

```text
OPERATIONAL_PROFILE:PAPER
IU4_MODE:SHADOW
IU4_ENFORCED:false
EXCHANGE:false
LIVE:false
SOURCE_STATE_MUTATION_ALLOWED:false
```

## 8. Frozen one-shot command

The following command is frozen and may execute exactly once. Shell standard
input transfers the exact validator bytes; it creates no Workstation file.

```bash
ssh -o BatchMode=yes workstation-win wsl.exe -d Ubuntu -- /usr/bin/python3 - --evidence /home/workstation/runs/sniper-bot/pee_iu4_workstation_full_history_shadow_observation_1042658_c7ce045_atomic-c7f188_live-state-r3_20260817/iu4_shadow_observation_evidence.json --expected-record-count 1042658 --expected-repository-commit c7ce0452aa2ccbf08c462784d68fa07b3dfe9595 < /home/benja/projects/sniper-bot/live_l1/tools/validate_iu4_shadow_observation.py
```

Any nonzero return, `BLOCKED` result, identity mismatch, interrupted
connection, or incomplete output is terminally not a PASS and must not be
retried under this handoff.

## 9. Next governed action

Execute the frozen command exactly once. Only a complete exit-zero validator
`PASS` whose reported identities match this handoff may be bound into the
Revision 21 final R3 attestation. A separate file-exact I1 mandate remains
forbidden until that final attestation exists and says `PASS`.
