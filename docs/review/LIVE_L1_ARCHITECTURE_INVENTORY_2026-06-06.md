# LIVE L1 ARCHITECTURE INVENTORY

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL
Status: Architecture Inventory

## Current Overall Status

Live L1 infrastructure is in a highly advanced paper-operation state.

Current readiness:

approximately 9.7 / 10

Approved for:

- supervised paper operation
- controlled unattended paper operation
- recovery testing
- operational testing

Not approved for:

- real-capital production deployment

PRODUCTION remains intentionally disabled.

## Core Runtime Flow

Current intended Live L1 flow:

safe_launch.py
-> startup_validator.py
-> reconcile_runtime_state.py
-> run_l1_loop_step1234567
-> execution.py
-> state_store.py
-> monitoring/control tools

## Active Core Runtime Components

live_l1/core/loop.py

Main Live L1 loop.

Responsibilities:

- load runtime configuration
- apply startup recovery
- load and persist state
- process market snapshots
- compute intent
- apply execution
- write runtime state

Status:

ACTIVE

live_l1/core/execution.py

Paper execution engine.

Responsibilities:

- open/close paper positions
- apply TP/SL and time-stop logic
- write trade log
- write execution audit
- maintain loss-cluster gate state

Status:

ACTIVE

live_l1/state/state_store.py

State persistence layer.

Responsibilities:

- load latest S2 position state
- load latest S4 risk state
- persist s2_position.jsonl
- persist s4_risk.jsonl
- write schema_version=1

Status:

ACTIVE

live_l1/state/models.py

Minimal state model definitions.

Current states:

- PositionStateS2
- RiskStateS4

Status:

ACTIVE

## Active Safety Components

live_l1/tools/safe_launch.py

Safe launch wrapper.

Responsibilities:

- enforce startup validation
- enforce reconciliation
- enforce safety flags
- enforce operational profiles
- block PRODUCTION

Status:

ACTIVE

live_l1/tools/startup_validator.py

Startup validator.

Responsibilities:

- WSL check
- market CSV check
- seed CSV check
- startup recovery / reconciliation gate consistency

Status:

ACTIVE

live_l1/tools/reconcile_runtime_state.py

Runtime reconciliation.

Responsibilities:

- audit vs s2_position
- audit vs trades
- loss-cluster state
- JSON validity

Status:

ACTIVE

live_l1/tools/validate_runtime_schema.py

Schema validator.

Responsibilities:

- validate schema_version
- accept legacy_v0
- accept schema_v1
- reject malformed or unsupported versions

Status:

ACTIVE

## Recovery Components

live_l1/tools/replay_execution_state.py

Deterministic replay from execution_audit.jsonl.

Status:

ACTIVE

live_l1/tools/recover_runtime_state.py

Startup recovery helper.

Status:

ACTIVE

## Monitoring Components

live_l1/tools/monitor_runtime.py

Machine-readable monitoring snapshot generator.

Output:

live_state/monitor_status.json

Status:

ACTIVE

live_l1/tools/monitor_summary.py

Human-readable monitoring summary.

Status:

ACTIVE

## Runtime Control Components

live_l1/tools/runtime_control_loop.py

Unattended control-loop classifier.

Output:

live_state/runtime_control.json

Responsibilities:

- run monitoring
- classify control state
- classify control action
- classify escalation level

Status:

ACTIVE

## Operational Profile Components

live_l1/operational_profiles.py

Central profile configuration.

Profiles:

- DEVELOPMENT
- PAPER
- PRODUCTION
- RECOVERY

Default:

PAPER

PRODUCTION:

implemented but disabled

Status:

ACTIVE

## Backup Components

live_l1/tools/create_runtime_backup.py

Runtime backup creator.

Status:

ACTIVE

live_l1/tools/validate_runtime_backup.py

Runtime backup validator.

Status:

ACTIVE

## Active Test Components

live_l1/tools/test_monitor_failure_injection.py

Tests monitoring failure detection.

Status:

ACTIVE TEST TOOL

live_l1/tools/test_operational_profiles.py

Tests profile safety behavior.

Status:

ACTIVE TEST TOOL

live_l1/tools/test_unattended_operation.py

Tests unattended control decisions.

Status:

ACTIVE TEST TOOL

## Active Runtime Artifacts

These are runtime files and must not be committed:

live_logs/execution_audit.jsonl
live_logs/trades_l1.jsonl
live_logs/l1_paper.log
live_state/s2_position.jsonl
live_state/s4_risk.jsonl
live_state/loss_cluster_state.json
live_state/monitor_status.json
live_state/runtime_control.json
backups/

## Current Runtime State

Current known state:

position: FLAT
trade_count: 2
kill_level: SOFT
monitor_status: WARN
runtime_control_state: DEGRADED
runtime_control_action: CONTINUE

Assessment:

Expected and safe for controlled paper operation.

Reason for WARN:

kill_level=SOFT

## Documentation Structure

docs/runbooks/

Operational procedures.

docs/disaster_recovery/

Backup and restore documentation.

docs/schema/

Schema versioning documentation.

docs/monitoring/

P19 monitoring documentation.

docs/operations/

P20 operational profile documentation.

docs/unattended/

P21 unattended control documentation.

docs/review/

Readiness reviews and final infrastructure assessment.

## Architecture Strengths

1. Deterministic recovery exists.

2. Runtime state can be reconciled.

3. Startup is gated.

4. Runtime artifacts are separated from Git.

5. Backups are validated.

6. Schema versioning exists.

7. Monitoring exists.

8. Operational profiles exist.

9. Unattended control decisions exist.

10. PRODUCTION is intentionally blocked.

## Current Weak Points

1. No real external alert channel.

Examples:

- email
- SMS
- mobile notification

2. No remote dashboard.

3. No broker/exchange integration.

4. PRODUCTION activation workflow not implemented.

5. Runtime control loop classifies STOP but does not yet terminate an independent long-running process.

6. kill_level=SOFT currently keeps monitoring in WARN.

## Files That Should Remain Active

Do not archive:

live_l1/core/loop.py
live_l1/core/execution.py
live_l1/state/state_store.py
live_l1/state/models.py
live_l1/tools/safe_launch.py
live_l1/tools/startup_validator.py
live_l1/tools/reconcile_runtime_state.py
live_l1/tools/validate_runtime_schema.py
live_l1/tools/replay_execution_state.py
live_l1/tools/recover_runtime_state.py
live_l1/tools/monitor_runtime.py
live_l1/tools/monitor_summary.py
live_l1/tools/runtime_control_loop.py
live_l1/operational_profiles.py
live_l1/tools/create_runtime_backup.py
live_l1/tools/validate_runtime_backup.py
live_l1/tools/test_monitor_failure_injection.py
live_l1/tools/test_operational_profiles.py
live_l1/tools/test_unattended_operation.py

## Potential Archive Candidates

No immediate code archive is recommended without a dedicated file tree review.

Reason:

Current uploaded and discussed files are active infrastructure components.

Recommended next archive check:

Run a repository tree review and identify old duplicate scripts, obsolete research outputs and unused experiments.

## Minimal Active Live L1 Structure

Recommended target structure:

live_l1/
  core/
  state/
  tools/
  meta_state/
  logs/
  io/

docs/
  runbooks/
  disaster_recovery/
  schema/
  monitoring/
  operations/
  unattended/
  review/

live_logs/
  runtime only, untracked

live_state/
  runtime only, untracked

backups/
  runtime only, untracked

## Next Recommended Step

Before adding new functionality:

1. run current operational checks
2. confirm current WARN reason
3. decide whether kill_level=SOFT should remain active
4. create a clean architecture checkpoint
5. only then continue toward strategy/live-paper operation

## Final Assessment

The Live L1 architecture is currently coherent, modular and safety-oriented.

The system is no longer just a strategy script.

It now has a real operational shell:

- launch policy
- validation
- reconciliation
- recovery
- backup
- monitoring
- profiles
- unattended control

Final architecture inventory result:

PASS
