# P25B DEAD CODE CANDIDATE DECISION

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Decide how to classify Live L1 dead-code candidates after content inspection.

No files are moved or deleted in this step.

## Reviewed Candidates

### live_l1/io/validate.py

Decision:

ARCHIVE_CANDIDATE_STRONG

Reason:

- imported_by=0
- overlaps conceptually with active live_l1/io/valid.py
- appears to be an older Step 2/8 validation module
- not part of the current Live L1 loop

Action:

Do not archive yet.
Mark for possible archive in next cleanup step.

### live_l1/core/gate_builder.py

Decision:

KEEP_FUTURE

Reason:

- contains online gate-building logic
- maps regime_v1 to allow_long/allow_short
- may become relevant for true online signal/regime construction

Action:

Keep.

### live_l1/core/regime_builder.py

Decision:

KEEP_FUTURE

Reason:

- contains online regime_v1 builder logic
- may become relevant when moving beyond CSV-precomputed regime inputs

Action:

Keep.

### live_l1/core/regime_v2_builder.py

Decision:

KEEP_FUTURE

Reason:

- contains regime_v2 construction logic
- related to future online regime handling

Action:

Keep.

### live_l1/core/signal_builder.py

Decision:

KEEP_FUTURE

Reason:

- contains online GS-compatible 1m signal builder logic
- important for future live-market signal construction

Action:

Keep.

### live_l1/guards/cost_guards.py

Decision:

KEEP_FUTURE_SAFETY

Reason:

- deterministic cost and overtrading guard module
- no side effects
- entry permission layer
- likely useful before production readiness

Action:

Keep.

### live_l1/core/timing_5m_v2.py

Decision:

KEEP_EXPERIMENTAL_PAIR

Reason:

- experimental 5m timing core v2
- not active in current loop
- future timing improvement candidate

Action:

Keep together with its test.

### tools/test_timing_5m_v2_minimal.py

Decision:

KEEP_EXPERIMENTAL_PAIR

Reason:

- minimal isolated test for timing_5m_v2.py

Action:

Keep while timing_5m_v2.py is retained.

## Final P25B Classification

Archive Candidate:

- live_l1/io/validate.py

Keep Future:

- live_l1/core/gate_builder.py
- live_l1/core/regime_builder.py
- live_l1/core/regime_v2_builder.py
- live_l1/core/signal_builder.py

Keep Future Safety:

- live_l1/guards/cost_guards.py

Keep Experimental Pair:

- live_l1/core/timing_5m_v2.py
- tools/test_timing_5m_v2_minimal.py

## Recommendation

Do not perform broad cleanup.

Only archive live_l1/io/validate.py after one final reference check.

## P25B Result

Candidate inspection completed.

Status:

PASS
