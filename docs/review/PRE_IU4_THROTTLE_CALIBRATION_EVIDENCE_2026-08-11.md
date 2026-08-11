# Pre-IU-4 Throttle Calibration Evidence — 2026-08-11

## Status

**CALIBRATION COMPLETE; NAMED POLICY APPROVAL REQUIRED**

This evidence does not authorize or activate IU4 ENFORCED, Exchange, or Live.
All evaluated profiles remain calibration-only and operationally unapproved.

## Scope and integrity

- Workstation full-history minutes: `1,042,658`
- Accepted entries / exits / closed trades: `111 / 111 / 111`
- Calibration code commit: `734e68bb6df146e2265deed3b98a2d09f7c58de0`
- Source CSV SHA-256: `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`
- Execution log SHA-256: `fbdd218c0592bfc12e79993f971f4d23bbe4a1ea458249fd96cad57e5875c0b8`
- Trades log SHA-256: `68e51147487bf2fc95c17526d31006c0e06f593bdeffb7058f30736f9a72553a`
- IU3 manifest SHA-256: `250a8c3b19e7b3f270d93625544db6441b607f27eeed4affe973cfd53b4c8eb9`
- Candidate set SHA-256: `2cc80be773aa22f1c89c4fbf9364e71562946114f4181d84614b145ac3d0a75b`
- Economics profile SHA-256: `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`
- Report SHA-256: `c7ecc33ff559ab8c57b15928bc0ad0f98a466bd15130ac9f30f763918454afe8`
- Report fingerprint: `22da65f4b9752f71cd26807a798f7e674f1236a02aec73a190e5252c8d40092d`
- Permanent report: `/home/workstation/runs/sniper-bot/pee_iu4_shadow_full_history_1042658_20260810/iu4_throttle_calibration/calibration_report.json`

The source logs remained on the workstation. Only the sanitized report was
transferred with explicit authorization and its SHA-256 matched the permanent
workstation artifact.

## Observed accepted-entry distribution

- UTC days with entries: `98`
- Daily histogram: `85` days with one entry; `13` days with two entries
- Maximum entries per UTC day: `2`
- Maximum entries in a rolling six-hour window: `2`
- Inter-entry gap: minimum `12,720 s`, p10 `21,660 s`, median `160,260 s`,
  p90 `963,120 s`, maximum `6,376,620 s`

## Single-threshold sensitivity

| Control | Candidate | Blocked | Percentage |
|---|---:|---:|---:|
| UTC-day limit | 1 | 13 | 11.7117% |
| UTC-day limit | 2, 3, 4, or 8 | 0 | 0% |
| Rolling six-hour limit | 1 | 10 | 9.0090% |
| Rolling six-hour limit | 2, 3, 4, or 8 | 0 | 0% |
| Re-entry cooldown | 180, 3,600, 10,800, or 12,720 s | 0 | 0% |
| Re-entry cooldown | 14,400 s | 4 | 3.6036% |
| Re-entry cooldown | 21,600 s | 10 | 9.0090% |

## Combined candidate results

| Candidate | Day / 6h / cooldown | Blocked | Trade delta | Fee delta | Net-PnL delta | Drawdown-rate delta |
|---|---|---:|---:|---:|---:|---:|
| `PEE_RATE_OBSERVED_BOUNDARY_CANDIDATE_001` | 2 / 2 / 10,800 s | 0 (0%) | 0 | 0 | 0 | 0 |
| `PEE_RATE_BUFFERED_CANDIDATE_001` | 4 / 3 / 3,600 s | 0 (0%) | 0 | 0 | 0 | 0 |
| `PEE_RATE_STRICT_STRESS_CANDIDATE_001` | 1 / 1 / 14,400 s | 16 (14.4144%) | -16 | -31.880682479946709 | +8.270498413247709 | -0.00113272709797643720242647651 |

Unthrottled isolated PEE V1 baseline: `111` settled trades, fees
`219.448065719206861`, net PnL `-241.172859201075861`, final equity
`9758.827140798924139`, and maximum realized drawdown rate
`0.02499450903022321288865717535`.

The economics comparison intentionally excludes Account and S4 guard effects
to isolate the throttle-only delta. This is not a profitability evaluation.

## Deterministic replay identities

- Observed-boundary decision replay SHA-256:
  `65f47adaace62a9d9073bc28695d58b09bd7c943f3df94b23f2c67f70ea8114b`
- Buffered decision replay SHA-256:
  `65f47adaace62a9d9073bc28695d58b09bd7c943f3df94b23f2c67f70ea8114b`
- Strict-stress decision replay SHA-256:
  `470c2f32529ee7810a206f13d00c55bc1dc96a29b2debf51d1bf1614b746576c`

## Interpretation and next gate

Both observed-boundary and buffered candidates preserve all 111 historical
accepted entries. The observed-boundary candidate is the tighter
non-distorting profile and is therefore the evidence-based recommendation for
the separate approval gate:

- maximum `2` accepted entries per UTC day;
- maximum `2` accepted entries per rolling six-hour window;
- minimum re-entry cooldown `10,800 seconds`;
- candidate policy fingerprint:
  `e70b2051a211934a7e276bc1488c516e0ecf1b9444ce5f41f81c276458f3b225`.

This recommendation is not an operational selection. A named immutable policy
profile and its fingerprint require explicit approval before wiring or a fresh
full-history validation. IU4 ENFORCED, Exchange, and Live remain locked.

## Verification

```text
.venv/bin/python -m unittest discover -s tests/live_l1 -p 'test_*.py'
Ran 271 tests — OK

.venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'
Ran 170 tests — OK
```

The targeted calibration suite ran 6 tests successfully. JSON validation,
`py_compile`, and `git diff --check` also passed.
