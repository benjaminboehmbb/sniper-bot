# Pre-IU-4 Float/Decimal Ownership Decision — 2026-08-09

## Status

**OWNERSHIP DECIDED; IMPLEMENTATION AND IU-4 ACTIVATION REMAIN LOCKED**

Branch: `codex/pre-iu4-decimal-ownership-2026-08-09`

This decision resolves the confirmed architecture blocker between the active
float-based paper execution and the Decimal PEE contracts. It does not activate
IU-4, Exchange, or Live and does not alter the accepted PEE V1 profile.

## Confirmed current state

1. `CSVMarketFeed` converts the raw CSV `close` text to `float` before creating
   `MarketSnapshot`.
2. `FeatureSnapshot` retains only float OHLC/price values.
3. `apply_paper_execution()` uses float price, size, TP/SL calculations, PnL,
   fee subtraction, S2 mutation, and the legacy trade log.
4. Its default/fallback entry quantity is `1.0`.
5. The legacy `fee_roundtrip` is subtracted as an absolute float from gross PnL;
   it is not the PEE notional-scaled entry-plus-exit fee model.
6. PEE shadow converts `str(features.price)` to Decimal for observation only.
   The raw source decimal text has already been lost at that point.
7. `PaperEconomicsConfig`, entry authorization, settlement, S2 V2 artifacts,
   Trade V2, and Paper Account use strict Decimal values and reject float inputs.
8. `PositionStateS2V2` exists for an open LONG/SHORT PEE position, but the active
   state store still reads and writes mutable schema-1 float S2 records. There is
   no active schema-2 S2 store or FLAT schema-2 representation.

Therefore IU-4 cannot safely be implemented by passing a PEE quantity into
`apply_paper_execution()` or by enabling the shadow result as a Boolean gate.
Either approach would leave two independent PnL, fee, position, and trade-log
truths.

## Single-owner decision

### OFF and SHADOW modes

The legacy execution path remains the sole execution owner. PEE remains
read-only and must not mutate S2, S4, throttle state, Paper Account, or the
legacy trade result.

### Future ENFORCED PAPER mode

Decimal PEE becomes the sole owner of all economic values and economic state.
The legacy execution function must not open, size, settle, account, or log a PEE
position.

There is no mode in which legacy float economics and Decimal PEE both write
authoritative results for the same trade.

An invalid, incomplete, or ambiguous mode blocks new entries. Existing exits
remain possible under the explicit legacy-position compatibility rule below.

## Ownership matrix

| Concern | Owner in ENFORCED PAPER | Representation |
|---|---|---|
| Signal scores, regime, intent, timing | Existing strategy pipeline | Existing types, including float where already used |
| TP/SL/time-stop trigger decision | Execution-control layer | May use existing float trigger semantics during migration |
| Source reference price | Market-data boundary | Canonical decimal text preserved from source |
| Entry authorization and sizing | `paper_economics.py` | Decimal |
| Entry/exit modeled fill | `paper_economics.py` | Decimal |
| Quantity and notional | PEE entry quote / S2 V2 | Decimal |
| Entry/exit fees | PEE quote/settlement | Decimal quote-currency values |
| Open position economics | S2 V2 | Decimal, profile-bound |
| Realized PnL/equity/drawdown | Paper Account | Decimal |
| Completed trade economics | TradeRecordV2 | Decimal, append-only evidence |
| Kill/risk mode | S4 | Existing risk authority; not an accounting owner |
| Entry rate/cooldown | Paper Entry Throttle | Profile-bound operational state |
| Legacy trade JSONL | Compatibility projection only | Derived after authoritative commit; never an input |

Float remains permitted for strategy and trigger calculations only. It must not
cross into economic authorization, sizing, persistence, settlement, account
limits, or economic audit as an authoritative value.

## Required market-data boundary

The raw decimal price text must survive ingestion.

Required additive fields for the future integration:

- `MarketSnapshot.reference_price_text`;
- `FeatureSnapshot.reference_price_text`.

For CSV replay, the value comes directly from the stripped source `close` cell.
It is validated as a finite positive decimal but not converted through float.
The existing float `price` remains available to strategy and trigger logic.

For a future exchange feed, the canonical text must be produced directly from
the exchange decimal/integer representation. The following are forbidden as an
economic boundary:

- `Decimal(float_value)`;
- re-creating authority from `str(features.price)` after float parsing;
- accepting a float in a PEE factory and silently normalizing it;
- fallback price, quantity, fee, or PnL values.

Canonical decimal strings are used in persisted records and hashes. Decimal is
constructed exactly once at the PEE boundary and remains Decimal thereafter.

## Required ENFORCED PAPER entry sequence

For a FLAT BUY/SELL candidate:

1. Validate mode, profile identity, raw price text, event identity, and
   reconciled startup state.
2. Evaluate the existing pre-execution risk/gate authority.
3. Evaluate Paper Account loss, drawdown, and actual-fee limits.
4. Evaluate the profile-bound entry throttle.
5. Call Decimal PEE authorization with the canonical price text, reconciled
   realized equity, and explicit reference stop.
6. On rejection, persist only denial evidence. S2, Paper Account, and throttle
   accepted-entry state remain unchanged.
7. On authorization, construct the complete S2 V2 open position directly from
   the returned `EntryEconomicsQuote`. No field is recalculated as float.
8. Commit the accepted-entry throttle event and S2 V2 position through one
   recoverable entry transaction identity.
9. Only after the authoritative commit succeeds, emit audit and any legacy
   compatibility projection.

`apply_paper_execution()` is not called for the entry mutation in ENFORCED
PAPER mode. Passing `hypothetical_quantity` into its `position_size` argument is
explicitly prohibited.

## Required ENFORCED PAPER exit sequence

The current monolithic `apply_paper_execution()` mixes trigger evaluation,
mutation, float settlement, logging, and loss-cluster updates. ENFORCED PAPER
requires those responsibilities to be separated.

1. A pure execution-control step determines whether the unchanged TP/SL,
   time-stop, or opposing-intent exit condition fired.
2. Load the authoritative S2 V2 entry economics and reconciled Paper Account.
3. Convert the current canonical source price text directly to Decimal.
4. Call PEE settlement exactly once.
5. Build `TradeRecordV2` from the stored entry quote and settlement.
6. Commit settlement journal and Paper Account exactly once.
7. Transition S2 V2 to an explicit FLAT schema-2 state through the same
   recoverable close transaction identity.
8. Emit audit and compatibility logs only from the committed Decimal artifacts.

The legacy `_compute_pnl()`, `_compute_pnl_pct()`, absolute `fee_roundtrip`
subtraction, and `_log_closed_trade()` are not economic authorities for PEE
trades.

## Legacy open-position compatibility

An open schema-1 position has no complete PEE entry quote and must never be
silently upgraded or assigned invented fills/fees.

On transition to ENFORCED PAPER:

- an existing schema-1 open position is **exit-only**;
- it closes through the legacy compatibility path;
- the close is marked `economics_incomplete` and is not booked as a precise PEE
  settlement;
- no new PEE entry is allowed until S2 is FLAT and startup reconciliation passes;
- historical trades are not retroactively revalued.

## Atomicity and restart consequence

The Float→Decimal takeover exposes a required transaction boundary that is not
implemented today:

- entry: throttle accepted-event + S2 V2 open position;
- exit: TradeRecordV2 + Paper Account settlement + S2 V2 FLAT transition;
- every artifact must share one stable execution event/transaction identity.

Independent writes with no coordinator are prohibited. In particular, a crash
after the throttle commit but before S2 mutation must recover the same entry,
not consume cooldown and lose the position. A crash after settlement but before
S2 becomes FLAT must complete the close without booking PnL twice.

The next implementation specification must choose one write-ahead coordinator
or equivalent journaled transaction protocol and define recovery for every
interruption point. This is coordinated with, but does not transfer ownership
to, the separate S2/S4/execution reconciliation task.

## Required implementation packages

1. **Canonical price carrier:** preserve raw decimal text through MarketSnapshot
   and FeatureSnapshot with parity tests proving strategy floats are unchanged.
2. **Version-aware S2 store:** add explicit schema-2 FLAT/open contracts and
   reject unsupported or incomplete states for new entries.
3. **Pure execution-control extraction:** determine entry/exit action without
   mutating state or calculating economics.
4. **Paper execution coordinator:** own guarded PEE entry and settlement
   transactions, including throttle and recovery identities.
5. **Compatibility projection:** derive any legacy-shaped logs from committed
   Decimal artifacts; label them non-authoritative.
6. **Mode switch:** OFF/SHADOW use legacy owner; future ENFORCED PAPER uses PEE
   owner; invalid transitions fail closed.

These packages must be individually reviewable. No single large rewrite of
`execution.py` is authorized by this decision.

## Mandatory acceptance tests before IU-4 activation

- raw source decimal text reaches PEE without a float round trip;
- OFF and SHADOW preserve the certified legacy path byte/field parity;
- ENFORCED rejection leaves S2, account, and throttle accepted state unchanged;
- ENFORCED entry quantity equals the authorized Decimal quantity exactly;
- no fallback quantity `1.0` is reachable in ENFORCED mode;
- PEE fees scale with executed notional and are applied exactly once;
- LONG/SHORT settlement and TradeRecordV2 are exactly reproducible;
- every logged economic value is derivable from committed Decimal artifacts;
- legacy open position remains exitable but cannot create fabricated PEE PnL;
- interruption at every entry/exit write boundary recovers exactly once;
- S2, throttle, TradeRecordV2, Paper Account, and audit transaction IDs agree;
- corrupt, missing, unsupported, or policy-mismatched state blocks entries and
  never blocks risk-reducing exits;
- full L1 and regression suites remain green;
- workstation shadow/full-history evidence passes before activation.

## Final decision

| Question | Decision |
|---|---|
| Can PEE quantity be passed into legacy `apply_paper_execution()`? | NO |
| Can `str(features.price)` become the final price authority? | NO |
| May strategy/trigger code remain float during migration? | YES, but never as economic authority |
| Is Decimal PEE the sole ENFORCED PAPER economics owner? | YES |
| May legacy and PEE both book/log authoritative economics? | NO |
| May a legacy open position be silently upgraded? | NO; exit-only compatibility |
| Is active IU-4 wiring authorized by this document? | NO |
| Are Exchange and Live unlocked? | NO |
