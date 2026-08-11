# Pre-IU-4 Workstation Full-History Replay Evidence — 2026-08-11

## Status

**FULL-HISTORY IU-4 SHADOW REPLAY PASSED — 1,042,658/1,042,658 (100.00%)**

Branch: `codex/pre-iu4-workstation-full-history-2026-08-10`

Runner commit: `2635918695169b765375e7ffbde273bafa994ed8`

IU-3 source commit: `74cc2fc9701d6ce0038a2e9d8759e78f8251c629`

Execution host: `WORKSTATION`; `x1_only=false`; `workstation_only=true`.

Windows task `Codex-IU4-Full-History-20260810` and the Linux launcher both
finished with exit code `0`. IU-4 ENFORCED, Exchange, and Live remained locked.
The throttle profile remained calibration-only and operationally unapproved.

## Dataset and IU-3 source chain

- source SHA-256 before and after the replay:
  `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`;
- valid one-minute records: `1,042,658`;
- interval: `2017-08-17T04:00:00Z` through `2019-08-15T01:59:00Z`;
- invalid source rows skipped: `5,542`;
- IU-3 return code: `0`;
- IU-3 transitions: `111 OPEN_LONG`, `111 CLOSE_LONG`;
- sidecar issues: `0`;
- integrated/sidecar observation IDs: exact ordered parity, `397/397`.

The IU-3 source state fingerprint remained
`5924c0563a1f4ff8204a05ec7cc50eff11efbba47b8685513bd5464db91b94b4`
at transaction sequence `0` before and after replay.

## IU-4 result

Replay input and outcome IDs matched exactly in order for all
`1,042,658/1,042,658` records.

- outcomes: `122 COMMITTED`, `1,042,340 NOOP`, `196 REJECTED`;
- committed transitions: `61 OPEN_LONG`, `61 CLOSE_LONG`;
- autonomous exits: `111/111` fully accounted;
- autonomous exits committed: `61`;
- autonomous exits represented by state-identical guard-divergence NOOP: `50`;
- guard-divergence records: `50`, bound to `190` rejected entry attempts;
- unbound autonomous-exit suppression: `0`;
- pipeline chain checks: `16/16` passed;
- source bytes/state unchanged: passed;
- sandbox consistency: passed;
- final sandbox transaction sequence: `122`;
- final position: `FLAT`.

Every autonomous exit was independently re-read against its replay input. It
either matched a committed close or carried complete same-side, same-state,
same-ID, same-sequence guard-divergence evidence bound to the preceding
fail-closed entry rejection. Parity and fail-closed gates were not weakened.

## Fingerprints and whole-file hashes

- launcher SHA-256:
  `a20486c7ad30a130082168cd5ba455cb9d8eb573261f7e6f719890146a2d2f52`;
- run manifest fingerprint:
  `3186dae8427a032a8ca8576781f92120e118706019176f1b6c698121a3c77be6`;
- run manifest SHA-256:
  `966706644d3d9d6b3ee96129b42a5b77771190ec40fb521f82018f4d2a81397a`;
- IU-3 manifest SHA-256:
  `250a8c3b19e7b3f270d93625544db6441b607f27eeed4affe973cfd53b4c8eb9`;
- replay input SHA-256:
  `ea65eeeee476fe4c3e4b0302f0811fc3182c9ded562a4b5328727cae07f20a8a`;
- replay input manifest fingerprint:
  `831d4a7f32b23e6d02ce4ab38018a261161f0694a3b5e87bd55655ee20065f44`;
- replay input manifest SHA-256:
  `01b0a30dc76e2c8acb88db11e7ce5ec3a3194cf8aaee90ad4618a6ceda9b7bfc`;
- replay evidence fingerprint:
  `4b8830a2dd391ce69979eef834470962ffc34edbe91adddbd3832fd2822ff65f`;
- replay evidence SHA-256:
  `5d869537ceaf4c9e4c0ea42544ebc3b19b81a5758adf47e7aaaf75db14a95587`;
- pipeline receipt fingerprint:
  `7442b30a26270c45d114f33829e52241cbe54098202f986bae39e9257c326304`;
- pipeline receipt SHA-256:
  `e80255eb56201137254416e7e4e92ad2c6bc949644eb620f93b047df30d688dd`.

The complete machine-readable validation record, including all hashes and the
targeted cleanup ledger, is stored in
`docs/review/evidence/PRE_IU4_WORKSTATION_FULL_HISTORY_REPLAY_VALIDATION_2026-08-11.json`.

After the hashes and fingerprints were committed, the seven ledgered,
reproducible large artifacts were removed from the Workstation run directory:
`6,697,839,245` bytes total. The immutable source CSV, its hash, the small
manifests, receipts, progress record, sidecar report, and atomic source state
were preserved. The source CSV was rehashed after cleanup and remained exact.

## Verification

```text
Workstation tests/live_l1
265/265 passed

Workstation tests/regression
170/170 passed

Full-history independent artifact validation
1,042,658/1,042,658 outcomes checked
16/16 pipeline chain checks passed
111/111 autonomous exits accounted
397/397 IU-3 observation IDs matched
final position FLAT
```

The independent validation rehashed the source after completion, rehashed all
large artifacts, recomputed all canonical manifest/receipt/evidence
fingerprints, and checked each replay/outcome ID and each autonomous-exit
binding. The validation script used on the Workstation had SHA-256
`5b75751c043e00ee918c1fe48b5785b3a176539bdcab1541aceb9e33b639e1f8`.

## Scope boundary

This closes the explicitly authorized Workstation full-history replay gate. It
does not authorize IU-4 ENFORCED, Exchange, Live, or operational approval of
the calibration-only throttle policy. Those remain separate, locked gates.
