# P20E PROFILE NEGATIVE TESTS - COMPLETED

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Validate operational profile safety behavior through negative tests.

## Implemented File

live_l1/tools/test_operational_profiles.py

## Tests

invalid_profile_fallback

Expected:

Invalid profile falls back to PAPER.

Observed:

PASS

Result:

PASS

production_safe_launch_blocked

Expected:

PRODUCTION launch blocked.

Observed:

PROFILE_POLICY: PRODUCTION is not enabled yet

Result:

PASS

production_monitor_fails

Expected:

Monitoring reports FAIL for PRODUCTION.

Observed:

status: FAIL

Result:

PASS

paper_without_safety_flags_blocked

Expected:

PAPER launch blocked without required safety flags.

Observed:

FAILED_STEP: required_safety_flags

Result:

PASS

## Overall Result

All negative profile tests passed.

## P20E Result

Operational profile negative testing completed.

Status:

PASS
