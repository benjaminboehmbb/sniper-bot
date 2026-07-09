Create a new document:

docs/architecture/technical_debt/ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Document the following open technical debt items from the final P1-03.1 Claude certification.

TD-001
Title:
Canonical Position Source for PnLEngine

Priority:
Medium

Target Phase:
P2

Status:
Deferred

Source:
Claude Final Certification – Finding 2

Description:
PnLEngine currently receives entry_basis from position_pre rather than CanonicalState. This is a known Phase-2 ownership consolidation item.

------------------------------------------------------------

TD-002

Title:
Unify _safe_float Implementations

Priority:
Low

Target Phase:
P2

Status:
Deferred

Source:
Claude Final Certification – Finding 4

Description:
TradeLifecycleEngine and PositionEngine currently use different _safe_float implementations. Consolidate into a single consistent implementation during Phase 2.

------------------------------------------------------------

TD-003

Title:
Document Pre-Trade Snapshot Dependency

Priority:
Low

Target Phase:
P1 Follow-up

Status:
Open

Source:
Claude Final Certification – Finding 3

Description:
Document why PnLEngine intentionally consumes position_pre instead of the post-trade Position snapshot.

------------------------------------------------------------

TD-004

Title:
Lifecycle-based Performance Evaluation

Priority:
Medium

Target Phase:
P3

Status:
Already Planned

Source:
Claude Final Certification – Finding 5

Description:
PerformanceEngine shall later consume lifecycle/financial outcomes instead of decision ticks.

------------------------------------------------------------

TD-005

Title:
Automated Regression Test Suite

Priority:
Medium

Target Phase:
Project-wide

Status:
Open

Source:
Claude Final Certification – Finding 6

Description:
Create an automated regression test suite for run_engine/core.

Do not modify any other files.
Do not commit.
Do not push.