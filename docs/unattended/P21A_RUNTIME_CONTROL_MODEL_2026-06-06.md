# P21A RUNTIME CONTROL MODEL

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL
Status: Draft

## Objective

Define unattended runtime control architecture for Live L1.

P21A introduces no runtime behavior changes.

## Goal

Allow controlled long-running operation while preserving safety.

The runtime must remain stoppable, observable and recoverable.

## Runtime Control Layers

Layer 1

Operational Profile

Source:

L1_OPERATIONAL_PROFILE

Responsibilities:

- mode selection
- launch policy
- monitoring policy

Layer 2

Monitoring

Source:

monitor_runtime.py

Responsibilities:

- health evaluation
- alert generation
- runtime visibility

Layer 3

Runtime Controls

Responsibilities:

- stop decisions
- pause decisions
- escalation decisions

Layer 4

Operator

Responsibilities:

- final authority
- incident handling
- recovery approval

## Runtime States

Allowed states:

STARTING

RUNNING

PAUSED

DEGRADED

STOPPING

STOPPED

RECOVERY_REQUIRED

## Runtime Actions

Allowed actions:

CONTINUE

PAUSE

RESUME

STOP

ESCALATE

## Control File

Planned file:

live_state/runtime_control.json

Purpose:

Machine-readable unattended control state.

## Initial Runtime Control Schema

schema_version

control_state

control_action

control_reason

generated_utc

profile

alerts

## Control State Meanings

RUNNING

Normal operation.

PAUSED

Runtime temporarily paused.

DEGRADED

Runtime allowed but requires attention.

STOPPING

Shutdown in progress.

STOPPED

Runtime stopped.

RECOVERY_REQUIRED

Recovery required before next launch.

## Escalation Levels

INFO

WARN

FAIL

CRITICAL

## Initial Escalation Rules

WARN

- kill_level_active
- loss_cluster_active

FAIL

- reconciliation_failed
- schema_validation_failed
- startup_validation_failed

CRITICAL

- runtime_state_corruption
- repeated_recovery_failure
- unsupported_schema_version

## Future Components

P21B

Automated Monitoring Loop

P21C

Automatic Stop Conditions

P21D

Escalation Rules

P21E

Unattended Operation Tests

P21F

Acceptance Review

## Acceptance Criteria

- runtime states defined
- runtime actions defined
- escalation model defined
- control file defined
- no runtime behavior changes

## Result

Runtime control model defined.

Status:

PASS
