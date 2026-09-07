# BTC-L1 Data Exposure Ledger V1

Date: 2026-09-02

Status: ACTIVE GOVERNANCE RECORD

## 1. Purpose

This ledger records when BTC-L1 market data, derived trades, performance results, thresholds, seeds, or replay outputs became available and how that exposure affects scientific claims.

It is a governance record. It does not authorize a market run, candidate change, OOS claim, paper start, or live deployment.

## 2. Bound identities

- Repository HEAD at ledger creation: `e6fd6975580aa617e51d3b22bc1b61fee340eea5`
- Canonical dataset logical ID: `BTC_L1_CANONICAL_V1`
- Canonical dataset path: `data/l1_full_run.csv`
- Canonical dataset SHA256: `530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f`
- Canonical period: `2017-08-17 04:00:00+00:00` through `2025-12-31 23:59:00+00:00`
- Canonical rows: `4,374,557`
- Canonical columns: `22`
- Certified replay runner: `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py`
- Certified replay runner SHA256: `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292`

## 3. Classification rules

- `SELECTION_EXPOSURE`: data or results used to choose a candidate, seed, threshold, parameter, architecture, or ranking.
- `DEVELOPMENT_EXPOSURE`: data or results inspected while the strategy or candidate remained mutable.
- `FALSIFICATION_EXPOSURE`: a prespecified reject-only check that cannot improve or rank a candidate.
- `CHARACTERIZATION_EXPOSURE`: behavior or performance observed without an OOS or selection claim.
- `REPRODUCTION_ONLY`: repetition of an already bound system whose result cannot change the candidate.
- `PROSPECTIVE_HOLDOUT`: post-T0 data protected by an operational firewall.

Exposure is not automatically selection contamination. However, performance-visible data observed while the candidate remained mutable cannot be treated as pristine Final-OOS without affirmative evidence of a prespecified firewall and a non-selection role.

Governance findings and uncontrolled raw-data availability are recorded in this document, but they are not exposure classifications.

Additional governance record types:

- `GOVERNANCE_FINDING`: a control, policy, or evidence-gap finding that does not itself prove data or result inspection.
- `PRE_T0_UNCONTROLLED_RAW_DATA_AVAILABILITY`: raw data existed locally before T0 without an operational prospective firewall; this status does not assert that performance was computed or inspected.

## 4. Audit and exposure ledger

### E001 - General OOS policies existed without a BTC-L1 split binding

- First tracked: `2026-03-17`
- Evidence: `docs/POLICIES/backtest_integrity_policy.md`, `docs/POLICIES/ml_validation_policy.md`, `docs/POLICIES/gs_acceptance_checklist.md`
- Record type: `GOVERNANCE_FINDING`
- Finding: general policy required IS/OOS separation, but the audit found no BTC-L1-specific period boundary, sealed artifact, access firewall, or preregistered Final-OOS assignment.
- Consequence: policy text alone does not establish an implemented BTC-L1 holdout.

### E002 - Full-history and multiple subwindow results were visible

- First tracked: `2026-06-05`
- Evidence: `docs/research/STEP20_FINAL_SUMMARY.md`, `docs/research/STATE_RESEARCH_FINAL_STATUS.md`
- Data windows: `200k @ 0`, `200k @ 500000`, `200k @ 1000000`, `500k @ 1500000`, `1M @ 2500000`, and `4.3M @ 0`
- Classification: `DEVELOPMENT_EXPOSURE`; selection-relevant performance exposure
- Finding: PnL, Profit Factor, drawdown, and risk-adjusted behavior were visible across multiple windows. The 4.3M run ended at `2025-11-10 05:22:00+00:00`, leaving `74,557` canonical ticks outside P66; the later complete 4,374,557-tick replay exposed that remaining tail.
- Consequence: the covered periods are not pristine Final-OOS.

### E003 - Timing seed construction and selection logic changed after performance exposure

- Date: `2026-06-06`
- Evidence: `docs/review/P32_5M_TIMING_SEED_V2_CREATION_2026-06-06.md`, `docs/review/P42_TIMING_SEED_SELECTION_LOGIC_AUDIT_2026-06-06.md`
- Classification: `SELECTION_EXPOSURE` and `DEVELOPMENT_EXPOSURE`
- Finding: timing seed v2 and short-seed selection behavior were created or audited after full-history and subwindow results had been observed.
- Consequence: subsequent results cannot create an independent retrospective OOS claim.

### E004 - Progressive runtime and segment performance was inspected

- Period: `2026-06-06` through `2026-06-09`
- Evidence: `docs/review/P51_SEGMENT_BASED_TRADING_BEHAVIOR_AUDIT_2026-06-06.md`, `docs/review/P59_EXTENDED_SEGMENT_VALIDATION_2026-06-06.md`, `docs/review/P60_EXTENDED_RUNTIME_TRADE_QUALITY_REVIEW_2026-06-06.md`, `docs/review/P61_EXTENDED_SEGMENT_ACCEPTANCE_REVIEW_2026-06-06.md`, `docs/review/P62_MEDIUM_RUNTIME_VALIDATION_25000_2026-06-06.md`, `docs/review/P63_LARGE_RUNTIME_VALIDATION_100000_2026-06-08.md`, `docs/review/P64_LARGE_RUNTIME_VALIDATION_500000_2026-06-08.md`, `docs/review/P65_LARGE_RUNTIME_VALIDATION_1000000_2026-06-08.md`, and `docs/review/P66_FULL_RUNTIME_VALIDATION_4300000_2026-06-09.md`
- Data sizes: segment checks, `25,000`, `100,000`, `500,000`, `1,000,000`, and `4,300,000` ticks
- Classification: `CHARACTERIZATION_EXPOSURE` and `DEVELOPMENT_EXPOSURE`
- Finding: progressively larger portions of the same historical series were inspected while the runtime and scientific candidate remained mutable.
- Consequence: P66 is historical development/characterization evidence, not Final-OOS.

### E005 - Full-history archive was locally retained

- Date: `2026-06-22`
- Evidence host: `workstation`
- Evidence source repository: `/mnt/c/Users/workstation/Desktop/sniper-bot`
- Source repository observed HEAD: `a5cdc25893cb2d6778e6223dfe46f740b429d747`
- External artifact: `/mnt/c/Users/workstation/Desktop/sniper-bot/transfer/paper_run_4300000_trade_inspector_2026-06-22.zip`
- Artifact bytes: `341,109,258`
- Artifact SHA256: `f6de9034e34e8076ddcd8987b43ba7745624d1528d3b7d72812425fcfb03f2cd`
- Source working-tree status: parent `transfer/` was untracked at audit time
- Classification: `CHARACTERIZATION_EXPOSURE`
- Finding: a 4.3M paper/trade-inspector archive remained locally available.
- Consequence: this corroborates full-history result availability; it does not establish selection use by itself.

### E006 - Pre-T0 2026 raw data was downloaded without a holdout firewall

- Download date: `2026-07-22`
- Evidence host: `workstation`
- Evidence source repository: `/mnt/c/Users/workstation/Desktop/sniper-bot`
- Source repository observed HEAD: `a5cdc25893cb2d6778e6223dfe46f740b429d747`
- External log: `/mnt/c/Users/workstation/Desktop/sniper-bot/logs/btcusdt_1m_bulk_download_2026-07-22.log`
- Log bytes: `8,282`
- Log SHA256: `6d950a6796ba94cb83d99299abf56c2fad1e98d5383c17b981f49aec75e99abe`
- Raw root: `/mnt/c/Users/workstation/Desktop/sniper-bot/data/btcusdt_1m_2026-07-22/raw`
- Raw inventory: `127` files and `230,077,908` bytes
- External log/raw tracking state: not asserted by this ledger; neither path was listed by the captured short status
- Available raw period: monthly data through `2026-06` and daily data through `2026-07-20`
- Download result: `ok=127`, `bad=0`, `missing=1`; `2026-07-21` returned HTTP 404 at download time
- Record type: `PRE_T0_UNCONTROLLED_RAW_DATA_AVAILABILITY`; selection use not evidenced; performance run not evidenced
- Finding: raw data was locally accessible before preregistration, candidate freeze, control attestation, and T0. The audit found no evidence that BTC-L1 performance was computed on these 2026 raw files.
- Consequence: the 2026 raw files are not `PROSPECTIVE_HOLDOUT`, may not be used for tuning, ranking, or candidate selection, and cannot retroactively become post-T0 data.

### E007 - Full-history IU4 and throttle replays were observed

- Period: `2026-08-11` through `2026-08-13`
- Evidence: `docs/review/PRE_IU4_WORKSTATION_FULL_HISTORY_REPLAY_EVIDENCE_2026-08-11.md`, `docs/review/PRE_IU4_APPROVED_THROTTLE_WORKSTATION_FULL_HISTORY_EVIDENCE_2026-08-12.md`, and `docs/review/PRE_IU4_WORKSTATION_FULL_HISTORY_SHADOW_GATE_EVIDENCE_2026-08-13.md`
- Classification: `CHARACTERIZATION_EXPOSURE` and `DEVELOPMENT_EXPOSURE`
- Finding: full-history evidence remained visible during continuing execution and control research.
- Consequence: no historical freshness was restored by later infrastructure work.

### E008 - Threshold, exit, and position-sizing surfaces were exposed

- Period: `2026-08-15` through `2026-08-16`
- Evidence: `docs/review/X1_STATE_RESEARCH_S21_STEP19_THRESHOLD_SWEEP_CHARACTERIZATION_2026-08-15.md`, `docs/review/X1_STATE_RESEARCH_S25_STEP19_SHADOW_GATE_REPLAY_CHARACTERIZATION_2026-08-15.md`, `docs/review/X1_STATE_RESEARCH_S25A_STEP19_SHADOW_GATE_REPLAY_THRESHOLD_AUTHORITY_DECISION_2026-08-15.md`, `docs/review/X1_STATE_RESEARCH_S25B_STEP19_SHADOW_GATE_REPLAY_REPAIR_SPECIFICATION_2026-08-15.md`, `docs/review/X1_STATE_RESEARCH_S25C_STEP19_SHADOW_GATE_REPLAY_THRESHOLD_BINDING_REPAIR_2026-08-16.md`, `docs/review/X1_STATE_RESEARCH_S27_STEP19_DYNAMIC_EXIT_REPLAY_CHARACTERIZATION_2026-08-16.md`, `docs/review/X1_STATE_RESEARCH_S29_STEP20C_LIVE_REPLAY_CHARACTERIZATION_2026-08-16.md`, `docs/review/X1_STATE_RESEARCH_S31_STEP20_POSITION_SIZING_REPLAY_CHARACTERIZATION_2026-08-16.md`, `docs/review/X1_STATE_RESEARCH_S33_STEP20D_SENSITIVITY_CHARACTERIZATION_2026-08-16.md`, `docs/review/X1_STATE_RESEARCH_S35_STEP19B_THRESHOLD_SWEEP_CHARACTERIZATION_2026-08-16.md`, `docs/review/X1_STATE_RESEARCH_S37_STEP19B_REAL_EXIT_REPLAY_CHARACTERIZATION_2026-08-16.md`, `docs/review/X1_STATE_RESEARCH_S39_STEP20D_DYNAMIC_EXPOSURE_SCALING_CHARACTERIZATION_2026-08-16.md`, and `docs/review/X1_STATE_RESEARCH_S41_STEP20E_TRUE_DYNAMIC_EXPOSURE_REPLAY_CHARACTERIZATION_2026-08-16.md`
- Classification: `DEVELOPMENT_EXPOSURE` and `CHARACTERIZATION_EXPOSURE`; selection-relevant results visible, selection use not proven
- Finding: threshold grids, exit configurations, position-sizing variants, PnL, Profit Factor, win rate, and drawdown outputs were available. S25A-S25C established an explicit diagnostic threshold parameter contract, not a selected or validated trading threshold.
- Consequence: historical performance remained decision-relevant while parameters and implementations were mutable.

### E009 - Canonical identity, boundary resolution, and V4 parity were established

- Period: `2026-08-31` through `2026-09-02`
- Evidence: canonical dataset governance, P66 boundary resolution, and high-speed replay V4 certification
- Classification: `DEVELOPMENT_EXPOSURE` and `CHARACTERIZATION_EXPOSURE`; declared purpose `REPRODUCTION_PARITY`; selection use not evidenced
- Finding: the 563-trade full-history sequence was reproduced deterministically and V4 matched the golden semantic event stream.
- Consequence: reproducibility is established, but final candidate selection and freeze were still open; therefore `REPRODUCTION_ONLY` is not claimed.

## 5. Final historical OOS decision

`HISTORICAL_FINAL_OOS_AVAILABLE=NO`

No scientifically defensible retrospective BTC-L1 Final-OOS period remains in `BTC_L1_CANONICAL_V1`.

Reasons:

1. Full-history and overlapping subwindow performance was visible while the candidate remained mutable.
2. Seeds, thresholds, exits, sizing, and execution-related variants continued to be evaluated afterward.
3. No affirmative evidence binds a specific historical interval to a prespecified BTC-L1 firewall and reject-only or non-selection role.
4. The 2026 raw files were downloaded pre-T0 and were not protected by an operational prospective firewall.

The only valid Final-OOS path is:

`PROSPECTIVE_POST_T0_HOLDOUT`

T0 has not been set. T0 may only be the first UTC day after a successful Control Attestation confirms that every mandatory control is operational and verified.

## 6. Binding governance rules from this point forward

1. `BTC_L1_CANONICAL_V1` remains development/characterization evidence and must not be described as Final-OOS.
2. Pre-T0 2026 raw data must not be used for tuning, ranking, candidate selection, or a retrospective OOS claim.
3. Candidate selection must use only explicitly permitted development evidence under a preregistered rule.
4. Candidate identity, parameters, seeds, commit, runtime configuration, and input path must be frozen before T0.
5. Post-T0 data must never flow back into development, tuning, ranking, or candidate replacement.
6. Any inspection of post-T0 performance must be recorded in this ledger before or at the time of access.
7. A candidate or configuration change after T0 invalidates the current prospective evaluation and requires a new candidate identity and a new future T0.
8. Historical replay V4 may be used only under its certified bindings unless a recertification trigger occurs.

## 7. Ledger maintenance contract

Every new exposure entry must record:

- unique entry ID;
- UTC timestamp;
- actor or process;
- data interval and logical dataset identity;
- artifact paths and hashes when available;
- candidate identity and freeze state;
- purpose declared before access;
- metrics or outputs revealed;
- primary and secondary classifications;
- whether selection use occurred;
- whether the exposure changes any OOS claim;
- reviewer and approval state.

This file is append-only after certification. Corrections must be added as new entries that reference the superseded entry; historical entries must not be silently rewritten.
