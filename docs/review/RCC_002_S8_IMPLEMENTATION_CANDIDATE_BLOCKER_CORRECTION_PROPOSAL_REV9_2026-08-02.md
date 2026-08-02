# RCC-002 S8 Implementation Candidate Blocker Correction Proposal - Revision 9

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001-REV9` |
| Proposal date | `2026-08-02` |
| Proposal class | Final consolidated correction architecture; no implementation authority |
| Repository branch | `main` |
| Required repository baseline | `5e45184ee662f582f1b5e86b5bd159fcf07ebc97` |
| Controlling predecessor proposal | `RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_REV8_2026-08-02.md` |
| Controlling predecessor SHA-256 | `d4ce33084010786e1edb295305974c6580295880e251eff6b7603a995dc5ff9e` |
| Status | Proposed for exactly one independent scientific and architecture review |
| Authorization | None: no Track 1 implementation, Track 2 repair, dataset generation, publication, or deployment |

## 1. Purpose and finality

Revision 9 replaces the iterative patch architecture with one closed correction
contract. It fixes every remaining decision before implementation. No path,
count, policy preimage, replay partition, runner behavior, or finalization step
is left for an implementer to choose.

This document supersedes Revision 8 for all gate, replay, inventory, and
sequencing rules. A preliminary Revision 8 re-review draft stated an S8-RR-003
generic remainder of 141. Full set recomputation proved that two additional
separately copied paths - the certified verifier and certified test module -
are also members of the 145-path ledger. The exact special set is therefore 6
and the exact generic remainder is 139. Revision 9 uses the corrected value.

The protected file `scripts/build_rcc002_spec_bundle.py` is outside every scope,
policy, ledger, package, test, and evidence set. It must not be read, hashed,
inspected, opened, executed, imported, copied, renamed, deleted, modified,
staged, committed, packaged, or used as evidence.

## 2. Frozen architecture summary

| Contract | Exact value |
|---|---:|
| Discovered `tests/rcc002/test_*.py` modules after Track 1 drafting | 60 |
| Track 1 current-state modules | 45 |
| Historical replay adapters | 2 |
| Historical audit-only modules | 2 |
| Excluded Track 2 candidate modules | 11 |
| Track 1 governed modules | 49 (`45 + 2 + 2`) |
| Track 1 executable modules | 47 (`45 + 2`) |
| Track 1 files | 46 (`4 MODIFIED + 42 NEW`) |
| Current draft ledger | 179 |
| New ledger paths still to add | 9 |
| Successor ledger | 188 (`179 + 9`) |
| Baseline-ledger expression | `188 = 145 + 43 - 0`, with 2 replacements count-neutral |
| S8-RR-002 certified methods | 28 |
| S8-RR-002 special/remainder paths | `4 / 37` |
| S8-RR-003 certified methods | 41 |
| S8-RR-003 special/remainder paths | `6 / 139` |

These numbers are fixed. A different number requires a new proposal and a new
independent review; it may not be selected during implementation.

## 3. Exact four-category module policy

### 3.1 Path-to-module rule

Every policy entry is a repository-relative ASCII POSIX path ending in `.py`.
Its dotted module name is formed by removing `.py` and replacing every `/`
with `.`. The runner executes only current-state and replay-adapter entries.

### 3.2 `current_state_modules` - 45 entries

1. `tests/rcc002/s0/test_ingest.py`
2. `tests/rcc002/s0/test_integrity.py`
3. `tests/rcc002/s0/test_manifest.py`
4. `tests/rcc002/s0/test_profiles.py`
5. `tests/rcc002/s0/test_source_identity.py`
6. `tests/rcc002/s1/test_normalize.py`
7. `tests/rcc002/s1/test_numeric.py`
8. `tests/rcc002/s1/test_row_id.py`
9. `tests/rcc002/s1/test_schema.py`
10. `tests/rcc002/s1/test_time.py`
11. `tests/rcc002/s2/test_anomalies.py`
12. `tests/rcc002/s2/test_duplicates.py`
13. `tests/rcc002/s2/test_invariants.py`
14. `tests/rcc002/s2/test_schema.py`
15. `tests/rcc002/s2/test_segment.py`
16. `tests/rcc002/s2/test_validate.py`
17. `tests/rcc002/s3/test_compute.py`
18. `tests/rcc002/s3/test_formulas.py`
19. `tests/rcc002/s3/test_golden_fixtures.py`
20. `tests/rcc002/s3/test_schema.py`
21. `tests/rcc002/s3/test_segment.py`
22. `tests/rcc002/s3/test_state.py`
23. `tests/rcc002/s4/test_compute.py`
24. `tests/rcc002/s5/test_compute.py`
25. `tests/rcc002/s5/test_formulas.py`
26. `tests/rcc002/s5/test_golden_fixtures.py`
27. `tests/rcc002/s5/test_schema.py`
28. `tests/rcc002/s5/test_state.py`
29. `tests/rcc002/s6/test_compute.py`
30. `tests/rcc002/s6/test_formulas.py`
31. `tests/rcc002/s6/test_golden_fixtures.py`
32. `tests/rcc002/s6/test_reason_codes.py`
33. `tests/rcc002/s6/test_schema.py`
34. `tests/rcc002/s7/test_compute.py`
35. `tests/rcc002/s7/test_formulas.py`
36. `tests/rcc002/s7/test_golden_fixtures.py`
37. `tests/rcc002/s7/test_planning.py`
38. `tests/rcc002/s7/test_reason_codes.py`
39. `tests/rcc002/s7/test_schema.py`
40. `tests/rcc002/test_constants.py`
41. `tests/rcc002/test_reason_codes.py`
42. `tests/rcc002/test_s8bcp001_implementation_correction.py`
43. `tests/rcc002/test_s8candbcp_gate_scope.py`
44. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py`
45. `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py`

### 3.3 `historical_replay_adapter_modules` - 2 entries

1. `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py`
2. `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py`

### 3.4 `historical_audit_only_modules` - 2 entries

1. `tests/rcc002/test_s8rr002_manifest_correction.py`
2. `tests/rcc002/test_s8rr003_normative_ledger.py`

### 3.5 `excluded_track2_candidate_modules` - 11 entries

1. `tests/rcc002/s8/test_artifact_class.py`
2. `tests/rcc002/s8/test_canonical.py`
3. `tests/rcc002/s8/test_field_registry.py`
4. `tests/rcc002/s8/test_identity.py`
5. `tests/rcc002/s8/test_manifests.py`
6. `tests/rcc002/s8/test_projection.py`
7. `tests/rcc002/s8/test_publication.py`
8. `tests/rcc002/s8/test_reconciliation.py`
9. `tests/rcc002/s8/test_states.py`
10. `tests/rcc002/s8/test_validation.py`
11. `tests/rcc002/s8/test_views.py`

The excluded modules may be discovered by filename only. The Track 1 runner
must never import, execute, inspect, or hash their content. They remain the
separate Track 2 implementation candidate and obtain their own gate only after
Track 1 certification and an authorized Track 2 correction cycle.

### 3.6 Exact set invariants

The gate-scope verifier must assert:

1. Each category equals its independently hardcoded ordered tuple.
2. Counts are exactly `45/2/2/11`.
3. Every category is sorted and unique.
4. All pairwise intersections are empty.
5. The four-category union contains exactly 60 paths.
6. Disk discovery under `tests/rcc002` equals the four-category union exactly.
7. The governed union contains exactly 49 paths.
8. The executable union contains exactly 47 paths.
9. No excluded or audit-only module enters the executable union.
10. No unknown, missing, duplicate, unsafe, or reclassified path is accepted.

## 4. Canonical gate-policy preimage and independent runner authority

### 4.1 Canonical preimage

The policy preimage is ASCII. It uses the category order shown below, preserves
the exact path order from Section 3, uses LF separators, and ends with exactly
one LF:

```text
policy_id=RCC002_S8CANDBCP_GATE_POLICY_V1
category=current_state_modules
path=<each Section 3.2 path>
category=historical_replay_adapter_modules
path=<each Section 3.3 path>
category=historical_audit_only_modules
path=<each Section 3.4 path>
category=excluded_track2_candidate_modules
path=<each Section 3.5 path>
```

The exact preimage contains 65 lines and 2687 bytes. Its SHA-256 is:

`27414251ea113e9f135f7ed93ce120bd0fe454575914083654b8c9d71e2bfbe1`

### 4.2 Four independent representations

1. `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json` contains
   all four exact path arrays, all counts, the canonical preimage rule, and the
   policy SHA-256.
2. `scripts/rcc002/verify_s8candbcp_gate_scope.py` independently hardcodes all
   four path tuples, all counts, the preimage rule, and the expected digest.
3. `scripts/rcc002/run_s8candbcp_gate.py` independently hardcodes counts
   `60/49/45/2/2/11/47` and policy digest
   `27414251ea113e9f135f7ed93ce120bd0fe454575914083654b8c9d71e2bfbe1`.
   It reconstructs the preimage from verifier-returned categories and rejects
   a digest mismatch before importing any test module.
4. `tests/rcc002/test_s8candbcp_gate_scope.py` independently hardcodes the four
   lists, counts, preimage rule, and digest as test authority.

No artifact imports another artifact's constants to define its own authority.

## 5. Exact runner behavior

The production command is:

```text
PYTHONDONTWRITEBYTECODE=1 python3 scripts/rcc002/run_s8candbcp_gate.py
```

The runner must:

1. Validate the gate-scope manifest through the verifier before imports.
2. Recompute and compare the canonical policy SHA-256 independently.
3. Assert all seven counts from Section 4.2.
4. Convert only the 45 current-state and 2 replay paths to dotted names.
5. Load exactly 47 modules, once each, in category and lexical order.
6. Never load the 2 audit-only or 11 excluded Track 2 modules.
7. Return nonzero for scope, digest, import, test-failure, or test-error defects.
8. Return zero only when all 47 executable modules load and all contained tests
   pass with no failure or error.

## 6. Exact runner and scope tests

`tests/rcc002/test_s8candbcp_gate_scope.py` must cover:

1. Valid four-category manifest and disk tree.
2. Missing, extra, duplicate, reordered, unsafe, or unknown path.
3. Every pairwise category overlap.
4. Current-state/replay/audit/excluded reclassification in both directions.
5. Same-count path substitution.
6. Wrong metadata or count.
7. Wrong policy SHA-256.
8. Drift between manifest, verifier, runner digest, and test authority.
9. Scope validation before import.
10. Exactly 47 loader calls, once each, in exact order.
11. Zero loader calls for audit-only and excluded paths.
12. Import failure, test failure, and test error return nonzero.
13. A full synthetic production-policy positive control.

The positive control creates an isolated temporary repository with all 60 exact
test-module paths. Each of the 47 executable modules contains one passing
`unittest.TestCase`. Each of the 2 audit-only and 11 excluded modules contains
one deliberately failing test. Required package `__init__.py` files are
created. Byte-identical copies of the finalized production gate runner,
gate-scope verifier, and manifest are placed at their exact paths. A subprocess
runs the production command from the temporary root. Success requires exit 0,
`Ran 47 tests`, and `OK`. Any loading of audit-only or excluded modules makes
the control fail, so exclusion is proven behaviorally.

## 7. Historical replay contracts

### 7.1 Common rules

Both adapters:

- run only inside `tempfile` roots outside the repository;
- verify every source byte against a certified hardcoded digest or historical
  ledger entry before copying;
- copy the byte-identical certified verifier and complete certified test module;
- execute the complete original test module in a subprocess with
  `PYTHONDONTWRITEBYTECODE=1`;
- require exact method count and exact passing summary;
- include a live-state substitution negative control;
- clean every temporary root in `finally`; and
- never access the protected builder.

### 7.2 S8-RR-002 replay

Exact counts:

```text
immutable inputs = 11
candidate outputs = 30
overlap = 0
union = 41
special paths = 4
generic remainder = 37
certified test methods = 28
```

The four special paths are DP, RM, the S8-RR-002 verifier, and the complete
S8-RR-002 test module. The generic set is the certified 41-path union minus
those four paths. The adapter asserts exact category equality, counts,
disjointness, special membership, remainder equality, and `len(remainder)==37`
before copying any byte. Every special and generic path is copied exactly once.

The subprocess must report `Ran 28 tests` and `OK`. Mutations must cover missing,
extra, duplicate, overlap, same-count substitution, absent special path, and
double-copy detection.

### 7.3 S8-RR-003 replay

Exact counts:

```text
certified ledger targets = 145
special paths = 6
generic remainder = 139
certified test methods = 41
```

The six special paths are:

1. `scripts/rcc002/verify_s8rr003_normative_ledger.py`
2. `tests/rcc002/test_s8rr003_normative_ledger.py`
3. `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`
4. `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
5. `docs/review/evidence/RCC_002_S8RR003_NORMATIVE_LEDGER_SCOPE_V1.json`
6. `docs/review/evidence/RCC_002_S8BCP001_REV2_NORMATIVE_BUNDLE_SHA256SUMS_2026-07-30.txt`

All six are members of the certified 145-target set. The adapter computes
`generic = certified_targets - special`, asserts `len(generic)==139`, and
copies every special and generic path exactly once. DP and RM come from their
frozen certified copies; all other bytes must match the certified ledger.

The subprocess must report `Ran 41 tests` and `OK`, thereby preserving the
ResourceWarning regression and full mutation battery. Mutations must cover
missing, extra, duplicate, overlap, same-count substitution, absent special
path, omitted certified test method, and double-copy detection.

## 8. Exact Track 1 inventory - 46 entries

The inventory is LC_ALL=C ordered.

1. `CLAUDE.md` - MODIFIED
2. `SHA256SUMS` - MODIFIED
3. `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json` - NEW
4. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_HISTORICAL_COPY_2026-08-01.txt` - NEW
5. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_NORMATIVE_LEDGER_SCOPE_V1.json` - NEW
6. `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` - NEW
7. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_0_8_0_CERTIFIED_COPY_2026-08-02.txt` - NEW
8. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_0_9_0_CERTIFIED_COPY_2026-08-02.txt` - NEW
9. `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` - MODIFIED
10. `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` - MODIFIED
11. `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` - NEW
12. `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` - NEW
13. `scripts/rcc002/run_s8candbcp_gate.py` - NEW
14. `scripts/rcc002/verify_s8candbcp_gate_scope.py` - NEW
15. `scripts/rcc002/verify_s8candbcp_rev2_normative_ledger.py` - NEW
16. `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` - NEW
17. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json` - NEW
18. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json` - NEW
19. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/CASE_LEDGER.json` - NEW
20. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/absolute-path.json` - NEW
21. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-specification.json` - NEW
22. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/duplicate-view.json` - NEW
23. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/extra-property.json` - NEW
24. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-id.json` - NEW
25. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/invalid-timestamp.json` - NEW
26. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-required-field.json` - NEW
27. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-specification.json` - NEW
28. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/missing-view.json` - NEW
29. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/path-traversal.json` - NEW
30. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-specification.json` - NEW
31. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/reordered-view.json` - NEW
32. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-field.json` - NEW
33. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/secret-like-value.json` - NEW
34. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/stale-specification-version.json` - NEW
35. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-specification.json` - NEW
36. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/unknown-view.json` - NEW
37. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-identity.json` - NEW
38. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-schema-version.json` - NEW
39. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-type-nullability.json` - NEW
40. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-allowlist-hash.json` - NEW
41. `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/wrong-view-fingerprint-hash.json` - NEW
42. `tests/rcc002/test_s8candbcp_gate_scope.py` - NEW
43. `tests/rcc002/test_s8candbcp_rev2_normative_ledger.py` - NEW
44. `tests/rcc002/test_s8candbcp_rev2_track1_normative_scope.py` - NEW
45. `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py` - NEW
46. `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py` - NEW

Category totals are exactly 4 modified and 42 new. None of the 33 separate S8
candidate Python files is a Track 1 inventory member.

## 9. Ledger contract

The current working ledger has exactly 179 entries. None of the following nine
paths is currently present:

1. `CLAUDE.md`
2. `docs/review/evidence/RCC_002_S8CANDBCP_GATE_SCOPE_V1.json`
3. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_DATA_PIPELINE_SPECIFICATION_0_8_0_CERTIFIED_COPY_2026-08-02.txt`
4. `docs/review/evidence/RCC_002_S8RR002_HISTORICAL_REPRODUCIBILITY_AND_MANIFEST_0_9_0_CERTIFIED_COPY_2026-08-02.txt`
5. `scripts/rcc002/run_s8candbcp_gate.py`
6. `scripts/rcc002/verify_s8candbcp_gate_scope.py`
7. `tests/rcc002/test_s8candbcp_gate_scope.py`
8. `tests/rcc002/test_s8rr002_manifest_correction_historical_replay.py`
9. `tests/rcc002/test_s8rr003_normative_ledger_historical_replay.py`

After all nine are byte-finalized, the ledger transition is exactly:

```text
179 current entries + 9 added entries = 188 successor entries
188 = 145 certified baseline + 43 additions - 0 removals
2 baseline replacements (DP and RM) are count-neutral
```

The root ledger never lists itself. The protected builder and all 33 separate
S8 candidate Python files remain absent.

## 10. Exact `CLAUDE.md` governance insertion

Before final verification, the `## Commands` fenced block gains exactly:

```text

# RCC-002 S8 Track 1 mandatory gate (authoritative for Track 1 only)
PYTHONDONTWRITEBYTECODE=1 python3 scripts/rcc002/run_s8candbcp_gate.py

# Flat RCC-002 discovery is historical-audit only for Track 1. The separate
# tests/rcc002/s8 candidate suite is excluded until the authorized Track 2 cycle.
python -m unittest discover -s tests/rcc002 -p "test_*.py"
```

`CLAUDE.md` is byte-finalized before ledger construction, independent review,
and certification. No post-certification edit is allowed.

## 11. Closed implementation and certification sequence

1. Confirm baseline commit, empty index, and unchanged pre-existing candidate
   paths. Do not access the protected builder.
2. Draft the eight new gate/replay artifacts and the exact `CLAUDE.md` change.
3. Apply the required count, correction-ID, entry, and hash updates to the five
   existing draft scope/ledger artifacts.
4. Byte-finalize the two frozen historical specification copies.
5. Byte-finalize both replay adapters using the exact `4+37` and `6+139`
   partitions.
6. Byte-finalize gate-scope verifier, manifest, runner, and combined test module
   using the exact four-category policy and policy digest.
7. Byte-finalize `CLAUDE.md` and every remaining Track 1 artifact.
8. Starting from the actual 179-entry ledger, add all nine new paths, update all
   changed hashes, sort in LC_ALL=C order, and prove exactly 188 entries.
9. Run the Track 1 scope verifier, normative-ledger verifier, and authoritative
   47-module gate. All must pass.
10. Run S8-RR-002 and S8-RR-003 replay adapters. They must report 28/28 and
    41/41 passing respectively.
11. Confirm both audit-only original modules still fail against the advanced
    live tree for only the documented historical reasons; they are not gate
    failures.
12. Stage exactly the 46 Track 1 files. Prove the staged path set, staged file
    count, staged patch SHA-256, file-list SHA-256, and clean unstaged diff for
    those paths.
13. Perform exactly one independent scientific and architecture review of the
    byte-finalized 46-file candidate and its verification evidence.
14. If and only if that review returns `APPROVE`, create one certification
    decision bound to the exact staged hashes and commit the already-reviewed
    bytes without mutation.
15. Push and prove `HEAD == origin/main`.
16. Only after Track 1 is certified may a separate Track 2 correction candidate
    be prepared from the 33 excluded S8 files.

No step may introduce a new design choice. Any failed invariant stops the cycle
and requires diagnosis, not another broad proposal rewrite.

## 12. Acceptance gates for the one independent review

Approval is permitted only if all statements below are mechanically true:

1. The four module lists equal Section 3 exactly.
2. Counts equal `60/49/45/2/2/11/47` exactly.
3. Policy preimage is 65 lines, 2687 bytes, and hashes to
   `27414251ea113e9f135f7ed93ce120bd0fe454575914083654b8c9d71e2bfbe1`.
4. No S8 Track 2 module is imported by the gate.
5. Runner independently rejects a same-count policy substitution.
6. Synthetic production-policy control runs exactly 47 passing tests and does
   not run the 13 audit/excluded failures.
7. S8-RR-002 path partition is exactly `41 = 4 + 37` and all 28 tests pass.
8. S8-RR-003 path partition is exactly `145 = 6 + 139` and all 41 tests pass.
9. Track 1 inventory is exactly `46 = 4 + 42`.
10. Ledger transition is exactly `179 + 9 = 188`.
11. All 188 ledger hashes verify.
12. The staged set contains exactly the 46 Track 1 files and no other path.
13. The separate 33-file S8 candidate and protected builder are absent from the
    staged set, Track 1 ledger additions, and review authority.
14. Nothing is edited after byte finalization.

## 13. Authorization boundary

This proposal authorizes no implementation by itself. Its only next action is
one independent review of this document. If approved, the exact architecture
may be implemented without another proposal revision. After implementation,
one candidate review and one certification decision remain required.

Track 2 repair, dataset generation, dataset publication, paper deployment,
live deployment, and production use remain unauthorized.

PROPOSED FOR ONE FINAL INDEPENDENT REVIEW
