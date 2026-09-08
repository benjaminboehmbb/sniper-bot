# BTC-L1 G10-B Evaluator Clarification V1

Date (UTC): 2026-09-08

**Status: APPROVED_FOR_ADOPTION**

Candidate source commit: `3c5927127a03de13d8c80a720f5c8b97a2a36789`

Repository HEAD at preparation: `6728a08d494a3e8dc16e2f400e6fd6b07189dfa9`

Machine-readable companion: `docs/review/evidence/BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08.json`

## Formal adoption record

```json
{
  "authority": "EXPLICIT_USER_AUTHORIZATION_IN_CURRENT_CONVERSATION",
  "commit_authorized": false,
  "date_utc": "2026-09-08",
  "decision": "FORMALLY_ACCEPT_REVIEWED_CLARIFICATION",
  "execution_authorized": false,
  "historical_wording": "Unchanged Proposed headings and conditional approval wording describe the reviewed proposal. This record supplies its formal user acceptance only; implementation and execution prerequisites remain open.",
  "push_authorized": false,
  "remaining_scope": "No implementation, candidate manifest, market run, commit, push, T0, Paper Trading or live capital is authorized.",
  "repository_publication_state": "NOT_COMMITTED_NOT_PUSHED_AT_ADOPTION_RECORDING",
  "review_errata": [
    "The document defines z=k*ln(r), followed by CAGR=exp(z)-1; do not multiply by ln(r) again.",
    "The specified accumulation is deterministic rounded Decimal arithmetic, not generally rounding-free arithmetic.",
    "Decimal supports fractional powers; the fixed ln/exp sequence is a chosen method, not the only valid method."
  ],
  "review_recommendation": "APPROVE_FOR_FORMAL_ADOPTION",
  "review_source": "ANTIGRAVITY_WORKSTATION_REVIEW_REPORTED_BY_USER",
  "reviewed_json_sha256": "0a339afca2231e9b9fa4a43610b5612f2a1890b38a4ef16fc71ee42903348ea8",
  "reviewed_markdown_sha256": "cbee3a3ca53e991e0e929c299190fc667b19a6ec55eff671baf9ff287e27638d",
  "scope": "Accept the reviewed specification and record approval in these two files; calculation rules unchanged.",
  "unchanged_rule_content_sha256": "8725f6ba30b039a20979503f77e16a0e8031916b2b548b0d574f1d136c5599de"
}
```

## Source bindings

- `docs/review/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.md` at `6728a08d494a3e8dc16e2f400e6fd6b07189dfa9`; SHA256 `628abdb89135f747dd24df624a416aeffa591d1486b8f8cce86779a627d5167e`.
- `docs/review/evidence/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.json` at `6728a08d494a3e8dc16e2f400e6fd6b07189dfa9`; SHA256 `21c5730a0f1a6134a826fd2ba34e8ff8c5ad8d7ff739ac6d8b45f6d7df57786a`.
- `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py` at `3c5927127a03de13d8c80a720f5c8b97a2a36789`; SHA256 `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292`.
- `live_l1/core/loop.py` at `3c5927127a03de13d8c80a720f5c8b97a2a36789`; SHA256 `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058`.
- `live_l1/core/execution.py` at `3c5927127a03de13d8c80a720f5c8b97a2a36789`; SHA256 `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3`.
- `live_l1/core/paper_economics.py` at `3c5927127a03de13d8c80a720f5c8b97a2a36789`; SHA256 `a302013134d1265ac85ad10b57a67ead9e2343043f7eb499fd965a44312525ae`.
- `live_l1/state/paper_artifacts.py` at `3c5927127a03de13d8c80a720f5c8b97a2a36789`; SHA256 `3cd9a459e2856672bb7b318c9cdbf8f8bb52e633ee9529d74761d64928213946`.
- `config/pee/PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json` at `3c5927127a03de13d8c80a720f5c8b97a2a36789`; SHA256 `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`.

## Fixed reference and scenario parameters

```json
{
  "nominal": {
    "entry_fee_rate": "0.001",
    "entry_slippage_bps": "5",
    "exit_fee_rate": "0.001",
    "exit_slippage_bps": "8",
    "leverage_max": "1",
    "max_daily_fee_rate": "0.0025",
    "max_daily_loss_rate": "0.01",
    "max_open_positions": 1,
    "max_position_notional_rate": "0.10",
    "max_realized_drawdown_rate": "0.05",
    "min_notional_quote": "10",
    "min_quantity": "0.00001",
    "quantity_step": "0.000001",
    "quote_currency": "USDT",
    "risk_per_trade_rate": "0.0025",
    "starting_equity_quote": "10000"
  },
  "numeric": {
    "Emax": 999999,
    "Emin": -999999,
    "bootstrap_dtype": "float64",
    "bootstrap_percentile": 5,
    "bootstrap_percentile_method": "linear",
    "bootstrap_replicates": 10000,
    "bootstrap_seed": 20260907,
    "clamp": 0,
    "decimal_precision": 50,
    "finite_float64_subnormals": "ALLOWED",
    "nonzero_decimal_return_converted_to_float64_zero": "ERROR",
    "rounding": "ROUND_HALF_EVEN",
    "seconds_per_day": "86400",
    "year_days": "365.2425"
  },
  "reference": {
    "closed_semantic_trades": 563,
    "dataset_id": "BTC_L1_CANONICAL_V1",
    "dataset_path": "data/l1_full_run.csv",
    "dataset_sha256": "530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f",
    "end_utc": "2025-12-31 23:59:00+00:00",
    "final_position": "FLAT",
    "historical_normalized_trade_sha256": "46706ec9f6446eb5ceecf7782199a8a7fab8a7f91c318ce560f5daa83b98646c",
    "historical_trade_normalization_method": "NOT_RECOVERED",
    "semantic_event_sha256": "ffa200c601dc6c2bdda0492909d6518573af6de0b621deb91ee3c9f46d7022e3",
    "semantic_events": 30621902,
    "start_utc": "2017-08-17 04:00:00+00:00",
    "ticks": 4374557
  },
  "stress_overrides_only": {
    "entry_fee_rate": "0.002",
    "entry_slippage_bps": "20",
    "exit_fee_rate": "0.002",
    "exit_slippage_bps": "20"
  }
}
```

## Status and authority

Status: APPROVED_FOR_ADOPTION. The user has formally accepted the reviewed G10-B evaluator clarification and authorized recording that acceptance in these two documents. Calculation rules, parameters and source bindings remain unchanged. This is not implementation, candidate-manifest, selection, market-run, commit, push, T0, Paper Trading or live-capital authorization.

G10-B together with this expressly accepted clarification defines the approved specification. The reviewed draft hashes, review recommendation and user acceptance are recorded above. These files have not been committed or pushed by this recording step. Remaining implementation, runtime, manifest and execution prerequisites are not waived.

The Antigravity Workstation review reported matching hashes and recommended APPROVE_FOR_FORMAL_ADOPTION for the exact draft bytes. This is a document/source review, not an implementation or runtime certification. The review's incorrect CAGR paraphrase and overstatements about rounding and fractional powers are corrected in the adoption record; the actual reviewed calculation rules are unchanged.

## Semantic input and trade reconstruction

Use the unchanged bound V4 runner and validate the entire semantic stream against its recorded event count and SHA256 before releasing selection metrics. Hash the original ordered UTF-8 bytes with LF endings, including all event categories; never hash a filtered or reserialized subset as a substitute.

The format is space-separated key=value tokens. Split each token at its first equals sign, preserve empty values, reject duplicate keys, and validate required fields. Logger escaping replaces spaces with underscores and LF/CR/TAB with literal backslash sequences; it is not generally invertible. Do not globally reverse underscores or use a generic escape decoder.

For each successfully processed tick require exactly one market_snapshot followed by exactly one execution, possibly with other events between them. Pair by tick in original order; do not sort to repair input. Require the canonical complete tick sequence and reject missing, duplicate, orphaned or unfinished pairs. NOOP and veto decisions are execution events too.

The bound loop reads one snapshot, makes one guarded execution call and logs one execution decision per completed tick. A close returns from that call; close plus re-entry in the same tick is unsupported and must be rejected.

Store the OPEN tick, snapshot ID, UTC time, side and exact reference_price_text. The Economics entry reference is Decimal of that OPEN snapshot text. The exit reference is Decimal of reference_price_text from the matched CLOSE snapshot. Both must be positive and finite; there is no fallback to float price. CLOSE execution fields already clear the entry price and time, so retained OPEN data is required.

Legacy float price and execution entry_price are consistency evidence, not replacement Economics price inputs. Reconstruct their finite float values and check equality without tolerances. Enforce position_before/position_after continuity: OPEN_LONG FLAT->LONG, OPEN_SHORT FLAT->SHORT, CLOSE_LONG LONG->FLAT, CLOSE_SHORT SHORT->FLAT, all executed=1. A nonexecuted decision must not change position. No partial positions, unpaired exits or silent flips.

Timestamp decoding must use a field-specific explicit UTC grammar, retain original tokens and reject ambiguous encodings. The exact parser grammar, schema and adversarial fixtures remain implementation-qualification requirements, not certified by this draft.

Require 563 complete semantic trades and final FLAT. Independently reconcile the trade ledger, audit, order and final S2/S4/loss-cluster states. The event hash does not replace these checks. The missing historical normalized-trade hash algorithm remains a provenance gap; do not claim that hash has been recomputed or invent its old serialization.

## Prices, sizing and costs

Model adverse slippage once per leg: LONG entry up and exit down; SHORT entry down and exit up. The multiplier is 1 +/- (bps / 10000), applied to that leg's exact reference price. Entry and exit fees are each charged once on absolute quantity times the corresponding modeled fill price.

Execution gross PnL is quantity times (exit_fill - entry_fill) for LONG and quantity times (entry_fill - exit_fill) for SHORT. Net PnL subtracts the sum of entry and exit fees. Slippage is already in fill prices and must not be subtracted again. Optional slippage-cost reporting is diagnostic, not another debit.

Keep the bound risk-budget/notional-cap sizing algorithm and its operation order under the proposed numeric context. Risk per unit includes modeled entry-to-stop loss and both modeled fees; risk quantity and notional-cap quantity determine the smaller raw quantity, which is floored to quantity_step. Validate risk, notional, minimum quantity, minimum notional, leverage and one-position controls without epsilon or silent quantity repair.

The bound Legacy call omits fee_roundtrip and receives its default 0.0 despite configuration containing 0.0004. Preserve that source behavior; never import Legacy pnl/pnl_net as G10 economics or apply a corrective 0.0004 deduction.

Exactly two independent Economics scenarios are allowed: nominal and the single stress scenario with only the four recorded cost overrides. Each starts at 10000 and maintains its own account, sizing and veto decisions. Do not force their economic trade counts to match. The stress result gate of DD<=0.10 does not relax the operative DD control of 0.05.

## Proposed strategy-derived sizing stop

This proposal uses the explicitly bound strategy L1_SL_PCT="0.015", not the excluded PEE_REFERENCE_STOP_RATE fallback.

Reconstruct legacy_entry=float(entry_reference_text) and verify it against the recorded Legacy entry. Set legacy_sl=float("0.015"). Compute legacy_stop=legacy_entry*(1.0-legacy_sl) for LONG or legacy_entry*(1.0+legacy_sl) for SHORT, preserving these separate Legacy float operations. Convert the finite result exactly with Decimal.from_float(legacy_stop). Do not substitute Decimal(str(legacy_stop)) or a newly calculated pure-Decimal strategy threshold.

Decimal.from_float preserves the actual float value; subsequent arithmetic still uses the declared rounded Decimal context. Require a positive stop, below the exact Economics entry reference for LONG and above it for SHORT. Retain the reconstructed float identity and Decimal stop in future audit evidence.

Use this stop only for Economics sizing and modeled risk. Do not create a new exit, change the Legacy stop, alter exit ticks or recompute strategy decisions. Freeze and qualify Python float behavior before use. This is a proposed mapping, not a claim that it is the only safe mapping.

## Proposed UTC settlement-day accounting

Book the entire closed trade's realized net PnL and both fees on its UTC close day. Entry-time fees can be recorded as modeled costs, but this proposal does not debit them early from realized equity or the daily fee accumulator. A trade spanning midnight assigns both fees to the close day.

This explicitly defines a settlement-day fee metric, not the actual cash-fee burden of each execution day. Compatibility with G10-B requires explicit approval; existing helper behavior alone is not authority to settle that policy question.

Daily net PnL and daily fees accumulate in economic settlement order and reset for a new UTC accounting day. Before an entry on a later day, prior-day counters contribute zero. Day-start equity is current realized equity minus the current day's booked net PnL. Daily loss is max(0, -daily_net_pnl); daily loss and fee rates divide by positive day-start equity.

Block new entries at daily_loss_rate>=0.01, daily_fee_rate>=0.0025 or realized_drawdown_rate>=0.05, with Decimal comparisons, for both scenarios. Reject invalid/nonpositive account bases and time regression. These checks use booked amounts, not a newly invented reservation of future exit fees. An exit always remains permitted even when it causes a limit to be exceeded; the resulting control and performance consequences remain observable. Do not force an earlier exit to satisfy a gate.

## Proposed semantic and economic ledger reconciliation

Assign each semantic trade a stable ordered identity independent of run-specific IDs. Per scenario record either ENTRY_ACCEPTED or ENTRY_VETOED with its semantic identity, tick, UTC time, reason and applicable account/control state.

An accepted entry opens one economic position. Its matched semantic exit closes that position and settles its costs and net PnL. A veto opens no economic position, charges no hypothetical fees and contributes no hypothetical or zero-PnL trade. Its later semantic exit explicitly completes the recorded veto pair; it is never silently ignored.

At completion, per scenario: 563 = economically closed trades + complete veto trade pairs. All semantic trades have exactly one classification and no mappings or positions remain open.

Winrate, PF, trade returns and bootstrap use only economically closed trades. CAGR still uses the full canonical dataset interval; vetoes never shorten that interval. All-veto or otherwise undefined metric cases cannot pass.

No alternative entry, research variant or second candidate is introduced. Economic vetoes never feed back into the fixed Legacy stream, signals, cooldown or Legacy loss-cluster state. This historical overlay does not certify equivalence of a future prospective execution/input path.

## Proposed Decimal arithmetic and authoritative equity

Use an explicit local Decimal context with precision 50, ROUND_HALF_EVEN, Emin=-999999, Emax=999999 and clamp=0. This is rounded decimal floating-point arithmetic, not generally exact or fixed-point arithmetic. Construct constants and Economics prices from strings; the declared Decimal.from_float stop mapping is the deliberate exception.

Do not inherit arithmetic settings from the caller. Invalid operations, division by zero, overflow and nonfinite values are errors. Set the context traps/flags explicitly during implementation and document their complete values. Ordinary context rounding and inexact division are allowed. No extra cent or price-tick quantization; only the prescribed quantity-step floor. No epsilon, isclose, clamp-to-PASS or rounding repair.

Let C0=0 and E0=H0=10000. In economic close order compute Ci=context.add(Cprev, net_pnl_i), Ei=context.add(E0, Ci), Hi=max(Hprev, Ei), Di=context.divide(context.subtract(Hi, Ei), Hi). Include initial drawdown zero. All account decisions, sizing bases, reports and gates use this same canonical equity series. Max drawdown is the maximum over these ordered realized close states, not daily-end or unrealized observations.

The existing settle_trade helper computes previous_equity+net_pnl, while apply_trade_to_account uses initial_equity+cumulative_pnl. These need not agree at finite precision. The future evaluator must use the canonical accumulation above everywhere, and qualify any reused helper against it. Do not modify the bound candidate code or quietly tolerate divergent account values. Resolving the helper integration is still an implementation obligation, not a passed test.

Accumulate gross_profit and signed negative net PnL separately in economic trade order; gross_loss is the absolute negative sum. PF divides gross_profit by strictly positive gross_loss. Net trade return divides trade net PnL by the positive canonical realized equity recorded immediately before its accepted entry. Winrate counts strictly positive net trades; zero-PnL trades are not wins.

## CAGR, Calmar and existing selection gates

Keep G10-B's formula: CAGR=(final_equity/10000)**(365.2425/elapsed_calendar_days)-1. The endpoints are the full canonical dataset timestamps in the fixed parameters. Derive exact integer elapsed seconds from UTC timedelta days and seconds, not a float total_seconds intermediate.

In the specified context and order: days=divide(Decimal(elapsed_seconds), Decimal("86400")); k=divide(Decimal("365.2425"), days); r=divide(final_equity, Decimal("10000")); z=multiply(k, ln(r)); CAGR=subtract(exp(z), Decimal("1")); Calmar=divide(CAGR, max_drawdown) only when max_drawdown>0. Require positive elapsed time and final equity. Decimal supports fractional powers; ln/exp is a chosen explicit operation sequence, not a workaround for missing support or a custom Taylor implementation.

At max_drawdown exactly zero, Calmar is undefined and cannot pass. A tiny positive finite denominator is not converted to zero by a tolerance. All nonfinite results are invalid.

Keep existing nominal gates: net_pnl>0; final_equity>10000; gross_loss>0; PF>1; bootstrap_LCB95>0; max_drawdown<=0.05; CAGR>0; Calmar>0; no control bypass. Keep stress gates: net_pnl>0; final_equity>10000; gross_loss>0; PF>1; max_drawdown<=0.10; unchanged control rules. All integrity gates remain mandatory. Except for the prescribed NumPy bootstrap result, compare metrics with Decimal constants without a float detour.

## Bootstrap and proposed Float64 boundary behavior

Follow G10-B using n ordered economic net returns, with n>0. Determine L as the smallest positive integer with L**3>=n. Initialize NumPy default_rng(20260907) once. For each of 10000 replicas draw rng.integers(0, n, size=(n+L-1)//L, dtype=np.int64). Expand each start to L consecutive circular observations, concatenate in draw order, truncate to n and compute the mean with dtype=np.float64. Use NumPy percentile 5 with method="linear" over the ordered replica means.

Convert each Decimal net return once, in economic trade order, to float64 via its Decimal string representation. Nonfinite conversion or converting a nonzero Decimal return to float64 zero is an error. Finite nonzero float64 subnormals are explicitly allowed; there is no cutoff at numpy.finfo(float64).tiny and no manual flush-to-zero. Decimal precision 50 does not by itself determine the exponent or prevent subnormals.

Use the bound NumPy float64 arithmetic, including its normal rounding behavior, and check numeric outputs for finiteness. Signed zero has zero comparison semantics; a zero LCB does not pass. Do not replace the prescribed bootstrap with an arbitrary-precision alternative or introduce an epsilon. The runtime must be qualified for subnormal preservation and the exact operation sequence before use; the behavior is specified here, not already validated.

Freeze Python/NumPy versions, platform and implementation identity before result observation. Additional implementation review must explicitly settle the complete NumPy error-state settings and any underflow signaling policy without silently changing this declared admissibility of finite subnormal values.

## Review corrections and remaining gates

Do not describe the normative accumulation as generally numerically exact. Do not claim Decimal lacks fractional-exponent support, that exp/ln requires a hand-written Taylor series, or that finite subnormals must be rejected by definition. Primary technical references: https://docs.python.org/3.12/library/decimal.html#decimal.Context.power and https://numpy.org/doc/2.3/reference/generated/numpy.finfo.html .

The known state_store.py hash difference was traced to added projection helpers outside the inspected active Legacy path. This is static evidence, not a new runtime parity certificate or a claim of whole-file byte identity.

Document review of the identified draft bytes and explicit user acceptance are recorded above. This document does not implement, qualify or execute the method. Pending: applicable governance recording/publication steps not authorized here; complete parser/output schemas; complete numeric trap/error-state settings; helper/ledger integration; synthetic qualification including rounding, midnight, veto and subnormal cases; dependency lock; fresh-state/input/output path contract; complete manifest before new selection metrics; authorized execution and append-only exposure evidence.

No historical Final-OOS claim, T0 or prospective input-path certification follows. The historical dataset remains frozen. Do not reopen the closed P66 boundary investigation. Do not substitute historical characterization metrics for the proposed G10 selection economics.
