# P34 STRICT TIMING DIRECTION IMPLEMENTED

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Implement strict direction handling for the 5m timing layer.

## Modified File

live_l1/core/timing_5m.py

## Change

Before:

missing direction -> long

After:

missing direction -> none

invalid direction -> none

Explicit long and explicit short remain valid.

## Validation

Test file:

tools/test_p34_strict_timing_direction.py

Test cases:

- missing_direction_defaults_none
- explicit_long
- explicit_short
- invalid_direction_defaults_none

Expected:

All PASS.

## Runtime Impact

Legacy seed files without direction no longer silently become long.

Explicit v2 seed files with direction=long still work.

Short seeds are now representable and testable.

## Result

Status: PASS
