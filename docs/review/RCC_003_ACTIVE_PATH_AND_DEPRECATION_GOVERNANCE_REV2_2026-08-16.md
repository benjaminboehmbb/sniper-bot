# RCC-003 Active-Path and Deprecation Governance Record (Revision 2)

## Metadata
- DOCUMENT_ID = RCC-003-ACTIVE-PATH-GOVERNANCE
- REVISION = 2
- STATUS = CORRECTED_CANDIDATE_PENDING_INDEPENDENT_REREVIEW
- RCC003_CLASSIFICATION_MATRIX_REVIEWED = YES (refers to prior RCC-003 matrix independent review only)
- RCC003_DEPRECATION_DISPOSITION_REGISTER_COMPLETE = YES
- RCC003_DEPRECATION_IMPLEMENTATION_PLAN_READY = NO
- RCC003_REMOVAL_AUTHORIZED = NO
- RCC003_CERTIFICATION_STATUS = NOT_YET_CERTIFIED

## 1. Canonical runtime ownership
- live_l1 = CANONICAL_OPERATIONAL
- live_l1/tools/safe_launch.py = CANONICAL_OPERATIONAL
- run_engine = REFERENCE_SEMANTICS
- deference clarification: run_engine assets remain REFERENCE_SEMANTICS and are not moved into operational startup authority.

## 2. Canonical runtime input contract and parity evidence
- canonical 5m seed: seeds/5m/btcusdt_5m_timing_core_v2.csv
- canonical 5m seed SHA-256: 6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5
- validation/runtime path parity evidence:
  - commit: d2c9c9f488a88133170f9bc474b8e93eeccd40c3
  - live_l1 regression test cited as parity evidence: `live_l1.tools.test_operational_profiles`
- explicit market override mechanisms:
  - L1_MARKET_CSV_PATH is the approved override key for runtime market CSV path.
  - Approved CLI path propagation is required from caller to launch layer to runtime configuration before any operational start.
  - This override applies only when explicitly provided and must never be conflated with default seed binding.

## 3. Path anchoring, precedence, and active-path matrix
- All matrix keys are repository-root-relative and prefixes match literally from repository root.
- `tools/` and `scripts/` are treated as top-level path roots.
- top-level `tools/` does NOT match `live_l1/tools/`.
- top-level `scripts/` does NOT match nested script-like paths elsewhere.
- Classification precedence for this matrix:
  1. exact file path
  2. longest matching directory prefix
  3. shorter directory prefix
  4. UNCLASSIFIED_PENDING_REVIEW (default)
- Disposition in Section 4 COMPOSES with this section’s active-path classifications and governs only retention/deprecation status; it does not redefine membership in Section 3.
- rcc002/ = CERTIFICATION_ONLY
- strategies/ = RESEARCH_ONLY
- archive/ = HISTORICAL_ARCHIVAL
- runtime_runs/ = RUNTIME_EVIDENCE_ONLY
- tests/ = TEST_ONLY
- docs/ = DOCUMENTATION_GOVERNANCE
- seeds/ = DATA_STORAGE_BOUNDARY
- data/ = DATA_STORAGE_BOUNDARY
- data/.gitkeep is structural.
- run_engine/ = REFERENCE_SEMANTICS
- live_l1/ = CANONICAL_OPERATIONAL
- scripts/
  - scripts/build_rcc002_spec_bundle.py = RESEARCH_EVIDENCE_GENERATION
  - scripts/run_live_l1_paper.py = RESEARCH_EVIDENCE_GENERATION
  - scripts/ (other) = MIXED_RESEARCH_AND_OPERATIONAL_SUPPORT
- tools/
  - tools/test_*.py = TEST_SUPPORT
  - tools/ (other) = MIXED_TOOLING_PENDING_SUBPATH_CLASSIFICATION
- all unlisted repository paths = UNCLASSIFIED_PENDING_REVIEW
- SAFE_TO_REMOVE_NOW = NO by default for all unlisted paths, unless a more specific disposition is recorded.

## 4. SAFE_TO_REMOVE_NOW rule
- SAFE_TO_REMOVE_NOW is the recorded instance of SAFE_TO_REMOVE and is governed by this section.
- SAFE_TO_REMOVE_NOW = YES requires positive evidence proving all of:
  1. no runtime dependency
  2. no tooling caller
  3. no test dependency
  4. no certification/evidence dependency
  5. no governance/provenance requirement
  6. no package-structure requirement
  7. no dynamic import, reflective lookup, plugin/entrypoint registration, configuration-string reference, or equivalent indirect dependency
- evidence standard to retain for this record:
  - repository import/caller search
  - path/file-load search
  - test dependency search
  - governance/certification reference search
  - dynamic/config/entrypoint search
  - relevant git/history checks where needed
- adjudicating authority: RCC-003 certification review
- evidence-retention rule: all evidence required by this section is retained in this RCC-003 review/certification record.

## 5. Deprecation disposition definitions
- KEEP_DEPRECATED = retain in current location; noncanonical/deferred; no new dependency should be introduced; removal requires later SAFE_TO_REMOVE_NOW gate.
- ISOLATE_LATER = retain now; candidate for movement into a clearly fenced historical/deferred namespace only after dependency review and explicit RCC-003 authorization.
- deprecation inside REFERENCE_SEMANTICS means: retained for compatibility/provenance/reference purposes but not part of the preferred future reference-semantic surface.
- deferred module = retained artifact kept for compatibility/provenance and historical traceability while not included in preferred active interface for future evolution.
- run_engine/runtime/state_memory.py
  - disposition = ISOLATE_LATER
  - SAFE_TO_REMOVE_NOW = NO
  - OWNER = RCC-003 repository-maintenance process
  - TRIGGER = before any move/removal or before final RCC-003 certification, whichever occurs first
  - REVIEW_DEADLINE = before final RCC-003 certification decision

## 6. Section 4 dispositions
run_engine/core/config.py
- KEEP_DEPRECATED
- SAFE_TO_REMOVE_NOW: NO

run_engine/runtime/recovery.py
- KEEP_DEPRECATED
- SAFE_TO_REMOVE_NOW: NO

run_engine/runtime/snapshot.py
- KEEP_DEPRECATED
- SAFE_TO_REMOVE_NOW: NO

run_engine/runtime/state_memory.py
- ISOLATE_LATER
- SAFE_TO_REMOVE_NOW: NO
- OWNER = RCC-003 repository-maintenance process
- TRIGGER = before any move/removal or before final RCC-003 certification, whichever occurs first
- REVIEW_DEADLINE = before final RCC-003 certification decision

scripts/run_live_l1_paper.py
- KEEP_DEPRECATED
- NONCANONICAL_DEPRECATED_TOOL
- SAFE_TO_REMOVE_NOW: NO

## 7. Noncanonical launcher note
scripts/run_live_l1_paper.py is a legacy path and may be described operationally in prose, but is not the approved operational startup path.
Approved operational startup remains: `live_l1/tools/safe_launch.py`.
No deprecation implementation is authorized by this revision.

## 8. Structural file rule
- data/.gitkeep is structural and not a removal candidate merely because it is empty.
- zero-byte __init__.py files are not removal candidates merely because they are empty.
- zero-byte/deferred modules require dependency/governance review before removal.

## 9. Removal policy and default constraints
- NO file may be classified SAFE_TO_REMOVE unless evidence proves all required criteria in Section 4.
- no file is marked SAFE_TO_REMOVE_NOW = YES in this revision.
- RCC003_DEPRECATION_DISPOSITION_REGISTER_COMPLETE = YES
- RCC003_DEPRECATION_IMPLEMENTATION_PLAN_READY = NO
- RCC003_REMOVAL_AUTHORIZED = NO

## 10. Next formal action
NEXT_ACTION=INDEPENDENT_REREVIEW_OF_EXACT_REV2_BYTES
