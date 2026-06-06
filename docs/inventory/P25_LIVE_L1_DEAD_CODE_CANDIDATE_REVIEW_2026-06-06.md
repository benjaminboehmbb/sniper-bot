# P25 LIVE L1 DEAD CODE CANDIDATE REVIEW

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Review Live L1 files flagged by P23/P24 as possible dead-code or legacy candidates.

No files are moved, deleted or archived in P25.

## Source Audits

- REPOSITORY_USAGE_AUDIT_2026-06-06
- DEPENDENCY_ENTRYPOINT_AUDIT_2026-06-06

## Review Principle

Do not archive based only on imported_by=0.

A file may still be valid if it is:

- a CLI entry-point
- a future-ready module
- documentation-backed
- used by shell commands
- used manually during diagnostics

## Candidate List

### live_l1/io/validate.py

Reason:

- imported_by=0
- similar name to live_l1/io/valid.py
- valid.py is actively imported by live_l1/core/loop.py

Initial Classification:

STRONG DEAD-CODE CANDIDATE

Required Follow-Up:

- inspect file content
- compare with valid.py
- check docs and shell references

Do not archive yet.

### live_l1/core/gate_builder.py

Reason:

- imported_by=0

Initial Classification:

POSSIBLE FUTURE/LEGACY BUILDER

Required Follow-Up:

- inspect file content
- check whether it was part of L1 gate-building experiments
- check references in docs/research

Do not archive yet.

### live_l1/core/regime_builder.py

Reason:

- imported_by=0

Initial Classification:

POSSIBLE FUTURE/LEGACY BUILDER

Required Follow-Up:

- inspect file content
- compare with active regime_detector.py
- check if used to reconstruct regime columns

Do not archive yet.

### live_l1/core/regime_v2_builder.py

Reason:

- imported_by=0

Initial Classification:

POSSIBLE FUTURE/LEGACY BUILDER

Required Follow-Up:

- inspect file content
- check relationship to regime_v2 logic
- check if used only by old tests/tools

Do not archive yet.

### live_l1/core/signal_builder.py

Reason:

- imported_by=0

Initial Classification:

POSSIBLE FUTURE/LEGACY BUILDER

Required Follow-Up:

- inspect file content
- check relationship to feature_snapshot.py
- check whether online signal construction still needs it

Do not archive yet.

### live_l1/guards/cost_guards.py

Reason:

- imported_by=0

Initial Classification:

POSSIBLE FUTURE SAFETY MODULE

Required Follow-Up:

- inspect file content
- check if cost/fee guard is planned but inactive
- check if needed before production readiness

Do not archive yet.

### live_l1/core/timing_5m_v2.py

Reason:

- not imported by live loop
- imported only by tools/test_timing_5m_v2_minimal.py

Initial Classification:

EXPERIMENTAL TIMING MODULE

Required Follow-Up:

- inspect relationship to timing_5m.py
- decide whether V2 remains planned future work or should be archived

Do not archive yet.

### tools/test_timing_5m_v2_minimal.py

Reason:

- standalone test for timing_5m_v2.py

Initial Classification:

TEST FOR EXPERIMENTAL MODULE

Required Follow-Up:

- keep if timing_5m_v2.py is retained
- archive together if timing_5m_v2.py is archived

Do not archive yet.

## Files Explicitly Not Dead Code

The following may show imported_by=0 but are valid CLI tools:

- live_l1/tools/safe_launch.py
- live_l1/tools/monitor_runtime.py
- live_l1/tools/monitor_summary.py
- live_l1/tools/runtime_control_loop.py
- live_l1/tools/create_runtime_backup.py
- live_l1/tools/validate_runtime_backup.py
- live_l1/tools/validate_runtime_schema.py
- live_l1/tools/operational_health_report.py
- live_l1/tools/test_monitor_failure_injection.py
- live_l1/tools/test_operational_profiles.py
- live_l1/tools/test_unattended_operation.py

Classification:

ACTIVE CLI ENTRYPOINTS

Do not archive.

## Initial Recommendation

Do not archive anything yet.

Next required step:

P25B Candidate Content Inspection

Inspect the candidate files directly and decide:

- KEEP ACTIVE
- KEEP FUTURE
- ARCHIVE CANDIDATE
- DELETE NEVER
- UNKNOWN

## P25 Result

Dead-code candidates identified.

No destructive action taken.

Status:

PASS
