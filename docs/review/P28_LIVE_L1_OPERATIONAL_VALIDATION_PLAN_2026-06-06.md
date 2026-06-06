# P28 LIVE L1 OPERATIONAL VALIDATION PLAN

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Transition from infrastructure development to operational validation.

The objective is no longer:

- adding infrastructure
- adding monitoring
- adding recovery logic

The objective is now:

- validate actual runtime behavior
- validate decision quality
- validate execution quality
- validate operational robustness over longer runs

## Current Status

Infrastructure:

PASS

Repository Review:

PASS

Architecture Review:

PASS

Operational Readiness:

PASS

Production Readiness:

NOT APPROVED

## Strategic Question

The next major question is no longer:

"Can the system run safely?"

The next major question is:

"Does the system make good decisions?"

## Validation Principles

Rule 1

No major architecture changes during validation.

Rule 2

One change at a time.

Rule 3

Every run must be documented.

Rule 4

Archive runtime artifacts after every run.

Rule 5

Use safe_launch.py as operational entry point.

## Phase P28A

Operational Smoke Validation

Goal:

Verify complete operational chain.

Run length:

Very short

Checks:

- startup validation
- reconciliation
- monitoring
- runtime control
- execution audit
- state persistence

Success Criteria:

No infrastructure failures.

## Phase P28B

Short Operational Run

Goal:

Observe behavior across a larger runtime window.

Checks:

- monitor stability
- state persistence
- reconciliation consistency
- trade generation

Questions:

- Are trades generated?
- Are states persisted correctly?
- Does monitoring remain consistent?

## Phase P28C

Execution Behavior Review

Goal:

Review generated trades.

Metrics:

- trade count
- long vs short ratio
- holding times
- exits
- stop losses
- time stops

Questions:

- Are trades reasonable?
- Are exits behaving as expected?

## Phase P28D

Signal Quality Review

Goal:

Inspect signal generation quality.

Focus:

- intent generation
- regime handling
- timing module behavior
- intent fusion behavior

Questions:

- Are signals coherent?
- Are obvious bad signals generated?

## Phase P28E

Operational Endurance Run

Goal:

Long-duration paper run.

Focus:

- monitoring stability
- state consistency
- runtime artifacts
- recovery capability

Questions:

- Can the system operate cleanly for extended periods?

## Phase P28F

Paper Performance Baseline

Goal:

Establish baseline operational statistics.

Metrics:

- trades
- winrate
- pnl
- profit factor
- drawdown
- runtime alerts

Result:

Reference baseline for future improvements.

## Explicitly Deferred

Not part of P28:

- broker integration
- exchange APIs
- production activation
- real capital deployment

## Expected Outcome

At the end of P28 we should know:

1. Whether Live L1 behaves correctly.

2. Whether decisions appear sensible.

3. Whether paper operation is stable.

4. Where future strategy improvements should focus.

## Recommendation

Start with:

P28A Operational Smoke Validation

before any further strategy or production work.

## P28 Result

Operational validation plan approved.

Status:

PASS
