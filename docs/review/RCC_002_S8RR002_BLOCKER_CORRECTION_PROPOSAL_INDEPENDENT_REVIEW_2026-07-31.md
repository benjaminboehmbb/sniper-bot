# RCC-002 S8-RR-002 Blocker Correction Proposal Independent Review

## Document control

| Field | Value |
|---|---|
| Review ID | `RCC-002-S8RR002-BCP-001-INDEPENDENT-REVIEW` |
| Review date | `2026-07-31` |
| Reviewer role | Independent scientific and architecture reviewer |
| Repository baseline | `3605d1de37d1fc56634b1011fa1ea1049e3f7115` |
| Branch state | `main`; `HEAD` and `origin/main` identical |
| Only untracked file | `scripts/build_rcc002_spec_bundle.py` |
| Baseline verdict | `MATCH` |
| Reviewed proposal | `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_2026-07-31.md` |
| Trigger review | `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-31.md` |
| Findings in scope | `S8-RR2-B01`, `S8-RR2-B02` |
| Review mode | Read-only; no repository writes, subagents, network access, or S8 implementation |

## 1. Independence statement

This review was performed independently of the S8-RR-002 readiness review and
the S8RR002-BCP-001 proposal authorship. No material claim was accepted merely
because it had been committed. The reviewer checked the relevant primary
sources under `docs/specifications/`, `schemas/rcc002/`,
`tests/fixtures/rcc002/`, `scripts/rcc002/`, and the root `SHA256SUMS`, and ran
the repository test suites.

No repository file was modified, staged, or committed. No S8 implementation
was written or started.

## 2. Scope and exclusions

The review covered:

1. readiness findings `S8-RR2-B01` and `S8-RR2-B02`;
2. the proposal's normative decisions;
3. the exact correction set and exclusions;
4. the mandatory execution sequence;
5. the proposal review checklist.

The following were confirmed outside the correction scope:

- all S0-S7 production code and scientific values;
- `rcc002/s8/`, which does not exist;
- source-provider registries;
- the protected untracked `scripts/build_rcc002_spec_bundle.py`;
- historical review and certification documents;
- Dataset Manifest Schema `1.0.0` and its historical fixtures;
- real dataset generation or publication.

## 3. Evidence inspected

- `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-31.md`
- `docs/review/RCC_002_S8RR002_BLOCKER_CORRECTION_PROPOSAL_2026-07-31.md`
- `docs/specifications/RCC_002_DATA_PIPELINE_SPECIFICATION_2026-07-23.md`
- `docs/specifications/RCC_002_REPRODUCIBILITY_AND_MANIFEST_2026-07-23.md`
- `docs/specifications/RCC_002_LABEL_AND_FORWARD_RETURN_SPECIFICATION_2026-07-23.md`
- `docs/review/RCC_002_S8_IMPLEMENTATION_READINESS_REVIEW_2026-07-30.md`
- `docs/review/RCC_002_S8BCP001_REV2_DEPENDENCY_MATRIX_2026-07-30.md`
- `docs/review/RCC_002_S8BCP001_REV2_IDENTITY_GRAPH_2026-07-30.md`
- the 2026-07-30 corrected-artifact scientific and architecture re-reviews;
- the 2026-07-30 normative-bundle and implementation certification decisions;
- Dataset Manifest Schema `1.0.0` and both positive and all 11 negative fixtures;
- `scripts/rcc002/verify_s8bcp001_artifacts.py`;
- the root `SHA256SUMS`;
- Stage Manifest Schema `1.0.0` and its complete-valid fixture;
- `registries/rcc002/release/release_artifact_class_registry.v1.json`.

## 4. Mechanical verification

| Check | Result |
|---|---|
| Baseline and branch | `HEAD=origin/main=3605d1de...`; branch `main`; only the protected builder untracked |
| Six-view registry order | Confirmed from Data Pipeline Sections 7.9.3.1-7.9.3.6 |
| Positive Dataset Manifest `1.0.0` fixtures | Byte-identical; SHA-256 `1766958549c83bcb1fb808fc1334fe8c11ef0fb17618095296b38ccc8e653002` |
| Positive fixture `views` | Six entries, all `rcc002.view.audit/2.0.0` |
| Positive fixture profile | Seven placeholders `RCC-002-SPEC-0` through `RCC-002-SPEC-6`, all `1.0.0` |
| Dataset Manifest negative fixtures | 11; none covers canonical view or specification-profile semantics |
| Root integrity ledger | `sha256sum -c SHA256SUMS --ignore-missing`: PASS |
| Historical verifier in full tree | Fails on unscoped `.claude/settings.local.json` traversal |
| Historical verifier scoped reproduction | Substantive checks reproduced; confirms curated-bundle scope |
| Regression suite | 170 tests: PASS |
| RCC-002 suite | 631 tests: PASS |
| Compile check | PASS |
| Seven current specification versions | `DP 0.8.0`, `DV 0.6.0`, `IS 0.4.3`, `ST 0.4.2`, `RG 0.5.1`, `LF 0.5.0`, `RM 0.8.0` |
| Manifest fixtures by type | Six types, each with two positive and 11 negative fixtures |

## 5. Independent reproduction of S8-RR2-B01

`S8-RR2-B01` is confirmed.

The authoritative ordered registry consists of:

1. `rcc002.view.research-features/1.0.0`;
2. `rcc002.view.backtest-inputs/1.0.0`;
3. `rcc002.view.paper/1.0.0`;
4. `rcc002.view.live/1.0.0`;
5. `rcc002.view.label-research/1.0.0`;
6. `rcc002.view.audit/2.0.0`.

This order and the two relevant allowlist hashes agree across Data Pipeline
Section 7.9.3, Reproducibility Section 8.7, Label and Forward Return Section
26.1, and the dependency matrix.

Reproducibility Section 24 and both positive Dataset Manifest `1.0.0`
fixtures instead contain six copies of `rcc002.view.audit/2.0.0`. The schema
only requires at least six generic view references, so the duplicate array is
schema-valid. The historical verifier does not inspect the fixture `views`
content and therefore cannot detect the defect.

## 6. Independent reproduction of S8-RR2-B02

`S8-RR2-B02` is confirmed.

The canonical current specification profile is:

1. `RCC_002_DATA_PIPELINE_SPECIFICATION/0.8.0`;
2. `RCC-002-DV/0.6.0`;
3. `RCC-002-IS/0.4.3`;
4. `RCC-002-ST/0.4.2`;
5. `RCC-002-RG/0.5.1`;
6. `RCC-002-LF/0.5.0`;
7. `RCC-002-RM/0.8.0`.

The profile agrees with Reproducibility Section 12.3 and the seven current
specification headers. Section 24 and both positive Dataset Manifest `1.0.0`
fixtures instead use `RCC-002-SPEC-0` through `RCC-002-SPEC-6`, each at
`1.0.0`. The generic schema accepts those placeholders, and neither the
historical verifier nor the certification decisions inspect this semantic
content.

## 7. Scientific findings

### S8RR002-PR-SCI-001

| Field | Value |
|---|---|
| Severity | `MAJOR` |
| Disposition | `OPEN` |

The proposal classifies the Reproducibility and Manifest change from `0.8.0`
to `0.8.1` as a patch correction. The document's own version history uses a
minor version increase for new normative content and patch increases for
purely mechanical follow-up changes without independent normative effect.

The proposal adds normative definitions for the canonical view snapshot,
ordered exact membership, a new schema identity, and withdrawal of the
defective schema from prospective use. A patch classification therefore
misrepresents the change under the document's own precedent.

Required correction: increase the Reproducibility and Manifest document from
`0.8.0` to `0.9.0` and update all internal self-references. The substantive
six-view and seven-specification decisions remain correct.

### S8RR002-PR-SCI-002

| Field | Value |
|---|---|
| Severity | `MINOR` |
| Disposition | `OPEN` |

The proposal does not unambiguously say whether zero-digest placeholders in
the corrected Section 24 specification profile apply only to the
self-referencing Reproducibility and Manifest entry or to all seven entries.

Required correction: use literal SHA-256 values for the six non-self
specification documents. Use one explicitly labelled, non-literal zero digest
only for the `RCC-002-RM` self-entry.

### S8RR002-PR-SCI-003

| Field | Value |
|---|---|
| Severity | `INFORMATIONAL` |
| Disposition | `CLOSED` |

Reproducibility Section 18.4 rejects unknown major schema versions. This
supports retaining Dataset Manifest Schema `1.0.1`; no schema version change
is required.

## 8. Architecture findings

### S8RR002-PR-ARCH-001

| Field | Value |
|---|---|
| Severity | `MINOR` |
| Disposition | `OPEN` |

The historical verifier traverses the full filesystem and fails on files
outside its intended correction bundle. The proposed verifier does not yet
declare a stable enumeration scope.

Required correction: the new verifier must use an explicit, versioned input
manifest or `git ls-files`, not unscoped filesystem traversal, and must
document the exact scope it validates. An explicit versioned manifest is
preferred because it is portable outside a Git working tree.

### S8RR002-PR-ARCH-002

| Field | Value |
|---|---|
| Severity | `INFORMATIONAL` |
| Disposition | `NOT APPLICABLE` |

Stage Manifest `1.0.0` also contains a field named
`specification_profile`, but it has different semantics and does not exhibit
either blocker. The correction record should state that it is semantically
distinct and outside this correction scope.

### S8RR002-PR-ARCH-003

| Field | Value |
|---|---|
| Severity | `INFORMATIONAL` |
| Disposition | `NOT APPLICABLE` |

Reproducibility Section 8.5 contains pre-existing illustrative field-name
drift from the real schema. This is unrelated to the two blockers and should
be reserved for a future editorial correction cycle.

### S8RR002-PR-ARCH-004

| Field | Value |
|---|---|
| Severity | `MINOR` |
| Disposition | `OPEN` |

Reproducibility Section 12.3 says the canonical profile must include "at
least" the listed documents, whereas the proposed schema closes the current
profile at exactly seven ordered entries.

Required correction: clarify that "at least" governs completeness as the
specification family evolves over time, while each declared Dataset Manifest
profile is exact and closed for its stated profile version.

## 9. Proposal checklist disposition

| # | Review question | Disposition |
|---|---|---|
| 1 | Are `views` and `artifacts` unambiguously separate? | `CLOSED` |
| 2 | Are the six views and their order complete and correct? | `CLOSED` |
| 3 | Is the seven-document profile complete and correctly ordered? | `CLOSED` |
| 4 | Is `1.0.1` the correct non-destructive schema version? | `CLOSED` |
| 5 | Are historical `1.0.0` bytes and evidence preserved? | `CLOSED` |
| 6 | Can every designed invalid case fail closed? | `CLOSED, CONTINGENT` on generated schema and verifier |
| 7 | Is structural validation reproducible without an undeclared dependency? | `OPEN`; validator not named or pinned |
| 8 | Does the proposal alter S0-S7 science or deterministic values? | `CLOSED` |
| 9 | Does any proposed identity edge create a cycle? | `CLOSED` |
| 10 | Is the correction set minimal and complete? | `CLOSED WITH CONDITIONS` |

## 10. Required corrections before approval

1. Reclassify the Reproducibility and Manifest change as `0.8.0` to `0.9.0`
   and update all self-references.
2. Require literal hashes for the six non-self specifications in Section 24
   and one labelled zero placeholder only for the `RCC-002-RM` self-entry.
3. Require explicit, versioned verifier input enumeration, with no unscoped
   filesystem traversal.
4. Name and pin a Draft 2020-12 JSON Schema validator before artifact
   generation.
5. Resolve the "at least" versus exact-current-profile wording in
   Reproducibility Section 12.3.
6. State that the same-named Stage Manifest field is semantically distinct and
   outside scope.
7. Document that the historical verifier is meaningful only for its curated
   correction-bundle input, not an arbitrary full working tree.

These corrections do not require reconsidering the canonical six-view order,
the seven-document profile, the `views` versus `artifacts` separation,
Dataset Manifest Schema `1.0.1`, or preservation of historical `1.0.0`
artifacts.

## 11. Residual risks

- The Stage Manifest name collision is not a defect but can confuse future
  correction work.
- Reproducibility Section 8.5 has unrelated illustrative drift that should be
  handled only in a separate editorial cycle.
- The new verifier must disclose its invocation context so a scoped PASS
  cannot be mistaken for a full-tree verification.
- S0-S7 baseline integrity remains reproduced: 170 regression tests, 631
  RCC-002 tests, compile check, and root SHA ledger all pass.

## 12. Final verdict

The proposal's core scientific and architectural decisions are independently
confirmed. However, `S8RR002-PR-SCI-001` remains an open `MAJOR` finding, and
the validator dependency, Section 24 hash rule, verifier scope, and profile
wording remain unresolved conditions.

Under the mandated verdict rule, an unresolved `MAJOR` finding requires
rejection. S8 implementation remains prohibited pending a corrected proposal,
its independent re-review, and a subsequent `READY` S8 readiness verdict.

`REJECT`
