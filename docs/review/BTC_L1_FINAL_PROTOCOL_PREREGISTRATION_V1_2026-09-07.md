# BTC-L1 Final Protocol Preregistration V1

Date: 2026-09-07

Status: PROPOSED - NOT BINDING UNTIL INDEPENDENTLY APPROVED AND COMMITTED

## 1. Purpose and authority

This protocol fixes the BTC-L1 candidate-selection rule, permitted development evidence, performance and operational gates, prospective holdout rule, stopping rule, and change-control consequences before the one-time Final Candidate Selection.

This document does not select or freeze a candidate, set T0, authorize a market-data run, authorize Paper Trading, establish a live input path, or authorize live capital.

After independent approval and commit, any candidate-selection execution must follow this protocol without discretionary reinterpretation. A material protocol change before selection requires a new version and review. A candidate or protocol change after T0 requires a new candidate identity and a new future T0.

## 2. Bound governance and repository identities

- Repository HEAD at protocol creation: `3c5927127a03de13d8c80a720f5c8b97a2a36789`
- Data Exposure Ledger: `docs/review/BTC_L1_DATA_EXPOSURE_LEDGER_V1_2026-09-02.md`
- Ledger decision: `HISTORICAL_FINAL_OOS_AVAILABLE=NO`
- Only valid Final-OOS path: `PROSPECTIVE_POST_T0_HOLDOUT_ONLY`
- Canonical development dataset logical ID: `BTC_L1_CANONICAL_V1`
- Canonical development dataset path: `data/l1_full_run.csv`
- Canonical development dataset SHA256: `530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f`
- Canonical development period: `2017-08-17 04:00:00+00:00` through `2025-12-31 23:59:00+00:00`
- Canonical rows: `4,374,557`
- Certified historical replay runner: `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py`
- Certified replay runner SHA256: `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292`
- Expected canonical semantic closed-trade count before economics: `563`
- Paper economics profile: `config/pee/PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json`
- Paper economics profile ID: `PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001`
- Paper economics profile fingerprint: `ac4cc746b57c2b802cf765c9c102f9921858c4d3cde2040f452b69ba1e6b14e1`

The historical dataset is development and characterization evidence. It is not Final-OOS evidence and may not support an OOS claim.

## 3. Permitted and prohibited evidence

### 3.1 Permitted for the one-time selection

Only the following may be used:

1. `BTC_L1_CANONICAL_V1` under its bound identity.
2. The certified V4 historical replay and its bound semantic event stream.
3. Tracked pre-T0 BTC-L1 development, characterization, runtime, reconciliation, and governance records already present at the bound repository state.
4. Deterministic nominal and stress economics derived from the bound semantic trade stream under Section 7.

### 3.2 Prohibited for selection, tuning, or ranking

The following are prohibited:

1. Every pre-T0 2026 market-data file, including the raw data downloaded on 2026-07-22.
2. Any bar, trade, metric, or result with market timestamp after `2025-12-31 23:59:00+00:00`.
3. Any post-T0 market data or performance result.
4. Any untracked, external, manually edited, or identity-unbound result not admitted by a reviewed protocol amendment.
5. Any new threshold sweep, seed search, parameter search, candidate ranking, architecture comparison, or discretionary visual selection.
6. Any information from the prospective holdout used to improve, replace, rerank, or retune a candidate.

## 4. Candidate universe and exclusions

The selection is a single-candidate pass/fail decision. It is not a tournament.

The only eligible candidate is the exact legacy BTC-L1 baseline as it exists in repository tree `3c5927127a03de13d8c80a720f5c8b97a2a36789` and as it produces the certified V4 semantic event stream. Candidate selection may not modify candidate code, parameters, seeds, or configuration. Its complete identity will be sealed in the subsequent Candidate Selection and Candidate Freeze records. The identity must bind strategy code, all parameters, timing seeds, short seeds, repository commit, runtime configuration, economics profile, replay runner, input path, output paths, dependency lock, and deterministic fingerprints.

The following research families are ineligible and may not be promoted, ranked, or substituted during this selection:

- STEP19 threshold and shadow-gate variants;
- STEP19 dynamic-exit variants;
- STEP20A position-sizing replay;
- STEP20C historical scaling replay;
- STEP20D retrospective exposure-scaling variants;
- STEP20E true-dynamic exposure replay;
- any variant documented as `NOT VALIDATED`, `NOT LIVE COMPATIBLE`, `NOT LIVE ACCURATE`, `PROOF OF CONCEPT ONLY`, or diagnostic-only.

If the legacy baseline fails any mandatory gate, the result is `NO_FINAL_CANDIDATE`. No runner-up, parameter repair, threshold adjustment, or second selection is allowed under this protocol.

## 5. One-time selection procedure

The selection procedure is fixed:

1. Verify every identity in Section 2.
2. Produce a complete candidate manifest before observing newly computed selection metrics.
3. Verify that the manifest contains no post-2025 market-data input and no prohibited research variant.
4. Reproduce the certified semantic event stream and exactly `563` closed trades with final position `FLAT`.
5. Compute the nominal economics metrics in Section 7.1.
6. Compute the single stress economics scenario in Section 7.2.
7. Evaluate every mandatory gate in Section 8 without changing code, data, parameters, seeds, costs, thresholds, or metric definitions.
8. Emit exactly one decision: `FINAL_CANDIDATE_SELECTED` or `NO_FINAL_CANDIDATE`.
9. Record the run and all revealed metrics in the Data Exposure Ledger as selection exposure.

No partial pass, weighted score, human override, or post-result exception is permitted.

## 6. Metric definitions

All monetary metrics use USDT and realized closed-trade outcomes only. The initial equity is `10000` USDT.

- `net_pnl`: sum of realized trade PnL after adverse slippage and both-side fees.
- `final_equity`: `10000 + net_pnl`.
- `gross_profit`: sum of strictly positive realized net trade PnL.
- `gross_loss`: absolute sum of strictly negative realized net trade PnL.
- `profit_factor`: `gross_profit / gross_loss`; `gross_loss` must be greater than zero for a valid selection result.
- `win_rate`: number of strictly positive net trades divided by closed economic trades; zero-PnL trades are not wins.
- `net_trade_return`: realized net trade PnL divided by realized equity immediately before that trade entry.
- `mean_net_trade_return`: arithmetic mean of the ordered `net_trade_return` sequence.
- `mean_net_trade_return_lcb95`: fifth percentile of `10000` circular moving-block bootstrap means. Let `n` be the number of ordered net trade returns and `L = ceil(n ** (1 / 3))`. For each replicate, NumPy `default_rng(20260907)` draws `ceil(n / L)` start indices independently and uniformly with replacement from `0` through `n - 1`; each start contributes the next `L` observations with circular wrap; concatenation is truncated to `n`; the replicate mean is stored. The lower bound is NumPy percentile `5` with method `linear`.
- `realized_drawdown_rate`: `(realized_high_water_mark - realized_equity) / realized_high_water_mark`.
- `max_realized_drawdown_rate`: maximum `realized_drawdown_rate` over the ordered sequence.
- `cagr`: `(final_equity / 10000) ** (365.2425 / elapsed_calendar_days) - 1`, using the canonical dataset endpoints.
- `calmar_ratio`: `cagr / max_realized_drawdown_rate`; undefined if maximum drawdown is zero and never treated as automatic PASS.

Trade order is the certified semantic order. Fees and slippage are applied exactly once. Missing, non-finite, unordered, duplicated, or unreconciled values fail closed.

## 7. Fixed economics scenarios

### 7.1 Nominal scenario

The nominal scenario uses the accepted SHADOW profile without modification:

- starting equity: `10000` USDT;
- risk per trade: `0.0025`;
- maximum position notional: `0.10` of realized equity;
- entry fee rate: `0.001`;
- exit fee rate: `0.001`;
- entry slippage: `5` bps adverse;
- exit slippage: `8` bps adverse;
- maximum daily realized loss rate: `0.01`;
- maximum daily fee rate: `0.0025`;
- maximum realized drawdown rate: `0.05`;
- no leverage above `1x`;
- at most one open position;
- entry controls may never block an exit.

`PEE_REFERENCE_STOP_RATE=0.015` is excluded. It is a SHADOW fallback, not an authorized trading rule.

### 7.2 Stress scenario

Exactly one stress scenario is allowed:

- entry fee rate: `0.002`;
- exit fee rate: `0.002`;
- entry slippage: `20` bps adverse;
- exit slippage: `20` bps adverse;
- all other candidate, sizing, ordering, and control rules identical to the nominal scenario.

No additional stress grid or best-case scenario may be introduced.

## 8. Mandatory development-selection gates

Every gate is conjunctive.

### 8.1 Identity and integrity gates

1. All Section 2 identities match exactly.
2. Candidate manifest completeness is `PASS`.
3. Semantic parity is exactly `563` closed trades.
4. Final semantic position is `FLAT`.
5. Runtime return code is zero.
6. Audit JSON, position, trade count, trade order, state, and reconciliation checks all pass.
7. No prohibited data or candidate family is accessed.

### 8.2 Nominal economic gates

1. `net_pnl > 0`.
2. `final_equity > 10000`.
3. `gross_loss > 0` and `profit_factor > 1.0`.
4. `mean_net_trade_return_lcb95 > 0`.
5. `max_realized_drawdown_rate <= 0.05`.
6. `cagr > 0`.
7. `calmar_ratio > 0`.
8. No daily-loss, daily-fee, sizing, notional, leverage, minimum-quantity, or minimum-notional control is bypassed.

### 8.3 Stress economic gates

1. `net_pnl > 0`.
2. `final_equity > 10000`.
3. `gross_loss > 0` and `profit_factor > 1.0`.
4. `max_realized_drawdown_rate <= 0.10`.

Passing these development gates selects a candidate for prospective testing only. It does not establish historical OOS performance, prospective edge, live readiness, or capital authorization.

## 9. Candidate Freeze requirements

After `FINAL_CANDIDATE_SELECTED` and before T0, a Candidate Freeze record must bind:

- immutable candidate ID;
- strategy and every parameter;
- timing and short seed files and hashes;
- repository commit and clean-tree status;
- Python and dependency identities;
- replay and prospective runtime entrypoints and hashes;
- PEE profile ID, content hash, and fingerprint;
- input source, symbol, interval, timestamp convention, and bar-close rule;
- output, audit, state, recovery, and reconciliation paths;
- configuration files, environment allowlist, and explicit defaults;
- deterministic expected fingerprints and recertification triggers.

Any missing or implicit value blocks Candidate Freeze.

## 10. T0 and prospective holdout

T0 is not set by this protocol. T0 is the first UTC day after a signed Control Attestation confirms that every mandatory control, firewall, provenance path, recovery path, reconciliation path, and prospective input path is operational and verified.

The prospective holdout is the half-open interval `[T0, infinity)` using bar open timestamps in UTC. A bar belongs to the holdout exactly when its open timestamp is greater than or equal to T0.

The prospective input path must prevent pre-T0 bars, locally retained 2026 files, development files, manual file replacement, and backfilled pre-T0 material from entering the holdout stream.

## 11. Prospective observation and terminal decision rule

Paper Trading may begin at T0 only after all preceding governance gates are closed. Starting Paper Trading is not an edge acceptance.

The terminal prospective evaluation occurs exactly once at the first fully reconciled `FLAT` boundary at or after the later of:

1. `365` complete UTC days after T0; and
2. `100` reconciled closed trades after T0.

Before both conditions are satisfied, performance status is `INSUFFICIENT_EVIDENCE`. Safety, integrity, and reconciliation may be monitored continuously, but interim performance must not be used for tuning, ranking, replacement, or an early edge claim.

At the terminal evaluation, every following gate must pass:

1. realized net PnL after actual modeled paper costs is greater than zero;
2. final realized equity is greater than starting equity;
3. gross loss is greater than zero and Profit Factor is greater than `1.0`;
4. `mean_net_trade_return_lcb95` is greater than zero under the fixed bootstrap rule in Section 6;
5. maximum realized drawdown rate is no greater than `0.05`;
6. CAGR and Calmar Ratio are both greater than zero;
7. all post-T0 trades, events, states, fees, and positions reconcile exactly;
8. there are zero duplicate, missing, orphaned, reordered, or fail-open trading events;
9. there is no unresolved critical incident or mandatory-control breach;
10. the candidate, protocol, runtime, economics, input path, and configuration identities remained unchanged from T0 through evaluation.

All gates passing yields `PROSPECTIVE_EDGE_ACCEPTED`. Any failed scientific or integrity gate yields `PROSPECTIVE_EDGE_REJECTED`. An identity change, contamination, or firewall failure yields `PROSPECTIVE_EVALUATION_INVALID`, not a performance failure.

`PROSPECTIVE_EDGE_ACCEPTED` is a BTC-L1 Paper Trading evidence decision only. It does not authorize live capital. Live capital remains blocked until the separate Live Edge Certification Protocol and every operational capital gate pass.

No repeated testing after a rejection is permitted for the same candidate and holdout.

## 12. Firewall, access, and feedback rules

1. Post-T0 holdout data may flow only into the frozen prospective runtime and append-only evidence path.
2. Development and research tools must have no read path to post-T0 data.
3. Holdout results must not change strategy, parameters, seeds, thresholds, sizing, exits, costs, candidate choice, or monitoring logic.
4. Every human or automated inspection of post-T0 performance must be entered in the Data Exposure Ledger before or at access time.
5. Operational safety monitoring may stop entries or close risk, but may not improve or replace the candidate.
6. A candidate or material configuration change ends the current evaluation and requires a new candidate identity, new Control Attestation, and new future T0.
7. Previously exposed post-T0 data can never become pristine holdout evidence for a replacement candidate.

## 13. Evidence and provenance requirements

Selection, freeze, attestation, T0, Paper Trading, and terminal evaluation records must be append-only and bind:

- UTC creation and access times;
- actor or process;
- repository commit and worktree status;
- input and output paths;
- file sizes and SHA256 hashes;
- candidate and protocol IDs;
- dataset interval and logical identity;
- command and runtime identity;
- metrics revealed;
- gate results and final decision;
- reviewer and approval state;
- off-host or independently controlled evidence receipt.

Silent overwrite, deletion, history rewrite, or replacement invalidates the affected governance claim.

## 14. Required next steps

After this exact protocol is independently approved and committed:

1. execute the one-time Final Candidate Selection on permitted development evidence;
2. append the selection exposure to the Data Exposure Ledger;
3. create and approve the Candidate Freeze;
4. close and certify the real-time prospective input path;
5. create the Final Paper Configuration Freeze;
6. operationalize the firewall and tamper-evident off-host provenance;
7. complete signed Control Attestation;
8. set T0 according to Section 10;
9. start prospective Paper Trading.

No later step may be treated as complete by this preregistration alone.
