# P26 LIVE L1 ARCHITECTURE DEPENDENCY REVIEW

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Review the active Live L1 architecture dependencies after completion of:

- P4-P22 infrastructure hardening
- P23 repository usage audit
- P24 dependency and entry-point audit
- P25 dead-code candidate review and archive

No runtime behavior changes are introduced.

## Active Live L1 Entry Points

### Primary Operational Launch

live_l1/tools/safe_launch.py

Purpose:

Safe operational startup.

Responsibilities:

- read operational profile
- block PRODUCTION
- run startup validation
- run reconciliation
- enforce required safety flags
- start Live L1 loop

### Legacy / Direct Paper Entry Review

scripts/run_live_l1_paper.py

Purpose:

Direct paper runner.

Status:

REVIEW REQUIRED

Reason:

It imports live_l1.core.loop directly and may bypass newer P17-P21 controls if used incorrectly.

Decision:

Do not delete.
Do not use as primary operational entry point.
Primary entry point is safe_launch.py.

### Monitoring Entry Point

live_l1/tools/monitor_runtime.py

Purpose:

Generate machine-readable monitor status.

Output:

live_state/monitor_status.json

### Monitoring Summary Entry Point

live_l1/tools/monitor_summary.py

Purpose:

Operator-readable monitor summary.

### Runtime Control Entry Point

live_l1/tools/runtime_control_loop.py

Purpose:

Generate unattended control decision.

Output:

live_state/runtime_control.json

## Active Runtime Dependency Flow

safe_launch.py
-> operational_profiles.py
-> startup_validator.py
-> reconcile_runtime_state.py
-> loop.py

loop.py
-> logger.py
-> market.py
-> valid.py
-> state_store.py
-> state_validation.py
-> guards.py
-> clock.py
-> feature_snapshot.py
-> regime_detector.py
-> intent.py
-> timing_5m.py
-> intent_fusion.py
-> execution.py
-> recover_runtime_state.py
-> reconcile_runtime_state.py
-> startup_validator.py
-> meta_state_shadow.py
-> meta_state_runtime.py

execution.py
-> execution_audit.jsonl
-> trades_l1.jsonl
-> loss_cluster_state.json

state_store.py
-> s2_position.jsonl
-> s4_risk.jsonl

monitor_runtime.py
-> startup_validator.py
-> reconcile_runtime_state.py
-> replay_execution_state.py
-> validate_runtime_schema.py
-> operational_profiles.py
-> monitor_status.json

runtime_control_loop.py
-> monitor_runtime.py
-> runtime_control.json

## Source-of-Truth Runtime Files

Primary runtime source of truth:

live_logs/execution_audit.jsonl

Reason:

Used for deterministic replay.

Secondary runtime state:

live_state/s2_position.jsonl

live_state/s4_risk.jsonl

Trade record:

live_logs/trades_l1.jsonl

Loss cluster:

live_state/loss_cluster_state.json

Monitoring:

live_state/monitor_status.json

Control:

live_state/runtime_control.json

## Active Data Inputs

Market CSV:

data/l1_paper_short_gate_test.csv

Default 5m seeds:

seeds/5m/btcusdt_5m_long_timing_core_v1.csv

Important:

Current Live L1 operation is still CSV-driven.

It is not yet exchange-feed driven.

## Active Strategy / Signal Flow

Current runtime signal flow:

CSVMarketFeed
-> MarketSnapshot
-> build_feature_snapshot
-> detect_regime
-> compute_1m_intent_raw
-> compute_5m_timing_vote
-> fuse_intent_with_5m_timing
-> apply_paper_execution

Current active 5m timing module:

live_l1/core/timing_5m.py

Inactive experimental timing module:

live_l1/core/timing_5m_v2.py

Status:

KEEP_EXPERIMENTAL_PAIR

## Active State Flow

load_or_init_state
-> validate_loaded_state
-> loop tick processing
-> persist_state

Persisted state files:

live_state/s2_position.jsonl
live_state/s4_risk.jsonl

Schema:

schema_version=1

## Recovery Flow

execution_audit.jsonl
-> replay_execution_state.py
-> recover_runtime_state.py
-> startup recovery inside loop.py
-> reconciliation gate if enabled

Recovery status:

ACTIVE

## Reconciliation Flow

execution_audit.jsonl
s2_position.jsonl
trades_l1.jsonl
loss_cluster_state.json

-> reconcile_runtime_state.py

Result:

PASS/FAIL gate before safe launch.

## Monitoring Flow

monitor_runtime.py reads:

- startup validation
- reconciliation
- schema validation
- replay state
- S2 state
- S4 risk
- trades
- loss cluster state
- operational profile

Writes:

live_state/monitor_status.json

## Runtime Control Flow

runtime_control_loop.py runs:

monitor_runtime.py

Reads:

live_state/monitor_status.json

Writes:

live_state/runtime_control.json

Classifies:

- control_state
- control_action
- control_reason
- escalation_level
- escalation_reason

## Active Profile Flow

operational_profiles.py defines:

- DEVELOPMENT
- PAPER
- PRODUCTION
- RECOVERY

Default:

PAPER

PRODUCTION:

intentionally disabled

## Known Architecture Risks

### Risk 1: Direct Runner Bypass

scripts/run_live_l1_paper.py imports loop.py directly.

Risk:

Could bypass safe_launch.py if used manually.

Mitigation:

Document safe_launch.py as the only approved operational entry point.

### Risk 2: CSV-Driven Runtime

Current operation is still based on CSV market feed.

Risk:

Not yet real exchange-feed architecture.

Mitigation:

Acceptable for paper operation.
Requires separate review before production/live exchange operation.

### Risk 3: Experimental Future Modules

Some builder modules are retained but not active:

- gate_builder.py
- regime_builder.py
- regime_v2_builder.py
- signal_builder.py
- timing_5m_v2.py
- cost_guards.py

Risk:

Future confusion if not documented.

Mitigation:

Classify as KEEP_FUTURE or KEEP_EXPERIMENTAL_PAIR.

### Risk 4: Runtime Control Does Not Kill Process

runtime_control_loop.py writes STOP decisions but does not terminate an independent long-running runtime process.

Risk:

True process-level unattended shutdown not implemented.

Mitigation:

Acceptable for current controlled paper phase.
Requires future implementation before production-grade unattended operation.

## Architecture Decisions

### Decision 1

safe_launch.py is the only approved operational launch entry point.

### Decision 2

scripts/run_live_l1_paper.py remains available but is not approved for operational launch.

### Decision 3

execution_audit.jsonl remains the primary replay source of truth.

### Decision 4

PRODUCTION profile remains disabled.

### Decision 5

Future online builder modules are retained but not active.

## Current Architecture Classification

Core Runtime:

ACTIVE

Recovery:

ACTIVE

Reconciliation:

ACTIVE

Monitoring:

ACTIVE

Runtime Control:

ACTIVE

Operational Profiles:

ACTIVE

Backup:

ACTIVE

Online Builders:

KEEP_FUTURE

Timing v2:

KEEP_EXPERIMENTAL_PAIR

Direct runner:

REVIEW_REQUIRED / NOT PRIMARY

## P26 Result

Live L1 architecture dependency review completed.

Status:

PASS
