# P33 STRICT TIMING DIRECTION HANDLING

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Remove implicit long fallback behavior from the 5m timing layer.

Introduce strict direction handling while preserving controlled legacy compatibility.

## Current Behavior

P30 identified:

_normalize_direction(None) -> long

As a result:

missing direction
=> long

This creates silent long bias.

## Design Decision

Direction must be explicit.

Allowed values:

- long
- short
- none

Any missing or invalid direction shall not silently become long.

## Legacy Compatibility

A temporary compatibility mode remains available.

Environment variable:

L1_TIMING_ALLOW_LEGACY_LONG_DEFAULT

Behavior:

enabled:

missing direction -> long

disabled:

missing direction -> none

## Recommended Default

Future default:

L1_TIMING_ALLOW_LEGACY_LONG_DEFAULT=0

Reason:

Explicit configuration is safer and easier to audit.

## Runtime Rules

Valid direction:

long

=> long

Valid direction:

short

=> short

Valid direction:

none

=> none

Missing direction:

=> none

Invalid direction:

=> none

## Seed Validation

Recommended future validation:

Reject seeds missing:

- seed_id
- direction
- comb_json

for strict v2 operation.

## Migration Path

P32:

explicit direction seed schema

PASS

P33:

strict handling design

PASS

P34:

implement strict handling

P35:

timing regression audit

P36:

optional short seed introduction

## Risk

Low.

Behavior only changes for malformed or legacy seeds.

Explicit v2 seeds remain unaffected.

## Decision

Implementation approved.

Proceed to:

P34 Strict Timing Direction Implementation

## Result

Status: PASS
