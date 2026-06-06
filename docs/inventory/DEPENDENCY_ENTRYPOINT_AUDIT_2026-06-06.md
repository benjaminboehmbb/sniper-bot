# DEPENDENCY AND ENTRY-POINT AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Target Dependency Usage

### live_l1.core.timing_5m

path: live_l1/core/timing_5m.py

imported_by_count: 1

- live_l1/core/loop.py

### live_l1.core.timing_5m_v2

path: live_l1/core/timing_5m_v2.py

imported_by_count: 1

- tools/test_timing_5m_v2_minimal.py

### live_l1.io.valid

path: live_l1/io/valid.py

imported_by_count: 1

- live_l1/core/loop.py

### live_l1.io.validate

path: 

imported_by_count: 0

- none

### live_l1.core.loop

path: live_l1/core/loop.py

imported_by_count: 2

- live_l1/tools/safe_launch.py
- scripts/run_live_l1_paper.py

### live_l1.tools.safe_launch

path: live_l1/tools/safe_launch.py

imported_by_count: 0

- none

### live_l1.tools.monitor_runtime

path: live_l1/tools/monitor_runtime.py

imported_by_count: 0

- none

### live_l1.tools.runtime_control_loop

path: live_l1/tools/runtime_control_loop.py

imported_by_count: 0

- none

### scripts.run_live_l1_paper

path: scripts/run_live_l1_paper.py

imported_by_count: 0

- none

## Live Entry-Point Candidates

- live_l1/tools/create_runtime_backup.py | main_guard=True | argparse=True
- live_l1/tools/monitor_runtime.py | main_guard=True | argparse=True
- live_l1/tools/monitor_summary.py | main_guard=True | argparse=True
- live_l1/tools/operational_health_report.py | main_guard=True | argparse=True
- live_l1/tools/reconcile_runtime_state.py | main_guard=True | argparse=True
- live_l1/tools/recover_runtime_state.py | main_guard=True | argparse=True
- live_l1/tools/replay_execution_state.py | main_guard=True | argparse=True
- live_l1/tools/runtime_control_loop.py | main_guard=True | argparse=False
- live_l1/tools/safe_launch.py | main_guard=True | argparse=True
- live_l1/tools/startup_validator.py | main_guard=True | argparse=True
- live_l1/tools/test_monitor_failure_injection.py | main_guard=True | argparse=False
- live_l1/tools/test_operational_profiles.py | main_guard=True | argparse=False
- live_l1/tools/test_unattended_operation.py | main_guard=True | argparse=False
- live_l1/tools/validate_runtime_backup.py | main_guard=True | argparse=True
- live_l1/tools/validate_runtime_schema.py | main_guard=True | argparse=True
- scripts/run_live_l1_paper.py | main_guard=True | argparse=True

## Suspicious Zero-Import Live L1 Files

- live_l1/core/gate_builder.py
- live_l1/core/regime_builder.py
- live_l1/core/regime_v2_builder.py
- live_l1/core/signal_builder.py
- live_l1/guards/cost_guards.py
- live_l1/tools/create_runtime_backup.py
- live_l1/tools/monitor_runtime.py
- live_l1/tools/monitor_summary.py
- live_l1/tools/operational_health_report.py
- live_l1/tools/runtime_control_loop.py
- live_l1/tools/safe_launch.py
- live_l1/tools/test_monitor_failure_injection.py
- live_l1/tools/test_operational_profiles.py
- live_l1/tools/test_unattended_operation.py
- live_l1/tools/validate_runtime_backup.py
- live_l1/tools/validate_runtime_schema.py

## Notes

Zero-import files may still be valid CLI entry-points.
Archive decisions require manual review.
