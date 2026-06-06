# P20A OPERATIONAL PROFILES MODEL

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL
Status: Draft

## Objective

Define explicit operational modes for Live L1.

The goal is to replace scattered operational behavior with a small number of clearly defined runtime profiles.

No runtime behavior changes are introduced in P20A.

## Operational Profiles

### DEVELOPMENT

Purpose:

Developer testing and implementation work.

Characteristics:

- local execution
- diagnostic output allowed
- failure investigation
- rapid iteration

### PAPER

Purpose:

Controlled paper operation.

Characteristics:

- startup validation required
- reconciliation required
- monitoring required
- schema validation required

### PRODUCTION

Purpose:

Future real-capital operation.

Current Status:

NOT YET ENABLED

### RECOVERY

Purpose:

Controlled recovery and incident handling.

Characteristics:

- recovery first
- reconciliation first

## Profile Selection

Environment variable:

L1_OPERATIONAL_PROFILE

Allowed values:

- DEVELOPMENT
- PAPER
- PRODUCTION
- RECOVERY

Default:

PAPER

## Result

Operational profile model defined.

Status:

PASS
