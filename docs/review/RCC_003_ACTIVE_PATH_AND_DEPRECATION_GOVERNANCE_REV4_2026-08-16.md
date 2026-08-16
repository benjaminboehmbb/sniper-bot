# RCC-003 Active-Path and Deprecation Governance Record (Revision 4)

## Metadata
- DOCUMENT_ID = RCC-003-ACTIVE-PATH-GOVERNANCE
- REVISION = 4
- STATUS = CORRECTED_CANDIDATE_PENDING_INDEPENDENT_REREVIEW
- RCC003_PRIOR_CLASSIFICATION_MATRIX_INDEPENDENTLY_REVIEWED = YES
- RCC003_REV4_INDEPENDENT_REREVIEW_STATUS = PENDING
- RCC003_DEPRECATION_DISPOSITION_REGISTER_COMPLETE_FOR_ENUMERATED_CANDIDATES = YES
- RCC003_DEPRECATION_IMPLEMENTATION_PLAN_READY = NO
- RCC003_REMOVAL_AUTHORIZED = NO
- RCC003_CERTIFICATION_STATUS = NOT_YET_CERTIFIED

## 1. Canonical runtime ownership
- live_l1 = CANONICAL_OPERATIONAL
- live_l1/tools/safe_launch.py = CANONICAL_OPERATIONAL
- run_engine = REFERENCE_SEMANTICS
- Section 3 is the authoritative locus for active-path classification.
- Section 1 is explanatory summary only and cannot override Section 3 classifications.
- Deference clarification: run_engine assets remain REFERENCE_SEMANTICS and are not moved into operational startup authority.

## 2. Canonical runtime input contract and parity evidence
- Operational execution requires an explicitly resolved market-data path.
- Market-data path resolution may originate from:
  - L1_MARKET_CSV_PATH
  - Approved safe-launch CLI market-path argument
- There is no approved implicit repository market-data default for operational execution.
- The regression "default case" refers only to canonical seed-default resolution, not to an operational market-data default.
- Canonical seed path: seeds/5m/btcusdt_5m_timing_core_v2.csv
- Canonical seed SHA-256: 6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5
- Market-path resolution and seed-default resolution are independent.
- canonical 5m seed SHA-256 check commit: SEED_HASH_VERIFICATION_COMMIT = d2c9c9f488a88133170f9bc474b8e93eeccd40c3
- canonical evidence and parity check:
  - commit: d2c9c9f488a88133170f9bc474b8e93eeccd40c3
  - parity evidence test: tests/live_l1/test_safe_launch_iu4_shadow_runtime_gate.py
  - verification command: python3 -m unittest discover -s tests/live_l1 -p 'test_*.py'
  - result: 318 tests run / PASS / OK
  - additional evidence: python3 -m compileall on the modified safe_launch/loop/test modules = PASS
  - git diff --check = PASS
- demonstrated proposition:
  safe_launch validation receives the same effective market CSV and seed paths that are propagated to and consumed by run_l1_loop_step1234567 for the covered default/override cases.

## 3. Path anchoring, precedence, and active-path matrix
- Classification rules are in this section.
- Classification keys are repository-root-relative and match literally from repository root.
- `tools/` and `scripts/` are treated as top-level path roots.
- precedence for this matrix is exactly:
  1. exact file path
  2. filename-pattern key within an explicitly anchored repository-root-relative directory
  3. longest matching directory prefix
  4. shorter directory prefix
  5. default UNCLASSIFIED_PENDING_REVIEW
- `tools/` and `scripts/` pattern semantics:
  - `tools/test_*.py` means only files matching that pattern directly under repository-root-relative `tools/`.
  - it does NOT match `live_l1/tools/test_*.py` or any other nested `tools` directory.
  - `top-level tools/` does NOT match `live_l1/tools/`.
  - `top-level scripts/` does NOT match nested script-like paths elsewhere.
- `NONCANONICAL_DEPRECATED_TOOL` is an ACTIVE-PATH CLASSIFICATION with the following meaning:
  - executable tooling remains present
  - not an approved canonical launcher
  - no new runtime/operational dependency may be introduced
  - retained only for governed legacy/test/support use
  - it does not imply removability
- Disposition in Section 6 composes with this section's active-path classifications and does not replace membership in Section 3.
- `live_l1/tools/test_*.py` inherits `live_l1/ = CANONICAL_OPERATIONAL` as structural active-path membership, while retaining a functional-role annotation of `TEST_SUPPORT`.
- Functional-role annotation does not override active-path ownership.
- rcc002/ = CERTIFICATION_ONLY
- strategies/ = RESEARCH_ONLY
- archive/ = HISTORICAL_ARCHIVAL
- runtime_runs/ = RUNTIME_EVIDENCE_ONLY
- tests/ = TEST_ONLY
- docs/ = DOCUMENTATION_GOVERNANCE
- seeds/ = DATA_STORAGE_BOUNDARY
- data/ = DATA_STORAGE_BOUNDARY
- data/.gitkeep = DATA_STORAGE_BOUNDARY with STRUCTURAL annotation and NON_REMOVAL_CANDIDATE annotation
- run_engine/ = REFERENCE_SEMANTICS
- live_l1/ = CANONICAL_OPERATIONAL
- scripts/
  - scripts/build_rcc002_spec_bundle.py = RESEARCH_EVIDENCE_GENERATION
  - scripts/run_live_l1_paper.py = NONCANONICAL_DEPRECATED_TOOL
  - scripts/ (other) = MIXED_RESEARCH_AND_OPERATIONAL_SUPPORT
- tools/
  - tools/test_*.py = TEST_SUPPORT
  - tools/ (other) = MIXED_TOOLING_PENDING_SUBPATH_CLASSIFICATION
- all unlisted repository paths = UNCLASSIFIED_PENDING_REVIEW

## 4. SAFE_TO_REMOVE framing and evidence-binding
- SAFE_TO_REMOVE = abstract removal-eligibility property.
- SAFE_TO_REMOVE_NOW = the recorded current adjudication of SAFE_TO_REMOVE at a specific evidence-search commit.
- SAFE_TO_REMOVE_NOW is governed by this section.
- SAFE_TO_REMOVE_NOW = YES requires positive evidence proving all of:
  1. no runtime dependency
  2. no tooling caller
  3. no test dependency
  4. no certification/evidence dependency
  5. no governance/provenance requirement
  6. no package-structure requirement
  7. no dynamic import, reflective lookup, plugin/entrypoint registration, configuration-string reference, or equivalent indirect dependency
- SAFE_TO_REMOVE_NOW = NO by default applies to:
  - UNCLASSIFIED_PENDING_REVIEW
  - MIXED_TOOLING_PENDING_SUBPATH_CLASSIFICATION
  - MIXED_RESEARCH_AND_OPERATIONAL_SUPPORT
  - pending/mixed/unclassified categories without explicit adjudicated removal disposition
- For every classification without explicit removal disposition,
  SAFE_TO_REMOVE_NOW = NO BY DEFAULT unless Section 4 positive evidence requirements are satisfied and formally adjudicated.
- For each of the following classifications, the default rule applies unless explicitly overridden by later RCC-003 adjudication:
  - CANONICAL_OPERATIONAL
  - REFERENCE_SEMANTICS
  - CERTIFICATION_ONLY
  - RESEARCH_ONLY
  - RUNTIME_EVIDENCE_ONLY
  - HISTORICAL_ARCHIVAL
  - TEST_ONLY
  - TEST_SUPPORT
  - DOCUMENTATION_GOVERNANCE
  - DATA_STORAGE_BOUNDARY
  - RESEARCH_EVIDENCE_GENERATION
  - pending/mixed/unclassified categories
- Evidence standard to retain for this record:
  - repository import/caller search
  - path/file-load search
  - test dependency search
  - governance/certification reference search
  - dynamic/config/entrypoint search
  - repository dependency checks
  - git/history checks where needed
  - every adjudication must record the exact Git commit at which dependency/evidence searches were executed
  - if repository HEAD advances before removal authorization, the relevant checks must be re-run or explicitly proven unaffected
- adjudicating authority: RCC-003 certification review
- evidence-retention rule:
  - supporting evidence corpus consists of the RCC-003 read-only audit/review chain that produced this governance record
  - detailed evidence remains in the RCC-003 review record; REV4 records only adjudicated outcome and binding commit.
  - evidence is not embedded in REV4
  - evidence-search currency and HEAD-advance checks are evaluated relative to GOVERNANCE_BASE_COMMIT
  - GOVERNANCE_BASE_COMMIT = d2c9c9f488a88133170f9bc474b8e93eeccd40c3

## 5. Deprecation disposition definitions
- KEEP_DEPRECATED = retain in current location; noncanonical/deferred; no new runtime, tooling, test, certification, or governance dependency MAY be introduced; removal requires later SAFE_TO_REMOVE_NOW gate.
- ISOLATE_LATER = retain now; candidate for movement into a clearly fenced historical/deferred namespace only after dependency review and explicit RCC-003 authorization.
- deprecation inside REFERENCE_SEMANTICS means: retained for compatibility/provenance/reference purposes but not part of the preferred future reference-semantic surface.
- deferred module = retained artifact kept for compatibility/provenance and historical traceability while not included in preferred active interface for future evolution.

## 6. Disposition Register
Disposition records in Section 6 compose with Section 3 active-path classifications. A disposition does not replace active-path classification.

run_engine/core/config.py
- REMOVAL_DISPOSITION = KEEP_DEPRECATED
- EVIDENCE_SEARCH_COMMIT = d2c9c9f488a88133170f9bc474b8e93eeccd40c3
- SAFE_TO_REMOVE_NOW = NO

run_engine/runtime/recovery.py
- REMOVAL_DISPOSITION = KEEP_DEPRECATED
- EVIDENCE_SEARCH_COMMIT = d2c9c9f488a88133170f9bc474b8e93eeccd40c3
- SAFE_TO_REMOVE_NOW = NO

run_engine/runtime/snapshot.py
- REMOVAL_DISPOSITION = KEEP_DEPRECATED
- EVIDENCE_SEARCH_COMMIT = d2c9c9f488a88133170f9bc474b8e93eeccd40c3
- SAFE_TO_REMOVE_NOW = NO

run_engine/runtime/state_memory.py
- REMOVAL_DISPOSITION = ISOLATE_LATER
- OWNER = RCC-003 repository-maintenance authority
- TRIGGER = before any move/removal or before final RCC-003 certification, whichever occurs first
- REVIEW_DEADLINE = before final RCC-003 certification decision
- EVIDENCE_SEARCH_COMMIT = d2c9c9f488a88133170f9bc474b8e93eeccd40c3
- SAFE_TO_REMOVE_NOW = NO

scripts/run_live_l1_paper.py
- ACTIVE_PATH_CLASSIFICATION = NONCANONICAL_DEPRECATED_TOOL
- RETENTION_DISPOSITION = KEEP_DEPRECATED
- EVIDENCE_SEARCH_COMMIT = d2c9c9f488a88133170f9bc474b8e93eeccd40c3
- SAFE_TO_REMOVE_NOW = NO

## 7. Noncanonical launcher note
scripts/run_live_l1_paper.py is legacy launch tooling and may be described operationally in prose, but is not the approved operational startup path.
- Approved operational startup remains: `live_l1/tools/safe_launch.py`.
- It is retained in NONCANONICAL_DEPRECATED_TOOL class.
- No deprecation implementation is authorized by this revision.

## 8. Structural file rule
- data/.gitkeep is structural and not a removal candidate merely because it is empty.
- STRUCTURAL is an annotation and does not replace FILE classification in Section 3.
- zero-byte __init__.py files are not removal candidates merely because they are empty.
- zero-byte/deferred modules require dependency/governance review before removal.

## 9. Removal policy and default constraints
- NO file may be classified SAFE_TO_REMOVE_NOW unless evidence proves all required criteria in Section 4.
- no file is marked SAFE_TO_REMOVE_NOW = YES in this revision.
- RCC003_DEPRECATION_DISPOSITION_REGISTER_COMPLETE_FOR_ENUMERATED_CANDIDATES = YES
- This completeness claim applies only to the five explicitly enumerated deprecation candidates identified at commit:
  d2c9c9f488a88133170f9bc474b8e93eeccd40c3.
  It does not claim dispositions exist for all mixed, pending, or unclassified repository paths.
- RCC003_DEPRECATION_IMPLEMENTATION_PLAN_READY = NO
- RCC003_REMOVAL_AUTHORIZED = NO

## 10. Independent rereview input requirement
The next independent rereview MUST receive:
1. exact REV4 bytes
2. previous REV2 independent review findings register containing C1-C8 / M1-M6 / m1-m6
3. REV3 independent rereview findings
4. expected REV4 SHA-256 (computed hash for the exact REV4 bytes)

The rereview must explicitly adjudicate closure of all carried findings.

## 11. Next formal action
NEXT_ACTION=INDEPENDENT_REREVIEW_OF_EXACT_REV4_BYTES_WITH_FULL_FINDINGS_REGISTER
