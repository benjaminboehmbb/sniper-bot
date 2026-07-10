# Document Metadata

Document Class: Architecture Technical Debt Register
Document ID: ARCH-TD-REGISTER
Version: V1.1
Status: Living Document
Date: 2026-07-09
Project: Trading-Bot Scientific Runtime
Subsystem: Run Engine
Storage Location: docs/architecture/technical_debt/
Filename: ARCHITECTURE_TECHNICAL_DEBT_REGISTER_V1_2026-07-09.md

Purpose: Track open technical debt items surfaced by Run Engine implementation certifications, so deferred findings remain owned and traceable to a named target unit rather than being silently dropped.

---

# Architecture Technical Debt Register

TD-001

Title:
Canonical Position Source for PnLEngine

Priority:
Medium

Target Phase:
P2 (P2-02A)

Status:
Deferred

Source:
P1-03.1 Final Certification – Finding 2

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
P1-03.1 Final Certification – Finding 4

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
P1-03.1 Final Certification – Finding 3

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
P1-03.1 Final Certification – Finding 5

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
P1-03.1 Final Certification – Finding 6

Description:
Create an automated regression test suite for run_engine/core.

------------------------------------------------------------

TD-006

Title:
RiskEngine Peak Equity and Drawdown Ownership Duplication

Priority:
Medium

Target Phase:
P2-03 / P2-04

Status:
Deferred

Source:
P2-01 Capability Gap Analysis and P2-01 Architecture

Description:
RiskEngine independently maintains peak equity and computes drawdown instead of consuming the CanonicalState-owned values, creating duplicate ownership contrary to ADR-006 and ADR-007. Resolve during P2-03/P2-04 as one coherent ownership change.

------------------------------------------------------------

TD-007

Title:
RunLoop Lifecycle Control Surface

Priority:
Medium

Target Phase:
Future Phase-2 Runtime Control Unit

Status:
Deferred

Source:
P2-02 Capability Gap Analysis and P2-02 Runtime Status Architecture

Description:
RunLoop currently has no explicit pause, stop, shutdown, or error lifecycle control surface. Therefore PAUSED, STOPPING, STOPPED, and ERROR are reserved Runtime Status vocabulary but are not yet reachable states. Implement their real transition triggers only in a dedicated future runtime-control unit. Do not fabricate transitions inside P2-02.
