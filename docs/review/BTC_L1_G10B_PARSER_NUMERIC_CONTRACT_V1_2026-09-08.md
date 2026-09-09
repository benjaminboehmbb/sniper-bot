# BTC-L1 G10-B Parser / Numeric Contract V1

## Status and authority

APPROVED_FOR_ADOPTION. The user expressly accepts P01-P07 under the decisions recorded below and authorizes recording that acceptance in these two documents. Existing approved G10-B calculation rules remain unchanged. Implementation, test execution, candidate manifest, commit, push and market run remain unauthorized. Acceptance of these decisions is not a completed implementation contract or a parser, runtime or numerical qualification certificate.

The reviewed draft consolidated user-reported Antigravity proposals with corrections checked against the bound source excerpts and primary documentation. Prior Antigravity answers contained errors; they are not blanket approval evidence. Repository/source hash checks establish document identity, not numerical qualification. All fixtures below are proposed tests, not executed tests or market observations.

## Preserved approved rules

All economics, sizing, cost, settlement, canonical-equity, metric and bootstrap formulas are inherited by reference from the approved clarification. This document does not replace those sections with abbreviated formulas.

In particular: canonical cumulative PnL is added in economic trade order, and equity is initial equity plus that cumulative value. Net trade return uses positive canonical realized equity immediately before the accepted entry. Costs apply once per execution leg; settlement-day accounting is preserved. Operative DD >= 0.05 blocks new economic entries in BOTH scenarios; exits remain permitted. Result DD gates remain nominal <= 0.05 and stress <= 0.10. No independent economic stop exit is introduced. Legacy float stop reconstruction is used only for the approved sizing reference.

The bound candidate and Legacy helpers must not be edited or monkeypatched by the evaluator. Economic account state is distinct from Legacy S2/S4 state. Existing helpers may only be reused after qualification against the approved rules.

## Source-backed semantic interface

The V4 semantic stream is not the ordinary physical log. FastReplayLoggerV4.log emits category, event and severity, followed by sorted escaped fields, excluding tick_started_utc; it appends LF and hashes UTF-8 bytes. Preserve and hash the complete original stream, including other event categories. Do not reserialize input, sort events or globally reverse escaping. Split each key/value token at its first equals sign.

loop.py:1110-1125 emits category=L2, event=market_snapshot, severity=INFO. Its fields are tick, snapshot_id, timestamp_utc, symbol, price, reference_price_text, allow_long, allow_short and regime_v2.

loop.py:1241-1258 emits category=L5, event=execution, severity=INFO. Its fields are tick, action, executed, position_before, position_after, side_after, entry_price, entry_timestamp_utc and reason. It contains no current market timestamp or entry_reference_text field. Current execution time and exact opening/closing reference prices are obtained from the paired snapshot; preserve opening information until its corresponding close.

The source emits action values OPEN_LONG, OPEN_SHORT, CLOSE_LONG, CLOSE_SHORT and NOOP. There is no separate action=VETO. Positions are FLAT, LONG and SHORT; side_after is lowercase long, lowercase short or the empty string. OPEN actions have executed=1 and change FLAT to the matching side; CLOSE actions have executed=1 and change that side to FLAT. NOOP has executed=0 and preserves position. Closing clears emitted entry_price and entry_timestamp_utc. NOOP metadata must be checked for consistency without overwriting the evaluator's saved opening metadata.

Require one snapshot followed by one execution for every complete tick, allowing intervening other events. Check the manifest-bound first/last ticks and complete successor sequence, not merely increasing IDs. Reject duplicate, missing, orphaned or unfinished pairs and inconsistent action/executed/position/side combinations. Final semantic FLAT is required at full-stream EOF, not at each midnight.

Only an executed semantic OPEN is classified per scenario as ENTRY_ACCEPTED or ENTRY_VETOED. A Legacy-blocked NOOP is not an economic veto trade. A veto has no simulated economic trade, fee or PnL; its later semantic CLOSE completes its audit pairing. Per scenario, 563 equals economically closed trades plus complete veto pairs. No open positions or unmatched identities may remain.

Validate category/severity for the two interpreted event types. Numeric metadata needs explicit grammar and finiteness checks. Economic reference prices must be finite and positive and must not fall back to the float price field. Complete field grammars, symbol/snapshot-ID constraints and output schemas still require specification and qualification; an abbreviated field list is not a completed schema.

## Accepted UTC parser: P01

Use fullmatch with the ASCII pattern below, followed by explicit calendar and clock validation:

    [0-9]{4}-[0-9]{2}-[0-9]{2}[T_][0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|\+00:00)

Accept no fraction or an all-zero fraction. After syntactic matching, reject any nonzero fractional digit as UNSUPPORTED_TIMESTAMP_PRECISION. Reject malformed syntax, invalid dates/times, absent or non-UTC offsets and trailing characters. Do not truncate, round, generically unescape or strip a token into validity. Keep its original bytes. Decode T/underscore only in this timestamp field; underscore is the logger's representation of a source space. Whole-second differences use integer timedelta components, not floating total_seconds.

This grammar is an accepted admission rule, not evidence that every canonical input timestamp satisfies it. Support for real subsecond timestamps would require a separate decision; it must not be improvised after observing results.

Proposed fixtures: 2017-08-17T04:00:00Z, 2017-08-17_04:00:00+00:00 and 2017-08-17T04:00:00.000Z are accepted. The .123Z variant produces UNSUPPORTED_TIMESTAMP_PRECISION. Invalid month 13, second 61, +02:00, absent timezone, empty token and appended characters are rejected. Actual embedded control bytes and literal backslash escape sequences need separate rejecting fixtures.

## Accepted NOOP reference-price decision: P02

An EMPTY reference_price_text is tolerated only on a valid semantic NOOP (executed=0), with audit recording, and only if every other required integrity check passes. Record the original token, tick, semantic state and classification EMPTY_REFERENCE_ON_SEMANTIC_NOOP; record the underlying raw-value cause as UNKNOWN. Do not infer that the source data were valid or that the missing value was harmless.

The bound market.py:_canonical_positive_decimal_text returns an empty string for absent, malformed, nonfinite or nonpositive raw values. These causes cannot be distinguished from the emitted empty token alone. This acceptance does not authorize additional market-data inspection, repair, fallback or hypothetical trade calculation.

Reject NONEMPTY reference texts that are syntactically invalid, nonfinite or nonpositive, including on NOOP ticks. A nonempty valid finite positive reference follows normal validation. The empty-token exception does not waive finite-value checks on other numeric fields, NOOP metadata consistency, tick/position continuity, semantic-stream identity or any other required integrity evidence.

For every executed semantic OPEN or CLOSE, missing or invalid reference_price_text causes an error, irrespective of economic acceptance or veto. Never substitute the float price field. A semantic NOOP does not become an economic veto or a zero-PnL trade. Preserve saved entry metadata and keep economic and semantic ledgers separate.

## Decimal settings and their status

Inherited parameters: prec=50, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999, clamp=0. Precision means significant decimal digits; it is not a fixed 10^-50 resolution and does not guarantee exact arithmetic.

Accepted additional parameter P03: capitals=1. Accepted initialization P04: ALL nine signal flags start False. Flags can subsequently become True; they must not be confused with traps or silently cleared to hide a failure. Use an explicitly constructed local context for all Decimal economics and metrics, without inheriting caller settings.

Trap settings implementing inherited error/rounding rules:
- InvalidOperation=True
- DivisionByZero=True
- Overflow=True
- Inexact=False
- Rounded=False

Additional accepted trap settings:
- P05: FloatOperation=True
- P06: Underflow=True, Subnormal=True, Clamped=True

P06 intentionally introduces additional rejection of Decimal subnormal or exponent-adjustment conditions. Such conditions do NOT inherently prove an internal bug. This stricter numeric admission boundary is expressly accepted under P06; it is not implied by prec=50, clamp=0 or the Float64 policy.

FloatOperation is a limited guard, not complete type enforcement. Decimal-plus-float raises TypeError. Decimal(float) can trigger FloatOperation; explicit Decimal.from_float does not. Mixed equality can remain permitted, so API/type checks and review are still needed. Finite-value checks are explicit: constructing Decimal('NaN') alone does not guarantee a trapped exception.

Reproduce the approved Legacy float operations in their prescribed order, then use Decimal.from_float for the stop value. Do not replace the calculation by pure Decimal arithmetic or Decimal(str(float_value)). The prescribed bootstrap boundary converts each ordered economic net return through its Decimal string to Float64 once. Reject nonfinite conversions and nonzero Decimal values converted to Float64 zero. Other float metadata handling must remain outside authoritative Decimal economics.

## Accepted NumPy error state: P07

Use a local np.errstate(invalid='raise', divide='raise', over='raise', under='ignore') for the prescribed Float64 bootstrap operations, restoring the caller's state afterward. These values specify error signaling only. They do not enable or guarantee hardware gradual underflow, and ignore is not the only possible policy compatible with admitting finite subnormals.

The approved Float64 operation sequence and normal rounding remain unchanged. Check inputs and outputs for finiteness explicitly; errstate is not a general detector of preexisting NaN/Inf. Finite subnormals are allowed, manual flush-to-zero is forbidden, and runtime preservation must be qualified. A legitimately rounded zero in later arithmetic has zero comparison semantics; a zero LCB does not pass. Do not accept zero as an alternative in a fixture specifically designed to preserve a nonzero subnormal.

## Proposed numerical fixtures: NOT EXECUTED

All Decimal arithmetic fixtures use the stated precision/exponent/rounding parameters and initially clear flags. A diagnostic context below has all traps False solely to inspect signal flags. It is not permission to disable proposed production traps. Production reactions refer to accepted P05/P06; they are not test results.

N01: Decimal('1') / Decimal('3'): finite rounded result, Inexact and Rounded flags True; their traps False, so continue.
N02: Decimal('0') / Decimal('0'): InvalidOperation, abort. Separately construct NaN and Infinity and reject them through is_finite() validation.
N03: Decimal('1') / Decimal('0'): DivisionByZero, abort.
N04: Decimal('1e500000') * Decimal('1e500000'): Overflow, abort. Merely exceeding the value 1e999999 is not itself overflow.
N05: Decimal('1e-999999') / Decimal('10'): exact 1e-1000000. Diagnostic flags: Subnormal=True, Underflow=False, Inexact=False, Rounded=False. Proposed production Subnormal trap aborts.
N06: Decimal('1e-1000048') / Decimal('3'): the exact result is below Etiny=-1000048 and rounds to zero. Diagnostic flags include Underflow, Subnormal, Inexact, Rounded and Clamped. Proposed production context aborts; do not call N05 an Underflow test.
N07: context.create_decimal('0e-1000049'): diagnostic zero exponent is adjusted to Etiny=-1000048 and Clamped is signaled. Proposed production Clamped trap aborts. Clamped is not proof that clamp=0 was violated.
N08: Decimal('1.5') + 1.0: native TypeError. Separate Decimal(1.5) construction: proposed FloatOperation trap aborts. Separate Decimal.from_float(1.5): allowed exact conversion. Mixed equality is not assumed to be trapped.
N09: x=np.float64('1e-315'); eight identical elements in a Float64 array; np.mean(array, dtype=np.float64) under the complete P07 error state must equal the original x bit-for-bit and remain nonzero. Compare to x, not the infinitely precise decimal literal. Failure means runtime qualification is blocked, not that the candidate has failed an economic selection gate.
N10: np.float64(str(Decimal('1e-400'))): conversion yields zero; explicit nonzero-Decimal-to-zero guard aborts. Use ASCII minus signs in executable fixtures.

These fixtures are not a complete qualification suite. Also qualify all numeric error states, finite-value guards, canonical summation, quantities, costs, midnight, vetoes, gate boundaries and undefined metrics, without evaluating historical market results during synthetic qualification.

## Accepted decisions and remaining gates

P01-P07 are expressly accepted by the user, including the completed P02 rule above. Acceptance is limited to these decisions; inherited settings remain governed by the approved clarification. The remaining implementation and qualification gates below are not waived.

Still pending: full parser and output schemas; typed error/status contract; exact Python/NumPy/platform and dependency identities; helper integration; synthetic qualification; fresh-state/input/output path bindings; complete manifest before new selection metrics; independently reconciled semantic trade/audit/order/final states; authorized execution and append-only exposure recording.

Dataset identity and semantic-stream identity are separate. The known dataset SHA256 is 530983b84c461d46a49058428b1549fa87fd320cb2f04a070eeb081275aafe1f. The certified semantic stream has 30621902 events and SHA256 ffa200c601dc6c2bdda0492909d6518573af6de0b621deb91ee3c9f46d7022e3. These are inherited metadata, not recomputed results. Validate the entire stream and other required integrity evidence before releasing selection metrics. A digest match alone is insufficient.

The missing historical normalized-trade serialization remains a disclosed provenance gap. Do not reconstruct it as an original algorithm or reopen the closed P66 investigation. No historical Final-OOS claim, T0, Paper Trading or live-capital authorization follows from this acceptance.

## Primary technical references

- https://docs.python.org/3.12/library/decimal.html
- https://speleotrove.com/decimal/daexcep.html
- https://numpy.org/doc/2.3/reference/generated/numpy.errstate.html
- https://numpy.org/doc/2.3/reference/generated/numpy.seterr.html

Documentation versions are references, not runtime locks. Library claims were reviewed from documentation; fixtures have not been executed.

## Formal acceptance record

```json
{
  "accepted_decisions": {
    "P01": "Specified ASCII UTC fullmatch grammar; calendar/clock validation; accept absent or all-zero fraction; reject nonzero fraction without truncation.",
    "P02": "Empty reference only on valid semantic NOOP with audit and unknown raw cause, subject to all other integrity checks. Reject nonempty malformed/nonfinite/nonpositive reference values. OPEN/CLOSE require valid reference regardless of economic veto. No float fallback.",
    "P03": "capitals=1",
    "P04": "All nine signal flags initially False; later flags may become True; trap settings remain distinct.",
    "P05": "FloatOperation=True as a limited additional guard; explicit Decimal.from_float remains allowed; type checks remain necessary.",
    "P06": "Underflow=True, Subnormal=True, Clamped=True as additional accepted rejection conditions, not proof of a software bug.",
    "P07": "Local np.errstate(invalid='raise', divide='raise', over='raise', under='ignore'); explicit finiteness checks and runtime subnormal qualification remain required."
  },
  "authority": "EXPLICIT_USER_AUTHORIZATION_IN_CURRENT_CONVERSATION",
  "candidate_manifest_authorized": false,
  "commit_authorized": false,
  "date_utc": "2026-09-08",
  "decision": "FORMALLY_ACCEPT_P01_THROUGH_P07",
  "historical_wording": "Remaining Proposed wording concerns retained, unexecuted qualification fixtures from the reviewed draft; it does not leave P01-P07 unaccepted.",
  "implementation_authorized": false,
  "json_field_scope": {
    "contract_text": "Exact UTF-8 body starting at Status and authority, including this acceptance record; excludes the document title and final Source identity bindings section.",
    "contract_text_sha256": "SHA256 of UTF-8 contract_text, including its final LF.",
    "markdown_sha256": "SHA256 of the complete Markdown file bytes.",
    "source_bindings": "Structured source identities also rendered in the final Markdown source appendix."
  },
  "market_run_authorized": false,
  "push_authorized": false,
  "remaining_gates": "Complete schemas, error/status contracts, runtime/dependency identities, helper integration, synthetic qualification, path bindings, full manifest before new selection metrics, integrity reconciliation and authorized exposure recording remain open.",
  "repository_publication_state": "NOT_COMMITTED_NOT_PUSHED_AT_ACCEPTANCE_RECORDING",
  "review_errata": [
    "The different scope of contract_text and the complete Markdown file is intentional, not a consistency defect. Their separate hash bindings are retained.",
    "N05 produces an exact subnormal without rounding loss; it is not rounding down and does not signal Underflow.",
    "FloatOperation does not prevent every mixed operation; mixed equality can remain allowed and explicit from_float does not trigger it.",
    "The nonzero-to-zero guard applies at Decimal-to-Float64 conversion; it is not a general prohibition on later correctly rounded zero results.",
    "An empty emitted reference does not prove harmless absence: bound normalization can also map invalid raw inputs to an empty string."
  ],
  "review_source": "ANTIGRAVITY_WORKSTATION_REVIEW_REPORTED_BY_USER",
  "reviewed_contract_text_sha256": "30a7de64952c002454fc69eb5d6147060cc40f76838220018a35eca1bf49be1a",
  "reviewed_json_sha256": "7f2d092aab475597e85a45f999934ca8dc788a2ee1ec1c3842bbc80ed39e11f9",
  "reviewed_markdown_sha256": "0c9c639526d8f6e488a756af0ab3dc0768ae2b362add54488b0141b6335d6037",
  "selection_authorized": false,
  "test_execution_authorized": false,
  "unchanged_inherited_rule_section_sha256": "4386c63ac4315f4243506150332fc8b58c21fc9fc9c358bc5be01782484b1601"
}
```

## Source identity bindings

- Path: `docs/review/BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08.md`
  Commit: `831857cea2dcdab3535e200d694c493cbfbc94d0`
  SHA256: `7962f6d9dbd66b9c6e3ea3a66b46b60ac765821deabd7f00ed8b1536daaa6b53`

- Path: `docs/review/evidence/BTC_L1_G10B_EVALUATOR_CLARIFICATION_V1_2026-09-08.json`
  Commit: `831857cea2dcdab3535e200d694c493cbfbc94d0`
  SHA256: `90b99bac40c7f640ba2df69e6f97a750e25b0762f83a8c6fc973184a3189e830`

- Path: `docs/review/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.md`
  Commit: `831857cea2dcdab3535e200d694c493cbfbc94d0`
  SHA256: `628abdb89135f747dd24df624a416aeffa591d1486b8f8cce86779a627d5167e`

- Path: `docs/review/evidence/BTC_L1_FINAL_PROTOCOL_PREREGISTRATION_V1_2026-09-07.json`
  Commit: `831857cea2dcdab3535e200d694c493cbfbc94d0`
  SHA256: `21c5730a0f1a6134a826fd2ba34e8ff8c5ad8d7ff739ac6d8b45f6d7df57786a`

- Path: `live_l1/tools/run_btc_l1_fast_replay_v4_a67b3da.py`
  Commit: `3c5927127a03de13d8c80a720f5c8b97a2a36789`
  SHA256: `af49126179eae0d7885d2ba07e0c342c1be9724a940457a8eb2f7a244b3a0292`

- Path: `live_l1/core/loop.py`
  Commit: `3c5927127a03de13d8c80a720f5c8b97a2a36789`
  SHA256: `54e9e7bc0977a9c94f2e85a3279157678249a8569cff63f7d4f29131443fd058`

- Path: `live_l1/logs/logger.py`
  Commit: `3c5927127a03de13d8c80a720f5c8b97a2a36789`
  SHA256: `cbfb29708bc81bbf7f2d524abe10a21382213973f897038bc8c315bad1323cfd`

- Path: `live_l1/io/market.py`
  Commit: `3c5927127a03de13d8c80a720f5c8b97a2a36789`
  SHA256: `014bbf7328c4bd354fb8a254979ef463670e49557c5ed89e5628a3b35dc8cd0e`

- Path: `live_l1/core/execution.py`
  Commit: `3c5927127a03de13d8c80a720f5c8b97a2a36789`
  SHA256: `a76f600d27feef969665bcd695ce11bc4e3abae0f25e045f7416fc78cd2513e3`
