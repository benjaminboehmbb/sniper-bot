# Pre-IU-4 Rate/Cooldown Policy Decision — 2026-08-09

## Status

**Decision:** preserve the safety mechanisms, replace the legacy implementation,
and do not adopt its numeric limits without calibration.

This document is a design decision only. It does not authorize IU-4, Exchange,
or Live. It does not change the accepted PEE V1 economics profile.

## Scope

Reviewed mechanisms from `live_l1/guards/cost_guards.py`:

- maximum trades per UTC day;
- maximum trades in a rolling six-hour window;
- minimum cooldown between trades.

The legacy fee-budget, daily-net-loss, fee-configuration, and gate-mode checks
were reviewed only to determine whether they still own unique protection.

## Findings

### 1. The legacy guard is not active authority

Repository usage audits show no production consumer or dedicated test for
`cost_guards.py`. Its inputs are not connected to the active entry path.

Legacy S4 fields named `trades_today`, `trades_6h`,
`last_trade_timestamp_utc`, and `cooldown_until_utc` are initialized, loaded,
validated, and persisted, but no execution code increments or updates them.
Persisting a value that remains zero or empty does not make the guard active.

### 2. The old numeric limits must not be copied as policy

The legacy constants are:

| Mechanism | Legacy value | Decision |
|---|---:|---|
| UTC-day cap | 400 trades | Preserve mechanism; calibrate value |
| Rolling window cap | 140 trades / 6 h | Preserve mechanism; replace value |
| Cooldown | 3 minutes | Preserve mechanism; calibrate value |

The combination is internally weak: a strict three-minute cooldown permits at
most 20 entries per hour and therefore at most 120 entries in six hours. The
140-per-six-hour limit can never become the blocking condition while that
cooldown is enforced. The daily limit can still bind because the same cooldown
permits at most 480 entries per 24 hours.

The values have no profile identity, version, provenance, calibration evidence,
or reproducible link to the IU-3 full-history dataset. They are therefore not
accepted PEE policy.

### 3. Existing PEE V1 does not contain rate/cooldown state

The accepted profile
`config/pee/PEE_V1_PAPER_CONSERVATIVE_CANDIDATE_001.json` contains monetary
limits for actual daily fees, daily loss, and realized drawdown. It has no daily
entry count, rolling-window count, or cooldown field.

`PaperAccountState.closed_trade_count` is a lifetime settlement sequence, not a
daily or rolling counter. The account snapshot also does not retain a durable
history of accepted entry timestamps. Consequently, the current account guard
cannot deterministically enforce these mechanisms across restart.

### 4. The intent cooldown is not a replacement

`live_l1/core/intent.py` has a separate strategy cooldown of 120 or 200 ticks
after a position becomes flat. It is in-memory, resets with process/tick reset,
and is based on tick count rather than durable event time. Forced test intents
also bypass it.

That cooldown may remain as signal-quality logic, but it cannot be the account
safety throttle. The two controls must have distinct names, ownership, tests,
and reason codes.

### 5. The other legacy checks already have stronger successors

| Legacy check | Successor / decision |
|---|---|
| Estimated fee budget from trade count and hard-coded float fee | Replaced by actual quote-denominated daily fees and `max_daily_fee_rate` |
| Hard-coded ROI daily net floor | Replaced by profile-bound daily-loss and realized-drawdown guards |
| Float fee mismatch | Replaced by strict config/profile fingerprint reconciliation |
| `gate_mode == auto` | Replaced by the pre-execution entry guard and explicit runtime mode checks |

These legacy checks must not be duplicated in the new throttle.

## Required successor

Create a separate, versioned **Paper Entry Throttle Policy** rather than adding
unversioned fields to `PaperEconomicsConfig` schema V1.

Minimum policy contract:

- `schema_version`;
- `policy_profile_id`;
- `policy_model_version`;
- `max_entries_per_utc_day`;
- `max_entries_per_rolling_window`;
- `rolling_window_seconds`;
- `min_reentry_cooldown_seconds`;
- canonical policy fingerprint.

Minimum durable state/evidence:

- accepted entry event ID and event timestamp;
- UTC-day bucket and accepted-entry count;
- bounded rolling-window entry events or equivalent replayable journal;
- last accepted entry timestamp;
- policy identity and fingerprint;
- idempotent last-update event ID.

The throttle must:

- count **accepted entries**, not strategy intents and not only completed exits;
- use the authoritative event timestamp, never the local wall clock;
- be deterministic in replay and after restart;
- update atomically and idempotently with entry authorization evidence;
- fail closed on corrupt or mismatched throttle state;
- always allow exits;
- run before any entry-side state mutation.

Proposed stable blocking reasons:

- `PEE_RATE_DAILY_ENTRY_LIMIT`;
- `PEE_RATE_ROLLING_ENTRY_LIMIT`;
- `PEE_RATE_REENTRY_COOLDOWN`;
- `PEE_RATE_POLICY_MISMATCH`;
- `PEE_RATE_STATE_INVALID`.

## Calibration rule

No numeric limit is accepted by this review.

The three values must be derived from the IU-3 full-history evidence on the
workstation and then explicitly approved in a named policy profile. Calibration
must report at least:

- entries per UTC day distribution;
- entries per rolling six-hour window distribution;
- time between accepted entries distribution;
- number and percentage of entries blocked for each candidate threshold;
- PnL, fee, drawdown, and trade-count deltas versus the unthrottled shadow run;
- deterministic replay hash for the selected candidate.

Changing a threshold requires a new profile identity or fingerprint. It must
not silently alter the accepted PEE V1 economics fingerprint.

## Implementation gates

`live_l1/guards/cost_guards.py` may be archived only after all of the following
are true:

1. the new profile-bound throttle contract is implemented and tested;
2. restart/replay/idempotency and corrupt-state fail-closed tests pass;
3. daily, rolling-window, cooldown-boundary, and exit-always-allowed tests pass;
4. the throttle is wired into the pre-execution entry path;
5. full-history calibration evidence and selected thresholds are approved;
6. a usage audit proves the legacy module has no remaining consumer.

Until then, the legacy file remains a documented refactor-first/archive-later
candidate, not active protection.

## Final classification

| Item | Classification |
|---|---|
| Daily entry cap mechanism | KEEP / REIMPLEMENT |
| Rolling-window entry cap mechanism | KEEP / REIMPLEMENT |
| Re-entry cooldown mechanism | KEEP / REIMPLEMENT |
| Legacy constants 400 / 140 / 3 min | DO NOT ADOPT WITHOUT CALIBRATION |
| Legacy fee/net/gate duplication | REPLACE WITH EXISTING AUTHORITIES |
| `cost_guards.py` today | REFACTOR FIRST; ARCHIVE LATER |
| IU-4 / Exchange / Live | REMAIN LOCKED |
