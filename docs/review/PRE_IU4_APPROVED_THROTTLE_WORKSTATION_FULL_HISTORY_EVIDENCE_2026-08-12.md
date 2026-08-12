# Pre-IU-4 Approved-Throttle Workstation Full-History Evidence — 2026-08-12

## Status

**OFFLINE WORKSTATION SHADOW REPLAY PASSED — 1,042,658/1,042,658 (100.00%)**

The user explicitly approved
`IU4-APPROVED-THROTTLE-WORKSTATION-FULL-HISTORY FREIGEBEN` on 2026-08-11.

The Windows task and Linux launcher finished with exit code `0` at
`2026-08-12T06:01:45Z`. IU4 ENFORCED, Exchange, and Live remained disabled.
The approved throttle profile remained replay-only with
`runtime_activated=false`.

## Immutable execution binding

- branch: `codex/iu4-throttle-calibration-2026-08-11`;
- Git commit: `a64fc756eadddaffd49b0467bd5f62f168143071`;
- execution host: `WORKSTATION`;
- `x1_only=false`; `workstation_only=true`;
- Windows task: `Codex-IU4-Approved-Throttle-Full-History-20260811`;
- launcher SHA-256:
  `565d0bf760b32dbe262e3c0acb59cf68ec09978715fb9578a0a123b38cd39a36`;
- source dataset SHA-256 before and after execution:
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`;
- approved profile ID: `PEE_RATE_OBSERVED_BOUNDARY_001`;
- approved profile SHA-256:
  `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`;
- canonical policy fingerprint:
  `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`;
- calibration report SHA-256:
  `c7ecc33ff559ab8c57b15928bc0ad0f98a466bd15130ac9f30f763918454afe8`;
- calibration decision-replay SHA-256:
  `65f47adaace62a9d9073bc28695d58b09bd7c943f3df94b23f2c67f70ea8114b`.

## IU-3 source result

- valid one-minute records: `1,042,658`;
- source rows scanned: `1,048,200`;
- invalid rows skipped: `5,542`;
- execution events: `1,042,658`;
- transitions: `111 OPEN_LONG`, `111 CLOSE_LONG`;
- sidecar issues: `0`;
- integrated/sidecar observation IDs: exact ordered parity, `397/397`;
- IU-3 return code: `0`.

The normalized market slice contained `1,042,658` records and had SHA-256
`902d10b1d7678777bd23140ff459b9c5eaa9ef7d968bab7ab6e09926bfbfba8a`.

## IU-4 replay result

Replay input and outcome IDs matched exactly in order for all
`1,042,658/1,042,658` records.

- outcomes: `122 COMMITTED`, `1,042,340 NOOP`, `196 REJECTED`;
- committed transitions: `61 OPEN_LONG`, `61 CLOSE_LONG`;
- rejected transitions: `196 OPEN_LONG`, all fail-closed with
  `PEE_RISK_REALIZED_DRAWDOWN_LIMIT`;
- autonomous exits: `111/111` fully accounted;
- autonomous exits committed: `61`;
- autonomous exits represented by state-identical guard-divergence NOOP: `50`;
- guard-divergence records: `50`, bound to `190` rejected entry attempts;
- unbound autonomous-exit suppression: `0`;
- continuation blocked: `false`;
- sandbox consistency: passed;
- final sandbox transaction sequence: `122`;
- final position: `FLAT`.

Every autonomous exit was independently re-read against its replay input. It
either matched a committed close or carried complete same-side, same-state,
same-ID, same-sequence guard-divergence evidence. Parity and fail-closed gates
were not weakened.

## Pipeline validation

All `16/16` chain checks passed:

1. `atomic_source_bytes_unchanged`;
2. `builder_replay_whole_file_hash`;
3. `builder_source_hash`;
4. `evidence_whole_file_hash`;
5. `generation_timestamp`;
6. `input_manifest_to_replay`;
7. `input_manifest_whole_file_hash`;
8. `processed_step_count_matches_mode`;
9. `replay_identity`;
10. `replay_to_evidence`;
11. `restart_fault_expectation`;
12. `sandbox_state_matches_expected_mode`;
13. `source_log_unchanged`;
14. `source_state_fingerprint_stable`;
15. `source_state_unchanged`;
16. `source_to_input_manifest`.

## Fingerprints and whole-file hashes

- run-manifest fingerprint:
  `1fb951e00e30884359ef858adb051218b8a1ff54c1881e575b2426790b4b2c78`;
- run-manifest SHA-256:
  `cdb7c966c86ee6261eb8d877fea7ba213f0284e467a4afa10ebaa0b0edd56bdf`;
- IU-3 manifest SHA-256:
  `c9c799886125a5f86c4e215b394131a5ebc6960f1245aec4893951a9a391c66f`;
- replay input SHA-256:
  `8217787b7358e6eeb9e8addd719afe77af98b66a3a6f2878f2c6007faf853950`;
- replay-input manifest SHA-256:
  `0d9f5bf598c3de75bfea5db06a04a238c2096d8e7b6ac5292241c0985187e2b5`;
- replay-evidence fingerprint:
  `cf591978e29fd857666df41938986f3e1f9fe31f13e4e6c7224493117d01df97`;
- replay-evidence SHA-256:
  `1d3f9f7e0b6378a01402cf7a84e3b688313a0ad99881bf8677e2f8e394a8bb5f`;
- pipeline-receipt fingerprint:
  `ef0f744144fdaa910a236ecc3981155035dba7b1e9af563ab0725c2dee741242`;
- pipeline-receipt SHA-256:
  `5204a341550c67740b6be0b977468f648898fb4450dc54f0c4db9ae4f2f26fb1`;
- phase-2 progress SHA-256:
  `a55c672dd53838765185da5160bc25f7d0668117e9f8dea0aad0883996d13fb4`;
- atomic source-state SHA-256:
  `c7f188c44497b6d4339b24fe8e239d2f3611681d8ac784dc871568e3b1b567b1`;
- IU-3 L1/stdout SHA-256:
  `248b7e979977185e7e66659ca26185c54a729b4fda36851ec0061fc8224b7bd3`;
- IU-3 S2 state log SHA-256:
  `84a5432e933810786cd9da5e1bf8edef18efeb264afad78111d2d58cc746456d`;
- IU-3 S4 state log SHA-256:
  `31e7b26bd61609e227deeed3da88618f188edf7c4aa0108cdd38086135e29337`;
- IU-3 sidecar report SHA-256:
  `6af6d802238f37fffa84f0bdc6d34dc99aff8b6ae156a61fce6a16f5b260a3e9`.

## Verification

```text
Workstation tests/live_l1
281/281 passed

Workstation tests/regression
170/170 passed

Full-history independent artifact validation
1,042,658/1,042,658 outcomes checked
16/16 pipeline chain checks passed
111/111 autonomous exits accounted
397/397 IU-3 observation IDs matched
final position FLAT
```

## Scope boundary

This closes only the explicitly authorized offline approved-throttle
full-history replay gate. It does not authorize IU4 ENFORCED, Exchange, Live,
or runtime activation of the approved profile. Those remain separate, locked
gates.
