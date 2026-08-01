# RCC-002 S8-RR-002 Correction Candidate ChatGPT Independent Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8RR002-CAND-CR-001` |
| Review date | `2026-08-01` |
| Reviewer | ChatGPT independent scientific and architecture reviewer |
| Review class | Independent review of generated correction artifacts |
| Repository baseline | `d06b629d7103482564d704276addb773a264cab5` |
| Candidate package | `RCC_002_S8RR002_CORRECTION_CANDIDATE_REVIEW_INPUT_2026-08-01.zip` |
| Candidate package SHA-256 | `9599485fdbbe5057cbb79c31ce0d9377df363b6f42bad2070f0dd7df06b1e9c9` |
| Controlling contract | `RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_REV2_2026-07-31.md` |
| Findings in scope | `S8-RR2-B01`, `S8-RR2-B02` |
| Final decision | `REJECT` |

## 1. Executive decision

The generated candidate correctly repairs the substantive Dataset Manifest
view and specification-profile defects. Its normative text, Schema `1.0.1`,
positive fixtures, negative fixtures, literal hashes and historical-artifact
immutability all passed independent verification.

The candidate nevertheless cannot be certified because the new mechanical
verifier does not enforce the completeness of its versioned scope manifest.
A required fixture path can be removed from the scope manifest while leaving
the file in place, and the complete verifier still returns `PASS`. The
reported candidate SHA-256 inventory is also incomplete: it covers 27 of the
30 generated or modified candidate files.

This is one major architecture and verification-scope finding. It does not
require changing the approved scientific or normative Dataset Manifest
contract.

## 2. Package and scope verification

The supplied package SHA-256 matched the owner-reported value. ZIP path
safety passed, 1,613 files were extracted into an isolated review directory,
and the protected untracked file
`scripts/build_rcc002_spec_bundle.py` was absent.

The review inspected:

- the approved Revision 2 proposal and both proposal reviews;
- the corrected Reproducibility and Manifest `0.9.0` specification;
- all six unchanged non-self specifications;
- Dataset Manifest Schemas `1.0.0` and `1.0.1`;
- historical and new positive and negative fixtures;
- the new case ledger and versioned scope manifest;
- the new correction verifier and focused tests;
- the review-only dependency pin.

No S8 production module was present in the candidate.

## 3. Independent verification results

### 3.1 Substantive contract checks

The following checks passed:

1. `DatasetManifest.views` contains exactly the six distinct registered views
   in the required canonical order.
2. View IDs, versions, references and allowlist hashes match the authoritative
   Data Pipeline registry.
3. `specification_profile` contains exactly the seven required documents in
   the required order and uses `RCC-002-RM/0.9.0`.
4. The six non-self literal hashes match the exact current specification
   bytes.
5. Section 24 uses the explicitly labelled all-zero placeholder only for the
   Run Manifest self-entry.
6. Both positive `1.0.1` fixtures use the actual Run Manifest `0.9.0` file
   hash:
   `23fd2fc0a0338124e9bbd9d95bf6797662d1e32012cb6247763e47a47bf61cf1`.
7. Dataset Manifest Schema `1.0.1` preserves the applicable `1.0.0`
   structural rules and adds exact ordered membership for both corrected
   arrays.
8. Both positive fixtures are distinct payloads.
9. All 11 applicable historical structural negative cases were ported and
   all 10 mandatory semantic negative cases were added.
10. Every negative fixture isolates its documented invalid dimension and is
    rejected for the corresponding schema constraint.
11. `CASE_LEDGER.json` is machine-readable, complete and deterministic. Its
    filename was not prescribed by Revision 2; the selected name is accepted
    and is not a finding.
12. Dataset Manifest Schema `1.0.0`, its two historical positive fixtures and
    Stage Manifest Schema `1.0.0` match their required immutable hashes.
13. `requirements-rcc002-review.txt` contains exactly
    `jsonschema==4.26.0`.
14. No S0-S7 science, production values or S8 production code were changed.

### 3.2 Mechanical execution

| Check | Independent result |
|---|---:|
| Candidate verifier with original scope | `PASS` |
| Focused correction tests | `16/16 PASS` |
| Complete RCC-002 suite | `647/647 PASS` |
| TD-005 regression suite | `170/170 PASS` |
| Targeted Python compilation | `PASS` |
| Draft 2020-12 cross-check with Ajv 8.17.1 | 2 positive accepted; 21 negative rejected |
| Historical immutable artifacts | `4/4 PASS` |
| Distinct positive fixture payloads | `2/2` |

The Python verification used the exact review dependency
`jsonschema==4.26.0` installed into an isolated temporary dependency target.
The extracted candidate was not modified.

## 4. Finding

### 4.1 `S8RR002-CAND-ARCH-001` -- MAJOR

**Title:** The verifier does not enforce a complete closed scope and reports
an incomplete candidate inventory.

**Affected artifacts:**

- `scripts/rcc002/verify_s8rr002_artifacts.py`, especially lines 136-162 and
  500-527 in the reviewed candidate;
- `docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`;
- `tests/rcc002/test_s8rr002_manifest_correction.py`, especially the scope
  tests around lines 201-217.

**Evidence:**

1. `load_scope()` validates ordering, duplicates, path syntax and existence
   only for the paths that happen to remain in the two lists. It does not
   compare the manifest against the exact required immutable-input and
   candidate-output sets.
2. The verifier discovers positive and negative fixtures independently with
   `Path.glob()` rather than deriving the read set from the committed scope
   lists.
3. A mutation removed the required path
   `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/wrong-schema-identity.json`
   from `correction_candidate_outputs` while leaving the fixture on disk.
   The complete verifier still returned `PASS`; its inventory merely shrank
   from 27 to 26 entries.
4. The normal candidate inventory contains 27 entries, while the generated
   correction candidate contains 30 modified or new files. These candidate
   files are absent from the inventory:

   - `docs/review/evidence/RCC_002_S8RR002_CORRECTION_VERIFIER_SCOPE_V1.json`;
   - `scripts/rcc002/verify_s8rr002_artifacts.py`;
   - `tests/rcc002/test_s8rr002_manifest_correction.py`.

5. The focused scope test checks for selected source strings and forbidden
   traversal strings, but it does not mutation-test missing or undeclared
   required entries.

**Contract impact:**

This violates Revision 2 Sections 5.5, 5.6 items 1 and 12, and 5.7. The
versioned scope is intended to be a closed portable path contract. Under the
current implementation it can be silently narrowed without invalidating the
verification result, and the purported complete stable candidate SHA-256
inventory omits three candidate artifacts. Revision 2 Section 9 explicitly
prevents approval while a verification-scope ambiguity remains.

**Required correction:**

1. Define and validate the exact required scope metadata and exact path sets,
   including every generated or modified candidate artifact that must enter
   the stable candidate inventory.
2. Derive fixture and candidate reads from the validated scope manifest,
   rather than independently discovering them by directory globbing.
3. Fail closed for every missing, duplicate, unsafe, category-misclassified or
   undeclared required scope entry.
4. Produce a complete stable SHA-256 inventory for all 30 candidate files,
   including the scope manifest, verifier and focused test file. The inventory
   may be emitted as review output or recorded separately, but it must be
   complete and reproducible without creating a self-hash cycle.
5. Add mutation tests proving rejection of at least:

   - a removed required scope entry;
   - an undeclared fixture or candidate path;
   - a duplicate path within and across categories;
   - an unsafe absolute or parent-traversal path;
   - a required path placed in the wrong scope category;
   - an incomplete candidate inventory.

6. Rerun the correction verifier, focused tests, complete RCC-002 suite,
   regression suite and independent review after the repair.

The normative Run Manifest text, Schema `1.0.1`, fixtures and their Run
Manifest self-hash do not need to change if the repair is confined to scope,
verifier and test artifacts.

## 5. Process observations

### 5.1 Protected-file read -- INFORMATIONAL PROCESS DEVIATION

The implementation agent disclosed that it ran `md5sum` against the protected
untracked builder despite an explicit prohibition on reading it. The file was
not modified, staged, deleted, renamed or executed, and it is absent from the
review package. This does not affect candidate bytes, but the deviation must
remain recorded.

### 5.2 Candidate file count

The implementation summary reported 27 files. The actual generated or
modified candidate contains 30 files. The difference is exactly the three
files missing from the verifier's candidate inventory, as listed in Finding
`S8RR002-CAND-ARCH-001`.

## 6. Final decision

The scientific and normative corrections for `S8-RR2-B01` and
`S8-RR2-B02` are substantively correct. Certification is blocked solely by
the incomplete enforcement of the approved versioned verification scope and
candidate inventory.

The candidate must be repaired and independently re-reviewed before
certification. S8 production code and dataset publication remain prohibited.

REJECT
