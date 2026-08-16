# RCC-003 Active-Path and Deprecation Governance Record

## 1. Canonical runtime ownership
- live_l1 = CANONICAL_OPERATIONAL
- live_l1/tools/safe_launch.py = canonical operational launcher
- run_engine = REFERENCE_SEMANTICS

## 2. Canonical runtime input contract
- canonical 5m seed: seeds/5m/btcusdt_5m_timing_core_v2.csv
- operational market input requires explicit override
- validation/runtime path parity fixed by commit: d2c9c9f488a88133170f9bc474b8e93eeccd40c3

## 3. Repository classifications
- rcc002/ = CERTIFICATION_ONLY
- strategies/ = RESEARCH_ONLY
- archive/ = HISTORICAL_ARCHIVAL
- runtime_runs/ = RUNTIME_EVIDENCE_ONLY
- tests/ = TEST_ONLY
- docs/ = DOCUMENTATION_GOVERNANCE
- seeds/ = ACTIVE_RUNTIME_DEPENDENCY
- run_engine/ = REFERENCE_SEMANTICS
- live_l1/ = CANONICAL_OPERATIONAL
- scripts/
  - scripts/build_rcc002_spec_bundle.py = RESEARCH_EVIDENCE_GENERATION
  - scripts/run_live_l1_paper.py = NONCANONICAL_DEPRECATED_TOOL
  - scripts/ (other) = MIXED_RESEARCH_AND_OPERATIONAL_SUPPORT
- tools/
  - tools/test_*.py = TEST_SUPPORT
  - tools/ (other) = ANALYSIS_AND_RESEARCH_TOOLING

## 4. Deprecation dispositions
run_engine/core/config.py
= KEEP_DEPRECATED
= SAFE_TO_REMOVE_NOW: NO

run_engine/runtime/recovery.py
= KEEP_DEPRECATED
= SAFE_TO_REMOVE_NOW: NO

run_engine/runtime/snapshot.py
= KEEP_DEPRECATED
= SAFE_TO_REMOVE_NOW: NO

run_engine/runtime/state_memory.py
= ISOLATE_LATER
= SAFE_TO_REMOVE_NOW: NO

scripts/run_live_l1_paper.py
= KEEP_DEPRECATED / NONCANONICAL OPERATIONAL TOOL
= SAFE_TO_REMOVE_NOW: NO

## 5. Noncanonical launcher warning
scripts/run_live_l1_paper.py must not be treated as the approved operational startup path.
Approved operational startup remains: live_l1/tools/safe_launch.py.

No removal is authorized.

## 6. Structural-file rule
- data/.gitkeep is structural and not a removal candidate merely because it is empty.
- zero-byte __init__.py files are not removal candidates merely because they are empty.
- zero-byte/deferred modules require dependency/governance review before removal.

## 7. Removal policy
No file may be classified SAFE_TO_REMOVE unless evidence proves all of:
- no runtime dependency;
- no tooling caller;
- no test dependency;
- no certification/evidence dependency;
- no governance/provenance requirement;
- no package-structure requirement.

## 8. RCC-003 current status
RCC003_CLASSIFICATION_MATRIX_AUTHORITATIVE = YES
RCC003_DEPRECATION_PLAN_READY = YES
RCC003_REMOVAL_AUTHORIZED = NO
RCC003_CERTIFICATION_STATUS = NOT_YET_CERTIFIED

## 9. Next formal action
Perform independent review of the exact governance document bytes before any deprecation implementation or RCC-003 certification decision.
