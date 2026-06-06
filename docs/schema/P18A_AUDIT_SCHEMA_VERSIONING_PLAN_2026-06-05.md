# P18A AUDIT SCHEMA VERSIONING PLAN

Date: 2026-06-05
Device: G15 / AR15
Environment: WSL

## Objective

Introduce explicit schema versioning for Live L1 audit, trade and state artifacts.

## Reason

Recovery, replay, reconciliation, health reports, backup and restore now depend on stable file schemas.

Unversioned schemas are a long-term risk.

## Target Artifacts

Primary:

- live_logs/execution_audit.jsonl
- live_logs/trades_l1.jsonl
- live_state/s2_position.jsonl
- live_state/loss_cluster_state.json
- live_state/s4_risk.jsonl

## Planned Schema Version

Initial schema version:

1

## Required Future Behavior

Every new runtime record should include:

schema_version: 1

## Compatibility Rule

Readers must accept:

- missing schema_version as legacy version 0
- schema_version 1 as current supported schema

Readers must reject or warn on:

- unsupported future schema_version
- malformed schema_version

## P18 Sequence

P18A Schema plan
P18B Schema validator tool
P18C Add schema_version to new audit/trade/state writes
P18D Backward compatibility tests
P18E Negative tests
P18F Documentation + Commit

## Status

P18A planned.

