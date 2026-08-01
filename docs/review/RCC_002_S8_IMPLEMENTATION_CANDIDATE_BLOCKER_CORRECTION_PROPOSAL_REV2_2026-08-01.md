# RCC-002 S8 Implementation Candidate Blocker Correction Proposal - Revision 2

## Document control

| Field | Value |
|---|---|
| Proposal ID | `RCC-002-S8-CAND-BCP-001-REV2` |
| Proposal date | `2026-08-01` |
| Proposal class | Correction planning only (no implementation) |
| Revision | `2` (supersedes Revision 1) |
| Target artifact | The rejected, uncommitted S8 implementation candidate |
| Candidate baseline (repository HEAD at drafting time) | `27cb48a0723b843960c70a7245f9f23830dc2958` |
| Candidate baseline branch | `main` |
| Candidate baseline `origin/main` | `27cb48a0723b843960c70a7245f9f23830dc2958` |
| Expected uncommitted worktree state at drafting time | `?? rcc002/s8/`, `?? scripts/build_rcc002_spec_bundle.py`, `?? tests/rcc002/s8/` |
| Superseded proposal | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_2026-08-01.md` |
| Superseded proposal SHA-256 | `df2f48a8ceb405ef3f4ad17312fad36fc378040e2c4ce02b99c1c30fdfea2b34` |
| Controlling proposal review (Revision 1 rejection) | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_BLOCKER_CORRECTION_PROPOSAL_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Controlling proposal review SHA-256 | `fff8902899c2d1ec4f8951159ffe6a2ece98c9adaae93c851ba02261a9370bd4` |
| Controlling proposal review decision | `REJECT` |
| Controlling candidate review | `docs/review/RCC_002_S8_IMPLEMENTATION_CANDIDATE_CHATGPT_INDEPENDENT_REVIEW_2026-08-01.md` |
| Controlling candidate review SHA-256 | `cf82b9463b8288e7665df1dd45811c3ddd46dacd754e7825d9c973fbcc60579d` |
| Controlling candidate review decision | `REJECT` |
| Authoritative readiness decision | `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_RR004_2026-08-01.md` |
| Authoritative readiness decision SHA-256 | `16876c0815e3735e64b2eacfd85199b5b7c2c5046488482b51389359218d0ee3` |
| Original candidate findings addressed | `S8-CAND-B01`, `S8-CAND-B02`, `S8-CAND-B03`, `S8-CAND-ARCH-001`, `S8-CAND-ARCH-002`, `S8-CAND-IMPL-001`, `S8-CAND-TEST-001`, `S8-CAND-STATE-001`, `S8-CAND-DOC-001` |
| Revision 1 proposal-review findings addressed | `S8-CAND-BCP-B01`, `S8-CAND-BCP-B02`, `S8-CAND-BCP-ARCH-001`, `S8-CAND-BCP-ARCH-002`, `S8-CAND-BCP-IMPL-001`, `S8-CAND-BCP-DOC-001` |
| Proposal status | **Proposal only. Not approved. Not certified. Does not authorize implementation.** |

### Protected-file exclusion statement

`scripts/build_rcc002_spec_bundle.py` is a pre-existing untracked protected
file. It was not read, hashed, inspected, opened, executed, imported,
copied, renamed, deleted, modified, staged, or packaged in the preparation
of this proposal. It appears in this document only in this explicit
exclusion statement and in the passive `git status` listing reproduced
above.

## 1. Purpose and scope of Revision 2

This document is a **correction proposal**, not a repair, not a
specification amendment, and not an implementation-readiness decision. It
does not modify any repository file. Revision 2 exists solely to close
the six findings raised by the independent review of Revision 1
(`RCC-002-S8-CAND-BCP-CHATGPT-IR-001`, `REJECT`), while preserving every
property of Revision 1 that the review confirmed as sound:

1. `S8-CAND-B02` (the View-schema fingerprint gap) remains classified as a
   normative-contract blocker.
2. This proposal still does not invent, infer, or silently select the
   View-schema-fingerprint preimage formula.
3. Track 1 (normative) and Track 2 (implementation) remain separated by an
   explicit, fail-closed gate.
4. No repaired candidate may be resubmitted for review while the
   fingerprint contract remains uncertified.
5. All nine original candidate findings remain mapped to a correction and
   a verification requirement.
6. The five-way decision separation (proposal approval / normative
   certification / implementation-repair authorization / candidate
   certification / dataset-publication authority) is preserved unchanged
   from Revision 1 Section 1.

Revision 2's changes are additive and corrective relative to Revision 1:
every open choice the Revision 1 review identified is now fixed to one
exact answer, and every omitted downstream artifact is now explicitly in
scope. Nothing in Revision 1 that the review marked `PASS` is weakened.

## 2. Baseline and evidence used

- Repository branch `main`, HEAD and `origin/main` both
  `27cb48a0723b843960c70a7245f9f23830dc2958`, verified before drafting.
- Worktree state verified to contain exactly the expected three untracked
  paths, with the protected builder excluded from all analysis.
- All four controlling-document SHA-256 values in the document-control
  table above were independently recomputed from the current repository
  tree and matched before any finding was transcribed into this revision.
- Additional specification and evidence sections read for Revision 2,
  beyond those already used for Revision 1 (restated in Revision 1
  Section 2): Reproducibility and Manifest Specification Section 24
  ("Minimales kanonisches Dataset-Manifest"); the complete Dataset
  Manifest Schema `1.0.1` (`schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json`);
  both certified positive Dataset Manifest `1.0.1` fixtures
  (`tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/minimal-valid.json`,
  `.../complete-valid.json`); the complete Dataset Manifest `1.0.1`
  negative-fixture inventory and its `CASE_LEDGER.json`; the certified
  `run-manifest/1.0.0` fixture's `run_id` value; the S8-RR-003 scope
  manifest and mechanical verifier as the established repository pattern
  for a versioned correction-scope artifact.
- Both certified Dataset Manifest `1.0.1` positive fixtures were confirmed
  to contain six `schema_fingerprint_sha256` values consisting entirely
  of the digit `0`, and the schema's `views[]` `prefixItems` were
  confirmed to bind `allowlist_sha256` to a literal `const` per view while
  leaving `schema_fingerprint_sha256` unconstrained (`$ref: "#/$defs/digest"`,
  accepting any 64-character lowercase hex value) -- independently
  reproducing the Revision 1 review's finding rather than only citing it.

No implementation file was executed, imported, or modified to prepare
this proposal. Read-only inspection only.

## 3. Absolute constraint on `S8-CAND-B02` (unchanged from Revision 1)

`S8-CAND-B02` is a **normative-contract blocker**, not an implementation
defect. This proposal does not invent, infer, or silently select a
replacement preimage for `schema_fingerprint_sha256`. Section 6 defines
exactly which certified specifications and machine-readable artifacts
must be corrected, and by whom, before any implementation code may emit a
real (non-placeholder) `schema_fingerprint_sha256` value. This constraint
is unchanged from Revision 1 Section 3 and is not weakened by any
Revision 2 correction below: Revision 2 makes the *surrounding* contract
(affected documents, versions, artifact paths, fixtures) exact; it still
does not choose the *formula*.

## 4. Revision 2 closure matrix (Revision 1 review findings)

| Finding | Severity | Revision 1 gap | Revision 2 closure section |
|---|---|---|---|
| `S8-CAND-BCP-B01` | BLOCKER | Track 1 omitted RM Section 24 and both certified Dataset Manifest `1.0.1` positive fixtures, which already carry the placeholder value at scale. | Section 6.1, Section 6.6, Section 8 (Track 1 artifact matrix) |
| `S8-CAND-BCP-B02` | BLOCKER | The canonicalization-authority architecture (S0-shared vs. S8-local) was left as an open implementer choice. | Section 7.1, Section 8 (Track 2 artifact matrix) |
| `S8-CAND-BCP-ARCH-001` | MAJOR | No exact successor versions were stated for Data Pipeline Specification or RM; the Minor/Patch classification was internally inconsistent. | Section 6.3, Section 8 |
| `S8-CAND-BCP-ARCH-002` | MAJOR | The fingerprint-registry artifact path/form, canonicalization-fixture path/format, and scope-manifest topology were left open. | Section 6.4, Section 7.2, Section 7.4, Section 8 |
| `S8-CAND-BCP-IMPL-001` | MAJOR | `run:.+` was presented as a complete grammar; it is not. | Section 7.3 |
| `S8-CAND-BCP-DOC-001` | MINOR | Section 5.5-equivalent said two golden preimages; Section 7.3-equivalent said "at least one". | Section 6.5 and every cross-reference in this document now say exactly two |

Every row above is closed by an exact decision in the sections cited, not
by a restatement of the requirement. Section 8 additionally provides a
single consolidated version/path/artifact matrix so no closure in this
table depends on cross-referencing prose alone.

## 5. Finding-to-correction-to-verification map (all nine original candidate findings)

| Finding | Severity | Track | Exact correction requirement | Exact verification requirement | Affected file(s) |
|---|---|---|---|---|---|
| `S8-CAND-B01` | BLOCKER | 2 | Implement actual RFC 8785 UTF-16-code-unit property ordering after NFC preprocessing, in the single shared canonicalization authority fixed in Section 7.1; reject any post-NFC duplicate property name. | Versioned external golden fixture (Section 7.2) including a non-BMP UTF-16-vs-scalar ordering case and an NFC-collision negative case; an independent oracle that does not itself use Python's native string sort; full focused/RCC-002/S0-identity/TD-005 regression re-run (Section 7.5). | `rcc002/canonical.py` (new, Section 7.1); `rcc002/s0/source_identity.py`; `rcc002/s8/canonical.py`; `tests/rcc002/s0/test_source_identity.py`; `tests/rcc002/s8/test_canonical.py`; new fixture file (Section 7.2). |
| `S8-CAND-B02` | BLOCKER | **1 (normative), then 2** | Stop emitting any View-schema fingerprint until the specification owner defines and certifies the complete logical-schema-contract preimage (Section 6). No implementation-chosen formula may be substituted. | Independent literal or fixture evidence for the certified preimage (Section 6.2); a mutation test proving two views with identical schema identity/fields but different allowed producer stages or allowlist identity produce **different** fingerprints once the certified formula is implemented. | `rcc002/s8/views.py:97-119`; `rcc002/s8/manifests/dataset.py` `_views_block()`; plus every artifact in Section 6 and Section 8. |
| `S8-CAND-B03` | BLOCKER | 2 | Validate the complete `dataset_artifact_set_id` against `^dataset-artifact-set:sha256:[0-9a-f]{64}$` before deriving any filesystem path; require the resolved target to be a direct child of the resolved `publish_root`; verify resolved-parent containment before `os.rename`. | Traversal (`../escaped`), absolute-path, malformed-digest, symlink, and out-of-root-staging mutation tests, each proving rejection before any filesystem action; regression re-run. | `rcc002/s8/publication.py:60-89`; `tests/rcc002/s8/test_publication.py`. |
| `S8-CAND-ARCH-001` | MAJOR | 2 | Replace `replace("\\","/").lstrip("./")` with the single canonical portable-path grammar (Section 7.4) applied before registry matching; remove at most one literal leading `./`, never strip repeatedly, never silently convert backslashes. | Mutation tests for `/SHA256SUMS`, `../SHA256SUMS`, `.\SHA256SUMS`, each proving rejection, not silent classification. | `rcc002/s8/artifact_class.py:80-107`; `tests/rcc002/s8/test_artifact_class.py`. |
| `S8-CAND-ARCH-002` | MAJOR | 2 | Define one strict canonical portable-path grammar (Section 7.4) rejecting all C0 controls, DEL, CR/LF, empty segments, `.`/`..`, absolute/drive paths, and backslashes; reuse this single grammar at every boundary. | Grammar tests at the helper boundary, the ledger boundary, and the publication boundary; regression re-run. | `rcc002/s8/validation.py:52-66`; `rcc002/s8/publication.py:102-116`; `tests/rcc002/s8/test_validation.py`; `tests/rcc002/s8/test_publication.py`. |
| `S8-CAND-IMPL-001` | MAJOR | 2 | Centralize complete ID-grammar validators (exact regex per ID kind, not `startswith`), including the corrected run-ID grammar (Section 7.3); enforce non-negative `row_count` and ordered `(start <= end)` `logical_time_coverage` in `DatasetComponent.as_preimage()` identically to `DataArtifactIdentity`; validate `PublishedDataArtifact.relative_path` with the Section 7.4 grammar before it enters any preimage or sort. | Combined mutation reproducing malformed `build_id` plus negative `row_count` plus reversed `logical_time_coverage`, submitted together, proving rejection; per-ID-kind malformed-grammar negative tests, including the run-ID cases in Section 7.3; unsafe-relative-path negative test. | `rcc002/s8/identity.py:205-263,281-346`; `tests/rcc002/s8/test_identity.py`. |
| `S8-CAND-TEST-001` | MAJOR | 2 | Add the machine-readable, versioned canonicalization fixture (Section 7.2), external to test source; make both the implementation test and an actually independent oracle consume it. | Fixture loads and validates in isolation; both consumers reproduce byte-identical results; the previously-passing-but-wrong case fails until `S8-CAND-B01` is corrected, then passes. | New fixture artifact (Section 7.2); `tests/rcc002/s8/test_canonical.py`. |
| `S8-CAND-STATE-001` | MINOR | 2 | Change the final-path helper to require membership in `PUBLICATION_PATH_STATES` rather than only excluding `failed`/`quarantined`; keep `require_publishable()` unchanged. | Mutation tests proving `planned`, `running`, `validating`, and `candidate` are now rejected from the final-path helper, in addition to `failed`/`quarantined`. | `rcc002/s8/states.py`; `rcc002/s8/publication.py`; `tests/rcc002/s8/test_states.py`; `tests/rcc002/s8/test_publication.py`. |
| `S8-CAND-DOC-001` | INFORMATIONAL | 2 | Correct the next candidate implementation report to state 33 files (21 + 12), not 32. No code change. | Manual count check against `find rcc002/s8 tests/rcc002/s8 -name "*.py" | wc -l` (33), reproduced in re-review. | Implementation report text only (not a repository source file). |

## 6. Track 1 - Normative correction track (`S8-CAND-B02`, closes `S8-CAND-BCP-B01`)

### 6.1 Exact affected specifications, examples, schemas, and fixtures

Revision 2 extends the Revision 1 Section 5.1 table with every downstream
artifact the Revision 1 review identified as already carrying the
placeholder value or already constraining its type. Nothing already
certified is silently mutated; every row below either adds new content or
defines an explicit, versioned successor that coexists with the
preserved historical artifact.

| Artifact | Current state | Required Track 1 output | Preservation rule |
|---|---|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` SS6.2 | Generic schema-identity dimension list; no View-fingerprint preimage. | Cross-reference to new SS7.9.5 (below), or inline extension, per Revision 1 Section 5.1 (unchanged). | Additive edit to the successor document version (Section 6.3); the `0.8.0` byte content is not retroactively altered, it is superseded by `0.9.0`. |
| `RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md` new `SS7.9.5` | Does not exist. | New subsection defining the exact `schema_fingerprint_sha256` preimage for all six registered views, in the SS7.9.2 style (explicit JSON preimage block, JCS canonicalization, one literal SHA-256 per view). | New content in the `0.9.0` successor document. |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` SS8.7 | Requires a per-view "logischer Schema-Fingerprint" reference without defining its preimage. | Prose cross-reference to the certified Data Pipeline SS7.9.5, by exact section number. | Additive edit to the successor document version (Section 6.3). |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` SS13 | Already correctly defines `schema_fingerprint_sha256` as "Hash des vollstaendigen logischen Schemavertrags", distinct from `field_registry_sha256` and `view_allowlist_sha256`. | No content change; retained as the field's normative purpose statement and cited from the new SS7.9.5. | Unchanged text, carried into the `0.9.1` successor document unmodified. |
| `RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md` **SS24** ("Minimales kanonisches Dataset-Manifest") | Its single normative example contains six `views[].schema_fingerprint_sha256` values and one `artifacts[].schema_fingerprint_sha256` value, all `"0000...0000"` (64 zero characters), and cites `manifest_schema_version: "1.0.1"`. | Update the example to reference `manifest_schema_ref: "rcc002.dataset-manifest/1.0.2"` and to carry the six certified literal `schema_fingerprint_sha256` values from the new SS7.9.5, once certified. | The `0.9.0`-content byte value of SS24 is superseded, not silently rewritten in place: the successor document `0.9.1` carries the corrected example; the certified `0.9.0` document's own SHA-256 remains a historical fact recorded in prior certification evidence and is not claimed to still describe the current tree. |
| `schemas/rcc002/manifests/dataset-manifest/1.0.1.schema.json` | Certified. `views[]` `prefixItems` bind `allowlist_sha256` to a literal `const` per view; `schema_fingerprint_sha256` is unconstrained (`$ref: "#/$defs/digest"`, any 64-hex value, including all-zero, is structurally valid). | **Preserved byte-for-byte as immutable historical evidence.** No edit. New code targets `1.0.2` exclusively (Section 6.3), mirroring the existing `1.0.0`-vs-`1.0.1` withdrawal-without-deletion precedent already certified for this schema family. | Byte-identical retention; historical verification remains valid against `1.0.1`. |
| `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` (new) | Does not exist. | New schema, structurally identical to `1.0.1` except: (a) `manifest_schema_version`/`manifest_schema_ref` consts updated to `1.0.2`; (b) each of the six `views[]` `prefixItems` entries gains a `schema_fingerprint_sha256: {"const": "<certified literal>"}` constraint, mirroring the existing `allowlist_sha256` `const` pattern exactly; (c) the seven `specification_profile` `prefixItems` version consts updated per Section 6.3's dependency table. `artifacts[].schema_fingerprint_sha256` (via `$defs/data_artifact`) **cannot** receive the same structural `const` treatment, because `artifacts[]` is a variable-length, variable-order array of whatever views a given build actually publishes (one to six entries), not a fixed six-entry `prefixItems` list; this field remains `$ref: "#/$defs/digest"` at the schema layer and is bound **semantically** by the Track 1 mechanical verifier (Section 6.4) and, downstream, by the Track 2 candidate's own manifest-builder validation, which must cross-check each `artifacts[]` entry's `schema_ref` against the `views[]` registry's certified fingerprint for that view. | New artifact; does not alter `1.0.1`. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/minimal-valid.json` | Certified. Contains one all-zero `schema_fingerprint_sha256`. | **Preserved byte-for-byte.** No edit. | Byte-identical retention. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/complete-valid.json` | Certified. Contains two all-zero `schema_fingerprint_sha256` values (one `artifacts[]` entry, one representative `views[]` entry pattern repeated per view). | **Preserved byte-for-byte.** No edit. | Byte-identical retention. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.1/negative/*` (21 files) plus `CASE_LEDGER.json` | Certified, `1.0.1`-scoped. | **Preserved byte-for-byte.** No edit. | Byte-identical retention. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/minimal-valid.json` (new) | Does not exist. | New positive fixture, structurally identical to the `1.0.1` minimal-valid fixture except `manifest_schema_version`/`manifest_schema_ref` set to `1.0.2` and its one `views[]`-implied `schema_fingerprint_sha256` (via its single `artifacts[]` entry) set to the certified literal for `audit`. | New artifact. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/complete-valid.json` (new) | Does not exist. | New positive fixture, structurally identical to the `1.0.1` complete-valid fixture except version fields set to `1.0.2`, `views[]` entries carry all six certified literals, and `artifacts[]` entries carry the literal matching each entry's `schema_ref`. | New artifact. |
| `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/negative/*` plus `CASE_LEDGER.json` (new) | Does not exist. | Port every one of the 21 existing `1.0.1` negative cases to `1.0.2` (same defect class, updated version fields and real fingerprints where a case does not itself target the fingerprint field), **plus** at least one new negative case, `wrong-view-fingerprint-hash.json`, mirroring the existing `wrong-view-allowlist-hash.json` pattern exactly, asserting a `views[]` entry with a fingerprint that does not match its `const`. | New artifacts; case ledger updated to the new total count. |

### 6.2 Exact logical-contract dimensions required in the fingerprint preimage (unchanged from Revision 1)

Per Data Pipeline Specification SS6.2 and RM SS8.7, the certified preimage
must be sensitive to, at minimum: `schema_id` and `schema_version`;
ordered field names; allowed producer stages, ordered; field owner stage
per field; leakage class per field; the View allowlist identity; field
types and nullability; primary key and sort contract; applied
compatibility profile; and relevant enum/reason-code registry versions.
This list, and the explicit statement that this proposal does not decide
the encoding of any of these dimensions, is unchanged from Revision 1
Section 5.2 and is restated here only for cross-reference completeness;
see Revision 1 for the full per-dimension rationale.

### 6.3 Exact successor versions, dependency ordering, and SemVer classification

This closes `S8-CAND-BCP-ARCH-001` completely.

| Object | Current | Proposed exact successor | Classification and rationale |
|---|---|---|---|
| `RCC_002_DATA_PIPELINE_SPECIFICATION` | `0.8.0` | **`0.9.0`** | New normative content (SS7.9.5) is added; no existing field, schema identity, or rule is removed, renamed, or redefined. This is additive per SS6.4's Minor criterion, applied here at document-version granularity by the same magnitude the repository has already used for a comparably-scoped correction chain (RM's own most recent jump to `0.9.0` bundled multiple structural corrections). Final version confirmation remains the specification owner's decision during Track 1 drafting (Section 6.6, step 1); this is this proposal's exact recommended target so every dependent artifact in this table has an unambiguous value to reference during planning. |
| `RCC-002-RM` (Reproducibility and Manifest Specification) | `0.9.0` | **`0.9.1`** | The only RM change is a prose cross-reference in SS8.7 to the new Data Pipeline SS7.9.5, plus updating the SS24 example (Section 6.1). RM's own field definitions (SS13) and rules (SS6.2, SS14) are unchanged. This is the smallest defined increment in the document's existing numbering convention, distinguishing it from the substantive `0.9.0` DP bump. |
| New View-schema-fingerprint registry/profile artifact | Does not exist | **`RCC002_S8_VIEW_SCHEMA_FINGERPRINT_PROFILE_V1`, version `1.0.0`** | First version of a new artifact; no predecessor to be compatible with. |
| `rcc002.dataset-manifest` schema | `1.0.1` (certified; `1.0.0` is separately certified and preserved per the existing S8-RR-002 precedent) | **`1.0.2`** | Adds `const` bindings to a previously-unconstrained field (`views[].schema_fingerprint_sha256`) without removing, renaming, or retyping any field, and without changing any already-`const`-bound field (`allowlist_sha256`, `schema_id`, `schema_version`). This is the same kind of "close a validation gap without touching the field's declared type" change the repository already versioned as a **Patch**-tier bump for the `1.0.0`-to-`1.0.1` transition (which similarly closed `views[]`/`specification_profile` from open to exact-`prefixItems`-with-`items:false`). Revision 2 therefore classifies this as the direct third-digit successor `1.0.2`, resolving the Revision 1 ambiguity by explicit analogy to the one directly comparable precedent already certified in this repository. |
| `rcc002.view.*` View schema identities (`research-features`, `backtest-inputs`, `paper`, `live`, `label-research`, `audit`) | `1.0.0` / `1.0.0` / `1.0.0` / `1.0.0` / `1.0.0` / `2.0.0` | **Unchanged.** | The fingerprint correction adds a new manifest-layer hash field; it does not add, remove, or retype any View field, change any allowlist, or change any `allowed_producer_stages` list. Per SS6.4, no schema-identity version bump is triggered. This resolves the Revision 1 ambiguity about "which object receives the Minor bump": no View schema receives one; only the Dataset Manifest schema (which structurally carries the new constraint) and the two specification documents (which normatively define it) do. |

**Dependency and ordering consequences (deterministic):**

1. The Dataset Manifest schema's `specification_profile` `prefixItems`
   hard-code `const` values for each of the seven profile documents'
   `id` and `version` (independently confirmed present in the certified
   `1.0.1` schema during Revision 2 drafting). The `1.0.2` schema
   **must** update the `RCC_002_DATA_PIPELINE_SPECIFICATION` entry's
   `version` const from `"0.8.0"` to `"0.9.0"` and the `RCC-002-RM` entry's
   `version` const from `"0.9.0"` to `"0.9.1"`; the other five profile
   entries (`RCC-002-DV`, `RCC-002-IS`, `RCC-002-ST`, `RCC-002-RG`, and
   any future entries) are unaffected and their consts are carried over
   unchanged.
2. Because step 1 changes two `const` values inside the `1.0.2` schema,
   the `1.0.2` schema cannot be finalized, hashed, or certified until
   **both** the `0.9.0` Data Pipeline Specification **and** the `0.9.1`
   RM successor documents are themselves certified (their final hashes
   are required inputs to the `1.0.2` schema's own `specification_profile`
   fixture content).
3. Because the `1.0.2` schema's `views[]` `prefixItems` require the six
   certified `schema_fingerprint_sha256` literals as `const` values, the
   `1.0.2` schema cannot be finalized until the new View-schema-fingerprint
   registry (Section 6.4) is itself drafted and its six literal values are
   fixed.
4. Therefore the exact drafting order within Track 1 is: (a) draft and
   internally review Data Pipeline `0.9.0` SS7.9.5 and the fingerprint
   registry together (they are logically one artifact pair); (b) compute
   and record the six literal fingerprints; (c) draft RM `0.9.1`'s SS8.7
   cross-reference and SS24 update, referencing the now-fixed Data
   Pipeline section number and the six literals; (d) only then draft the
   Dataset Manifest `1.0.2` schema and its fixtures, which depend on the
   final hashes of both documents from steps (a)-(c); (e) run the full
   Track 1 gate sequence (Section 6.6) against the complete, mutually
   consistent set.
5. No step above may be reordered: attempting to fix the Dataset
   Manifest `1.0.2` schema's `specification_profile` consts before the
   Data Pipeline/RM successor documents are certified would bind the
   schema to a hash that does not yet exist, which is the same
   forward-reference defect this proposal prohibits for the fingerprint
   formula itself (Section 6.7).

### 6.4 Required machine-readable registry or profile artifact (exact, closes part of `S8-CAND-BCP-ARCH-002`)

Revision 1 left the choice between an embedded normative JSON block and a
standalone registry file open. Revision 2 fixes this to exactly one
choice:

- **Exact path:** `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` (new `registries/rcc002/views/` subdirectory, matching the existing domain-scoped layout already used by `registries/rcc002/release/` and `registries/rcc002/source/`).
- **Exact registry identity:** `registry_id = "RCC002_S8_VIEW_SCHEMA_FINGERPRINT_PROFILE_V1"`, `registry_version = "1.0.0"`.
- **Rationale for standalone over embedded:** the six-view, multi-dimension preimage (Section 6.2) is materially larger and more structurally regular than the two-literal SS8.7 table entries it extends, closer in size and shape to the existing standalone `registries/rcc002/release/release_artifact_class_registry.v1.json` than to an inline table; a standalone file also lets the Track 1 mechanical verifier (Section 6.6) hash and re-derive it independently of the surrounding prose, exactly as `release_artifact_class_registry.v1.json` is already consumed by `rcc002/s8/artifact_class.py`.
- **Required top-level keys** (exact; the specification owner may add fields required to encode a Section 6.2 dimension the owner determines is not yet covered, but may not remove or rename any of these): `registry_id`, `registry_version`, `project` (`"RCC-002"`), `status`, `owning_specification` (`{"id": "RCC_002_DATA_PIPELINE_SPECIFICATION", "version": "0.9.0", "section": "7.9.5"}`), `canonicalization_profile_id` (`"RCC_JSON_CANONICALIZATION_V1"`), `views` (an array, in the exact SS8.7 order: `research-features`, `backtest-inputs`, `paper`, `live`, `label-research`, `audit`), each `views[]` entry carrying at minimum `schema_id`, `schema_version`, every Section 6.2 dimension in a mechanically re-derivable form, and the resulting literal `schema_fingerprint_sha256`.
- **Additional-property policy:** `additionalProperties: false` at every object level, matching the existing repository convention already used throughout the certified manifest schemas.
- **Canonical hashing rule:** each `views[]` entry's `schema_fingerprint_sha256` is the `RCC_JSON_CANONICALIZATION_V1` (corrected per Section 7.1) SHA-256 of that entry's own preimage subset, exactly as `allowlist_sha256` is already derived from the SS7.9.2 preimage subset today; the *preimage subset's exact key set* is the one normative decision this proposal does not make (Section 6.7).

### 6.5 Required literal or versioned fixture evidence (exact count, closes `S8-CAND-BCP-DOC-001`)

Revision 1 was internally inconsistent between "one non-label and one
label view" (two examples) and "at least one". Revision 2 fixes this
everywhere in this document to exactly:

- **Six** literal `schema_fingerprint_sha256` values (one per registered
  view, in SS8.7 order), published in the new Data Pipeline SS7.9.5 and in
  the registry artifact (Section 6.4) -- mirroring how the six
  `allowlist_sha256` values are already published in SS8.7's existing
  table.
- **Exactly two** fully expanded golden preimage examples (not "at
  least one", not a range): one for a non-label view (any one of
  `research-features`, `backtest-inputs`, `paper`, `live` -- they are
  fingerprint-input-identical except for `schema_id`/`schema_ref`, since
  their `allowed_producer_stages` and `fields` are already proven
  byte-identical) and one for a label view (either `label-research` or
  `audit`), so an independent implementer can reconstruct the
  canonicalization byte-for-byte for both structural shapes the formula
  must handle (non-label vs. label-eligible views).
- One negative-evidence case, as literal expected values (not only a
  textual rule), demonstrating that two views differing only in
  `allowed_producer_stages` or only in allowlist identity resolve to
  different fingerprints.

Every section of this document that refers to golden preimage count now
states "exactly two"; there is no remaining "at least one" phrasing in
Revision 2.

### 6.6 Review, certification, and readiness gates (updated ordering)

1. **Specification and registry drafting** by the specification owner,
   producing Data Pipeline `0.9.0` (SS7.9.5), the registry artifact
   (Section 6.4), RM `0.9.1` (SS8.7 cross-reference and SS24 update), in
   the exact dependency order fixed in Section 6.3.
2. **Internal review** of the drafted text and artifacts for internal
   consistency with SS6.2, SS6.4, SS8.7, and SS13.
3. **Scientific consistency review**, confirming the preimage dimensions
   do not silently alter any certified scientific transformation, label,
   or leakage-classification rule.
4. **Architecture review**, confirming the ownership split (Data Pipeline
   owns the logical view contract; RM continues to own the manifest field
   that carries the resulting hash, per SS8.8) and confirming the
   Section 6.4 artifact path/form decision was actually followed.
5. **Independent mechanical verification** of the six literal fingerprint
   values and the two golden preimages (Section 6.5), by independent
   re-derivation from the published preimage, compared byte-for-byte to
   the published literals.
6. **Dataset Manifest `1.0.2` schema and fixture drafting** (Section 6.1),
   only after step 5, consuming the now-fixed six literals and the
   now-certified `0.9.0`/`0.9.1` document hashes (Section 6.3, step 4).
7. **Track 1 mechanical verifier and scope manifest** (Section 8) run
   against the complete artifact set from steps 1-6, hardcoded
   independently of the artifacts themselves, exactly as the existing
   S8-RR-003 scope/verifier pattern already established in this
   repository.
8. **Certification** of the resulting specification revision, registry,
   schema, and fixture set as a normal RCC-002 correction cycle output.
9. Only after step 8 is complete may the implementation repair track
   implement the certified formula, and only after that implementation is
   itself repaired and re-tested may a new candidate be submitted for the
   independent scientific and architecture re-review required by
   Section 10.

### 6.7 Explicit prohibition on implementing an unapproved fingerprint formula (unchanged from Revision 1)

Until Section 6.6 step 8 is complete: no implementation file may compute
or emit a real `schema_fingerprint_sha256` value; no implementation-owned
default, heuristic, or "reasonable guess" for the preimage may be
substituted; if Track 2 work reaches a point where this value would
otherwise be required, the corrected candidate must leave the field
visibly and explicitly blocked (for example, by raising a typed error
identifying the open normative dependency) rather than emit any value.
This proposal does not decide which blocking mechanism the implementer
uses; it only prohibits emitting a value. This is unchanged from
Revision 1 Section 5.7.

## 7. Track 2 - Implementation repair track

### 7.1 Exact canonicalization authority and architecture (closes `S8-CAND-BCP-B02`)

Revision 1 left open whether the RFC 8785/JCS ordering fix belongs inside
the shared S0 primitive or in a new S8-local implementation, and
explicitly forbade a permanent S8-local duplicate without resolving which
alternative to take instead. Revision 2 fixes this to exactly one
architecture:

**Decision:** create a new, single, shared canonicalization module,
`rcc002/canonical.py`, at the top level of the `rcc002` package -- a
peer of the already-established cross-stage shared modules
`rcc002/constants.py` and `rcc002/reason_codes.py`, not owned by any
individual stage. This module becomes the **sole** implementation of
`RCC_JSON_CANONICALIZATION_V1` in the repository.

- `rcc002/s0/source_identity.py`'s `canonical_json_bytes` function
  (currently defined locally, lines 45-71) is changed to import and
  delegate to `rcc002.canonical`, preserving its existing public name and
  call signature so no caller outside this correction needs to change.
- `rcc002/s8/canonical.py`'s `canonical_bytes`/`canonical_sha256` are
  changed to import and delegate to `rcc002.canonical` directly, instead
  of importing `rcc002.s0.source_identity.canonical_json_bytes` as an
  indirect proxy for a stage-owned function.
- **A permanent S8-local duplicate of the JCS ordering, NFC
  normalization, or duplicate-key-rejection logic is prohibited.** Any
  future stage requiring canonical JSON bytes imports
  `rcc002.canonical` directly; no stage module may re-implement any part
  of this logic.
- This resolves the Revision 1 ambiguity between "fix inside S0" and "new
  S8-local module": the correction is neither -- it is a new, shared,
  stage-independent primitive that both S0 and S8 (and any future
  consumer) import identically. This is a **normative-scope-neutral**
  architectural refactor: it changes no specification text, because RM
  SS6.2 already correctly requires actual RFC 8785/JCS today (the
  candidate review's finding was that the *code* did not implement the
  already-correct *rule*). No Track 1 involvement is required for this
  decision.

**Enumerated deterministic identities whose bytes can change once the
ordering/collision fix lands**, and the exact scope of required
regression:

| Identity or hash | Computed via the corrected primitive? | Expected to change for currently-certified inputs? | Required verification |
|---|---|---|---|
| `source_snapshot_id` (S0) | Yes | The Source Snapshot V1 preimage's keys (`identity_profile_id`, `provider`, `market_type`, ..., `source_files[].provider_relative_name`, `csv_member_name`) and, for the currently certified Binance Vision BTCUSDT spot-kline scope, its values are all within the ASCII (Basic Latin, code points 0-127) range. UTF-16 code-unit order and Unicode scalar-value order are provably identical for any preimage containing only such content, because every ASCII character is exactly one UTF-16 code unit numerically equal to its scalar value. **Therefore the currently certified `source_snapshot_id` values are expected to be byte-identical before and after this correction**, but this expectation must be independently confirmed, not assumed, because it depends on every currently certified preimage actually being ASCII-only, which is a factual claim about data, not a proof about all possible future input. | Full `tests/rcc002/s0/test_source_identity.py` regression re-run; an explicit new test asserting the pre-correction and post-correction `source_snapshot_id` are equal for every currently certified fixture in that test module. |
| `field_registry_sha256`, all six `allowlist_sha256` values | Yes (via `rcc002/s8/field_registry.py` and `rcc002/s8/views.py`, both delegating to the same corrected primitive) | No. The field-registry and allowlist preimages use only ASCII object keys (`field_owner_stage`, `leakage_class`, `fields`, `field_name`, `allowed_producer_stages`) and ASCII field-name string values, by the same ASCII-equivalence argument above. **Expected unchanged**, and because these six values are literal `const`s already certified in RM SS8.7, this expectation is independently checkable against those literals directly, with no dependency on data outside the specification text itself. | `tests/rcc002/s8/test_field_registry.py` and `tests/rcc002/s8/test_views.py` full re-run; the existing import-time self-check in `rcc002/s8/views.py` (`_build_view`, which already compares a freshly computed hash against the certified literal) continues to pass unmodified. |
| `build_id`, `dataset_id`, `dataset_artifact_set_id`, `manifest_id`, `artifact_id` (all S8, via `rcc002/s8/identity.py`) | Yes | Not certified against any literal today (the candidate is uncertified); these are expected to be internally self-consistent before and after the fix (the same inputs still produce the same output under the corrected algorithm), which is exactly what `tests/rcc002/s8/test_identity.py`'s determinism tests already check. No specific "before/after" byte comparison is meaningful because no certified literal exists yet for any of these identities. | `tests/rcc002/s8/test_identity.py` full re-run. |

- **Historical identity fixtures:** the ASCII-equivalence argument above
  means no currently certified fixture value (in `tests/rcc002/s0/` or
  anywhere else) is expected to require a versioned successor as a
  consequence of this correction. If the required verification in the
  table above discovers an actual byte change for any currently certified
  fixture, that discovery immediately triggers the same SS27.3 re-review
  requirement as any other identity-preimage change, and this correction
  may not proceed past that point without first drafting a versioned
  successor for the affected fixture through a separate, focused
  correction cycle -- this proposal does not pre-authorize such a
  successor because it does not yet know whether one is needed.

### 7.2 Versioned external canonicalization golden fixtures (exact path and format, closes remainder of `S8-CAND-BCP-ARCH-002`)

- **Exact path:** `tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json` (new `tests/fixtures/rcc002/canonicalization/` subdirectory, matching the existing `tests/fixtures/rcc002/manifests/` and `tests/fixtures/rcc002/source/` layout convention).
- **Exact format:** a single JSON document with top-level keys `fixture_id` (`"RCC002_JSON_CANONICALIZATION_V1_GOLDEN_V1"`), `fixture_version` (`"1.0.0"`), `canonicalization_profile_id` (`"RCC_JSON_CANONICALIZATION_V1"`), and `cases` (an array). Each `cases[]` entry carries: `case_id` (a stable string); `description`; `input` (the JSON value to canonicalize, given inline); `expect` (either `{"canonical_bytes_utf8_hex": "<hex>", "sha256": "<64-hex>"}` for an accepted case, or `{"reject": true, "reason": "<stable machine-readable reason code>"}` for a rejected case).
- **Mandatory cases, at minimum:** (1) the non-BMP UTF-16-vs-scalar ordering pair from the controlling candidate review (`U+E000` and `U+1F600` as object keys), with `expect.canonical_bytes_utf8_hex` reflecting true UTF-16 code-unit order; (2) the NFC-collision pair (precomposed `U+00E9` vs. decomposed `U+0065 U+0301` as two distinct input keys of the same object), with `expect.reject = true`; (3) the existing Revision-1-era JCS/NFC/decimal/timestamp/non-finite golden cases already enumerated in the candidate's own `tests/rcc002/s8/test_canonical.py`, relocated into this external fixture rather than left embedded in test source.
- Both the corrected implementation's own test module and the independent oracle (Section 7.6) load and check against this one file; neither may embed its own copy of the expected bytes/digests.

### 7.3 Complete run-ID grammar (closes `S8-CAND-BCP-IMPL-001`)

The normative RM format is `run:<UTC timestamp>:<UUIDv7-or-UUIDv4>`.
Revision 2 fixes the complete grammar as follows, replacing the
candidate's `run:.+` pattern everywhere it is used.

**Exact two-stage validation** (a single regular expression cannot
express calendar validity; both stages are mandatory):

1. **Lexical/structural stage** (regular expression):

   ```text
   ^run:
   (\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])
    T([01]\d|2[0-3]):[0-5]\d:[0-5]\d(\.\d{6})?Z)
   :
   ([0-9a-f]{8}-[0-9a-f]{4}-[47][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})$
   ```

   (written across lines here for readability; the implemented pattern is
   a single unbroken expression). The UUID version nibble (`[47]`) accepts
   version 4 or version 7 only; the UUID variant nibble (`[89ab]`) accepts
   only the RFC 4122/RFC 9562 variant both UUID versions use.

2. **Calendar-validity stage** (real date-time parsing, not regex): the
   timestamp component must additionally parse as an actual valid UTC
   calendar date and time (rejecting, for example, `2026-04-31` even
   though the regex's day range `01-31` would otherwise accept it, and
   rejecting `2026-02-29` in a non-leap year while accepting
   `2028-02-29` in a leap year).

**Fractional-seconds precision is optional, not mandatory, and exactly
six digits when present.** This is an explicit, evidence-based decision:
the certified `tests/fixtures/rcc002/manifests/run-manifest/1.0.0/complete-valid.json`
fixture's `run_id` value uses no fractional seconds
(`"run:2026-07-30T12:00:00Z:00000000-0000-4000-8000-000000000000"`),
while the current S8 candidate's `rcc002/s8/identity.py` `new_run_id()`
always emits exactly six fractional digits. Making fractional seconds
optional (and exactly six digits when present) is the only grammar that
accepts both the already-certified historical fixture and the candidate's
own current output without requiring either to change, honoring this
proposal's non-destructive-to-certified-evidence principle (Section 6.1)
even outside Track 1's specific scope.

**Required positive boundary tests:**

- `run:2026-08-01T12:00:00Z:` + a valid v4 UUID (no fractional seconds,
  matching the certified run-manifest fixture pattern).
- `run:2026-08-01T12:00:00.123456Z:` + a valid v4 UUID (six-digit
  fractional seconds).
- `run:2026-08-01T12:00:00.000000Z:` + a valid v7 UUID.
- `run:2028-02-29T00:00:00Z:` + a valid UUID (leap-day boundary).

**Required negative boundary tests:**

- `run:source` and `run:target` (the exact two malformed values the
  Revision 1 review found already live in the candidate's own test
  fixtures, both of which `run:.+` incorrectly accepted).
- `run:2026-02-29T00:00:00Z:` + a valid UUID (non-leap-year Feb 29;
  regex-passable, calendar-invalid).
- `run:2026-04-31T00:00:00Z:` + a valid UUID (April has 30 days;
  regex-passable, calendar-invalid).
- `run:2026-13-01T00:00:00Z:` + a valid UUID (invalid month).
- `run:2026-08-01T12:00:00+02:00:` + a valid UUID (non-UTC offset instead
  of `Z`).
- `run:2026-08-01T12:00:00Z:` + a UUID with version nibble `1` or `3`
  (invalid UUID version).
- `run:2026-08-01T12:00:00Z:` + a UUID with variant nibble `c` or `0`
  (invalid UUID variant).
- `run:2026-08-01T12:00:00Z:` + a UUID with a `\n` or other control
  character appended (trailing-data / control-character injection).
- `run:2026-08-01T12:00:00Z:` + a path-separator-bearing string in the
  UUID position (`../escaped`).

**Application boundary:** the same validator function is applied at
every manifest and identity boundary that accepts a `run_id`:
`rcc002/s8/identity.py` (`new_run_id`'s own output, defensively, and any
externally supplied `run_id` accepted by a builder), `rcc002/s8/manifests/run.py`
(`run_id`), `rcc002/s8/manifests/stage.py` (`run_id`), and
`rcc002/s8/manifests/dataset.py` (`publication_run_id`).

### 7.4 One strict canonical portable-path grammar reused everywhere (unchanged decision, restated exactly)

Exactly one portable-path grammar function is the single source of truth,
rejecting: all C0 control characters and DEL; CR and LF; empty path
segments; `.` and `..` segments; absolute paths; Windows drive-letter
paths; and backslashes. This function replaces both the current narrower
`require_portable_relative_path` in `rcc002/s8/validation.py` and the ad
hoc `replace`/`lstrip` logic in `rcc002/s8/artifact_class.py`, and is
reused, without a local variant, at every boundary: artifact
classification (before registry matching), identity preimages
(`relative_path` fields), release-ledger generation, manifest field
validation, and publication path derivation. This is unchanged from
Revision 1 Section 6.7 and is restated here because Section 5 of this
document (the finding map) and Section 8 (the artifact matrix) both
depend on it having exactly one implementation location.

### 7.5 Regression gates (exact, extended for the S0 boundary)

After every Track 2 correction (and, separately, after Track 1 is
certified and its formula is implemented), the corrected candidate must
re-pass, in this order:

1. the focused `tests/rcc002/s8` discovery suite, with an expected pass
   count strictly greater than the current 185;
2. the complete `tests/rcc002` discovery suite;
3. **`tests/rcc002/s0` discovery** (new requirement relative to Revision
   1, added because Section 7.1's canonicalization-authority decision
   brings `rcc002/s0/source_identity.py` into scope);
4. the complete `tests/regression` (TD-005) discovery suite;
5. a repeated independent adverse-mutation pass (Section 7.6), performed
   by the new reviewer required in Section 10, outside the candidate
   tree, leaving no project artifact behind.

No corrected candidate may claim closure of any finding in Section 5
without all five steps above passing.

### 7.6 All original nine adverse mutations, plus the Revision 1 boundary tests, plus the Revision 2 additions

Every mutation already required by Revision 1 Section 6.12 (the nine
reproduced defects plus symlink and malformed-digest boundary tests)
remains required unchanged. Revision 2 adds:

- the run-ID positive and negative boundary tests in Section 7.3;
- an S0-boundary regression case proving `source_snapshot_id` is
  byte-identical before and after the canonicalization-authority
  refactor, for every currently certified S0 fixture (Section 7.1);
- a Dataset Manifest `1.0.2` structural negative case,
  `wrong-view-fingerprint-hash.json` (Section 6.1), once Track 1
  artifacts exist;
- a Track 1 scope-manifest mutation battery (missing, extra, duplicated,
  reordered, miscategorized, unsafe, or undeclared artifact), matching
  the existing S8-RR-003 mechanical-verifier mutation pattern, applied to
  the Section 8 scope manifests once they exist.

## 8. Exact correction-scope topology and consolidated version/path/artifact matrix

This section closes the remainder of `S8-CAND-BCP-ARCH-002` (scope
topology) and consolidates every exact path, version, and identity
decision made in Sections 6-7 into one place, so no closure in this
document depends on cross-referencing prose alone.

### 8.1 Scope-manifest topology (exact, one arrangement)

**Decision: two separate, versioned scope manifests, one per track**,
mirroring the existing S8-RR-002/S8-RR-003 pattern already certified in
this repository, and preserving the Track 1/Track 2 fail-closed
separation at the evidence layer, not only at the prose layer:

- **Track 1 (normative) scope manifest:**
  `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json`,
  `scope_id = "RCC002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1"`,
  `correction_id = "RCC-002-S8CANDBCP-REV2-TRACK1"`,
  `findings_in_scope = ["S8-CAND-B02", "S8-CAND-BCP-B01", "S8-CAND-BCP-ARCH-001", "S8-CAND-BCP-ARCH-002", "S8-CAND-BCP-DOC-001"]`,
  consumed by a new mechanical verifier at
  `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py`.
- **Track 2 (implementation) scope manifest:**
  `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK2_IMPLEMENTATION_SCOPE_V1.json`,
  `scope_id = "RCC002_S8CANDBCP_REV2_TRACK2_IMPLEMENTATION_SCOPE_V1"`,
  `correction_id = "RCC-002-S8CANDBCP-REV2-TRACK2"`,
  `findings_in_scope = ["S8-CAND-B01", "S8-CAND-B03", "S8-CAND-ARCH-001", "S8-CAND-ARCH-002", "S8-CAND-IMPL-001", "S8-CAND-TEST-001", "S8-CAND-STATE-001", "S8-CAND-DOC-001", "S8-CAND-BCP-B02", "S8-CAND-BCP-IMPL-001"]`,
  consumed by a new mechanical verifier at
  `scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py`.
- **Rejected alternative, and why:** a single combined scope manifest was
  considered and rejected, because it would let a verifier report
  "in-scope" status for Track 2 files while Track 1 remains uncertified,
  reintroducing exactly the ambiguity this proposal's Section 6.7 gate
  prohibits. Two manifests make the gate machine-checkable: a Track 2
  candidate resubmission can be mechanically verified against the Track 2
  scope alone, and a reviewer can mechanically confirm the Track 1 scope's
  `findings_in_scope` are independently certified before the Track 2
  verifier is ever run against a combined candidate.
- Each verifier follows the established S8-RR-003 pattern exactly:
  independent hardcoded expected path/version lists (not read from the
  scope manifest as ground truth), rejection of missing, extra,
  duplicated, reordered, miscategorized, unsafe, or undeclared artifacts,
  and a single deterministic JSON result object on stdout.

### 8.2 Consolidated version/path/artifact matrix

| Item | Exact value |
|---|---|
| Data Pipeline Specification successor version | `0.9.0` |
| RM successor version | `0.9.1` |
| View-schema-fingerprint registry path | `registries/rcc002/views/s8_view_schema_fingerprint_profile.v1.json` |
| View-schema-fingerprint registry identity/version | `RCC002_S8_VIEW_SCHEMA_FINGERPRINT_PROFILE_V1` / `1.0.0` |
| Dataset Manifest successor schema version | `1.0.2` |
| Dataset Manifest successor schema path | `schemas/rcc002/manifests/dataset-manifest/1.0.2.schema.json` |
| Dataset Manifest `1.0.2` fixture directory | `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.2/` (`minimal-valid.json`, `complete-valid.json`, `negative/*` ported from `1.0.1` plus `wrong-view-fingerprint-hash.json`, `negative/CASE_LEDGER.json`) |
| View schema identities/versions | Unchanged: `research-features`/`1.0.0`, `backtest-inputs`/`1.0.0`, `paper`/`1.0.0`, `live`/`1.0.0`, `label-research`/`1.0.0`, `audit`/`2.0.0` |
| Canonicalization shared-authority module | `rcc002/canonical.py` (new) |
| Canonicalization golden fixture path | `tests/fixtures/rcc002/canonicalization/rcc_json_canonicalization_v1.golden.v1.json` |
| Canonicalization golden fixture identity/version | `RCC002_JSON_CANONICALIZATION_V1_GOLDEN_V1` / `1.0.0` |
| Run-ID grammar | Section 7.3, two-stage (regex plus calendar parse), fractional seconds optional/exactly-six-digits-when-present |
| Golden preimage example count | Exactly two (one non-label view, one label view) |
| Literal fingerprint count | Exactly six (one per registered view) |
| Track 1 scope manifest | `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK1_NORMATIVE_SCOPE_V1.json` |
| Track 1 verifier | `scripts/rcc002/verify_s8candbcp_rev2_track1_normative_scope.py` |
| Track 2 scope manifest | `docs/review/evidence/RCC_002_S8CANDBCP_REV2_TRACK2_IMPLEMENTATION_SCOPE_V1.json` |
| Track 2 verifier | `scripts/rcc002/verify_s8candbcp_rev2_track2_implementation_scope.py` |

### 8.3 Existing candidate files that may be modified under Track 2 (updated from Revision 1 Section 7.1)

- `rcc002/canonical.py` (**new**)
- `rcc002/s0/source_identity.py` (newly in scope: delegate to `rcc002/canonical.py`, no public signature change)
- `rcc002/s8/canonical.py`
- `rcc002/s8/publication.py`
- `rcc002/s8/artifact_class.py`
- `rcc002/s8/validation.py`
- `rcc002/s8/identity.py`
- `rcc002/s8/states.py`
- `rcc002/s8/views.py` (Track 1 dependency only, per Section 6.7 -- may be changed earlier only to make the blocked status explicit)
- `rcc002/s8/manifests/dataset.py` (same Track 1 dependency note)
- `tests/rcc002/s0/test_source_identity.py` (newly in scope)
- `tests/rcc002/s8/test_canonical.py`
- `tests/rcc002/s8/test_publication.py`
- `tests/rcc002/s8/test_artifact_class.py`
- `tests/rcc002/s8/test_validation.py`
- `tests/rcc002/s8/test_identity.py`
- `tests/rcc002/s8/test_states.py`
- `tests/rcc002/s8/test_views.py` (Track 1 dependency note)
- `tests/rcc002/s8/test_manifests.py` (Track 1 dependency note)

No other repository file may be modified under this proposal, and this
proposal does not itself modify any of them.

## 9. Fail-closed sequencing (updated diagram, same governing rule as Revision 1)

```text
                    +----------------------------------------------+
                    | Track 1: Normative correction (S8-CAND-B02,    |
                    | closes S8-CAND-BCP-B01)                         |
                    | Sections 6.1-6.6                                |
                    +----------------------------------------------+
                                     |
     Drafting (DP 0.9.0 SS7.9.5 + fingerprint registry, in that
     dependency order) -> six literals fixed -> RM 0.9.1 (SS8.7 +
     SS24) -> Dataset Manifest 1.0.2 schema + fixtures ->
     Internal review -> Scientific review -> Architecture review ->
     Independent mechanical verification -> Certification
     (Section 6.6, steps 1-8)
                                     |
                                     v
                    [ GATE: Track 1 certified? ]
                     NO  -------------------------------> STOP.
                     |                                    No implementation of the
                     |                                    fingerprint formula. No
                     |                                    real schema_fingerprint_sha256
                     |                                    may be emitted (Section 6.7).
                     YES
                     |
                     v
     +---------------------------------------------------------------+
     | Track 2: Implementation repair (S8-CAND-B01, B03, ARCH-001/002, |
     | IMPL-001, TEST-001, STATE-001, DOC-001, S8-CAND-BCP-B02,         |
     | S8-CAND-BCP-IMPL-001 -- independent of Track 1 and MAY start     |
     | in parallel with Track 1 drafting)                               |
     | Sections 7.1-7.6                                                 |
     +---------------------------------------------------------------+
                     |
                     v
     [ GATE: all Track-2 findings closed AND regression re-run       ]
     [        (focused S8 / complete RCC-002 / S0 identity / TD-005)  ]
     [        all green (Section 7.5)?                                ]
                     |
                     v
     +---------------------------------------------------------------+
     | View-schema fingerprint formula implementation (only after the |
     | Track 1 gate above is YES) in rcc002/s8/views.py and             |
     | rcc002/s8/manifests/dataset.py                                   |
     +---------------------------------------------------------------+
                     |
                     v
     [ GATE: both tracks fully closed, all fifteen findings' (nine    ]
     [        original plus six Revision-1-review) verification       ]
     [        requirements satisfied?                                 ]
                     |
                     v
          New independent scientific and architecture re-review
          (Section 10) of the corrected candidate, including a fresh
          proposal-conformance check against this Revision 2 document
                     |
                     v
          [ Re-review decision: ACCEPT or REJECT ]
                     |
            ACCEPT --+-- REJECT --> back to the relevant track above
                     |
                     v
     Candidate certification (a separate act from this proposal and
     from the re-review itself)
                     |
                     v
     S8 implementation remains bounded by RR-004 Sections 9-10.
     Dataset generation, publication, and deployment remain
     separately unauthorized regardless of certification (Section 10).
```

**The critical fail-closed rule, restated:** the path from "Track 1
drafted" to "fingerprint formula implemented" has exactly one gate
(Section 6.6, step 8: certification), not merely proposal approval, not
merely a passing review, and not merely implementer confidence that a
reasonable formula was chosen. Track 2 work may proceed in parallel with
Track 1 drafting precisely because it does not depend on this gate; it
must not be used to justify skipping the gate for the one finding that
does.

## 10. Preservation, prohibition, and re-review requirements (unchanged in substance from Revision 1, restated for Revision 2)

- **Historical preservation.** No certified historical artifact --
  including the certified `SHA256SUMS` successor, the historical ledger
  evidence copy, any certified specification document at its
  currently-certified version and hash (including Data Pipeline `0.8.0`
  and RM `0.9.0` themselves, which remain valid historical documents
  describing the tree as it was certified, even after `0.9.0`/`0.9.1`
  successors exist), the certified Dataset Manifest `1.0.0` and `1.0.1`
  schemas, and every currently certified fixture under
  `tests/fixtures/rcc002/manifests/dataset-manifest/1.0.0/` and
  `.../1.0.1/` -- may be modified as part of either track unless an
  explicit versioned successor is drafted, reviewed, and certified
  through the normal correction-cycle process. This Revision 2 proposal
  does not itself modify, and does not authorize modifying, any such
  artifact; Section 6.1's table states this explicitly per affected
  artifact.
- **No dataset generation, publication, or deployment.** Neither track
  authorizes generating or publishing a real dataset, nor live or paper
  production deployment, at any point in this proposal, including after
  both tracks are closed and a corrected candidate is certified.
- **No S8 production code from this proposal.** This document contains
  no code, no pseudocode intended for direct inclusion, and no
  copy-pasteable implementation.
- **Mandatory new independent review.** A new read-only independent
  scientific and architecture re-review is required after both tracks are
  closed, before any certification decision is made, and that re-review
  must independently re-run the complete adverse-mutation matrix
  (Revision 1 Section 6.12 plus Section 7.6 of this revision) outside the
  candidate tree.
- **Decision separation, restated.** Proposal approval (this document),
  normative contract certification (Track 1 output), implementation
  repair authorization (Track 2 start), candidate re-certification (the
  Section 10 re-review's outcome), and S8/dataset readiness (RR-004,
  unaffected by this proposal in either direction) remain five separate
  decisions. Approving this proposal approves only the plan in
  Sections 5 through 9; it does not itself grant any of the other four.

## 11. Restrictions honored while preparing this revision

- No repository file was created, modified, staged, committed, or
  pushed.
- The existing S8 candidate (`rcc002/s8/`, `tests/rcc002/s8/`) was not
  modified, staged, committed, or pushed.
- No implementation code was run. No test was executed.
- No dependency was installed. No network access was used.
- No dataset was generated or published.
- No S8 production code was created.
- `scripts/build_rcc002_spec_bundle.py` was not read, hashed, inspected,
  opened, executed, imported, copied, renamed, deleted, modified,
  staged, or packaged; it appears only in the document-control table's
  worktree-state row and in this restrictions section.
- All diagnostics performed to prepare this revision were passive
  (branch/HEAD/origin/status checks, read-only file inspection,
  read-only search, and in-memory reasoning); none created a repository
  artifact.

## 12. Final statement

Revision 2 closes all six findings raised against Revision 1
(`S8-CAND-BCP-B01`, `S8-CAND-BCP-B02`, `S8-CAND-BCP-ARCH-001`,
`S8-CAND-BCP-ARCH-002`, `S8-CAND-BCP-IMPL-001`, `S8-CAND-BCP-DOC-001`)
with exact, executable decisions -- affected artifacts, successor
versions, artifact paths, scope topology, fixture formats, and grammars
-- while preserving every property of Revision 1 the review confirmed as
sound, and while continuing to withhold the one decision that does not
belong to this proposal: the actual View-schema-fingerprint preimage
formula, which remains reserved for the independently reviewed and
certified Track 1 normative correction artifact. It approves nothing
beyond itself: implementation of any correction described here,
generation or publication of any dataset, and any live or paper
deployment all remain separately unauthorized until the sequencing in
Section 9 and the requirements in Section 10 are satisfied in full.
